from pathlib import Path
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
    """채널 로고: 프로필(사용자 일러스트 악어새) 원형 + 흰 테두리. 파일이 없으면 예전 개미 배지."""
    p = Path(__file__).resolve().parents[1] / "assets/media/profile_circle.png"
    if p.exists():
        k = 3
        S = size * k
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((0, 0, S - 1, S - 1), fill=(255, 255, 255, 255))
        b = int(S * 0.06)
        pic = Image.open(p).convert("RGBA").resize((S - 2 * b, S - 2 * b), Image.LANCZOS)
        im.alpha_composite(pic, (b, b))
        return im.resize((size, size), Image.LANCZOS)
    return _logo_badge_ant(size, ring)


def _logo_badge_ant(size=200, ring=(14, 20, 38)):
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


# ── 주식 악어새 v2: 외곽선 없는 플랫 일러스트 (귀엽지만 성숙한 톤) ──────────
V2 = {
    "back": (120, 136, 156), "back_d": (94, 108, 128), "back_l": (150, 164, 182),
    "belly": (238, 214, 180), "belly_d": (214, 184, 146),
    "white": (246, 244, 238), "black": (28, 30, 36), "beak": (36, 38, 44),
    "leg": (120, 134, 150), "gold": (214, 172, 84), "eye_hl": (255, 255, 255),
    "croc": (44, 98, 86), "croc_d": (30, 72, 64), "croc_l": (66, 124, 108), "croc_eye": (232, 196, 92),
    "bill": (64, 150, 104), "bill_d": (44, 116, 80), "bill_l": (150, 206, 170),
}


def _smooth(pts, n=12):
    """Catmull-Rom 스플라인으로 다각형을 부드러운 곡선 점들로 (닫힌 도형)"""
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def _shape(c, pts, color, u, smooth=True):
    d = ImageDraw.Draw(c)
    q = _smooth(pts) if smooth else pts
    d.polygon([(x * u, y * u) for x, y in q], fill=color + (255,))


def _masked(c, pts_mask, draw_fn, u):
    """pts_mask 영역 안에만 그리기 (무늬를 몸 안에 가두기)"""
    S_ = c.width
    lay = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    draw_fn(lay)
    m = Image.new("L", (S_, S_), 0)
    ImageDraw.Draw(m).polygon([(x * u, y * u) for x, y in _smooth(pts_mask)], fill=255)
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    c.alpha_composite(lay)


def bird_v2(size=800, holding="bill", glasses=True):
    """오른쪽을 보는 악어새. 회색 등·검은 머리띠·흰 눈썹·크림색 배, 가는 다리. 날개 끝에 접은 지폐."""
    S_ = size * K
    c = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    u = S_ / 1000
    C = V2
    d = ImageDraw.Draw(c)
    # 다리 (가늘고 길게)
    for x0, x1 in ((455, 430), (520, 545)):
        d.line([(x0 * u, 700 * u), (x1 * u, 880 * u)], fill=C["leg"] + (255,), width=int(11 * u))
        for dx in (-34, 0, 30):
            d.line([(x1 * u, 880 * u), ((x1 + dx) * u, 902 * u)], fill=C["leg"] + (255,), width=int(8 * u))
    # 꼬리
    _shape(c, [(300, 560), (150, 610), (160, 640), (320, 615)], C["black"], u)
    # 몸 (눈물방울형)
    body = [(300, 560), (370, 470), (520, 430), (650, 450), (700, 540), (660, 660), (540, 720), (400, 690), (320, 620)]
    _shape(c, body, C["back"], u)
    # 배 (크림색) — 몸 안에만
    _masked(c, body, lambda lay: _shape(lay, [(420, 560), (560, 520), (720, 560), (690, 700), (520, 760), (400, 720)], C["belly"], u), u)
    # 가슴 검은 띠
    _masked(c, body, lambda lay: _shape(lay, [(600, 470), (680, 470), (720, 540), (650, 560), (610, 530)], C["black"], u), u)
    # 은은한 그림자 (배 아래쪽)
    _masked(c, body, lambda lay: _shape(lay, [(380, 690), (560, 660), (690, 640), (640, 760), (420, 760)], C["belly_d"], u), u)
    # 날개 (등 위, 매끈한 잎사귀형) + 깃 줄무늬
    wing = [(330, 520), (430, 480), (560, 490), (620, 560), (540, 600), (400, 590)]
    _shape(c, wing, C["back_d"], u)
    _masked(c, wing, lambda lay: [ImageDraw.Draw(lay).line([((360 + i * 55) * u, 600 * u), ((440 + i * 50) * u, 500 * u)],
                                                          fill=C["back_l"] + (150,), width=int(5 * u)) for i in range(4)], u)
    # 머리
    head = [(560, 300), (640, 250), (730, 260), (780, 320), (770, 400), (700, 450), (610, 445), (560, 390)]
    _shape(c, head, C["white"], u)
    # 검은 머리 위 + 눈을 지나는 검은 띠 (실제 악어새 무늬)
    _masked(c, head, lambda lay: _shape(lay, [(540, 240), (800, 240), (800, 300), (700, 300), (600, 320), (540, 330)], C["black"], u), u)
    _masked(c, head, lambda lay: _shape(lay, [(560, 360), (660, 340), (790, 350), (790, 385), (660, 385), (560, 400)], C["black"], u), u)
    # 부리 (가늘고 길게)
    _shape(c, [(775, 360), (880, 378), (775, 392)], C["beak"], u, smooth=False)
    d = ImageDraw.Draw(c)
    # 눈 (작고 반짝임) — 검은 띠 위에
    d.ellipse(((688) * u, (346) * u, (728) * u, (386) * u), fill=(16, 16, 20, 255))
    d.ellipse(((700) * u, (352) * u, (712) * u, (364) * u), fill=C["eye_hl"] + (255,))
    if glasses:  # 얇은 금테 안경 + 줄
        d.ellipse((672 * u, 330 * u, 744 * u, 402 * u), outline=C["gold"] + (255,), width=int(6 * u))
        d.line([(672 * u, 372 * u), (610 * u, 440 * u), (590 * u, 500 * u)], fill=C["gold"] + (200,), width=int(3 * u), joint="curve")
    # 접은 지폐 (날개 끝에 낀 모습)
    if holding == "bill":
        bw, bh = int(230 * u), int(120 * u)
        bill = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bill)
        r = int(10 * u)
        bd.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=r, fill=C["bill"] + (255,))
        bd.rounded_rectangle((int(10 * u), int(10 * u), bw - int(10 * u), bh - int(10 * u)), radius=r, outline=C["bill_l"] + (255,), width=int(3 * u))
        bd.ellipse((bw / 2 - 30 * u, bh / 2 - 30 * u, bw / 2 + 30 * u, bh / 2 + 30 * u), fill=C["bill_d"] + (255,))
        from . import draw as G_
        t = G_.text_img("$", "Black", int(44 * u), C["bill_l"])
        bill.alpha_composite(t, (int(bw / 2 - t.width / 2), int(bh / 2 - t.height / 2)))
        bill = bill.rotate(18, resample=Image.BICUBIC, expand=True)
        c.alpha_composite(bill, (int(500 * u), int(520 * u)))
        _shape(c, [(560, 560), (620, 560), (640, 610), (590, 620)], C["back_d"], u)  # 날개 끝이 지폐를 덮음
    return c.reduce(K)


def croc_v2(w=1000, h=380):
    """왼쪽을 보는 악어 머리, 납작하고 기하학적인 실루엣 (외곽선 없음)"""
    k = 3
    W_, H_ = w * k, h * k
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    u = W_ / 1000
    v = H_ / 380
    C = V2

    def P(pts):
        return [(x * u, y * v) for x, y in pts]
    d = ImageDraw.Draw(im)
    # 아래턱
    d.polygon(P([(0, 250), (980, 230), (1000, 300), (940, 340), (0, 360)]), fill=C["croc_d"] + (255,))
    # 윗턱/머리
    top = [(0, 250), (0, 160), (140, 130), (420, 140), (700, 95), (900, 80), (1000, 150), (1000, 235)]
    d.polygon(P(top), fill=C["croc"] + (255,))
    # 윗면 하이라이트
    d.polygon(P([(30, 165), (420, 150), (700, 110), (880, 98), (700, 140), (420, 175), (30, 195)]), fill=C["croc_l"] + (255,))
    # 등 돌기 (뒤쪽)
    for i in range(5):
        x = 640 + i * 60
        d.polygon(P([(x, 100 - i * 2), (x + 26, 50), (x + 52, 92 - i * 2)]), fill=C["croc_d"] + (255,))
    # 눈두덩 + 눈
    d.ellipse(P([(560, 40), (680, 140)])[0] + P([(680, 140)])[0], fill=C["croc"] + (255,))
    d.ellipse(P([(590, 66)])[0] + P([(650, 116)])[0], fill=C["croc_eye"] + (255,))
    d.ellipse(P([(614, 70)])[0] + P([(626, 112)])[0], fill=(16, 16, 20, 255))
    # 이빨 (작고 단정하게)
    for i in range(11):
        x = 70 + i * 80
        d.polygon(P([(x, 248), (x + 22, 248), (x + 11, 274)]), fill=(240, 236, 222, 255))
    # 콧구멍
    d.ellipse(P([(40, 168)])[0] + P([(62, 182)])[0], fill=C["croc_d"] + (255,))
    return im.reduce(k)


# ── 주식 악어새 v3: 의인화(서 있는 캐릭터, 옷·표정) / 라인 일러스트 ─────────────
def _grad_fill(c, pts, top, bot, u, smooth=True, hl=None):
    """세로 그라데이션으로 칠한 도형 (+ 선택: 부드러운 하이라이트)"""
    S_ = c.width
    m = Image.new("L", (S_, S_), 0)
    q = _smooth(pts) if smooth else pts
    ImageDraw.Draw(m).polygon([(x * u, y * u) for x, y in q], fill=255)
    bb = m.getbbox()
    if not bb:
        return
    g = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    y0, y1 = bb[1], bb[3]
    for y in range(y0, y1 + 1, 2):
        t = (y - y0) / max(1, y1 - y0)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        gd.rectangle((bb[0], y, bb[2], y + 2), fill=col + (255,))
    if hl:
        h = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
        hx, hy, hr = hl
        ImageDraw.Draw(h).ellipse(((hx - hr) * u, (hy - hr) * u, (hx + hr) * u, (hy + hr) * u), fill=(255, 255, 255, 70))
        g.alpha_composite(h.filter(ImageFilter.GaussianBlur(hr * u * 0.5)))
    g.putalpha(ImageChops.multiply(g.getchannel("A"), m))
    c.alpha_composite(g)


def bird_toon(size=800):
    """의인화 악어새: 두 발로 서서 남색 조끼+금색 넥타이, 큰 눈·눈썹으로 자신만만한 미소, 한 손엔 상승 차트 폰"""
    S_ = size * K
    c = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    u = S_ / 1000
    d = ImageDraw.Draw(c)
    # 그림자
    sh = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((330 * u, 900 * u, 670 * u, 950 * u), fill=(0, 0, 0, 70))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * u)))
    # 다리
    for x in (430, 560):
        d.rounded_rectangle(((x - 14) * u, 760 * u, (x + 14) * u, 905 * u), radius=int(14 * u), fill=(92, 104, 120, 255))
        d.ellipse(((x - 50) * u, 890 * u, (x + 40) * u, 925 * u), fill=(70, 80, 96, 255))
    # 꼬리
    _grad_fill(c, [(330, 700), (230, 780), (250, 800), (360, 740)], (40, 42, 52), (24, 26, 32), u)
    # 몸 (배 크림색, 서 있는 서양배 모양)
    body = [(500, 430), (620, 480), (670, 620), (640, 760), (500, 800), (360, 760), (330, 620), (380, 480)]
    _grad_fill(c, body, (246, 230, 204), (222, 196, 160), u, hl=(450, 560, 80))
    # 조끼 (남색, 몸 양옆)
    _masked(c, body, lambda lay: (_grad_fill(lay, [(300, 440), (470, 470), (440, 820), (300, 820)], (34, 46, 78), (20, 28, 52), u),
                                  _grad_fill(lay, [(530, 470), (700, 440), (700, 820), (560, 820)], (34, 46, 78), (20, 28, 52), u)), u)
    # 넥타이 (금색)
    _grad_fill(c, [(486, 480), (514, 480), (530, 520), (500, 640), (470, 520)], (236, 196, 96), (196, 150, 60), u, smooth=False)
    d = ImageDraw.Draw(c)
    d.polygon([(484 * u, 470 * u), (516 * u, 470 * u), (506 * u, 492 * u), (494 * u, 492 * u)], fill=(206, 160, 70, 255))
    # 날개-팔 (왼쪽: 허리에 손, 오른쪽: 폰 들기)
    _grad_fill(c, [(360, 500), (300, 560), (290, 650), (340, 660), (370, 580)], (122, 138, 160), (92, 106, 128), u)
    _grad_fill(c, [(640, 500), (720, 540), (760, 600), (730, 620), (660, 580)], (122, 138, 160), (92, 106, 128), u)
    # 폰 (상승 차트)
    ph = [(720, 520), (800, 500), (830, 620), (750, 640)]
    _grad_fill(c, ph, (30, 34, 44), (20, 22, 30), u, smooth=False)
    scr = [(732, 532), (792, 517), (816, 610), (757, 626)]
    _grad_fill(c, scr, (236, 246, 240), (214, 232, 222), u, smooth=False)
    d = ImageDraw.Draw(c)
    d.line([(742 * u, 608 * u), (760 * u, 585 * u), (776 * u, 592 * u), (800 * u, 545 * u)], fill=(46, 160, 100, 255), width=int(7 * u), joint="curve")
    d.polygon([(800 * u, 538 * u), (808 * u, 556 * u), (790 * u, 552 * u)], fill=(46, 160, 100, 255))
    _grad_fill(c, [(720, 590), (760, 575), (775, 610), (735, 625)], (122, 138, 160), (92, 106, 128), u)  # 폰 쥔 손
    # 머리 (큰 머리, 의인화 비율)
    head = [(500, 120), (620, 150), (680, 250), (660, 370), (580, 440), (470, 445), (380, 400), (340, 290), (370, 180)]
    _grad_fill(c, head, (250, 248, 242), (228, 224, 214), u, hl=(450, 210, 90))
    # 검은 정수리 깃 + 눈 아래 검은 띠 (악어새 무늬)
    _masked(c, head, lambda lay: _grad_fill(lay, [(300, 90), (720, 90), (720, 220), (600, 205), (480, 215), (300, 250)], (44, 46, 56), (28, 30, 38), u), u)
    _masked(c, head, lambda lay: _grad_fill(lay, [(330, 330), (440, 300), (700, 290), (700, 335), (450, 345), (330, 375)], (44, 46, 56), (28, 30, 38), u), u)
    # 뒷머리 깃털 한 가닥
    _grad_fill(c, [(380, 160), (300, 120), (330, 170), (370, 200)], (44, 46, 56), (28, 30, 38), u)
    d = ImageDraw.Draw(c)
    # 눈 (큰 눈 + 반짝임) & 눈썹 (자신만만)
    for ex in (500, 600):
        d.ellipse(((ex - 44) * u, 236 * u, (ex + 44) * u, 330 * u), fill=(255, 255, 255, 255))
        d.ellipse(((ex - 22) * u, 252 * u, (ex + 26) * u, 312 * u), fill=(58, 44, 30, 255))
        d.ellipse(((ex - 12) * u, 262 * u, (ex + 16) * u, 302 * u), fill=(14, 12, 12, 255))
        d.ellipse(((ex - 6) * u, 262 * u, (ex + 8) * u, 276 * u), fill=(255, 255, 255, 255))
        d.ellipse(((ex + 6) * u, 290 * u, (ex + 12) * u, 296 * u), fill=(255, 255, 255, 220))
        # 윗눈꺼풀 살짝 (여유로운 표정)
        d.chord(((ex - 46) * u, 232 * u, (ex + 46) * u, 300 * u), 190, 350, fill=(236, 232, 222, 255))
    d.line([(452 * u, 226 * u), (540 * u, 216 * u)], fill=(28, 30, 38, 255), width=int(10 * u))
    d.line([(562 * u, 214 * u), (648 * u, 232 * u)], fill=(28, 30, 38, 255), width=int(10 * u))
    # 부리 (작고 단정)
    _grad_fill(c, [(560, 330), (640, 350), (560, 372)], (56, 58, 66), (32, 34, 40), u, smooth=False)
    d = ImageDraw.Draw(c)
    d.line([(560 * u, 352 * u), (620 * u, 352 * u)], fill=(20, 20, 24, 255), width=int(3 * u))
    # 미소 (부리 옆 살짝 올라감)
    d.arc((520 * u, 330 * u, 570 * u, 380 * u), 60, 150, fill=(60, 50, 50, 255), width=int(5 * u))
    # 금테 안경 (한쪽)
    d.ellipse((546 * u, 228 * u, 654 * u, 338 * u), outline=(216, 174, 84, 255), width=int(7 * u))
    return c.reduce(K)


def bird_line(size=800, ink=(30, 32, 40), fill_body=(120, 136, 156), fill_belly=(240, 222, 192), accent=(214, 172, 84)):
    """라인 일러스트 악어새: 일정한 굵기의 선 + 최소한의 면 (아이콘·로고용)"""
    S_ = size * K
    c = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    u = S_ / 1000
    lw = int(14 * u)
    d = ImageDraw.Draw(c)

    def poly(pts, fill=None, close=True):
        q = _smooth(pts) if close else pts
        P = [(x * u, y * u) for x, y in q]
        if fill:
            d.polygon(P, fill=fill + (255,))
        d.line(P + ([P[0]] if close else []), fill=ink + (255,), width=lw, joint="curve")
    # 다리
    for x0, x1 in ((450, 440), (530, 545)):
        d.line([(x0 * u, 700 * u), (x1 * u, 860 * u)], fill=ink + (255,), width=lw)
        d.line([((x1 - 30) * u, 860 * u), ((x1 + 30) * u, 860 * u)], fill=ink + (255,), width=lw)
    # 몸 · 배
    poly([(290, 580), (380, 470), (540, 440), (660, 480), (690, 590), (620, 690), (480, 720), (340, 680)], fill_body)
    poly([(420, 610), (560, 570), (680, 600), (620, 690), (480, 720), (400, 690)], fill_belly)
    # 꼬리
    poly([(300, 580), (180, 620), (300, 640)], ink, close=False)
    # 날개 선
    d.line([(380 * u, 520 * u), (500 * u, 500 * u), (590 * u, 560 * u)], fill=ink + (255,), width=lw, joint="curve")
    # 머리
    poly([(560, 300), (640, 250), (730, 262), (775, 330), (750, 410), (670, 450), (590, 440), (550, 380)], (252, 250, 244))
    # 머리 무늬 (정수리, 눈 띠) — 선 안쪽 채움
    d.chord((556 * u, 246 * u, 778 * u, 420 * u), 200, 330, fill=ink + (255,))
    d.line([(575 * u, 365 * u), (765 * u, 355 * u)], fill=ink + (255,), width=int(22 * u))
    # 부리
    poly([(770, 350), (870, 372), (768, 392)], ink, close=False)
    d.polygon([(770 * u, 350 * u), (870 * u, 372 * u), (768 * u, 392 * u)], fill=ink + (255,))
    # 눈 + 안경
    d.ellipse((690 * u, 336 * u, 726 * u, 372 * u), fill=(255, 255, 255, 255))
    d.ellipse((700 * u, 344 * u, 720 * u, 366 * u), fill=ink + (255,))
    d.ellipse((676 * u, 322 * u, 740 * u, 386 * u), outline=accent + (255,), width=int(8 * u))
    return c.reduce(K)


# ── 주식 악어새 v4: 굵은 외곽선 치비 스타일 (악어 + 주둥이 위 악어새) ─────────────
CH = {
    "ink": (30, 26, 24), "g": (138, 196, 104), "g_d": (92, 150, 74), "g_l": (176, 220, 140),
    "cream": (252, 238, 196), "cream_d": (226, 206, 160), "pink": (240, 128, 128), "tooth": (255, 255, 250),
    "blush": (250, 150, 150), "y": (255, 200, 60),
    "bill": (120, 186, 120), "bill_d": (78, 140, 86), "bill_l": (214, 238, 200),
    "b_back": (120, 140, 166), "b_belly": (250, 246, 236), "b_black": (34, 34, 40), "gold": (226, 178, 70),
}


def _ink(c, pts, fill, u, lw=12, smooth=True):
    """굵은 외곽선 + 면 채우기 (외곽선이 바깥으로 lw 만큼)"""
    d = ImageDraw.Draw(c)
    q = _smooth(pts) if smooth else pts
    P = [(x * u, y * u) for x, y in q]
    d.line(P + [P[0]], fill=CH["ink"] + (255,), width=int(lw * 2 * u), joint="curve")
    for x, y in (P[0],):
        r = lw * u
        d.ellipse((x - r, y - r, x + r, y + r), fill=CH["ink"] + (255,))
    d.polygon(P, fill=fill + (255,))


def _ink_ell(c, box, fill, u, lw=12):
    d = ImageDraw.Draw(c)
    x0, y0, x1, y1 = [v * u for v in box]
    o = lw * u
    d.ellipse((x0 - o, y0 - o, x1 + o, y1 + o), fill=CH["ink"] + (255,))
    d.ellipse((x0, y0, x1, y1), fill=fill + (255,))


def _bill_fan(n=4, w=230, h=120, k=3, spread=16):
    """부채꼴로 펼친 초록 지폐 다발. 반환 (이미지, 손잡이 위치) — 손잡이는 지폐 왼쪽 아래 모서리"""
    from . import draw as G_
    L = int((w + h) * 1.6)
    out = Image.new("RGBA", (L * k, L * k), (0, 0, 0, 0))
    pv = (int(L * k * 0.35), int(L * k * 0.65))  # 회전 중심(손)
    for i in range(n):
        b = Image.new("RGBA", ((w + 24) * k, (h + 24) * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(b)
        d.rounded_rectangle((0, 0, (w + 23) * k, (h + 23) * k), radius=14 * k, fill=CH["ink"] + (255,))
        d.rounded_rectangle((10 * k, 10 * k, (w + 13) * k, (h + 13) * k), radius=8 * k, fill=CH["bill"] + (255,))
        d.rounded_rectangle((24 * k, 24 * k, (w - 1) * k, (h - 1) * k), radius=6 * k, outline=CH["bill_l"] + (255,), width=4 * k)
        cx, cy = (w + 24) * k / 2, (h + 24) * k / 2
        d.ellipse((cx - 34 * k, cy - 34 * k, cx + 34 * k, cy + 34 * k), fill=CH["bill_d"] + (255,))
        t = G_.text_img("$", "Black", 52 * k, CH["bill_l"])
        b.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))
        lay = Image.new("RGBA", out.size, (0, 0, 0, 0))
        lay.alpha_composite(b, (pv[0] - int(20 * k), pv[1] - b.height + int(20 * k)))
        lay = lay.rotate(28 + (n - 1 - i) * spread, resample=Image.BICUBIC, center=pv)
        out.alpha_composite(lay)
    return out.reduce(k), (pv[0] / k, pv[1] / k)


def croc_chibi(size=800, bird=True, money=True, sparkle=True):
    """치비 악어 캐릭터: 2등신, 굵은 외곽선, 긴 주둥이·솟은 눈·등 비늘, 한 손엔 돈다발. 주둥이 위엔 안경 쓴 작은 악어새."""
    K3 = 3
    S_ = size * K3
    c = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    u = S_ / 1000
    d = ImageDraw.Draw(c)
    # 꼬리 + 등 비늘
    for x, y in ((150, 790), (210, 760), (270, 720), (300, 660), (300, 590)):
        _ink(c, [(x - 30, y + 10), (x, y - 40), (x + 30, y + 10)], CH["g_d"], u, 10, smooth=False)
    _ink(c, [(330, 690), (230, 760), (110, 810), (80, 850), (160, 860), (270, 830), (340, 790)], CH["g"], u)
    # 다리
    _ink_ell(c, (300, 800, 420, 900), CH["g"], u)
    _ink_ell(c, (470, 810, 590, 905), CH["g"], u)
    # 몸통 + 배
    _ink(c, [(330, 470), (480, 440), (590, 500), (620, 640), (590, 790), (470, 860), (340, 840), (290, 720), (295, 580)], CH["g"], u)
    _ink(c, [(410, 560), (530, 540), (580, 640), (565, 780), (480, 830), (395, 800), (375, 680)], CH["cream"], u, 8)
    d = ImageDraw.Draw(c)
    for y in (620, 680, 740, 790):
        d.arc((390 * u, (y - 30) * u, 570 * u, (y + 20) * u), 20, 160, fill=CH["cream_d"] + (255,), width=int(7 * u))
    # 뒤쪽 팔 (돈 드는 팔)
    fan_img = None
    if money:
        fan, (px, py) = _bill_fan()
        sc = 200 * u / 230
        fan_img = fan.resize((int(fan.width * sc), int(fan.height * sc)), Image.LANCZOS)
        fan_pos = (int(815 * u - px * sc), int(650 * u - py * sc))
    _ink(c, [(570, 560), (680, 560), (790, 610), (800, 660), (700, 670), (590, 630)], CH["g"], u)
    if fan_img is not None:
        c.alpha_composite(fan_img, fan_pos)
    _ink_ell(c, (770, 600, 860, 690), CH["g"], u)
    # 머리 (넓적) + 긴 주둥이
    _ink(c, [(840, 330), (890, 370), (880, 440), (780, 470), (600, 480), (560, 410), (600, 330), (720, 310)], CH["g"], u)  # 주둥이
    _ink(c, [(300, 330), (360, 230), (470, 200), (580, 240), (630, 330), (610, 440), (500, 490), (370, 480), (300, 420)], CH["g"], u)  # 머리
    d = ImageDraw.Draw(c)
    # 주둥이 윗면 밝은 띠
    d.polygon([(p[0] * u, p[1] * u) for p in _smooth([(620, 345), (740, 330), (850, 345), (860, 372), (740, 362), (620, 378)])], fill=CH["g_l"] + (255,))
    # 입 (활짝 웃음): 아래턱 크림 + 혀
    _ink(c, [(470, 410), (860, 410), (820, 470), (640, 500), (500, 480)], CH["cream"], u, 9)
    d = ImageDraw.Draw(c)
    d.polygon([(p[0] * u, p[1] * u) for p in _smooth([(560, 420), (760, 420), (720, 470), (600, 478)])], fill=CH["pink"] + (255,))
    d.line([(470 * u, 410 * u), (860 * u, 410 * u)], fill=CH["ink"] + (255,), width=int(9 * u))
    for i in range(8):  # 윗니
        x = 520 + i * 42
        d.polygon([(x * u, 412 * u), ((x + 22) * u, 412 * u), ((x + 11) * u, 436 * u)], fill=CH["tooth"] + (255,), outline=CH["ink"] + (255,))
    # 콧구멍 혹 + 콧구멍
    _ink_ell(c, (810, 320, 880, 360), CH["g"], u, 9)
    d = ImageDraw.Draw(c)
    d.ellipse((826 * u, 332 * u, 840 * u, 344 * u), fill=CH["ink"] + (255,))
    d.ellipse((852 * u, 332 * u, 866 * u, 344 * u), fill=CH["ink"] + (255,))
    # 위로 솟은 눈 (악어 특징) + 큰 눈동자
    for ex, ey, r in ((420, 250, 70), (545, 235, 64)):
        _ink_ell(c, (ex - r, ey - r, ex + r, ey + r), CH["g"], u)
        d = ImageDraw.Draw(c)
        d.ellipse(((ex - r * 0.62) * u, (ey - r * 0.55) * u, (ex + r * 0.62) * u, (ey + r * 0.7) * u), fill=(255, 255, 255, 255))
        d.ellipse(((ex - r * 0.36) * u, (ey - r * 0.32) * u, (ex + r * 0.34) * u, (ey + r * 0.6) * u), fill=CH["ink"] + (255,))
        d.ellipse(((ex - r * 0.18) * u, (ey - r * 0.22) * u, (ex + r * 0.02) * u, (ey - r * 0.02) * u), fill=(255, 255, 255, 255))
    # 볼터치
    bl = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    ImageDraw.Draw(bl).ellipse((335 * u, 375 * u, 425 * u, 420 * u), fill=(255, 120, 130, 210))
    c.alpha_composite(bl.filter(ImageFilter.GaussianBlur(8 * u)))
    # 앞쪽 팔 (주먹, 가슴 앞)
    _ink_ell(c, (330, 560, 430, 650), CH["g"], u)
    d = ImageDraw.Draw(c)
    d.arc((350 * u, 585 * u, 410 * u, 630 * u), 200, 340, fill=CH["ink"] + (255,), width=int(6 * u))
    # 주둥이 위 작은 악어새
    if bird:
        bx, by = 700, 255
        _ink(c, [(bx - 70, by + 30), (bx - 120, by + 50), (bx - 70, by + 55)], CH["b_black"], u, 8, smooth=False)  # 꼬리
        _ink_ell(c, (bx - 80, by - 20, bx + 40, by + 70), CH["b_back"], u, 9)  # 몸
        d = ImageDraw.Draw(c)
        d.ellipse(((bx - 30) * u, (by + 10) * u, (bx + 36) * u, (by + 66) * u), fill=CH["b_belly"] + (255,))
        _ink_ell(c, (bx - 10, by - 90, bx + 80, by), CH["b_belly"], u, 9)  # 머리
        d = ImageDraw.Draw(c)
        d.chord(((bx - 10) * u, (by - 90) * u, (bx + 80) * u, (by + 0) * u), 185, 355, fill=CH["b_black"] + (255,))
        d.line([((bx - 6) * u, (by - 40) * u), ((bx + 78) * u, (by - 46) * u)], fill=CH["b_black"] + (255,), width=int(12 * u))
        d.polygon([((bx + 76) * u, (by - 50) * u), ((bx + 120) * u, (by - 42) * u), ((bx + 76) * u, (by - 32) * u)], fill=CH["ink"] + (255,))
        d.ellipse(((bx + 42) * u, (by - 54) * u, (bx + 62) * u, (by - 34) * u), fill=(255, 255, 255, 255))
        d.ellipse(((bx + 48) * u, (by - 50) * u, (bx + 60) * u, (by - 38) * u), fill=CH["ink"] + (255,))
        d.ellipse(((bx + 36) * u, (by - 60) * u, (bx + 68) * u, (by - 28) * u), outline=CH["gold"] + (255,), width=int(5 * u))
        for lx in (bx - 30, bx + 5):
            d.line([(lx * u, (by + 70) * u), (lx * u, (by + 92) * u)], fill=CH["ink"] + (255,), width=int(7 * u))
    # 반짝 표시
    if sparkle:
        for pts in ([(830, 120), (870, 110), (850, 220), (830, 225)], [(930, 160), (965, 180), (900, 270), (885, 258)]):
            _ink(c, pts, CH["y"], u, 0, smooth=False)
    return c.reduce(K3)


# ── 주식 악어새 v5: 입을 쩍 벌린 악어 + 입안의 악어새(주인공) ─────────────────
def _bird_chibi(c, cx, by, s, u, calc=True):
    """입안에 선 치비 악어새. (cx, by)=발 아래 중심, s=크기 배율. 금테 안경, 계산기를 안고 있음"""
    def X(v):
        return cx + v * s

    def Y(v):
        return by + v * s
    ink = CH["ink"] + (255,)
    d = ImageDraw.Draw(c)
    # 다리
    for lx in (-26, 22):
        d.line([(X(lx) * u, Y(-60) * u), (X(lx) * u, Y(0) * u)], fill=ink, width=int(9 * s * u))
        d.line([(X(lx - 18) * u, Y(0) * u), (X(lx + 20) * u, Y(0) * u)], fill=ink, width=int(9 * s * u))
    # 꼬리
    _ink(c, [(X(-70), Y(-120)), (X(-150), Y(-110)), (X(-145), Y(-90)), (X(-70), Y(-95))], CH["b_black"], u, 8 * s, smooth=False)
    # 몸통
    _ink(c, [(X(-80), Y(-150)), (X(0), Y(-190)), (X(80), Y(-150)), (X(85), Y(-90)), (X(40), Y(-55)), (X(-40), Y(-55)), (X(-85), Y(-95))], CH["b_back"], u, 10 * s)
    d = ImageDraw.Draw(c)
    d.polygon([(x * u, y * u) for x, y in _smooth([(X(-35), Y(-150)), (X(40), Y(-160)), (X(70), Y(-100)), (X(30), Y(-62)), (X(-30), Y(-62)), (X(-50), Y(-100))])],
              fill=CH["b_belly"] + (255,))
    # 머리 (크게)
    _ink_ell(c, (X(-75), Y(-330), X(85), Y(-175)), CH["b_belly"], u, 10 * s)
    d = ImageDraw.Draw(c)
    d.chord((X(-75) * u, Y(-330) * u, X(85) * u, Y(-175) * u), 180, 360, fill=CH["b_black"] + (255,))          # 검은 정수리
    d.arc((X(-60) * u, Y(-300) * u, X(80) * u, Y(-200) * u), 195, 345, fill=(255, 255, 255, 255), width=int(14 * s * u))  # 흰 눈썹줄
    d.line([(X(-70) * u, Y(-238) * u), (X(84) * u, Y(-246) * u)], fill=CH["b_black"] + (255,), width=int(20 * s * u))     # 눈 띠
    # 부리
    d.polygon([(X(80) * u, Y(-258) * u), (X(150) * u, Y(-244) * u), (X(80) * u, Y(-228) * u)], fill=ink)
    # 눈 (반짝) + 금테 안경
    d.ellipse((X(26) * u, Y(-266) * u, X(58) * u, Y(-232) * u), fill=(255, 255, 255, 255))
    d.ellipse((X(34) * u, Y(-260) * u, X(56) * u, Y(-236) * u), fill=ink)
    d.ellipse((X(40) * u, Y(-258) * u, X(48) * u, Y(-250) * u), fill=(255, 255, 255, 255))
    d.ellipse((X(16) * u, Y(-276) * u, X(68) * u, Y(-222) * u), outline=CH["gold"] + (255,), width=int(7 * s * u))
    # 볼터치
    bl = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(bl).ellipse((X(-10) * u, Y(-215) * u, X(30) * u, Y(-195) * u), fill=(255, 130, 140, 190))
    c.alpha_composite(bl.filter(ImageFilter.GaussianBlur(5 * s * u)))
    # 계산기 (상승 차트 화면)
    if calc:
        _ink(c, [(X(0), Y(-175)), (X(95), Y(-185)), (X(105), Y(-60)), (X(10), Y(-50))], (60, 66, 86), u, 8 * s, smooth=False)
        d = ImageDraw.Draw(c)
        d.polygon([(X(12) * u, Y(-165) * u), (X(88) * u, Y(-173) * u), (X(92) * u, Y(-128) * u), (X(16) * u, Y(-120) * u)], fill=(196, 236, 180, 255))
        d.line([(X(20) * u, Y(-128) * u), (X(42) * u, Y(-142) * u), (X(58) * u, Y(-136) * u), (X(84) * u, Y(-164) * u)],
               fill=(30, 140, 70, 255), width=int(6 * s * u), joint="curve")
        for r in range(2):
            for q in range(3):
                x0, y0 = 22 + q * 24, -108 + r * 24
                d.rounded_rectangle((X(x0) * u, Y(y0) * u, X(x0 + 16) * u, Y(y0 + 14) * u), radius=int(3 * s * u),
                                    fill=(CH["y"] if (r, q) == (1, 2) else (226, 230, 240)) + (255,))
        # 날개(팔)로 계산기 감싸기
        _ink(c, [(X(-40), Y(-150)), (X(20), Y(-140)), (X(30), Y(-95)), (X(-20), Y(-90))], CH["b_back"], u, 8 * s)


def croc_mouth(w=1000, bird=True):
    """옆모습 악어가 입을 크게 벌리고 있고, 그 입안에 악어새가 서 있는 장면. 크기 w × 0.62w"""
    K3 = 3
    W_, H_ = w * K3, int(w * 0.62) * K3
    c = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    u = W_ / 1000
    ink = CH["ink"] + (255,)
    sh = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((60 * u, 575 * u, 990 * u, 612 * u), fill=(0, 0, 0, 60))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * u)))
    # 꼬리 + 몸통 (길쭉하게 오른쪽으로)
    _ink(c, [(880, 470), (950, 430), (970, 470), (940, 540), (860, 560)], CH["g"], u)
    _ink(c, [(590, 230), (700, 180), (820, 230), (920, 360), (935, 470), (860, 560), (680, 572), (600, 480)], CH["g"], u)
    _ink_ell(c, (820, 520, 905, 598), CH["g"], u)
    # 입안 (어두운 분홍)
    _ink(c, [(80, 120), (610, 245), (650, 380), (630, 495), (70, 505)], (176, 74, 88), u, 10, smooth=False)
    d = ImageDraw.Draw(c)
    d.polygon([(x * u, y * u) for x, y in _smooth([(110, 478), (380, 448), (600, 452), (615, 492), (100, 500)])], fill=CH["pink"] + (255,))
    # 윗턱 (두껍고 크게 열림)
    _ink(c, [(20, 30), (340, 80), (640, 190), (700, 290), (640, 300), (600, 250), (330, 165), (60, 115)], CH["g"], u, 12, smooth=False)
    d = ImageDraw.Draw(c)
    d.polygon([(x * u, y * u) for x, y in [(40, 50), (340, 98), (600, 190), (590, 205), (335, 120), (50, 75)]], fill=CH["g_l"] + (255,))
    # 아랫턱
    _ink(c, [(40, 505), (630, 495), (710, 535), (700, 595), (70, 590), (20, 548)], CH["g"], u, 12, smooth=False)
    d = ImageDraw.Draw(c)
    # 윗니 (아래로) — 윗턱 안쪽 선을 따라
    for i in range(11):
        x = 80 + i * 48
        y = 115 + (x - 60) * (250 - 115) / (600 - 60)
        d.polygon([(x * u, (y + 2) * u), ((x + 26) * u, (y + 8) * u), ((x + 12) * u, (y + 36) * u)], fill=CH["tooth"] + (255,), outline=ink)
    # 아랫니 (위로)
    for i in range(11):
        x = 80 + i * 48
        d.polygon([(x * u, 503 * u), ((x + 26) * u, 501 * u), ((x + 13) * u, 472 * u)], fill=CH["tooth"] + (255,), outline=ink)
    # 콧구멍 혹
    _ink_ell(c, (0, 5, 80, 55), CH["g"], u, 10)
    d = ImageDraw.Draw(c)
    d.ellipse((24 * u, 22 * u, 40 * u, 38 * u), fill=ink)
    # 등 비늘
    for x, y in ((735, 185), (795, 205), (850, 245), (900, 300)):
        _ink(c, [(x - 22, y + 8), (x, y - 30), (x + 22, y + 8)], CH["g_d"], u, 9, smooth=False)
    # 솟은 눈 (느긋하게 반쯤 감은 눈으로 새를 내려다봄)
    _ink_ell(c, (640, 120, 740, 215), CH["g"], u)
    d = ImageDraw.Draw(c)
    d.ellipse((658 * u, 138 * u, 722 * u, 202 * u), fill=(255, 255, 255, 255))
    d.ellipse((660 * u, 160 * u, 690 * u, 196 * u), fill=ink)
    d.ellipse((665 * u, 164 * u, 675 * u, 174 * u), fill=(255, 255, 255, 255))
    d.chord((656 * u, 134 * u, 724 * u, 206 * u), 190, 350, fill=CH["g"] + (255,))
    d.line([(656 * u, 168 * u), (724 * u, 168 * u)], fill=ink, width=int(6 * u))
    # 볼터치 (악어도 기분 좋음)
    bl = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    ImageDraw.Draw(bl).ellipse((690 * u, 235 * u, 750 * u, 262 * u), fill=(255, 130, 140, 170))
    c.alpha_composite(bl.filter(ImageFilter.GaussianBlur(6 * u)))
    # 앞다리
    _ink(c, [(610, 525), (665, 525), (675, 600), (600, 600)], CH["g"], u)
    # 주인공: 입안의 악어새
    if bird:
        _bird_chibi(c, 330, 478, 1.0, u)
    return c.reduce(K3)


def croc_bird(size=400, mood=None):
    """채널 캐릭터(사용자 일러스트: 입 벌린 악어 + 지폐 문 악어새). size = 결과 높이(px)"""
    p = Path(__file__).resolve().parents[1] / "assets/media/character_croc_bird_cutout.png"
    im = Image.open(p).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)
