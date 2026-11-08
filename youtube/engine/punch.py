"""'훅' 비주얼 — 롱폼 중간중간(3~6번) 핵심 숫자를 치고 들어가는 컬러 풀스크린 카드.
같은 디자인을 쇼츠 커버(9:16)에도 쓴다 → 롱폼 변주 + 쇼츠 썸네일 차별화.

spec (롱폼 장면 type: punch / 쇼츠 cover style: punch)
  tone:  up(빨강) | down(파랑) | gold(노랑)
  label: 위 작은 태그 (예: "버블기 제외 · 1년 뒤")
  big:   큰 숫자/문구 (예: "+46.9%", "14번 중 14번")
  sub:   아래 한 줄
  mascot: true/false (오른쪽 아래 악어새)
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import draw as G
from . import style as S

TONES = {
    #        위 색            아래 색          큰 글자          보조 글자
    "up":   ((214, 52, 64), (120, 14, 30), (255, 255, 255), (255, 220, 220)),
    "down": ((40, 104, 230), (10, 36, 110), (255, 255, 255), (214, 228, 255)),
    "gold": ((255, 204, 84), (232, 140, 28), (20, 24, 40), (70, 50, 20)),
}


@lru_cache(maxsize=8)
def background(w, h, tone="up"):
    top, bot = TONES.get(tone, TONES["up"])[:2]
    y = np.linspace(0, 1, h)[:, None, None]
    x = np.linspace(0, 1, w)[None, :, None]
    t = np.clip(y * 0.7 + x * 0.3, 0, 1)
    arr = (np.array(top) * (1 - t) + np.array(bot) * t).astype(np.uint8)
    arr = np.broadcast_to(arr, (h, w, 3)).copy()
    im = Image.fromarray(arr, "RGB").convert("RGBA")
    # 집중선(아주 옅게) — 가운데로 모이는 사선
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = w / 2, h / 2
    rng = np.random.default_rng(3)
    for a in np.linspace(0, 2 * np.pi, 72, endpoint=False):
        a2 = a + rng.uniform(0.004, 0.012)
        r = max(w, h)
        d.polygon([(cx + np.cos(a) * r * 0.42, cy + np.sin(a) * r * 0.42),
                   (cx + np.cos(a) * r, cy + np.sin(a) * r),
                   (cx + np.cos(a2) * r, cy + np.sin(a2) * r)], fill=(255, 255, 255, 22))
    im.alpha_composite(lay)
    # 가운데 은은한 밝기
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((w * 0.2, h * 0.25, w * 0.8, h * 0.75), fill=(255, 255, 255, 40))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(min(w, h) // 6)))
    return im


@lru_cache(maxsize=4)
def _mascot(h):
    from .character import croc_bird
    return croc_bird(h)


def _fit(text, size, maxw, color, weight="Black", stroke=0, stroke_fill=(0, 0, 0)):
    im = G.text_img(text, weight, size, color, stroke=stroke, stroke_fill=stroke_fill, align="center", line_gap=1.1)
    while im.width > maxw and size > 40:
        size -= 8
        im = G.text_img(text, weight, size, color, stroke=stroke, stroke_fill=stroke_fill, align="center", line_gap=1.1)
    return im


def compose(w, h, sp, k=1.0, k_sub=1.0, k_m=1.0, vertical=False):
    """k: 큰 글자 등장 진행(0~1), k_sub: 아래 줄, k_m: 마스코트"""
    tone = sp.get("tone", "up")
    _, _, fg, fg2 = TONES.get(tone, TONES["up"])
    f = background(w, h, tone).copy()
    dark = tone == "gold"
    shadow = (0, 0, 0) if not dark else (255, 236, 180)
    cy = h * (0.44 if vertical else 0.47)
    big = _fit(sp["big"], sp.get("size", 300 if not vertical else 230), w - (160 if vertical else 260), fg)
    lab = None
    if sp.get("label"):
        lab = G.pill(sp["label"], "Black", 64 if not vertical else 72,  # 쇼츠 썸네일로 쓰일 때 읽히도록 크게
                     (20, 24, 40) if not dark else (255, 255, 255), (255, 255, 255) if not dark else (20, 24, 40),
                     pad=(36, 16))
    if vertical and sp.get("top"):
        top = _fit(sp["top"], 96, w - 120, fg)
        G.blit(f, top, (w / 2, h * 0.17), 1, "mt")
    # 큰 글자: 살짝 커졌다가 '쾅' 자리잡기 + 그림자
    if k > 0:
        e = G.ease_out(k)
        sc = 1.35 - 0.35 * e + 0.04 * np.sin(min(k, 1) * np.pi)
        bi = big.resize((max(1, int(big.width * sc)), max(1, int(big.height * sc))), Image.BICUBIC) if abs(sc - 1) > 1e-3 else big
        sh = Image.new("RGBA", bi.size, shadow + (0,))
        sh.putalpha(bi.getchannel("A").point(lambda a: a * 0.35))
        G.blit(f, sh.filter(ImageFilter.GaussianBlur(10)), (w / 2 + 8, cy + 12), min(1, e * 1.4), "mm")
        G.blit(f, bi, (w / 2, cy), min(1, e * 1.4), "mm")
    if lab is not None:
        G.blit(f, lab, (w / 2, cy - big.height / 2 - 40), min(1, k * 2), "mb")
    if sp.get("sub") and k_sub > 0:
        sub = _fit(sp["sub"], 60 if not vertical else 64, w - 200, fg2, weight="ExtraBold")
        G.blit(f, sub, (w / 2, cy + big.height / 2 + 36 + (1 - k_sub) * 20), k_sub, "mt")
    if sp.get("mascot", True) and k_m > 0:
        m = _mascot(int(h * (0.3 if not vertical else 0.17)))
        x = w - m.width * 0.92 + (1 - G.ease_out(k_m)) * m.width
        f.alpha_composite(m, (int(x), int(h - m.height * 0.9)))
    return f


def cover_vertical(sp, channel_logo=None, W=1080, H=1920):
    """쇼츠 커버 9:16"""
    f = compose(W, H, sp, vertical=True)
    if channel_logo is not None:
        f.alpha_composite(channel_logo, ((W - channel_logo.width) // 2, 90))
    return f
