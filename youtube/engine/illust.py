"""코드로 그리는 일러스트. 저작권 걱정 없는 단순 벡터 스타일."""
import math

from PIL import ImageDraw

from . import draw as G
from . import style as S

K = 3


def gauge(size, value, labels=("공포", "탐욕")):
    """공포-탐욕 게이지. value: -1(극단적 공포) ~ +1(극단적 탐욕)"""
    w, h = size, int(size * 0.72)
    im, d = G.supersample(w, h, K)
    cx, cy, r = w * K / 2, size * 0.60 * K, w * K * 0.42
    seg = 60
    for i in range(seg):
        a0 = math.pi + math.pi * i / seg
        a1 = math.pi + math.pi * (i + 1.05) / seg
        f = i / (seg - 1)
        c = tuple(int(S.DOWN[j] * (1 - f) + S.UP[j] * f) for j in range(3))
        if 0.35 < f < 0.65:
            m = 1 - abs(f - 0.5) / 0.15 * 0.6
            c = tuple(int(c[j] * (1 - m * 0.5) + S.NEUTRAL[j] * m * 0.5) for j in range(3))
        d.pieslice((cx - r, cy - r, cx + r, cy + r), math.degrees(a0), math.degrees(a1), fill=c + (255,))
    ri = r * 0.68
    d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=(0, 0, 0, 0))  # 안쪽을 투명하게 뚫기
    for i in range(11):  # 눈금
        a = math.pi + math.pi * i / 10
        x0, y0 = cx + math.cos(a) * (ri - 10 * K), cy + math.sin(a) * (ri - 10 * K)
        x1, y1 = cx + math.cos(a) * (ri - 26 * K), cy + math.sin(a) * (ri - 26 * K)
        d.line((x0, y0, x1, y1), fill=S.MUTED + (200,), width=2 * K)
    # 바늘
    a = math.pi * 1.5 + value * math.pi / 2 * 0.92
    nx, ny = cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92
    px, py = math.cos(a + math.pi / 2) * 9 * K, math.sin(a + math.pi / 2) * 9 * K
    d.polygon([(cx + px, cy + py), (nx, ny), (cx - px, cy - py)], fill=S.FG + (255,))
    d.ellipse((cx - 22 * K, cy - 22 * K, cx + 22 * K, cy + 22 * K), fill=S.FG + (255,))
    d.ellipse((cx - 9 * K, cy - 9 * K, cx + 9 * K, cy + 9 * K), fill=S.BG_BOT + (255,))
    out = G.finish(im, K)
    lf = G.text_img(labels[0], "ExtraBold", int(size * 0.07), S.DOWN)
    rt = G.text_img(labels[1], "ExtraBold", int(size * 0.07), S.UP)
    # 라벨은 호의 양 끝 아래
    out.alpha_composite(lf, (int(w * 0.21 - lf.width / 2), int(size * 0.62)))
    out.alpha_composite(rt, (int(w * 0.79 - rt.width / 2), int(size * 0.62)))
    return out


def newspaper(size, headline="Buy American. I Am.", masthead="THE NEW YORK TIMES · 2008.10"):
    w, h = size, int(size * 1.18)
    im, d = G.supersample(w, h, K)
    W2, H2 = w * K, h * K
    d.rounded_rectangle((14 * K, 22 * K, W2 - 6 * K, H2 - 2 * K), radius=18 * K, fill=(0, 0, 0, 90))
    d.rounded_rectangle((0, 0, W2 - 20 * K, H2 - 24 * K), radius=18 * K, fill=(242, 238, 226, 255))
    pad = 34 * K
    d.rectangle((pad, pad + 70 * K, W2 - 20 * K - pad, pad + 74 * K), fill=(40, 40, 40, 255))
    y = pad + 210 * K
    for i in range(9):
        lw = (W2 - 20 * K - pad * 2) * (0.62 if i % 4 == 3 else 1.0)
        d.rounded_rectangle((pad, y, pad + lw, y + 12 * K), radius=6 * K, fill=(170, 165, 150, 255))
        y += 32 * K
    out = G.finish(im, K)
    mt = G.text_img(masthead, "Bold", int(size * 0.045), (40, 40, 40))
    out.alpha_composite(mt, (34, 34 + 20))
    hl = G.text_img(headline, "Black", int(size * 0.095), (20, 20, 20), max_w=w - 20 - 68)
    out.alpha_composite(hl, (34, 34 + 92))
    return out


def warning(size):
    im, d = G.supersample(size, size, K)
    s = size * K
    pts = [(s / 2, s * 0.08), (s * 0.95, s * 0.88), (s * 0.05, s * 0.88)]
    d.polygon(pts, fill=S.GOLD + (255,))
    d.line(pts + [pts[0]], fill=S.GOLD + (255,), width=int(s * 0.07), joint="curve")
    d.rounded_rectangle((s * 0.465, s * 0.33, s * 0.535, s * 0.64), radius=s * 0.03, fill=(20, 20, 30, 255))
    d.ellipse((s * 0.455, s * 0.70, s * 0.545, s * 0.79), fill=(20, 20, 30, 255))
    return G.finish(im, K)


def number_badge(n, size=72, color=S.GOLD):
    im, d = G.supersample(size, size, K)
    d.ellipse((0, 0, size * K - 1, size * K - 1), fill=color + (255,))
    out = G.finish(im, K)
    t = G.text_img(str(n), "Black", int(size * 0.5), (16, 20, 32))
    out.alpha_composite(t, ((size - t.width) // 2, (size - t.height) // 2 - 2))
    return out


def check(size=56, color=S.GOLD):
    im, d = G.supersample(size, size, K)
    s = size * K
    d.ellipse((0, 0, s - 1, s - 1), outline=color + (255,), width=int(s * 0.08))
    d.line([(s * 0.28, s * 0.52), (s * 0.44, s * 0.68), (s * 0.73, s * 0.36)], fill=color + (255,),
           width=int(s * 0.1), joint="curve")
    return G.finish(im, K)


def get(name, size, **kw):
    return {"gauge": gauge, "newspaper": newspaper, "warning": warning}[name](size, **kw)
