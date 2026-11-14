"""EP015 조선주 — 9:16 전용 쇼츠 3개 (2026-11-14)
규칙: 첫 1초 가장 센 숫자 · 3초 질문 · 5초 약속 · 2~3초 컷 · 위쪽 제목 띠 · 큰 한 줄 자막 · Gemini 1.12배 · 움직이는 영상 배경
숫자: 롱폼 checks와 같음 (네이버 차트 종가)

  python3 youtube/shorts9/ep015_ship.py 1 [--stills]   → youtube/out/ep015_shipbuilding/shorts9/s1/short.mp4
"""
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "science"))
sys.path.insert(0, str(ROOT / "youtube"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter  # noqa: E402

import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, GOLD, MINT  # noqa: E402
from engine import data as D  # noqa: E402
from ep014_kjh import big, pop, pill, bgp, disclaimer, RED, GREEN, BLUE  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep015_shipbuilding" / "shorts9"
VID = ROOT / "youtube" / "assets" / "video"
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}}


@lru_cache(maxsize=4)
def _vframes(name, secs=12):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(VID / f"{name}.mp4"), "-t", str(secs), "-vf",
                          "fps=15,scale=360:640:force_original_aspect_ratio=increase,crop=360:640", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 640, 360, 3)


def vbg(f, name, t, dark=0.55, blur=2):
    """세로 영상 배경 (핑퐁 재생) — 2026-11-14 사용자: 움직이는 영상 배경이 볼맛이 좋다"""
    fr = _vframes(name)
    n = len(fr)
    i = int(t * 15) % (2 * n - 2)
    i = i if i < n else 2 * n - 2 - i
    im = Image.fromarray(fr[i]).resize((W, H), Image.BILINEAR)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(im).enhance(1 - dark)
    f.alpha_composite(im.convert("RGBA"))


def line_chart(f, t, series, start, end, y0=640, h=620, color=RED, upto=1.0, marks=()):
    s = D.series(series, start, end)
    x0, x1 = 80, W - 80
    lo, hi = s.min() * 0.9, s.max() * 1.05
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((40, y0 - 50, W - 40, y0 + h + 70), 30, fill=(10, 14, 26, 210))
    n = max(2, int(len(s) * upto))
    pts = [(x0 + (x1 - x0) * i / (len(s) - 1), y0 + h - h * (v - lo) / (hi - lo)) for i, v in enumerate(s.values[:n])]
    d.line(pts, fill=color + (255,), width=8, joint="curve")
    f.alpha_composite(ov)
    G.blit(f, T(start[:4], 34, (190, 196, 214), "Bold"), (x0, y0 + h + 16), 1, "lt")
    G.blit(f, T(end[:4], 34, (190, 196, 214), "Bold"), (x1, y0 + h + 16), 1, "rt")
    for date, lab, col, t0, dy in marks:
        if t < t0 or upto < 0.999:
            continue
        i = s.index.get_indexer([np.datetime64(date)], method="nearest")[0]
        x, y = pts[min(i, len(pts) - 1)]
        k = pop(t, t0)
        ImageDraw.Draw(f).ellipse((x - 14, y - 14, x + 14, y + 14), fill=col + (255,))
        G.blit(f, G.pill(lab, "Black", 52, (14, 16, 24), col, pad=(18, 8), radius=14), (x, y + dy), k, "mm")


def cta(f, t, sc):
    vbg(f, "port_aerial_v", t, 0.6)
    big(f, "여러분 생각은?", 520, 140, hl="생각은?")
    pill(f, "좋아요 누르고 친구한테도 물어보세요", 860, t, 0.4, size=50)
    disclaimer(f)


# ── 쇼츠 1: 10개월 만에 -67% · 2007년 결말 ──────────────────────
def a1(f, t, sc):
    vbg(f, "container_ship_v", t, 0.55)
    big(f, "한화오션\n10개월 만에", 260, 110)
    big(f, "-67%", 640, 330, col=RED, o=pop(t, 0.05, 0.25))


def a2(f, t, sc):
    vbg(f, "port_aerial_v", t, 0.6)
    big(f, "조선 슈퍼사이클,\n끝났을까?", 420, 140, hl="끝났을까?", hlc=RED)
    pill(f, "19년 전 결말을 보면 보여요", 860, t, 0.5, bg=MINT)


def a3(f, t, sc):
    vbg(f, "container_ship_v", t, 0.7)
    big(f, "2007년에도 슈퍼사이클", 200, 80)
    line_chart(f, t, "hanwha_ocean", "2005-01-01", "2009-06-30", upto=min(1, max(0.02, (t - 0.2) / 1.8)),
               marks=[("2007-10-16", "꼭대기", GOLD, 0.0, -70), ("2008-10-29", "1년 뒤 -86%", RED, 0.0, 70)])


def a4(f, t, sc):
    bgp(f, "ai_ships_idle", t, 0.45)
    big(f, "2007년 꼭대기에서\n1,000만 원", 220, 96)
    big(f, "1년 뒤 141만", 620, 120, col=(220, 224, 236), o=pop(t, 0.2))
    big(f, "19년 뒤 172만", 820, 150, col=RED, o=pop(t, 1.2))


def a5(f, t, sc):
    vbg(f, "port_aerial_v", t, 0.62)
    big(f, "그런데 반전", 260, 110, col=GOLD)
    big(f, "배 값은\n아직 꼭대기", 500, 160, hl="꼭대기", hlc=GREEN, o=pop(t, 0.2))
    big(f, "신조선가지수 185 · 2008년 꼭대기 190", 1000, 50, o=pop(t, 0.6))


def a6(f, t, sc):
    bgp(f, "ai_stock_ahead", t, 0.45)
    big(f, "2007년에도\n주가가 1년 먼저 꺾였다", 300, 100, hl="1년 먼저", hlc=GOLD)


S1 = [
    {"draw": a1, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "mx:2908", 0.8)], "narr": ["한화오션, 10개월 만에 마이너스 67%."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "accent_low", 0.5)],
     "narr": ["조선 슈퍼사이클, 끝난 걸까요? 19년 전 결말을 보면 보여요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.6, "fall_burn", 0.6)],
     "narr": ["2007년에도 조선은 슈퍼사이클이었어요. 그런데 꼭대기 1년 뒤, 주가는 마이너스 86%."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.2, "mx:2182", 0.8)],
     "narr": ["그 꼭대기에서 산 1,000만 원은, 19년이 지난 지금도 172만 원이에요."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "reveal", 0.6)],
     "narr": ["그런데 반전. 지금 배 값은 아직 꼭대기 근처예요."]},
    {"draw": a6, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "accent", 0.5)],
     "narr": ["2007년에도 배 값은 높았는데, 주가가 1년 먼저 꺾였거든요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["끝난 걸까요, 숨 고르기일까요? 좋아요 누르고, 친구한테도 물어보세요."]},
]


# ── 쇼츠 2: 배 값은 꼭대기인데 주가만 반 토막? ─────────────────
def b1(f, t, sc):
    vbg(f, "container_ship_v", t, 0.55)
    big(f, "배 값은 꼭대기", 300, 120, col=GREEN)
    big(f, "주가는 -67%?", 560, 150, col=RED, o=pop(t, 0.3))


def b2(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 30, 255)))
    big(f, "2007년 · 무엇이 먼저 꺾였나", 300, 70)
    for i, (y, lab, sub, col) in enumerate([(560, "2007.10", "주가 꼭대기", RED), (820, "2008.9", "배 값 꼭대기", GOLD)]):
        k = pop(t, 0.2 + i * 0.6)
        G.blit(f, T(lab, 130, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (W / 2, y), k, "mt")
        G.blit(f, T(sub, 56, CREAM, "Black"), (W / 2, y + 150), k, "mt")
    big(f, "약 1년 먼저", 1110, 90, col=GOLD, o=pop(t, 1.4))


def b3(f, t, sc):
    bgp(f, "ai_watermelon_glut", t, 0.4)
    big(f, "수박이 비싸면", 250, 110)
    big(f, "다들 심는다", 420, 150, col=GOLD, o=pop(t, 0.4))


def b4(f, t, sc):
    vbg(f, "port_aerial_v", t, 0.6)
    big(f, "주식은 지금 말고\n2~3년 뒤를 산다", 400, 120, hl="2~3년 뒤", hlc=GOLD)


def b5(f, t, sc):
    vbg(f, "container_ship_v", t, 0.68)
    big(f, "지켜볼 신호 3", 220, 110, hl="3", hlc=GOLD)
    for i, s in enumerate(["① 신조선가지수가 꺾이나", "② 주문 취소 소식", "③ 중국 조선소 증설"]):
        G.blit(f, T(s, 70, CREAM, "Black", stroke=6, stroke_fill=(0, 0, 0)), (W / 2, 460 + i * 160), pop(t, 0.3 + i * 0.5), "mt")


S2 = [
    {"draw": b1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "mx:2908", 0.7)], "narr": ["배 값은 꼭대기인데, 주가는 마이너스 67%? 이상하죠?"]},
    {"draw": b2, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "pop", 0.5), (0.8, "pop", 0.5), (1.4, "accent", 0.5)],
     "narr": ["2007년에도 그랬어요. 주가는 2007년 10월에 꼭대기, 배 값은 2008년 9월. 주가가 1년 먼저 꺾였죠."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.4, "pop", 0.5)],
     "narr": ["수박이 비싸면 다들 수박을 심잖아요. 그다음 해엔 넘쳐서 값이 떨어지고요."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "accent", 0.5)],
     "narr": ["주식시장은 지금이 아니라, 2~3년 뒤를 사고팔거든요."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "tick", 0.5), (0.8, "tick", 0.5), (1.3, "tick", 0.5)],
     "narr": ["그래서 볼 건 세 가지. 신조선가지수, 주문 취소 소식, 그리고 중국 조선소 증설이에요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["여러분은 어떻게 보세요? 좋아요 누르고, 친구한테도 물어보세요."]},
]


# ── 쇼츠 3: -20% 빠지면 판다, 이 규칙의 함정 ─────────────────────
def c1(f, t, sc):
    vbg(f, "port_aerial_v", t, 0.6)
    big(f, "-20% 빠지면 판다", 300, 120, col=RED)
    big(f, "2.09배에\n내렸다", 560, 170, col=CREAM, o=pop(t, 0.4))


def c2(f, t, sc):
    vbg(f, "container_ship_v", t, 0.7)
    big(f, "2020년 코로나 바닥에\n한화오션 매수", 220, 90)
    bars_y = 620
    for i, (lab, v, txt, col) in enumerate([("-20% 규칙 · 석 달 만에 매도", 2.09, "2.09배", (200, 206, 220)), ("그냥 보유 · 지금도", 4.91, "4.91배", GREEN)]):
        k = pop(t, 0.3 + i * 0.6, 0.5)
        y = bars_y + i * 250
        G.blit(f, T(lab, 54, CREAM, "Black"), (80, y), k, "lt")
        w = int((W - 420) * v / 5.5 * k)
        ImageDraw.Draw(f).rounded_rectangle((80, y + 80, 80 + max(8, w), y + 170), 16, fill=col + (255,))
        G.blit(f, T(txt, 74, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (100 + w, y + 125), k, "lm")


def c3(f, t, sc):
    bgp(f, "ai_alarm_early", t, 0.4)
    big(f, "너무 일찍 울린 경보", 300, 110, col=GOLD)


def c4(f, t, sc):
    bgp(f, "ai_ships_idle", t, 0.5)
    big(f, "그런데 2007년 꼭대기엔", 240, 84)
    big(f, "-30% 규칙이\n살렸다", 420, 150, col=GREEN, o=pop(t, 0.3))
    big(f, "그 뒤 -79%를 피함", 860, 80, o=pop(t, 0.9))


def c5(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 30, 255)))
    big(f, "언제 파느냐보다", 420, 110)
    big(f, "어디서 샀느냐", 620, 170, col=GOLD, o=pop(t, 0.4))


S3 = [
    {"draw": c1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "accent_low", 0.6), (0.4, "mx:2182", 0.7)],
     "narr": ["고점에서 20% 빠지면 판다. 이 규칙대로 했더니 2.09배에 내렸어요."]},
    {"draw": c2, "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "pop", 0.5), (0.9, "mx:2003", 0.6)],
     "narr": ["2020년 코로나 바닥에서 한화오션을 샀다면, 규칙은 석 달 만에 팔라고 했죠. 그냥 들고 있었다면 지금도 4.9배예요."]},
    {"draw": c3, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "sos_beep", 0.4)],
     "narr": ["너무 일찍 울린 경보였던 거예요."]},
    {"draw": c4, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "reveal", 0.6)],
     "narr": ["그런데 2007년 꼭대기 근처에선, 30% 규칙이 그 뒤 마이너스 79%를 피하게 해 줬어요."]},
    {"draw": c5, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.4, "accent", 0.5)],
     "narr": ["그러니까 사이클 주식은, 언제 파느냐보다 어디서 샀느냐가 결과를 정해요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["여러분은 손절 규칙 있으세요? 좋아요 누르고, 친구한테도 물어보세요."]},
]

SETS = {1: (S1, ["10개월 만에 -67%", "조선 슈퍼사이클의 결말"], [(0, "tense"), (4, "hope")]),
        2: (S2, ["배 값은 꼭대기인데", "주가만 반 토막?"], [(0, "tense"), (3, "hope")]),
        3: (S3, ["-20% 빠지면 판다", "이 규칙의 함정"], [(0, "tense"), (3, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), argv=sys.argv[2:], bgm_cues=cues)
