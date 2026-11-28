"""빅7 공식 실적 (SEC EDGAR XBRL companyfacts · 허용 호스트 data.sec.gov)
  python3 tools/sec_facts.py → assets/data/m7/sec_<티커>.json(원본) + 실적요약.txt
분기 매출 · 순이익(최근 8분기) · 연간(최근 3년)
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "data" / "m7"
CIK = {"GOOGL": 1652044, "AAPL": 320193, "MSFT": 789019, "AMZN": 1018724, "META": 1326801, "NVDA": 1045810, "TSLA": 1318605}
REV = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]
UA = {"User-Agent": "worknote-research contact@example.com"}   # SEC는 연락처 형식 UA를 요구 (개인 정보 아님)


def facts(t):
    p = OUT / f"sec_{t.lower()}.json"
    if not p.exists():
        u = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK[t]:010d}.json"
        p.write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read())
        time.sleep(0.3)
    return json.loads(p.read_text())


def series(f, tags, annual):
    best = {}
    for tag in tags:
        u = f["facts"].get("us-gaap", {}).get(tag, {}).get("units", {}).get("USD", [])
        for x in u:
            if "frame" not in x:
                continue
            fr = x["frame"]
            if annual and len(fr) == 6:        # CY2025
                best.setdefault(fr, x["val"])
            if not annual and len(fr) == 8 and "Q" in fr:   # CY2025Q3
                best.setdefault(fr, x["val"])
    return dict(sorted(best.items()))


def main():
    lines = []
    for t in CIK:
        f = facts(t)
        rq, nq = series(f, REV, False), series(f, ["NetIncomeLoss"], False)
        ra, na = series(f, REV, True), series(f, ["NetIncomeLoss"], True)
        lines.append(f"■ {t} ({f.get('entityName')})")
        lines.append("  연간: " + " · ".join(f"{k} 매출 {ra[k] / 1e9:.1f}B 순익 {na.get(k, 0) / 1e9:.1f}B" for k in list(ra)[-3:]))
        lines.append("  분기: " + " · ".join(f"{k} {rq[k] / 1e9:.1f}B/{nq.get(k, 0) / 1e9:.1f}B" for k in list(rq)[-8:]))
    (OUT / "실적요약.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
