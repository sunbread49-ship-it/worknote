"""지식창고 쇼츠 #7 · 우주보다 7배 외로운 곳이 지구에 있다? (포인트 니모 · 바다의 도달불능극)
  python3 science/nemo.py [--stills]
숫자 (구면 거리, 지구 반지름 6,371km — 직접 계산):
  포인트 니모 48.88°S 123.39°W → 듀시섬 2,695km · 모투누이(이스터섬 옆) 2,692km · 남극 마헤르섬 2,683km → '약 2,700km'
  국제우주정거장(ISS) 고도 약 400km → 2,700 / 400 ≈ 6.7 → '약 7배'
  우주선 무덤: 러시아 미르 우주정거장(2001년, 약 130톤) · 살류트 등이 이 바다에 떨어짐 / ISS(축구장 크기)도 2030년쯤 이곳으로 내려올 계획(NASA)
  서울~하노이 2,740km(구면 계산) · 바다의 사막: 남태평양 환류 중심은 영양분이 매우 적은 바다
  러브크래프트 「크툴루의 부름」(1928) 속 르뤼에 좌표 47°9′S 126°43′W → 포인트 니모에서 약 310km
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
HEAD = {"kicker": "지구에서 가장 외로운 곳", "title": "포인트 니모", "highlight": "니모"}
SAY = {"텅빈": "텅빈", "국제우주정거장": "국제우주정거장", "130톤": "백삼십 톤", "1928년": "천구백이십팔 년", "2,740킬로미터": "이천칠백사십 킬로미터", "2,700킬로미터": "이천칠백 킬로미터", "400킬로미터": "사백 킬로미터", "7배": "일곱 배", "2030년": "이천삼십 년",
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
    p = G.pill(text, "Black", 66, (12, 10, 6), col, pad=(38, 14))  # 상단 띠 크게 (2026-11-12)
    K.drop(f, p, (CX, y - (1 - k) * 20), "mt", k, blur=12)


def big(f, text, y, size=120, hl="", col=CREAM, o=1.0):
    im = T(text, size, col, "Black", highlight=hl, hl_fill=GOLD, align="center", line_gap=1.08, stroke=9, stroke_fill=(6, 8, 14))
    if im.width > W - 60:
        im = im.resize((W - 60, int(im.height * (W - 60) / im.width)), Image.LANCZOS)
    K.drop(f, im, (CX, y), "mm", o, blur=26, alpha=0.8)


# ── 장면 (2026-11-12 대폭 수정: 장면마다 화면을 바꾸고 2~4초씩 빠르게) ─────────────────
C_LAT, C_LON = -40.0, -125.0


def full_photo(f, name, t, dark=0.45, zoom=0.06, focus=(0.5, 0.5), tint=None):
    """사진을 세로 화면 가득 + 천천히 확대(켄 번스)"""
    im = K.photo(name, int(W * 1.12), int(H * 1.12), focus, dark)
    z = 1 + zoom * G.clamp(t / 4)
    w, h = int(W * 1.12 / z), int(H * 1.12 / z)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    f.alpha_composite(im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR))
    if tint:
        f.alpha_composite(Image.new("RGBA", (W, H), tint))


def s_hook(f, t, sc):
    full_photo(f, "rough_sea", t, dark=0.35, zoom=0.1)
    f.alpha_composite(Image.new("RGBA", (W, H), (20, 0, 0, 60)))
    if int(t * 3) % 2 == 0:  # 깜빡이는 SOS
        K.drop(f, G.pill("SOS", "Black", 110, (255, 255, 255), (220, 30, 30), pad=(40, 12)), (CX, 360), "mt", 1, blur=20)
    big(f, "여기서 조난당하면\n가장 가까운 사람은\n우주에 있다", 960, 112, hl="우주")
    K.credit(f, K.credit_of("rough_sea"))


def s_where(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    k = G.ease_out(G.clamp(t / 0.5))
    r = globe(f, CX, 830, 440, C_LAT, C_LON, 1.0 + 0.3 * k)
    p, _ = project(*NEMO, CX, 830, r, C_LAT, C_LON)
    glow_pin(f, p, t, CORAL, "포인트 니모")
    pill_tag(f, "남태평양 한가운데", t)


def s_radar(f, t, sc):
    """레이더: 아무리 돌려도 아무것도 안 잡힘"""
    f.alpha_composite(Image.new("RGBA", (W, H), (2, 14, 8, 255)))
    cx, cy, R = CX, 830, 430
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in (1, 0.75, 0.5, 0.25):
        d.ellipse((cx - R * k, cy - R * k, cx + R * k, cy + R * k), outline=(60, 220, 120, 120), width=3)
    d.line((cx - R, cy, cx + R, cy), fill=(60, 220, 120, 80), width=2)
    d.line((cx, cy - R, cx, cy + R), fill=(60, 220, 120, 80), width=2)
    a = t * 2.4
    for j in range(30):  # 회전하는 빛줄기 + 잔상
        aa = a - j * 0.03
        d.line((cx, cy, cx + R * math.cos(aa), cy + R * math.sin(aa)), fill=(80, 255, 150, int(200 * (1 - j / 30))), width=6)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(255, 90, 90, 255))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
    f.alpha_composite(ov)
    G.blit(f, T("반경 2,700km · 섬 0개 · 배 0척", 46, (120, 255, 170), "Black"), (CX, 1300), G.appear(t, 0.3, 0.3), "mb")
    pill_tag(f, "사방 2,700km, 아무것도 없다", t, col=(90, 230, 140))


def s_hanoi(f, t, sc):
    """서울에서 하노이까지(2,740km) 선이 그어짐 — 그만큼 사방에 아무것도 없다"""
    box = (40, 430, W - 80, 820)
    lon0, lon1, lat0, lat1 = 95.0, 145.0, 10.0, 48.0

    def xy(la, lo):
        return box[0] + (lo - lon0) / (lon1 - lon0) * box[2], box[1] + (lat1 - la) / (lat1 - lat0) * box[3]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((box[0], box[1], box[0] + box[2], box[1] + box[3]), 26, fill=(10, 24, 50, 255))
    for ring in FL.world():
        if not any(lon0 - 20 < lo < lon1 + 20 and lat0 - 20 < la < lat1 + 20 for lo, la in ring[::5]):
            continue
        d.polygon([xy(la, lo) for lo, la in ring], fill=(78, 108, 150, 255), outline=(170, 205, 240, 255))
    mk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mk).rounded_rectangle((box[0], box[1], box[0] + box[2], box[1] + box[3]), 26, fill=255)
    lay.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").asarray(lay.getchannel("A")), __import__("numpy").asarray(mk))))
    f.alpha_composite(lay)
    a, b = xy(37.57, 126.98), xy(21.03, 105.85)
    k = G.ease_out(G.clamp((t - 0.3) / 1.0))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).line((a, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)), fill=GOLD + (255,), width=10)
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(8)))
    f.alpha_composite(ov)
    for p_, n_ in ((a, "서울"), (b, "하노이")):
        ImageDraw.Draw(f).ellipse((p_[0] - 13, p_[1] - 13, p_[0] + 13, p_[1] + 13), fill=(255, 255, 255, 255))
        G.blit(f, T(n_, 46, CREAM, "Black", stroke=5, stroke_fill=(6, 8, 14)), (p_[0], p_[1] - 22), 1, "mb")
    pill_tag(f, "이 거리만큼 사방이 텅 빈 바다", t)
    big(f, f"{int(2740 * k):,}km", 1180, 110, col=GOLD)


def s_iss(f, t, sc):
    full_photo(f, "iss_sts132", t, dark=0.25, zoom=0.12, focus=(0.5, 0.45))
    k = G.ease_out(G.clamp((t - 0.2) / 0.5))
    if t < sc["L"][-1] - 0.05:
        big(f, "머리 위\n고작 400km", 1080, 130, hl="400km", o=k)
    else:
        big(f, "가장 가까운 이웃\n= 우주비행사", 1080, 112, hl="우주비행사")
    K.credit(f, K.credit_of("iss_sts132"))


def s_astro(f, t, sc):
    """'우주비행사'가 가장 가까운 이웃 — 아래 바다 · 위 우주정거장 · 거리 비교 막대"""
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    x0, full = 90, W - 180
    k1 = G.ease_out(G.clamp(t / 0.6))
    k2 = G.ease_out(G.clamp((t - 0.5) / 0.5))
    for i, (lab, km, col, k) in enumerate((("가장 가까운 섬", 2700, MINT, k1), ("우주비행사", 400, GOLD, k2))):
        y = 560 + i * 230
        G.blit(f, T(lab, 54, col, "Black"), (x0, y), min(1, k * 3), "lt")
        bw = int(full * km / 2700 * k)
        if bw > 4:
            bar = Image.new("RGBA", (bw, 70), col + (255,))
            mk = Image.new("L", bar.size, 0)
            ImageDraw.Draw(mk).rounded_rectangle((0, 0, bw - 1, 69), 35, fill=255)
            bar.putalpha(mk)
            f.alpha_composite(bar.filter(ImageFilter.GaussianBlur(14)), (x0, y + 80))
            f.alpha_composite(bar, (x0, y + 80))
            G.blit(f, T(f"{int(km * k):,}km", 56, CREAM, "Black", stroke=5, stroke_fill=(6, 8, 14)),
                   (x0 + bw + 16 if km < 1000 else x0 + bw - 16, y + 115), 1, "lm" if km < 1000 else "rm")
    o = G.appear(t, 1.0, 0.25)
    big(f, "가장 가까운 이웃\n= 우주비행사", 1150, 104, hl="우주비행사", o=o)


def s_desert(f, t, sc):
    """바다의 사막: 물고기가 하나둘 사라짐"""
    f.alpha_composite(Image.new("RGBA", (W, H), (2, 10, 26, 255)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(14):
        x = (90 + i * 137 + t * 60 * (1 + i % 3)) % (W + 200) - 100
        y = 520 + (i * 97) % 560
        fade = G.clamp(1 - (t - 0.3 - i * 0.12) / 0.4)
        if fade <= 0:
            continue
        a = int(200 * fade)
        d.ellipse((x - 46, y - 18, x + 30, y + 18), fill=(140, 200, 255, a))
        d.polygon([(x + 26, y), (x + 60, y - 22), (x + 60, y + 22)], fill=(140, 200, 255, a))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1.5)))
    pill_tag(f, "영양분이 거의 없는 바다", t, col=(120, 200, 255))
    big(f, "바다의 사막", 1150, 130, col=(150, 210, 255), o=G.appear(t, 0.8, 0.3))


def s_fall(f, t, sc):
    full_photo(f, "rough_sea", t + 2, dark=0.55, zoom=0.05, tint=(60, 10, 0, 70))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(9):
        st = (t * 0.8 + i / 9) % 1
        sx = 80 + i * 110 + st * 260
        sy = 200 + st * 900
        d.line((sx - 120, sy - 170, sx, sy), fill=(255, 150, 60, int(230 * (1 - st))), width=10)
        d.ellipse((sx - 12, sy - 12, sx + 12, sy + 12), fill=(255, 245, 210, int(255 * (1 - st))))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))
    f.alpha_composite(ov)
    big(f, "하늘에서\n우주선이 떨어진다", 1100, 112, col=(255, 140, 110))
    K.credit(f, K.credit_of("rough_sea"))


def s_why_burn(f, t, sc):
    """왜 떨어뜨리나: 큰 우주선은 대기권에서 다 타지 않고, 남은 조각이 넓게 흩어진다"""
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 8, 18, 255)))
    # 지구 가장자리(아래 큰 호) + 대기권
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((-900, 1050, W + 900, 3600), fill=(20, 50, 100, 255))
    d.ellipse((-940, 1010, W + 940, 3640), outline=(110, 180, 255, 120), width=26)
    k = G.ease_out(G.clamp(t / 1.6))
    x, y = 140 + 700 * k, 420 + 560 * k
    for j in range(16):  # 불꽃 꼬리
        a = j / 16
        d.line((x - 300 * a * k, y - 240 * a * k, x - 300 * (a + 0.07) * k, y - 240 * (a + 0.07) * k),
               fill=(255, int(220 - 160 * a), 80, int(230 * (1 - a))), width=int(26 * (1 - a)) + 2)
    d.rectangle((x - 22, y - 14, x + 22, y + 14), fill=(230, 230, 240, 255))
    if t > 1.2:  # 다 타지 않은 조각들이 흩어짐
        for i in range(9):
            u = G.clamp((t - 1.2) / 1.2)
            px = x + (i - 4) * 60 * u + 40 * u
            py = y + 80 * u + (i % 3) * 30 * u
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=(255, 190, 120, 255))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(5)))
    f.alpha_composite(ov)
    pill_tag(f, "왜 하필 여기로?", t, col=CORAL)
    big(f, "다 타지 않은 조각이\n비처럼 쏟아진다", 720, 96, hl="조각", o=G.appear(t, 1.0, 0.3))


def s_why_aim(f, t, sc):
    """그래서 일부러 조준: 사람도 배도 없는 곳 = 포인트 니모 (섬이 아니라 바다 한가운데)"""
    f.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 14, 255)))
    r = globe(f, CX, 830, 440, C_LAT, C_LON, 1.3)
    p, _ = project(*NEMO, CX, 830, r, C_LAT, C_LON)
    k = G.ease_out(G.clamp(t / 0.9))
    R0 = 420 - 300 * k
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((p[0] - R0, p[1] - R0, p[0] + R0, p[1] + R0), outline=(255, 70, 70, 255), width=8)
    d.line((p[0] - R0 - 40, p[1], p[0] + R0 + 40, p[1]), fill=(255, 70, 70, 255), width=5)
    d.line((p[0], p[1] - R0 - 40, p[0], p[1] + R0 + 40), fill=(255, 70, 70, 255), width=5)
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(5)))
    f.alpha_composite(ov)
    pill_tag(f, "사람 머리 위는 절대 안 돼", t, col=CORAL)
    big(f, "그래서 일부러\n여기를 조준", 1200, 112, hl="조준", o=G.appear(t, 0.6, 0.3))


def s_mir(f, t, sc):
    name = "mir" if (K.PHOTOS / "mir.json").exists() else "iss_sts132"
    full_photo(f, name, t, dark=0.3, zoom=0.14, tint=(80, 20, 0, 40))
    k = G.ease_out(G.clamp(t / 0.4))
    K.drop(f, G.pill("2001년 · 러시아 미르", "Black", 66, (255, 255, 255), (200, 40, 40), pad=(38, 14)),
           (CX, 430 + (1 - k) * 20), "mt", k, blur=12)
    big(f, "130톤이\n불타며 추락", 1100, 124, hl="130톤", o=G.appear(t, 0.5, 0.3))
    K.credit(f, K.credit_of(name))


def s_next(f, t, sc):
    full_photo(f, "iss_sts132", t + 3, dark=0.35, zoom=0.1, focus=(0.5, 0.45))
    k = G.ease_out(G.clamp(t / 0.4))
    K.drop(f, G.pill("다음 차례는?", "Black", 66, (12, 10, 6), GOLD, pad=(38, 14)), (CX, 430 + (1 - k) * 20), "mt", k, blur=12)
    big(f, "2030년쯤\n축구장만 한\n국제우주정거장", 1100, 104, hl="국제우주정거장", o=G.appear(t, 0.3, 0.3))
    K.credit(f, K.credit_of("iss_sts132"))


def s_cthulhu(f, t, sc):
    """반전 하나 더: 1928년 공포 소설 속 괴물의 바닷속 도시 좌표가 바로 근처"""
    f.alpha_composite(Image.new("RGBA", (W, H), (2, 12, 10, 255)))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = int(110 + 60 * math.sin(t * 5))
    ImageDraw.Draw(g).ellipse((CX - 360, 560, CX + 360, 1100), fill=(40, 200, 120, a))
    f.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(5):  # 아래에서 올라오는 촉수 실루엣
        base = 150 + i * 200
        pts = []
        for j in range(40):
            yy = 1350 - j * 16 * G.ease_out(G.clamp((t - i * 0.1) / 1.2))
            xx = base + 50 * math.sin(j * 0.35 + t * 3 + i)
            pts.append((xx, yy))
        d.line(pts, fill=(6, 30, 22, 255), width=46 - i, joint="curve")
    f.alpha_composite(ov)
    G.blit(f, T("47°9′S 126°43′W", 46, (140, 255, 190), "Black"), (CX, 470), G.appear(t, 0.2, 0.3), "mt")
    big(f, "소설 속 괴물이\n잠든 도시도\n바로 근처", 860, 108, hl="괴물", o=G.appear(t, 0.5, 0.3))


def s_share(f, t, sc):
    full_photo(f, "rough_sea", t, dark=0.6, zoom=0.04)
    k = G.ease_out(G.clamp(t / 0.3))
    K.drop(f, T("좋아요 누르고", 110, GOLD, "Black", stroke=8, stroke_fill=(6, 8, 14)), (CX, 720 - (1 - k) * 20), "mm", k, blur=20)
    k2 = G.ease_out(G.clamp((t - 0.7) / 0.3))
    K.drop(f, T("친구한테\n물어보세요", 140, CREAM, "Black", highlight="물어보세요", hl_fill=GOLD, align="center", line_gap=1.08,
                stroke=8, stroke_fill=(6, 8, 14)), (CX, 960 - (1 - k2) * 20), "mm", k2, blur=24)
    K.credit(f, K.credit_of("rough_sea"))


def draw_cover(f):
    s_hook(f, 0.0, {"L": [0]})


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.6, "gap": 0.12, "tail": 0.15, "sfx_t": [(0.05, "accent_low", 0.6), (0.4, "wow", 0.45)],
     "narr": ["이 바다에서 조난당하면, / 가장 가까운 사람은 우주에 있어요."]},
    {"draw": s_where, "flash": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "glide", 0.5)],
     "narr": ["남태평양 한가운데, 포인트 니모."]},
    {"draw": s_radar, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.1, "tick", 0.4), (0.9, "tick", 0.4), (1.7, "tick", 0.4)],
     "narr": ["사방 어디로 가도, 섬까지 2,700킬로미터."]},
    {"draw": s_hanoi, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "glide", 0.55)],
     "narr": ["서울에서 하노이 거리만큼, / 텅빈 / 바다예요."]},
    {"draw": s_iss, "flash": True, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.1,
     "sfx_fn": lambda sc: [(0.2, "wow", 0.55), (sc["L"][-1], "reveal", 0.55)],
     "narr": ["머리 위 우주정거장은 고작 400킬로미터.", "가장 가까운 이웃이, 우주비행사인 거죠."]},
    {"draw": s_desert, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.8, "accent", 0.5)],
     "narr": ["물고기도 드문, 바다의 사막이고요."]},
    {"draw": s_fall, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "accent_low", 0.6), (0.5, "boom", 0.35)],
     "narr": ["그래서 이곳은, / 우주선의 무덤이 됐어요."]},
    {"draw": s_why_burn, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "glide", 0.5), (1.2, "boom", 0.35)],
     "narr": ["큰 우주선은 떨어질 때 다 타지 않아서, / 불타고 남은 조각이 비처럼 쏟아지거든요."]},
    {"draw": s_why_aim, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "riser", 0.35), (0.9, "accent_low", 0.6)],
     "narr": ["사람 머리 위로 떨어지면 큰일이니까, / 지구에서 제일 외로운 이 바다를 일부러 조준하는 거예요."]},
    {"draw": s_mir, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.5, "boom", 0.4)],
     "narr": ["2001년엔 130톤짜리 미르가, 불타며 떨어졌고,"]},
    {"draw": s_next, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "accent", 0.5)],
     "narr": ["2030년쯤엔, 축구장만 한 / 국제우주정거장 차례예요."]},
    {"draw": s_cthulhu, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "riser", 0.4), (0.5, "accent_low", 0.55)],
     "narr": ["게다가 공포 소설 속 괴물이 잠든 도시도, / 바로 이 근처래요."]},
    {"draw": s_share, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.75, "pop", 0.6)],
     "narr": [K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["이 바다에서 조난당하면, / 가장 가까운 사람은 우주에 있어요."]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
