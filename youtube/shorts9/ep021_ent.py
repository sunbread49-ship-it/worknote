"""EP021 엔터 4사 사장님 연봉 — 9:16 전용 쇼츠 2개 (2026-11-21 12:00 · 21:00) · 색 조합 08
규칙: 첫 1초 가장 센 숫자 · 위쪽 제목 띠 · 중하단 큰 멘트(자막은 받아쓰기 단어 시각에 맞춰 전환) · Gemini Umbriel · 한 목소리
숫자: 롱폼과 같음 (DART 2025 사업보고서 · 네이버 차트 2026.11.20 종가)

  CH_THEME=08 GEMINI_ONLY=gemini-2.5-flash-preview-tts python3 youtube/shorts9/ep021_ent.py 1 [--stills]
"""
import os
os.environ.setdefault("CH_THEME", "08")
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep015_ship import K, G, T, W, H, ROOT, vbg, big, pop, disclaimer, Image, ImageDraw  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep021_ent_ceo_pay" / "shorts9"
PH = ROOT / "youtube" / "assets" / "photos"
WH, GRN, RD, YEL = (251, 251, 249), (72, 176, 120), (232, 66, 62), (255, 204, 40)
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}, "BTS": "비티에스", "JYP": "제이와이피", "YG": "와이지", "SM": "에스엠"}


def pill(f, text, y, t, t0=0.0, size=56, bg=(1, 66, 43)):
    p = G.pill(text, "Black", size, WH, bg, pad=(30, 12), radius=12)
    G.blit(f, p, (W / 2, y), pop(t, t0), "mt")


def photo_bg(f, name, t, dark=0.55, fallback="concert_lights_v"):
    """공개 라이선스 사진(있으면) → 천천히 확대 · 없으면 공연 영상"""
    if (PH / f"{name}.json").exists():
        z = 1.0 + 0.05 * min(1, t / 4)
        im = K.photo(name, int(W * z), int(H * z), (0.5, 0.3), dark)
        f.alpha_composite(im, (int((W - im.width) / 2), int((H - im.height) / 2)))
        K.credit(f, K.credit_of(name))
    else:
        vbg(f, fallback, t, dark)


def logo_row(f, t, y, t0=0.0, h=70, names=("logo_hybe", "logo_sm", "logo_jyp", "logo_yg")):
    """엔터 4사 CI 한 줄 (흰 판)"""
    k = pop(t, t0)
    if k <= 0:
        return
    chips = []
    for n in names:
        lg = Image.open(PH / f"{n}.png").convert("RGBA")
        sc = min(190 / lg.width, h / lg.height)
        lg = lg.resize((int(lg.width * sc), int(lg.height * sc)), Image.LANCZOS)
        c = Image.new("RGBA", (214, h + 24), (0, 0, 0, 0))
        ImageDraw.Draw(c).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 14, fill=(255, 255, 255, 245))
        c.alpha_composite(lg, ((c.width - lg.width) // 2, (c.height - lg.height) // 2))
        chips.append(c)
    x = (W - (len(chips) * 214 + (len(chips) - 1) * 18)) / 2
    for c in chips:
        G.blit(f, c, (x, y), k, "lt")
        x += 214 + 18


def rank_rows(f, t, rows, y0=120, t0=0.2, step=0.45, gap=118):
    for i, (name, val, col) in enumerate(rows):
        k = pop(t, t0 + i * step)
        if k <= 0:
            continue
        y = y0 + i * gap
        G.blit(f, T(name, 58, WH, "Black", stroke=6, stroke_fill=(0, 0, 0)), (90, y), k, "lt")
        G.blit(f, T(val, 70, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (W - 90, y - 6), k, "rt")


def cta(f, t, sc, q="여러분이라면\n연봉? 지분?", line="풀버전은 오늘 오후 4시"):
    photo_bg(f, "skz_gda", t, 0.62)
    big(f, q, 260, 120, hl=q.split("\n")[-1], hlc=YEL)
    pill(f, line, 620, t, 0.2)
    disclaimer(f)


# ── 쇼츠 1 (12:00): 연봉 1등은 사장님이 아니다 ─────────────────
def a1(f, t, sc):
    photo_bg(f, "bp_toronto", t, 0.55)
    logo_row(f, t, 40)
    big(f, "엔터 회사 연봉 1등", 190, 96)
    big(f, "27.6억", 330, 230, col=RD, o=pop(t, 0.2, 0.25))
    big(f, "그런데 사장님이 아니다", 610, 76, o=pop(t, 0.8))


def a2(f, t, sc):
    photo_bg(f, "bts_live_55161609401", t, 0.78)
    big(f, "2025년 연봉 (금감원 공시)", 30, 60)
    rank_rows(f, t, [("양현석 · YG 프로듀서", "27.6억", RD), ("박진영 · JYP 창업자", "26.6억", RD), ("이재상 · 하이브 대표", "16.5억", WH),
                     ("정욱 · JYP 대표", "15.0억", WH), ("양민석 · YG 사장", "8.4억", WH)], y0=140, t0=0.3, step=0.55)



def a3(f, t, sc):
    vbg(f, "money_count_v", t, 0.66)
    big(f, "YG 직원 평균 연봉", 120, 80)
    big(f, "5,800만 원", 250, 140, o=pop(t, 0.2))
    big(f, "양현석 프로듀서 = 47배", 470, 84, hl="47배", hlc=RD, o=pop(t, 1.0))
    K.credit(f, "영상: Hassas_Arts (Pixabay)")


def a4(f, t, sc):
    photo_bg(f, "bts_wh2", t, 0.6)
    big(f, "하이브 방시혁 의장", 140, 86)
    big(f, "연봉 5억 미만", 280, 140, col=YEL, o=pop(t, 0.2))
    big(f, "공시 명단에 이름 없음", 470, 76, o=pop(t, 0.8))


def a5(f, t, sc):
    vbg(f, "money_count_v", t, 0.66)
    big(f, "대신 배당금만", 160, 90)
    big(f, "65.8억", 300, 200, col=GRN, o=pop(t, 0.2))
    big(f, "회장님 월급은 주가", 540, 80, hl="주가", hlc=YEL, o=pop(t, 0.9))
    K.credit(f, "영상: Hassas_Arts (Pixabay) · 1,315만 주 × 2025 주당 배당 500원")


S1 = [
    {"draw": a1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "mx:2182", 0.8)],
     "narr": ["엔터 회사 연봉 1등은 27억 6천만 원. 그런데 사장님이 아니에요."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 3.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3 + 0.55 * i, "pop", 0.4) for i in range(5)],
     "narr": ["와이지 양현석 프로듀서 27.6억, 제이와이피 박진영 26.6억. 사장님들은 그 아래, 와이지 양민석 사장은 8.4억이에요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "reveal", 0.5)],
     "narr": ["와이지 직원 평균 연봉 5,800만 원의 47배죠."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "accent", 0.5)],
     "narr": ["그런데 하이브 방시혁 의장은, 연봉 5억 원이 안 돼서 공시 명단에 이름조차 없어요."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "mx:2003", 0.6)],
     "narr": ["대신 작년 배당금만 65억 8천만 원. 회장님 월급은 연봉이 아니라 주가예요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["여러분이라면 연봉 27억, 지분 1%, 뭐 고르실래요? 좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]


# ── 쇼츠 2 (21:00): BTS 컴백했는데 하이브 -45%? ─────────────────
def b1(f, t, sc):
    photo_bg(f, "bts_wh", t, 0.55)
    big(f, "BTS 컴백 · 역대 최대 실적", 150, 76)
    big(f, "주가 -45%", 290, 200, col=RD, o=pop(t, 0.3))


def b2(f, t, sc):
    vbg(f, "stock_decline_v", t, 0.66)
    big(f, "올해 엔터주 (1.2 → 11.20)", 40, 60)
    rank_rows(f, t, [("하이브", "-45.6%", RD), ("JYP", "-36.6%", RD), ("YG", "-31.6%", RD), ("SM", "-25.2%", RD)], y0=160, t0=0.2, step=0.4, gap=130)
    K.credit(f, "영상: Dimitri_K (Pixabay) · 네이버 차트 종가")


def b3(f, t, sc):
    photo_bg(f, "bts_live_55161609401", t, 0.66)
    big(f, "엔터주는", 120, 80)
    big(f, "기대로 오르고\n뉴스에 판다", 240, 120, hl="뉴스에 판다", hlc=RD, o=pop(t, 0.2))
    big(f, "컴백 직후 하루 -15.6%", 560, 70, o=pop(t, 1.0))


def b4(f, t, sc):
    photo_bg(f, "bts_wh2", t, 0.66)
    big(f, "BTS 쉬어 간다 발표 다음 날", 100, 66)
    big(f, "14만 5천 원에 샀다면", 210, 84, o=pop(t, 0.2))
    big(f, "→ 40만 원 (2.8배)", 360, 110, col=GRN, o=pop(t, 1.0))



def b5(f, t, sc):
    photo_bg(f, "aespa_klink", t, 0.62)
    logo_row(f, t, 40)
    big(f, "효자 가수\n공백기에 사고", 190, 120, hl="공백기에 사고", hlc=GRN)
    big(f, "컴백 축제에 판다", 510, 100, col=RD, o=pop(t, 0.8))


S2 = [
    {"draw": b1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "mx:2782", 0.7)],
     "narr": ["비티에스가 컴백하고 역대 최대 실적을 냈는데, 하이브 주가는 올해 -45%예요."]},
    {"draw": b2, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2 + 0.4 * i, "pop", 0.4) for i in range(4)],
     "narr": ["제이와이피 -36%, 와이지 -31%, 에스엠 -25%. 엔터 4사가 다 빠졌죠."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "fail", 0.5)],
     "narr": ["엔터주는 기대로 미리 오르고, 소식이 나오는 날 팔아요. 하이브도 컴백 직후 하루에 -15.6%였어요."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "reveal", 0.5)],
     "narr": ["반대로 비티에스가 쉬어 간다고 한 다음 날 샀다면, 14만 5천 원이 40만 원. 2.8배였죠."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.8, "accent", 0.5)],
     "narr": ["그래서 엔터주는, 효자 가수 공백기에 사고, 컴백 축제에 팔아요."]},
    {"draw": lambda f, t, sc: cta(f, t, sc, "지금 엔터주는\n공백기? 축제?", "풀버전은 채널에서"), "nohead": True, "flash": True, "min": 2.4, "gap": 0.1,
     "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)], "narr": ["지금 엔터주는 공백기일까요, 축제일까요? 좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]

def cover1(f):
    photo_bg(f, "bp_toronto", 1.0, 0.5)
    logo_row(f, 1.0, 60)
    big(f, "엔터 회사\n연봉 1등", 230, 130)
    big(f, "27.6억", 560, 260, col=RD)
    big(f, "사장님이 아니다?", 880, 100, col=YEL)


def cover2(f):
    photo_bg(f, "bts_wh", 1.0, 0.5)
    big(f, "BTS 컴백했는데", 230, 120)
    big(f, "하이브\n-45%", 420, 230, col=RD)
    big(f, "엔터주 언제 살까?", 900, 96, col=YEL)


SETS = {1: (S1, ["엔터 회사 연봉 1등", "사장님이 아니다?"], [(0, "tense"), (3, "drive")]),
        2: (S2, ["BTS 컴백했는데", "하이브 -45%?"], [(0, "tense"), (4, "hope")])}
COVERS = {1: cover1, 2: cover2}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), cover=COVERS[n], argv=sys.argv[2:], bgm_cues=cues)
