"""빅7 분석 2 (EP024 구글)
1) 종목별 '고점 대비 -30%에 처음 닿은 날' 샀다면: 그 뒤 더 빠진 폭 · 산 값 회복까지 · 전고점 회복까지
2) 빅7 똑같이 나눠 담기(2012-05-18 메타 상장일~): 그냥 들고 있기 vs 분기마다 비율 맞추기(리밸런싱)
"""
import csv
from datetime import date
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "assets" / "data" / "m7"
T = ["googl", "aapl", "msft", "amzn", "meta", "nvda", "tsla"]
KO = {"googl": "구글", "aapl": "애플", "msft": "MS", "amzn": "아마존", "meta": "메타", "nvda": "엔비디아", "tsla": "테슬라"}


def load(t):
    r = [(x["date"], float(x["close"])) for x in csv.DictReader(open(D / f"{t}.csv"))]
    return [x for x in r if x[0] != "2011-01-13"]


def days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def minus30(t, lv=-0.30):
    r = load(t)
    out, peak, armed = [], r[0], True
    for i, (dt, c) in enumerate(r):
        if c > peak[1]:
            peak, armed = (dt, c), True
        if armed and c / peak[1] - 1 <= lv:
            armed = False
            mn, back, rec = c, None, None
            for dt2, c2 in r[i + 1:]:
                mn = min(mn, c2)
                if back is None and c2 >= c and mn < c:
                    back = dt2
                if c2 >= peak[1]:
                    rec = dt2
                    break
            out.append({"t": t, "buy": dt, "more": mn / c - 1, "back": days(dt, back) if back else (0 if mn >= c else None),
                        "rec": days(dt, rec) if rec else None, "peak": peak[0]})
    return out


def portfolio(start="2012-05-18", rebalance_every=None):
    S = {t: dict(load(t)) for t in T}
    dates = sorted(set.intersection(*[set(v) for v in S.values()]))
    dates = [d for d in dates if d >= start]
    w = {t: 1 / 7 / S[t][dates[0]] for t in T}   # 주식 수 (처음 1을 7등분)
    vals, last_q = [], None
    for d in dates:
        v = sum(w[t] * S[t][d] for t in T)
        vals.append((d, v))
        q = (d[:4], (int(d[5:7]) - 1) // 3)
        if rebalance_every == "q" and last_q is not None and q != last_q:
            w = {t: v / 7 / S[t][d] for t in T}
        last_q = q
    return vals


def stats(vals):
    v0, v1 = vals[0][1], vals[-1][1]
    yrs = days(vals[0][0], vals[-1][0]) / 365.25
    peak, mdd, cur = vals[0][1], 0, 0
    for _, v in vals:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    ath = max(v for _, v in vals)
    return v1 / v0, (v1 / v0) ** (1 / yrs) - 1, mdd, v1 / ath - 1


def main():
    print("■ 고점 대비 -30%에 처음 닿은 날 샀다면 (2010~)")
    rows = []
    for t in T:
        for h in minus30(t):
            rows.append(h)
            print(f"  {KO[t]} {h['buy']} · 더 빠진 폭 {h['more'] * 100:.0f}% · 산 값 회복 {h['back'] if h['back'] is not None else '아직'}일 · "
                  f"전고점 회복 {h['rec'] if h['rec'] is not None else '아직'}일")
    print("\n■ 종목별 평균 (끝난 구간만)")
    for t in T:
        hs = [h for h in rows if h["t"] == t and h["rec"] is not None]
        if hs:
            print(f"  {KO[t]}: {len(hs)}번 · 전고점 회복 평균 {sum(h['rec'] for h in hs) / len(hs):.0f}일 · 최장 {max(h['rec'] for h in hs)}일 · "
                  f"산 뒤 더 빠진 폭 평균 {sum(h['more'] for h in hs) / len(hs) * 100:.0f}%")
    print("\n■ 빅7 똑같이 나눠 담기 (2012-05-18 ~ 2026-11-20)")
    for name, mode in (("그냥 들고 있기", None), ("분기마다 비율 맞추기", "q")):
        x, cagr, mdd, now = stats(portfolio(rebalance_every=mode))
        print(f"  {name}: {x:.1f}배 · 연 {cagr * 100:.1f}% · 최대 낙폭 {mdd * 100:.0f}% · 지금 고점 대비 {now * 100:.1f}%")
    for name, mode in (("그냥 들고 있기", None), ("분기마다 비율 맞추기", "q")):
        x, cagr, mdd, now = stats(portfolio(start="2021-11-19", rebalance_every=mode))
        print(f"  [2021-11 고점에 시작] {name}: {x:.2f}배 · 최대 낙폭 {mdd * 100:.0f}%")


if __name__ == "__main__":
    main()
