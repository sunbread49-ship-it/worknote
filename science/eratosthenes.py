"""지식창고 쇼츠 #2 · 막대기 하나로 지구 크기를 잰 남자 (에라토스테네스)
  python3 science/eratosthenes.py [--stills]
숫자: 그림자 7.2° = 360°/50 · 시에네~알렉산드리아 약 5,000 스타디온 → 250,000 스타디온
      1스타디온 157.5m(이집트 단위로 보는 견해, 축구장 105m의 1.5배) → 39,375km · 실제 자오선 둘레 약 40,008km
사진: 위키미디어 공용(퍼블릭 도메인 · CC BY · CC BY-SA) — 화면 왼쪽 아래 출처 자동 표기
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, CREAM, DIM, CORAL, BLUE, MINT, GOLD

OUT = K.HERE / "out" / "eratosthenes"
HEAD = {"kicker": "기원전 240년, 이집트", "title": "막대기 하나로\n지구 크기를 잰 남자", "highlight": "지구 크기"}
SAY = {"5,000 스타디온": "오천 스타디온", "25만 스타디온": "이십오만 스타디온", "157.5미터": "백오십칠 점 오 미터"}
CX = W / 2 - 30  # 오른쪽 버튼 피해서 살짝 왼쪽


def s_hook(f, t, sc):
    k = G.ease_out(t / 0.8)
    g = K.globe(300)
    s = 0.92 + 0.08 * k + t * 0.004
    g2 = g.resize((int(g.width * s), int(g.height * s)), Image.LANCZOS)
    G.blit(f, g2, (CX, 820), k, "mm")
    o = G.appear(t, sc["L"][0] + 2.6, 0.3)
    G.blit(f, T("?", 300, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (CX, 820), o, "mm")
    G.blit(f, G.pill("둘레 = ?", "Black", 56, (10, 12, 20), GOLD, pad=(28, 12), radius=30), (CX, 1150), o, "mt")
    K.credit(f, K.credit_of("bluemarble_east"))


def s_who(f, t, sc):
    K.band(f, "alex_library", 380, 880, dark=0.72, sat=0.6, blur=3)
    k = G.ease_out(t / 0.5)
    card = K.photo("erato_strozzi", 760, 520, (0.62, 0.3), radius=26)
    K.drop(f, card, (CX, 690 + (1 - k) * 30), "mm", k)
    o = G.appear(t, 0.5, 0.35)
    tag = Image.new("RGBA", (760, 170), (0, 0, 0, 0))
    ImageDraw.Draw(tag).rounded_rectangle((0, 0, 759, 169), radius=22, fill=(12, 16, 30, 235), outline=MINT + (255,), width=3)
    tag.alpha_composite(T("에라토스테네스", 62, CREAM), (34, 22))
    tag.alpha_composite(T("알렉산드리아 도서관장 · 기원전 276~194년경", 32, MINT, "ExtraBold"), (36, 106))
    K.drop(f, tag, (CX, 1040), "mm", o, blur=16)
    K.credit(f, K.credit_of("erato_strozzi", "alex_library"))


def cylinder_well(w, h, light):
    """위에서 비스듬히 본 우물(원통) — 벽 그라데이션 + 바닥 빛"""
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rx, ry = w * k * 0.42, w * k * 0.12
    cx, top, bot = w * k / 2, ry + 10, h * k - ry - 10
    for i in range(int(2 * rx)):
        x = cx - rx + i
        u = (i / (2 * rx)) * 2 - 1
        sh = int(60 + 90 * (1 - abs(u + 0.3)))
        d.line((x, top, x, bot), fill=(sh + 40, sh + 20, max(0, sh - 10), 255))
    d.ellipse((cx - rx, bot - ry, cx + rx, bot + ry), fill=(70 + int(170 * light), 60 + int(150 * light), 40 + int(60 * light), 255))
    d.ellipse((cx - rx, top - ry, cx + rx, top + ry), fill=(20, 24, 40, 255))
    d.ellipse((cx - rx, top - ry, cx + rx, top + ry), outline=(210, 180, 130, 255), width=10 * k)
    return im.resize((w, h), Image.LANCZOS)


def s_well(f, t, sc):
    K.band(f, "aswan_nile", 380, 880, focus=(0.5, 0.45), dark=0.55, sat=0.85)
    kk = G.clamp((t - 0.4) / 1.2)
    K.drop(f, cylinder_well(420, 520, kk), (CX, 800), "mm")
    beam = Image.new("RGBA", f.size, (0, 0, 0, 0))
    y1 = 420 + (1000 - 420) * kk
    ImageDraw.Draw(beam).rectangle((CX - 120, 380, CX + 120, y1), fill=(255, 220, 120, 70))
    f.alpha_composite(beam.filter(ImageFilter.GaussianBlur(26)))
    for dx in (-80, -27, 27, 80):
        K.glow_line(f, (CX + dx, 400), (CX + dx, y1), GOLD, 4, 14)
    G.blit(f, G.pill("시에네 (지금의 아스완)", "Black", 44, (10, 12, 20), CREAM, pad=(22, 10), radius=24), (90, 420), 1, "lt")
    G.blit(f, G.pill("하짓날 정오 · 그림자 0", "Black", 50, (10, 12, 20), GOLD, pad=(26, 10), radius=26), (CX, 1140),
           G.appear(t, sc["L"][-1], 0.3), "mt")
    K.credit(f, K.credit_of("aswan_nile"))


def s_stick(f, t, sc):
    K.band(f, "alexandria_dusk", 380, 880, focus=(0.5, 0.55), dark=0.5, sat=0.9)
    kk = G.clamp((t - 0.3) / 1.0)
    k = 2
    lay = Image.new("RGBA", (W * k, 1300 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    gy = 1010
    for i in range(0, 220):
        c = int(70 + i * 0.35)
        d.line(((120 - i * 0.6) * k, (gy + i) * k, (W - 160 + i * 0.6) * k, (gy + i) * k), fill=(c + 40, c + 25, c, 230))
    f.alpha_composite(lay.resize((W, 1300), Image.LANCZOS))
    sx, top = CX + 120, 560
    a = math.radians(7.2 * 3)
    shl = (gy - top) * math.tan(a) * kk
    sh = Image.new("RGBA", f.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(sx - 8, gy + 4), (sx + 8, gy + 4), (sx - shl + 2, gy + 14), (sx - shl - 10, gy + 10)], fill=(0, 0, 0, 200))
    f.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    for i in range(-14, 15):
        c = int(235 - abs(i + 4) * 7)
        ImageDraw.Draw(f).line((sx + i, top, sx + i, gy + 4), fill=(c + 30, c + 15, c - 20, 255))
    sun = (sx + (gy - top) * math.tan(a) + 160, top - 90)
    glow = Image.new("RGBA", f.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((sun[0] - 70, sun[1] - 70, sun[0] + 70, sun[1] + 70), fill=(255, 210, 110, 220))
    f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(24)))
    for dx in (-90, 0, 90):
        p1 = (sx - shl + dx, gy)
        p0 = (p1[0] + 520 * math.sin(a), p1[1] - 520 * math.cos(a))
        K.glow_line(f, p0, (p0[0] + (p1[0] - p0[0]) * kk, p0[1] + (p1[1] - p0[1]) * kk), GOLD, 4, 12)
    G.blit(f, G.pill("알렉산드리아", "Black", 44, (10, 12, 20), CREAM, pad=(22, 10), radius=24), (90, 420), 1, "lt")
    G.blit(f, G.pill("햇빛 기울기 7.2°", "Black", 58, (10, 12, 20), CORAL, pad=(30, 12), radius=30), (CX, 1120),
           G.appear(t, sc["L"][-1], 0.3), "mt")
    G.blit(f, T("※ 각도는 보기 쉽게 확대", 24, DIM, "SemiBold"), (W - 160, 1228), 1, "rb")
    K.credit(f, K.credit_of("alexandria_dusk"))


def s_center(f, t, sc):
    r, cx, cy = 320, CX, 860
    G.blit(f, K.globe(r, light=(-0.2, -0.75)), (cx, cy), 1, "mm")
    B = math.radians(-90 - 7.2 * 3)
    pa = (cx, cy - r)
    pb = (cx + r * math.cos(B), cy + r * math.sin(B))
    kk = G.ease_out(t / 0.8)
    for x in range(-4, 5):
        dx = x * 78
        y_end = cy - math.sqrt(r * r - dx * dx) if abs(dx) < r else 1000
        K.glow_line(f, (cx + dx, 400), (cx + dx, 400 + (y_end - 400) * kk), GOLD, 3, 10)
    o2 = G.clamp((t - sc["L"][0] - 1.6) / 0.6)
    K.glow_line(f, (cx, cy), pa, CREAM, 5, 10)
    K.glow_line(f, (cx, cy), pb, CORAL, 5, 10)
    d = ImageDraw.Draw(f)
    if o2 > 0:
        rr = 110
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), start=math.degrees(B), end=-90, fill=GOLD + (int(255 * o2),), width=8)
    for p, col in ((pa, MINT), (pb, CORAL)):
        d.ellipse((p[0] - 15, p[1] - 15, p[0] + 15, p[1] + 15), fill=col + (255,), outline=(255, 255, 255, 255), width=3)
    G.blit(f, G.pill("시에네", "Black", 36, (10, 12, 20), MINT, pad=(16, 6), radius=18), (pa[0] + 26, pa[1] - 56), 1, "lt")
    G.blit(f, G.pill("알렉산드리아", "Black", 36, (10, 12, 20), CORAL, pad=(16, 6), radius=18), (pb[0] - 20, pb[1] - 30), 1, "rb")
    if o2 > 0:
        G.blit(f, G.pill("중심각 7.2°", "Black", 52, (10, 12, 20), GOLD, pad=(26, 10), radius=26), (cx, cy + 70), o2, "mt")
    G.blit(f, T("※ 각도는 보기 쉽게 확대", 24, DIM, "SemiBold"), (W - 160, 1228), 1, "rb")
    K.credit(f, K.credit_of("bluemarble_east"))


def s_pie(f, t, sc):
    k = 3
    R = 260
    im = Image.new("RGBA", (2 * R * k, 2 * R * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = int(G.clamp(t / 1.6) * 50)
    for i in range(50):
        a0, a1 = -90 + i * 7.2, -90 + (i + 1) * 7.2
        if i == 0:
            col = CORAL + (255,)
        elif i < n:
            sh = int(120 + 80 * math.cos(math.radians(a0 + 135)))
            col = (40, 90 + sh // 3, 150 + sh // 3, 255)
        else:
            col = (36, 42, 66, 255)
        d.pieslice((0, 0, 2 * R * k, 2 * R * k), a0, a1, fill=col, outline=(14, 18, 34, 255), width=2 * k)
    disk = im.resize((2 * R, 2 * R), Image.LANCZOS)
    hl = Image.new("RGBA", disk.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((40, 30, 2 * R - 140, 2 * R - 160), fill=(255, 255, 255, 40))
    disk.alpha_composite(hl.filter(ImageFilter.GaussianBlur(40)))
    K.drop(f, disk, (CX, 740), "mm")
    G.blit(f, T(f"7.2° × {max(n, 1)}", 76, GOLD, "Black"), (CX, 1040), 1, "mt")
    G.blit(f, T("= 360° · 한 바퀴의 50분의 1", 46, CREAM, "ExtraBold"), (CX, 1140), G.appear(t, 1.7, 0.3), "mt")


def field(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(10):
        c = (52, 140, 70) if i % 2 else (60, 156, 80)
        d.rectangle((i * w / 10, 0, (i + 1) * w / 10, h), fill=c + (255,))
    d.rectangle((6, 6, w - 6, h - 6), outline=(240, 240, 240, 255), width=4)
    d.line((w / 2, 6, w / 2, h - 6), fill=(240, 240, 240, 255), width=4)
    d.ellipse((w / 2 - h * 0.16, h / 2 - h * 0.16, w / 2 + h * 0.16, h / 2 + h * 0.16), outline=(240, 240, 240, 255), width=4)
    return im


def s_stadion(f, t, sc):
    G.blit(f, T("1스타디온 =", 60, CREAM, "Black"), (110, 430), G.appear(t, 0.0, 0.3))
    G.blit(f, T("약 157.5m", 110, GOLD, "Black"), (110, 510), G.appear(t, 0.1, 0.3))
    fw, fh = 520, 280
    k1 = G.ease_out((t - sc["L"][-1]) / 0.5)
    K.drop(f, field(fw, fh), (110, 720), "lt", 1, blur=14)
    if k1 > 0:
        K.drop(f, field(fw // 2, fh), (110 + fw + 14, 720), "lt", k1, blur=14)
    ImageDraw.Draw(f).line((110, 1030, 110 + (fw + 14 + fw // 2 * max(k1, 0)), 1030), fill=GOLD + (255,), width=6)
    G.blit(f, T("축구장 약 1.5개 길이", 52, CREAM, "Black", highlight="1.5개", hl_fill=GOLD), (110, 1060), max(k1, 0), "lt")
    G.blit(f, T("※ 스타디온 길이는 학자마다 해석이 다름", 24, DIM, "SemiBold"), (110, 1262), 1, "lb")


def s_calc(f, t, sc):
    y = 470
    o = G.appear(t, 0.0, 0.3)
    G.blit(f, T("두 도시 사이 거리", 50, DIM, "ExtraBold"), (110, y), o)
    G.blit(f, T("5,000 스타디온", 84, CREAM, "Black"), (110, y + 64), o)
    G.blit(f, T("× 50", 120, GOLD, "Black"), (CX, y + 230), G.appear(t, sc["L"][-1] - 0.2, 0.3), "mt")
    o3 = G.appear(t, sc["L"][-1] + 0.6, 0.35)
    G.blit(f, T("지구 둘레", 50, DIM, "ExtraBold"), (110, y + 420), o3)
    G.blit(f, T("250,000 스타디온", 84, CORAL, "Black"), (110, y + 484), o3)


def s_result(f, t, sc):
    bars = [("에라토스테네스 (기원전 240년경)", 39375, CORAL), ("실제 지구 둘레 (극 통과)", 40008, BLUE)]
    y = 480
    for i, (lab, v, col) in enumerate(bars):
        k = max(0.0, G.ease_out((t - 0.3 - i * 0.6) / 0.8))
        G.blit(f, T(lab, 40, CREAM, "ExtraBold"), (110, y), 1)
        bw = int(760 * v / 40008 * k)
        if bw > 4:
            bar = Image.new("RGBA", (bw, 62), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bar)
            for yy in range(62):
                c = tuple(min(255, int(cc * (1.15 - yy / 62 * 0.45))) for cc in col)
                bd.line((0, yy, bw, yy), fill=c + (255,))
            K.drop(f, bar, (110, y + 62), "lt", 1, blur=10, alpha=0.5)
        G.blit(f, T(f"{int(v * k):,} km", 64, col, "Black"), (110, y + 140), min(1, k * 2))
        y += 270
    G.blit(f, G.pill("오차 약 2%", "Black", 62, (10, 12, 20), MINT, pad=(30, 12), radius=30), (CX, 1080),
           G.appear(t, sc["L"][-1] + 1.2, 0.3), "mt")
    G.blit(f, T("1스타디온 157.5m 기준", 24, DIM, "SemiBold"), (110, 1262), 1, "lb")


def s_end(f, t, sc):
    k = G.ease_out(t / 0.6)
    G.blit(f, K.globe(200, light=(-0.6, -0.4)), (CX, 600), k, "mm")
    G.blit(f, T("막대기 하나\n그림자 하나\n그리고 생각 하나", 74, CREAM, "Black", highlight="생각 하나", hl_fill=CORAL, align="center", line_gap=1.18),
           (CX, 860 + (1 - k) * 30), k, "mt")
    K.credit(f, K.credit_of("bluemarble_east"))


def draw_cover(f):
    G.blit(f, T("2,200년 전", 60, MINT, "ExtraBold"), (W / 2, 190), 1, "mt")
    G.blit(f, T("막대기 하나로\n지구 크기를\n쟀다고?", 130, CREAM, "Black", highlight="쟀다고?", hl_fill=CORAL, align="center", line_gap=1.08,
                stroke=6, stroke_fill=(0, 0, 0)), (W / 2, 280), 1, "mt")
    G.blit(f, K.globe(300), (W / 2, 1080), 1, "mm")
    G.blit(f, T("?", 280, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (W / 2, 1080), 1, "mm")


SCENES = [
    {"draw": s_hook, "min": 3.5, "narr": ["2,200년 전, 막대기 하나로 지구 둘레를 잰 사람이 있습니다. | 어떻게 했을까요?"]},
    {"draw": s_who, "min": 3.0, "narr": ["주인공은 에라토스테네스. 고대 이집트 알렉산드리아 도서관의 관장이었죠."]},
    {"draw": s_well, "min": 3.5, "narr": ["어느 날 그는 남쪽 도시 시에네의 소문을 들어요.", "하짓날 정오가 되면, 햇빛이 우물 바닥까지 곧장 비친다는 거죠. 그림자가 하나도 없이요."]},
    {"draw": s_stick, "min": 3.5, "narr": ["그래서 같은 날 같은 시각, 알렉산드리아에 막대기를 세워 봤어요.", "그런데 여기선 그림자가 생겼죠. 햇빛이 7.2도 기울어져 있었던 거예요."]},
    {"draw": s_center, "min": 3.5, "narr": ["햇빛은 평행하게 들어오니까, | 이 7.2도가 지구 중심에서 두 도시가 벌어진 각도와 똑같은 거죠."]},
    {"draw": s_pie, "min": 3.0, "narr": ["7.2도는 한 바퀴 360도의 딱 50분의 1."]},
    {"draw": s_calc, "min": 3.5, "narr": ["두 도시 사이 거리는 약 5,000 스타디온.", "여기에 50을 곱하면, 지구 둘레는 25만 스타디온이에요."]},
    {"draw": s_stadion, "min": 3.0, "narr": ["스타디온은 고대 그리스의 거리 단위인데, 1스타디온은 약 157.5미터.", "축구장 한 개 반 정도 길이예요."]},
    {"draw": s_result, "min": 3.5, "narr": ["미터로 바꾸면, 약 3만 9천 킬로미터.", "실제 지구 둘레는 4만 킬로미터. | 오차가 겨우 2% 정도예요."]},
    {"draw": s_end, "min": 3.0, "narr": ["필요한 건 막대기 하나, 그림자 하나, 그리고 생각 하나였던 거죠.", K.CTA]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
