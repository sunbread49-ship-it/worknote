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
SAY = {"__rate__": 1.12, "6~8킬로그램": "육에서 팔 킬로그램", "1킬로그램": "일 킬로그램", "1999년": "천구백구십구 년",
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
        k = G.ease_out(G.clamp((t - L[0] - 0.4 - i * 0.45) / 0.9))
        card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(card).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=(18, 20, 30, 230), outline=(60, 64, 84, 255), width=2)
        f.alpha_composite(card, (x, 540))
        if k > 0:
            f.alpha_composite(tiles(kind, w, h, 92, max(k, 0.02), col), (x, 540))
        G.blit(f, T(lab, 48, col, "Black"), (x + w / 2, 975), G.appear(t, L[0] + 0.4 + i * 0.45, 0.3), "mt")


def s_wall(f, t, sc):
    L = sc["L"]
    G.blit(f, T("같은 넓이, 벽 길이는?", 54, CREAM, "Black"), (CX, 420), 1, "mt")
    rows = [(CORAL, "삼각형", 4.559), (SKY, "사각형", 4.000), (GOLD, "육각형", 3.722)]
    y = 560
    for i, (col, lab, v) in enumerate(rows):
        k = G.ease_out(G.clamp((t - 0.2 - i * 0.35) / 0.7))
        G.blit(f, T(lab, 44, col, "Black"), (90, y + 6), 1, "lt")
        bw = int(560 * v / 4.6 * k)
        if bw > 4:
            bar = Image.new("RGBA", (bw, 54), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bar)
            for xx in range(bw):
                c = tuple(int(cc * (0.55 + 0.45 * xx / max(bw, 1))) for cc in col)
                bd.line((xx, 0, xx, 54), fill=c + (255,))
            mk = Image.new("L", bar.size, 0)
            ImageDraw.Draw(mk).rounded_rectangle((0, 0, bw - 1, 53), 27, fill=255)
            bar.putalpha(mk)
            f.alpha_composite(bar.filter(ImageFilter.GaussianBlur(12)), (300, y + 2))
            f.alpha_composite(bar, (300, y + 2))
        G.blit(f, T(f"{v * k:.2f}", 50, CREAM, "Black"), (316 + bw, y), min(1, k * 2), "lt")
        y += 150
    o = G.appear(t, L[-1] + 0.1, 0.3)
    p = G.pill("육각형이 가장 짧다", "Black", 56, (12, 10, 6), GOLD, pad=(32, 14))
    K.drop(f, p, (CX, 1060 + (1 - o) * 20), "mt", o, blur=16)
    G.blit(f, T("넓이 1 기준 둘레", 26, DIM, "SemiBold"), (W - 70, 1240), 1, "rb")


def s_wax(f, t, sc):
    K.pband(f, "bee_comb_bartz", t, sc["dur"], 380, 880, move={"zoom": 0.14, "dx": -0.02, "dy": 0.01}, focus=(0.5, 0.35), dark=0.4)
    o = G.appear(t, sc["L"][-1], 0.3)
    card = Image.new("RGBA", (840, 240), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, 839, 239), 30, fill=(12, 10, 6, 225), outline=GOLD + (255,), width=3)
    card.alpha_composite(T("밀랍 1kg", 72, CREAM, "Black"), (54, 34))
    card.alpha_composite(T("= 꿀 6~8kg", 72, GOLD, "Black"), (54, 126))
    K.drop(f, card, (CX, 1060 - (1 - o) * 30), "mm", o, blur=16)
    K.credit(f, K.credit_of("bee_comb_bartz"))


def s_proof(f, t, sc):
    comb(f, t + 3, r=70, grow=0.1, center=(0.5, 0.5), dim=0.72, sweep=True)
    o = G.appear(t, 0.1, 0.3)
    G.blit(f, T("2,000년 넘은 수수께끼", 52, DIM, "ExtraBold"), (CX, 560), o, "mt")
    k = G.appear(t, sc["L"][-1] + 1.2, 0.35)
    K.drop(f, T("1999년", 190, GOLD, "Black", stroke=8, stroke_fill=(8, 6, 4)), (CX, 820 - (1 - k) * 30), "mm", k, blur=24)
    G.blit(f, T("수학자 토머스 헤일스, 증명", 48, CREAM, "Black"), (CX, 960), k, "mt")


def s_end(f, t, sc):
    L = sc["L"]
    comb(f, t + 3, r=96, grow=0.1, dim=0.55, sweep=True)
    o = G.appear(t, 0.1, 0.35)
    if t < L[-1] - 0.1:
        K.drop(f, T("가장 적은 밀랍으로\n가장 많은 꿀을", 84, CREAM, "Black", highlight="가장 많은 꿀", hl_fill=GOLD,
                    align="center", line_gap=1.16, stroke=6, stroke_fill=(8, 6, 4)), (CX, 820), "mm", o, blur=24)
    else:  # 마지막 문장 = 첫 질문 → 처음으로 이어지는 루프
        k = G.ease_out(G.clamp((t - L[-1] + 0.1) / 0.35))
        big_q(f, t, y=830, size=150, o=k)


def draw_cover(f):
    f.alpha_composite(Image.new("RGBA", (W, H), (6, 5, 4, 255)))
    comb(f, 4.0, r=110, grow=0.1, dim=0.25)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(dark).rectangle((0, 560, W, 1180), fill=(6, 5, 4, 170))
    f.alpha_composite(dark.filter(ImageFilter.GaussianBlur(60)))
    big_q(f, 0, y=870, size=175)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.6, "gap": 0.15, "tail": 0.25,
     "narr": ["벌집은 왜, 하필 육각형일까요?"]},
    {"draw": s_tiles, "min": 3.0, "gap": 0.2, "tail": 0.2,
     "narr": ["빈틈없이 바닥을 채우는 정다각형은, 삼각형, 사각형, 육각형. 딱 셋뿐."]},
    {"draw": s_wall, "min": 3.0, "gap": 0.2, "tail": 0.25,
     "narr": ["그중 같은 넓이에 벽이 가장 짧은 게 육각형. 사각형보다 7%, 삼각형보다 18%나 짧아요."]},
    {"draw": s_wax, "min": 3.0, "gap": 0.2, "tail": 0.2,
     "narr": ["벌한테 벽은 밀랍인데, 밀랍 1킬로그램에 꿀이 6~8킬로그램이나 들어요.", "벽이 짧을수록 꿀을 아끼는 거죠."]},
    {"draw": s_proof, "min": 2.6, "gap": 0.2, "tail": 0.2,
     "narr": ["이게 최선이라는 증명은, 겨우 1999년에야 나왔죠."]},
    {"draw": s_end, "nohead": True, "min": 3.0, "gap": 0.2, "tail": 0.15,
     "narr": ["벌은 계산기 없이, 가장 적은 밀랍으로 가장 많은 꿀을 담은 거예요.",
              "친구한테도 물어보세요.", K.CTA, "벌집은 왜, 하필 육각형일까요?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
