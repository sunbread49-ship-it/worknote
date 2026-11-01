"""실제 시세 데이터 로더 + 대본 숫자 검증용 통계.

시리즈 이름(에피소드 YAML의 `series:`):
  sp500           S&P500 월평균 지수 (1871~, 1957년 이전은 Shiller 재구성 지수)
  sp500_drawdown  S&P500 고점 대비 하락률(%)
  vix             CBOE VIX 일간 종가 (1990~)
"""
from functools import lru_cache

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


def series(name: str, start=None, end=None) -> pd.Series:
    if name == "sp500":
        s = _sp500()
    elif name == "sp500_drawdown":
        p = _sp500()
        s = (p / p.cummax() - 1) * 100
    elif name == "vix":
        s = _vix()
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
