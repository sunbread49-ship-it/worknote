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


@lru_cache(maxsize=None)
def _daily(name: str) -> pd.Series:
    df = pd.read_csv(DATA / f"{name}_daily.csv")
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    col = "adj_close" if name not in ("ndx", "spx") else "close"
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


def series(name: str, start=None, end=None) -> pd.Series:
    if name == "sp500":
        s = _sp500()
    elif name == "sp500_drawdown":
        p = _sp500()
        s = (p / p.cummax() - 1) * 100
    elif name == "vix":
        s = _vix()
    elif name in ("strat_mid2pres", "strat_pres2mid"):
        s = _cycle_strategy(name)
    elif name in ("tqqq", "sqqq", "qqq", "ndx", "spx"):
        s = _daily(name)
    elif name == "sim3x_ndx":
        s = _sim3x()
    elif name.endswith("_drawdown") and name[:-9] in ("tqqq", "sqqq", "qqq", "ndx", "sim3x_ndx"):
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
