"""EP016 CEO 축출 — 9:16 전용 쇼츠 2개 (2026-11-16 12:00 · 21:00, 2주 시험: 롱폼 당일 쇼츠 2개)
규칙: 첫 1초 가장 센 숫자 · 3초 질문 · 5초 약속 · 2~3초 컷 · 위쪽 제목 띠 · 큰 한 줄 자막 · Gemini 1.12배 · 움직이는 영상 배경
숫자: 롱폼 checks와 같음 (Yahoo Finance 일별 수정 종가)

  python3 youtube/shorts9/ep016_ceo.py 1 [--stills]   → youtube/out/ep016_ceo_ousted/shorts9/s1/short.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep015_ship import K, G, T, W, H, CREAM, GOLD, MINT, ROOT, vbg, line_chart, big, pop, pill, bgp, disclaimer, RED, GREEN, BLUE, Image, ImageDraw  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep016_ceo_ousted" / "shorts9"
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}, "CEO": "씨이오", "HP": "에이치피"}


def cta(f, t, sc, line="풀버전은 오늘 저녁 6시"):
    vbg(f, "boardroom_v", t, 0.66)
    big(f, "여러분 생각은?", 420, 140, hl="생각은?")
    pill(f, line, 760, t, 0.2, bg=MINT, size=56)
    pill(f, "좋아요 누르고 친구한테도 물어보세요", 900, t, 0.5, size=50)
    disclaimer(f)


def bars(f, t, rows, y0=520, t0=0.2, step=0.4, vmax=26):
    for i, (lab, v, txt, col) in enumerate(rows):
        k = pop(t, t0 + i * step, 0.45)
        if k <= 0:
            continue
        y = y0 + i * 190
        G.blit(f, T(lab, 52, CREAM, "Black", stroke=5, stroke_fill=(0, 0, 0)), (80, y), k, "lt")
        w = int((W - 460) * abs(v) / vmax * k)
        ImageDraw.Draw(f).rounded_rectangle((80, y + 72, 80 + max(10, w), y + 150), 16, fill=col + (255,))
        G.blit(f, T(txt, 72, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (100 + max(10, w), y + 111), k, "lm")


# ── 쇼츠 1 (12:00): 젠슨 황 쫓겨난 엔비디아 · CEO 쫓겨나면 망할까? ──────────
def a1(f, t, sc):
    bgp(f, "jensen_010", t, 0.55, (0.5, 0.3))
    big(f, "젠슨 황 떠난\n엔비디아", 220, 110)
    big(f, "-12.75%", 620, 220, col=BLUE, o=pop(t, 0.05, 0.25))
    big(f, "단 일주일", 900, 80, o=pop(t, 0.4))
    K.credit(f, K.credit_of("jensen_010"))


def a2(f, t, sc):
    vbg(f, "boardroom_v", t, 0.62)
    big(f, "CEO가 쫓겨나면\n주가는 망할까?", 380, 130, hl="망할까?", hlc=RED)
    pill(f, "9개 회사 실제 주가로 확인", 820, t, 0.5, bg=MINT)


def a3(f, t, sc):
    vbg(f, "stock_decline_v", t, 0.72)
    big(f, "떠난 다음 날", 220, 110, col=GOLD)
    bars(f, t, [("스타벅스 · 2024", 24.5, "+24.5%", RED), ("디즈니 · 2022", 6.3, "+6.3%", RED),
                ("엔비디아 · 2026", 4.3, "-4.3%", BLUE), ("HP · 2010", 8.0, "-8.0%", BLUE)])


def a4(f, t, sc):
    bgp(f, "ai_captain_ship", t, 0.45)
    big(f, "다음 날 주가와\n1년 뒤 주가는", 220, 100)
    big(f, "완전히\n따로 놀았다", 500, 160, col=GOLD, o=pop(t, 0.3))


def a5(f, t, sc):
    bgp(f, "b737max_grounded", t, 0.5)
    big(f, "보잉 · CEO 해임", 240, 100)
    big(f, "다음 날 +2.9%", 520, 120, col=RED, o=pop(t, 0.2))
    big(f, "1년 뒤 -33%", 760, 150, col=BLUE, o=pop(t, 0.9))
    K.credit(f, K.credit_of("b737max_grounded"))


def a6(f, t, sc):
    vbg(f, "datacenter_v", t, 0.62)
    big(f, "1년 뒤를 정한 건\nCEO보다 사업", 300, 120, hl="사업", hlc=GOLD)
    pill(f, "엔비디아는 11월 17일 실적부터", 800, t, 0.6, bg=MINT)


S1 = [
    {"draw": a1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "mx:2908", 0.8)], "narr": ["젠슨 황이 떠난 엔비디아, 일주일 만에 마이너스 12.75%."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "accent_low", 0.5)],
     "narr": ["CEO가 쫓겨나면, 주가는 망할까요? 9개 회사로 확인해 봤어요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "pop", 0.5), (0.6, "pop", 0.5), (1.0, "pop", 0.5), (1.4, "fall_burn", 0.5)],
     "narr": ["떠난 다음 날, 스타벅스는 오히려 24.5% 올랐고, HP는 8% 빠졌어요."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "reveal", 0.5)],
     "narr": ["그런데 다음 날 주가와 1년 뒤 주가는, 완전히 따로 놀았어요. 다음 날 올랐다고, 1년 뒤에도 오르는 게 아니었죠."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "pop", 0.5), (0.9, "fall_burn", 0.6)],
     "narr": ["보잉은 CEO 해임 다음 날 올랐는데, 1년 뒤엔 마이너스 33%였죠."]},
    {"draw": a6, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "accent", 0.5)],
     "narr": ["1년 뒤를 정한 건 CEO보다 사업이었어요. 엔비디아는 11월 17일 실적부터 보면 돼요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["풀버전은 오늘 저녁 6시. 좋아요 누르고, 친구한테도 물어보세요."]},
]


# ── 쇼츠 2 (21:00): 잡스를 쫓아낸 애플, 6년 뒤 벌어진 일 ──────────────────
def b1(f, t, sc):
    bgp(f, "jobs_1984", t, 0.55, (0.5, 0.25))
    big(f, "잡스를 쫓아낸 애플", 220, 100)
    big(f, "6년 동안\n10배", 520, 190, col=RED, o=pop(t, 0.05, 0.25))
    K.credit(f, K.credit_of("jobs_1984"))


def b2(f, t, sc):
    vbg(f, "skyline_v", t, 0.62)
    big(f, "창업자 없이도\n잘나갔다?", 380, 140, hl="잘나갔다?", hlc=GOLD)
    pill(f, "그다음 6년을 보면…", 820, t, 0.5, bg=MINT)


def b3(f, t, sc):
    vbg(f, "stock_decline_v", t, 0.72)
    big(f, "애플 · 1985 ~ 1998", 200, 80)
    line_chart(f, t, "aapl", "1985-01-01", "1998-06-30", upto=min(1, max(0.02, (t - 0.2) / 1.8)),
               marks=[("1985-09-17", "잡스 떠남", (200, 206, 220), 0.0, 70), ("1991-04-02", "10배", GOLD, 0.0, -70), ("1997-12-23", "-81%", BLUE, 0.0, 70)])


def b4(f, t, sc):
    bgp(f, "ai_apple_tree", t, 0.45)
    big(f, "창업자가 심은 나무", 230, 100)
    big(f, "열매를\n다 따 먹은 뒤", 420, 150, col=GOLD, o=pop(t, 0.3))


def b5(f, t, sc):
    f.alpha_composite(K.photo("jobs_2008", W, H, (0.85, 0.55), 0.62, blur=8))   # 뒤 슬라이드 영어 글자가 읽히지 않게 흐림
    big(f, "1997년 잡스 복귀", 220, 100)
    big(f, "14년 동안\n110배", 520, 190, col=RED, o=pop(t, 0.2))
    K.credit(f, K.credit_of("jobs_2008"))


def b6(f, t, sc):
    vbg(f, "datacenter_v", t, 0.62)
    big(f, "젠슨 황 없는\n엔비디아는?", 300, 130, hl="엔비디아", hlc=GREEN)
    pill(f, "정식 CEO · 11월 17일 실적", 800, t, 0.5, bg=MINT)


S2 = [
    {"draw": b1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "mx:2003", 0.7)], "narr": ["스티브 잡스를 쫓아낸 애플, 6년 동안 주가가 10배가 됐어요."]},
    {"draw": b2, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "accent_low", 0.5)],
     "narr": ["창업자 없이도 잘나간 걸까요? 그다음 6년을 보면 달라요."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "mx:2003", 0.5), (1.7, "fall_burn", 0.7)],
     "narr": ["1991년 꼭대기 이후 새 히트작이 없었고, 1997년엔 꼭대기에서 마이너스 81%까지 빠졌어요."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "reveal", 0.5)],
     "narr": ["창업자가 심은 나무에서, 열매를 다 따 먹은 뒤였던 거죠."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "mx:2003", 0.7)],
     "narr": ["그리고 1997년 잡스가 돌아오자, 14년 동안 110배가 됐어요."]},
    {"draw": b6, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "accent", 0.5)],
     "narr": ["그럼 젠슨 황 없는 엔비디아는요? 정식 CEO와 11월 17일 실적이 첫 힌트예요."]},
    {"draw": lambda f, t, sc: cta(f, t, sc, "풀버전은 채널에서"), "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.05, "pop", 0.6)], "narr": ["여러분은 어떻게 보세요? 좋아요 누르고, 친구한테도 물어보세요."]},
]

SETS = {1: (S1, ["젠슨 황 쫓겨난 엔비디아", "CEO 쫓겨나면 망할까?"], [(0, "tense"), (3, "drive")]),
        2: (S2, ["잡스를 쫓아낸 애플", "6년 뒤 벌어진 일"], [(0, "drive"), (2, "dark"), (4, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), argv=sys.argv[2:], bgm_cues=cues)
