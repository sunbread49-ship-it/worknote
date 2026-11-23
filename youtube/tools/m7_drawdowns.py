"""빅테크 7 하락 구간 분석 (assets/data/m7/*.csv · 2010~)
- 고점 대비 -20% 넘게 빠진 구간: 고점 · 바닥 · 깊이 · 원금 회복까지 걸린 날
- '고점 대비 -X%에 처음 닿은 날' 샀다면: 그 뒤 더 빠진 폭 · 1년 뒤 · 3년 뒤 수익률
"""
import csv
from datetime import date
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "assets" / "data" / "m7"
NAMES = {"googl": "구글", "aapl": "애플", "msft": "마이크로소프트", "amzn": "아마존", "meta": "메타", "nvda": "엔비디아", "tsla": "테슬라", "qqq": "나스닥100(QQQ)"}


def load(t):
    r = [(x["date"], float(x["close"])) for x in csv.DictReader(open(D / f"{t}.csv"))]
    return [x for x in r if x[0] != "2011-01-13"]   # 애플 데이터 오류 1줄


def d(s):
    return date.fromisoformat(s)


def episodes(r, th=-0.20):
    out, peak, low, inside = [], r[0], None, False
    for i, (dt, c) in enumerate(r):
        if c >= peak[1]:
            if inside:
                out.append({"peak": peak, "low": low, "rec": (dt, c)})
                inside = False
            peak, low = (dt, c), None
            continue
        if low is None or c < low[1]:
            low = (dt, c)
        if c / peak[1] - 1 <= th:
            inside = True
    if inside:
        out.append({"peak": peak, "low": low, "rec": None})
    return out


def after(r, i, days):
    tgt = d(r[i][0]).toordinal() + days
    for dt, c in r[i:]:
        if d(dt).toordinal() >= tgt:
            return c / r[i][1] - 1
    return None


def entry_table(r, levels=(-0.2, -0.25, -0.3, -0.35, -0.4)):
    rows = []
    for lv in levels:
        peak = r[0]
        hits = []
        armed = True
        for i, (dt, c) in enumerate(r):
            if c > peak[1]:
                peak = (dt, c)
                armed = True
            if armed and c / peak[1] - 1 <= lv:
                lo = min(x[1] for x in r[i:]) if False else None
                # 그 뒤 원금 회복(고점 회복) 전까지 최저점
                j, mn = i, c
                while j < len(r) and r[j][1] < peak[1]:
                    mn = min(mn, r[j][1])
                    j += 1
                hits.append({"date": dt, "price": c, "more": mn / c - 1, "y1": after(r, i, 365), "y3": after(r, i, 365 * 3),
                             "peak": peak[0]})
                armed = False
        rows.append((lv, hits))
    return rows


def main():
    for t in NAMES:
        r = load(t)
        last = r[-1]
        ath = max(r, key=lambda x: x[1])
        print(f"\n■ {NAMES[t]} · 지금 {last[0]} {last[1]:.2f} · 최고 {ath[0]} {ath[1]:.2f} · 고점 대비 {(last[1] / ath[1] - 1) * 100:.1f}%")
        for e in episodes(r):
            depth = e["low"][1] / e["peak"][1] - 1
            rec = e["rec"]
            days = (d(rec[0]) - d(e["peak"][0])).days if rec else None
            print(f"  -20%↓ 구간: 고점 {e['peak'][0]} → 바닥 {e['low'][0]} ({depth * 100:.1f}%) · 고점 회복 "
                  f"{rec[0] + f' ({days}일)' if rec else '아직'}")
    r = load("googl")
    print("\n■ 구글: 고점 대비 -X%에 처음 닿은 날 샀다면")
    for lv, hits in entry_table(r):
        for h in hits:
            print(f"  {lv * 100:.0f}% · {h['date']} {h['price']:.1f} · 그 뒤 더 빠진 폭 {h['more'] * 100:.1f}% · 1년 뒤 "
                  f"{'-' if h['y1'] is None else f'{h[chr(121) + chr(49)] * 100:+.0f}%'} · 3년 뒤 {'-' if h['y3'] is None else f'{h[chr(121) + chr(51)] * 100:+.0f}%'}")


if __name__ == "__main__":
    main()
