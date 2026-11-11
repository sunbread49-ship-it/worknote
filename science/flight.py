"""지식창고 쇼츠 #6 · 인천→뉴욕 비행기는 왜 북극 쪽으로 돌아갈까? (대권 항로, 쉬운 말로)
  python3 science/flight.py [--stills]
숫자 (구면 거리, 지구 반지름 6,371km):
  인천(37.46N, 126.44E) → 뉴욕 JFK(40.64N, 73.78W)
  대권(공 위 최단) 11,090km · 평평한 지도(위경도 격자)에서 쭉 그은 직선을 따라가면 13,800km → 약 2,700km 짧음
  대권 경로 최고 위도 약 78°N · 서울~부산 직선 약 325km → 2,700km는 8번 넘게
  실제 항로는 바람(제트기류) · 하늘길 사정으로 조금씩 다름 (화면에 표기)
지도: assets/geo/world.json (Natural Earth 기반 공개 데이터)
"""
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, H, CREAM, DIM, CORAL, BLUE, MINT, GOLD

OUT = K.HERE / "out" / "flight"
HEAD = {"kicker": "지구의 수학", "title": "비행기는 왜\n북극으로 돌아갈까?", "highlight": "북극"}
SAY = {"1만 3,800킬로미터": "만 삼천팔백 킬로미터", "1만 1,090킬로미터": "만 천구십 킬로미터", "2,700킬로미터": "이천칠백 킬로미터",
       "인천": "인천", "뉴욕": "뉴욕"}
CX = W / 2
ICN, JFK = (37.46, 126.44), (40.64, -73.78)
SEA, LAND, LAND_EDGE = (10, 22, 44), (52, 70, 96), (96, 120, 150)
ROUTE, FLAT = GOLD, CORAL


@lru_cache(maxsize=1)
def world():
    d = json.loads((K.HERE.parent / "youtube" / "assets" / "geo" / "world.json").read_text())
    polys = []
    for ft in d["features"]:
        g = ft["geometry"]
        rings = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in rings:
            polys.append(poly[0])
    return polys


def gc_points(a, b, n=200):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    p1 = np.array([math.cos(la1) * math.cos(lo1), math.cos(la1) * math.sin(lo1), math.sin(la1)])
    p2 = np.array([math.cos(la2) * math.cos(lo2), math.cos(la2) * math.sin(lo2), math.sin(la2)])
    om = math.acos(float(np.dot(p1, p2)))
    pts = []
    for i in range(n + 1):
        f = i / n
        v = (math.sin((1 - f) * om) * p1 + math.sin(f * om) * p2) / math.sin(om)
        pts.append((math.degrees(math.atan2(v[2], math.hypot(v[0], v[1]))), math.degrees(math.atan2(v[1], v[0]))))
    return pts


# ── 평평한 지도 (태평양 가운데) ─────────────────────────────────────
LON0, LON1, LAT0, LAT1 = 100.0, 318.0, 5.0, 86.0


def mxy(lat, lon, box):
    x0, y0, w, h = box
    lo = lon % 360
    return x0 + (lo - LON0) / (LON1 - LON0) * w, y0 + (LAT1 - lat) / (LAT1 - LAT0) * h


@lru_cache(maxsize=4)
def flat_map(box):
    x0, y0, w, h = box
    k = 2
    im = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((x0 * k, y0 * k, (x0 + w) * k, (y0 + h) * k), fill=SEA + (255,))
    for gl in range(-0, 90, 15):  # 위도선
        _, yy = mxy(gl, 180, box)
        d.line((x0 * k, yy * k, (x0 + w) * k, yy * k), fill=(40, 60, 96, 255), width=k)
    for ring in world():
        lons = [lo % 360 for lo, la in ring]
        if any(abs(lons[i + 1] - lons[i]) > 180 for i in range(len(lons) - 1)):
            continue  # 0°/360° 경계에 걸친 조각(유럽 · 아프리카 일부)은 화면 밖이라 생략
        pts = [mxy(la, lo, box) for lo, la in ring]
        d.polygon([(px * k, py * k) for px, py in pts], fill=LAND + (255,), outline=LAND_EDGE + (255,))
    im = im.resize((W, H), Image.LANCZOS)
    mk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mk).rounded_rectangle((x0, y0, x0 + w, y0 + h), 28, fill=255)
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(mk))))
    return im


def route_xy(box, kind):
    if kind == "gc":
        return [mxy(la, lo, box) for la, lo in gc_points(ICN, JFK)]
    n = 120
    return [mxy(ICN[0] + (JFK[0] - ICN[0]) * i / n, ICN[1] + (JFK[1] + 360 - ICN[1]) * i / n, box) for i in range(n + 1)]


def draw_route(f, pts, k, col, width=8, dash=False):
    m = max(2, int(len(pts) * k))
    seg = pts[:m]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    if dash:
        for i in range(0, len(seg) - 1, 4):
            d.line(seg[i:i + 3], fill=col + (255,), width=width)
    else:
        d.line(seg, fill=col + (255,), width=width, joint="curve")
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(10)))
    f.alpha_composite(ov)
    if k < 1:  # 비행기 점
        x, y = seg[-1]
        ImageDraw.Draw(f).ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 255, 255, 255))


def pins(f, box, o=1.0):
    for (la, lo), name, anc in ((ICN, "인천", "rm"), (JFK, "뉴욕", "rm")):
        x, y = mxy(la, lo, box)
        ImageDraw.Draw(f).ellipse((x - 14, y - 14, x + 14, y + 14), fill=(255, 255, 255, int(255 * o)), outline=(10, 12, 20, 255), width=4)
        G.blit(f, T(name, 46, CREAM, "Black", stroke=5, stroke_fill=(6, 8, 14)), (x + (-24 if anc == "rm" else 24), y + 46), o, "rm" if anc == "rm" else "lm")


# ── 지구본 (정사영) ─────────────────────────────────────────────
def ortho(lat, lon, c_lat, c_lon):
    la, lo, cl, cn = map(math.radians, (lat, lon, c_lat, c_lon))
    cosc = math.sin(cl) * math.sin(la) + math.cos(cl) * math.cos(la) * math.cos(lo - cn)
    x = math.cos(la) * math.sin(lo - cn)
    y = math.cos(cl) * math.sin(la) - math.sin(cl) * math.cos(la) * math.cos(lo - cn)
    return x, y, cosc


@lru_cache(maxsize=64)
def globe_img(r, c_lat, c_lon):
    k = 2
    s = r * 2 * k
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=SEA + (255,))
    R = r * k
    for gl in range(-60, 90, 30):  # 위도선
        pts = []
        for lo in range(0, 361, 6):
            x, y, c = ortho(gl, lo, c_lat, c_lon)
            pts.append((R + x * R, R - y * R) if c > 0 else None)
        seg = []
        for p in pts + [None]:
            if p:
                seg.append(p)
            elif len(seg) > 1:
                d.line(seg, fill=(40, 60, 96, 255), width=k)
                seg = []
            else:
                seg = []
    for ring in world():
        pr = [ortho(la, lo, c_lat, c_lon) for lo, la in ring]
        if sum(1 for _, _, c in pr if c > 0) < len(pr) * 0.6:
            continue
        d.polygon([(R + x * R, R - y * R) for x, y, c in pr], fill=LAND + (255,), outline=LAND_EDGE + (255,))
    # 입체감: 가장자리 어둡게 + 왼쪽 위 빛
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    rr = np.sqrt((xx - R) ** 2 + (yy - R) ** 2) / R
    shade = np.clip(1 - 0.55 * rr ** 3, 0, 1)
    a = np.asarray(im).astype(np.float32)
    a[..., :3] *= shade[..., None]
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    gl_ = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(gl_).ellipse((s * 0.12, s * 0.08, s * 0.55, s * 0.45), fill=(255, 255, 255, 36))
    out.alpha_composite(gl_.filter(ImageFilter.GaussianBlur(s * 0.06)))
    mk = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mk).ellipse((0, 0, s - 1, s - 1), fill=255)
    out.putalpha(mk)
    return out.resize((r * 2, r * 2), Image.LANCZOS)


def globe_route(f, cx, cy, r, c_lat, c_lon, k=1.0, sag=0.0, col=ROUTE):
    """지구본 위 대권 + (sag>0이면 느슨한 실처럼 남쪽으로 처진 모양에서 시작)"""
    g = globe_img(r, round(c_lat, 1), round(c_lon, 1))
    K.drop(f, g, (cx, cy), "mm", 1, blur=40, alpha=0.6)
    pts = []
    for i, (la, lo) in enumerate(gc_points(ICN, JFK, 120)):
        fr = i / 120
        la2 = la - sag * 60 * math.sin(math.pi * fr)
        x, y, c = ortho(la2, lo, c_lat, c_lon)
        if c > 0:
            pts.append((cx + x * r, cy - y * r))
    m = max(2, int(len(pts) * k))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).line(pts[:m], fill=col + (255,), width=8, joint="curve")
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(9)))
    f.alpha_composite(ov)
    for (la, lo), name in ((ICN, "인천"), (JFK, "뉴욕")):
        x, y, c = ortho(la, lo, c_lat, c_lon)
        if c > 0:
            px, py = cx + x * r, cy - y * r
            ImageDraw.Draw(f).ellipse((px - 13, py - 13, px + 13, py + 13), fill=(255, 255, 255, 255), outline=(10, 12, 20, 255), width=4)
            G.blit(f, T(name, 40, CREAM, "Black", stroke=5, stroke_fill=(6, 8, 14)), (px, py + 26), 1, "mt")


def big_q(f, y=1000, size=132, o=1.0):
    q = T("인천→뉴욕 비행기\n왜 북극으로 돌아갈까?", size, CREAM, "Black", highlight="북극", hl_fill=GOLD, align="center",
          line_gap=1.1, stroke=10, stroke_fill=(6, 8, 14))
    if q.width > W - 60:
        q = q.resize((W - 60, int(q.height * (W - 60) / q.width)), Image.LANCZOS)
    K.drop(f, q, (CX, y), "mm", o, blur=30, alpha=0.8)


# ── 장면 ─────────────────────────────────────────────────────────
BOX_FULL = (0, 300, W, 700)


def s_hook(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 20, 255)))
    f.alpha_composite(flat_map(BOX_FULL))
    pins(f, BOX_FULL)
    draw_route(f, route_xy(BOX_FULL, "gc"), G.clamp(0.25 + t / 1.6), ROUTE, 10)
    big_q(f, y=1170, size=118, o=1.0)


BOX = (40, 430, W - 80, 560)


def s_compare(f, t, sc):
    L = sc["L"]
    f.alpha_composite(flat_map(BOX))
    pins(f, BOX)
    k1 = G.clamp((t - L[0] - 0.2) / 1.4)
    draw_route(f, route_xy(BOX, "flat"), k1, FLAT, 8, dash=True)
    k2 = G.clamp((t - L[-1] - 0.1) / 1.4)
    if k2 > 0:
        draw_route(f, route_xy(BOX, "gc"), k2, ROUTE, 10)
    o1 = G.appear(t, L[0] + 0.6, 0.3)
    G.blit(f, T(f"지도 위 직선  {int(13800 * min(1, k1 * 1.2)):,}km", 50, FLAT, "Black"), (70, 1040), o1, "lt")
    o2 = G.appear(t, L[-1] + 0.3, 0.3)
    G.blit(f, T(f"휘어진 길  {int(11090 * min(1, k2 * 1.2)):,}km", 50, ROUTE, "Black"), (70, 1110), o2, "lt")
    if k2 >= 1:
        o3 = G.appear(t, L[-1] + 1.6, 0.25)
        K.drop(f, G.pill("휘어진 길이 더 짧다!", "Black", 52, (12, 10, 6), GOLD, pad=(28, 12)), (W - 60, 1180), "rb", o3, blur=14)


def s_globe(f, t, sc):
    """평평한 지도는 귤껍질을 편 그림 → 공 위에선 이게 직선 (지구본 천천히 회전)"""
    L = sc["L"]
    c_lon = -150 + 8 * math.sin(t * 0.4)
    globe_route(f, CX, 830, 400, 62, c_lon, k=G.clamp((t - (L[-1] if len(L) > 1 else 0.5)) / 1.4))
    o = G.appear(t, 0.2, 0.3)
    G.blit(f, T("지구는 공", 64, CREAM, "Black"), (CX, 420), o, "mt")


def s_string(f, t, sc):
    """지구본에 실을 팽팽하게 당기면 → 북쪽으로 지나감"""
    L = sc["L"]
    tau = G.ease_out(G.clamp((t - 0.8) / 1.8))
    globe_route(f, CX, 830, 400, 62, -150, k=1.0, sag=1 - tau, col=(240, 236, 226))
    o = G.appear(t, 0.2, 0.3)
    G.blit(f, T("실을 팽팽하게 당기면?", 60, CREAM, "Black"), (CX, 420), o, "mt")


def s_save(f, t, sc):
    L = sc["L"]
    f.alpha_composite(flat_map(BOX))
    draw_route(f, route_xy(BOX, "flat"), 1, FLAT, 6, dash=True)
    draw_route(f, route_xy(BOX, "gc"), 1, ROUTE, 10)
    pins(f, BOX)
    k = G.ease_out(G.clamp((t - 0.2) / 0.8))
    K.drop(f, T(f"{int(2700 * k):,}km 절약", 120, GOLD, "Black", stroke=8, stroke_fill=(6, 8, 14)), (CX, 1075), "mm", min(1, k * 2), blur=24)
    o = G.appear(t, L[-1], 0.3)
    G.blit(f, G.pill("서울~부산을 8번 넘게", "Black", 56, (12, 10, 6), CREAM, pad=(30, 12)), (CX, 1160), o, "mt")
    G.blit(f, T("실제 항로는 바람 · 하늘길 사정에 따라 조금씩 달라요", 26, DIM, "SemiBold"), (CX, 395), 1, "mt")


def s_share(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 20, 255)))
    f.alpha_composite(flat_map(BOX_FULL))
    draw_route(f, route_xy(BOX_FULL, "gc"), 1, ROUTE, 10)
    dk = Image.new("RGBA", (W, H), (6, 10, 20, 150))
    f.alpha_composite(dk)
    k = G.ease_out(G.clamp(t / 0.3))
    K.drop(f, T("좋아요 누르고", 110, GOLD, "Black", stroke=8, stroke_fill=(6, 8, 14)), (CX, 700 - (1 - k) * 20), "mm", k, blur=20)
    k2 = G.ease_out(G.clamp((t - 0.7) / 0.3))
    K.drop(f, T("친구한테\n물어보세요", 140, CREAM, "Black", highlight="물어보세요", hl_fill=GOLD, align="center", line_gap=1.08,
                stroke=8, stroke_fill=(6, 8, 14)), (CX, 940 - (1 - k2) * 20), "mm", k2, blur=24)


def s_loop(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 20, 255)))
    f.alpha_composite(flat_map(BOX_FULL))
    pins(f, BOX_FULL)
    draw_route(f, route_xy(BOX_FULL, "gc"), 1, ROUTE, 10)
    big_q(f, y=1170, size=118, o=1.0)


def draw_cover(f):
    s_hook(f, 3.0, {"L": [0]})


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.6, "gap": 0.15, "tail": 0.2,
     "narr": ["인천에서 뉴욕 가는 비행기, / 왜 굳이 북극 쪽으로 돌아갈까요?"]},
    {"draw": s_compare, "flash": True, "min": 6.0, "gap": 0.25, "tail": 0.6,
     "narr": ["지도에서 쭉 그은 직선은, 1만 3,800킬로미터.", "그런데 휘어진 길은, / 1만 1,090킬로미터예요."]},
    {"draw": s_globe, "flash": True, "min": 3.4, "gap": 0.2, "tail": 0.3,
     "narr": ["지구는 공이고, 평평한 지도는 귤껍질을 억지로 펴 놓은 그림이거든요.", "공 위에선, 이 휘어진 길이 진짜 직선이에요."]},
    {"draw": s_string, "flash": True, "min": 3.4, "gap": 0.2, "tail": 0.3,
     "narr": ["지구본에 실을 팽팽하게 당겨 봐도, / 실은 똑같이 북쪽으로 지나가죠."]},
    {"draw": s_save, "flash": True, "min": 3.4, "gap": 0.2, "tail": 0.3,
     "narr": ["덕분에 아끼는 거리는 약 2,700킬로미터.", "서울에서 부산을 여덟 번 넘게 가는 거리예요."]},
    {"draw": s_share, "flash": True, "nohead": True, "min": 2.2, "gap": 0.15, "tail": 0.15,
     "narr": [K.CTA]},
    {"draw": s_loop, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["인천에서 뉴욕 가는 비행기, / 왜 굳이 북극 쪽으로 돌아갈까요?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
