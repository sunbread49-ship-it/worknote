"""정사영(orthographic) 지구본 — 실제 대륙 모양(Natural Earth 1:110m, 퍼블릭 도메인)으로 돌아가는 3D 지구
  globe_img(r, lon0, lat0, alpha=255, grid=True) → RGBA (2r+2pad)
  project(lon, lat, lon0, lat0, r) → (x, y, 앞면 여부)  (지구본 중심 기준 좌표)
"""
import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PAD = 40
CITIES = {"서울": (126.98, 37.57), "부산": (129.08, 35.18), "뉴욕": (-74.0, 40.71), "도쿄": (139.69, 35.69),
          "서울 반대편": (-53.02, -37.57), "북극": (0, 90), "남극": (0, -90), "런던": (-0.13, 51.51)}


@lru_cache(maxsize=1)
def _world():
    return json.loads((ROOT / "assets/data/world110.json").read_text())


def project(lon, lat, lon0, lat0, r):
    p, l = math.radians(lat), math.radians(lon - lon0)
    p0 = math.radians(lat0)
    cosc = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l)
    x = r * math.cos(p) * math.sin(l)
    y = -r * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l))
    return x, y, cosc > 0


def xyz(lon, lat, lon0, lat0, r):
    """3D 좌표(화면 x, 화면 y, 앞쪽 z) — 지구 속을 지나는 직선 터널 그리기용"""
    p, l = math.radians(lat), math.radians(lon - lon0)
    p0 = math.radians(lat0)
    z = r * (math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l))
    x = r * math.cos(p) * math.sin(l)
    y = -r * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l))
    return x, y, z


def globe_img(r, lon0, lat0, alpha=255, grid=True, ocean=(28, 86, 168), land=(96, 168, 92), glow=True):
    s = 2   # 2배로 그려서 줄이기(매끈하게)
    R = r * s
    W = 2 * (R + PAD * s)
    c = W / 2
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if glow:
        g = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((c - R - 18 * s, c - R - 18 * s, c + R + 18 * s, c + R + 18 * s), fill=(90, 170, 255, 110))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14 * s)))
    d.ellipse((c - R, c - R, c + R, c + R), fill=ocean + (255,))
    for poly in _world():
        pts, vis = [], 0
        for lon, lat in poly:
            x, y, v = project(lon, lat, lon0, lat0, R)
            if not v:
                n = math.hypot(x, y) or 1
                x, y = x / n * R, y / n * R
            else:
                vis += 1
            pts.append((c + x, c + y))
        if vis >= 2 and len(pts) >= 3:
            d.polygon(pts, fill=land + (255,))
    if grid:
        for lat in range(-60, 90, 30):
            pts = [project(lon, lat, lon0, lat0, R) for lon in range(-180, 181, 4)]
            seg = [(c + x, c + y) for x, y, v in pts if v]
            if len(seg) > 1:
                d.line(seg, fill=(255, 255, 255, 40), width=s)
        for lon in range(-180, 180, 30):
            pts = [project(lon, lat, lon0, lat0, R) for lat in range(-90, 91, 4)]
            seg = [(c + x, c + y) for x, y, v in pts if v]
            if len(seg) > 1:
                d.line(seg, fill=(255, 255, 255, 40), width=s)
    # 입체감: 왼쪽 위 빛 · 오른쪽 아래 그림자
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for k in range(40, 0, -1):
        q = k / 40
        rr = R * q
        ox, oy = -R * 0.35 * (1 - q), -R * 0.35 * (1 - q)
        sd.ellipse((c + ox - rr, c + oy - rr, c + ox + rr, c + oy + rr), fill=(0, 0, 0, int(150 * (q ** 3) * 0.9)))
    hl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((c - R * 0.75, c - R * 0.8, c - R * 0.05, c - R * 0.1), fill=(255, 255, 255, 60))
    hl = hl.filter(ImageFilter.GaussianBlur(R * 0.15))
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).ellipse((c - R, c - R, c + R, c + R), fill=255)
    inv = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    inv.paste(sh, (0, 0), mask)
    # 그림자는 안쪽 원 기준으로 반전(가장자리가 어둡게)
    edge = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    for k in range(24):
        q = k / 24
        ed.ellipse((c - R + R * 0.25 * q, c - R + R * 0.25 * q, c + R - R * 0.05 * q, c + R - R * 0.05 * q), outline=(0, 0, 20, int(110 * (1 - q))), width=int(R * 0.012) + 2)
    im.alpha_composite(edge)
    hl2 = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    hl2.paste(hl, (0, 0), mask)
    im.alpha_composite(hl2)
    d.ellipse((c - R, c - R, c + R, c + R), outline=(150, 205, 255, 255), width=3 * s)
    im = im.resize((W // s, W // s), Image.LANCZOS)
    if alpha < 255:
        a = im.getchannel("A").point(lambda v: int(v * alpha / 255))
        im.putalpha(a)
    return im
