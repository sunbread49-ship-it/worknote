"""지식창고 쇼츠 · 내가 선 줄만 안 줄어드는 이유 (2026-11-16 20:00)
  python3 science/waiting_line.py [--stills]
흐름(사용자 확정 11/15): 맥도날드 오픈런으로 집중 → '왜 내 줄만 길까? 옆 줄은 빠른데' 공감 질문 → 이유 3가지 → 마트 줄 꿀팁(수학)
사실 근거:
  - 트렌드: 구글 트렌드 한국 '맥도날드 세종dt점' 500+ (2026.11.14) · 기사 제목 "새벽 2시부터 줄 섰다…'인구 40만' 세종시 첫 맥도날드, 오픈런에 경찰까지 출동"
  - 확률: 속도가 비슷한 줄 3개 중 내 줄이 가장 빠를 확률 1/3
  - 기다림의 심리: 아무것도 안 하고 기다리는 시간은 더 길게 느껴진다 (David Maister, 'The Psychology of Waiting Lines', 1985)
  - 계산대 시간: 수학 교사 댄 마이어 측정 — 손님 1명당 약 41초(인사 · 결제 · 짐 챙기기), 물건 1개당 약 3초 (CBC · Business Insider 보도, 2016)
    → 산더미 카트 1명(물건 50개) 41+150 = 191초 · 바구니 3명(각 10개) 3×(41+30) = 213초 (사용자 11/15: 극단적 비교)
사진 · 영상: Pixabay (실사) + AI 점토 그림 섞어서 (사용자 11/15)
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, GOLD, MINT  # noqa: E402
from drone import vbg, pbg, big, pop, pill  # noqa: E402

OUT = K.HERE / "out" / "queue"
HEAD = {"kicker": "생활 속 과학", "title": "줄 서기", "highlight": "줄",
        "banner": ["내가 선 줄만", "안 줄어드는 이유"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}}
CX = W / 2
RED = (240, 70, 70)
BLUE = (80, 160, 255)
DARK = (14, 16, 24)


def credit(f, text):
    K.credit(f, text)


def headline_card(f, t, t0, y=640):
    k = pop(t, t0, 0.3)
    if k <= 0:
        return
    w = 960
    card = Image.new("RGBA", (w, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w - 1, 329), 26, fill=(250, 250, 248, 250))
    d.rectangle((0, 0, 14, 329), fill=(220, 40, 40, 255))
    card.alpha_composite(T("2026.11.14 보도 · 기사 제목", 30, (110, 112, 124), "Bold"), (50, 30))
    card.alpha_composite(T("새벽 2시부터 줄 섰다…\n'인구 40만' 세종시 첫 맥도날드,\n오픈런에 경찰까지 출동", 52, (20, 22, 30), "Black", line_gap=1.15), (50, 82))
    K.drop(f, card.rotate(-2 * (1 - k), expand=True, resample=Image.BICUBIC), (CX, y + (1 - k) * 60), "mm", k, blur=22)


# ── 장면 ─────────────────────────────────────────────
def s_hook(f, t, sc):
    """첫 1초: 새벽 오픈런 줄 + 기사 제목"""
    pbg(f, "queue_dawn", t, 0.3, 0.1, (0.35, 0.5))
    big(f, "햄버거 먹으려고\n새벽 2시부터 줄?", 60, 112, hl="새벽 2시")
    headline_card(f, t, 0.5, 860)
    credit(f, "사진: Vilkasss (Pixabay) · 기사 제목: 2026.11.14 보도")


def s_question(f, t, sc):
    pbg(f, "ai_slow_line", t, 0.2, 0.08, (0.3, 0.5))
    big(f, "근데 왜\n내 줄만 안 줄어들까?", 60, 120, hl="내 줄만", hlc=(255, 120, 100))
    pill(f, "옆 줄은 쑥쑥 빠지는데…", CX, 1060, t, 0.9, bg=CREAM, size=60)
    credit(f, "그림: AI 생성 (Gemini)")


def s_promise(f, t, sc):
    vbg(f, "supermarket_cart_v", t, 0.5, 3)
    big(f, "기분 탓?\n아니에요", 120, 150, hl="아니에요", hlc=MINT)
    pill(f, "이유 3가지 + 마트 줄 꿀팁", CX, 760, t, 0.4, bg=GOLD, size=64)
    credit(f, "영상: Buvrix27 (Pixabay)")


def lanes(f, t, t0, y0=330, labels=("내 줄", "옆 줄 A", "옆 줄 B"), seed=3):
    """줄 3개 경주: 매번 무작위로 1등이 바뀌는 모습 → 3번 중 내 줄이 이긴 건 1번"""
    rnd = random.Random(seed)
    rounds = [[rnd.uniform(0.75, 1.0) for _ in labels] for _ in range(3)]
    rounds[0] = [0.78, 1.0, 0.86]   # 1판: 옆 줄 A 승
    rounds[1] = [0.84, 0.80, 1.0]   # 2판: 옆 줄 B 승
    rounds[2] = [1.0, 0.82, 0.88]   # 3판: 내 줄 승
    dur = 1.0
    u = max(0.0, t - t0)
    r = min(2, int(u // dur))
    p = min(1.0, (u - r * dur) / (dur * 0.85))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((60, y0 - 40, W - 60, y0 + 560), 36, fill=(10, 12, 22, 200))
    f.alpha_composite(ov)
    win = max(range(3), key=lambda i: rounds[r][i])
    for i, lab in enumerate(labels):
        y = y0 + 40 + i * 170
        col = (255, 120, 100) if i == 0 else (150, 170, 210)
        G.blit(f, T(lab, 54, col, "Black"), (110, y), 1, "lt")
        x1 = 110 + (W - 340) * rounds[r][i] * p
        ImageDraw.Draw(f).rounded_rectangle((110, y + 72, max(130, x1), y + 120), 20, fill=col + (255,))
        if p >= 1 and i == win:
            G.blit(f, T("1등", 52, GOLD, "Black", stroke=5, stroke_fill=(0, 0, 0)), (x1 + 20, y + 96), 1, "lm")
    # 판 기록
    marks = ["옆 줄 승", "옆 줄 승", "내 줄 승"]
    for j in range(r + (1 if p >= 1 else 0)):
        G.blit(f, G.pill(f"{j + 1}판 · {marks[j]}", "Black", 40, DARK, MINT if j == 2 else CREAM, pad=(18, 8), radius=14),
               (110 + j * 300, y0 + 500), 1, "lt")


def s_prob(f, t, sc):
    pbg(f, "grocery_aisle", t, 0.62, 0.06)
    big(f, "① 확률", 50, 110, col=GOLD)
    L = sc["L"]
    lanes(f, t, 0.3)
    if len(L) > 1 and t > L[1]:
        big(f, "3번 중 2번은\n옆 줄이 이긴다", 1000, 96, hl="옆 줄", o=pop(t, L[1]))
    credit(f, "사진: ccipeggy (Pixabay)")


def s_grandma(f, t, sc):
    pbg(f, "ai_coupon_grandma", t, 0.25, 0.08, (0.6, 0.5))
    big(f, "② 앞사람 변수", 50, 110, col=GOLD)
    big(f, "한 명만 멈춰도\n줄 전체 STOP", 860, 112, hl="STOP", hlc=RED, o=pop(t, 0.4))
    credit(f, "그림: AI 생성 (Gemini)")


def s_memory(f, t, sc):
    vbg(f, "clock_anxiety_v", t, 0.45, 2)
    big(f, "③ 기억", 50, 110, col=GOLD)
    L = sc["L"]
    big(f, "가만히 기다리면\n더 길게 느껴지고", 420, 100, o=pop(t, 0.2))
    if len(L) > 1 and t > L[1]:
        big(f, "막힌 날만\n기억에 남는다", 820, 110, hl="막힌 날", hlc=RED, o=pop(t, L[1]))
    credit(f, "영상: kostkarubika005 (Pixabay)")


def s_tip(f, t, sc):
    pbg(f, "grocery_carts", t, 0.5, 0.08)
    pill(f, "꿀팁", CX, 120, t, 0.05, bg=GOLD, size=80)
    big(f, "줄 설 땐\n물건 말고\n사람을 세라", 300, 150, hl="사람", hlc=MINT)
    credit(f, "사진: 652234 (Pixabay)")


def s_math(f, t, sc):
    pbg(f, "till_receipt", t, 0.78, 0.05)
    L = sc["L"]
    big(f, "계산대 시간을 재 보니", 60, 80)
    rows = [("손님 1명", "약 41초", "인사 · 결제 · 영수증 · 짐 챙기기", RED, 0.2), ("물건 1개", "약 3초", "삑!", BLUE, 0.7)]
    for i, (a, b, c, col, t0) in enumerate(rows):
        k = pop(t, t0)
        y = 300 + i * 300
        G.blit(f, T(a, 70, CREAM, "Black"), (100, y), k, "lt")
        G.blit(f, T(b, 120, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (W - 100, y - 20), k, "rt")
        G.blit(f, T(c, 40, (180, 186, 204), "Bold"), (100, y + 110), k, "lt")
    if len(L) > 1 and t > L[1]:
        k = pop(t, L[1])
        G.blit(f, T("사람 1명 = 물건 14개", 100, GOLD, "Black", stroke=7, stroke_fill=(0, 0, 0)), (CX, 1000), k, "mm")
    credit(f, "자료: 수학 교사 댄 마이어 측정 (CBC · Business Insider 보도)")


def s_mountain(f, t, sc):
    """극단적 비교 문제: 산더미 카트 1명 vs 바구니 3명"""
    pbg(f, "ai_mountain_cart", t, 0.12, 0.06, (0.5, 0.6))
    big(f, "어느 줄이\n빠를까?", 40, 130, hl="빠를까?")
    k = pop(t, 0.4)
    G.blit(f, G.pill("산더미 카트 1명 · 물건 50개", "Black", 46, DARK, MINT, pad=(22, 10), radius=16), (W * 0.27, 1180), k, "mm")
    G.blit(f, G.pill("바구니 3명 · 10개씩", "Black", 46, DARK, CREAM, pad=(22, 10), radius=16), (W * 0.75, 1180), pop(t, 0.8), "mm")
    credit(f, "그림: AI 생성 (Gemini)")


def s_compare(f, t, sc):
    pbg(f, "grocery_aisle", t, 0.8, 0.04)
    big(f, "정답은?", 60, 110)
    rows = [("산더미 카트 1명", "물건 50개 · 41초 + 50 × 3초", 191, "3분 11초", MINT), ("바구니 3명", "10개씩 · (41초 + 30초) × 3", 213, "3분 33초", RED)]
    for i, (a, b, sec, txt, col) in enumerate(rows):
        k = pop(t, 0.2 + i * 0.5)
        y = 330 + i * 330
        G.blit(f, T(a, 74, CREAM, "Black"), (90, y), k, "lt")
        G.blit(f, T(b, 44, (180, 186, 204), "Bold"), (90, y + 92), k, "lt")
        g = G.clamp((t - 0.4 - i * 0.5) / 1.2)
        w = int((W - 420) * sec / 213 * g)
        ImageDraw.Draw(f).rounded_rectangle((90, y + 160, 90 + max(10, w), y + 240), 18, fill=col + (255,))
        if g > 0.05:
            G.blit(f, T(txt, 66, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (110 + w, y + 200), 1, "lm")
    if t > 2.0:
        G.blit(f, T("산더미 카트가 이긴다", 90, GOLD, "Black", stroke=7, stroke_fill=(0, 0, 0)), (CX, 1080), pop(t, 2.0), "mm")
    credit(f, "손님 1명 41초 · 물건 1개 3초로 계산한 예시 · 사진: ccipeggy (Pixabay)")


def s_cta(f, t, sc):
    pbg(f, "ai_slow_line", t, 0.5, 0.06, (0.3, 0.5))
    big(f, "다음엔\n사람 수부터!", 120, 140, hl="사람 수", hlc=MINT)
    pill(f, "좋아요 누르고 친구한테도 물어보세요", CX, 760, t, 0.4, size=50)
    credit(f, "그림: AI 생성 (Gemini)")


def draw_cover(f):
    pbg(f, "ai_slow_line", 2.0, 0.2, 0.0, (0.3, 0.5))
    big(f, "내 줄만\n안 줄어든다?", 80, 160, hl="내 줄만", hlc=(255, 120, 100))
    pill(f, "기분 탓 아님", CX, 1080, 3.0, 0.0, bg=GOLD, size=80)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1,
     "sfx_t": [(0.0, "accent", 0.5), (0.5, "pop", 0.5)],
     "narr": ["햄버거 하나 먹으려고 새벽 2시부터 줄, / 경찰까지 출동했대요."]},
    {"draw": s_question, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.9, "whoosh", 0.4)],
     "narr": ["근데 줄 설 때, 왜 꼭 내 줄만 안 줄어들까요? / 마트에서도 옆 줄은 쑥쑥 빠지는데요."]},
    {"draw": s_promise, "flash": True, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.4, "ding", 0.5)],
     "narr": ["기분 탓 아니에요. 이유 세 가지랑 꿀팁까지, 30초면 끝나요."]},
    {"draw": s_prob, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(1.15, "pop", 0.4), (2.15, "pop", 0.4), (3.15, "ding", 0.5)],
     "narr": ["첫째, 확률. 줄이 세 개면, 내 줄이 제일 빠를 확률은 3분의 1.", "3번 중 2번은 옆 줄이 이기는 게 정상이에요."]},
    {"draw": s_grandma, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.4, "fail", 0.35)],
     "narr": ["둘째, 앞사람 변수. 쿠폰 찾고, 카드 안 긁히고, / 한 명만 멈춰도 그 줄 전체가 멈춰요.", "줄이 길수록, 이런 분이 끼어 있을 확률도 커지죠."]},
    {"draw": s_memory, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.2,
     "sfx_fn": lambda sc: [(0.2, "tick", 0.4), (sc["L"][1], "accent_low", 0.45)],
     "narr": ["셋째, 기억. 가만히 서서 기다리면 시간이 더 길게 느껴지고,", "빨리 끝난 날은 금방 잊고, 막힌 날만 기억에 남거든요."]},
    {"draw": s_tip, "flash": True, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "sparkle", 0.5)],
     "narr": ["그럼 꿀팁. 마트에선 물건 말고, 사람 수를 세세요."]},
    {"draw": s_math, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.2, "pop", 0.5), (0.7, "pop", 0.5), (sc["L"][1], "reveal", 0.55)],
     "narr": ["한 미국 수학 교사가 계산대 시간을 재 봤더니, / 손님 한 명은 결제랑 인사만으로 약 41초, 물건 하나는 약 3초였어요.", "사람 한 명이 물건 14개랑 맞먹는 거죠."]},
    {"draw": s_mountain, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.4, "pop", 0.5), (0.8, "pop", 0.5)],
     "narr": ["그럼 문제. 물건 50개를 산처럼 쌓은 카트 한 명 줄, / 바구니 든 세 명 줄. 어디가 빠를까요?"]},
    {"draw": s_compare, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.25,
     "sfx_t": [(0.2, "pop", 0.5), (0.7, "pop", 0.5), (2.0, "ding", 0.55)],
     "narr": ["정답은 산더미 카트. 3분 11초 대 3분 33초로, / 사람 적은 줄이 이겨요."]},
    {"draw": s_cta, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.45, "pop", 0.6)],
     "narr": ["다음엔 사람 수부터 세 보세요. 좋아요 누르고, 친구한테도 물어보세요."]},
    {"draw": s_question, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["근데 줄 설 때, 왜 꼭 내 줄만 안 줄어들까요?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "drive"), (6, "hope")])
