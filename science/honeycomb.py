"""지식창고 쇼츠 #5 · 왜 벌집은 삼각형, 사각형이 아니라 육각형일까? (벌집 추측)
  python3 science/honeycomb.py [--stills]
숫자: 넓이 1을 만드는 둘레 — 정삼각형 4.559 · 정사각형 4.000 · 정육각형 3.722 (사각형보다 약 7%, 삼각형보다 약 18% 짧음)
      평면을 빈틈없이 채우는 정다각형은 정삼각형 · 정사각형 · 정육각형 3가지뿐
      밀랍 1kg ← 꿀 약 6~8kg (양봉 문헌에서 흔히 인용되는 범위)
      벌집 추측: 기원전 36년 바로(Varro) 언급 · 서기 4세기 파푸스 · 1999년 토머스 헤일스 증명
사진: 위키미디어 공용(CC BY-SA) — 깊이감(2.5D) 카메라 이동 (engine/depth.py)
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, CREAM, DIM, CORAL, BLUE, MINT, GOLD

OUT = K.HERE / "out" / "honeycomb"
HEAD = {"kicker": "자연의 수학", "title": "벌집은 왜\n육각형일까?", "highlight": "육각형"}
SAY = {"6~8킬로그램": "육에서 팔 킬로그램", "1킬로그램": "일 킬로그램", "기원전 36년": "기원전 삼십육 년",
       "1999년": "천구백구십구 년", "7%": "칠 퍼센트", "18%": "십팔 퍼센트", "2,000년": "이천 년", "벌은 계산기": "벌은, 계산기"}
CX = W / 2
HONEY = (255, 196, 60)


def poly(n, r, rot=0.0):
    return [(r * math.cos(rot + 2 * math.pi * i / n), r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def tile_layer(kind, w, h, s, k=1.0, col=HONEY):
    """빈틈없이 채운 타일 (k: 채워진 비율, 위에서부터)"""
    sc = 2
    im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cells = []
    if kind == "tri":
        hh = s * math.sqrt(3) / 2
        for r in range(int(h / hh) + 2):
            for c in range(int(w / (s / 2)) + 3):
                x, y = c * s / 2 - s / 2, r * hh
                up = (c + r) % 2 == 0
                pts = [(x, y + hh), (x + s / 2, y), (x + s, y + hh)] if up else [(x, y), (x + s, y), (x + s / 2, y + hh)]
                cells.append(pts)
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
                x = c * dx + (dx / 2 if r % 2 else 0)
                y = r * dy
                cells.append([(x + px, y + py) for px, py in poly(6, R, math.pi / 6)])
    cells.sort(key=lambda p: (sum(q[1] for q in p), sum(q[0] for q in p)))
    m = int(len(cells) * k)
    for i, p in enumerate(cells[:m]):
        sh = 0.82 + 0.18 * ((i * 37) % 11) / 10
        fill = tuple(int(c * sh) for c in col) + (255,)
        d.polygon([(a * sc, b * sc) for a, b in p], fill=fill, outline=(70, 46, 10, 255))
        d.line([(a * sc, b * sc) for a, b in p] + [(p[0][0] * sc, p[0][1] * sc)], fill=(120, 80, 20, 255), width=3 * sc)
    im = im.resize((w, h), Image.LANCZOS)
    hl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((-w * 0.2, -h * 0.4, w * 0.8, h * 0.5), fill=(255, 255, 255, 40))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(40)))
    mk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=255)
    a = im.getchannel("A")
    im.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").array(a), __import__("numpy").array(mk))))
    return im


def shape_icon(n, r, col, rot=None):
    sc = 3
    im = Image.new("RGBA", (int(r * 2.4) * sc, int(r * 2.4) * sc), (0, 0, 0, 0))
    c = r * 1.2 * sc
    rot = (-math.pi / 2 if n == 3 else (math.pi / 4 if n == 4 else math.pi / 6)) if rot is None else rot
    pts = [(c + x * sc, c + y * sc) for x, y in poly(n, r, rot)] if n else None
    d = ImageDraw.Draw(im)
    if n:
        d.polygon(pts, fill=col + (255,), outline=(255, 255, 255, 255))
        d.line(pts + [pts[0]], fill=(255, 255, 255, 230), width=5 * sc)
    else:
        d.ellipse((c - r * sc, c - r * sc, c + r * sc, c + r * sc), fill=col + (255,), outline=(255, 255, 255, 255), width=5 * sc)
    return im.resize((im.width // sc, im.height // sc), Image.LANCZOS)


# ── 장면 ─────────────────────────────────────────────────────────
def s_hook(f, t, sc):
    K.pband(f, "bee_comb_rader", t, sc["dur"], 380, 880, move={"zoom": 0.16, "dx": 0.02, "dy": -0.01}, focus=(0.45, 0.5), dark=0.25)
    o = G.appear(t, sc["L"][0] + 0.6, 0.3)
    for i, (n, col) in enumerate([(3, CORAL), (4, BLUE), (6, GOLD)]):
        oi = G.appear(t, sc["L"][0] + 0.5 + i * 0.25, 0.25)
        ic = shape_icon(n, 70, col)
        K.drop(f, ic, (CX - 260 + i * 260, 1100 - (1 - oi) * 30), "mm", oi, blur=12)
    G.blit(f, T("?", 220, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (CX + 360, 760), o, "mm")
    K.credit(f, K.credit_of("bee_comb_rader"))


def s_tiles(f, t, sc):
    L = sc["L"]
    w, h = 300, 420
    for i, (kind, col, lab) in enumerate([("tri", CORAL, "정삼각형"), ("sq", BLUE, "정사각형"), ("hex", HONEY, "정육각형")]):
        x = 60 + i * 330
        k = G.clamp((t - L[-1] - i * 0.35) / 0.8) if len(L) > 1 else 1
        if t < (L[1] if len(L) > 1 else 0):
            k = 0.0
        tl = tile_layer(kind, w, h, 92, max(k, 0.02), col)
        K.drop(f, tl, (x, 560), "lt", 1, blur=14)
        G.blit(f, T(lab, 44, CREAM, "Black"), (x + w / 2, 1010), G.appear(t, (L[1] if len(L) > 1 else 0) + i * 0.35, 0.3), "mt")
    # 오각형은 안 맞음
    o = G.appear(t, L[0] + 0.3, 0.3) * (1 - G.appear(t, L[1] if len(L) > 1 else 99, 0.3))
    if o > 0:
        for j in range(3):
            G.blit(f, shape_icon(5, 90, (150, 150, 170)), (CX - 200 + j * 160, 760 + (j % 2) * 90), o, "mm")
        G.blit(f, G.pill("정오각형 → 빈틈 생김", "Black", 46, (10, 12, 20), CORAL, pad=(24, 10)), (CX, 470), o, "mt")
    G.blit(f, T("빈틈없이 채울 수 있는 정다각형", 40, DIM, "ExtraBold"), (CX, 440), G.appear(t, L[1] if len(L) > 1 else 0, 0.3), "mt")


def s_wall(f, t, sc):
    L = sc["L"]
    G.blit(f, T("같은 넓이를 만드는 벽 길이", 46, CREAM, "Black"), (CX, 440), 1, "mt")
    rows = [(3, CORAL, "정삼각형", 4.559), (4, BLUE, "정사각형", 4.000), (6, GOLD, "정육각형", 3.722)]
    y = 560
    for i, (n, col, lab, v) in enumerate(rows):
        k = G.ease_out(G.clamp((t - 0.3 - i * 0.45) / 0.7))
        G.blit(f, shape_icon(n, 52, col), (140, y + 40), 1, "mm")
        G.blit(f, T(lab, 38, CREAM, "ExtraBold"), (220, y - 4), 1, "lt")
        bw = int(620 * v / 4.6 * k)
        if bw > 4:
            bar = Image.new("RGBA", (bw, 46), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bar)
            for yy in range(46):
                c = tuple(min(255, int(cc * (1.15 - yy / 46 * 0.45))) for cc in col)
                bd.line((0, yy, bw, yy), fill=c + (255,))
            K.drop(f, bar, (220, y + 48), "lt", 1, blur=8, alpha=0.5)
        G.blit(f, T(f"{v * k:.2f}", 46, col, "Black"), (230 + bw, y + 46), min(1, k * 2), "lt")
        y += 170
    o = G.appear(t, L[-1] + 0.2, 0.3)
    G.blit(f, G.pill("육각형: 사각형보다 7% · 삼각형보다 18% 짧다", "Black", 38, (10, 12, 20), GOLD, pad=(22, 10)), (CX, 1110), o, "mt")
    G.blit(f, T("넓이 1 기준 둘레", 24, DIM, "SemiBold"), (W - 80, 1250), 1, "rb")


def s_wax(f, t, sc):
    K.pband(f, "bee_comb_bartz", t, sc["dur"], 380, 880, move={"zoom": 0.14, "dx": -0.02, "dy": 0.01}, focus=(0.5, 0.35), dark=0.35)
    o = G.appear(t, sc["L"][-1], 0.3)
    card = Image.new("RGBA", (820, 250), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, 819, 249), 28, fill=(14, 16, 26, 225), outline=GOLD + (255,), width=3)
    card.alpha_composite(T("밀랍 1kg", 70, CREAM, "Black"), (50, 40))
    card.alpha_composite(T("= 꿀 약 6~8kg", 70, GOLD, "Black"), (50, 130))
    K.drop(f, card, (CX, 1080 - (1 - o) * 30), "mm", o, blur=16)
    K.credit(f, K.credit_of("bee_comb_bartz"))


def s_history(f, t, sc):
    L = sc["L"]
    G.blit(f, T("2,000년 넘은 수수께끼", 54, CREAM, "Black"), (CX, 440), 1, "mt")
    items = [("기원전 36년", "로마의 바로", "벌집이 육각형인 건\n밀랍을 아끼려는 것?", 0),
             ("서기 300년경", "알렉산드리아의 파푸스", "벌은 기하학적\n선견지명이 있다", 0),
             ("1999년", "수학자 토머스 헤일스", "육각형이 최선임을\n증명", 1)]
    for i, (yr, who, txt, hl) in enumerate(items):
        y = 560 + i * 220
        on = L[min(i, len(L) - 1)] if i < 2 else L[-1]
        o = G.appear(t, on + (0.4 if i == 1 else 0.1), 0.3)
        col = GOLD if hl else DIM
        ImageDraw.Draw(f).ellipse((100, y + 10, 136, y + 46), fill=col + (int(255 * o),))
        if i < 2:
            ImageDraw.Draw(f).line((118, y + 50, 118, y + 220), fill=DIM + (int(160 * o),), width=4)
        G.blit(f, T(yr, 44, col, "Black"), (170, y), o, "lt")
        G.blit(f, T(who, 34, CREAM, "ExtraBold"), (170, y + 58), o, "lt")
        G.blit(f, T(txt, 34, DIM, "SemiBold", line_gap=1.2), (560, y + 4), o, "lt")


def s_end(f, t, sc):
    K.pband(f, "honeycomb_drip", t, sc["dur"], 380, 880, move={"zoom": 0.12, "dx": 0.0, "dy": -0.02}, focus=(0.4, 0.3), dark=0.4)
    o = G.appear(t, 0.4, 0.4)
    G.blit(f, T("가장 적은 밀랍으로\n가장 많은 꿀을", 74, CREAM, "Black", highlight="가장 많은 꿀", hl_fill=GOLD, align="center", line_gap=1.18,
                stroke=4, stroke_fill=(0, 0, 0)), (CX, 960), o, "mm")
    K.credit(f, K.credit_of("honeycomb_drip"))


def draw_cover(f):
    im = K.photo("bee_comb_rader", W, 1920, (0.45, 0.5), dark=0.45)
    f.alpha_composite(im)
    G.blit(f, T("자연의 수학", 64, MINT, "ExtraBold"), (W / 2, 200), 1, "mt")
    G.blit(f, T("벌집은 왜\n육각형일까?", 150, CREAM, "Black", highlight="육각형", hl_fill=GOLD, align="center", line_gap=1.08,
                stroke=8, stroke_fill=(0, 0, 0)), (W / 2, 300), 1, "mt")
    for i, (n, col) in enumerate([(3, CORAL), (4, BLUE), (6, GOLD)]):
        K.drop(f, shape_icon(n, 100, col), (W / 2 - 300 + i * 300, 1150), "mm")
    G.blit(f, T("?", 240, GOLD, "Black", stroke=10, stroke_fill=(0, 0, 0)), (W / 2, 1450), 1, "mm")


SCENES = [
    {"draw": s_hook, "min": 3.5, "narr": ["벌집은 왜 삼각형도, 사각형도 아닌, 육각형일까요?"]},
    {"draw": s_tiles, "min": 4.0, "narr": ["벽돌처럼 빈틈없이 바닥을 채우려면, 아무 모양이나 안 돼요. | 오각형만 해도 틈이 생기거든요.",
                                           "빈틈없이 채울 수 있는 정다각형은, | 정삼각형, 정사각형, 정육각형. 딱 세 가지뿐이에요."]},
    {"draw": s_wall, "min": 4.0, "narr": ["그런데 같은 넓이의 방을 만들 때, 벽 길이를 재 보면요,",
                                          "육각형이 가장 짧아요. | 사각형보다 7%, 삼각형보다 18%나 짧죠."]},
    {"draw": s_wax, "min": 3.5, "narr": ["벌한테 벽은 곧 밀랍인데요, | 밀랍 1킬로그램을 만들려면, 꿀을 6~8킬로그램이나 먹어야 해요.",
                                         "벽이 짧을수록, 아까운 꿀을 덜 쓰는 거죠."]},
    {"draw": s_history, "min": 4.0, "narr": ["이 사실은 2,000년 넘게 추측으로만 남아 있었어요. | 기원전 36년, 로마의 학자 바로가 처음 이야기했고,",
                                             "1999년, 수학자 토머스 헤일스가 마침내 증명했죠. | 평면을 같은 넓이로 나눌 때, 둘레가 가장 짧은 건 육각형이라고요."]},
    {"draw": s_end, "min": 3.0, "narr": ["벌은 계산기 없이도, 가장 적은 밀랍으로 가장 많은 꿀을 담는 답을 찾은 거예요.", K.CTA]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
