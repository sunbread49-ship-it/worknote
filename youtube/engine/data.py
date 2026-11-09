"""실제 시세 데이터 로더 + 대본 숫자 검증용 통계.

시리즈 이름(에피소드 YAML의 `series:`):
  sp500           S&P500 월평균 지수 (1871~, 1957년 이전은 Shiller 재구성 지수)
  sp500_drawdown  S&P500 고점 대비 하락률(%)
  vix             CBOE VIX 일간 종가 (1990~)
  tqqq/sqqq/qqq   ETF 일간 수정주가(배당·분할 반영) (TQQQ·SQQQ 2010.2~, QQQ 1999.3~)
  ndx             나스닥100 지수 일간 종가 (1985.10~)
  sim3x_ndx       나스닥100 일간 수익률 x3 - 운용보수(연 0.95%)로 만든 '가상 TQQQ' (1985~)
                  ※ 차입비용 미반영 → 실제보다 유리하게 나옴(보수적 비교)
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from .style import ROOT

DATA = ROOT / "assets" / "data"


@lru_cache(maxsize=None)
def _sp500() -> pd.Series:
    df = pd.read_csv(DATA / "sp500_monthly.csv", parse_dates=["Date"])
    return df.set_index("Date")["SP500"].astype(float)


@lru_cache(maxsize=None)
def _vix() -> pd.Series:
    df = pd.read_csv(DATA / "vix_daily.csv", parse_dates=["DATE"])
    return df.set_index("DATE")["CLOSE"].astype(float)


# 네이버 차트 일별 종가 (tools/fetch_assets.naver_stock)
KR_NAVER = ("kodex200", "kodex_lev", "kodex_inv2x", "bat_kodex", "bat_lev_kodex", "bat_lev_tiger",
            "lges", "ecopro", "ecopro_bm", "hanwha_aero")


@lru_cache(maxsize=None)
def _daily(name: str) -> pd.Series:
    df = pd.read_csv(DATA / f"{name}_daily.csv")
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    col = "adj_close" if name not in ("ndx", "spx", "kospi", "skhynix", "samsung") + KR_NAVER else "close"
    s = df.assign(date=pd.to_datetime(df["date"])).set_index("date")[col].astype(float)
    return s[s > 0].dropna()


def _sim3x(fee=0.0095):
    r = _daily("ndx").pct_change().dropna()
    return (1 + 3 * r - fee / 252).cumprod()


# ── 미국 선거 사이클 ──────────────────────────────────────────────
def election_day(y):
    """11월 첫 월요일 다음 화요일"""
    import datetime as dt
    x = dt.date(y, 11, 1)
    while x.weekday() != 0:
        x += dt.timedelta(1)
    return pd.Timestamp(x + dt.timedelta(1))


def _on(p, t):   # t 이후 첫 거래일 종가
    return p.loc[t:].iloc[0]


def _by(p, t):   # t 이전 마지막 거래일 종가
    return p.loc[:t].iloc[-1]


def elec_fwd(kind="midterm", y0=1950, y1=2022):
    """선거일 종가 → 1년 뒤 수익률(%) 목록 [(연도, %)]"""
    p = _daily("spx")
    start = y0 if kind == "midterm" else y0 + 2
    out = []
    for y in range(start, y1 + 1, 4):
        e = election_day(y)
        if e + pd.Timedelta(days=365) > p.index[-1]:
            continue
        out.append((y, (_by(p, e + pd.Timedelta(days=365)) / _on(p, e) - 1) * 100))
    return out


def cycle_years_list(k, y0=1950, y1=2025):
    yr = _daily("spx").resample("YE").last().pct_change().dropna() * 100
    yr = yr[(yr.index.year >= y0) & (yr.index.year <= y1)]
    return [(y, v) for y, v in zip(yr.index.year, yr.values) if (y - 2) % 4 == (k - 2) % 4]


def cycle_years(k, y0=1950, y1=2025):
    """임기 k년차 연간 수익률(%) 목록. k: 1=대선 다음 해, 2=중간선거 해, 3=대선 전 해, 4=대선 해"""
    yr = _daily("spx").resample("YE").last().pct_change().dropna() * 100
    yr = yr[(yr.index.year >= y0) & (yr.index.year <= y1)]
    return [v for y, v in zip(yr.index.year, yr.values) if (y - 2) % 4 == (k - 2) % 4]


def dd_events(th=-0.3, since="1927", years=5):
    """S&P500이 직전 최고점 대비 th 이하로 처음 내려간 날(하락장마다 1번)
    → [(날짜, 1년 뒤%, years년 뒤%, 그 뒤 추가 최대낙폭%)] (years년이 안 지난 건 제외)"""
    p = _daily("spx")
    dd = p / p.cummax() - 1
    out, armed = [], False
    for t, v in dd.loc[str(since):].items():
        if v == 0:
            armed = True
        if armed and v <= th:
            armed = False
            end = t + pd.Timedelta(days=365 * years)
            if end > p.index[-1]:
                continue
            f1 = (_by(p, t + pd.Timedelta(days=365)) / _on(p, t) - 1) * 100
            fy = (_by(p, end) / _on(p, t) - 1) * 100
            further = (p.loc[t:end].min() / _on(p, t) - 1) * 100
            out.append((t, f1, fy, further))
    # 1927년 이전 고점 정보가 없어 첫 하락장은 1929년 고점부터 인정
    return out


def vix_events(level=40, reset=25):
    """VIX가 level을 처음 넘은 날(reset 아래로 내려가야 다시 인정)
    → [(날짜, VIX, 나스닥100 1년%, 3배 1년%, 3배 1년 내 최대낙폭%)]. 3배 = TQQQ(2010.2~) / 가상 TQQQ(이전)"""
    v, n, s3, t = _vix(), _daily("ndx"), _sim3x(), _daily("tqqq")
    out, armed = [], True
    for d, x in v.items():
        if x < reset:
            armed = True
        if armed and x > level:
            armed = False
            if d + pd.Timedelta(days=365) > n.index[-1]:
                continue
            lev = t if d >= pd.Timestamp("2010-02-12") else s3
            e = d + pd.Timedelta(days=365)
            out.append((d, float(x), (_by(n, e) / _on(n, d) - 1) * 100, (_by(lev, e) / _on(lev, d) - 1) * 100,
                        (lev.loc[d:e].min() / _on(lev, d) - 1) * 100))
    return out


def crash_days(th=-0.06, days=252):
    """나스닥100 하루 수익률이 th 이하인 날 → [(날짜, 그날%, days거래일 뒤%)] (뒤 기간이 안 지난 날은 제외)"""
    p = _daily("ndx")
    r = p.pct_change()
    out = []
    for t in r[r <= th].index:
        i = p.index.get_loc(t)
        if i + days < len(p):
            out.append((t, r.loc[t] * 100, (p.iloc[i + days] / p.iloc[i] - 1) * 100))
    return out


# 미국 정부 구성(달력 연도 기준, 1950~): 대통령 정당 + 의회(상·하원) 장악 · 2001년은 상원이 중간에 바뀌어 '의회 분할'
GOV = {}
for _ys, _k in (((1949, 1952), "uD"), ((1953, 1954), "uR"), ((1955, 1960), "RpDc"), ((1961, 1968), "uD"),
                ((1969, 1976), "RpDc"), ((1977, 1980), "uD"), ((1981, 1986), "split"), ((1987, 1992), "RpDc"),
                ((1993, 1994), "uD"), ((1995, 2000), "DpRc"), ((2001, 2002), "split"), ((2003, 2006), "uR"),
                ((2007, 2008), "RpDc"), ((2009, 2010), "uD"), ((2011, 2014), "split"), ((2015, 2016), "DpRc"),
                ((2017, 2018), "uR"), ((2019, 2020), "split"), ((2021, 2022), "uD"), ((2023, 2024), "split"),
                ((2025, 2026), "uR"), ((2027, 2028), "RpDc")):
    for _y in range(_ys[0], _ys[1] + 1):
        GOV[_y] = _k


def year_ret(y, name="spx"):
    p = _daily(name)
    return (p.loc[:f"{y}-12-31"].iloc[-1] / p.loc[:f"{y - 1}-12-31"].iloc[-1] - 1) * 100


def seasons(name="spx", which="winter", y0=1950, y1=2025):
    p = _daily(name)
    c = lambda d: p.loc[:d].iloc[-1]
    out = []
    for y in range(y0, y1 + 1):
        if which == "winter":
            if pd.Timestamp(f"{y + 1}-04-30") <= p.index[-1] and pd.Timestamp(f"{y}-10-31") >= p.index[0]:
                out.append((y, c(f"{y + 1}-04-30") / c(f"{y}-10-31") - 1))
        elif pd.Timestamp(f"{y}-04-30") >= p.index[0]:
            out.append((y, c(f"{y}-10-31") / c(f"{y}-04-30") - 1))
    return out


def thanksgiving(y0=1950, y1=2025):
    p = _daily("spx")
    out = []
    for y in range(y0, y1 + 1):
        th = [d for d in pd.date_range(f"{y}-11-01", f"{y}-11-30") if d.weekday() == 3][3]
        a = p.loc[:th - pd.Timedelta(days=2)].iloc[-1]
        b = p.loc[th + pd.Timedelta(days=1):].iloc[0]
        out.append(b / a - 1)
    return out


def lump_dca(name="spx", y0=1950, months=12, horizon=12, end="2026-10-31", cash=0.0):
    """매달 시작점마다: 한 번에(12) vs 12개월 나눠(1씩, 대기 현금 0%) → horizon개월 뒤 가치(투자금 1 기준 배수)
    → DataFrame[start, lump, dca, half, ath(시작 시 사상 최고치 근처 여부), paper_lump, paper_dca]"""
    p = _daily(name)
    mm = p.resample("ME").last()
    hi = mm.cummax()
    m = mm.loc[str(y0):end]
    v, h = m.values, hi.loc[m.index].values
    rows = []
    for i in range(len(v) - max(horizon, months)):
        l = v[i + horizon] / v[i]
        d = sum(v[i + horizon] / v[i + k] * (1 + cash) ** (k / 12) for k in range(months)) / months
        pl = min(v[i + k] / v[i] for k in range(months + 1)) - 1
        pdv = min(sum(v[i + k] / v[i + j] for j in range(min(k + 1, months))) / min(k + 1, months) for k in range(months + 1)) - 1
        rows.append((m.index[i], l, d, 0.5 * l + 0.5 * d, v[i] >= h[i] * 0.999, pl, pdv))
    return pd.DataFrame(rows, columns=["start", "lump", "dca", "half", "ath", "paper_lump", "paper_dca"])


BUBBLE = ("2000-01-01", "2002-12-31")  # 닷컴 버블 붕괴기


def _cycle_strategy(name):
    """중간선거일→대선일만 보유(strat_mid2pres) 또는 대선일→중간선거일만 보유(strat_pres2mid), 나머지는 현금"""
    p = _daily("spx").loc["1950-11-01":]
    r = p.pct_change().fillna(0)
    inmk = pd.Series(False, index=p.index)
    for y in range(1950, p.index[-1].year + 1, 4):
        m, pr, nm = election_day(y), election_day(y + 2), election_day(y + 4)
        a, b = (m, pr) if name == "strat_mid2pres" else (pr, nm)
        inmk[(p.index > a) & (p.index <= b)] = True
    eq = (1 + r.where(inmk, 0)).cumprod()
    return eq.loc[str(election_day(1950).date()):]


# ── 한국(코스피) · 한·미 연동 ─────────────────────────────────────
def kr_weekly_drops(th=-0.10, gap_days=56):
    """금요일 종가 기준 한 주 th 이하 하락. gap_days 안에 이어진 하락은 한 사건으로 묶음(첫 주 기준).
    반환: [(주, 하락%, 4주 뒤%, 13주 뒤%, 52주 뒤%, 156주 뒤%)]"""
    w = _daily("kospi").resample("W-FRI").last().dropna()
    r = w.pct_change()
    out, last = [], None
    for dt, v in r[r <= th].items():
        if last is not None and (dt - last).days < gap_days:
            last = dt
            continue
        last = dt
        i = w.index.get_loc(dt)
        g = lambda h: (w.iloc[i + h] / w.iloc[i] - 1) * 100 if i + h < len(w) else np.nan
        out.append((dt, v * 100, g(4), g(13), g(52), g(156)))
    return out


def kr_us_nightly(us="spx", y0="2000"):
    """코스피 일간 수익률 vs 직전 미국 거래일(전날 밤) 수익률 (소수)"""
    k = _daily("kospi").pct_change().dropna()
    u = _daily(us).pct_change().dropna()
    idx = u.index.searchsorted(k.index, side="left") - 1
    prev = pd.Series([u.iloc[i] if i >= 0 else np.nan for i in idx], index=k.index)
    df = pd.DataFrame({"k": k, "u": prev}).dropna()
    return df.loc[str(y0):]


# ── 한국 아파트(KB) · 환율 · 물가 (EP011) ───────────────────────────
@lru_cache(maxsize=None)
def _kb(col):
    df = pd.read_csv(DATA / "kb_apt_monthly.csv")
    return df.assign(m=pd.to_datetime(df["month"])).set_index("m")[col].astype(float).dropna()


@lru_cache(maxsize=None)
def _fred(sid):
    s = pd.read_csv(DATA / "fred" / f"{sid}.csv", parse_dates=[0], index_col=0).iloc[:, 0]
    return pd.to_numeric(s, errors="coerce").dropna()


def _spx_krw():
    fx = _fred("DEXKOUS")
    s = _daily("spx")
    fx = fx.reindex(s.index).ffill()
    return (s * fx).dropna()


def kr_rate():
    """주택담보대출 금리 근사: 3개월 은행간 금리 + 1.5%p (월별)"""
    return (_fred("IR3TIB01KRM156N") + 1.5).resample("MS").ffill()


def house_lev(t0, ltv=0.6, eq=1.0, col="서울"):
    """서울 아파트를 자기자본 eq(억) + 대출(LTV)로 샀을 때 → (현재 자기자본, 낸 이자 합, 자기자본 최저, 최저 시점)"""
    H = _kb(col).loc[:"2026-10-01"]
    t0 = pd.Timestamp(t0)
    price = eq / (1 - ltv)
    loan = price - eq
    path = price * H.loc[t0:] / H.loc[t0] - loan
    r = kr_rate().reindex(H.loc[t0:].index[1:]).ffill()
    return float(path.iloc[-1]), float((loan * r / 100 / 12).sum()), float(path.min()), path.idxmin()


def series(name: str, start=None, end=None) -> pd.Series:
    if name in ("kb_jr", "kb_conv"):  # 서울 아파트 전세가율(%) · 전월세전환율(%)
        df = pd.read_csv(DATA / "kb_seoul_extra.csv")
        s = df.assign(m=pd.to_datetime(df["month"])).set_index("m")[{"kb_jr": "jeonse_ratio", "kb_conv": "conv_rate"}[name]]
        return pd.to_numeric(s, errors="coerce").dropna().loc[start:end]
    if name in ("kb_seoul", "kb_gangnam11", "kb_total"):
        s = _kb({"kb_seoul": "서울", "kb_gangnam11": "강남11개구", "kb_total": "전국"}[name])
        return s.loc[start:end]
    if name == "spx_krw":
        return _spx_krw().loc[start:end]
    if name == "sp500":
        s = _sp500()
    elif name == "sp500_drawdown":
        p = _sp500()
        s = (p / p.cummax() - 1) * 100
    elif name == "vix":
        s = _vix()
    elif name in ("strat_mid2pres", "strat_pres2mid"):
        s = _cycle_strategy(name)
    elif name in ("tqqq", "sqqq", "qqq", "ndx", "spx", "nvda", "msft", "aapl", "amd", "kospi",
                  "smh", "soxx", "intc", "mu", "tsm", "skhynix", "samsung") + KR_NAVER:
        s = _daily(name)
    elif name == "sim3x_ndx":
        s = _sim3x()
    elif name in ("halloween_spx", "halloween_ndx"):  # 10월 말~4월 말만 보유, 나머지 현금(0%) 자산 곡선
        p = _daily(name.split("_")[1])
        r = p.pct_change().fillna(0)
        m, d = r.index.month, r.index.day
        # 그날 수익률을 받으려면 '전날 보유 중'이어야 함: 보유 구간 = 11월~4월 (10월 마지막 거래일 종가 매수 → 4월 마지막 거래일 종가 매도)
        held = pd.Series(r.index.month, index=r.index).isin([11, 12, 1, 2, 3, 4])
        held &= r.index >= pd.Timestamp("1950-11-01")
        s = (1 + r.where(held, 0)).cumprod()
        s = s / s.loc[:"1950-10-31"].iloc[-1] if name == "halloween_spx" else s / s.loc[:"1985-10-31"].iloc[-1]
    elif name.endswith("_drawdown") and name[:-9] in ("tqqq", "sqqq", "qqq", "ndx", "sim3x_ndx", "kospi", "spx"):
        p = series(name[:-9])
        s = (p / p.cummax() - 1) * 100
    else:
        raise KeyError(f"알 수 없는 시리즈: {name}")
    return s.loc[start:end]


# ── 통계 (에피소드의 bar/stat 장면이 직접 호출 → 대본 숫자와 대조) ──
def fwd_return(months=12):
    p = _sp500()
    return (p.shift(-months) / p - 1) * 100


def stat(kind: str, **kw) -> float:
    """
    kind:
      fwd_mean_all        since부터 아무 달에나 샀을 때 months 뒤 평균 수익률(%)
      fwd_winrate_all     〃 플러스 확률(%)
      fwd_mean_dd         고점 대비 threshold% 이하인 달에 샀을 때 평균 수익률(%)
      fwd_winrate_dd      〃 플러스 확률(%)
      fwd_mean_vix        VIX 월중 최고치 > level 인 달에 샀을 때 평균 수익률(%)
      fwd_winrate_vix     〃 플러스 확률(%)
      count_dd / count_vix  해당 달 수
      change              start→end 지수 변화율(%)
    """
    if kind.startswith("dropev_"):  # 하루(또는 주) th 이하 급락 뒤 h거래일 성과: dropev_n / _up / _med (series, th, h, y0, y1, weekly)
        p = series(kw["series"])
        if kw.get("weekly"):
            p = p.resample("W-FRI").last().dropna()
        r = p.pct_change()
        out, last = [], None
        for dt, v in r[r <= kw.get("th", -0.07)].items():
            if last is not None and (dt - last).days < kw.get("gap", 30):
                last = dt
                continue
            last = dt
            if not (str(kw.get("y0", 1900)) <= str(dt.year) <= str(kw.get("y1", 2100))):
                continue
            i = p.index.get_loc(dt)
            h = kw.get("h", 252)
            if i + h < len(p):
                out.append((p.iloc[i + h] / p.iloc[i] - 1) * 100)
        v = np.array(out)
        return float({"dropev_n": len(v), "dropev_up": (v > 0).sum(), "dropev_med": np.median(v) if len(v) else 0}[kind])
    if kind == "from_peak":  # since 이후 최고점 대비 현재(%)
        p = series(kw["series"]).loc[str(kw.get("since", "2025")):]
        return float((p.iloc[-1] / p.max() - 1) * 100)
    if kind == "day_ret":  # 특정 날 하루 수익률(%)
        p = series(kw["series"]).pct_change()
        return float(p.loc[str(kw["date"])] * 100)
    if kind.startswith("hl_"):  # 대출로 산 서울 아파트: hl_eq / hl_int / hl_min (t0, ltv)
        v = house_lev(kw["t0"], kw.get("ltv", 0.6), 1.0, kw.get("col", "서울"))
        return {"hl_eq": v[0], "hl_int": v[1], "hl_min": v[2]}[kind]
    if kind == "mult_m":  # 월평균 기준 배수 (series, start, end)
        p = series(kw["series"]).resample("MS").mean()
        return float(p.loc[:str(kw["end"])].iloc[-1] / p.loc[str(kw["start"]):].iloc[0])
    if kind == "mdd":  # 월평균 기준 최대 낙폭(%)
        p = series(kw["series"]).resample("MS").mean().loc[str(kw.get("start", "1990")):str(kw.get("end", "2026-10"))]
        return float((p / p.cummax() - 1).min() * 100)
    if kind.startswith("kr_"):
        if kind.startswith("kr_wk_"):  # kr_wk_n / kr_wk_up / kr_wk_med / kr_wk_mean / kr_wk_cnt (h: 1m|3m|1y|3y)
            ev = kr_weekly_drops(kw.get("th", -0.10))
            if kind == "kr_wk_n":
                return float(len(ev))
            j = {"1m": 2, "3m": 3, "1y": 4, "3y": 5}[kw.get("h", "1y")]
            v = np.array([e[j] for e in ev if not np.isnan(e[j])])
            return float({"kr_wk_cnt": len(v), "kr_wk_up": (v > 0).sum(), "kr_wk_win": (v > 0).mean() * 100,
                          "kr_wk_med": np.median(v), "kr_wk_mean": v.mean()}[kind])
        if kind == "kr_corr":  # 코스피 vs 전날 밤 미국 일간 상관계수 (y0~y1)
            df = kr_us_nightly(kw.get("us", "spx"), str(kw.get("y0", 1990))).loc[:str(kw.get("y1", 2026))]
            return float(df.k.corr(df.u))
        if kind.startswith("kr_night_"):  # 전날 밤 미국 lo < 수익률 <= hi 일 때 코스피: kr_night_n / _mean / _down / _up
            df = kr_us_nightly(kw.get("us", "ndx"), str(kw.get("y0", 2000)))
            m = df[(df.u > kw.get("lo", -1)) & (df.u <= kw.get("hi", 1))]
            return float({"kr_night_n": len(m), "kr_night_mean": m.k.mean() * 100, "kr_night_down": (m.k < 0).mean() * 100,
                          "kr_night_up": (m.k > 0).mean() * 100}[kind])
        if kind == "kr_beta":  # side: down|up
            df = kr_us_nightly(kw.get("us", "spx"), str(kw.get("y0", 2000)))
            m = df[df.u < 0] if kw.get("side") == "down" else df[df.u > 0]
            return float(np.polyfit(m.u, m.k, 1)[0])
        if kind == "kr_year":  # 연간 수익률 (series: kospi|spx)
            return year_ret(kw["y"], kw.get("series", "kospi"))
        if kind == "kr_same_years":  # y0~y1 중 코스피 · S&P500 연간 방향이 같은 해 수
            ys = range(kw.get("y0", 1991), kw.get("y1", 2026) + 1)
            return float(sum(np.sign(year_ret(y, "kospi")) == np.sign(year_ret(y, "spx")) for y in ys))
    if kind == "ath_days":
        p = series(kw.get("series", "spx")).loc[str(kw.get("y0", 1950)):]
        return float((p >= p.cummax()).sum())
    if kind.startswith("ld_") and kind != "ld_case":  # 한 번에 vs 나눠서. series, y0, horizon, ath(True면 사상 최고치 시작만)
        mo = kw.get("months", 12)
        df = lump_dca(kw.get("series", "spx"), kw.get("y0", 1950), mo, kw.get("horizon", mo), cash=kw.get("cash", 0.0))
        if kw.get("ath"):
            df = df[df.ath]
        if kw.get("decade"):
            df = df[(df.start.dt.year // 10) * 10 == kw["decade"]]
        f = {"ld_n": lambda: len(df), "ld_win": lambda: (df.lump > df.dca).mean() * 100,
             "ld_diff": lambda: ((df.lump - df.dca) * 100).mean(),
             "ld_lump": lambda: (df.lump.mean() - 1) * 100, "ld_dca": lambda: (df.dca.mean() - 1) * 100,
             "ld_half": lambda: (df.half.mean() - 1) * 100,
             "ld_lump_worst": lambda: (df.lump.min() - 1) * 100, "ld_dca_worst": lambda: (df.dca.min() - 1) * 100,
             "ld_half_worst": lambda: (df.half.min() - 1) * 100,
             "ld_lump_loss": lambda: (df.lump < 1).mean() * 100, "ld_dca_loss": lambda: (df.dca < 1).mean() * 100,
             "ld_paper_lump": lambda: df.paper_lump.mean() * 100, "ld_paper_dca": lambda: df.paper_dca.mean() * 100,
             "ld_half_beat": lambda: (df.half > df.dca).mean() * 100}
        return float(f[kind]())
    if kind == "ld_case":  # start(YYYY-MM)에 1200만 원: which=lump|dca, at=개월 뒤(또는 'now')
        p = _daily(kw.get("series", "spx"))
        m = p.resample("ME").last().loc[:"2026-10-31"]
        i = list(m.index.strftime("%Y-%m")).index(kw["start"])
        e = len(m) - 1 if kw.get("at") == "now" else i + int(kw["at"])
        v = m.values
        if kw.get("which") == "lump":
            return float(1200 * v[e] / v[i])
        return float(sum(100 * v[e] / v[i + k] for k in range(12)))
    if kind == "dca_forever":  # start부터 매달 100만 원 적립 → 2026.10 말 평가액(만 원). which=value|invested
        m = _daily(kw.get("series", "spx")).resample("ME").last().loc[kw["start"]:"2026-10-31"]
        return float(len(m) * 100 if kw.get("which") == "invested" else (100 / m).sum() * m.iloc[-1])
    if kind.startswith("season_") and kind != "season_beat":  # 겨울(10.31→다음 해 4.30) / 여름(4.30→10.31). which: winter|summer, y0, y1
        v = np.array([x for _, x in seasons(kw.get("series", "spx"), kw.get("which", "winter"), kw.get("y0", 1950), kw.get("y1", 2025))]) * 100
        return float({"season_n": len(v), "season_mean": v.mean(), "season_up": (v > 0).sum()}[kind])
    if kind == "season_beat":  # 겨울이 같은 해 여름보다 높았던 해 수
        w = dict(seasons(kw.get("series", "spx"), "winter", kw.get("y0", 1950), kw.get("y1", 2025)))
        sm = dict(seasons(kw.get("series", "spx"), "summer", kw.get("y0", 1950), kw.get("y1", 2025)))
        return float(sum(w[y] > sm[y] for y in w if y in sm))
    if kind == "halloween_mult":  # 핼러윈 매매(겨울만 보유, 여름은 현금 연 cash 이자) 배수. which: winter|hold
        sr = kw.get("series", "spx")
        w = seasons(sr, "winter", kw.get("y0", 1950), kw.get("y1", 2025))
        if kw.get("which") == "hold":
            p = _daily(sr)
            return float(p.loc[:f"{w[-1][0] + 1}-04-30"].iloc[-1] / p.loc[:f"{w[0][0]}-10-31"].iloc[-1])
        return float(np.prod([(1 + x) * (1 + kw.get("cash", 0.0)) ** 0.5 for _, x in w]))
    if kind.startswith("month_"):  # 달별 수익률. month, y0, y1
        p = _daily(kw.get("series", "spx"))
        y0, y1 = kw.get("y0", 1950), kw.get("y1", 2025)
        m = p.loc[f"{y0 - 1}-12-01":f"{y1}-12-31"].resample("ME").last().pct_change().dropna() * 100
        m = m[(m.index.year >= y0) & (m.index.month == kw["month"])]
        return float({"month_mean": m.mean(), "month_up": (m > 0).sum(), "month_n": len(m)}[kind])
    if kind.startswith("tg_"):  # 추수감사절 전 화요일 종가 → 다음 날 금요일 종가
        v = np.array(thanksgiving(kw.get("y0", 1950), kw.get("y1", 2025))) * 100
        return float({"tg_n": len(v), "tg_mean": v.mean(), "tg_up": (v > 0).sum()}[kind])
    if kind == "avg_2day":  # 아무 이틀 평균 수익률(%)
        r = _daily("spx").loc[str(kw.get("y0", 1950)):str(kw.get("y1", 2025))].pct_change().dropna()
        return float(((1 + r).rolling(2).apply(np.prod, raw=True) - 1).mean() * 100)
    if kind.startswith("gov_"):  # 정부 구성별 S&P500 연간 수익률. cfg: uD|uR|RpDc|DpRc|split|divided|unified, exclude: [연도]
        c = kw["cfg"]
        grp = {"divided": ("RpDc", "DpRc", "split"), "unified": ("uD", "uR")}.get(c, (c,))
        ys = [y for y, k in GOV.items() if k in grp and kw.get("y0", 1950) <= y <= kw.get("y1", 2025)
              and y not in kw.get("exclude", [])]
        v = np.array([year_ret(y) for y in ys])
        return float({"gov_n": len(v), "gov_mean": v.mean() if len(v) else 0, "gov_up": (v > 0).sum(),
                      "gov_med": np.median(v) if len(v) else 0}[kind])
    if kind == "max_dd_window":  # start~end 사이 최대 낙폭(%)
        w = series(kw["series"]).loc[str(kw["start"]):str(kw["end"])]
        return float(((w / w.cummax()) - 1).min() * 100)
    if kind.startswith("crash_"):  # 나스닥100 -6% 하락일 통계. scope: all|bubble|ex (버블기 2000~2002 / 제외)
        ev = crash_days(kw.get("th", -0.06), kw.get("days", 252))
        sc = kw.get("scope", "all")
        inb = lambda t: BUBBLE[0] <= str(t.date()) <= BUBBLE[1]
        ev = [e for e in ev if sc == "all" or (sc == "bubble") == inb(e[0])]
        v = np.array([e[2] for e in ev])
        if kind == "crash_n":
            return float(len(ev))
        if kind == "crash_up":
            return float((v > 0).sum())
        if kind == "crash_mean":
            return float(v.mean())
        if kind == "crash_med":
            return float(np.median(v))
    if kind == "best_days_miss":  # 나스닥100 since~ 전체 배수 vs 최고의 날 k일 빠졌을 때 배수 (which: all|miss)
        r = _daily("ndx").pct_change().loc[str(kw.get("since", "1985")):].dropna()
        if kw.get("which") == "miss":
            r = r.drop(r.nlargest(int(kw["k"])).index)
        return float((1 + r).prod())
    if kind == "split4":  # start일에 1/4, 21·42·63거래일 뒤 1/4씩 → days거래일 뒤 수익률(%)
        p = series(kw["series"])
        i = p.index.get_loc(p.loc[str(kw["start"]):].index[0])
        e = i + kw.get("days", 252)
        return float((np.mean([p.iloc[e] / p.iloc[i + k] for k in (0, 21, 42, 63)]) - 1) * 100)
    if kind == "allin":
        p = series(kw["series"])
        i = p.index.get_loc(p.loc[str(kw["start"]):].index[0])
        return float((p.iloc[i + kw.get("days", 252)] / p.iloc[i] - 1) * 100)
    if kind == "ret":  # 일간 시리즈 start→end 변화율(%) (가장 가까운 거래일)
        p = series(kw["series"])
        a = p.loc[str(kw["start"]):].iloc[0] if kw.get("start") else p.iloc[0]
        b = p.loc[:str(kw["end"])].iloc[-1] if kw.get("end") else p.iloc[-1]
        return (b / a - 1) * 100
    if kind == "mult":  # 몇 배
        return stat("ret", **kw) / 100 + 1
    if kind == "best_window_mult":  # 아무 날 매수 → days 거래일 안에 도달한 최고 배수
        p = series(kw["series"]).values
        d = kw.get("days", 504)
        return float(max(p[i:i + d + 1].max() / p[i] for i in range(len(p))))
    if kind in ("anyyear_mean", "anyyear_win"):  # 매년 11월 선거일 무렵 → 1년 뒤 (1950~2024)
        p = _daily("spx")
        v = [(_by(p, election_day(y) + pd.Timedelta(days=365)) / _on(p, election_day(y)) - 1) * 100 for y in range(1950, 2025)]
        return float(np.mean(v) if kind == "anyyear_mean" else np.mean(np.array(v) > 0) * 100)
    if kind.startswith("dd_"):  # dd_n / dd_mean1 / dd_meanY / dd_winY / dd_upY / dd_further / dd_worstY / dd_worst_further
        ev = dd_events(kw.get("th", -0.3), kw.get("since", "1927"), kw.get("years", 5))
        a1 = np.array([e[1] for e in ev]); ay = np.array([e[2] for e in ev]); af = np.array([e[3] for e in ev])
        return float({"dd_n": len(ev), "dd_mean1": a1.mean(), "dd_meanY": ay.mean(), "dd_winY": (ay > 0).mean() * 100,
                      "dd_upY": (ay > 0).sum(), "dd_further": af.mean(), "dd_worstY": ay.min(),
                      "dd_worst_further": af.min(), "dd_win1": (a1 > 0).mean() * 100}[kind])
    if kind.startswith("vix_"):  # vix_n / vix_ndx / vix_lev / vix_levwin / vix_levup / vix_levworst / vix_dd
        ev = vix_events(kw.get("level", 40))
        n_ = np.array([e[2] for e in ev]); l_ = np.array([e[3] for e in ev]); d_ = np.array([e[4] for e in ev])
        return float({"vix_n": len(ev), "vix_ndx": n_.mean(), "vix_lev": l_.mean(), "vix_levmed": np.median(l_),
                      "vix_levwin": (l_ > 0).mean() * 100, "vix_levup": (l_ > 0).sum(), "vix_levworst": l_.min(),
                      "vix_dd": d_.mean(), "vix_ddworst": d_.min()}[kind])
    if kind == "elec_compound":  # 선거일→1년만 보유를 이어 붙인 배수
        v = [x for _, x in elec_fwd(kw.get("which", "midterm"), kw.get("y0", 1950), kw.get("y1", 2022))]
        return float(np.prod([1 + x / 100 for x in v]))
    if kind in ("elec_mean", "elec_win", "elec_min", "elec_max", "elec_n", "elec_up"):
        v = [x for _, x in elec_fwd(kw.get("which", "midterm"), kw.get("y0", 1950), kw.get("y1", 2022))]
        return float({"elec_mean": np.mean(v), "elec_win": np.mean(np.array(v) > 0) * 100, "elec_min": min(v),
                      "elec_max": max(v), "elec_n": len(v), "elec_up": sum(x > 0 for x in v)}[kind])
    if kind in ("cycle_mean", "cycle_win", "cycle_up", "cycle_n"):
        v = cycle_years(kw["k"])
        return float({"cycle_mean": np.mean(v), "cycle_win": np.mean(np.array(v) > 0) * 100,
                      "cycle_up": sum(x > 0 for x in v), "cycle_n": len(v)}[kind])
    if kind == "cycle_dd":  # 임기 k년차의 연중 최대 낙폭 평균(%)
        p = _daily("spx")
        v = [((p[str(y)] / p[str(y)].cummax() - 1).min()) * 100 for y in range(1950, 2026) if (y - 2) % 4 == (kw["k"] - 2) % 4]
        return float(np.mean(v))
    if kind == "midlow_fwd":  # 중간선거 해 최저점 → 1년 뒤 평균(%)
        p = _daily("spx")
        v = []
        for y in range(1950, 2023, 4):
            s_ = p[str(y)]
            t = s_.idxmin()
            v.append((_by(p, t + pd.Timedelta(days=365)) / s_.min() - 1) * 100)
        return float(np.mean(v))
    if kind in ("half_mean", "half_win", "half_up"):  # 2년 구간 수익률
        p = _daily("spx")
        v = []
        for y in range(1950, 2026, 4):
            m, pr, nm = election_day(y), election_day(y + 2), election_day(y + 4)
            a, b = (m, pr) if kw["half"] == "mid2pres" else (pr, nm)
            if b <= p.index[-1]:
                v.append((_by(p, b) / _on(p, a) - 1) * 100)
        return float({"half_mean": np.mean(v), "half_win": np.mean(np.array(v) > 0) * 100, "half_up": sum(x > 0 for x in v)}[kind])
    if kind == "count_days_below":  # 하루 수익률이 threshold% 미만인 날 수
        p = series(kw["series"]).loc[str(kw["start"]):str(kw["end"])]
        return float((p.pct_change() * 100 < kw["threshold"]).sum())
    if kind == "max_dd":
        p = series(kw["series"]).loc[str(kw.get("start", "1900")):str(kw.get("end", "2100"))]
        return float((p / p.cummax() - 1).min() * 100)
    months = kw.get("months", 12)
    since = str(kw.get("since", "1871"))
    f = fwd_return(months)
    if kind == "change":
        p = _sp500()
        return (p[kw["end"]] / p[kw["start"]] - 1) * 100
    if kind.endswith("_all"):
        sel = f.loc[since:].dropna()
    elif kind.endswith("_dd"):
        dd = series("sp500_drawdown").loc[since:]
        sel = f.loc[since:][dd <= kw["threshold"]].dropna()
    elif kind.endswith("_vix"):
        vm = _vix().resample("MS").max()
        vm = vm[vm > kw["level"]]
        sel = f.reindex(vm.index).dropna()
    else:
        raise KeyError(kind)
    if kind.startswith("count"):
        return float(len(sel))
    if "winrate" in kind:
        return float((sel > 0).mean() * 100)
    return float(sel.mean())
