"""폰트·시세 데이터를 assets/ 로 내려받는다. (최초 1회, 데이터 갱신 시 재실행)

  python tools/fetch_assets.py          # 없는 것만 받기
  python tools/fetch_assets.py --data   # 시세 데이터만 강제로 새로 받기
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PRET = "https://raw.githubusercontent.com/orioncactus/pretendard/main/packages/pretendard/dist/public/static/Pretendard-{}.otf"
FONTS = {f"fonts/Pretendard-{w}.otf": PRET.format(w)
         for w in ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]}
FONTS["fonts/LICENSE-Pretendard.txt"] = "https://raw.githubusercontent.com/orioncactus/pretendard/main/LICENSE"

# 공개 데이터셋(datasets.io, GitHub 미러). 실제 시세.
DATA = {
    # S&P500 월평균 지수 1871~ (Robert Shiller 데이터 기반, 매월 갱신)
    "data/sp500_monthly.csv": "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv",
    # CBOE VIX 일간 1990~
    "data/vix_daily.csv": "https://raw.githubusercontent.com/datasets/finance-vix/main/data/vix-daily.csv",
}


def get(rel, url, force=False):
    dst = ASSETS / rel
    if dst.exists() and not force:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    print("받는 중:", rel)
    with urllib.request.urlopen(url, timeout=60) as r:
        dst.write_bytes(r.read())


def main():
    force_data = "--data" in sys.argv
    for rel, url in FONTS.items():
        get(rel, url)
    for rel, url in DATA.items():
        get(rel, url, force=force_data)
    print("완료 →", ASSETS)


if __name__ == "__main__":
    main()
