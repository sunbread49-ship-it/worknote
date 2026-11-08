"""지식창고 쇼츠 #4 · 종이를 42번 접으면 두께가 얼마나 될까? (힌트: 투더문)
  python3 science/paper.py [--stills]
숫자: 종이 두께 0.1mm · n번 접기 = 2^n겹
      10번 1,024겹 = 10.24cm · 20번 = 104.9m(아파트 약 35층) · 30번 = 107.4km(우주 경계 100km 넘음)
      42번 = 2^42 × 0.1mm ≈ 439,805km > 지구~달 평균 384,400km · 2^42 = 4,398,046,511,104(약 4조 4천억)
      실제: 2002년 브리트니 갈리반(당시 미국 고등학생) 약 1.2km 휴지로 12번 접기 성공
사진: NASA(퍼블릭 도메인) — 화면 왼쪽 아래 출처 자동 표기
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, CREAM, DIM, CORAL, BLUE, MINT, GOLD

OUT = K.HERE / "out" / "paper"
HEAD = {"kicker": "두 배의 힘", "title": "종이를 42번 접으면\n두께는?", "highlight": "42번"}
SAY = {"42번": "마흔두 번", "0.1밀리미터": "영 점 일 밀리미터", "1,024겹": "천이십사 겹", "10센티미터": "십 센티미터",
       "100미터": "백 미터", "35층": "삼십오 층", "107킬로미터": "백칠 킬로미터", "44만 킬로미터": "사십사만 킬로미터",
       "38만 킬로미터": "삼십팔만 킬로미터", "4조 4천억": "사조 사천억", "7~8번": "일곱, 여덟 번", "12번": "열두 번",
       "1.2킬로미터": "일 점 이 킬로미터", "2002년": "이천이 년", "2를": "이를"}
CX = W / 2
PAPER = (246, 244, 236)


def sheet(w, h, tilt=0.0):
    """살짝 기울어진 종이 한 장(그라데이션 + 가장자리 두께)"""
    k = 2
    im = Image.new("RGBA", (w * k, (h + 30) * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sk = int(w * k * 0.18)
    top = [(sk, 0), (w * k, 0), (w * k - sk, h * k), (0, h * k)]
    d.polygon([(p[0], p[1] + 8 * k) for p in top], fill=(170, 168, 160, 255))
    d.polygon(top, fill=PAPER + (255,))
    shade = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(h * k):
        a = int(50 * i / (h * k))
        x0 = sk * (1 - i / (h * k))
        sd.line((x0, i, x0 + w * k - sk, i), fill=(150, 160, 190, a))
    im.alpha_composite(shade)
    return im.resize((w, h + 30), Image.LANCZOS)


def block(w, h, depth=40, top=PAPER, side=(196, 194, 186), front=(226, 224, 216), lines=0):
    """종이 뭉치 상자(위 · 앞 · 옆 면)"""
    im = Image.new("RGBA", (w + depth + 4, h + depth + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, depth), (depth, 0), (w + depth, 0), (w, depth)], fill=top + (255,))
    d.polygon([(w, depth), (w + depth, 0), (w + depth, h), (w, h + depth)], fill=side + (255,))
    d.rectangle((0, depth, w, h + depth), fill=front + (255,))
    for i in range(1, lines):
        y = depth + h * i / lines
        d.line((0, y, w, y), fill=(180, 178, 170, 255), width=1)
    return im


# ── 장면 ─────────────────────────────────────────────────────────
def s_hook(f, t, sc):
    K.band(f, "earthrise", 380, 880, focus=(0.5, 0.12), dark=0.45, sat=1.0)
    k = G.ease_out(t / 0.7)
    sh = sheet(520, 340)
    K.drop(f, sh, (CX, 900 + (1 - k) * 40), "mm", k)
    o = G.appear(t, sc["L"][0] + 0.9, 0.3)
    G.blit(f, T("×42번", 150, GOLD, "Black", stroke=8, stroke_fill=(0, 0, 0)), (CX, 900), o, "mm")
    G.blit(f, G.pill("두께 = ?", "Black", 58, (10, 12, 20), CREAM, pad=(30, 12), radius=30), (CX, 1110), o, "mt")
    K.credit(f, K.credit_of("earthrise"))


def s_double(f, t, sc):
    G.blit(f, T("종이 1장 ≈ 0.1mm", 64, CREAM, "Black", highlight="0.1mm", hl_fill=GOLD), (CX, 440), 1, "mt")
    xs = [200, 420, 640, 860]
    t1 = sc["L"][-1]
    for i, x in enumerate(xs):
        o = G.appear(t, t1 + i * 0.45, 0.3) if i else 1
        n = 2 ** i
        hpx = 30 * n
        b = block(150, hpx, 34, lines=n)
        K.drop(f, b, (x - 17, 1000), "mb", o, blur=12, alpha=0.5)
        G.blit(f, T(f"{n}겹", 54, GOLD if i == 3 else CREAM, "Black"), (x + 17, 1030), o, "mt")
        G.blit(f, T(f"{i}번 접기", 34, DIM, "ExtraBold"), (x + 17, 1100), o, "mt")
        if i:
            G.blit(f, T("×2", 44, CORAL, "Black"), ((xs[i - 1] + x) / 2, 1000 - 30 * n - 90), o, "mm")


def s_ten(f, t, sc):
    k = G.ease_out(G.clamp(t / 1.0))
    hpx = int(360 * k) + 2
    b = block(300, hpx, 60, lines=0)
    K.drop(f, b, (CX - 60, 1080), "mb", 1, blur=16)
    # 자
    rx = CX + 230
    d = ImageDraw.Draw(f)
    d.rounded_rectangle((rx, 1080 - 450, rx + 70, 1080), 10, fill=(250, 214, 110, 255))
    for i in range(0, 11):
        y = 1080 - i * 36
        d.line((rx, y, rx + (40 if i % 5 == 0 else 24), y), fill=(60, 50, 30, 255), width=4)
        if i % 5 == 0:
            G.blit(f, T(f"{i}", 26, (60, 50, 30), "Black"), (rx + 62, y), 1, "rm")
    G.blit(f, T("cm", 24, (60, 50, 30), "Black"), (rx + 35, 1080 - 435), 1, "mt")
    G.blit(f, T(f"{int(1024 * k):,}겹", 92, GOLD, "Black"), (CX, 500), 1, "mt")
    G.blit(f, T("10번 접기", 44, DIM, "ExtraBold"), (110, 430), 1, "lt")
    G.blit(f, G.pill("약 10cm", "Black", 56, (10, 12, 20), CREAM, pad=(28, 12), radius=28), (CX, 1120), G.appear(t, sc["L"][-1], 0.3), "mt")


def building(w, h, floors):
    im = Image.new("RGBA", (w + 30, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=(64, 78, 118, 255))
    d.polygon([(w, 0), (w + 30, 16), (w + 30, h), (w, h)], fill=(40, 50, 80, 255))
    fh = h / floors
    for i in range(floors):
        y = i * fh
        for c in range(4):
            x = 14 + c * (w - 28) / 4
            lit = (i * 7 + c * 3) % 5 == 0
            d.rectangle((x + 4, y + fh * 0.25, x + (w - 28) / 4 - 6, y + fh * 0.8), fill=(255, 214, 120, 255) if lit else (120, 150, 200, 255))
    return im


def s_twenty(f, t, sc):
    b = building(240, 600, 35)
    K.drop(f, b, (CX + 140, 1180), "mb", 1, blur=16)
    k = G.ease_out(G.clamp(t / 1.4))
    hpx = int(600 * k)
    col = block(110, max(hpx - 30, 2), 30, top=PAPER)
    K.drop(f, col, (CX - 90, 1180), "mb", 1, blur=14)
    G.blit(f, T(f"{104.9 * k:.0f}m", 84, GOLD, "Black"), (CX - 150, 1180 - hpx + 10), 1, "rt")
    G.blit(f, T("20번 접기", 44, DIM, "ExtraBold"), (110, 430), 1, "lt")
    G.blit(f, G.pill("아파트 35층 높이", "Black", 52, (10, 12, 20), CREAM, pad=(26, 10), radius=26), (CX + 160, 470), G.appear(t, sc["L"][-1], 0.3), "mt")


def s_thirty(f, t, sc):
    r = 900
    g = K.globe(r, light=(-0.2, -0.9))
    gy = 1180 + r - 120
    top_g = int(gy - g.height / 2)
    g = g.crop((0, 0, g.width, max(1, 1290 - top_g)))
    G.blit(f, g, (CX - g.width / 2, top_g), 1)
    d = ImageDraw.Draw(f)
    ly = 700
    for x in range(0, W, 36):
        d.line((x, ly, x + 18, ly), fill=MINT + (255,), width=4)
    G.blit(f, G.pill("우주의 경계 · 100km", "Black", 40, (10, 12, 20), MINT, pad=(18, 8), radius=20), (70, ly - 16), 1, "lb")
    k = G.ease_out(G.clamp(t / 1.6))
    top = 1150 - (1150 - 540) * k
    col = Image.new("RGBA", (40, int(1150 - top) + 1), PAPER + (255,))
    K.drop(f, col, (CX + 60, 1150), "mb", 1, blur=10)
    G.blit(f, T(f"{107.4 * k:.0f}km", 84, GOLD, "Black"), (CX + 110, top - 10), 1, "lt")
    G.blit(f, T("30번 접기", 44, DIM, "ExtraBold"), (110, 430), 1, "lt")
    K.credit(f, K.credit_of("bluemarble_east"))


def s_moon(f, t, sc):
    G.blit(f, K.globe(130, light=(-0.4, -0.5)), (CX - 220, 1110), 1, "mm")
    G.blit(f, K.globe(85, name="moon_full", light=(-0.5, -0.3)), (CX + 240, 520), 1, "mm")
    L = sc["L"]
    k = G.ease_out(G.clamp((t - 0.3) / (L[-1] + 0.4)))
    p0, p1 = (CX - 160, 1010), (CX + 330, 430)
    pe = (p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k)
    K.glow_line(f, p0, pe, PAPER, 14, 22)
    # 달 거리 표시
    d = ImageDraw.Draw(f)
    m0, m1 = (CX - 300, 980), (CX + 160, 470)
    G.blit(f, G.pill("지구~달 38만 km", "Black", 40, (10, 12, 20), BLUE, pad=(18, 8), radius=20), (110, 640), 1, "lt")
    v = 439805 * k
    G.blit(f, T(f"{v / 10000:.0f}만 km", 96, GOLD, "Black"), (CX + 40, 760), 1, "lt")
    G.blit(f, T("42번 접기", 44, DIM, "ExtraBold"), (CX + 44, 880), 1, "lt")
    G.blit(f, G.pill("달을 훌쩍 넘음!", "Black", 52, (10, 12, 20), CORAL, pad=(26, 10), radius=26), (CX + 44, 960), G.appear(t, L[-1] + 0.6, 0.3), "lt")
    K.credit(f, "사진: NASA (퍼블릭 도메인, Wikimedia Commons)")


def s_why(f, t, sc):
    x0, y0, gw, gh = 130, 1150, 820, 560
    n = int(G.clamp(t / 2.0) * 42)
    bw = gw / 42
    d = ImageDraw.Draw(f)
    for i in range(1, n + 1):
        h = gh * (2 ** i) / (2 ** 42)
        h = max(h, 2)
        c = GOLD if i == n else (255, 140, 110)
        d.rectangle((x0 + (i - 1) * bw + 2, y0 - h, x0 + i * bw - 2, y0), fill=c + (255,))
    d.line((x0, y0, x0 + gw, y0), fill=(255, 255, 255, 90), width=3)
    G.blit(f, T("2 × 2 × 2 × … (42번)", 54, CREAM, "Black"), (CX, 430), 1, "mt")
    o = G.appear(t, sc["L"][-1], 0.3)
    G.blit(f, T("= 약 4조 4천억 겹", 76, GOLD, "Black"), (CX, 510), o, "mt")
    G.blit(f, T("처음 30번은 바닥에 붙어 보이다가 마지막에 폭발", 30, DIM, "SemiBold"), (CX, 1180), 1, "mt")


def s_real(f, t, sc):
    L = sc["L"]
    G.blit(f, T("실제로는?", 60, CREAM, "Black"), (CX, 430), 1, "mt")
    # 긴 휴지 띠 — 지그재그로 접힘
    k = G.ease_out(G.clamp((t - L[-1]) / 1.4))
    folds = 12
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(folds):
        y = 640 + i * 34
        w = 760 * (1 - 0.55 * k) if True else 760
        x = CX - w / 2 + (14 if i % 2 else -14) * k
        d.rounded_rectangle((x, y, x + w, y + 26), 8, fill=(250, 248, 240, 255))
        d.rectangle((x, y + 20, x + w, y + 26), fill=(205, 203, 196, 255))
    f.alpha_composite(lay)
    G.blit(f, G.pill("손으로는 7~8번이 한계?", "Black", 48, (10, 12, 20), CREAM, pad=(24, 10), radius=24), (CX, 530), 1, "mt")
    o = G.appear(t, L[-1] + 0.5, 0.3)
    G.blit(f, T("12번 성공", 110, GOLD, "Black", stroke=6, stroke_fill=(0, 0, 0)), (CX, 1080), o, "mt")
    G.blit(f, T("2002년 · 1.2km 휴지 · 고등학생 브리트니 갈리반", 30, DIM, "SemiBold"), (CX, 1215), o, "mt")


def s_end(f, t, sc):
    k = G.ease_out(t / 0.6)
    card = K.photo("earthrise", 760, 520, (0.5, 0.15), radius=26)
    K.drop(f, card, (CX, 700 + (1 - k) * 30), "mm", k)
    G.blit(f, T("종이 한 장 × 두 배의 힘", 66, CREAM, "Black", highlight="두 배", hl_fill=GOLD), (CX, 1010), G.appear(t, 0.3, 0.4), "mt")
    K.credit(f, K.credit_of("earthrise"))


def draw_cover(f):
    G.blit(f, T("힌트: 투더문", 64, MINT, "ExtraBold"), (W / 2, 200), 1, "mt")
    G.blit(f, T("종이를 42번\n접으면?", 150, CREAM, "Black", highlight="42번", hl_fill=CORAL, align="center", line_gap=1.08,
                stroke=6, stroke_fill=(0, 0, 0)), (W / 2, 300), 1, "mt")
    G.blit(f, K.globe(260, name="moon_full", light=(-0.5, -0.3)), (W / 2, 1100), 1, "mm")
    G.blit(f, T("?", 260, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (W / 2, 1100), 1, "mm")


SCENES = [
    {"draw": s_hook, "min": 3.5, "narr": ["종이를 42번 접으면, 두께가 얼마나 될까요?"]},
    {"draw": s_double, "min": 4.0, "narr": ["종이 한 장의 두께는 약 0.1밀리미터.", "한 번 접을 때마다, 두께는 두 배가 돼요."]},
    {"draw": s_ten, "min": 3.0, "narr": ["열 번 접으면 1,024겹. | 약 10센티미터예요."]},
    {"draw": s_twenty, "min": 3.0, "narr": ["스무 번이면 약 100미터. | 아파트 35층 높이죠."]},
    {"draw": s_thirty, "min": 3.0, "narr": ["서른 번이면 약 107킬로미터. | 우주가 시작되는 높이를 넘어요."]},
    {"draw": s_moon, "min": 4.0, "narr": ["그리고 마흔두 번이면, 약 44만 킬로미터.", "지구에서 달까지 38만 킬로미터를, 훌쩍 넘어요."]},
    {"draw": s_why, "min": 3.5, "narr": ["비밀은 두 배의 반복이에요.", "2를 마흔두 번 곱하면, 4조 4천억이 넘거든요."]},
    {"draw": s_real, "min": 4.0, "narr": ["물론 실제로는 손으로 7~8번이 한계라고들 하죠.",
                                          "그런데 2002년, 미국의 한 고등학생이 1.2킬로미터짜리 휴지로, | 12번 접기에 성공했어요."]},
    {"draw": s_end, "min": 3.0, "narr": ["두 배의 힘, 정말 무섭죠?", K.CTA]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
