"""지식창고 쇼츠 #2 · 막대기 하나로 지구 크기를 잰 남자 (에라토스테네스)
  python3 science/eratosthenes.py [--stills]
숫자: 그림자 7.2° = 360°/50 · 시에네~알렉산드리아 약 5,000 스타디온 → 250,000 스타디온
      1스타디온 157.5m(이집트 단위로 보는 견해) → 39,375km · 실제 자오선 둘레 약 40,008km
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, CREAM, DIM, CORAL, BLUE, MINT, GOLD, VIOLET

OUT = K.HERE / "out" / "eratosthenes"
HEAD = {"kicker": "기원전 240년, 이집트", "title": "막대기 하나로\n지구 크기를 잰 남자", "highlight": "지구 크기"}
SAY = {"5,000 스타디온": "오천 스타디온", "25만 스타디온": "이십오만 스타디온", "7.2도": "칠 점 이 도"}


def AA(w, h, k=3):
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), k


def down(im, k):
    return im.resize((im.width // k, im.height // k), Image.LANCZOS)


def earth(r=300, glow=True, rot=0.0):
    """단순한 지구(바다 + 대륙 무늬 대신 위도선)"""
    im, d, k = AA(2 * r + 40, 2 * r + 40)
    c = (r + 20) * k
    R = r * k
    d.ellipse((c - R, c - R, c + R, c + R), fill=(36, 70, 130, 255), outline=BLUE + (255,), width=5 * k)
    for lat in (-60, -30, 0, 30, 60):
        y = c + R * math.sin(math.radians(lat))
        hw = R * math.cos(math.radians(lat))
        d.line((c - hw, y, c + hw, y), fill=(255, 255, 255, 40), width=2 * k)
    for j in range(6):
        a = math.radians(rot + j * 30)
        ex = R * abs(math.cos(a))
        d.ellipse((c - ex, c - R, c + ex, c + R), outline=(255, 255, 255, 35), width=2 * k)
    return down(im, k)


def s_hook(f, t, sc):
    e = earth(300, rot=t * 20)
    G.blit(f, e, (W / 2, 820), G.appear(t, 0.0, 0.4), "mm")
    o = G.appear(t, sc["L"][-1], 0.3)
    G.blit(f, T("?", 260, CORAL), (W / 2, 820), o, "mm")
    G.blit(f, T("둘레 = ?", 60, GOLD, "Black"), (W / 2, 1160), o, "mt")


def s_who(f, t, sc):
    im, d, k = AA(880, 300)
    d.rounded_rectangle((0, 0, 880 * k - 1, 300 * k - 1), radius=28 * k, fill=(24, 30, 54, 240), outline=MINT + (255,), width=4 * k)
    card = down(im, k)
    card.alpha_composite(T("에라토스테네스", 70, CREAM), (50, 40))
    card.alpha_composite(T("알렉산드리아 도서관장 · 수학자", 38, DIM, "SemiBold"), (52, 140))
    card.alpha_composite(T("기원전 276 ~ 194년경", 38, MINT, "ExtraBold"), (52, 200))
    G.blit(f, card, (W / 2, 720 + (1 - G.ease_out(t / 0.4)) * 30), G.appear(t, 0, 0.4), "mm")
    if True:
        o = G.appear(t, sc["L"][0] + 2.5, 0.4)
        G.blit(f, T("세상 모든 책이 모인 곳", 52, GOLD, "Black"), (W / 2, 960), o, "mt")


def s_well(f, t, sc):
    # 시에네의 우물 단면 + 수직 햇빛
    im, d, k = AA(700, 640)
    gx = 350 * k
    d.rectangle((0, 200 * k, 700 * k, 640 * k), fill=(120, 96, 64, 255))
    d.rectangle((gx - 90 * k, 200 * k, gx + 90 * k, 620 * k), fill=(30, 40, 70, 255))
    kk = G.clamp((t - 0.4) / 1.2)
    for x in range(-60, 61, 30):
        y1 = 200 + 420 * kk
        d.line((gx + x * k, 0, gx + x * k, y1 * k), fill=GOLD + (230,), width=6 * k)
    if kk >= 1:
        d.ellipse((gx - 80 * k, 590 * k, gx + 80 * k, 640 * k), fill=GOLD + (255,))
    G.blit(f, down(im, k), (W / 2 - 40, 470), 1, "mt")
    G.blit(f, T("시에네의 우물", 50, CREAM, "Black"), (110, 480), 1, "lt")
    G.blit(f, G.pill("하짓날 정오 · 그림자 0", "Black", 50, (10, 12, 20), GOLD, pad=(26, 10), radius=26), (W / 2 - 40, 1140), G.appear(t, sc["L"][-1], 0.3), "mt")


def stick(f, t, angle_deg, cx, base, h=420, label=True):
    im, d, k = AA(900, 640)
    ox, oy = 450 * k, 560 * k
    d.line((0, oy, 900 * k, oy), fill=(200, 190, 160, 255), width=6 * k)
    d.line((ox, oy, ox, oy - h * k), fill=CREAM + (255,), width=12 * k)
    kk = G.clamp((t - 0.3) / 1.0)
    a = math.radians(angle_deg * 3)  # 보기 쉽게 3배
    L = 700 * k
    tip = (ox, oy - h * k)
    end = (ox - h * k * math.tan(a), oy)          # 그림자 끝
    for dx in (-200, 0, 200):
        x1, y1 = end[0] + dx * k, end[1]
        x0, y0 = x1 + L * math.sin(a), y1 - L * math.cos(a)
        d.line((x0, y0, x0 + (x1 - x0) * kk, y0 + (y1 - y0) * kk), fill=GOLD + (210,), width=5 * k)
    d.line((ox, oy, ox + (end[0] - ox) * kk, oy), fill=(10, 10, 16, 255), width=16 * k)
    if kk >= 1 and label:
        r = 130 * k
        d.arc((tip[0] - r, tip[1] - r, tip[0] + r, tip[1] + r), start=90 - angle_deg * 3, end=90, fill=CORAL + (255,), width=6 * k)
    G.blit(f, down(im, k), (cx, base), 1, "mt")
    G.blit(f, T("※ 각도는 보기 쉽게 확대", 26, DIM, "SemiBold"), (110, 1240), 1, "lb")


def s_stick(f, t, sc):
    stick(f, t, 7.2, W / 2 - 40, 460)
    G.blit(f, T("알렉산드리아의 막대기", 50, CREAM, "Black"), (110, 470), 1, "lt")
    o = G.appear(t, sc["L"][-1], 0.3)
    G.blit(f, G.pill("햇빛 기울기 7.2°", "Black", 60, (10, 12, 20), CORAL, pad=(30, 12), radius=30), (W / 2 - 40, 1100), o, "mt")


def s_center(f, t, sc):
    r, cx, cy = 330, 470, 860
    k = 3
    im = Image.new("RGBA", (W * k, 1300 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    C = (cx * k, cy * k)
    R = r * k
    d.ellipse((C[0] - R, C[1] - R, C[0] + R, C[1] + R), fill=(36, 70, 130, 255), outline=BLUE + (255,), width=5 * k)
    A, B = math.radians(-90), math.radians(-90 - 7.2 * 3)
    pa = (C[0] + R * math.cos(A), C[1] + R * math.sin(A))
    pb = (C[0] + R * math.cos(B), C[1] + R * math.sin(B))
    kk = G.ease_out(t / 0.8)
    for x in range(-4, 5):
        xx = C[0] + x * 80 * k
        d.line((xx, 430 * k, xx, (cy - r - 10) * k if abs(x) < 3 else (cy - 240) * k), fill=GOLD + (int(150 * kk),), width=3 * k)
    o2 = G.clamp((t - sc["L"][-1]) / 0.6)
    d.line((C[0], C[1], pa[0], pa[1]), fill=CREAM + (255,), width=5 * k)
    d.line((C[0], C[1], pb[0], pb[1]), fill=CORAL + (255,), width=5 * k)
    if o2 > 0:
        rr = 110 * k
        d.arc((C[0] - rr, C[1] - rr, C[0] + rr, C[1] + rr), start=math.degrees(B), end=-90, fill=GOLD + (int(255 * o2),), width=8 * k)
    for p, col in ((pa, MINT), (pb, CORAL)):
        d.ellipse((p[0] - 15 * k, p[1] - 15 * k, p[0] + 15 * k, p[1] + 15 * k), fill=col + (255,))
    f.alpha_composite(im.resize((W, 1300), Image.LANCZOS))
    G.blit(f, T("시에네", 40, MINT, "ExtraBold"), (cx + 24, cy - r - 54), 1, "lt")
    G.blit(f, T("알렉산드리아", 40, CORAL, "ExtraBold"), (cx + r * math.cos(B) - 14, cy + r * math.sin(B) - 24), 1, "rb")
    if o2 > 0:
        G.blit(f, G.pill("중심각도 7.2°", "Black", 50, (10, 12, 20), GOLD, pad=(24, 10), radius=26), (cx, cy + 60), o2, "mt")
    G.blit(f, T("※ 각도는 보기 쉽게 확대", 26, DIM, "SemiBold"), (110, 1240), 1, "lb")


def s_pie(f, t, sc):
    im, d, k = AA(560, 560)
    R = 270 * k
    c = 280 * k
    d.ellipse((c - R, c - R, c + R, c + R), fill=(40, 50, 80, 255), outline=(120, 130, 160, 255), width=3 * k)
    n = int(G.clamp(t / 1.6) * 50)
    for i in range(n):
        a0, a1 = -90 + i * 7.2, -90 + (i + 1) * 7.2
        d.pieslice((c - R, c - R, c + R, c + R), a0, a1, fill=(CORAL if i == 0 else BLUE) + (255 if i == 0 else 120,), outline=(14, 18, 34, 255), width=2 * k)
    G.blit(f, down(im, k), (W / 2 - 40, 450))
    G.blit(f, T(f"7.2° × {max(n, 1)}", 72, GOLD, "Black"), (W / 2 - 40, 1050), 1, "mt")
    o = G.appear(t, sc["L"][-1], 0.3)
    G.blit(f, T("= 360° · 한 바퀴의 50분의 1", 46, CREAM, "ExtraBold"), (W / 2 - 40, 1150), o, "mt")


def s_calc(f, t, sc):
    rows = [("두 도시 거리", "5,000 스타디온", CREAM, 0), ("", "", GOLD, 1), ("지구 둘레", "250,000 스타디온", CORAL, 1)]
    y = 520
    for i, (a, b, col, on) in enumerate(rows):
        o = G.appear(t, sc["L"][min(on, len(sc["L"]) - 1)] + i * 0.25, 0.3)
        if a:
            G.blit(f, T(a, 52, DIM, "ExtraBold"), (120, y), o)
        if b:
            G.blit(f, T(b, 76, col, "Black"), (120, y + 70), o)
            y += 220
        else:
            G.blit(f, T("× 50", 110, GOLD, "Black"), (W / 2 - 40, y - 10), o, "mt")
            y += 170
    d = ImageDraw.Draw(f)
    if t > sc["L"][-1]:
        d.line((120, y - 40, W - 200, y - 40), fill=(255, 255, 255, 60), width=3)


def s_result(f, t, sc):
    bars = [("에라토스테네스 (기원전 240년경)", 39375, CORAL), ("실제 지구 둘레 (극 통과)", 40008, BLUE)]
    y = 540
    for i, (lab, v, col) in enumerate(bars):
        k = G.ease_out((t - 0.3 - i * 0.6) / 0.8)
        G.blit(f, T(lab, 40, CREAM, "ExtraBold"), (110, y), 1)
        bw = int(760 * v / 40008 * max(k, 0))
        if bw > 0:
            G.blit(f, Image.new("RGBA", (bw, 54), col + (255,)), (110, y + 64))
        G.blit(f, T(f"{int(v * max(k, 0)):,} km", 60, col, "Black"), (110, y + 130), min(1, max(k, 0) * 2))
        y += 260
    o = G.appear(t, sc["L"][-1], 0.3)
    G.blit(f, G.pill("오차 약 2%", "Black", 60, (10, 12, 20), MINT, pad=(30, 12), radius=30), (W / 2 - 40, 1100), o, "mt")
    G.blit(f, T("1스타디온 = 157.5m로 보는 견해 기준 · 단위 해석에 따라 오차는 커질 수 있음", 22, DIM, "SemiBold", max_w=860), (110, 1250), 1, "lb")


def s_end(f, t, sc):
    k = G.ease_out(t / 0.6)
    G.blit(f, T("막대기 하나\n그림자 하나\n그리고 생각 하나", 78, CREAM, "Black", highlight="생각 하나", hl_fill=CORAL, align="center", line_gap=1.2),
           (W / 2 - 30, 560 + (1 - k) * 30), k, "mt")


def draw_cover(f):
    G.blit(f, T("2,200년 전", 60, MINT, "ExtraBold"), (W / 2, 200), 1, "mt")
    G.blit(f, T("막대기 하나로\n지구 크기를\n쟀다고?", 130, CREAM, "Black", highlight="쟀다고?", hl_fill=CORAL, align="center", line_gap=1.08,
                stroke=6, stroke_fill=(0, 0, 0)), (W / 2, 290), 1, "mt")
    G.blit(f, earth(260), (W / 2, 1060), 1, "mm")
    G.blit(f, T("?", 260, GOLD, "Black", stroke=8, stroke_fill=(0, 0, 0)), (W / 2, 1060), 1, "mm")


SCENES = [
    {"draw": s_hook, "min": 3.5, "narr": ["2,200년 전, 막대기 하나로 지구 둘레를 잰 사람이 있습니다. | 어떻게 했을까요?"]},
    {"draw": s_who, "min": 3.0, "narr": ["주인공은 에라토스테네스. 고대 이집트 알렉산드리아 도서관의 관장이었죠."]},
    {"draw": s_well, "min": 3.5, "narr": ["어느 날 그는 남쪽 도시 시에네의 소문을 들어요.", "하짓날 정오가 되면, 햇빛이 우물 바닥까지 곧장 비친다는 거죠. 그림자가 하나도 없이요."]},
    {"draw": s_stick, "min": 3.5, "narr": ["그래서 같은 날 같은 시각, 알렉산드리아에 막대기를 세워 봤어요.", "그런데 여기선 그림자가 생겼죠. 햇빛이 7.2도 기울어져 있었던 거예요."]},
    {"draw": s_center, "min": 3.5, "narr": ["햇빛은 평행하게 들어오니까, | 이 7.2도가, 지구 중심에서 두 도시가 벌어진 각도와 똑같은 거죠."]},
    {"draw": s_pie, "min": 3.0, "narr": ["7.2도는 한 바퀴 360도의 딱 50분의 1."]},
    {"draw": s_calc, "min": 3.5, "narr": ["두 도시 사이 거리는 약 5,000 스타디온.", "여기에 50을 곱하면, 지구 둘레는 25만 스타디온이에요."]},
    {"draw": s_result, "min": 3.5, "narr": ["지금 단위로 바꾸면 약 3만 9천 킬로미터.", "실제 지구 둘레 4만 킬로미터와, 오차가 2% 정도밖에 안 나요."]},
    {"draw": s_end, "min": 3.0, "narr": ["필요한 건 막대기 하나, 그림자 하나, 그리고 생각 하나였던 거죠.", K.CTA]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
