"""EP020 서학개미 연말 절세 — 9:16 전용 쇼츠 2개 (2026-11-20 12:00 · 21:00) · 색 조합 08 (CH_THEME=08: 진초록 띠 · 딥레드 상자 · 초록 테두리 멘트)
규칙: 첫 1초 가장 센 숫자 · 3초 질문 · 5초 약속 · 위쪽 제목 띠 · 중하단 큰 멘트 · Gemini Umbriel 1.12배 · 한 목소리
      · 내용 자체를 영상으로 (롤러코스터 실사 · 3D 동전 탑 · 차트) · 마무리 '친구한테 아는 척'
숫자: 롱폼과 같음 (250만 원 공제 · 22% · 손익통산 · 결제일 기준 · QQQ 10년 422만 원)

  CH_THEME=08 python3 youtube/shorts9/ep020_tax.py 1 [--stills]   → youtube/out/ep020_year_end_tax/shorts9/s1/short.mp4
"""
import os
os.environ.setdefault("CH_THEME", "08")
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep015_ship import K, G, T, W, H, ROOT, vbg, big, pop, bgp, disclaimer, line_chart, Image, ImageDraw, np  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep020_year_end_tax" / "shorts9"
MEDIA = ROOT / "youtube" / "assets" / "media"
WH, GRN, RD = (251, 251, 249), (72, 176, 120), (232, 66, 62)
CXS = 540   # 08 · 어두운 화면용 밝은 톤
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}, "QQQ": "큐큐큐", "SOXL": "속슬"}


def pill(f, text, y, t, t0=0.0, size=56):
    p = G.pill(text, "Black", size, WH, (1, 66, 43), pad=(30, 12), radius=12)
    G.blit(f, p, (W / 2, y), pop(t, t0), "mt")


@lru_cache(maxsize=2)
def _clip_frames(name, w=1080):
    src = MEDIA / name if (MEDIA / name).exists() else MEDIA.parent / "video" / name
    h = int(w * (1080 * 0.95) / (1920 * 0.70)) // 2 * 2
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(src), "-vf",
                          f"fps=30,crop=iw*0.70:ih*0.95:iw*0.15:0,scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


@lru_cache(maxsize=2)
def _full_frames(name, w=960, h=540):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(MEDIA.parent / "video" / name), "-t", "12", "-vf", f"fps=30,scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def clip(f, name, t, y, speed=1.0):
    fr = _clip_frames(name)
    i = min(int(t * 30 * speed), len(fr) - 1)
    f.alpha_composite(Image.fromarray(fr[i]).convert("RGBA"), (0, y))


def cta(f, t, sc, line="풀버전은 오늘 오후 4시"):
    vbg(f, "liberty_v", t, 0.6)
    big(f, "올해 미국 주식\n플러스? 마이너스?", 300, 120, hl="마이너스?", hlc=RD)
    pill(f, line, 640, t, 0.2)
    disclaimer(f)


# ── 쇼츠 1 (12:00): 250만 원 쿠폰이 불탄다 ─────────────────────
def a1(f, t, sc):
    vbg(f, "paper_burn_v", t, 0.3)
    big(f, "서학개미가 매년\n그냥 태우는 돈", 160, 96)
    big(f, "250만 원", 440, 220, col=RD, o=pop(t, 0.2, 0.25))
    K.credit(f, "영상: konstantinrotkevich (Pixabay)")


def a2(f, t, sc):
    vbg(f, "accountant_v", t, 0.7)
    big(f, "미국 주식 세금", 90, 80)
    big(f, "1년에 250만 원까지 0원", 220, 84, col=GRN, o=pop(t, 0.2))
    big(f, "넘는 부분만 22%", 360, 84, o=pop(t, 0.9))
    big(f, "안 팔면 쿠폰은 소멸", 500, 84, col=RD, o=pop(t, 1.6))
    K.credit(f, "영상: RainMeditateHub (Pixabay)")


def a3(f, t, sc):
    vbg(f, "money_count_v", t, 0.66)
    big(f, "12월에 250만 원어치\n팔고 바로 다시 사기", 120, 86, hl="바로 다시 사기", hlc=GRN)
    big(f, "QQQ 10년\n세금 422만 원 차이", 400, 110, hl="422만 원", hlc=RD, o=pop(t, 0.8))
    K.credit(f, "영상: Hassas_Arts (Pixabay)")


def a4(f, t, sc):
    vbg(f, "calc_surprise_v", t, 0.55)
    big(f, "올해 마감", 160, 90)
    big(f, "12월 29일", 300, 190, col=RD, o=pop(t, 0.2))
    big(f, "(미국 현지 · 결제일 기준)", 520, 56, o=pop(t, 0.6))
    K.credit(f, "영상: conte_public (Pixabay)")


def a5(f, t, sc):
    vbg(f, "liberty_v", t, 0.62)
    big(f, "그런데 올해처럼\n빠진 해가 찬스?", 220, 110, hl="찬스?", hlc=GRN)
    pill(f, "오늘 오후 4시 풀버전", 560, t, 0.3, size=70)
    K.credit(f, "영상: Activedia (Pixabay)")


S1 = [
    {"draw": a1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "mx:2182", 0.8)],
     "narr": ["미국 주식 하는 분들, 매년 250만 원짜리 쿠폰을 그냥 태워요."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "pop", 0.4), (0.9, "pop", 0.4), (1.6, "fail", 0.4)],
     "narr": ["1년에 번 돈 250만 원까지는 세금이 0원이에요. 그런데 그해 안 팔면, 이 쿠폰은 그냥 사라져요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.8, "reveal", 0.5)],
     "narr": ["12월에 250만 원어치만 팔았다가 바로 다시 사면, 큐큐큐 10년 기준 세금이 422만 원 줄어요."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "accent", 0.5)],
     "narr": ["올해 마감은 미국 현지 12월 29일이에요."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "pop", 0.5)],
     "narr": ["그리고 올해처럼 빠진 해가 오히려 찬스인 이유, 오늘 오후 4시 풀버전에서 알려 드릴게요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]


# ── 쇼츠 2 (21:00): 마이너스가 쿠폰이 된다 ──────────────────────
def b1(f, t, sc):
    vbg(f, "stock_decline_v", t, 0.6)
    big(f, "미국 주식 마이너스?", 180, 100)
    big(f, "오히려 찬스", 360, 170, col=GRN, o=pop(t, 0.3))
    K.credit(f, "영상: Dimitri_K (Pixabay)")


def b2(f, t, sc):
    vbg(f, "accountant_v", t, 0.72)
    big(f, "엔비디아 +700만", 140, 110, col=GRN, o=pop(t, 0.1))
    big(f, "SOXL -700만", 300, 110, col=RD, o=pop(t, 0.8))
    big(f, "= 올해 번 돈 0원", 470, 110, o=pop(t, 1.6))
    K.credit(f, "영상: RainMeditateHub (Pixabay)")


def b3(f, t, sc):
    vbg(f, "money_count_v", t, 0.7)
    big(f, "내년 5월 세금", 120, 80)
    big(f, "99만 원", 260, 150, col=RD, o=pop(t, 0.1))
    big(f, "↓", 420, 100, o=pop(t, 0.7))
    big(f, "0원", 530, 170, col=GRN, o=pop(t, 1.0))
    K.credit(f, "영상: Hassas_Arts (Pixabay)")


def b4(f, t, sc):
    vbg(f, "liberty_v", t, 0.62)
    big(f, "손실 주식 팔고\n같은 날 다시 사기", 160, 110, hl="같은 날 다시 사기", hlc=GRN)
    big(f, "주식은 그대로 · 세금만 0원", 480, 70, col=GRN, o=pop(t, 0.8))
    K.credit(f, "영상: Activedia (Pixabay)")


def b5(f, t, sc):
    vbg(f, "calc_surprise_v", t, 0.55)
    big(f, "마감", 160, 90)
    big(f, "12월 29일", 300, 190, col=RD, o=pop(t, 0.2))
    big(f, "(미국 현지 · 증권사 공지 확인)", 520, 52, o=pop(t, 0.6))
    K.credit(f, "영상: conte_public (Pixabay)")


S2 = [
    {"draw": b1, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "mx:2003", 0.7)],
     "narr": ["올해 미국 주식이 마이너스라면, 오히려 찬스예요."]},
    {"draw": b2, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "pop", 0.4), (0.8, "pop", 0.4), (1.6, "ding", 0.5)],
     "narr": ["세금은 같은 해 이익과 손실을 더해서 매겨요. 엔비디아로 700만 원 벌고 SOXL로 700만 원 잃으면, 올해 번 돈은 0원."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "reveal", 0.5)],
     "narr": ["그래서 내년 5월 세금이 99만 원에서 0원이 돼요."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "sparkle", 0.5)],
     "narr": ["손실 난 주식을 팔고 같은 날 다시 사면, 주식은 그대로인데 세금만 0원이죠."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.2, "accent", 0.5)],
     "narr": ["마감은 미국 현지 12월 29일. 증권사 공지 꼭 확인하세요."]},
    {"draw": lambda f, t, sc: cta(f, t, sc, "풀버전은 채널에서"), "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.05, "pop", 0.6)], "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]

SETS = {1: (S1, ["미국 주식 세금", "매년 250만 원 날린다?"], [(0, "tense"), (3, "hope")]),
        2: (S2, ["미국 주식 마이너스?", "세금 0원 찬스"], [(0, "drive"), (2, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), argv=sys.argv[2:], bgm_cues=cues)
