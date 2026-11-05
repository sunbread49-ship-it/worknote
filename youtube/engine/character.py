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


# ── 옆모습 개미 (기본 캐릭터) ────────────────────────────────────────
SIDE_BODY = (52, 46, 64)       # 짙은 차콜
SIDE_BODY_D = (32, 28, 40)
SIDE_LINE = (18, 16, 24)
MONEY = (58, 170, 100)         # 지폐 초록
MONEY_D = (34, 120, 70)
MONEY_L = (150, 220, 170)


def _bill(w, h, k):
    """초록 지폐 한 장"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(h * 0.08)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=MONEY_D + (255,))
    d.rounded_rectangle((k * 3, k * 3, w - 1 - k * 3, h - 1 - k * 3), radius=r, fill=MONEY + (255,))
    d.rounded_rectangle((w * 0.07, h * 0.16, w * 0.93, h * 0.84), radius=r, outline=MONEY_L + (255,), width=max(2, k * 2))
    cx, cy, rr = w / 2, h / 2, h * 0.27
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=MONEY_L + (255,), outline=MONEY_D + (255,), width=max(2, k * 2))
    return im


def money_stack(w, h, k=3):
    """띠지 두른 지폐 다발 (약간씩 어긋난 3장)"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bw, bh = int(w * 0.92), int(h * 0.62)
    for i, (dx, dy, rot) in enumerate(((0.0, 0.30, -6), (0.04, 0.18, 3), (0.02, 0.05, -2))):
        b = _bill(bw, bh, k).rotate(rot, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(b, (int(w * dx), int(h * dy)))
    # 띠지
    d = ImageDraw.Draw(im)
    x0 = w * 0.42
    d.polygon([(x0, h * 0.02), (x0 + w * 0.13, h * 0.02), (x0 + w * 0.15, h * 0.98), (x0 + w * 0.02, h * 0.98)],
              fill=(246, 232, 196, 255), outline=(190, 170, 130, 255))
    # $ 표시
    from . import draw as G
    t = G.text_img("$", "Black", int(bh * 0.42), MONEY_D)
    im.alpha_composite(t, (int(w * 0.18), int(h * 0.05 + bh * 0.25)))
    return im


def ant_side(size=800, carry="money", glasses=True, mood="smile"):
    """옆모습(오른쪽을 봄) 개미가 등에 초록 지폐 다발을 지고 가는 모습"""
    S = size * K
    c = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    u = S / 1000
    lw = int(8 * u)

    def P(x, y):
        return (x * u, y * u)

    def E(x0, y0, x1, y1):
        return (x0 * u, y0 * u, x1 * u, y1 * u)

    d = ImageDraw.Draw(c)

    def leg(pts, near=True):
        col = SIDE_BODY if near else (88, 82, 104)
        d.line([P(*p) for p in pts], fill=SIDE_LINE + (255,), width=int((26 if near else 22) * u), joint="curve")
        d.line([P(*p) for p in pts], fill=col + (255,), width=int((12 if near else 9) * u), joint="curve")
        fx, fy = pts[-1]
        d.ellipse(E(fx - 16, fy - 10, fx + 22, fy + 12), fill=SIDE_LINE + (255,))

    # 먼 쪽 다리 3개 (뒤, 밝은 색)
    for pts in (((470, 640), (420, 720), (380, 840)), ((530, 650), (540, 740), (520, 850)),
                ((590, 640), (660, 720), (700, 840))):
        leg([(x + 25, y) for x, y in pts], near=False)
    # 먼 쪽 더듬이
    d.line([P(735, 420), P(770, 300), P(860, 250)], fill=SIDE_LINE + (255,), width=int(18 * u), joint="curve")
    d.line([P(735, 420), P(770, 300), P(860, 250)], fill=(88, 82, 104, 255), width=int(8 * u), joint="curve")
    _ell(c, E(845, 232, 885, 270), (88, 82, 104), SIDE_BODY_D, lw)
    # 배(가스터) · 허리 마디 · 가슴 · 머리
    _ell(c, E(110, 470, 450, 720), SIDE_BODY, SIDE_BODY_D, lw, hl_rel=(0.2, 0.08, 0.7, 0.35))
    _ell(c, E(430, 560, 495, 625), SIDE_BODY, SIDE_BODY_D, lw)
    _ell(c, E(470, 520, 650, 640), SIDE_BODY, SIDE_BODY_D, lw)
    _ell(c, E(610, 380, 860, 610), SIDE_BODY, SIDE_BODY_D, lw, hl_rel=(0.2, 0.06, 0.65, 0.35), shadow=0.14)
    d = ImageDraw.Draw(c)
    # 가까운 쪽 다리 3개
    for pts in (((470, 625), (400, 700), (340, 850)), ((540, 635), (520, 740), (480, 860)),
                ((600, 625), (690, 700), (750, 850))):
        leg(pts, near=True)
    # 가까운 쪽 더듬이 (꺾인 모양)
    d.line([P(770, 400), P(830, 290), P(940, 260)], fill=SIDE_LINE + (255,), width=int(22 * u), joint="curve")
    d.line([P(770, 400), P(830, 290), P(940, 260)], fill=SIDE_BODY + (255,), width=int(10 * u), joint="curve")
    _ell(c, E(920, 238, 970, 285), SIDE_BODY, SIDE_BODY_D, lw)
    d = ImageDraw.Draw(c)
    # 눈 (크게, 앞을 봄)
    d.ellipse(E(735, 425, 830, 525), fill=(255, 255, 255, 255), outline=SIDE_LINE + (255,), width=int(6 * u))
    d.ellipse(E(772, 448, 828, 512), fill=(20, 18, 26, 255))
    d.ellipse(E(785, 456, 805, 476), fill=(255, 255, 255, 255))
    d.ellipse(E(810, 492, 818, 500), fill=(255, 255, 255, 220))
    # 안경 (한 쪽 렌즈 + 다리)
    if glasses:
        d.ellipse(E(718, 408, 848, 538), outline=(240, 196, 70, 255), width=int(10 * u))
        d.line([P(720, 460), P(650, 445)], fill=(240, 196, 70, 255), width=int(9 * u))
    # 볼
    ch = Image.new("RGBA", (int(120 * u), int(80 * u)), (0, 0, 0, 0))
    ImageDraw.Draw(ch).ellipse((20 * u, 20 * u, 100 * u, 60 * u), fill=(255, 120, 140, 120))
    c.alpha_composite(ch.filter(ImageFilter.GaussianBlur(8 * u)), (int(700 * u), int(510 * u)))
    # 입
    if mood == "wow":
        d.ellipse(E(812, 545, 846, 585), fill=(150, 40, 50, 255), outline=SIDE_LINE + (255,), width=int(5 * u))
    else:
        d.arc(E(790, 520, 856, 578), 10, 120, fill=(255, 255, 255, 230), width=int(8 * u))
    # 등에 진 지폐 다발
    if carry == "money":
        st = money_stack(int(420 * u), int(300 * u), k=K).rotate(8, resample=Image.BICUBIC, expand=True)
        c.alpha_composite(st, (int(150 * u), int(200 * u)))
        # 받치는 앞다리 하나 (위로 들어 다발을 잡음)
        d = ImageDraw.Draw(c)
        pts = [P(620, 560), P(640, 470), P(560, 420)]
        d.line(pts, fill=SIDE_LINE + (255,), width=int(26 * u), joint="curve")
        d.line(pts, fill=SIDE_BODY + (255,), width=int(12 * u), joint="curve")
    return c.reduce(K)


def logo_badge(size=200, ring=(14, 20, 38)):
    """채널 로고: 금색 원 + 남색 테두리 + 지폐 진 옆모습 개미"""
    k = 3
    S = size * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, S - 1, S - 1), fill=ring + (255,))
    d.ellipse((S * 0.05, S * 0.05, S * 0.95, S * 0.95), fill=(252, 196, 70, 255))
    a = ant_side(int(size * 0.98), "money").resize((int(S * 0.98), int(S * 0.98)), Image.LANCZOS)
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((S * 0.05, S * 0.05, S * 0.95, S * 0.95), fill=255)
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    lay.alpha_composite(a, (int(S * -0.02), int(S * 0.02)))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    im.alpha_composite(lay)
    return im.reduce(k)


# ── 주식 악어새 (채널 캐릭터) ─────────────────────────────────────
BIRD_BACK = (92, 118, 150)      # 푸른 회색 등
BIRD_BACK_D = (62, 84, 112)
BIRD_BELLY = (250, 240, 214)    # 크림색 배
BIRD_BELLY_D = (226, 206, 168)
BIRD_CAP = (30, 32, 42)         # 검은 머리 깃
BIRD_LINE = (24, 26, 36)
BEAK = (40, 40, 48)
LEG = (110, 120, 132)
CROC = (86, 150, 82)
CROC_D = (56, 110, 58)
CROC_L = (150, 200, 120)


def bird_side(size=800, holding="money", glasses=True, mood="smile"):
    """옆모습(오른쪽을 봄) 악어새. 둥근 몸·큰 눈·검은 머리깃과 흰 눈썹줄, 금테 안경, 날개로 지폐 다발을 듦"""
    S_ = size * K
    c = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    u = S_ / 1000
    lw = int(9 * u)

    def P(x, y):
        return (x * u, y * u)

    def E(x0, y0, x1, y1):
        return (x0 * u, y0 * u, x1 * u, y1 * u)

    d = ImageDraw.Draw(c)
    # 다리 (가늘고 긴 다리 2개)
    for x0, x1 in ((430, 400), (520, 540)):
        d.line([P(x0, 760), P(x1, 900)], fill=BIRD_LINE + (255,), width=int(26 * u))
        d.line([P(x0, 760), P(x1, 900)], fill=LEG + (255,), width=int(13 * u))
        for dx in (-50, 0, 46):
            d.line([P(x1, 900), P(x1 + dx, 930)], fill=BIRD_LINE + (255,), width=int(14 * u))
    # 꼬리깃
    d.polygon([P(250, 560), P(120, 520), P(140, 600), P(260, 640)], fill=BIRD_LINE + (255,))
    d.polygon([P(255, 575), P(150, 545), P(165, 595), P(262, 625)], fill=BIRD_BACK_D + (255,))
    # 몸통 (등은 푸른 회색, 배는 크림색)
    _ell(c, E(220, 400, 700, 800), BIRD_BACK, BIRD_BACK_D, lw, hl_rel=(0.2, 0.06, 0.62, 0.3))
    belly = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    _ell(belly, E(330, 520, 700, 800), BIRD_BELLY, BIRD_BELLY_D, lw, hl_rel=(0.25, 0.1, 0.7, 0.4))
    c.alpha_composite(belly)
    # 머리
    _ell(c, E(470, 200, 800, 520), BIRD_BELLY, BIRD_BELLY_D, lw, hl_rel=(0.2, 0.08, 0.6, 0.35), shadow=0.12)
    d = ImageDraw.Draw(c)
    # 검은 머리깃(정수리~뒷머리) + 흰 눈썹줄
    d.pieslice(E(470, 200, 800, 520), 180, 340, fill=BIRD_CAP + (255,))
    d.arc(E(470, 200, 800, 520), 180, 340, fill=BIRD_LINE + (255,), width=lw)
    d.arc(E(520, 250, 790, 470), 200, 330, fill=(255, 255, 255, 255), width=int(22 * u))
    # 부리 (짧고 뾰족)
    d.polygon([P(775, 360), P(900, 392), P(775, 410)], fill=BEAK + (255,), outline=BIRD_LINE + (255,))
    # 눈
    d.ellipse(E(625, 320, 725, 420), fill=(255, 255, 255, 255), outline=BIRD_LINE + (255,), width=int(6 * u))
    d.ellipse(E(660, 338, 720, 408), fill=(18, 18, 26, 255))
    d.ellipse(E(674, 348, 694, 368), fill=(255, 255, 255, 255))
    d.ellipse(E(700, 388, 708, 396), fill=(255, 255, 255, 220))
    if glasses:  # 금테 안경 (모노클)
        d.ellipse(E(608, 302, 742, 436), outline=(240, 196, 70, 255), width=int(10 * u))
        d.line([P(610, 360), P(545, 340)], fill=(240, 196, 70, 255), width=int(8 * u))
    # 볼
    ch = Image.new("RGBA", (int(120 * u), int(80 * u)), (0, 0, 0, 0))
    ImageDraw.Draw(ch).ellipse((20 * u, 20 * u, 100 * u, 60 * u), fill=(255, 130, 140, 130))
    c.alpha_composite(ch.filter(ImageFilter.GaussianBlur(8 * u)), (int(640 * u), int(410 * u)))
    if mood == "wow":
        d.ellipse(E(790, 400, 816, 426), fill=(150, 40, 50, 255))
    # 들고 있는 지폐 다발 (날개 앞)
    if holding == "money":
        st = money_stack(int(330 * u), int(240 * u), k=K).rotate(-10, resample=Image.BICUBIC, expand=True)
        c.alpha_composite(st, (int(470 * u), int(520 * u)))
    # 날개 (지폐를 감싸 쥠)
    wing = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wing)
    pts = [P(300, 500), P(470, 470), P(600, 560), P(620, 650), P(520, 640), P(400, 610)]
    wd.polygon(pts, fill=BIRD_BACK_D + (255,), outline=BIRD_LINE + (255,))
    wd.line(pts + [pts[0]], fill=BIRD_LINE + (255,), width=lw, joint="curve")
    for i in range(3):
        wd.line([P(380 + i * 60, 520 + i * 10), P(500 + i * 40, 600 + i * 12)], fill=BIRD_BACK + (255,), width=int(8 * u))
    c.alpha_composite(wing)
    return c.reduce(K)


def croc_head(w=900, h=420):
    """옆모습 악어 머리(왼쪽을 봄 아님: 오른쪽으로 길게). 미소 짓는 입, 이빨, 눈"""
    k = 3
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    W_, H_ = w * k, h * k
    d = ImageDraw.Draw(im)
    lw = 7 * k
    top = [(0, H_ * 0.35), (W_ * 0.25, H_ * 0.18), (W_ * 0.55, H_ * 0.28), (W_ * 0.98, H_ * 0.42), (W_ * 0.98, H_ * 0.55), (0, H_ * 0.62)]
    jaw = [(0, H_ * 0.62), (W_ * 0.96, H_ * 0.58), (W_ * 0.9, H_ * 0.72), (W_ * 0.4, H_ * 0.82), (0, H_ * 0.9)]
    for poly, col in ((jaw, CROC_D), (top, CROC)):
        d.polygon(poly, fill=col + (255,))
        d.line(poly + [poly[0]], fill=BIRD_LINE + (255,), width=lw, joint="curve")
    # 이빨
    for i in range(9):
        x = W_ * (0.32 + i * 0.07)
        d.polygon([(x, H_ * 0.6), (x + W_ * 0.025, H_ * 0.6), (x + W_ * 0.012, H_ * 0.69)], fill=(255, 255, 250, 255))
    # 등 비늘 돌기
    for i in range(6):
        x = W_ * (0.06 + i * 0.07)
        d.polygon([(x, H_ * 0.3), (x + W_ * 0.04, H_ * 0.12), (x + W_ * 0.08, H_ * 0.27)], fill=CROC_D + (255,), outline=BIRD_LINE + (255,))
    # 눈 (빼꼼 올라온 눈두덩)
    d.ellipse((W_ * 0.42, H_ * 0.05, W_ * 0.58, H_ * 0.3), fill=CROC + (255,), outline=BIRD_LINE + (255,), width=lw)
    d.ellipse((W_ * 0.46, H_ * 0.1, W_ * 0.55, H_ * 0.24), fill=(255, 230, 90, 255))
    d.ellipse((W_ * 0.495, H_ * 0.11, W_ * 0.515, H_ * 0.23), fill=(20, 20, 26, 255))
    # 콧구멍·무늬
    d.ellipse((W_ * 0.9, H_ * 0.4, W_ * 0.93, H_ * 0.44), fill=BIRD_LINE + (255,))
    for i in range(5):
        d.ellipse((W_ * (0.12 + i * 0.12), H_ * 0.38, W_ * (0.16 + i * 0.12), H_ * 0.44), fill=CROC_L + (255,))
    return im.reduce(k)


def bird_badge(size=200, ring=(14, 20, 38)):
    """채널 로고: 금색 원 + 남색 테두리 + 악어새"""
    k = 3
    S_ = size * k
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, S_ - 1, S_ - 1), fill=ring + (255,))
    d.ellipse((S_ * 0.05, S_ * 0.05, S_ * 0.95, S_ * 0.95), fill=(252, 196, 70, 255))
    b = bird_side(size, "money").resize((int(S_ * 0.96), int(S_ * 0.96)), Image.LANCZOS)
    m = Image.new("L", (S_, S_), 0)
    ImageDraw.Draw(m).ellipse((S_ * 0.05, S_ * 0.05, S_ * 0.95, S_ * 0.95), fill=255)
    lay = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    lay.alpha_composite(b, (int(S_ * -0.02), int(S_ * 0.0)))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    im.alpha_composite(lay)
    return im.reduce(k)
