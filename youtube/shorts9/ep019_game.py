"""EP019 펄어비스 · 게임주 — 9:16 전용 쇼츠 2개 (2026-11-19 12:00 · 21:00) · 색 조합 08 (CH_THEME=08: 진초록 띠 · 딥레드 상자 · 초록 테두리 멘트)
규칙: 첫 1초 가장 센 숫자 · 3초 질문 · 5초 약속 · 위쪽 제목 띠 · 중하단 큰 멘트 · Gemini Umbriel 1.12배 · 한 목소리
      · 내용 자체를 영상으로 (롤러코스터 실사 · 3D 동전 탑 · 차트) · 마무리 '친구한테 아는 척'
숫자: 롱폼과 같음 (네이버 차트 일별 종가 · 대작 11개 출시 전후)

  CH_THEME=08 python3 youtube/shorts9/ep019_game.py 1 [--stills]   → youtube/out/ep019_game_stocks/shorts9/s1/short.mp4
"""
import os
os.environ.setdefault("CH_THEME", "08")
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep015_ship import K, G, T, W, H, ROOT, vbg, big, pop, bgp, disclaimer, line_chart, Image, ImageDraw, np  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep019_game_stocks" / "shorts9"
MEDIA = ROOT / "youtube" / "assets" / "media"
WH, GRN, RD = (251, 251, 249), (72, 176, 120), (232, 66, 62)   # 08 · 어두운 화면용 밝은 톤
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}}


def pill(f, text, y, t, t0=0.0, size=56):
    p = G.pill(text, "Black", size, WH, (1, 66, 43), pad=(30, 12), radius=12)
    G.blit(f, p, (W / 2, y), pop(t, t0), "mt")


@lru_cache(maxsize=2)
def _clip_frames(name, w=1080):
    h = int(w * (1080 * 0.95) / (1920 * 0.70)) // 2 * 2
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(MEDIA / name), "-vf",
                          f"fps=30,crop=iw*0.70:ih*0.95:iw*0.15:0,scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def clip(f, name, t, y, speed=1.0):
    fr = _clip_frames(name)
    i = min(int(t * 30 * speed), len(fr) - 1)
    f.alpha_composite(Image.fromarray(fr[i]).convert("RGBA"), (0, y))


def cta(f, t, sc, line="풀버전은 오늘 오후 4시"):
    vbg(f, "gamepad_v", t, 0.66)
    big(f, "여러분은 어떤 게임\n기다리세요?", 300, 120, hl="어떤 게임", hlc=RD)
    pill(f, line, 640, t, 0.2)
    disclaimer(f)


# ── 쇼츠 1 (12:00): 600만 장인데 -60% ─────────────────────
def a1(f, t, sc):
    vbg(f, "gamepad_v", t, 0.5)
    big(f, "600만 장 팔린 게임\n펄어비스 주가는", 170, 100)
    big(f, "-60%", 440, 280, col=RD, o=pop(t, 0.1, 0.25))
    K.credit(f, "영상: zakariacomputer222 (Pixabay)")


def a2(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 13, 13, 255)))
    big(f, "펄어비스 주가", 50, 76)
    big(f, "출시 직전 6만 5,600원", 150, 66, col=GRN, o=pop(t, 1.0))
    line_chart(f, t, "pearlabyss", "2025-09-19", "2026-11-18", y0=300, h=330, color=RD, upto=min(1, t / 1.6),
               marks=[("2026-03-19", "-30%", RD, 1.7, 90), ("2026-11-18", "2만 8,600", RD, 2.3, -70)])


def a3(f, t, sc):
    vbg(f, "game_over_v", t, 0.3)
    big(f, "리뷰 공개 날", 200, 100)
    big(f, "하루 -30%", 360, 170, col=RD, o=pop(t, 0.2))
    K.credit(f, "영상: SlimeyFox (Pixabay)")


def a4(f, t, sc):
    vbg(f, "market_crash_v", t, 0.66)
    big(f, "대작 게임 11개\n출시 전날 샀다면", 120, 90)
    big(f, "1년 뒤\n9개 마이너스", 380, 140, hl="9개 마이너스", hlc=RD, o=pop(t, 0.4))
    K.credit(f, "영상: MrWashingt0n (Pixabay)")


def a5(f, t, sc):
    vbg(f, "money_count_v", t, 0.62)
    big(f, "그럼 게임주는\n언제 사야 할까?", 240, 110, hl="언제", hlc=GRN)
    pill(f, "오늘 오후 4시 풀버전", 560, t, 0.3, size=70)


S1 = [
    {"draw": a1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "mx:2182", 0.8)],
     "narr": ["600만 장 팔린 붉은사막, 펄어비스 주가는 꼭대기에서 마이너스 60%."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 3.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(1.7, "fall_burn", 0.5)],
     "narr": ["출시 직전엔 6만 5,600원까지 올랐는데, 지금은 2만 8,600원이에요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "fail", 0.4)],
     "narr": ["리뷰 점수가 공개된 날, 하루 만에 30%가 빠졌죠."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.4, "mx:2182", 0.5)],
     "narr": ["대작 게임 11개를 출시 전날 샀다면, 1년 뒤 9개가 마이너스였어요."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "pop", 0.5)],
     "narr": ["그럼 게임주는 언제 사야 할까요? 오늘 오후 4시 풀버전에서 정리해 드릴게요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]


# ── 쇼츠 2 (21:00): 6달 전에 사서 2주 전에 판다 ────────────────
def b1(f, t, sc):
    vbg(f, "gaming_setup_v", t, 0.6)
    big(f, "게임주 꼭대기는", 200, 100)
    big(f, "출시 전", 360, 190, col=RD, o=pop(t, 0.2))
    K.credit(f, "영상: Graphitage1 (Pixabay)")


def b2(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 11, 11, 255)))
    clip(f, "towers_ep019.mp4", t, 40, speed=1.7)


def b3(f, t, sc):
    vbg(f, "money_count_v", t, 0.7)
    big(f, "대작 11개 · 1,000만 원", 120, 76)
    big(f, "출시 전날 사면", 260, 96, o=pop(t, 0.1))
    big(f, "1년 뒤 -29%", 380, 130, col=RD, o=pop(t, 0.4))
    big(f, "6달 전 사서 2주 전 팔면", 560, 80, o=pop(t, 1.2))
    big(f, "+29%", 680, 150, col=GRN, o=pop(t, 1.6))
    K.credit(f, "영상: Hassas_Arts (Pixabay) · 중간값")


def b4(f, t, sc):
    vbg(f, "gamepad_v", t, 0.66)
    big(f, "게임주는", 120, 90)
    big(f, "6달 전에 사고\n2주 전에 판다", 260, 130, hl="2주 전에 판다", hlc=GRN, o=pop(t, 0.3))
    K.credit(f, "영상: zakariacomputer222 (Pixabay)")


def b5(f, t, sc):
    vbg(f, "game_over_v", t, 0.35)
    big(f, "소문에 사서", 240, 140, o=pop(t, 0.1))
    big(f, "출시에 판다", 420, 140, col=GRN, o=pop(t, 0.5))
    K.credit(f, "영상: SlimeyFox (Pixabay)")


S2 = [
    {"draw": b1, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "mx:2003", 0.7)],
     "narr": ["게임주 꼭대기는, 출시 전이었어요."]},
    {"draw": b2, "nohead": True, "flash": True, "min": 3.6, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.2, "tick", 0.4), (2.6, "reveal", 0.5)],
     "narr": ["펄어비스를 6달 전에 사서 출시 직전에 판 사람은 1,890만 원. 출시 날 산 사람은 689만 원이에요."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 3.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.4, "mx:2182", 0.5), (1.6, "ding", 0.5)],
     "narr": ["대작 11개로 봐도, 출시 전날 사면 1년 뒤 마이너스 29%. 6달 전에 사서 2주 전에 팔면 플러스 29%."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "sparkle", 0.5)],
     "narr": ["그러니까 게임주는, 6달 전에 사고 2주 전에 파는 거예요."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.1, "pop", 0.5), (0.5, "accent", 0.5)],
     "narr": ["소문에 사서, 출시에 판다."]},
    {"draw": lambda f, t, sc: cta(f, t, sc, "풀버전은 채널에서"), "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.05, "pop", 0.6)], "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]

SETS = {1: (S1, ["600만 장 팔렸는데", "펄어비스 -60%?"], [(0, "tense"), (4, "hope")]),
        2: (S2, ["게임주 이렇게 사라", "6달 전 사서 2주 전 판다"], [(0, "drive"), (3, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), argv=sys.argv[2:], bgm_cues=cues)
