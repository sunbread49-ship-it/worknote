"""지식창고 쇼츠 · 수능 날, 대한민국이 35분 동안 멈춘다 (2026-11-18 20:00 · 수능 전날 밤)
  python3 science/csat_sky.py [--stills]
사실 (국토교통부 발표 · 2026.11.17 보도 — 파이낸셜뉴스 · 아시아경제 · MBC):
  2027학년도 수능 11.19(목) 영어 듣기평가 13:05~13:40 (35분) 전국 공항 이착륙 통제
  비상 · 긴급 항공기 빼고 이륙 금지 · 비행 중인 항공기는 지상 3km 이상 상공에서 대기 · 헬기 · 경량항공기 · 드론도 통제
  운항 시간 조정 국제선 81편 + 국내선 49편 = 130편
  한국거래소: 수능일 정규장 10:00 개장 (1시간 늦게) · 관공서 · 기업 출근 10시 이후로 · 수도권 지하철 증편
소리: 제트기 이륙 소음 가까이서 120dB 이상(어림) · 거리 2배마다 약 6dB 감소(역제곱 법칙, 어림)
규칙: 내용 자체를 영상으로(실사 · 3D 공중 대기) · 중하단 큰 멘트 · 한 목소리 · '친구한테 아는 척'
"""
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, GOLD, MINT  # noqa: E402
from drone import vbg, big, pop, pill  # noqa: E402

OUT = K.HERE / "out" / "csat_sky"
MEDIA = K.HERE.parent / "youtube" / "assets" / "media"
HEAD = {"kicker": "생활 속 과학", "title": "수능", "highlight": "수능",
        "banner": ["내일 오후 1시 5분", "대한민국이 멈춘다"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}}
CX = W / 2
RED = (240, 70, 70)
DARK = (14, 16, 24)


def clock(f, t, y, start=(13, 5), t0=0.0):
    """시계가 13:05에서 멈춤 (빨간 정지)"""
    hh, mm = start
    box = G.pill(f"{hh:02d}:{mm:02d}", "Black", 150, (255, 255, 255), (20, 22, 30), pad=(50, 20), radius=28)
    G.blit(f, box, (CX, y), pop(t, t0), "mt")
    if t > t0 + 0.5:
        G.blit(f, G.pill("STOP", "Black", 60, (255, 255, 255), RED, pad=(26, 10), radius=14).rotate(-8, expand=True),
               (CX + box.width / 2 - 30, y - 10), pop(t, t0 + 0.5), "mm")


def s_hook(f, t, sc):
    vbg(f, "runway_v", t, 0.45, 1)
    clock(f, t, 80)
    big(f, "하늘이 35분 동안", 400, 96, o=pop(t, 0.3))
    big(f, "멈춘다", 520, 170, col=RED, o=pop(t, 0.6))
    K.credit(f, "영상: Life-Of-Vids (Pixabay)")


def s_question(f, t, sc):
    vbg(f, "plane_takeoff_v", t, 0.5, 2)
    big(f, "전쟁도 아닌데\n나라 전체가 왜?", 160, 130, hl="왜?", hlc=GOLD)
    K.credit(f, "영상: Vimeo-Free-Videos (Pixabay)")


BOARD = [("인천 → 도쿄", "13:10", "13:45"), ("김포 → 제주", "13:15", "13:50"), ("인천 → 방콕", "13:20", "13:55"),
         ("제주 → 김포", "13:25", "14:00"), ("김해 → 오사카", "13:30", "14:05")]


def s_board(f, t, sc):
    """출발 안내판이 줄줄이 '시간 변경'으로 바뀜 (예시)"""
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 12, 18, 255)))
    vbg(f, "runway_v", t, 0.85, 8)
    G.blit(f, T("출발 안내 (예시)", 46, (150, 160, 180), "Bold"), (70, 40), 1, "lt")
    for i, (route, a, b) in enumerate(BOARD):
        y = 120 + i * 106
        d = ImageDraw.Draw(f)
        d.rounded_rectangle((50, y, W - 50, y + 92), 14, fill=(26, 30, 40, 255))
        G.blit(f, T(route, 46, (240, 240, 240), "Black"), (80, y + 46), 1, "lm")
        flip = t > 0.25 + i * 0.22
        G.blit(f, T(b if flip else a, 48, RED if flip else (250, 210, 90), "Black"), (W - 330, y + 46), 1, "lm")
        if flip:
            G.blit(f, G.pill("변경", "Black", 34, (255, 255, 255), RED, pad=(14, 6), radius=10), (W - 80, y + 46), pop(t, 0.25 + i * 0.22), "rm")
    if t > 1.6:
        G.blit(f, T("130편", 170, RED, "Black", stroke=9, stroke_fill=(0, 0, 0)), (CX, 640), pop(t, 1.6), "mt")


@lru_cache(maxsize=1)
def _hold_frames():
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(MEDIA / "holding_csat.mp4"), "-vf", "fps=30,scale=1080:698",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 698, 1080, 3)


def s_hold(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 24, 255)))
    fr = _hold_frames()
    f.alpha_composite(Image.fromarray(fr[min(int(t * 30), len(fr) - 1)]).convert("RGBA"), (0, 40))
    G.blit(f, G.pill("땅에서 3km 넘게 위", "Black", 50, DARK, GOLD, pad=(22, 10), radius=14), (CX, 70), pop(t, 0.2), "mt")
    G.blit(f, G.pill("시험장", "Black", 40, DARK, CREAM, pad=(18, 8), radius=12), (CX, 600), pop(t, 0.4), "mt")
    K.credit(f, "3D: Blender로 직접 제작")


def s_heli(f, t, sc):
    vbg(f, "heli_v" if t < 1.2 else "drone_hover_v", t, 0.5, 2)
    big(f, "헬기도", 200, 140, o=pop(t, 0.05))
    big(f, "드론도", 380, 140, o=pop(t, 1.2))
    big(f, "금지", 560, 170, col=RED, o=pop(t, 1.6))
    K.credit(f, "영상: Matthias_Groeneveld (Pixabay)" if t < 1.2 else "영상: orlandoalan (Pixabay)")


def s_nation(f, t, sc):
    vbg(f, "seoul_subway_tl", t, 0.62, 3)
    rows = [("출근", "10시로 늦춤"), ("주식시장", "1시간 늦게 개장"), ("지하철", "더 자주")]
    L = sc["L"]
    for i, (a, b) in enumerate(rows):
        t0 = 0.15 + i * 0.6
        k = pop(t, t0, 0.3)
        if k <= 0:
            continue
        y = 160 + i * 170
        G.blit(f, G.pill(a, "Black", 60, DARK, GOLD, pad=(24, 10), radius=14), (70, y), k, "lt")
        G.blit(f, T(b, 76, CREAM, "Black", stroke=7, stroke_fill=(0, 0, 0)), (W - 70, y + 4), k, "rt")
    K.credit(f, "영상: run2cross (Pixabay)")


DB = [("제트기 이륙 (가까이)", 120, RED), ("지하철 안", 85, GOLD), ("대화 소리", 60, CREAM), ("조용한 시험장", 30, MINT)]


def s_why(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 24, 255)))
    vbg(f, "exam_write_v", t, 0.78, 6)
    big(f, "영어 듣기평가 35분", 40, 84, hl="듣기평가")
    for i, (lab, db, col) in enumerate(DB):
        k = pop(t, 0.2 + i * 0.3, 0.3)
        if k <= 0:
            continue
        y = 210 + i * 120
        G.blit(f, T(lab, 44, CREAM, "Bold"), (70, y), k, "lt")
        g = G.clamp((t - 0.2 - i * 0.3) / 0.6)
        w = int((W - 360) * db / 120 * g)
        ImageDraw.Draw(f).rounded_rectangle((70, y + 56, 70 + max(10, w), y + 96), 12, fill=col + (255,))
        G.blit(f, T(f"{db}dB", 48, col, "Black", stroke=5, stroke_fill=(0, 0, 0)), (90 + max(10, w), y + 76), min(1, g * 2), "lm")
    L = sc["L"]
    if len(L) > 1 and t > L[1]:
        G.blit(f, G.pill("거리 2배 → 6dB 작아짐", "Black", 54, DARK, MINT, pad=(24, 10), radius=14), (CX, 700), pop(t, L[1]), "mt")
    K.credit(f, "영상: Dx21 (Pixabay) · 데시벨은 어림값")


def s_end(f, t, sc):
    vbg(f, "plane_wing_v", t, 0.5, 2)
    big(f, "수험생의 35분을 위해", 180, 90)
    big(f, "나라 전체가\n숨을 죽인다", 330, 140, hl="숨을 죽인다", hlc=GOLD, o=pop(t, 0.3))
    K.credit(f, "영상: Trek_Jason (Pixabay)")


def s_cta(f, t, sc):
    vbg(f, "exam_night_v", t, 0.55, 3)
    big(f, "수험생 친구한테\n응원 한마디!", 140, 130, hl="응원 한마디!")
    pill(f, "좋아요 누르고 친구한테 아는 척!", CX, 560, t, 0.4, size=52)
    K.credit(f, "영상: MrWashingt0n (Pixabay)")


def draw_cover(f):
    vbg(f, "runway_v", 1.0, 0.45, 1)
    clock(f, 2.0, 80)
    big(f, "하늘이 35분 동안", 400, 96)
    big(f, "멈춘다", 520, 170, col=RED)


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.5, "mx:2182", 0.7)],
     "narr": ["내일 오후 1시 5분, / 대한민국 하늘이 35분 동안 멈춰요."]},
    {"draw": s_question, "flash": True, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "ding", 0.5)],
     "narr": ["전쟁도 아닌데, / 나라 전체가 왜 이럴까요?"]},
    {"draw": s_board, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.25 + 0.22 * i, "tick", 0.4) for i in range(5)] + [(1.6, "accent", 0.6)],
     "narr": ["이 시간엔 이륙이 전부 금지. / 국제선 81편, 국내선 49편, / 모두 130편이 시간을 바꿔요."]},
    {"draw": s_hold, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.2, "flyby", 0.5)],
     "narr": ["이미 날고 있던 비행기는, / 땅에서 3km 넘게 떨어진 하늘에서 빙빙 돌며 기다려요."]},
    {"draw": s_heli, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.6, "fail", 0.4)],
     "narr": ["헬기도, / 드론도 못 떠요."]},
    {"draw": s_nation, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.15,
     "sfx_t": [(0.15 + 0.6 * i, "pop", 0.45) for i in range(3)],
     "narr": ["출근은 10시로 늦춰지고, / 주식시장까지 1시간 늦게 열려요."]},
    {"draw": s_why, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.2 + 0.3 * i, "tick", 0.4) for i in range(4)] + [(sc["L"][1], "reveal", 0.5)],
     "narr": ["이유는 딱 하나, 영어 듣기평가. / 제트기 소리는 가까이서 120데시벨이 넘거든요.",
              "거리가 두 배 멀어질 때마다 소리는 6데시벨씩 줄어서, / 높이 떠 있어야 시험장까지 안 들려요."]},
    {"draw": s_end, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.3, "sparkle", 0.5)],
     "narr": ["수험생들의 35분을 위해, / 나라 전체가 숨을 죽이는 거죠."]},
    {"draw": s_cta, "flash": True, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.45, "pop", 0.6)],
     "narr": ["수험생 친구한테 응원 한마디! / " + K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.15,
     "narr": ["내일 오후 1시 5분, / 대한민국 하늘이 35분 동안 멈춰요."]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "tense"), (5, "drive"), (8, "hope")])
