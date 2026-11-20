"""지식창고 쇼츠 · 겨울의 과학 ① 눈송이는 왜 전부 육각형일까? (2026-11-20 20:00)
  GEMINI_ONLY=gemini-2.5-pro-preview-tts python3 science/snowflake.py [--stills]
2026-11-20 정체 진단 반영: 30초 안팎 · 첫 1초 결과 화면(자라는 눈송이) · 둘 중 하나 댓글 질문 · 첫 장면으로 루프 · 시리즈 '겨울의 과학'
과학 (출처: Libbrecht 'Snowflake Science' (Caltech) · Wikipedia 'Ice Ih', 'Wilson Bentley', 'Snowflake'):
  물 분자 H2O = 산소 하나에 수소 둘, 104.5°로 꺾인 모양 (미키마우스 머리)
  얼 때 수소결합으로 이웃 4개와 손을 잡음 → 산소 6개가 고리(육각형)를 이루는 결정 (얼음 Ih) → 눈 결정의 씨앗은 육각기둥
  모서리(뾰족한 곳)가 주변 수증기에 더 많이 닿아 빨리 자람 → 여섯 팔 (가지 = 같은 원리 반복)
  여섯 팔은 같은 공기를 같이 지나므로 비슷하게 자람 · 눈송이마다 떨어진 경로(온도 · 습도)가 달라 서로 다름
  Wilson Bentley (미국 버몬트 농부): 1885년부터 눈 결정 사진 5천 장 넘게 촬영
  댓글 정답(고정 댓글): 1988년 Nancy Knight가 겉보기에 똑같은 단순 기둥 결정 한 쌍 발견 · 분자 배열까지 같을 확률은 사실상 0
"""
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM  # noqa: E402
from drone import vbg, big, pop  # noqa: E402

OUT = K.HERE / "out" / "snowflake"
HEAD = {"kicker": "겨울의 과학", "title": "눈송이", "highlight": "눈송이",
        "banner": ["겨울의 과학 ①", "눈송이는 왜 육각형?"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.2}}
CX = W / 2
ICE = (150, 220, 255)
YEL = (255, 214, 60)
RED = (240, 70, 70)
DARK = (8, 14, 30)


# ── 눈송이 그리기 (팔 6개 · 가지 · g=자란 정도 0~1) ─────────────────
def _arm(d, L, g, seed, w, col):
    rnd = np.random.default_rng(seed)
    n = 5
    spots = sorted(rnd.uniform(0.18, 0.85, n))
    lens = rnd.uniform(0.18, 0.42, n)
    ang = rnd.uniform(55, 62)
    tip = L * g
    d.line((0, 0, tip, 0), fill=col, width=w)
    for s, ln in zip(spots, lens):
        if tip <= s * L:
            continue
        bl = min(ln * L * (1 - s * 0.6), (tip - s * L) * 0.9)
        for sg in (1, -1):
            a = math.radians(ang) * sg
            x1, y1 = s * L + bl * math.cos(a), bl * math.sin(a)
            d.line((s * L, 0, x1, y1), fill=col, width=max(2, w - 3))
    if g > 0.05:   # 끝 작은 판
        r = w * 1.6
        d.regular_polygon((tip, 0, r), 6, fill=col)


@lru_cache(maxsize=256)
def flake(size, g, seed=7, col=(235, 248, 255, 255)):
    """g를 0.02 단위로 반올림해서 캐시"""
    S = size * 2
    arm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    da = ImageDraw.Draw(arm)
    # 팔 하나를 가운데에서 오른쪽으로 그린 뒤 60°씩 돌려 6개
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    w = max(4, size // 28)

    class _Off:
        def line(self, xy, **k):
            x0, y0, x1, y1 = xy
            dl.line((S / 2 + x0, S / 2 + y0, S / 2 + x1, S / 2 + y1), **k)

        def regular_polygon(self, c, n, **k):
            dl.regular_polygon((S / 2 + c[0], S / 2 + c[1], c[2]), n, **k)
    _arm(_Off(), size * 0.92, g, seed, w, col)
    for k in range(6):
        arm.alpha_composite(lay.rotate(60 * k, resample=Image.BICUBIC))
    core = min(1.0, g * 4) * size * 0.16
    if core > 2:
        da.regular_polygon((S / 2, S / 2, core), 6, fill=col, rotation=30)
    glow = arm.filter(ImageFilter.GaussianBlur(size // 18))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(glow)
    out.alpha_composite(arm)
    return out


def F(size, g, seed=7):
    return flake(size, round(min(1, max(0, g)) * 50) / 50, seed)


def dim(f, a=200):
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (a,)))


# ── 장면 ─────────────────────────────────────────────
def s_hook(f, t, sc):
    vbg(f, "snow_fall_v", t, 0.55, 2)
    g = 0.25 + 0.75 * G.ease_out(min(1, t / 1.8))
    im = F(260, g).rotate(t * 8, resample=Image.BICUBIC)
    G.blit(f, im, (CX, 540), 1, "mm")
    big(f, "왜 전부\n팔이 6개?", 60, 140, hl="6개", hlc=YEL, o=pop(t, 0.15))
    K.credit(f, "영상: MilanWulf (Pixabay)")


def s_bentley(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)))
    z = 1.0 + 0.08 * G.clamp(t / 4)
    im = K.photo("bentley_grid", int(640 * z), int(700 * z), (0.5, 0.0))
    G.blit(f, im, (CX, 40), pop(t, 0.0, 0.3), "mt")
    if t > 0.6:
        G.blit(f, G.pill("1885년 · 한 농부가 찍은 눈송이 5천 장", "Black", 46, DARK, CREAM, pad=(22, 10), radius=14), (CX, 70), pop(t, 0.6), "mt")
    L = sc["L"]
    t1 = L[1] if len(L) > 1 else 1.8
    if t > t1:
        G.blit(f, G.pill("전부 육각형", "Black", 92, (255, 255, 255), RED, pad=(30, 12), radius=18), (CX, 620), pop(t, t1), "mm")
    K.credit(f, "사진: Wilson Bentley (퍼블릭 도메인)")


def mickey(r):
    """물 분자 = 미키마우스 머리 (산소 큰 공 + 수소 귀 2개, 104.5°)"""
    S = int(r * 4)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    for a in (-52.25, 52.25):
        x, y = c + math.sin(math.radians(a)) * r * 1.15, c - math.cos(math.radians(a)) * r * 1.15
        d.ellipse((x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55), fill=(245, 245, 250, 255))
    d.ellipse((c - r, c - r, c + r, c + r), fill=(235, 70, 70, 255))
    return im


def s_molecule(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (255,)))
    big(f, "범인은 물 분자", 40, 100, hl="물 분자", hlc=ICE)
    L = sc["L"]
    t1 = L[1] if len(L) > 1 else 1.6
    cy = 400
    if t < t1:   # 분자 하나 크게 등장
        G.blit(f, mickey(90), (CX, cy), pop(t, 0.1), "mm")
        G.blit(f, T("산소", 46, CREAM, "Black"), (CX, cy + 150), pop(t, 0.4), "mt")
        G.blit(f, T("수소   수소", 40, CREAM, "Bold"), (CX, cy - 250), pop(t, 0.4), "mt")
    else:        # 6개가 손잡고 고리
        k = G.ease_out(G.clamp((t - t1) / 0.8))
        R = 180
        pts = []
        for i in range(6):
            a = math.radians(90 + i * 60)
            x0, y0 = CX + math.cos(a) * 520, cy + math.sin(a) * 520
            x1, y1 = CX + math.cos(a) * R, cy + math.sin(a) * R
            pts.append((x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, a))
        d = ImageDraw.Draw(f)
        if k > 0.9:
            for i in range(6):   # 손 (수소결합) — 점선
                xa, ya, _ = pts[i]; xb, yb, _ = pts[(i + 1) % 6]
                for s in np.linspace(0.25, 0.75, 6):
                    x, y = xa + (xb - xa) * s, ya + (yb - ya) * s
                    d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=YEL + (255,))
            d.regular_polygon((CX, cy, R * 0.98), 6, outline=YEL + (110,), width=4, rotation=0)
        for x, y, a in pts:
            m = mickey(48).rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
            G.blit(f, m, (x, y), 1, "mm")
        if t > t1 + 1.0:
            G.blit(f, G.pill("꼭 6개씩 둥글게 손잡기", "Black", 56, DARK, YEL, pad=(26, 12), radius=16), (CX, 640), pop(t, t1 + 1.0), "mt")


def s_grow(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (255,)))
    big(f, "모서리가 먼저 먹는다", 40, 96, hl="모서리", hlc=YEL)
    cy = 390
    g = 0.04 + 0.96 * G.clamp((t - 0.5) / 3.2)
    G.blit(f, F(290, g, seed=11), (CX, cy), 1, "mm")
    rnd = np.random.default_rng(3)
    d = ImageDraw.Draw(f)
    for i in range(70):   # 수증기 점 → 가장 가까운 모서리(팔 끝)로 빨려 들어감
        a0 = rnd.uniform(0, 2 * math.pi); r0 = rnd.uniform(300, 420)
        u = (t * 0.7 + rnd.uniform(0, 1)) % 1.0
        corner = math.radians(round(math.degrees(a0) / 60) * 60)
        tip = 290 * 0.92 * g + 20
        x0, y0 = CX + math.cos(a0) * r0, cy + math.sin(a0) * r0
        x1, y1 = CX + math.cos(corner) * tip, cy + math.sin(corner) * tip
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(140, 200, 255, int(220 * (1 - u * 0.7))))
    G.blit(f, G.pill("수증기 = 눈송이 밥", "Black", 46, DARK, ICE, pad=(22, 10), radius=14), (CX, 660), pop(t, 0.3), "mt")


def s_twins(f, t, sc):
    """여섯 팔은 같은 길 → 같은 모양 / 눈송이끼리는 다른 길 → 다른 모양"""
    vbg(f, "snow_trees_v", t, 0.7, 3)
    L = sc["L"]
    t1 = L[1] if len(L) > 1 else 1.8
    d = ImageDraw.Draw(f)
    if t < t1:
        big(f, "여섯 팔은 같이 날아서", 40, 92, hl="같이", hlc=YEL)
        g = 0.6 + 0.4 * G.clamp(t / 1.5)
        G.blit(f, F(260, g, seed=5).rotate(t * 10, resample=Image.BICUBIC), (CX, 400), 1, "mm")
        G.blit(f, G.pill("같은 온도 · 같은 습도 → 똑같이 자람", "Black", 44, DARK, CREAM, pad=(22, 10), radius=14), (CX, 660), pop(t, 0.5), "mt")
    else:
        lt = t - t1
        big(f, "눈송이끼리는 다른 길", 40, 92, hl="다른 길", hlc=RED)
        for i, (sx, seed) in enumerate([(200, 21), (540, 33), (880, 47)]):
            k = G.clamp((lt - i * 0.15) / 1.6)
            pts = [(sx + 90 * math.sin(s * 5 + i * 2.1), 200 + s * 380) for s in np.linspace(0, k, 24)]
            if len(pts) > 1:
                d.line(pts, fill=ICE + (200,), width=6)
            x, y = pts[-1]
            G.blit(f, F(130, 0.25 + 0.75 * k, seed=seed), (x, y), 1, "mm")
        if lt > 1.4:
            G.blit(f, G.pill("지나온 길이 다르면 모양도 다름", "Black", 46, DARK, YEL, pad=(22, 10), radius=14), (CX, 660), pop(t, t1 + 1.4), "mt")


def s_quiz(f, t, sc):
    vbg(f, "snow_fall_v", t, 0.6, 3)
    G.blit(f, F(180, 1.0, seed=7), (CX - 190, 200), pop(t, 0.1), "mm")
    G.blit(f, F(180, 1.0, seed=7), (CX + 190, 200), pop(t, 0.25), "mm")
    G.blit(f, T("=?", 120, YEL, "Black", stroke=8, stroke_fill=(0, 0, 0)), (CX, 200), pop(t, 0.4), "mm")
    big(f, "똑같은 눈송이\n있다? 없다?", 290, 100, hl="있다? 없다?", hlc=YEL, o=pop(t, 0.3))
    if t > 1.0:
        G.blit(f, G.pill("A 있다", "Black", 70, (255, 255, 255), (40, 120, 220), pad=(30, 12), radius=18), (CX - 200, 620), pop(t, 1.0), "mm")
        G.blit(f, G.pill("B 없다", "Black", 70, (255, 255, 255), RED, pad=(30, 12), radius=18), (CX + 200, 620), pop(t, 1.15), "mm")
    if t > 1.6:
        G.blit(f, T("댓글로 찍어 보세요 · 정답은 고정 댓글", 44, CREAM, "Black", stroke=6, stroke_fill=(0, 0, 0)), (CX, 700), pop(t, 1.6), "mt")
    K.credit(f, "영상: MilanWulf (Pixabay)")


def draw_cover(f):
    vbg(f, "snow_fall_v", 1.0, 0.55, 2)
    G.blit(f, F(260, 1.0), (CX, 540), 1, "mm")
    big(f, "왜 전부\n팔이 6개?", 60, 140, hl="6개", hlc=YEL)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "whoosh", 0.4), (0.3, "ding", 0.4)],
     "narr": ["눈송이는 왜 전부 팔이 여섯 개일까요?"]},
    {"draw": s_bentley, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_fn": lambda sc: [(sc["L"][1], "accent", 0.5)],
     "narr": ["백사십 년 전, 한 농부가 눈송이 5천 장을 찍었는데,", "전부 육각형이었어요."]},
    {"draw": s_molecule, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.15, "sfx_fn": lambda sc: [(0.1, "pop", 0.5), (sc["L"][1] + 0.8, "ding", 0.5)],
     "narr": ["범인은 미키마우스 머리처럼 생긴 물 분자.", "얼 때 서로 손을 잡으면, 꼭 여섯 개씩 둥글게 모여요."]},
    {"draw": s_grow, "flash": True, "nohead": True, "min": 3.6, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.5, "zoom_in", 0.4)],
     "narr": ["이 육각형 씨앗이 수증기를 먹는데, / 툭 튀어나온 모서리가 먼저 먹어서 팔이 쭉쭉 자라요."]},
    {"draw": s_twins, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.15, "sfx_fn": lambda sc: [(sc["L"][1], "reveal", 0.45)],
     "narr": ["여섯 팔은 같은 하늘을 같이 날아서 똑같이 자라고,", "눈송이끼리는 지나온 길이 달라서 다 다르게 생겼죠."]},
    {"draw": s_quiz, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "pop", 0.5), (1.15, "pop", 0.5)],
     "narr": ["그럼 똑같은 눈송이, 있다? 없다? 댓글로 찍어 보세요! / " + K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 1.6, "gap": 0.1, "tail": 0.1,
     "narr": ["눈송이는 왜 전부 팔이 여섯 개일까요?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "hope"), (2, "drive"), (5, "hope")])
