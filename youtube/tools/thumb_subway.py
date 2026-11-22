"""지식창고 롱폼 '지하철 노선 색깔' 썸네일 10종 — 아이보리 종이 · 노선도 · 색 견본 · 명조 · 손글씨 · 지식 악어새
  python tools/thumb_subway.py → out/sci02_subway_colors/thumbs10/T01~T10 + 비교표
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import editorial as E  # noqa: E402
import thumb_seoul as TS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out/sci02_subway_colors/thumbs10"
W, H = 1920, 1080
INK, RED = (34, 36, 48), (196, 36, 40)
M = E._metro()
COL = {k: tuple(v) for k, v in M["colors"].items()}


def metro_map(box, lines=None, focus=None, old=None, width=22):
    d0 = E._seoul()
    gs = [n for n in d0 if not n.startswith("_")]
    pts = [p for n in gs for poly in d0[n] for p in poly]
    lon0, lon1 = min(p[0] for p in pts), max(p[0] for p in pts)
    lat0, lat1 = min(p[1] for p in pts), max(p[1] for p in pts)
    kx = math.cos(math.radians(37.55))
    sc = min((box[2] - box[0]) / ((lon1 - lon0) * kx), (box[3] - box[1]) / (lat1 - lat0))
    ox = box[0] + ((box[2] - box[0]) - (lon1 - lon0) * kx * sc) / 2
    oy = box[1] + ((box[3] - box[1]) - (lat1 - lat0) * sc) / 2
    P = lambda lo, la: (ox + (lo - lon0) * kx * sc, oy + (lat1 - la) * sc)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for n in gs:
        for poly in d0[n]:
            d.polygon([P(*p) for p in poly], fill=(236, 228, 210, 255), outline=(190, 180, 160, 255), width=3)
    lines = [str(x) for x in (lines or range(1, 10))]
    focus = {str(x) for x in (focus or [])}
    old = {str(x) for x in (old or [])}
    for l in [x for x in lines if x not in focus] + [x for x in lines if x in focus]:
        c = tuple(M["old"][l]) if l in old else COL[l]
        a = 70 if focus and l not in focus else 255
        w = width // 2 if focus and l not in focus else width
        pp = [P(*p) for p in M["lines"][l]]
        d.line(pp, fill=(255, 255, 255, a), width=w + 10, joint="curve")
        d.line(pp, fill=c + (a,), width=w, joint="curve")
    sh = im.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.35))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(Image.merge("RGBA", (Image.new("L", (W, H), 0),) * 3 + (sh,)), (10, 16))
    out.alpha_composite(im)
    return out


def chip(col, w=200, h=260, label="", strike=False, tilt=0):
    c = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((8, 8, w + 8, h + 8), fill=(252, 250, 244, 255), outline=(200, 190, 170, 255), width=3)
    d.rectangle((20, 20, w - 4, int(h * 0.7)), fill=tuple(col) + (255,))
    if strike:
        d.line((20, 20, w - 4, int(h * 0.7)), fill=(255, 255, 255, 255), width=10)
    if label:
        t = E._ink(label, "NanumMyeongjo-ExtraBold.ttf", int(h * 0.15), INK)
        c.alpha_composite(t, ((c.width - t.width) // 2, int(h * 0.72)))
    return c.rotate(tilt, expand=True, resample=Image.BICUBIC)


def title(f, txt, xy, size=170, first=INK, rest=RED, stroke=6):
    x, y = xy
    for i, ln in enumerate(txt.split("\n")):
        im = TS.text(ln, "NanumMyeongjo-ExtraBold.ttf", size, first if i == 0 else rest, stroke=stroke)
        f.alpha_composite(im, (x, y))
        y += im.height - 10
    return y


def sticker(d=230):
    return E._sticker_profile(d)


def make(sp):
    f = E.paper_bg((247, 241, 228)).convert("RGBA").resize((W, H))
    v = sp["v"]
    if v == "map":
        f.alpha_composite(metro_map((820, 40, 1900, 1060), sp.get("lines"), sp.get("focus"), sp.get("old")))
        if sp.get("kicker"):
            f.alpha_composite(TS.text(sp["kicker"], "NanumPenScript-Regular.ttf", 92, RED), (70, 80))
        y = title(f, sp["title"], (60, 190), sp.get("size", 170))
        if sp.get("sub"):
            f.alpha_composite(TS.text(sp["sub"], "NanumPenScript-Regular.ttf", 84, INK), (80, y + 10))
    elif v == "chips":
        cs = sp["chips"]
        n = len(cs)
        cw = min(300, int(1760 / n) - 20)
        x = (W - n * (cw + 20)) // 2
        for i, c in enumerate(cs):
            im = chip(c[0], cw, int(cw * 1.3), c[1], c[2] if len(c) > 2 else False, [-3, 2, -2, 3][i % 4])
            f.alpha_composite(im, (x + i * (cw + 20), sp.get("chip_y", 470)))
        title(f, sp["title"], (60, 40), sp.get("size", 150))
    elif v == "photo":
        p = TS.polaroid(sp["photo"], 760, 520, sp["cap"], -4)
        f.alpha_composite(p, (W - p.width - 40, 220))
        y = title(f, sp["title"], (60, 120), sp.get("size", 160))
        if sp.get("sub"):
            f.alpha_composite(TS.text(sp["sub"], "NanumPenScript-Regular.ttf", 84, INK), (80, y + 10))
    elif v == "collage":
        f.alpha_composite(metro_map((1100, 420, 1900, 1070), width=16))
        for (ph, cap, tl, xy) in sp["photos"]:
            f.alpha_composite(TS.polaroid(ph, 420, 290, cap, tl), xy)
        title(f, sp["title"], (60, 580), sp.get("size", 150))
    s = sticker(sp.get("sticker", 200))
    f.alpha_composite(s, (W - s.width - 30, H - s.height - 20) if v != "map" else (40, H - s.height - 30))
    tag = TS.text("악어새 지식창고, 한 번에 정리", "NanumPenScript-Regular.ttf", 46, (120, 110, 92))
    f.alpha_composite(tag, (W - tag.width - 40, 20))
    return f.convert("RGB")


R1 = (220, 40, 40)
SPECS = [
    {"name": "T01", "v": "map", "kicker": "매일 타는데 몰랐던", "title": "지하철 색깔의\n비밀", "sub": "2호선은 왜 초록?"},
    {"name": "T02", "v": "map", "lines": [1], "focus": [1], "old": [1], "kicker": "1974년 개통", "title": "1호선은\n원래 빨강", "size": 190},
    {"name": "T03", "v": "chips", "chips": [(R1, "1"), (COL["2"], "2"), (COL["3"], "3"), (COL["4"], "4"), (COL["5"], "5")], "title": "노선 색깔에\n무지개 규칙?"},
    {"name": "T04", "v": "chips", "chips": [((200, 30, 140), "마젠타"), ((189, 160, 90), "골드"), ((246, 244, 238), "화이트"), ((30, 30, 34), "블랙")], "title": "9호선 색은\n투표로 뽑았다"},
    {"name": "T05", "v": "photo", "photo": "sub_crowded", "cap": "출근길 9호선", "title": "골드라인\n→ 지옥철", "sub": "금색이 된 진짜 이유"},
    {"name": "T06", "v": "map", "lines": [1], "focus": [1], "old": [1], "kicker": "같은 열차, 다른 색", "title": "서울역이\n환승역?", "sub": "빨강 1호선의 비밀"},
    {"name": "T07", "v": "map", "lines": [1, 2], "focus": [2], "old": [1], "kicker": "빨강의 반대색", "title": "2호선이\n초록인 이유", "size": 160},
    {"name": "T08", "v": "chips", "chips": [((30, 30, 34), "블랙"), ((189, 160, 90), "골드")], "title": "검정 지하철\n될 뻔했다", "size": 160},
    {"name": "T09", "v": "collage", "title": "지하철 노선 색깔\n한 번에 정리", "photos": [("sub_platform", "승강장", -5, (60, 40)), ("sub_car", "9호선 열차", 4, (560, 70)), ("sub_station", "역 안내판", -3, (1080, 30))]},
    {"name": "T10", "v": "chips", "chips": [(R1, "1", True), (COL["1"], "1")], "title": "빨간 1호선은\n어디 갔을까?", "size": 150},
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    outs = []
    for sp in SPECS:
        im = make(sp).resize((1280, 720), Image.LANCZOS)
        p = OUT / f"{sp['name']}.png"
        im.save(p)
        outs.append((sp["name"], p))
    sheet = Image.new("RGB", (2 * 650 + 10, 5 * 400 + 10), (20, 20, 24))
    from engine import draw as G
    for i, (nm, p) in enumerate(outs):
        x, y = 10 + (i % 2) * 650, 10 + (i // 2) * 400
        sheet.paste(Image.open(p).resize((640, 360)), (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + 364), nm, fill=(180, 255, 60))
    sheet.save(OUT / "비교표.jpg", quality=90)
    print("비교표 →", OUT / "비교표.jpg")
