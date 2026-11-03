"""채널 캐릭터 '계산기 개미' — 코드로 그린 귀여운 개미 캐릭터.

  ant_character(size, holding="moneybag" | "calculator" | None, mood="smile" | "wow")
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from . import illust as I

K = 3
BODY = (204, 98, 58)      # 따뜻한 적갈색
BODY_D = (150, 62, 36)
LINE = (70, 34, 24)       # 외곽선
CHEEK = (255, 130, 140)


def _ell(canvas, box, base, dark, lw, hl_rel=(0.18, 0.08, 0.6, 0.38), shadow=0.22):
    """타원 하나를 외곽선 + 아래 그림자 + 위 하이라이트로 칠한다 (해당 영역만 계산 → 빠름)"""
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = lw * 2 + 4
    w, h = x1 - x0 + pad * 2, y1 - y0 + pad * 2
    loc = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(loc)
    d.ellipse((pad - lw, pad - lw, w - pad + lw, h - pad + lw), fill=LINE + (255,))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((pad, pad, w - pad, h - pad), fill=255)
    fill = Image.new("RGBA", (w, h), base + (255,))
    s_px = max(2, int((y1 - y0) * shadow))
    sh = ImageChops.subtract(m, ImageChops.offset(m, 0, s_px)).filter(ImageFilter.GaussianBlur(s_px * 0.5))
    dk = Image.new("RGBA", (w, h), dark + (0,))
    dk.putalpha(ImageChops.multiply(sh, m))
    fill.alpha_composite(dk)
    bw, bh = x1 - x0, y1 - y0
    hl = Image.new("L", (w, h), 0)
    hx0, hy0, hx1, hy1 = hl_rel
    ImageDraw.Draw(hl).ellipse((pad + bw * hx0, pad + bh * hy0, pad + bw * hx1, pad + bh * hy1), fill=110)
    hl = ImageChops.multiply(hl.filter(ImageFilter.GaussianBlur(max(2, bw * 0.06))), m)
    li = Image.new("RGBA", (w, h), (255, 238, 215, 0))
    li.putalpha(hl)
    fill.alpha_composite(li)
    fill.putalpha(m)
    loc.alpha_composite(fill)
    canvas.alpha_composite(loc, (x0 - pad, y0 - pad))


def ant_character(size=800, holding="moneybag", mood="smile", glasses=True):
    S = size * K
    W = H = S
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    u = S / 1000  # 1000 기준 좌표계
    lw = int(9 * u)

    def E(x0, y0, x1, y1):
        return (x0 * u, y0 * u, x1 * u, y1 * u)

    # 더듬이 (뒤)
    d = ImageDraw.Draw(c)
    for sx in (-1, 1):
        pts = [(500 + sx * 70, 230), (500 + sx * 110, 140), (500 + sx * 170, 95)]
        d.line([(x * u, y * u) for x, y in pts], fill=LINE + (255,), width=int(16 * u), joint="curve")
        d.line([(x * u, y * u) for x, y in pts], fill=BODY_D + (255,), width=int(8 * u), joint="curve")
    for sx in (-1, 1):
        _ell(c, E(500 + sx * 170 - 34, 95 - 34, 500 + sx * 170 + 34, 95 + 34), BODY, BODY_D, lw)
    # 다리 (뒤)
    for x0, x1 in ((395, 360), (605, 640)):
        d.line([(x0 * u, 830 * u), (x1 * u, 930 * u)], fill=LINE + (255,), width=int(34 * u))
        d.line([(x0 * u, 830 * u), (x1 * u, 930 * u)], fill=BODY_D + (255,), width=int(18 * u))
        _ell(c, E(x1 - 48, 905, x1 + 48, 955), BODY_D, LINE, lw)
    # 배(엉덩이) + 가슴
    _ell(c, E(330, 640, 670, 900), BODY, BODY_D, lw)
    _ell(c, E(420, 560, 580, 680), BODY, BODY_D, lw)
    # 머리 (크게)
    _ell(c, E(250, 170, 750, 610), BODY, BODY_D, lw, shadow=0.16)
    d = ImageDraw.Draw(c)
    # 볼터치
    for cx in (340, 660):
        bw_, bh_ = int(160 * u), int(100 * u)
        bl = Image.new("RGBA", (bw_, bh_), (0, 0, 0, 0))
        ImageDraw.Draw(bl).ellipse((25 * u, 22 * u, 135 * u, 77 * u), fill=CHEEK + (150,))
        c.alpha_composite(bl.filter(ImageFilter.GaussianBlur(10 * u)), (int((cx - 80) * u), int(428 * u)))
    # 눈
    for cx in (400, 600):
        d.ellipse(E(cx - 62, 330, cx + 62, 470), fill=(255, 255, 255, 255), outline=LINE + (255,), width=int(7 * u))
        px = cx + 10
        d.ellipse(E(px - 40, 360, px + 40, 455), fill=(40, 24, 20, 255))
        d.ellipse(E(px - 22, 372, px + 2, 398), fill=(255, 255, 255, 255))
        d.ellipse(E(px + 12, 420, px + 24, 434), fill=(255, 255, 255, 230))
    # 안경
    if glasses:
        for cx in (400, 600):
            d.ellipse(E(cx - 92, 312, cx + 92, 492), outline=(40, 44, 60, 255), width=int(13 * u))
        d.arc(E(470, 370, 530, 420), 200, 340, fill=(40, 44, 60, 255), width=int(12 * u))
    # 입
    if mood == "wow":
        d.ellipse(E(470, 500, 530, 565), fill=(120, 30, 40, 255), outline=LINE + (255,), width=int(6 * u))
    else:
        d.arc(E(445, 470, 555, 555), 20, 160, fill=LINE + (255,), width=int(10 * u))
    # 들고 있는 것 + 팔
    if holding:
        item = I.emoji(holding, int(340 * u))
        c.alpha_composite(item, (int(330 * u), int(600 * u)))
        for (sx, sy), (hx, hy) in (((445, 640), (370, 730)), ((555, 640), (630, 730))):
            d.line([(sx * u, sy * u), (hx * u, hy * u)], fill=LINE + (255,), width=int(34 * u))
            d.line([(sx * u, sy * u), (hx * u, hy * u)], fill=BODY + (255,), width=int(18 * u))
            _ell(c, E(hx - 36, hy - 36, hx + 36, hy + 36), BODY, BODY_D, lw)
    else:
        for (sx, sy), (hx, hy) in (((440, 640), (350, 700)), ((560, 640), (650, 700))):
            d.line([(sx * u, sy * u), (hx * u, hy * u)], fill=LINE + (255,), width=int(34 * u))
            d.line([(sx * u, sy * u), (hx * u, hy * u)], fill=BODY + (255,), width=int(18 * u))
    return c.reduce(K)
