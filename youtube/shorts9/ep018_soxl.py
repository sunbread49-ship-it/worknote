"""EP018 SOXL — 9:16 전용 쇼츠 2개 (2026-11-18 12:00 · 21:00) · 색 조합 08 (CH_THEME=08: 진초록 띠 · 딥레드 상자 · 초록 테두리 멘트)
규칙: 첫 1초 가장 센 숫자 · 3초 질문 · 5초 약속 · 위쪽 제목 띠 · 중하단 큰 멘트 · Gemini Umbriel 1.12배 · 한 목소리
      · 내용 자체를 영상으로 (롤러코스터 실사 · 3D 동전 탑 · 차트) · 마무리 '친구한테 아는 척'
숫자: 롱폼 checks와 같음 (SOXL · SOXX 수정 주가, 11.17 미국 종가)

  CH_THEME=08 python3 youtube/shorts9/ep018_soxl.py 1 [--stills]   → youtube/out/ep018_soxl/shorts9/s1/short.mp4
"""
import os
os.environ.setdefault("CH_THEME", "08")
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep015_ship import K, G, T, W, H, ROOT, vbg, big, pop, bgp, disclaimer, line_chart, Image, ImageDraw, np  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep018_soxl" / "shorts9"
MEDIA = ROOT / "youtube" / "assets" / "media"
WH, GRN, RD = (251, 251, 249), (72, 176, 120), (232, 66, 62)   # 08 · 어두운 화면용 밝은 톤
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}, "SOXL": "속슬"}


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
    vbg(f, "coaster2_v", t, 0.66)
    big(f, "여러분 SOXL\n몇 % 담으셨어요?", 300, 120, hl="몇 %", hlc=RD)
    pill(f, line, 640, t, 0.2)
    disclaimer(f)


# ── 쇼츠 1 (12:00): 반도체 -35%인데 SOXL -84% ─────────────────────
def a1(f, t, sc):
    vbg(f, "coaster_v", t, 0.5)
    big(f, "반도체 -35% 동안\nSOXL은", 170, 110)
    big(f, "-84%", 440, 280, col=RD, o=pop(t, 0.1, 0.25))
    K.credit(f, "영상: josepht_007 (Pixabay)")


def a2(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 11, 11, 255)))
    clip(f, "towers_ep018.mp4", t, 40, speed=1.7)


def a3(f, t, sc):
    vbg(f, "market_crash_v", t, 0.66)
    big(f, "100에서 출발\n+10% → -10%", 130, 84)
    big(f, "지수  99", 380, 130, o=pop(t, 0.2))
    big(f, "3배  91", 560, 150, col=RD, o=pop(t, 1.0))
    K.credit(f, "영상: MrWashingt0n (Pixabay)")


def a4(f, t, sc):
    vbg(f, "coaster2_v", t, 0.6)
    big(f, "출렁일수록\n녹는다", 260, 170, hl="녹는다", hlc=RD)
    K.credit(f, "영상: ChristianBodhi (Pixabay)")


def a5(f, t, sc):
    vbg(f, "money_count_v", t, 0.62)
    big(f, "그런데 16년 데이터엔\n살아남는 방법이", 240, 100, hl="살아남는 방법", hlc=GRN)
    pill(f, "오늘 오후 4시 풀버전", 560, t, 0.3, size=70)


S1 = [
    {"draw": a1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "mx:2182", 0.8)],
     "narr": ["반도체가 35% 빠지는 동안, SOXL은 마이너스 84%."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 3.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.2, "tick", 0.4), (2.4, "fall_burn", 0.5)],
     "narr": ["6월 꼭대기에 1,000만 원씩. 반도체는 648만 원, SOXL은 163만 원만 남았어요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "ding", 0.5), (1.0, "mx:2182", 0.5)],
     "narr": ["지수가 10% 오르고 10% 빠지면 99. 3배는 91. 손해가 3배가 아니라 9배예요."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "fail", 0.35)],
     "narr": ["그래서 출렁일수록, 3배는 녹아요."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "pop", 0.5)],
     "narr": ["그런데 16년 데이터엔 살아남는 방법이 있었어요. 오늘 오후 4시 풀버전에서 정리해 드릴게요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]


# ── 쇼츠 2 (21:00): 몰빵 vs 반만 담기 16년 ─────────────────────────
def b1(f, t, sc):
    vbg(f, "casino_v", t, 0.6)
    big(f, "서학개미 11월 순매수", 170, 84)
    big(f, "68%가\nSOXL", 330, 190, hl="68%", hlc=RD, o=pop(t, 0.15))
    K.credit(f, "영상: olenchic (Pixabay)")


def b2(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 13, 13, 255)))
    big(f, "2021년 꼭대기 몰빵", 80, 80)
    line_chart(f, t, "soxl", "2021-12-27", "2026-03-31", y0=260, h=380, color=RD, upto=min(1, t / 1.6),
               marks=[("2022-10-14", "-90%", RD, 1.7, 90), ("2026-02-25", "본전까지 4년 2개월", GRN, 2.4, -80)])


def b3(f, t, sc):
    vbg(f, "money_count_v", t, 0.7)
    big(f, "16년 · 1,000만 원", 120, 80)
    big(f, "몰빵 8.2억", 270, 120, o=pop(t, 0.1))
    big(f, "최악 -90%", 420, 80, col=RD, o=pop(t, 0.5))
    big(f, "반만 담기 4.5억", 560, 120, col=GRN, o=pop(t, 1.2))
    big(f, "최악 -62%", 710, 80, o=pop(t, 1.6))
    K.credit(f, "영상: Hassas_Arts (Pixabay)")


def b4(f, t, sc):
    vbg(f, "coaster_v", t, 0.66)
    big(f, "방법은 간단", 160, 90)
    big(f, "반은 현금\n매달 반반으로", 330, 140, hl="매달 반반", hlc=GRN, o=pop(t, 0.3))
    K.credit(f, "영상: josepht_007 (Pixabay)")


def b5(f, t, sc):
    bgp(f, "charlie_munger", t, 0.5, (0.5, 0.3))
    big(f, "똑똑한 사람이 망하는 길", 160, 84)
    big(f, "술, 여자,\n레버리지", 320, 150, hl="레버리지", hlc=RD, o=pop(t, 0.3))
    big(f, "— 찰리 멍거", 680, 54, o=pop(t, 0.6))
    K.credit(f, K.credit_of("charlie_munger"))


S2 = [
    {"draw": b1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.15, "mx:2003", 0.7)],
     "narr": ["11월 서학개미가 산 미국 주식의 68%가, SOXL 하나였어요."]},
    {"draw": b2, "nohead": True, "flash": True, "min": 3.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(1.7, "fall_burn", 0.5), (2.4, "ding", 0.4)],
     "narr": ["그런데 2021년 꼭대기에 몰빵한 사람은 마이너스 90%. 본전까지 4년 2개월이 걸렸어요."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 3.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "tick", 0.4), (1.2, "reveal", 0.5)],
     "narr": ["16년 데이터로 보면, 몰빵은 8억 2천에 최악 마이너스 90%. 반만 담은 사람은 4억 5천에 최악 마이너스 62%."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "sparkle", 0.5)],
     "narr": ["방법은 간단해요. 반은 현금으로 두고, 매달 한 번 반반으로 맞추기."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "accent", 0.5)],
     "narr": ["찰리 멍거는 말했죠. 똑똑한 사람이 망하는 길은 술, 여자, 그리고 레버리지."]},
    {"draw": lambda f, t, sc: cta(f, t, sc, "풀버전은 채널에서"), "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.05, "pop", 0.6)], "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]

SETS = {1: (S1, ["반도체 -35% 동안", "SOXL은 -84%?"], [(0, "tense"), (4, "hope")]),
        2: (S2, ["SOXL 몰빵 vs 반만", "16년 뒤 결과는?"], [(0, "drive"), (3, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), argv=sys.argv[2:], bgm_cues=cues)
