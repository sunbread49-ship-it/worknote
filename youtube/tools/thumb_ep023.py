"""EP023 '나스닥 -20%, 지금 사면?' 썸네일 10종 (11/22 사용자: 꼭대기 X → 지금이 바닥? 현금 넣어 볼까 느낌) (주식 채널 어두운 톤 · 2026-11-22 CCN: New가 3초 안에 이해 · 결과는 숨기는 안 위주)
  python tools/thumb_ep023.py → out/ep023_nasdaq_minus20/thumbs10/T01~T10 + 비교표
"""
import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402
from engine import draw as G  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/ep023_nasdaq_minus20/thumbs10"
W, H = TH.W, TH.H
YEL, RED, WHITE, MINT, GOLD = (255, 214, 40), (255, 60, 60), (255, 255, 255), (90, 230, 170), (240, 190, 70)
PEAKS = [("2000-04-12", "닷컴"), ("2008-01-23", "금융위기"), ("2018-12-21", "무역전쟁"), ("2020-03-12", "코로나"),
         ("2022-03-14", "금리"), ("2025-04-04", "관세"), ("2026-11-20", "지금")]
SPX = {r["date"]: float(r["close"]) for r in csv.DictReader(open(ROOT / "assets/data/ndx_daily.csv")) if r["date"] >= "1999-06"}
YEARS = ["1987", "1990", "1998", "2000", "2008", "2018", "2020", "2022", "2025"]


def chart(w, h, start="1999-06-01", end="2026-11-20", peaks=True, color=WHITE, lw=7, dot=24, labels=False, log=True):
    import math
    ks = [k for k in sorted(SPX) if start <= k <= end]
    vs = [math.log(SPX[k]) if log else SPX[k] for k in ks]
    lo, hi = min(vs), max(vs)
    P = lambda i, v: (40 + i / (len(ks) - 1) * (w - 80), h - 40 - (v - lo) / (hi - lo) * (h - 100))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [P(i, v) for i, v in enumerate(vs)][::3]
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).line(pts, fill=color + (150,), width=lw * 4, joint="curve")
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d.line(pts, fill=color + (255,), width=lw, joint="curve")
    if peaks:
        for date, name in PEAKS:
            if not (start <= date <= end):
                continue
            i = ks.index(date)
            x, y = P(i, vs[i])
            d.ellipse((x - dot, y - dot, x + dot, y + dot), fill=RED + (255,), outline=WHITE + (255,), width=5)
            if labels:
                t = TH.T(name, 34, WHITE)
                im.alpha_composite(t, (int(x - t.width / 2), int(max(0, y - dot - t.height - 6))))
    return im


def mascot(h):
    im = Image.open(ROOT / "assets/media/character_croc_bird_cutout.png").convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def base(glow=(120, 20, 20), pos=(0.5, 0.4)):
    return TH.bg_dark(glow, pos)


def card(title, val, col, w=520, h=560, sub=""):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(22, 26, 40, 245), outline=col + (255,), width=8)
    t = TH.T(title, 80, col)
    c.alpha_composite(t, ((w - t.width) // 2, 50))
    if sub:
        s = TH.T(sub, 40, (200, 204, 214), weight="Bold")
        c.alpha_composite(s, ((w - s.width) // 2, 160))
    v = TH.fit(val, 200, w - 40, color=WHITE)
    c.alpha_composite(v, ((w - v.width) // 2, h - v.height - 70))
    return c


def make(sp):
    v = sp["v"]
    f = base(sp.get("glow", (120, 20, 20)))
    if v == "chart":   # 26년 차트 + 꼭대기 7개 빨간 점
        ch = chart(1840, 700, labels=sp.get("labels", False))
        f.alpha_composite(ch, (40, 120))
        TH.shadowed(f, TH.fit(sp["top"], 130, 1500, color=WHITE, hl=sp.get("hl_top", ""), hl_color=RED), (60, 40))
        b = TH.fit(sp["bottom"], 190, 1500, color=YEL, hl=sp.get("hl", ""), hl_color=RED)
        TH.shadowed(f, b, (60, H - b.height - 50))
        m = mascot(sp.get("m", 420))
        f.alpha_composite(m, (W - m.width - 30, H - m.height - 10))
    elif v == "three":   # 세 사람 카드 · 금액 숨김
        cs = [("불운이", RED, "꼭대기에서만"), ("행운이", GOLD, "바닥에서만"), ("꾸준이", MINT, "매달 조금씩")]
        for i, (n, c, s) in enumerate(cs):
            cd = card(n, "???", c, sub=s)
            TH.shadowed(f, cd, (80 + i * 600, 420))
        TH.shadowed(f, TH.fit(sp["top"], 150, 1800, color=WHITE, hl=sp.get("hl", ""), hl_color=YEL), (W / 2, 40), "mt")
    elif v == "big":
        ch = chart(1840, 640, peaks=True, color=(120, 130, 150))
        ch.putalpha(ch.getchannel("A").point(lambda a: int(a * 0.55)))
        f.alpha_composite(ch, (40, 260))
        TH.shadowed(f, TH.fit(sp["top"], 140, 1800, color=WHITE), (W / 2, 50), "mt")
        b = TH.fit(sp["big"], 420, 1800, color=sp.get("big_col", MINT))
        TH.shadowed(f, b, (W / 2, 300), "mt")
        if sp.get("bottom"):
            bb = TH.fit(sp["bottom"], 110, 1800, color=YEL)
            TH.shadowed(f, bb, (W / 2, H - bb.height - 50), "mt")
    elif v == "dates":   # 날짜 도장 7개
        for i, (d0, n) in enumerate(PEAKS):
            st = G.pill(f"{d0.replace('-', '.')}  {n}", "Black", 50, WHITE, RED if i % 2 == 0 else (190, 30, 40), pad=(28, 12), radius=14)
            st = st.rotate([-4, 3, -2, 4, -3, 2, -5][i], expand=True, resample=Image.BICUBIC)
            f.alpha_composite(st, (60 + (i % 2) * 620, 300 + i * 92))
        TH.shadowed(f, TH.fit(sp["top"], 150, 1800, color=WHITE, hl=sp.get("hl", ""), hl_color=RED), (60, 40))
        m = mascot(560)
        f.alpha_composite(m, (W - m.width - 20, H - m.height))
        b = TH.fit(sp["bottom"], 120, 700, color=YEL)
        TH.shadowed(f, b, (W - b.width - 60, 200))
    elif v == "vs":
        l = card(sp["l"][0], sp["l"][1], GOLD, 760, 620, sp["l"][2])
        r = card(sp["r"][0], sp["r"][1], MINT, 760, 620, sp["r"][2])
        TH.shadowed(f, l, (90, 300)); TH.shadowed(f, r, (W - 90 - 760, 300))
        TH.shadowed(f, TH.T("VS", 160, YEL), (W / 2, 560), "mm")
        TH.shadowed(f, TH.fit(sp["top"], 140, 1800, color=WHITE, hl=sp.get("hl", ""), hl_color=YEL), (W / 2, 50), "mt")
    elif v == "now":   # 이번 주 폭락 + 질문
        ch = chart(1840, 760, start="2026-07-01", peaks=False, color=RED, log=False, lw=10)
        f.alpha_composite(ch, (40, 160))
        TH.shadowed(f, G.pill(sp["tag"], "Black", 60, WHITE, RED, pad=(30, 12), radius=14), (60, 50))
        b = TH.fit(sp["bottom"], 200, 1300, color=YEL, hl=sp.get("hl", ""), hl_color=WHITE)
        TH.shadowed(f, b, (60, H - b.height - 60))
        m = mascot(600)
        f.alpha_composite(m, (W - m.width - 10, H - m.height))
    elif v == "years":   # 9개 연도 칸 + 질문
        cw = 190
        x0 = (W - 9 * cw - 8 * 12) // 2
        for i, y in enumerate(YEARS):
            c = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
            ImageDraw.Draw(c).rounded_rectangle((0, 0, cw - 1, cw - 1), 24, fill=(RED if y in sp.get("red", []) else (40, 46, 66)) + (255,))
            t = TH.T(y, 58, WHITE)
            c.alpha_composite(t, ((cw - t.width) // 2, 30))
            q = TH.T(sp.get("cell", "?"), 70, YEL)
            c.alpha_composite(q, ((cw - q.width) // 2, 100))
            f.alpha_composite(c, (x0 + i * (cw + 12), 430))
        TH.shadowed(f, TH.fit(sp["top"], 150, 1800, color=WHITE, hl=sp.get("hl_top", ""), hl_color=RED), (W / 2, 60), "mt")
        b = TH.fit(sp["bottom"], 170, 1800, color=YEL, hl=sp.get("hl", ""), hl_color=RED)
        TH.shadowed(f, b, (W / 2, H - b.height - 60), "mt")
    elif v == "bubble":
        ch = chart(1840, 640)
        f.alpha_composite(ch, (40, 330))
        bub = Image.new("RGBA", (1500, 280), (0, 0, 0, 0))
        ImageDraw.Draw(bub).rounded_rectangle((0, 0, 1499, 250), 60, fill=(255, 255, 255, 250))
        ImageDraw.Draw(bub).polygon([(1200, 240), (1300, 240), (1330, 280)], fill=(255, 255, 255, 250))
        t = G.text_img(sp["bubble"], "Black", 96, (20, 20, 30))
        bub.alpha_composite(t, ((1500 - t.width) // 2, (250 - t.height) // 2))
        f.alpha_composite(bub, (60, 40))
        b = TH.fit(sp["bottom"], 150, 1300, color=YEL, hl=sp.get("hl", ""), hl_color=RED)
        TH.shadowed(f, b, (60, H - b.height - 40))
    return TH.finish(f)


SPECS = [
    {"name": "T01", "v": "now", "tag": "나스닥 고점 대비 -20%", "bottom": "지금이\n바닥일까?", "hl": "바닥"},
    {"name": "T02", "v": "bubble", "bubble": "현금, 슬슬 넣어 볼까?", "bottom": "나스닥 -20% 때 산 9번의 결말", "hl": "9번"},
    {"name": "T03", "v": "years", "top": "나스닥 -20%, 그날 산 사람들", "hl_top": "-20%", "bottom": "9번 중 몇 번이 바닥?", "hl": "몇 번"},
    {"name": "T04", "v": "now", "tag": "나스닥 -20%", "bottom": "지금이니!!\n현금 넣을 때?", "hl": "지금이니!!"},
    {"name": "T05", "v": "vs", "top": "나스닥 -20%, 당신의 선택은?", "hl": "-20%", "l": ("지금 산다", "???", "-20% 날 바로"), "r": ("더 기다린다", "???", "바닥 확인하고")},
    {"name": "T06", "v": "big", "top": "나스닥 -20%에 샀는데", "big": "13년?", "big_col": RED, "bottom": "본전까지 걸린 최악의 시간"},
    {"name": "T07", "v": "years", "top": "지금 사면 천재? 바보?", "hl_top": "천재?", "bottom": "과거 9번이 답한다", "hl": "9번", "cell": "?"},
    {"name": "T08", "v": "chart", "start": "1999-06-01", "top": "40년 동안 딱 9번 온 기회?", "hl_top": "9번", "bottom": "지금이 10번째", "hl": "10번째"},
    {"name": "T09", "v": "bubble", "bubble": "바닥 확인하고 살래…", "bottom": "그러다 못 산 사람 9번 중 4번", "hl": "9번 중 4번"},
    {"name": "T10", "v": "now", "tag": "나스닥 한 주 -10% · 고점 대비 -20%", "bottom": "물 타? 기다려?\n데이터로 답함", "hl": "데이터"},
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
