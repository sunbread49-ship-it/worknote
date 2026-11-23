"""EP024 '구글 -34%, 지금 사도 될까?' 썸네일 10종 (실사 위주 · CCN: 3초 안에 '구글 -34% → 지금 사? 말아?')
  python tools/thumb_google.py → out/ep024_google/thumbs10/T01~T10 + 비교표
사진: 선다 피차이(Lukasz Kobus/European Commission, CC BY 4.0) · 구글 본사/로고/검색 화면/차트 (Unsplash)
"""
import csv
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402
from engine import draw as G  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/ep024_google/thumbs10"
W, H = TH.W, TH.H
YEL, RED, WHITE, MINT, BLUE = (255, 214, 40), (255, 60, 60), (255, 255, 255), (90, 230, 170), (66, 133, 244)
GOOGL = [(r["date"], float(r["close"])) for r in csv.DictReader(open(ROOT / "assets/data/m7/googl.csv"))]
EPIS = ["2011-06-24", "2018-12-24", "2020-03-23", "2022-11-03", "2024-09-10", "2025-04-08", "2026-03-30", "2026-11-20"]


def chart(w, h, start="2010-07-01", color=WHITE, lw=8, dots=False, log=True, last_red=True):
    ks = [x for x in GOOGL if x[0] >= start]
    vs = [math.log(c) if log else c for _, c in ks]
    lo, hi = min(vs), max(vs)
    P = lambda i, v: (40 + i / (len(ks) - 1) * (w - 80), h - 50 - (v - lo) / (hi - lo) * (h - 110))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pts = [P(i, v) for i, v in enumerate(vs)][::2]
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).line(pts, fill=color + (150,), width=lw * 4, joint="curve")
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.line(pts, fill=color + (255,), width=lw, joint="curve")
    if dots:
        idx = {dt: i for i, (dt, _) in enumerate(ks)}
        for k, dt in enumerate(EPIS):
            if dt in idx:
                x, y = P(idx[dt], vs[idx[dt]])
                r = 26 if k == len(EPIS) - 1 else 18
                c = RED if k == len(EPIS) - 1 else (255, 150, 150)
                d.ellipse((x - r, y - r, x + r, y + r), fill=c + (255,), outline=WHITE + (255,), width=5)
    elif last_red:
        x, y = P(len(vs) - 1, vs[-1])
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=RED + (255,), outline=WHITE + (255,), width=5)
    return im


def photo(name, w, h, focus=(0.5, 0.5), dark=0.35, gray=0.15):
    return TH.photo_fill(name, w, h, focus=focus, dark=dark, gray=gray)


def shade(f, side="left", width=0.65, strength=235):
    import numpy as np
    g = np.zeros((H, W), "float32")
    xs = np.linspace(0, 1, W)
    if side == "left":
        g[:] = np.clip(1 - xs / width, 0, 1) ** 1.2
    elif side == "bottom":
        g[:] = np.clip((np.linspace(0, 1, H)[:, None] - (1 - width)) / width, 0, 1) ** 1.2
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.putalpha(Image.fromarray((g * strength).astype("uint8")))
    f.alpha_composite(lay)


def big(text, size, maxw, color=WHITE, hl="", hl_color=RED):
    return TH.fit(text, size, maxw, color=color, hl=hl, hl_color=hl_color)


def pill(text, size=60, bg=RED, fg=WHITE):
    return G.pill(text, "Black", size, fg, bg, pad=(30, 12), radius=14)


def bars(sp):
    """빅7 회복 속도 막대 (구글만 공개, 나머지 '?')"""
    names = [("MS", 235), ("애플", 266), ("구글", 304), ("메타", 351), ("아마존", 352), ("테슬라", 390), ("엔비디아", 502)]
    im = Image.new("RGBA", (1100, 700), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (n, v) in enumerate(names):
        y = 10 + i * 96
        g = n == "구글"
        ln = int(v / 502 * 700)
        d.rounded_rectangle((260, y, 260 + ln, y + 78), 18, fill=(BLUE if g else (70, 78, 100)) + (255,))
        t = TH.T(n if g or sp.get("show") else "?", 58, YEL if g else WHITE)
        im.alpha_composite(t, (230 - t.width, y + 6))
        if g:
            r = TH.T("?위", 54, YEL)   # 답은 영상에서
            im.alpha_composite(r, (260 + ln + 20, y + 8))
    return im


def make(sp):
    v = sp["v"]
    f = Image.new("RGBA", (W, H), (8, 10, 18, 255))
    if v == "hq":            # 구글 본사 + 하락 차트 + 큰 -34%
        f.alpha_composite(photo("g_hq_logo", W, H, focus=(0.55, 0.3), dark=0.45))
        shade(f, "bottom", 0.7, 230)
        ch = chart(1840, 520, start="2025-06-01", color=WHITE, log=False)
        f.alpha_composite(ch, (40, 300))
        TH.shadowed(f, big(sp["big"], 330, 1100, color=RED), (60, 30))
        b = big(sp["bottom"], 170, 1800, color=YEL, hl=sp.get("hl", ""), hl_color=WHITE)
        TH.shadowed(f, b, (60, H - b.height - 50))
    elif v == "ceo":         # 선다 피차이 오른쪽 + 왼쪽 글
        f.alpha_composite(photo("g_pichai", 900, H, focus=(0.5, 0.2), dark=0.15, gray=0.1), (W - 900, 0))
        shade(f, "left", 0.72, 255)
        TH.shadowed(f, pill(sp["tag"], 64), (70, 70))
        TH.shadowed(f, big(sp["big"], 300, 1150, color=RED), (60, 200))
        b = big(sp["bottom"], 150, 1150, color=YEL, hl=sp.get("hl", ""), hl_color=WHITE)
        TH.shadowed(f, b, (70, H - b.height - 70))
    elif v == "crash":       # 로고 벽 + 역대 최악의 하루
        f.alpha_composite(photo("g_logo_wall", W, H, focus=(0.4, 0.5), dark=0.5, gray=0.25))
        tint = Image.new("RGBA", (W, H), (120, 0, 0, 90))
        f.alpha_composite(tint)
        TH.shadowed(f, pill(sp["tag"], 66), (70, 70))
        TH.shadowed(f, big(sp["big"], 360, 1800, color=WHITE, hl=sp.get("hl_big", ""), hl_color=RED), (W / 2, 330), "mt")
        b = big(sp["bottom"], 150, 1800, color=YEL)
        TH.shadowed(f, b, (W / 2, H - b.height - 70), "mt")
    elif v == "dots":        # 16년 차트 + -20% 하락 8번 점
        f = TH.bg_dark((20, 40, 110), (0.5, 0.5))
        f.alpha_composite(chart(1840, 680, dots=True), (40, 250))
        TH.shadowed(f, big(sp["top"], 140, 1800, color=WHITE, hl=sp.get("hl_top", ""), hl_color=RED), (60, 40))
        b = big(sp["bottom"], 150, 1100, color=YEL, hl=sp.get("hl", ""), hl_color=RED)
        TH.shadowed(f, b, (W - b.width - 60, H - b.height - 60))
    elif v == "bars":
        f = TH.bg_dark((20, 50, 120), (0.7, 0.5))
        f.alpha_composite(photo("g_pichai", 620, H, focus=(0.5, 0.25), dark=0.3, gray=0.2), (0, 0))
        shade(f, "left", 0.42, 120)
        TH.shadowed(f, bars(sp), (700, 350))
        TH.shadowed(f, big(sp["top"], 130, 1250, color=WHITE, hl=sp.get("hl", ""), hl_color=YEL), (680, 60))
    elif v == "phone":       # 검색 화면 + AI 질문
        f.alpha_composite(photo("g_search_phone", W, H, focus=(0.45, 0.4), dark=0.3, gray=0.1))
        shade(f, "left", 0.7, 245)
        TH.shadowed(f, big(sp["top"], 150, 1100, color=WHITE, hl=sp.get("hl_top", ""), hl_color=YEL), (70, 80))
        TH.shadowed(f, big(sp["big"], 300, 1100, color=RED), (60, 330))
        b = big(sp["bottom"], 120, 1100, color=YEL)
        TH.shadowed(f, b, (70, H - b.height - 70))
    elif v == "vs":
        f.alpha_composite(photo("crash_screen", W, H, dark=0.6, gray=0.3))
        for i, (t, s, c) in enumerate(sp["cards"]):
            cd = Image.new("RGBA", (780, 520), (0, 0, 0, 0))
            ImageDraw.Draw(cd).rounded_rectangle((0, 0, 779, 519), 40, fill=(18, 20, 30, 235), outline=c + (255,), width=8)
            a = TH.fit(t, 130, 700, color=c)
            cd.alpha_composite(a, ((780 - a.width) // 2, 70))
            b = TH.fit(s, 64, 700, color=WHITE, weight="Bold")
            cd.alpha_composite(b, ((780 - b.width) // 2, 300))
            TH.shadowed(f, cd, (100 + i * 940, 380))
        TH.shadowed(f, TH.T("VS", 170, YEL), (W / 2, 640), "mm")
        TH.shadowed(f, big(sp["top"], 150, 1800, color=WHITE, hl=sp.get("hl", ""), hl_color=RED), (W / 2, 60), "mt")
    elif v == "money":       # 1초에 560만 원 vs -34%
        f.alpha_composite(photo("g_hq_logo", W, H, focus=(0.5, 0.3), dark=0.55, gray=0.2))
        TH.shadowed(f, big(sp["top"], 130, 1800, color=WHITE, hl=sp.get("hl_top", ""), hl_color=MINT), (W / 2, 60), "mt")
        TH.shadowed(f, big(sp["big"], 280, 1800, color=MINT), (W / 2, 300), "mt")
        b = big(sp["bottom"], 160, 1800, color=YEL, hl=sp.get("hl", ""), hl_color=RED)
        TH.shadowed(f, b, (W / 2, H - b.height - 60), "mt")
    elif v == "screen":      # 빨간 캔들 + 질문
        f.alpha_composite(photo("crash_screen", W, H, focus=(0.3, 0.5), dark=0.25, gray=0.0))
        shade(f, "left", 0.75, 230)
        TH.shadowed(f, pill(sp["tag"], 64, bg=BLUE), (70, 70))
        TH.shadowed(f, big(sp["big"], 320, 1200, color=RED), (60, 210))
        b = big(sp["bottom"], 150, 1300, color=YEL, hl=sp.get("hl", ""), hl_color=WHITE)
        TH.shadowed(f, b, (70, H - b.height - 70))
    return TH.finish(f)


SPECS = [
    {"name": "T01", "v": "hq", "big": "구글 -34%", "bottom": "지금 사도 될까?", "hl": "지금"},
    {"name": "T02", "v": "ceo", "tag": "구글에 물린 분들", "big": "-34%", "bottom": "과거 데이터가\n말해 준 결말", "hl": "결말"},
    {"name": "T03", "v": "crash", "tag": "역대 최악의 하루", "big": "669조 증발", "hl_big": "669조", "bottom": "구글, 지금이 바닥일까?"},
    {"name": "T04", "v": "dots", "top": "구글 -20% 폭락, 16년간 8번", "hl_top": "8번", "bottom": "7번은 회복\n지금이 8번째", "hl": "8번째"},
    {"name": "T05", "v": "bars", "top": "빅7 폭락 후 회복 속도\n구글은 몇 등?", "hl": "몇 등?"},
    {"name": "T06", "v": "phone", "top": "AI가 구글을 먹었다?", "hl_top": "AI", "big": "-34%", "bottom": "지금 사면 바닥? 함정?"},
    {"name": "T07", "v": "vs", "top": "구글 -30%에 산 사람들", "hl": "-30%", "cards": [("+94%", "2020년 3월에 샀다면", MINT), ("-20% 더", "2022년 9월에 샀다면", RED)]},
    {"name": "T08", "v": "money", "top": "1초에 560만 원 버는 회사가", "hl_top": "560만 원", "big": "1초 = 560만", "bottom": "주가는 -34%?", "hl": "-34%"},
    {"name": "T09", "v": "screen", "tag": "GOOGL", "big": "-34%", "bottom": "바닥일까?\n한 번 더일까?", "hl": "한 번 더"},
    {"name": "T10", "v": "ceo", "tag": "빅7 회복 속도 비교", "big": "구글 -34%", "bottom": "그래도 희망이\n있는 이유", "hl": "희망"},
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    outs = []
    for sp in SPECS:
        im = make(sp).convert("RGB").resize((1280, 720), Image.LANCZOS)
        p = OUT / f"{sp['name']}.png"
        im.save(p)
        outs.append((sp["name"], p))
    sheet = Image.new("RGB", (2 * 650 + 10, 5 * 400 + 10), (20, 20, 24))
    for i, (nm, p) in enumerate(outs):
        x, y = 10 + (i % 2) * 650, 10 + (i // 2) * 400
        sheet.paste(Image.open(p).resize((640, 360)), (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + 364), nm, fill=(180, 255, 60))
    sheet.save(OUT / "비교표.jpg", quality=90)
    print("비교표 →", OUT / "비교표.jpg")
