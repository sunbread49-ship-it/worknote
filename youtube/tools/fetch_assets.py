"""폰트·시세 데이터를 assets/ 로 내려받는다. (최초 1회, 데이터 갱신 시 재실행)

  python tools/fetch_assets.py          # 없는 것만 받기
  python tools/fetch_assets.py --data   # 시세 데이터만 강제로 새로 받기
"""
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PRET = "https://raw.githubusercontent.com/orioncactus/pretendard/main/packages/pretendard/dist/public/static/Pretendard-{}.otf"
FONTS = {f"fonts/Pretendard-{w}.otf": PRET.format(w)
         for w in ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]}
FONTS["fonts/LICENSE-Pretendard.txt"] = "https://raw.githubusercontent.com/orioncactus/pretendard/main/LICENSE"

# Microsoft Fluent UI Emoji 3D (MIT 라이선스, 상업적 사용 가능) → 스티커/짤 용도
FLUENT = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/"
EMOJI = {
    "rocket": "Rocket", "gem": "Gem stone", "fire": "Fire", "skull": "Skull", "scream": "Face screaming in fear",
    "clown": "Clown face", "down": "Chart decreasing", "up": "Chart increasing", "money_wings": "Money with wings",
    "slot": "Slot machine", "monocle": "Face with monocle", "thinking": "Thinking face", "moneybag": "Money bag",
    "explode": "Exploding head", "cry": "Loudly crying face", "cool": "Smiling face with sunglasses",
    "warning": "Warning", "bomb": "Bomb", "boom": "Collision", "100": "Hundred points",
    "rollercoaster": "Roller coaster", "eyes": "Eyes", "party": "Party popper", "melting": "Melting face",
    "coffin": "Coffin", "hourglass": "Hourglass not done", "dice": "Game die", "ghost": "Ghost",
    "hands": "Raising hands*", "pray": "Folded hands*", "check": "Check mark button", "x": "Cross mark",
    "stop": "Stop sign", "sweat": "Downcast face with sweat", "joy": "Face with tears of joy", "zzz": "Zzz",
    "liberty": "Statue of liberty", "popcorn": "Popcorn", "brain": "Brain", "snail": "Snail", "zap": "High voltage",
    "ant": "Ant", "bear": "Bear", "ox": "Ox", "banknote": "Dollar banknote", "magnifier": "Magnifying glass tilted left",
    "point_up": "Index pointing up*", "thumbsup": "Thumbs up*", "megaphone": "Megaphone", "receipt": "Receipt",
    "cityscape": "Cityscape", "bulb": "Light bulb", "seedling": "Seedling", "turtle": "Turtle", "chart": "Bar chart",
    "coin": "Coin", "abacus": "Abacus", "sparkles": "Sparkles",
    # 포스터 실루엣용 (검게 칠해서 씀)
    "turkey": "Turkey", "pumpkin": "Jack-o-lantern", "runner": "Person running*", "eagle": "Eagle",
    "bull": "Water buffalo", "flag_us": "Flag: United States", "capitol": "Classical building", "santa": "Santa Claus*",
    "rabbit": "Rabbit", "sailboat": "Sailboat", "mountain": "Mountain", "wave": "Water wave", "anchor": "Anchor",
}


def emoji_url(name):
    skin = name.endswith("*")
    name = name.rstrip("*")
    fn = name.lower().replace(" ", "_")
    p = f"{name}/Default/3D/{fn}_3d_default.png" if skin else f"{name}/3D/{fn}_3d.png"
    return FLUENT + urllib.parse.quote(p)


EMOJIS = {f"emoji/{k}.png": emoji_url(v) for k, v in EMOJI.items()}
EMOJIS["emoji/LICENSE-fluentui-emoji.txt"] = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/LICENSE"

# 공개 데이터셋(datasets.io, GitHub 미러). 실제 시세.
# 일간 ETF/지수: Yahoo Finance 일간 시세를 매일 갱신하는 공개 저장소 미러(두 저장소 값 대조 확인, 오차 <0.001%)
DAILY = "https://raw.githubusercontent.com/alm0421/alm0421/main/data/prices/{}.csv"
DATA = {
    "data/tqqq_daily.csv": DAILY.format("TQQQ"),
    "data/sqqq_daily.csv": DAILY.format("SQQQ"),
    "data/qqq_daily.csv": DAILY.format("QQQ"),
    "data/ndx_daily.csv": DAILY.format("%5ENDX"),
    "data/spx_daily.csv": DAILY.format("%5EGSPC"),
    "data/nvda_daily.csv": DAILY.format("NVDA"),
    "data/msft_daily.csv": DAILY.format("MSFT"),
    "data/aapl_daily.csv": DAILY.format("AAPL"),
    "data/amd_daily.csv": DAILY.format("AMD"),
    "data/smh_daily.csv": DAILY.format("SMH"),
    "data/soxx_daily.csv": DAILY.format("SOXX"),
    "data/intc_daily.csv": DAILY.format("INTC"),
    "data/mu_daily.csv": DAILY.format("MU"),
    "data/tsm_daily.csv": DAILY.format("TSM"),
    # S&P500 월평균 지수 1871~ (Robert Shiller 데이터 기반, 매월 갱신)
    # 지도 (공개 GeoJSON)
    "geo/us_states.json": "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
    "geo/world.json": "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json",
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


def naver_stock(code, name, force=False):
    """국내 종목 일별(네이버 차트) — 000660 SK하이닉스, 005930 삼성전자"""
    import json, re
    dst = ASSETS / "data" / f"{name}_daily.csv"
    if dst.exists() and not force:
        return
    u = (f"https://fchart.stock.naver.com/siseJson.nhn?symbol={code}&requestType=1"
         "&startTime=19900101&endTime=20991231&timeframe=day")
    txt = urllib.request.urlopen(u, timeout=60).read().decode("utf-8", "ignore")
    with open(dst, "w") as f:
        f.write("date,open,high,low,close,volume\n")
        for l in txt.splitlines():
            l = l.strip()
            if not l.startswith('["'):
                continue
            p = json.loads(re.sub(r",\s*,", ",null,", re.sub(r",\s*]", "]", l.rstrip(","))))
            f.write(f"{p[0][:4]}-{p[0][4:6]}-{p[0][6:]},{p[1]},{p[2]},{p[3]},{p[4]},{p[5] if len(p) > 5 else ''}\n")


def kospi(force=False):
    """코스피 일별(1990~) — 네이버 차트 데이터 (환경 허용 호스트: fchart.stock.naver.com)"""
    import json
    dst = ASSETS / "data" / "kospi_daily.csv"
    if dst.exists() and not force:
        return
    print("받는 중: data/kospi_daily.csv")
    u = ("https://fchart.stock.naver.com/siseJson.nhn?symbol=KOSPI&requestType=1"
         "&startTime=19800101&endTime=20991231&timeframe=day")
    txt = urllib.request.urlopen(u, timeout=60).read().decode("utf-8", "ignore")
    rows = [json.loads(l.strip().rstrip(",")) for l in txt.splitlines() if l.strip().startswith('["')]
    with open(dst, "w") as f:
        f.write("date,open,high,low,close,volume,foreign_ratio\n")
        for p in rows:
            f.write(f"{p[0][:4]}-{p[0][4:6]}-{p[0][6:]},{p[1]},{p[2]},{p[3]},{p[4]},{p[5]},{p[6]}\n")


def main():
    force_data = "--data" in sys.argv
    for rel, url in FONTS.items():
        get(rel, url)
    for rel, url in EMOJIS.items():
        try:
            get(rel, url)
        except Exception as e:  # 이모지 하나 실패해도 계속
            print("  실패:", rel, e)
    for rel, url in DATA.items():
        get(rel, url, force=force_data)
    for code, nm in (("000660", "skhynix"), ("005930", "samsung")):
        try:
            naver_stock(code, nm, force_data)
        except Exception as e:
            print("  실패:", nm, e)
    try:
        kospi(force_data)
    except Exception as e:
        print("  실패: 코스피", e)
    print("완료 →", ASSETS)


if __name__ == "__main__":
    main()
