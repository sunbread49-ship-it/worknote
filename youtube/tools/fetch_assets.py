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
    print("완료 →", ASSETS)


if __name__ == "__main__":
    main()
