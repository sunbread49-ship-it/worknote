"""그리기 기본 도구: 텍스트, 투명도 합성, 이징, 배경."""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import style as S


# ── 시간/애니메이션 ──────────────────────────────────────────────
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def appear(t, t0, dur=0.25):
    """t0 시점부터 dur 동안 0→1"""
    return ease_out((t - t0) / dur) if t >= t0 else 0.0


# ── 합성 ─────────────────────────────────────────────────────────
def with_opacity(im: Image.Image, op: float) -> Image.Image:
    if op >= 0.999:
        return im
    a = im.getchannel("A").point(lambda v: int(v * op))
    out = im.copy()
    out.putalpha(a)
    return out


def blit(frame: Image.Image, im: Image.Image, xy, op=1.0, anchor="lt"):
    """frame(RGBA)에 im을 투명도 op로 합성. anchor: l/m/r + t/m/b"""
    if op <= 0.001:
        return
    x, y = xy
    w, h = im.size
    if anchor[0] == "m":
        x -= w // 2
    elif anchor[0] == "r":
        x -= w
    if anchor[1] == "m":
        y -= h // 2
    elif anchor[1] == "b":
        y -= h
    frame.alpha_composite(with_opacity(im, op), (int(x), int(y)))


# ── 텍스트 ───────────────────────────────────────────────────────
def wrap(text: str, fnt, max_w: int):
    """공백 기준 줄바꿈(한글 어절 단위). '\n'은 강제 줄바꿈."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = word if not cur else cur + " " + word
            if fnt.getlength(trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


_EMOJI_RE = __import__("re").compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")


@lru_cache(maxsize=4096)
def text_img(text: str, weight: str, size: int, fill=S.FG, max_w: int = 0,
             line_gap: float = 1.32, align: str = "left", highlight: str = "",
             hl_fill=S.GOLD, stroke: int = 0, stroke_fill=(0, 0, 0)) -> Image.Image:
    """텍스트를 딱 맞는 RGBA 이미지로. highlight 부분 문자열은 hl_fill 색."""
    text = _EMOJI_RE.sub("", text).rstrip()  # 폰트에 없는 이모지는 지움(이모지는 스티커로)
    fnt = S.font(weight, size)
    lines = wrap(text, fnt, max_w) if max_w else text.split("\n")
    lh = int(size * line_gap)
    asc, desc = fnt.getmetrics()
    w = int(max(fnt.getlength(l) for l in lines)) + 4 + stroke * 2
    h = lh * (len(lines) - 1) + asc + desc + 4 + stroke * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        lw = fnt.getlength(line)
        x = 2 + stroke if align == "left" else (w - lw) / 2 if align == "center" else w - lw - 2 - stroke
        y = 2 + stroke + i * lh
        sk = {"stroke_width": stroke, "stroke_fill": stroke_fill} if stroke else {}
        if highlight and highlight in line:
            pre, _, post = line.partition(highlight)
            d.text((x, y), pre, font=fnt, fill=fill, **sk)
            x2 = x + fnt.getlength(pre)
            d.text((x2, y), highlight, font=fnt, fill=hl_fill, **sk)
            d.text((x2 + fnt.getlength(highlight), y), post, font=fnt, fill=fill, **sk)
        else:
            d.text((x, y), line, font=fnt, fill=fill, **sk)
    return im


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def pill(text, weight="SemiBold", size=30, fg=S.FG, bg=S.PANEL, pad=(22, 10), radius=None):
    # 밝은(노랑 · 크림) 알약 안의 밝은 글씨는 안 보임 → 자동으로 검정 글씨 (EP010 피드백)
    if isinstance(bg, tuple) and len(bg) >= 3 and _lum(bg) > 150 and _lum(fg) > 150:
        fg = (14, 16, 24)
    t = text_img(text, weight, size, fg)
    w, h = t.width + pad[0] * 2, t.height + pad[1] * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius or h // 2, fill=bg)
    im.alpha_composite(t, (pad[0], pad[1]))
    return im


def panel(w, h, fill=S.PANEL, radius=28, outline=None, alpha=235):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius,
                                         fill=fill + (alpha,), outline=outline, width=2)
    return im


# ── 배경 ─────────────────────────────────────────────────────────
@lru_cache(maxsize=2)
def background() -> Image.Image:
    y = np.linspace(0, 1, S.H)[:, None, None]
    top, bot = np.array(S.BG_TOP), np.array(S.BG_BOT)
    grad = top * (1 - y) + bot * y
    arr = np.broadcast_to(grad, (S.H, S.W, 3)).copy()
    # 은은한 비네트
    yy, xx = np.mgrid[0:S.H, 0:S.W]
    r = np.sqrt(((xx - S.W / 2) / (S.W * 0.75)) ** 2 + ((yy - S.H * 0.4) / (S.H * 0.9)) ** 2)
    arr *= (1 - 0.35 * np.clip(r, 0, 1) ** 2)[..., None]
    im = Image.fromarray(arr.clip(0, 255).astype("uint8"), "RGB").convert("RGBA")
    # 옅은 격자
    grid = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)  # RGBA에 바로 그리면 블렌딩이 안 되므로 별도 레이어에 그려 합성
    for x in range(0, S.W, 80):
        d.line((x, 0, x, S.H), fill=(255, 255, 255, 7))
    for y_ in range(0, S.H, 80):
        d.line((0, y_, S.W, y_), fill=(255, 255, 255, 7))
    im.alpha_composite(grid)
    # 왼쪽 위 골드 글로우
    glow = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-400, -500, 700, 400), fill=S.GOLD + (18,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    return im


def supersample(w, h, k=2):
    """안티앨리어싱용: k배 크기 캔버스를 만들고, 끝나면 finish()로 축소."""
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def finish(im, k=2):
    return im.reduce(k)
