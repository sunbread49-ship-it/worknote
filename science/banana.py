"""지식창고 쇼츠 · 바나나에서 방사능이 나온다, 몇 개 먹으면 위험할까? (2026-11-19 20:00)
  python3 science/banana.py [--stills]
과학 (출처: Wikipedia 'Banana equivalent dose' · 질병관리청 의료방사선 2026.8 보도 · ICRP 표준인):
  바나나 1개 칼륨 약 0.5g · 자연 칼륨의 0.0117%가 칼륨-40 (방사성) · 칼륨 1g ≈ 31Bq → 바나나 1개 ≈ 15Bq
  바나나 1개 먹은 피폭 ≈ 0.1μSv (반올림 · 엄밀히 0.08~0.1)
  흉부 X선 0.07mSv = 바나나 700개 · 흉부 CT 4.4mSv = 4만 4천 개 (질병관리청) · 우리나라 연간 자연방사선 약 3mSv = 3만 개
  급성 방사선 증상 약 1Sv부터 = 바나나 1,000만 개 (한 번에)
  반전: 성인(70kg) 몸속 칼륨 약 140g → 칼륨-40 약 4,300Bq = 바나나 약 290개 · 몸은 칼륨을 일정하게 유지 → 먹어도 쌓이지 않음 (콩팥이 배출)
  주의: 콩팥 질환이 있으면 칼륨 섭취 조절 (의사 상담)
규칙: 내용 자체를 영상으로 · 실사 + 도식 변주 · 중하단 큰 멘트 · 한 목소리 · '친구한테 아는 척'
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, GOLD, MINT  # noqa: E402
from drone import vbg, big, pop, pill  # noqa: E402
from engine import illust as I  # noqa: E402

OUT = K.HERE / "out" / "banana"
HEAD = {"kicker": "생활 속 과학", "title": "바나나", "highlight": "바나나",
        "banner": ["바나나 몇 개 먹으면", "방사능 위험?"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.18}, "칼륨-40": "칼륨 사십", "Bq": "베크렐", "μSv": "마이크로시버트",
       "mSv": "밀리시버트", "Sv": "시버트", "CT": "씨티", "X선": "엑스선"}
CX = W / 2
RED = (240, 70, 70)
GREEN = (60, 210, 120)
DARK = (14, 16, 24)
YEL = (255, 214, 60)


def geiger(f, t, y, rate=15, t0=0.0):
    """방사선 측정기: 숫자 + 깜빡이는 바늘 (1초에 15번 '딱')"""
    w, h = 620, 300
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(30, 34, 30, 240), outline=(255, 214, 60, 255), width=6)
    d.rounded_rectangle((30, 30, w - 31, 170), 18, fill=(12, 26, 14, 255))
    blink = int(t * rate) % 2 == 0 and t > t0
    p.alpha_composite(T("15 Bq" if t > t0 else "0 Bq", 100, (120, 255, 140) if blink else (90, 200, 110), "Black"), (60, 40))
    d.ellipse((w - 110, 200, w - 50, 260), fill=(255, 60, 60, 255) if blink else (90, 30, 30, 255))
    p.alpha_composite(T("방사선 측정기", 40, CREAM, "Bold"), (40, 205))
    G.blit(f, p, (CX, y), pop(t, t0 - 0.2), "mt")


def s_hook(f, t, sc):
    vbg(f, "banana_market_v", t, 0.45, 1)
    geiger(f, t, 60, t0=0.2)
    big(f, "바나나에서\n방사능이?", 420, 140, hl="방사능", hlc=YEL, o=pop(t, 0.5))
    K.credit(f, "영상: andrej567 (Pixabay)")


def s_question(f, t, sc):
    vbg(f, "banana_plant_v", t, 0.55, 2)
    big(f, "그럼 몇 개 먹으면\n위험할까?", 160, 130, hl="위험할까?", hlc=RED)
    K.credit(f, "영상: Matthias_Groeneveld (Pixabay)")


def s_atoms(f, t, sc):
    """칼륨 원자 1만 개 중 1개 = 칼륨-40 (점 격자 → 빨간 점 하나로 줌)"""
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 12, 18, 255)))
    big(f, "범인은 칼륨", 40, 90, hl="칼륨", hlc=YEL)
    z = 1.0 + 5.0 * G.ease_out(min(1.0, max(0.0, (t - 1.2) / 1.4)))
    n, gap = 100, 9.0 * z
    cx0, cy0 = CX, 470
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    hot = (63, 41)   # 칼륨-40 하나
    hx, hy = cx0 + (hot[0] - n / 2) * gap, cy0 + (hot[1] - n / 2) * gap
    for i in range(n):
        x = cx0 + (i - n / 2) * gap - (hx - cx0) * (z - 1) / 5
        if x < -10 or x > W + 10:
            continue
        for j in range(n):
            y = cy0 + (j - n / 2) * gap - (hy - cy0) * (z - 1) / 5
            if y < 160 or y > 800:
                continue
            r = max(1.2, 1.8 * z)
            if (i, j) == hot:
                rr = r * (2.4 + 0.6 * math.sin(t * 8))
                d.ellipse((x - rr * 2, y - rr * 2, x + rr * 2, y + rr * 2), fill=(255, 60, 60, 90))
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 70, 70, 255))
            else:
                d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 170, 200, 200))
    f.alpha_composite(lay)
    G.blit(f, G.pill("칼륨 알갱이 1만 개 중 1개는 '불안정'", "Black", 46, DARK, YEL, pad=(22, 10), radius=14), (CX, 170), pop(t, 0.3), "mt")
    if t > 2.0:   # 불안정한 알갱이가 작은 에너지 총알을 '퓽'
        k = (t * 1.6) % 1.0
        ang = (int(t * 1.6) * 2.4) % (2 * math.pi)
        x0, y0 = CX, 470
        x1, y1 = x0 + math.cos(ang) * 420 * k, y0 + math.sin(ang) * 280 * k
        dd = ImageDraw.Draw(f)
        dd.line((x0, y0, x1, y1), fill=(255, 240, 120, int(255 * (1 - k))), width=8)
        G.blit(f, T("퓽!", 70, (255, 240, 120), "Black", stroke=6, stroke_fill=(0, 0, 0)), (x1, y1), 1 - k * 0.6, "mm")
    if t > 2.6:
        G.blit(f, T("바나나 1개 = 1초에 15번 퓽", 62, CREAM, "Black", stroke=6, stroke_fill=(0, 0, 0)), (CX, 690), pop(t, 2.6), "mt")


LADDER = [("바나나 1개", 0.1, "1개", YEL), ("흉부 X선", 70, "700개", CREAM), ("1년 자연방사선", 3000, "3만 개", CREAM),
          ("흉부 CT", 4400, "4만 4천 개", (255, 160, 60)), ("급성 증상 시작", 1e6, "1,000만 개", RED)]


def s_ladder(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 12, 18, 255)))
    vbg(f, "xray_chest_v", t, 0.85, 6)
    big(f, "바나나로 환산하면", 30, 80)
    L = sc["L"]
    for i, (lab, usv, txt, col) in enumerate(LADDER):
        t0 = (0.2 + i * 0.45) if i < 3 else (L[1] if len(L) > 1 else 1.8) + (i - 3) * 0.6
        k = pop(t, t0, 0.35)
        if k <= 0:
            continue
        y = 160 + i * 128
        G.blit(f, T(lab, 46, CREAM, "Black"), (60, y), k, "lt")
        g = G.clamp((t - t0) / 0.7)
        w = int((W - 420) * (math.log10(usv * 10) / math.log10(1e7)) * g)
        ImageDraw.Draw(f).rounded_rectangle((60, y + 60, 60 + max(10, w), y + 104), 12, fill=col + (255,))
        G.blit(f, T(txt, 52, col, "Black", stroke=5, stroke_fill=(0, 0, 0)), (80 + max(10, w), y + 82), min(1, g * 2), "lm")
    K.credit(f, "영상: intersubjektiv (Pixabay) · 선량: 질병관리청 · 바나나 1개 ≈ 0.1μSv · 로그 눈금")


def body_shape(h=560):
    """사람 실루엣 (머리 · 몸통 · 팔 · 다리) — 단순 도형"""
    w = int(h * 0.55)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (255, 214, 60, 255)
    hr = h * 0.09
    d.ellipse((w / 2 - hr, 0, w / 2 + hr, hr * 2), fill=c)
    d.rounded_rectangle((w / 2 - h * 0.13, hr * 2 + 10, w / 2 + h * 0.13, h * 0.58), 30, fill=c)
    d.rounded_rectangle((w / 2 - h * 0.25, hr * 2 + 20, w / 2 - h * 0.15, h * 0.52), 20, fill=c)
    d.rounded_rectangle((w / 2 + h * 0.15, hr * 2 + 20, w / 2 + h * 0.25, h * 0.52), 20, fill=c)
    d.rounded_rectangle((w / 2 - h * 0.12, h * 0.56, w / 2 - h * 0.02, h), 20, fill=c)
    d.rounded_rectangle((w / 2 + h * 0.02, h * 0.56, w / 2 + h * 0.12, h), 20, fill=c)
    return im


def s_body(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 12, 18, 255)))
    big(f, "반전 · 내 몸도 퓽!", 30, 84, hl="퓽!", hlc=YEL)
    b = body_shape(520)
    bx, by = CX - b.width / 2, 160
    G.blit(f, b, (bx, by), pop(t, 0.1), "lt")
    rnd = np.random.default_rng(int(t * 12))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if t > 0.4:   # 몸 여기저기서 퓽퓽 (1초에 4천 번 넘게)
        for _ in range(26):
            x = bx + rnd.uniform(0.25, 0.75) * b.width
            y = by + rnd.uniform(0.08, 0.95) * b.height
            a = rnd.uniform(0, 2 * math.pi); L_ = rnd.uniform(30, 70)
            d.line((x, y, x + math.cos(a) * L_, y + math.sin(a) * L_), fill=(255, 255, 255, 230), width=4)
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 70, 70, 255))
    f.alpha_composite(lay)
    G.blit(f, G.pill("내 몸에서 1초에 4,300번 퓽", "Black", 50, DARK, YEL, pad=(22, 10), radius=14), (CX, 700), pop(t, 0.9), "mt")
    L = sc["L"]
    if len(L) > 1 and t > L[1]:
        G.blit(f, G.pill("= 바나나 290개를 늘 들고 다니는 셈", "Black", 46, DARK, CREAM, pad=(22, 10), radius=14), (CX, 790), pop(t, L[1]), "mt")


def s_balance(f, t, sc):
    """몸속 칼륨 = 늘 같은 높이로 차 있는 물통 · 바나나를 부으면 넘친 만큼 배수구(콩팥)로"""
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 12, 18, 255)))
    big(f, "몸은 칼륨 물통", 30, 90, hl="물통", hlc=GREEN)
    d = ImageDraw.Draw(f)
    x0, x1, y0, y1 = 260, 820, 250, 720
    level = 400 + 6 * math.sin(t * 3)
    d.rectangle((x0, level, x1, y1), fill=(60, 150, 230, 255))
    d.line((x0, y0, x0, y1), fill=CREAM + (255,), width=10); d.line((x1, y0, x1, y1), fill=CREAM + (255,), width=10)
    d.line((x0, y1, x1, y1), fill=CREAM + (255,), width=10)
    d.line((x0 - 20, 400, x0 + 30, 400), fill=YEL + (255,), width=6)
    G.blit(f, T("늘 이 높이", 38, YEL, "Black"), (x0 - 30, 400), 1, "rm")
    d.rectangle((x1, 392, x1 + 140, 412), fill=CREAM + (255,))
    for i in range(3):   # 넘친 물 → 배수구(콩팥)
        u = (t * 1.2 + i / 3) % 1.0
        d.ellipse((x1 + 140 - 10, 412 + u * 260 - 10, x1 + 140 + 10, 412 + u * 260 + 10), fill=(60, 150, 230, 255))
    G.blit(f, G.pill("콩팥 → 소변", "Black", 40, DARK, GREEN, pad=(18, 8), radius=12), (x1 + 140, 690), 1, "mt")
    ban = I.emoji("banana", 110)
    for i in range(2):   # 위에서 바나나 퐁당
        u = (t * 0.8 + i * 0.5) % 1.0
        G.blit(f, ban.rotate(u * 200, expand=True), ((x0 + x1) / 2 + (i - 0.5) * 160, 120 + u * 260), 1 - max(0, u - 0.8) * 5, "mm")
    if t > 1.6:
        G.blit(f, T("더 먹어도 넘친 만큼 빠져나가서\n방사능이 쌓이지 않아요", 46, CREAM, "Bold", align="center"), (CX, 760), pop(t, 1.6), "mt")


def s_end(f, t, sc):
    vbg(f, "banana_market_v", t, 0.5, 2)
    big(f, "1,000만 개 먹기 전에", 150, 90)
    big(f, "배가 먼저\n터진다", 290, 160, hl="터진다", hlc=YEL, o=pop(t, 0.3))
    if t > 1.4:
        G.blit(f, G.pill("단, 콩팥이 안 좋다면 칼륨은 의사와 상담", "Black", 40, DARK, CREAM, pad=(20, 8), radius=12), (CX, 680), pop(t, 1.4), "mt")
    K.credit(f, "영상: andrej567 (Pixabay)")


def s_cta(f, t, sc):
    vbg(f, "banana_plant_v", t, 0.6, 3)
    big(f, "오늘 바나나\n몇 개 드셨어요?", 140, 130, hl="몇 개")
    pill(f, "좋아요 누르고 친구한테 아는 척!", CX, 560, t, 0.4, size=52)
    K.credit(f, "영상: Matthias_Groeneveld (Pixabay)")


def draw_cover(f):
    vbg(f, "banana_market_v", 1.0, 0.45, 1)
    geiger(f, 1.0, 60, t0=0.2)
    big(f, "바나나에서\n방사능이?", 420, 140, hl="방사능", hlc=YEL)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2 + i / 15, "tick", 0.25) for i in range(20)],
     "narr": ["바나나에 측정기를 대면, / 방사능이 나와요."]},
    {"draw": s_question, "flash": True, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "ding", 0.5)],
     "narr": ["그럼 몇 개 먹으면 위험할까요?"]},
    {"draw": s_atoms, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(1.2, "zoom_in", 0.5), (2.6, "accent", 0.5)],
     "narr": ["범인은 바나나 속 영양소, 칼륨이에요. / 칼륨 알갱이 1만 개 중 1개는 성격이 불안정해서,", "가만히 있다가 아주 작은 에너지 총알을 퓽 쏘고 얌전해져요. 이게 방사선이에요. / 바나나 하나에선 1초에 15번 퓽. 그래서 15베크렐이에요."]},
    {"draw": s_ladder, "flash": True, "nohead": True, "min": 3.6, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.2 + 0.45 * i, "pop", 0.45) for i in range(3)] + [(sc["L"][1], "pop", 0.45), (sc["L"][1] + 0.6, "fail", 0.4)],
     "narr": ["이제 방사선 양을 바나나 개수로 바꿔 볼게요. / 병원 가슴 엑스레이 한 번이 바나나 700개, / 그냥 1년 동안 살면서 자연에서 받는 게 3만 개예요.",
              "흉부 CT는 4만 4천 개, / 그리고 몸에 증상이 나타나려면, / 한 번에 1,000만 개를 먹어야 해요."]},
    {"draw": s_body, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.2, "sfx_fn": lambda sc: [(0.8, "reveal", 0.5), (sc["L"][1], "ding", 0.5)],
     "narr": ["그런데 반전. / 칼륨은 원래 우리 몸에도 많아요. 그래서 지금 이 순간에도, / 내 몸에서 1초에 4천 번 넘게 퓽퓽 하고 있어요.", "바나나 290개를 늘 들고 다니는 셈이죠."]},
    {"draw": s_balance, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.2 + 0.5 * i, "pop", 0.4) for i in range(3)],
     "narr": ["게다가 우리 몸은, 늘 같은 높이로 물이 차 있는 물통 같아요. / 바나나를 먹어서 칼륨을 더 부으면, / 넘친 만큼 콩팥이 소변으로 내보내요. 그래서 바나나 방사능은 쌓이지 않아요."]},
    {"draw": s_end, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.3, "boom", 0.4), (1.4, "pop", 0.4)],
     "narr": ["결국 1,000만 개를 먹기 전에, / 배가 먼저 터져요. / 단, 콩팥이 안 좋은 분은 칼륨을 의사와 상담하세요."]},
    {"draw": s_cta, "flash": True, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.45, "pop", 0.6)],
     "narr": ["오늘 바나나 몇 개 드셨어요? / " + K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.15,
     "narr": ["바나나에 측정기를 대면, / 방사능이 나와요."]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "tense"), (4, "drive"), (6, "hope")])
