"""빅테크 7(매그니피센트 7) 일별 시세 — 네이버 해외주식 차트 API (허용 호스트: api.stock.naver.com)
  python3 tools/fetch_m7.py  → assets/data/m7/<티커>.csv (date,open,high,low,close,volume)
"""
import csv
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "data" / "m7"
TICKERS = {"GOOGL": "GOOGL.O", "AAPL": "AAPL.O", "MSFT": "MSFT.O", "AMZN": "AMZN.O", "META": "META.O", "NVDA": "NVDA.O", "TSLA": "TSLA.O",
           "QQQ": "QQQ.O"}


def get(code, y0, y1):
    u = (f"https://api.stock.naver.com/chart/foreign/item/{code}/day?startDateTime={y0}01010000&endDateTime={y1}12312359")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for t, code in TICKERS.items():
        rows = {}
        for y0 in range(1996, 2027, 5):   # 5년씩 나눠 받기
            try:
                for r in get(code, y0, min(y0 + 4, 2026)):
                    d = r["localDate"]
                    rows[d] = (f"{d[:4]}-{d[4:6]}-{d[6:]}", r["openPrice"], r["highPrice"], r["lowPrice"], r["closePrice"],
                               r.get("accumulatedTradingVolume", 0))
            except Exception as e:
                print(t, y0, "실패", str(e)[:60])
            time.sleep(0.4)
        with open(OUT / f"{t.lower()}.csv", "w", newline="") as fp:
            w = csv.writer(fp)
            w.writerow(["date", "open", "high", "low", "close", "volume"])
            for k in sorted(rows):
                w.writerow(rows[k])
        ks = sorted(rows)
        print(t, len(ks), ks[0] if ks else "-", ks[-1] if ks else "-")


if __name__ == "__main__":
    main()
