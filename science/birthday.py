"""지식창고 쇼츠 #3 · 생일이 같은 사람, 몇 명이면 50%? (생일 문제)
  python3 science/birthday.py [--stills]
숫자: 모두 다를 확률 = Π(365-i)/365, i=0..n-1 → n=23: 49.27% → 같은 쌍 있을 확률 50.73%
      23명 쌍의 수 23C2 = 253 · n=57: 99.01% · n=70: 99.92% (윤년 · 생일 쏠림 무시)
사진: 위키미디어 공용(CC BY-SA) — 화면 왼쪽 아래 출처 자동 표기
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, CREAM, DIM, CORAL, BLUE, MINT, GOLD

OUT = K.HERE / "out" / "birthday"
HEAD = {"kicker": "확률의 함정", "title": "생일 같은 두 사람,\n몇 명이면 만날까?", "highlight": "몇 명"}
SAY = {"183명": "백팔십삼 명", "365일": "삼백육십오 일", "23명": "스물세 명", "22명": "스물두 명", "23쌍": "스물세 쌍", "50명": "오십 명", "97%": "구십칠 퍼센트", "심판 1명": "심판 한 명",
       "253쌍": "이백오십삼 쌍", "365분의 364": "삼백육십오 분의 삼백육십사", "365분의 363": "삼백육십오 분의 삼백육십삼",
       "49%": "사십구 퍼센트", "51%": "오십일 퍼센트", "57명": "오십칠 명", "70명": "칠십 명",
       "99.9%": "구십구 점 구 퍼센트", "99%": "구십구 퍼센트", "50%": "오십 퍼센트", "100%": "백 퍼센트"}
CX = W / 2


def p_same(n):
    q = 1.0
    for i in range(n):
        q *= (365 - i) / 365
    return 1 - q


def ball(r, col, light=(-0.4, -0.45)):
    """빛 · 그림자 들어간 구슬"""
    k = 3
    d = 2 * r * k
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    steps = 26
    for i in range(steps):
        u = i / steps
        rr = d / 2 * (1 - u * 0.92)
        cx = d / 2 + light[0] * d / 2 * u * 0.55
        cy = d / 2 + light[1] * d / 2 * u * 0.55
        sh = 0.45 + 0.75 * u
        c = tuple(min(255, int(v * sh + 255 * max(0, u - 0.8) * 1.6)) for v in col)
        dr.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=c + (255,))
    return im.resize((2 * r, 2 * r), Image.LANCZOS)


# ── 장면 ─────────────────────────────────────────────────────────
def s_hook(f, t, sc):
    K.band(f, "bday_cake", 380, 880, focus=(0.5, 0.3), dark=0.55, sat=0.9)
    k = G.ease_out(t / 0.6)
    G.blit(f, T("?명", 260, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (CX, 790 + (1 - k) * 30), k, "mm")
    o = G.appear(t, sc["L"][0] + 1.0, 0.3)
    G.blit(f, G.pill("같은 생일 두 사람 = ?명", "Black", 56, (10, 12, 20), CREAM, pad=(30, 12), radius=30), (CX, 1010), o, "mt")
    K.credit(f, K.credit_of("bday_cake"))


def s_guess(f, t, sc):
    """365칸 달력 — 절반(183칸)이 차오름"""
    cols, rows = 15, 25
    cw, chh, gap = 46, 21, 5
    gw = cols * (cw + gap) - gap
    x0, y0 = CX - gw / 2, 450
    n = int(G.clamp((t - 0.2) / 1.2) * 183)
    lay = Image.new("RGBA", (gw + 40, rows * (chh + gap) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(365):
        r, c = divmod(i, cols)
        x, y = 20 + c * (cw + gap), 20 + r * (chh + gap)
        if i < n:
            d.rounded_rectangle((x, y, x + cw, y + chh), 6, fill=(255, 150, 120, 255))
            d.rounded_rectangle((x, y, x + cw, y + chh * 0.45), 6, fill=(255, 190, 165, 255))
        else:
            d.rounded_rectangle((x, y, x + cw, y + chh), 6, fill=(44, 52, 82, 255))
            d.rounded_rectangle((x, y, x + cw, y + chh * 0.45), 6, fill=(56, 66, 100, 255))
    K.drop(f, lay, (x0 - 20, y0 - 20), "lt", 1, blur=14, alpha=0.5)
    G.blit(f, T("1년 = 365칸", 44, DIM, "ExtraBold"), (CX, y0 + rows * (chh + gap) + 20), 1, "mt")
    o = G.appear(t, sc["L"][-1], 0.3)
    big = T("183명?", 150, CORAL, "Black", stroke=8, stroke_fill=(0, 0, 0))
    G.blit(f, big, (CX, y0 + rows * (chh + gap) / 2), max(o, G.appear(t, 0.4, 0.3)), "mm")


def s_answer(f, t, sc):
    K.band(f, "soccer_lineup", 380, 880, focus=(0.35, 0.45), dark=0.45, sat=0.9)
    k = G.ease_out((t - 0.2) / 0.5)
    sc_ = 1.3 - 0.3 * k
    big = T("23명", 230, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0))
    big = big.resize((int(big.width * sc_), int(big.height * sc_)), Image.LANCZOS)
    G.blit(f, big, (CX, 640), k, "mm")
    o = G.appear(t, sc["L"][-1] + 0.3, 0.35)
    G.blit(f, G.pill("선수 22명 + 심판 1명", "Black", 54, (10, 12, 20), MINT, pad=(30, 12), radius=30), (CX, 1000), o, "mt")
    K.credit(f, K.credit_of("soccer_lineup"))


def s_pairs(f, t, sc):
    """23명을 원으로 → 둘씩 잇는 선이 253개까지"""
    n = 23
    cx, cy, R = CX, 790, 330
    pts = [(cx + R * math.cos(-math.pi / 2 + 2 * math.pi * i / n), cy + R * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    t0 = sc["L"][1] + 0.2
    m = int(G.clamp((t - t0) / 2.6) * len(pairs))
    if t < t0:  # 처음: '나' 한 명 기준으로만 22개
        m = 0
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    me = G.clamp(t / 1.2)
    for j in range(1, int(me * 22) + 1):
        d.line((pts[0], pts[j]), fill=BLUE + (200,), width=3)
    for (i, j) in pairs[:m]:
        d.line((pts[i], pts[j]), fill=(255, 140, 110, 110), width=2)
    f.alpha_composite(lay)
    for i, p in enumerate(pts):
        b = ball(22, GOLD if i == 0 else (120, 170, 255))
        G.blit(f, b, p, 1, "mm")
    G.blit(f, T("나", 34, (10, 12, 20), "Black"), pts[0], 1, "mm")
    if m == 0:
        lab, col = f"나와 비교: {int(me * 22)}쌍", BLUE
    else:
        lab, col = f"아무 둘이나: {max(m, 22)}쌍", CORAL
    G.blit(f, G.pill(lab, "Black", 56, (10, 12, 20), col, pad=(30, 12), radius=30), (CX, 1180), 1, "mt")


def s_calc(f, t, sc):
    L = sc["L"]
    y = 450
    G.blit(f, T("모두 생일이 다를 확률", 50, DIM, "ExtraBold"), (CX, y), 1, "mt")
    o1 = G.appear(t, L[0] + 0.3, 0.3)
    G.blit(f, T("364/365 × 363/365 × …", 70, CREAM, "Black"), (CX, y + 80), o1, "mt")
    o2 = G.appear(t, L[1] + 0.8 if len(L) > 1 else 1.5, 0.3)
    G.blit(f, T("× 343/365", 70, CREAM, "Black"), (CX, y + 170), o2, "mt")
    G.blit(f, T("(23명까지 22번)", 36, DIM, "SemiBold"), (CX, y + 260), o2, "mt")
    # 확률 바: 100% → 49.3%
    kk = G.clamp((t - (L[1] if len(L) > 1 else 1.0)) / 1.6)
    q = 1 - p_same(max(1, int(kk * 23)))
    bw, bh, bx, by = 820, 70, CX - 410, y + 360
    bar = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle((0, 0, bw - 1, bh - 1), 20, fill=(40, 46, 72, 255))
    fw = int(bw * q)
    for yy in range(bh):
        c = tuple(min(255, int(v * (1.15 - yy / bh * 0.45))) for v in BLUE)
        bd.line((10, yy, max(10, fw - 10), yy), fill=c + (255,))
    m = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, bw - 1, bh - 1), 20, fill=255)
    bar.putalpha(m)
    K.drop(f, bar, (bx, by), "lt", 1, blur=12, alpha=0.5)
    G.blit(f, T(f"{q * 100:.1f}%", 72, BLUE, "Black"), (CX, by + bh + 24), 1, "mt")
    o3 = G.appear(t, L[-1] + 0.2, 0.35)
    G.blit(f, G.pill("같은 생일 한 쌍 이상 = 약 51%", "Black", 54, (10, 12, 20), GOLD, pad=(30, 12), radius=30), (CX, by + bh + 150), o3, "mt")


def s_curve(f, t, sc):
    x0, y0, gw, gh = 140, 1150, 800, 600
    xmax = 80
    d = ImageDraw.Draw(f)
    for p in (0, 0.5, 1.0):
        yy = y0 - gh * p
        d.line((x0, yy, x0 + gw, yy), fill=(255, 255, 255, 40), width=2)
        G.blit(f, T(f"{int(p * 100)}%", 30, DIM, "SemiBold"), (x0 - 16, yy), 1, "rm")
    for n in (0, 20, 40, 60, 80):
        G.blit(f, T(f"{n}명", 30, DIM, "SemiBold"), (x0 + gw * n / xmax, y0 + 16), 1, "mt")
    kk = G.clamp(t / 2.4)
    pts = [(x0 + gw * n / xmax, y0 - gh * p_same(n)) for n in range(0, int(kk * xmax) + 1)]
    if len(pts) > 1:
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
        poly = pts + [(pts[-1][0], y0), (x0, y0)]
        ImageDraw.Draw(lay).polygon(poly, fill=CORAL + (50,))
        f.alpha_composite(lay)
        for a, b in zip(pts, pts[1:]):
            K.glow_line(f, a, b, CORAL, width=6, glow=10) if False else d.line((a, b), fill=CORAL + (255,), width=7)
    marks = [(23, "23명 · 50.7%", GOLD, 0.0), (57, "57명 · 99%", MINT, sc["L"][-1] + 0.2)]
    for n, lab, col, at in marks:
        if n > kk * xmax:
            continue
        o = G.appear(t, at, 0.3)
        p = (x0 + gw * n / xmax, y0 - gh * p_same(n))
        G.blit(f, ball(16, col), p, o, "mm")
        dx, dy = {23: (-40, 60), 57: (-30, 70), 70: (40, 170)}[n]
        G.blit(f, G.pill(lab, "Black", 40, (10, 12, 20), col, pad=(18, 8), radius=20), (p[0] + dx, p[1] + dy), o, "mt")


def s_class(f, t, sc):
    """한 반 50명 — 책상마다 생일, 같은 생일 한 쌍이 반짝"""
    import random
    rnd = random.Random(7)
    days = [(m, d) for m in range(1, 13) for d in range(1, 29)]
    bd = rnd.sample(days, 50)
    a, b = 13, 36
    bd[b] = bd[a]
    # 칠판
    bw, bh = 760, 120
    board = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    dd = ImageDraw.Draw(board)
    dd.rounded_rectangle((0, 0, bw - 1, bh - 1), 14, fill=(118, 84, 52, 255))
    dd.rounded_rectangle((10, 10, bw - 11, bh - 11), 10, fill=(34, 74, 58, 255))
    board.alpha_composite(T("3학년 2반 · 50명", 52, (236, 240, 230), "ExtraBold"), (bw // 2 - 190, 28))
    K.drop(f, board, (CX, 430), "mt", 1, blur=12)
    cols, rows = 10, 5
    dw, dh, gx, gy = 84, 92, 12, 22
    x0 = CX - (cols * dw + (cols - 1) * gx) / 2
    y0 = 600
    hit = G.appear(t, sc["L"][-1] + 0.2, 0.3)
    pos = []
    for i in range(50):
        r, c = divmod(i, cols)
        x, y = x0 + c * (dw + gx), y0 + r * (dh + gy)
        pos.append((x + dw / 2, y + dh / 2))
        k = G.ease_out(G.clamp((t - i * 0.02) / 0.4))
        on = i in (a, b) and hit > 0
        top = (255, 196, 90) if on else (92, 104, 150)
        desk = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(desk)
        d2.rounded_rectangle((0, 8, dw - 1, dh - 1), 10, fill=tuple(int(v * 0.6) for v in top) + (255,))
        d2.rounded_rectangle((0, 0, dw - 1, dh - 14), 10, fill=top + (255,))
        m_, d_ = bd[i]
        desk.alpha_composite(T(f"{m_}/{d_}", 26, (10, 12, 20) if on else (226, 232, 250), "Black"), (dw // 2 - T(f"{m_}/{d_}", 26).width // 2, 24))
        G.blit(f, desk, (x, y + (1 - k) * 20), k)
    if hit > 0:
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).line((pos[a], pos[b]), fill=GOLD + (int(230 * hit),), width=6)
        f.alpha_composite(lay)
    G.blit(f, G.pill("50명 반 → 같은 생일 있을 확률 97%", "Black", 50, (10, 12, 20), GOLD, pad=(28, 12), radius=28),
           (CX, 1190), max(hit, G.appear(t, 0.3, 0.3)) if False else hit, "mt")


def s_end(f, t, sc):
    k = G.ease_out(t / 0.6)
    card = K.photo("bday_cake", 640, 460, (0.5, 0.3), radius=26)
    K.drop(f, card, (CX, 650 + (1 - k) * 30), "mm", k)
    G.blit(f, T("직관은 183명,\n숫자는 23명", 80, CREAM, "Black", highlight="23명", hl_fill=GOLD, align="center", line_gap=1.15),
           (CX, 930), G.appear(t, 0.3, 0.4), "mt")
    K.credit(f, K.credit_of("bday_cake"))


def draw_cover(f):
    G.blit(f, T("생일 같은 두 사람", 70, MINT, "ExtraBold"), (W / 2, 200), 1, "mt")
    G.blit(f, T("몇 명 모이면\n만날까?", 150, CREAM, "Black", highlight="몇 명", hl_fill=CORAL, align="center", line_gap=1.08,
                stroke=6, stroke_fill=(0, 0, 0)), (W / 2, 300), 1, "mt")
    card = K.photo("bday_cake", 760, 560, (0.5, 0.3), radius=30)
    K.drop(f, card, (W / 2, 1060), "mm")
    G.blit(f, T("?명", 240, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (W / 2, 1060), 1, "mm")


SCENES = [
    {"draw": s_hook, "min": 3.5, "narr": ["서로 생일이 같은 두 사람을 만나려면, 몇 명이 모여야 할까요?"]},
    {"draw": s_guess, "min": 3.5, "narr": ["많은 사람이 183명쯤을 떠올려요. | 1년 365일의 절반이니까요."]},
    {"draw": s_answer, "min": 3.5, "narr": ["그런데 23명만 모여도, | 생일 같은 두 사람이 있을 확률이 50%를 넘어요.",
                                            "축구장에 선수 22명과 심판 1명. | 딱 그 정도 인원이죠."]},
    {"draw": s_pairs, "min": 4.0, "narr": ["비밀은 이거예요. | 나랑 생일이 같을 필요는 없어요.", "아무나 두 사람만 같으면 되죠.",
                                           "23명이 둘씩 짝을 지으면, | 253쌍이나 나와요."]},
    {"draw": s_calc, "min": 4.0, "narr": ["계산은 거꾸로 해요. | 모두 생일이 다를 확률부터요.",
                                          "두 번째 사람은 365분의 364, 세 번째는 365분의 363. | 이렇게 23명까지 곱하면 약 49%.",
                                          "그러니 생일 같은 쌍이 하나라도 있을 확률은, 약 51%예요."]},
    {"draw": s_curve, "min": 4.0, "narr": ["사람이 늘수록 확률은 확 올라가요.", "57명이면 99%. | 거의 100%죠."]},
    {"draw": s_class, "min": 4.0, "narr": ["한 반에 50명이 넘던 학창 시절, 기억나세요?",
                                           "그 교실엔 97% 확률로, | 생일이 같은 친구가 꼭 한 쌍은 있었던 거예요."]},
    {"draw": s_end, "min": 3.0, "narr": ["다음에 23명 넘게 모이면, 생일을 한번 물어보세요. | 생각보다 자주 겹칠 거예요.", K.CTA]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
