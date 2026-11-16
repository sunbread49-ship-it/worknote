"""커버드콜 ETF 데이터 (EP017): 국내 = 네이버 차트 종가 + funetf 분배금(과세표준 포함) · 미국 = 일간 수정 전 종가 + 배당
  python tools/cc_data.py   → assets/data/cc/<code>_price.csv · <code>_div.csv
"""
import json, re, urllib.request
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "assets" / "data" / "cc"
UA = {"User-Agent": "Mozilla/5.0"}
KR = {"498400": ("KR7498400001", "K55105EG3659"), "472150": ("KR7472150002", "K55301DY9046"),
      "458760": ("KR7458760006", "K55301E27659"), "441640": ("KR7441640000", "K55105DW2744"),
      "069500": ("KR7069500007", "KR5105352888"), "458730": ("KR7458730009", "K55301E27634"),
      "133690": ("KR7133690008", "KR5225652084")}
US = ["JEPQ", "JEPI", "QQQI", "QQQ", "SCHD", "SPY", "QYLD"]


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "ignore")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for c, (isin, fund) in KR.items():
        t = get(f"https://fchart.stock.naver.com/siseJson.nhn?symbol={c}&requestType=1&startTime=19900101&endTime=20991231&timeframe=day")
        rows = re.findall(r'\["(\d{8})",\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)', t)
        (OUT / f"{c}_price.csv").write_text("date,close\n" + "".join(f"{d[:4]}-{d[4:6]}-{d[6:]},{cl}\n" for d, o, h, l, cl in rows))
        divs = []
        for page in range(0, 20):
            js = json.loads(get(f"https://www.funetf.co.kr/api/public/product/view/etfdividend?itemId={isin}&fundCd={fund}&page={page}&size=50") or "[]")
            if not js:
                break
            divs += js
            if len(divs) >= js[0].get("total", 0):
                break
        seen = {}
        for d in divs:
            seen[d["gijunYmd"]] = d
        lines = ["date,amount,taxable\n"] + [f"{k[:4]}-{k[4:6]}-{k[6:]},{v['divAmt']},{v.get('taxDividAmt') or v['divAmt']}\n" for k, v in sorted(seen.items())]
        (OUT / f"{c}_div.csv").write_text("".join(lines))
        print(c, len(rows), "days ·", len(seen), "분배")
    for s in US:
        t = get(f"https://raw.githubusercontent.com/alm0421/alm0421/main/data/prices/{s}.csv")
        (OUT / f"{s.lower()}_raw.csv").write_text(t)
        print(s, t.count("\n"))


if __name__ == "__main__":
    main()
