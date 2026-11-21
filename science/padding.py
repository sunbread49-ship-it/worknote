"""지식창고 쇼츠 · 겨울의 과학 ② 패딩은 왜 따뜻할까? (2026-11-21 20:00 · 구글 트렌드 '패딩' 1위)
  GEMINI_ONLY=gemini-2.5-pro-preview-tts python3 science/padding.py [--stills]
규칙(2026-11-20~): 30초 안팎 · 첫 1초 결과 화면 · A/B 댓글 질문 · 첫 장면으로 루프 · 시리즈 '겨울의 과학'
과학 (출처: 열전도율 표 — 공기 약 0.026 W/m·K, 물 약 0.6 W/m·K (약 23배) · 다운(솜털) 구조 · 필파워(fill power) 정의):
  솜털(down)은 깃대 없이 가는 털이 한 점에서 사방으로 퍼진 뭉치(민들레 씨앗 모양) → 털 사이에 공기를 가둠
  패딩 충전재 부피의 대부분(90% 이상)은 털이 붙잡은 공기 · 공기는 열을 잘 못 옮김 + 갇혀서 움직이지 못하면(대류 X) 더 잘 막음
  젖으면 털이 뭉쳐 공기 자리를 물이 차지 → 물은 공기보다 열을 20배 넘게 빨리 옮김 → 추움
  고정 댓글 정답: 보통은 거위털 — 털뭉치가 더 커서 같은 무게로 공기를 더 품음(필파워 ↑). 단, 필파워가 같으면 따뜻함은 비슷
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM  # noqa: E402
from drone import vbg, big, pop  # noqa: E402
from engine import illust as I  # noqa: E402

OUT = K.HERE / "out" / "padding"
HEAD = {"kicker": "겨울의 과학", "title": "패딩", "highlight": "패딩",
        "banner": ["겨울의 과학 ②", "패딩은 왜 따뜻할까?"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.2}}
CX = W / 2
ICE = (150, 220, 255)
YEL = (255, 214, 60)
RED = (240, 70, 70)
ORG = (255, 150, 60)
BLUE = (60, 150, 235)
DARK = (8, 14, 30)


def down(d, cx, cy, r, g=1.0, seed=1, col=(250, 250, 255, 235)):
    """솜털 한 뭉치: 한 점에서 가는 털이 사방으로 (민들레 씨앗)"""
    rnd = np.random.default_rng(seed)
    for _ in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        L = r * rnd.uniform(0.6, 1.0) * g
        bend = rnd.uniform(-0.35, 0.35)
        pts = []
        for s in np.linspace(0, 1, 7):
            aa = a + bend * s
            pts.append((cx + math.cos(aa) * L * s, cy + math.sin(aa) * L * s))
        d.line(pts, fill=col, width=3)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=col)


def baffle(f, x0, y0, w, h, t, g=1.0, wet=0.0, heat=True, seed=3):
    """패딩 한 칸 단면: 겉감(둥근 칸) 안에 솜털 뭉치 + 갇힌 공기 점 · wet: 물이 차오른 비율"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 60, fill=(40, 60, 90, 235), outline=(200, 210, 230, 255), width=8)
    if wet > 0:
        wy = y0 + h - h * wet
        d.rounded_rectangle((x0 + 8, wy, x0 + w - 8, y0 + h - 8), 50, fill=BLUE + (200,))
    rnd = np.random.default_rng(seed)
    for i in range(9):   # 솜털 뭉치 (젖으면 쪼그라듦)
        cx = x0 + w * (0.12 + 0.76 * (i % 3) / 2) + rnd.uniform(-20, 20)
        cy = y0 + h * (0.2 + 0.6 * (i // 3) / 2) + rnd.uniform(-15, 15)
        down(d, cx, cy, 90 * (1 - 0.6 * wet), g, seed=seed + i)
    if wet < 0.5:   # 갇힌 공기 (살짝 흔들리기만)
        for i in range(60):
            px = x0 + 30 + rnd.uniform(0, w - 60) + 4 * math.sin(t * 3 + i)
            py = y0 + 30 + rnd.uniform(0, h - 60) + 4 * math.cos(t * 2.5 + i)
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=ICE + (150,))
    f.alpha_composite(lay)


def s_hook(f, t, sc):
    vbg(f, "jacket_snow_v", t, 0.55, 2)
    # 확대경: 패딩 속
    k = pop(t, 0.1, 0.4)
    if k > 0:
        lens = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        baffle(lens, CX - 250, 400, 500, 340, t)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse((CX - 270, 300, CX + 270, 840), fill=int(255 * k))
        f.paste(lens, (0, 0), Image.composite(lens.getchannel("A"), Image.new("L", (W, H), 0), m))
        ImageDraw.Draw(f).ellipse((CX - 270, 300, CX + 270, 840), outline=(255, 255, 255, int(255 * k)), width=12)
    big(f, "패딩 속\n90%는 공기?", 20, 120, hl="공기?", hlc=ICE, o=pop(t, 0.2))
    K.credit(f, "영상: aghyadnajjar (Pixabay)")


def s_air(f, t, sc):
    """열 배달부: 공기 길은 느리게, 물 길은 빠르게"""
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (255,)))
    big(f, "공기는 열을\n잘 못 옮긴다", 30, 110, hl="못 옮긴다", hlc=ICE)
    d = ImageDraw.Draw(f)
    L = sc["L"]
    for row, (name, col, speed, y) in enumerate([("공기", ICE, 0.18, 420), ("물", BLUE, 1.0, 620)]):
        k = pop(t, 0.3 + row * 0.4)
        if k <= 0:
            continue
        G.blit(f, T(name, 64, col, "Black"), (90, y), k, "lm")
        d.rounded_rectangle((230, y - 26, 990, y + 26), 26, outline=col + (200,), width=5)
        for i in range(5):   # 열 알갱이(주황)가 오른쪽으로
            u = ((t - 0.3) * speed * 0.9 + i / 5) % 1.0
            x = 250 + u * 720
            d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=ORG + (255,))
    if t > (L[1] if len(L) > 1 else 1.6):
        G.blit(f, G.pill("물이 공기보다 20배 넘게 빨리", "Black", 50, DARK, YEL, pad=(24, 10), radius=14), (CX, 740), pop(t, L[1] if len(L) > 1 else 1.6), "mt")


def s_down(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (255,)))
    big(f, "솜털 = 민들레 씨앗", 40, 100, hl="민들레 씨앗", hlc=YEL)
    d = ImageDraw.Draw(f)
    g = 0.3 + 0.7 * G.ease_out(G.clamp((t - 0.2) / 1.2))
    down(d, CX, 470, 260, g, seed=7)
    rnd = np.random.default_rng(5)
    if t > 1.2:   # 털 사이에 갇힌 공기
        for i in range(70):
            a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(40, 240)
            px, py = CX + math.cos(a) * r + 3 * math.sin(t * 3 + i), 470 + math.sin(a) * r
            d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=ICE + (170,))
        G.blit(f, G.pill("털 사이에 공기를 꽉 붙잡는다", "Black", 50, DARK, ICE, pad=(24, 10), radius=14), (CX, 760), pop(t, 1.2), "mt")


def s_still(f, t, sc):
    """찬 바람(파란 화살)은 막히고, 몸의 열(주황)은 안에 머문다"""
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (255,)))
    big(f, "갇힌 공기는\n움직이지 못한다", 30, 105, hl="움직이지 못한다", hlc=YEL)
    baffle(f, 300, 330, 480, 400, t, seed=11)
    d = ImageDraw.Draw(f)
    for i in range(4):   # 바람: 왼쪽에서 와서 벽에 막힘
        u = (t * 0.9 + i / 4) % 1.0
        y = 380 + i * 90
        x1 = 40 + u * 220
        d.line((40, y, x1, y), fill=BLUE + (230,), width=10)
        d.polygon([(x1, y - 16), (x1 + 26, y), (x1, y + 16)], fill=BLUE + (230,))
    for i in range(3):   # 몸의 열: 오른쪽 안쪽에 머묾
        y = 420 + i * 110
        r = 26 + 4 * math.sin(t * 4 + i)
        d.ellipse((880 - r, y - r, 880 + r, y + r), fill=ORG + (240,))
    G.blit(f, T("몸", 54, ORG, "Black"), (880, 330), 1, "mb")
    G.blit(f, T("찬 바람", 44, BLUE, "Black"), (140, 330), 1, "mb")


def s_wet(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), DARK + (255,)))
    big(f, "그래서 젖으면 춥다", 40, 100, hl="춥다", hlc=RED)
    wet = G.ease_out(G.clamp((t - 0.3) / 1.6))
    baffle(f, 300, 260, 480, 400, t, wet=wet, seed=11)
    G.blit(f, I.emoji("droplet", 110), (CX + 340, 330), pop(t, 0.1), "mm")
    if t > 1.4:
        G.blit(f, G.pill("공기 자리를 물이 차지 → 열이 술술", "Black", 46, DARK, ICE, pad=(22, 10), radius=14), (CX, 720), pop(t, 1.4), "mt")


def s_quiz(f, t, sc):
    vbg(f, "winter_walk_v", t, 0.6, 3)
    G.blit(f, I.emoji("goose", 230), (CX - 230, 280), pop(t, 0.1), "mm")
    G.blit(f, I.emoji("duck", 230), (CX + 230, 280), pop(t, 0.25), "mm")
    G.blit(f, T("VS", 110, YEL, "Black", stroke=8, stroke_fill=(0, 0, 0)), (CX, 280), pop(t, 0.4), "mm")
    big(f, "더 따뜻한 건?", 440, 110, hl="따뜻한", hlc=YEL, o=pop(t, 0.3))
    if t > 0.9:
        G.blit(f, G.pill("A 거위털", "Black", 70, (255, 255, 255), (40, 120, 220), pad=(30, 12), radius=18), (CX - 220, 640), pop(t, 0.9), "mm")
        G.blit(f, G.pill("B 오리털", "Black", 70, (255, 255, 255), RED, pad=(30, 12), radius=18), (CX + 220, 640), pop(t, 1.05), "mm")
    if t > 1.5:
        G.blit(f, T("댓글로 찍어 보세요 · 정답은 고정 댓글", 44, CREAM, "Black", stroke=6, stroke_fill=(0, 0, 0)), (CX, 720), pop(t, 1.5), "mt")
    K.credit(f, "영상: NickyPe (Pixabay)")


def draw_cover(f):
    vbg(f, "jacket_snow_v", 1.0, 0.5, 2)
    lens = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    baffle(lens, CX - 300, 330, 600, 420, 1.0)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((CX - 330, 210, CX + 330, 870), fill=255)
    f.paste(lens, (0, 0), Image.composite(lens.getchannel("A"), Image.new("L", (W, H), 0), m))
    ImageDraw.Draw(f).ellipse((CX - 330, 210, CX + 330, 870), outline=(255, 255, 255, 255), width=12)
    big(f, "패딩 속\n90%는 공기?", 40, 130, hl="공기?", hlc=ICE)
    big(f, "거위털 vs 오리털", 960, 100, col=YEL)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "zoom_in", 0.4), (0.3, "ding", 0.4)],
     "narr": ["패딩 속은 90% 넘게 공기예요."]},
    {"draw": s_air, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_fn": lambda sc: [(sc["L"][1], "accent", 0.5)],
     "narr": ["공기는 열을 아주 느리게 옮기는 게으른 배달부예요.", "물보다 20배 넘게 느리죠."]},
    {"draw": s_down, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.2, "sparkle", 0.4)],
     "narr": ["오리와 거위 가슴의 솜털은 민들레 씨앗처럼 사방으로 퍼져서, | 그 사이에 공기를 꽉 붙잡아요."]},
    {"draw": s_still, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "whoosh", 0.4)],
     "narr": ["갇힌 공기는 움직이지 못하니까, 찬 바람은 못 들어오고 몸의 열은 못 나가요."]},
    {"draw": s_wet, "flash": True, "nohead": True, "min": 2.8, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "splash", 0.4)],
     "narr": ["그래서 패딩이 젖으면 추워요. | 공기 자리를 물이 차지하거든요."]},
    {"draw": s_quiz, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.9, "pop", 0.5), (1.05, "pop", 0.5)],
     "narr": ["그럼 거위털 vs 오리털, 더 따뜻한 건? 댓글로 찍어 보세요! / " + K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 1.6, "gap": 0.1, "tail": 0.1,
     "narr": ["패딩 속은 90% 넘게 공기예요."]},
]

K.SUB_HL = ["90%", "공기", "20배", "민들레 씨앗", "꽉 붙잡아요", "몸의 열", "추워요", "물이", "거위털 vs 오리털"]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "hope"), (2, "drive"), (5, "hope")])
