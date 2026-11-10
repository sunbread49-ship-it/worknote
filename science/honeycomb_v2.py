"""지식창고 쇼츠 #5 v2 · 벌집은 왜 육각형일까? — 첫 1초 개선판 (약 45초)
  python3 science/honeycomb_v2.py [--stills]
개선 (2026-11-10 분석: '계속 시청함' 30~50% → 첫 화면에서 절반 이상 넘김)
  1) 결과 장면 먼저: 0초부터 화면 가득 금빛 벌집이 가운데서 터지듯 자라남 (고정 제목 없이)
  2) 질문을 화면 가득 크게
  3) 첫 문장 짧고 세게
  4) 45초 안팎 · 마지막 문장이 첫 질문으로 이어지는 루프 · 공유 유도 한 줄
숫자: 넓이 1을 만드는 둘레 — 정삼각형 4.559 · 정사각형 4.000 · 정육각형 3.722 / 밀랍 1kg ← 꿀 약 6~8kg / 1999년 토머스 헤일스 증명
"""
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, H, CREAM, DIM, CORAL, BLUE, GOLD

OUT = K.HERE / "out" / "honeycomb_v2"
HEAD = {"kicker": "자연의 수학", "title": "벌집은 왜\n육각형일까?", "highlight": "육각형"}
SAY = {"1등": "일등", "6~8킬로그램": "육에서 팔 킬로그램", "1킬로그램": "일 킬로그램", "1999년": "천구백구십구 년",
       "7%": "칠 퍼센트", "18%": "십팔 퍼센트", "2,000년": "이천 년", "벌은 계산기": "벌은, 계산기"}
CX = W / 2
AMBER_HI, AMBER_LO, RIM = (255, 206, 92), (110, 58, 8), (255, 226, 150)
SKY = (120, 200, 255)


# ── 고급 육각 셀 (유리 같은 호박색 + 금빛 테두리 + 광택) ─────────────────────
def hexpts(cx, cy, r, rot=math.pi / 6):
    return [(cx + r * math.cos(rot + i * math.pi / 3), cy + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]


@lru_cache(maxsize=16)
def cell(r, tint="amber"):
    k = 3
    s = int(r * 2.2) * k
    c = s / 2
    R = r * k
    # 안쪽 그라데이션 (가운데 밝고 가장자리 어둡게)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((xx - c + R * 0.25) ** 2 + (yy - c + R * 0.3) ** 2) / (R * 1.25)
    d = np.clip(d, 0, 1)[..., None]
    hi, lo = (np.array(AMBER_HI), np.array(AMBER_LO)) if tint == "amber" else (np.array((150, 210, 255)), np.array((14, 40, 90)))
    rgb = (hi * (1 - d) ** 1.4 + lo * (1 - (1 - d) ** 1.4)).astype(np.uint8)
    im = Image.fromarray(np.dstack([rgb, np.full((s, s), 255, np.uint8)]), "RGBA")
    mk = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mk).polygon(hexpts(c, c, R * 0.9), fill=255)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(im, (0, 0), mk)
    dr = ImageDraw.Draw(out)
    rim = RIM if tint == "amber" else (190, 230, 255)
    dr.line(hexpts(c, c, R * 0.92) + [hexpts(c, c, R * 0.92)[0]], fill=rim + (255,), width=int(R * 0.07), joint="curve")
    # 광택: 위쪽 반달 하이라이트
    gl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((c - R * 0.6, c - R * 0.85, c + R * 0.35, c - R * 0.15), fill=(255, 255, 255, 70))
    gl = gl.filter(ImageFilter.GaussianBlur(R * 0.12))
    gm = Image.new("L", (s, s), 0)
    ImageDraw.Draw(gm).polygon(hexpts(c, c, R * 0.86), fill=255)
    out.alpha_composite(Image.composite(gl, Image.new("RGBA", (s, s), (0, 0, 0, 0)), gm))
    return out.resize((s // k, s // k), Image.LANCZOS)


@lru_cache(maxsize=4)
def comb_layout(r, w=W, h=H):
    dx, dy = r * math.sqrt(3), r * 1.5
    pts = []
    for row in range(-2, int(h / dy) + 3):
        for col in range(-2, int(w / dx) + 3):
            x = col * dx + (dx / 2 if row % 2 else 0)
            y = row * dy
            pts.append((x, y))
    cx, cy = w / 2, h * 0.42
    pts.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
    return tuple(pts)


def comb(f, t, r=92, grow=1.6, center=(0.5, 0.42), tint="amber", dim=0.0, sweep=True):
    """가운데서 바깥으로 셀이 '톡톡' 자라나는 벌집 + 빛줄기"""
    pts = comb_layout(r)
    cx, cy = W * center[0], H * center[1]
    far = math.hypot(W, H) * 0.6
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (x, y) in pts:
        dd = math.hypot(x - cx, y - cy) / far
        k = G.clamp((t - dd * grow) / 0.35)
        if k <= 0:
            continue
        k = 1 - (1 - k) ** 3
        sc = 0.35 + 0.65 * k
        cl = cell(int(r * sc), tint)
        G.blit(layer, cl, (x, y), min(1, k * 1.4), "mm")
    if sweep:  # 대각선 빛줄기가 지나감
        ph = (t * 0.45) % 1.6 - 0.3
        sw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x0 = ph * (W + H)
        ImageDraw.Draw(sw).polygon([(x0 - 260, 0), (x0, 0), (x0 - H * 0.6, H), (x0 - H * 0.6 - 260, H)], fill=(255, 240, 200, 46))
        sw = sw.filter(ImageFilter.GaussianBlur(50))
        a = np.minimum(np.asarray(sw.getchannel("A")), np.asarray(layer.getchannel("A")))
        sw.putalpha(Image.fromarray(a))
        layer.alpha_composite(sw)
    if dim:
        layer.putalpha(Image.fromarray((np.asarray(layer.getchannel("A")) * (1 - dim)).astype(np.uint8)))
    glow = layer.filter(ImageFilter.GaussianBlur(28))
    f.alpha_composite(glow)
    f.alpha_composite(layer)


def vignette(f, top=0.0, strength=0.75):
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(v)
    for i in range(40):
        a = int(255 * strength * (i / 40) ** 2.2)
        d.rectangle((i * 14, i * 22, W - i * 14, H - i * 22), outline=(4, 5, 10, 255 - a), width=24)
    f.alpha_composite(v.filter(ImageFilter.GaussianBlur(40)))


def big_q(f, t, y=820, size=170, o=1.0):
    q = T("벌집은 왜\n육각형일까?", size, CREAM, "Black", highlight="육각형", hl_fill=GOLD, align="center", line_gap=1.06,
          stroke=10, stroke_fill=(8, 6, 4))
    K.drop(f, q, (CX, y), "mm", o, blur=30, alpha=0.8)


# ── 장면 ─────────────────────────────────────────────────────────
def s_hook(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 5, 4, 255)))
    comb(f, t + 0.7, r=96, grow=1.4)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(dark).rectangle((0, 520, W, 1140), fill=(6, 5, 4, 150))
    f.alpha_composite(dark.filter(ImageFilter.GaussianBlur(60)))
    k = G.ease_out(G.clamp(t / 0.35))
    big_q(f, t, y=830 - (1 - k) * 20, size=int(158 + 12 * k), o=1.0)


def tiles(kind, w, h, s, k, col):
    sc = 2
    im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cells = []
    if kind == "tri":
        hh = s * math.sqrt(3) / 2
        for r in range(int(h / hh) + 2):
            for c in range(int(w / (s / 2)) + 3):
                x, y = c * s / 2 - s / 2, r * hh
                cells.append([(x, y + hh), (x + s / 2, y), (x + s, y + hh)] if (c + r) % 2 == 0 else [(x, y), (x + s, y), (x + s / 2, y + hh)])
    elif kind == "sq":
        for r in range(int(h / s) + 2):
            for c in range(int(w / s) + 2):
                x, y = c * s, r * s
                cells.append([(x, y), (x + s, y), (x + s, y + s), (x, y + s)])
    else:
        R = s / 2
        dx, dy = R * math.sqrt(3), R * 1.5
        for r in range(int(h / dy) + 2):
            for c in range(int(w / dx) + 2):
                cells.append(hexpts(c * dx + (dx / 2 if r % 2 else 0), r * dy, R))
    cells.sort(key=lambda p: math.hypot(sum(q[0] for q in p) / len(p) - w / 2, sum(q[1] for q in p) / len(p) - h / 2))
    m = int(len(cells) * k)
    for i, p in enumerate(cells[:m]):
        pp = [(a * sc, b * sc) for a, b in p]
        d.polygon(pp, fill=col + (60,))
        d.line(pp + [pp[0]], fill=col + (255,), width=3 * sc)
    im = im.resize((w, h), Image.LANCZOS)
    glow = im.filter(ImageFilter.GaussianBlur(8))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(im)
    mk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, w - 1, h - 1), radius=30, fill=255)
    out.putalpha(Image.fromarray(np.minimum(np.asarray(out.getchannel("A")), np.asarray(mk))))
    return out


def s_tiles(f, t, sc):
    L = sc["L"]
    w, h = 300, 400
    G.blit(f, T("빈틈없이 채우는 정다각형", 50, CREAM, "Black"), (CX, 420), 1, "mt")
    for i, (kind, col, lab) in enumerate([("tri", CORAL, "삼각형"), ("sq", SKY, "사각형"), ("hex", GOLD, "육각형")]):
        x = 60 + i * 330
        k = G.ease_out(G.clamp((t - L[-1] + 0.1 - i * 0.55) / 0.7))
        card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(card).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=(18, 20, 30, 230), outline=(60, 64, 84, 255), width=2)
        f.alpha_composite(card, (x, 540))
        if k > 0:
            f.alpha_composite(tiles(kind, w, h, 92, max(k, 0.02), col), (x, 540))
        G.blit(f, T(lab, 48, col, "Black"), (x + w / 2, 975), G.appear(t, L[-1] + i * 0.55, 0.25), "mt")


def s_wall(f, t, sc):
    """벽 쌓기 경주: 넓이가 같은 세 방의 벽을 같은 속도로 쌓으면 육각형이 1등 (둘레 4.56 · 4.00 · 3.72)"""
    G.blit(f, T("같은 넓이 방, 벽 쌓기 경주!", 54, CREAM, "Black"), (CX, 420), 1, "mt")
    rows = [(3, CORAL, "삼각형", 4.559, -math.pi / 2), (4, SKY, "사각형", 4.000, math.pi / 4), (6, GOLD, "육각형", 3.722, 0.0)]
    t0 = 0.5
    speed = 3.722 / 3.0          # 육각형이 3초에 완성
    fin = sorted(rows, key=lambda r: r[3])
    for i, (n, col, lab, per, rot) in enumerate(rows):
        cx, cy = 190 + i * 350, 800
        Rn = 178 * math.sqrt(2 / (n * math.sin(2 * math.pi / n)))  # 넓이가 같은 정다각형의 외접원 반지름 (비례)
        pts = [(cx + Rn * math.cos(rot + 2 * math.pi * q / n), cy + Rn * math.sin(rot + 2 * math.pi * q / n)) for q in range(n)] 
        p = G.clamp((t - t0) * speed / per)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.polygon(pts, fill=col + (int(40 + 60 * (p >= 1)),))
        d.line(pts + [pts[0]], fill=(80, 84, 104, 255), width=6)
        # 지금까지 쌓은 벽(밝게) + 벽돌 쌓는 점
        segs = [(pts[q], pts[(q + 1) % n]) for q in range(n)]
        rem = p * n
        path = [pts[0]]
        for q, (a, b) in enumerate(segs):
            u = G.clamp(rem - q)
            if u <= 0:
                break
            path.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
        if len(path) > 1:
            d.line(path, fill=col + (255,), width=12, joint="curve")
            if p < 1:
                x, y = path[-1]
                d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(255, 255, 255, 255))
        f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(10)))
        f.alpha_composite(ov)
        G.blit(f, T(lab, 48, col, "Black"), (cx, 1010), 1, "mt")
        if p >= 1:
            rank = [r[2] for r in fin].index(lab) + 1
            o = G.appear(t, t0 + per / speed, 0.25)
            badge = G.pill(f"{rank}등", "Black", 48 if rank == 1 else 38, (12, 10, 6), GOLD if rank == 1 else (200, 204, 214), pad=(22, 8))
            K.drop(f, badge, (cx, cy - (1 - o) * 20), "mm", o, blur=12)
    o = G.appear(t, t0 + 4.559 / speed + 0.2, 0.3)
    G.blit(f, T("벽이 덜 든다 = 재료를 아낀다", 48, CREAM, "Black"), (CX, 1110), o, "mt")
    G.blit(f, T("넓이가 같을 때 둘레 · 사각형보다 7%, 삼각형보다 18% 짧음", 26, DIM, "SemiBold"), (CX, 1185), o, "mt")


def s_wax(f, t, sc):
    K.pband(f, "bee_comb_bartz", t, sc["dur"], 380, 880, move={"zoom": 0.2, "dx": -0.03, "dy": 0.01}, focus=(0.5, 0.35), dark=0.3)
    o = G.appear(t, 0.35, 0.25)
    p = G.pill("벽 = 밀랍", "Black", 92, (12, 10, 6), GOLD, pad=(40, 16))
    K.drop(f, p, (CX, 1080 - (1 - o) * 30), "mm", o, blur=18)
    K.credit(f, K.credit_of("bee_comb_bartz"))


def jar(h=210, fill=0.0):
    """꿀단지 아이콘 (그림) — fill: 채워진 비율"""
    k = 3
    w_, h_ = int(h * 0.82) * k, h * k
    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (w_ * 0.08, h_ * 0.22, w_ * 0.92, h_ * 0.98)
    d.rounded_rectangle(body, radius=w_ * 0.22, fill=(40, 30, 16, 230), outline=RIM + (255,), width=4 * k)
    if fill > 0:
        top = body[3] - (body[3] - body[1]) * fill
        mk = Image.new("L", (w_, h_), 0)
        ImageDraw.Draw(mk).rounded_rectangle(body, radius=w_ * 0.22, fill=255)
        hn = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
        ImageDraw.Draw(hn).rectangle((0, top, w_, h_), fill=AMBER_HI + (255,))
        im.alpha_composite(Image.composite(hn, Image.new("RGBA", (w_, h_), (0, 0, 0, 0)), mk))
        d.rounded_rectangle(body, radius=w_ * 0.22, outline=RIM + (255,), width=4 * k)
    d.rounded_rectangle((w_ * 0.2, h_ * 0.04, w_ * 0.8, h_ * 0.2), radius=10 * k, fill=(190, 120, 40, 255))
    return im.resize((w_ // k, h_ // k), Image.LANCZOS)


def s_honey(f, t, sc):
    """밀랍 1kg 저울 → 꿀단지 8개가 차례로 떨어지며 차오름 + 카운터"""
    L = sc["L"]
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 6, 255)))
    comb(f, t + 3, r=70, grow=0.1, center=(0.5, 0.5), dim=0.8, sweep=False)
    G.blit(f, T("밀랍 1kg 만들려면", 60, CREAM, "Black"), (CX, 430), G.appear(t, 0.0, 0.2), "mt")
    t1 = L[-1] if len(L) > 1 else 0.6
    n = 8
    for i in range(n):
        k = G.ease_out(G.clamp((t - t1 - i * 0.16) / 0.3))
        if k <= 0:
            continue
        x = 150 + (i % 4) * 260
        y = 640 + (i // 4) * 270
        G.blit(f, jar(200, min(1, k * 1.1)), (x, y - (1 - k) * 160), min(1, k * 1.5), "mt")
    kk = G.clamp((t - t1) / (0.16 * n + 0.3))
    num = T("꿀 6~8kg" if kk >= 1 else f"꿀 {8 * kk:.0f}kg", 120, GOLD, "Black", stroke=8, stroke_fill=(8, 6, 4))
    K.drop(f, num, (CX, 1210), "mb", G.appear(t, t1, 0.2), blur=18)
    G.blit(f, T("양봉 문헌 · 약 6~8kg", 26, DIM, "SemiBold"), (W - 70, 1240), 1, "rb")


def s_proof(f, t, sc):
    """기원전 36년 → 1999년: 연도가 빠르게 굴러가는 카운터"""
    L = sc["L"]
    f.alpha_composite(Image.new("RGBA", (W, H), (8, 7, 5, 255)))
    comb(f, t + 3, r=70, grow=0.1, center=(0.5, 0.5), dim=0.72, sweep=True)
    G.blit(f, T("2,000년 넘은 수수께끼", 54, DIM, "ExtraBold"), (CX, 470), 1, "mt")
    t1 = L[-1] if len(L) > 1 else 0.8
    k = G.clamp((t - 0.2) / max(0.4, t1 - 0.1))
    k = k ** 2.2
    yr = int(-36 + (1999 + 36) * k)
    label = f"기원전 {-yr}년" if yr < 0 else f"{max(yr, 1)}년"
    col = GOLD if k >= 1 else CREAM
    sz = 170 if k >= 1 else 130
    K.drop(f, T(label, sz, col, "Black", stroke=8, stroke_fill=(8, 6, 4)), (CX, 820), "mm", 1, blur=24)
    if k >= 1:
        o = G.appear(t, t1 + 0.1, 0.25)
        G.blit(f, G.pill("수학자 토머스 헤일스, 드디어 증명", "Black", 46, (12, 10, 6), GOLD, pad=(26, 12)), (CX, 980), o, "mt")


def s_bee(f, t, sc):
    K.pband(f, "honeycomb_drip", t, sc["dur"], 380, 880, move={"zoom": 0.22, "dx": 0.0, "dy": -0.03}, focus=(0.4, 0.3), dark=0.35)
    o = G.appear(t, 0.3, 0.3)
    K.drop(f, T("가장 적은 밀랍으로\n가장 많은 꿀을", 84, CREAM, "Black", highlight="가장 많은 꿀", hl_fill=GOLD,
                align="center", line_gap=1.16, stroke=6, stroke_fill=(8, 6, 4)), (CX, 830), "mm", o, blur=24)
    K.credit(f, K.credit_of("honeycomb_drip"))


def s_share(f, t, sc):
    L = sc["L"]
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 5, 4, 255)))
    comb(f, t + 3, r=96, grow=0.1, dim=0.6, sweep=True)
    if t < L[-1] - 0.05:
        k = G.ease_out(G.clamp(t / 0.3))
        K.drop(f, T("친구한테\n물어보세요", 150, CREAM, "Black", highlight="물어보세요", hl_fill=GOLD, align="center",
                    line_gap=1.08, stroke=8, stroke_fill=(8, 6, 4)), (CX, 830), "mm", 1, blur=24)
        q = G.pill("벌집은 왜 육각형?", "Black", 54, (12, 10, 6), CREAM, pad=(30, 12))
        G.blit(f, q, (CX, 1060 + (1 - k) * 30), k, "mt")
    else:
        k = G.ease_out(G.clamp((t - L[-1] + 0.05) / 0.3))
        K.drop(f, T("구독하고\n함께해요!", 150, GOLD, "Black", align="center", line_gap=1.08, stroke=8, stroke_fill=(8, 6, 4)),
               (CX, 830 - (1 - k) * 30), "mm", k, blur=24)


def s_loop(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 5, 4, 255)))
    comb(f, t + 3, r=96, grow=0.1, dim=0.35, sweep=True)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(dark).rectangle((0, 520, W, 1140), fill=(6, 5, 4, 150))
    f.alpha_composite(dark.filter(ImageFilter.GaussianBlur(60)))
    k = G.ease_out(G.clamp(t / 0.3))
    big_q(f, t, y=830, size=int(158 + 12 * k), o=1.0)


def draw_cover(f):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 5, 4, 255)))
    comb(f, 4.0, r=110, grow=0.1, dim=0.25)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(dark).rectangle((0, 560, W, 1180), fill=(6, 5, 4, 170))
    f.alpha_composite(dark.filter(ImageFilter.GaussianBlur(60)))
    big_q(f, 0, y=870, size=175)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.4, "gap": 0.15, "tail": 0.2,
     "narr": ["벌집은 왜 / 하필 육각형일까요?"]},
    {"draw": s_tiles, "flash": True, "min": 3.0, "gap": 0.3, "tail": 0.3,
     "narr": ["빈틈없이 바닥을 채우는 정다각형은,", "삼각형 / 사각형 / 육각형. / 딱 / 셋뿐."]},
    {"draw": s_wall, "flash": True, "min": 5.0, "gap": 0.2, "tail": 0.3,
     "narr": ["같은 넓이의 방을, 세 모양으로 지어 볼게요.", "벽을 같은 속도로 쌓으면? / 1등은 육각형."]},
    {"draw": s_wax, "flash": True, "min": 1.6, "gap": 0.15, "tail": 0.1,
     "narr": ["그런데 벌한테 벽은 밀랍이에요."]},
    {"draw": s_honey, "flash": True, "min": 3.0, "gap": 0.15, "tail": 0.3,
     "narr": ["밀랍 1킬로그램을 만들려면,", "꿀을 6~8킬로그램이나 먹어야 하죠."]},
    {"draw": s_proof, "flash": True, "min": 2.6, "gap": 0.15, "tail": 0.3,
     "narr": ["이게 최선이라는 증명은,", "겨우 1999년에야 나왔어요."]},
    {"draw": s_bee, "flash": True, "min": 2.4, "gap": 0.15, "tail": 0.2,
     "narr": ["벌은 계산기 없이, 가장 적은 밀랍으로 가장 많은 꿀을 담은 거예요."]},
    {"draw": s_share, "flash": True, "nohead": True, "min": 2.4, "gap": 0.15, "tail": 0.15,
     "narr": ["친구한테도 물어보세요.", K.CTA]},
    {"draw": s_loop, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.15,
     "narr": ["벌집은 왜 / 하필 육각형일까요?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
