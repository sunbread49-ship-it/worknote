"""지식창고 쇼츠 #7 · 우주보다 7배 외로운 곳이 지구에 있다? (포인트 니모 · 바다의 도달불능극)
  python3 science/nemo.py [--stills]
숫자 (구면 거리, 지구 반지름 6,371km — 직접 계산):
  포인트 니모 48.88°S 123.39°W → 듀시섬 2,695km · 모투누이(이스터섬 옆) 2,692km · 남극 마헤르섬 2,683km → '약 2,700km'
  국제우주정거장(ISS) 고도 약 400km → 2,700 / 400 ≈ 6.7 → '약 7배'
  우주선 무덤: 러시아 미르 우주정거장(2001년) · 살류트 등이 이 바다에 떨어짐 / ISS도 2030년쯤 이곳으로 내려올 계획(NASA)
쇼츠 기조(사용자): 전환은 빠르고 많게 · 장면당 2~3초
"""
import math
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, H, CREAM, DIM, CORAL, GOLD, MINT
import flight as FL

FL.SEA, FL.LAND, FL.LAND_EDGE = (12, 30, 64), (78, 108, 150), (170, 205, 240)  # 이 편은 지구본을 더 밝고 선명하게

OUT = K.HERE / "out" / "nemo"
HEAD = {"kicker": "지구의 수학", "title": "우주보다\n외로운 곳?", "highlight": "외로운"}
SAY = {"2,700킬로미터": "이천칠백 킬로미터", "400킬로미터": "사백 킬로미터", "7배": "일곱 배", "2030년": "이천삼십 년",
       "2001년": "이천일 년", "포인트 니모": "포인트 니모"}
CX = W / 2
NEMO = (-48.88, -123.39)
ISLES = [((-24.67, -124.78), "듀시섬"), ((-27.2, -109.45), "이스터섬 옆"), ((-72.97, -126.4), "남극")]
SKY = (120, 200, 255)


@lru_cache(maxsize=8)
def gl(r, lat, lon):
    return FL.globe_img(r, lat, lon)


def project(lat, lon, cx, cy, r, c_lat, c_lon):
    x, y, c = FL.ortho(lat, lon, c_lat, c_lon)
    return (cx + x * r, cy - y * r), c > 0


def ring_pts(center, dist_km, n=180):
    la1, lo1 = map(math.radians, center)
    d = dist_km / 6371
    out = []
    for i in range(n + 1):
        b = 2 * math.pi * i / n
        la = math.asin(math.sin(la1) * math.cos(d) + math.cos(la1) * math.sin(d) * math.cos(b))
        lo = lo1 + math.atan2(math.sin(b) * math.sin(d) * math.cos(la1), math.cos(d) - math.sin(la1) * math.sin(la))
        out.append((math.degrees(la), math.degrees(lo)))
    return out


def globe(f, cx, cy, r, c_lat, c_lon, zoom=1.0):
    g = gl(r, c_lat, c_lon)
    if zoom != 1.0:
        g = g.resize((int(g.width * zoom), int(g.height * zoom)), Image.BILINEAR)
    R = g.width / 2
    rim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rim).ellipse((cx - R - 6, cy - R - 6, cx + R + 6, cy + R + 6), outline=(120, 190, 255, 200), width=10)
    f.alpha_composite(rim.filter(ImageFilter.GaussianBlur(22)))   # 대기권처럼 은은한 푸른 테
    K.drop(f, g, (cx, cy), "mm", 1, blur=40, alpha=0.6)
    return r * zoom


def glow_pin(f, xy, t, col=GOLD, label=None, size=16):
    x, y = xy
    pulse = (t * 1.2) % 1.0
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rr = size + 70 * pulse
    d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col + (int(220 * (1 - pulse)),), width=5)
    d.ellipse((x - size, y - size, x + size, y + size), fill=col + (255,))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))
    f.alpha_composite(ov)
    if label:
        G.blit(f, T(label, 54, CREAM, "Black", stroke=6, stroke_fill=(6, 8, 14)), (x, y + size + 20), 1, "mt")


def pill_tag(f, text, t, y=420, col=GOLD):
    k = G.ease_out(G.clamp(t / 0.25))
    p = G.pill(text, "Black", 50, (12, 10, 6), col, pad=(28, 10))
    K.drop(f, p, (CX, y - (1 - k) * 20), "mt", k, blur=12)


def big(f, text, y, size=120, hl="", col=CREAM, o=1.0):
    im = T(text, size, col, "Black", highlight=hl, hl_fill=GOLD, align="center", line_gap=1.08, stroke=9, stroke_fill=(6, 8, 14))
    if im.width > W - 60:
        im = im.resize((W - 60, int(im.height * (W - 60) / im.width)), Image.LANCZOS)
    K.drop(f, im, (CX, y), "mm", o, blur=26, alpha=0.8)


# ── 장면 ─────────────────────────────────────────────────────────
C_LAT, C_LON = -40.0, -125.0


def s_hook(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    z = 1.0 + 0.08 * G.clamp(t / 2.5)
    r = globe(f, CX, 600, 430, C_LAT, C_LON, z)
    p, vis = project(*NEMO, CX, 600, r, C_LAT, C_LON)
    glow_pin(f, p, t, CORAL)
    big(f, "우주보다 7배\n외로운 곳이\n지구에 있다?", 1110, 118, hl="7배")


def s_where(f, t, sc):
    k = G.ease_out(G.clamp(t / 0.6))
    r = globe(f, CX, 830, 440, C_LAT, C_LON, 1.0 + 0.25 * k)
    p, _ = project(*NEMO, CX, 830, r, C_LAT, C_LON)
    glow_pin(f, p, t, CORAL, "포인트 니모" if t > 0.5 else None)
    pill_tag(f, "남태평양 한가운데", t)


def s_ring(f, t, sc):
    L = sc["L"]
    r = globe(f, CX, 830, 440, C_LAT, C_LON, 1.25)
    k = G.ease_out(G.clamp((t - 0.2) / 1.3))
    pts = []
    for la, lo in ring_pts(NEMO, 2700 * max(k, 0.02)):
        q, vis = project(la, lo, CX, 830, r, C_LAT, C_LON)
        if vis:
            pts.append(q)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if len(pts) > 2:
        ImageDraw.Draw(ov).line(pts, fill=MINT + (255,), width=7, joint="curve")
        ImageDraw.Draw(ov).polygon(pts, fill=MINT + (40,))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(8)))
    f.alpha_composite(ov)
    p, _ = project(*NEMO, CX, 830, r, C_LAT, C_LON)
    glow_pin(f, p, t, CORAL)
    if k >= 0.98:
        for (ll, name) in ISLES:
            q, vis = project(*ll, CX, 830, r, C_LAT, C_LON)
            if vis:
                ImageDraw.Draw(f).ellipse((q[0] - 12, q[1] - 12, q[0] + 12, q[1] + 12), fill=(255, 255, 255, 255))
    pill_tag(f, "외로움 ① 가장 가까운 섬까지", t)
    big(f, f"{int(2700 * k):,}km", 1180, 120, col=MINT)


def s_iss(f, t, sc):
    """옆으로 2,700km vs 위로 400km — 같은 비율의 굵은 막대 두 개 + '7배'"""
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    pill_tag(f, "외로움 ② 머리 위 우주정거장", t)
    x0, full = 90, W - 180
    k1 = G.ease_out(G.clamp((t - 0.1) / 0.8))
    k2 = G.ease_out(G.clamp((t - sc["L"][-1]) / 0.5))
    for i, (lab, km, col, k) in enumerate((("가장 가까운 육지", 2700, MINT, k1), ("우주정거장", 400, GOLD, k2))):
        y = 620 + i * 230
        G.blit(f, T(lab, 52, col, "Black"), (x0, y), min(1, k * 3), "lt")
        bw = int(full * km / 2700 * k)
        if bw > 4:
            bar = Image.new("RGBA", (bw, 70), col + (255,))
            mk = Image.new("L", bar.size, 0)
            ImageDraw.Draw(mk).rounded_rectangle((0, 0, bw - 1, 69), 35, fill=255)
            bar.putalpha(mk)
            f.alpha_composite(bar.filter(ImageFilter.GaussianBlur(14)), (x0, y + 80))
            f.alpha_composite(bar, (x0, y + 80))
            G.blit(f, T(f"{int(km * k):,}km", 56, CREAM, "Black", stroke=5, stroke_fill=(6, 8, 14)), (x0 + bw + 16 if km < 1000 else x0 + bw - 16, y + 115), 1, "lm" if km < 1000 else "rm")
    if k2 >= 1:
        o = G.appear(t, sc["L"][-1] + 0.6, 0.25)
        big(f, "약 7배 더 멀다", 1160, 96, hl="7배", o=o)


def s_astro(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    r = globe(f, CX, 1080, 520, C_LAT, C_LON, 1.0)
    # 우주정거장 궤도(경사 51.6°) 한 줄 + 지나가는 점
    pts = []
    for i in range(0, 361, 3):
        lon = -200 + i
        lat = 51.6 * math.sin(math.radians(i * 1.0 + 20))
        q, vis = project(lat, lon, CX, 1080, r * 1.08, C_LAT, C_LON)
        pts.append(q if vis else None)
    seg = [p for p in pts if p]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if len(seg) > 2:
        ImageDraw.Draw(ov).line(seg, fill=GOLD + (200,), width=4)
        k = (t * 0.25) % 1
        x, y = seg[int(k * (len(seg) - 1))]
        ImageDraw.Draw(ov).ellipse((x - 16, y - 16, x + 16, y + 16), fill=(255, 255, 255, 255))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(5)))
    f.alpha_composite(ov)
    big(f, "가장 가까운 사람\n= 우주비행사", 560, 108, hl="우주비행사")


def s_grave(f, t, sc):
    """반전: 우주선의 무덤 — 빨간 원이 깜빡이고 우주선들이 떨어짐"""
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    r = globe(f, CX, 860, 440, C_LAT, C_LON, 1.25)
    p, _ = project(*NEMO, CX, 860, r, C_LAT, C_LON)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(90 + 70 * (0.5 + 0.5 * math.sin(t * 7)))
    d.ellipse((p[0] - 170, p[1] - 110, p[0] + 170, p[1] + 110), fill=(230, 50, 50, a), outline=(255, 90, 90, 255), width=5)
    for i in range(7):  # 떨어지는 우주선(불꽃 꼬리)
        st = (t * 0.9 + i / 7) % 1
        sx = p[0] - 300 + i * 90 + st * 140
        sy = p[1] - 520 + st * 470
        d.line((sx - 60, sy - 80, sx, sy), fill=(255, 170, 80, int(220 * (1 - st))), width=6)
        d.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=(255, 240, 200, int(255 * (1 - st))))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4)))
    f.alpha_composite(ov)
    pill_tag(f, "그런데 반전", t, col=CORAL)
    big(f, "우주선의 무덤", 1180, 120, col=(255, 110, 110))


def s_mir(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    r = globe(f, CX, 860, 440, C_LAT, C_LON, 1.25)
    p, _ = project(*NEMO, CX, 860, r, C_LAT, C_LON)
    glow_pin(f, p, t, (255, 110, 110))
    k = G.ease_out(G.clamp(t / 0.4))
    K.drop(f, G.pill("2001 · 러시아 미르 우주정거장", "Black", 50, (255, 255, 255), (200, 40, 40), pad=(28, 12)),
           (CX, 440 + (1 - k) * 20), "mt", k, blur=12)
    k2 = G.ease_out(G.clamp((t - sc["L"][-1]) / 0.4))
    if k2 > 0:
        big(f, "2030년쯤\n국제우주정거장도", 1110, 96, hl="국제우주정거장", o=k2)


def s_share(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    globe(f, CX, 900, 470, C_LAT, C_LON, 1.0)
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 150)))
    k = G.ease_out(G.clamp(t / 0.3))
    K.drop(f, T("좋아요 누르고", 110, GOLD, "Black", stroke=8, stroke_fill=(6, 8, 14)), (CX, 720 - (1 - k) * 20), "mm", k, blur=20)
    k2 = G.ease_out(G.clamp((t - 0.7) / 0.3))
    K.drop(f, T("친구한테\n물어보세요", 140, CREAM, "Black", highlight="물어보세요", hl_fill=GOLD, align="center", line_gap=1.08,
                stroke=8, stroke_fill=(6, 8, 14)), (CX, 960 - (1 - k2) * 20), "mm", k2, blur=24)


def draw_cover(f):
    s_hook(f, 2.0, {"L": [0]})


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.4, "gap": 0.12, "tail": 0.15, "sfx_t": [(0.05, "wow", 0.5)],
     "narr": ["우주보다 7배나 외로운 곳이, / 지구에 있다면 믿으시겠어요?"]},
    {"draw": s_where, "flash": True, "min": 1.8, "gap": 0.12, "tail": 0.15, "sfx_t": [(0.1, "glide", 0.5)],
     "narr": ["남태평양 한가운데, / 포인트 니모."]},
    {"draw": s_ring, "flash": True, "min": 2.6, "gap": 0.12, "tail": 0.25, "sfx_t": [(0.2, "glide", 0.6), (1.5, "ding", 0.5)],
     "narr": ["가장 가까운 섬까지, 사방 어디로 가도 약 2,700킬로미터예요."]},
    {"draw": s_iss, "flash": True, "min": 2.6, "gap": 0.15, "tail": 0.3,
     "sfx_fn": lambda sc: [(0.1, "glide", 0.45), (sc["L"][-1], "wow", 0.55)],
     "narr": ["그런데 머리 위 우주정거장은,", "겨우 400킬로미터."]},
    {"draw": s_astro, "flash": True, "min": 2.4, "gap": 0.12, "tail": 0.2, "sfx_t": [(0.1, "reveal", 0.55)],
     "narr": ["그래서 여기서 가장 가까운 사람은, / 우주비행사일 때가 많아요."]},
    {"draw": s_grave, "flash": True, "min": 2.4, "gap": 0.12, "tail": 0.2, "sfx_t": [(0.05, "accent_low", 0.6), (0.6, "boom", 0.35)],
     "narr": ["그리고 반전. / 이곳은 우주선의 무덤이에요."]},
    {"draw": s_mir, "flash": True, "min": 2.6, "gap": 0.15, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.05, "accent_low", 0.5), (sc["L"][-1], "accent", 0.5)],
     "narr": ["2001년, 러시아의 미르 우주정거장도 여기로 떨어졌고,", "2030년쯤엔 국제우주정거장도 이곳으로 내려올 예정이죠."]},
    {"draw": s_share, "flash": True, "nohead": True, "min": 2.2, "gap": 0.12, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.75, "pop", 0.6)],
     "narr": [K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["우주보다 7배나 외로운 곳이, / 지구에 있다면 믿으시겠어요?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
