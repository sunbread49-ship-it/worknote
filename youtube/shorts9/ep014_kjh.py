"""EP014 김장훈 국민연금 — 9:16 전용 쇼츠 3개 (2026-11-14 사용자 결정: 롱폼 잘라 쓰기 대신 전용 제작)
인트로 규칙: 첫 1초 = 가장 강한 숫자 화면 가득 · 3초 안 갈등 질문 · 5초 안 약속 · 2~3초 빠른 컷 · Gemini 음성(빠르게)
숫자는 롱폼 checks와 같음 (engine/data.py nps_dca · 2026 A값 319만 원 · 1996.11~2026.10)

  python3 youtube/shorts9/ep014_kjh.py 1 [--stills]     → youtube/out/ep014_pension_kjh/shorts9/s1/short.mp4
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "science"))
sys.path.insert(0, str(ROOT / "youtube"))
from PIL import Image, ImageDraw  # noqa: E402

import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, CORAL, GOLD, MINT  # noqa: E402
from engine import data as D  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep014_pension_kjh" / "shorts9"
PEOPLE = ROOT / "youtube" / "assets" / "people"
RED, GREEN, BLUE = (255, 76, 76), (90, 220, 150), (96, 168, 255)
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게"}, "S&P500": "에스앤피 오백"}


def cut(name, h):
    im = Image.open(PEOPLE / f"{name}.png").convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def bgp(f, name, t, dark=0.55, focus=(0.5, 0.5), zoom=0.06):
    """화면 가득 사진 + 천천히 줌"""
    z = 1 + zoom * min(1, t / 3)
    im = K.photo(name, int(W * z), int(H * z), focus, dark)
    f.alpha_composite(im, (int((W - im.width) / 2), int((H - im.height) / 2)))


def big(f, text, y, size=150, col=CREAM, hl="", hlc=GOLD, o=1.0, anchor="mt"):
    im = T(text, size, col, "Black", highlight=hl, hl_fill=hlc, align="center", line_gap=1.08, stroke=8, stroke_fill=(0, 0, 0))
    G.blit(f, im, (W / 2, y), o, anchor)
    return im


def pop(t, t0=0.0, d=0.25):
    return G.ease_out((t - t0) / d)


def pill(f, text, y, t, t0=0.0, bg=GOLD, fg=(14, 16, 24), size=54):
    p = G.pill(text, "Black", size, fg, bg, pad=(30, 12), radius=18)
    G.blit(f, p, (W / 2, y), pop(t, t0), "mt")


def person(f, name, h, x, t, t0=0.0, y_bottom=H + 30):
    fig = cut(name, h)
    k = pop(t, t0, 0.35)
    G.blit(f, fig, (x, y_bottom + (1 - k) * 80), k, "mb")


def chart(f, t, y0=520, h=700, upto=1.0, lines=(("nps_spx", RED, "S&P500"), ("nps_kospi", GOLD, "코스피"), ("nps_paid", (200, 206, 220), "낸 돈"))):
    """30년 적립 곡선 (만 원) · upto: 그려진 비율"""
    x0, x1 = 90, W - 90
    vmax = 31000
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((50, y0 - 60, W - 50, y0 + h + 60), 30, fill=(10, 14, 26, 200))
    for nm, col, lab in lines:
        s = D.series(nm)
        n = max(2, int(len(s) * upto))
        pts = [(x0 + (x1 - x0) * i / (len(s) - 1), y0 + h - h * v / vmax) for i, v in enumerate(s.values[:n])]
        d.line(pts, fill=col + (255,), width=9, joint="curve")
        if upto >= 0.999:
            v = s.values[-1]
            txt = f"{lab} {v / 1e4:.2f}억" if v >= 1e4 else f"{lab} {v:,.0f}만"
            G.blit(ov, G.pill(txt, "Black", 40, (14, 16, 24), col, pad=(16, 6), radius=12), (x1 - 10, pts[-1][1] - 10), 1, "rb")
    f.alpha_composite(ov)
    G.blit(f, T("1996", 34, (190, 196, 214), "Bold"), (x0, y0 + h + 14), 1, "lt")
    G.blit(f, T("2026", 34, (190, 196, 214), "Bold"), (x1, y0 + h + 14), 1, "rt")


def bars(f, t, rows, y0=620, vmax=3.2, t0=0.2):
    for i, (lab, v, txt, col) in enumerate(rows):
        k = pop(t, t0 + i * 0.35, 0.5)
        y = y0 + i * 210
        G.blit(f, T(lab, 50, CREAM, "Black"), (90, y), k, "lt")
        w = int((W - 420) * v / vmax * k)
        ImageDraw.Draw(f).rounded_rectangle((90, y + 72, 90 + max(8, w), y + 150), 14, fill=col + (255,))
        G.blit(f, T(txt, 64, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (110 + w, y + 111), k, "lm")


def pyramid(f, t, layers, cx=W / 2, base=1350, hh=150, wb=900, wt=260, t0s=(0.1, 99, 99), ghost=False):
    for i, (lab, txt, col) in enumerate(layers):
        k = pop(t, t0s[i], 0.4)
        if k <= 0:
            continue
        yb, yt = base - i * (hh + 14), base - i * (hh + 14) - hh
        wbi, wti = wb - i * (wb - wt) / 3, wb - (i + 1) * (wb - wt) / 3
        yo = (1 - k) * 60
        ImageDraw.Draw(f).polygon([(cx - wbi / 2, yb + yo), (cx + wbi / 2, yb + yo), (cx + wti / 2, yt + yo), (cx - wti / 2, yt + yo)], fill=col + (255,))
        G.blit(f, T(lab, 52, (14, 16, 24), "Black"), (cx, (yb + yt) / 2 + yo), k, "mm")
        G.blit(f, T(txt, 60, col, "Black", stroke=6, stroke_fill=(0, 0, 0)), (cx + wbi / 2 + 20, (yb + yt) / 2 + yo), k, "lm")
    if ghost:
        yt = base - 3 * (hh + 14) + 14
        d = ImageDraw.Draw(f)
        for j in range(0, 20, 2):
            for (xa, ya), (xb, yb2) in (((cx - wt / 2, yt), (cx, yt - 200)), ((cx, yt - 200), (cx + wt / 2, yt))):
                d.line([(xa + (xb - xa) * j / 20, ya + (yb2 - ya) * j / 20), (xa + (xb - xa) * (j + 1) / 20, ya + (yb2 - ya) * (j + 1) / 20)], fill=(236, 240, 248, 200), width=6)
        G.blit(f, T("연예인급", 40, (220, 224, 236), "ExtraBold"), (cx, yt - 80), 1, "mm")


def disclaimer(f):
    G.blit(f, T("투자 교육 목적 · 특정 상품 추천 아님 · 과거 수익이 미래를 보장하지 않음", 28, (170, 176, 196), "SemiBold"), (W / 2, H - 70), 1, "mb")


def cta(f, t, sc):
    bgp(f, "pensioner_bench", t, 0.6)
    big(f, "내 연금은\n얼마일까?", 520, 150, hl="얼마일까?")
    pill(f, "좋아요 누르고 친구한테도 물어보세요", 1000, t, 0.4, size=50)
    disclaimer(f)


# ── 쇼츠 1: 그 돈, S&P500에 넣었다면 ─────────────────────────────
def a1(f, t, sc):
    bgp(f, "krw_coins", t, 0.5, (0.5, 0.4))
    big(f, "내 국민연금,\n주식이었다면?", 200, 110, hl="주식")
    k = pop(t, 0.05, 0.3)
    v = 0.65 + (2.89 - 0.65) * min(1, t / 1.0)
    big(f, "6,468만", 700, 150, col=(220, 224, 236), o=k)
    big(f, "↓", 880, 110, col=GOLD, o=k)
    big(f, f"{v:.2f}억", 1010, 250, col=RED, o=k)


def a2(f, t, sc):
    bgp(f, "seoul_subway", t, 0.6)
    person(f, "kimjanghoon_cut", 1100, W * 0.66, t, 0.05)
    big(f, "국민연금,\n손해일까?", 260, 160, hl="손해일까?", hlc=RED)
    pill(f, "끝까지 보면 답이 나와요", 760, t, 0.6, bg=MINT)


def a3(f, t, sc):
    bgp(f, "seoul_night_still", t, 0.55)
    person(f, "kimjanghoon_cut", 1150, W * 0.5, t, 0.0)
    q = T("“한 달에?\n그렇게 많이 줘요?”", 110, MINT, "Black", align="center", stroke=8, stroke_fill=(0, 0, 0))
    G.blit(f, q, (W / 2, 230), pop(t, 0.15), "mt")
    pill(f, "김장훈 · 예상 연금 듣고", 560, t, 0.4, bg=(236, 240, 248))


def a4(f, t, sc):
    bgp(f, "stock_monitor", t, 0.78)
    big(f, "30년 낸 보험료를\n낼 때마다 주식에", 170, 92, hl="주식에")
    chart(f, t, upto=min(1.0, max(0.02, (t - 0.2) / 2.4)))


def a5(f, t, sc):
    bgp(f, "krw_coins", t, 0.62)
    chart(f, t, y0=900, h=520)
    big(f, "S&P500이었다면", 260, 100)
    big(f, "2억 8,896만 원", 420, 150, col=RED, o=pop(t, 0.1))


def a6(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 30, 255)))
    big(f, "그런데", 520, 120, col=(200, 206, 220))
    big(f, "연금으로\n받으면?", 700, 200, hl="받으면?", hlc=GREEN, o=pop(t, 0.25))


def a7(f, t, sc):
    bgp(f, "pensioner_bench", t, 0.66)
    big(f, "월 103만 원 × 평생", 230, 96, hl="평생", hlc=GREEN)
    bars(f, t, [("코스피 적립", 2.02, "2.02억", GOLD), ("연금 (21.7년)", 2.68, "2.68억", GREEN), ("S&P500 적립", 2.89, "2.89억", RED)], y0=560)


def a8(f, t, sc):
    bgp(f, "pensioner_bench", t, 0.5)
    big(f, "회사가 절반을 내 주니까", 300, 80)
    big(f, "내 몫의\n8배", 520, 260, col=GREEN, o=pop(t, 0.15))
    big(f, "내 돈 3,234만 → 연금 2.68억", 1120, 64, col=CREAM, o=pop(t, 0.5))


S1 = [
    {"draw": a1, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "mx:2003", 0.7), (0.9, "accent_low", 0.6)],
     "narr": ["내가 낸 국민연금 6천5백만 원, 주식에 넣었으면 2억 9천만 원?"]},
    {"draw": a2, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "accent", 0.5)],
     "narr": ["그럼 국민연금, 손해 본 걸까요? 끝까지 보면 답이 나와요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "pop", 0.5)],
     "narr": ["가수 김장훈 씨는 예상 연금을 듣고, 그렇게 많이 주냐고 놀랐죠."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "riser", 0.35)],
     "narr": ["평균 직장인이 30년 동안 낸 보험료를, 낼 때마다 S&P500에 넣었다면,"]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "mx:1936", 0.8)],
     "narr": ["지금 2억 8천9백만 원이에요."]},
    {"draw": a6, "nohead": True, "flash": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.25, "accent_low", 0.6)],
     "narr": ["그런데, 연금으로 받으면 얘기가 달라져요."]},
    {"draw": a7, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "pop", 0.4), (0.55, "pop", 0.4), (0.9, "mx:2841", 0.6)],
     "narr": ["한 달 103만 원씩 평생 받으면 2억 6천8백만 원. S&P500이랑 거의 비슷해요."]},
    {"draw": a8, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.15, "mx:1999", 0.8), (0.4, "sparkle", 0.5)],
     "narr": ["회사가 절반을 내 주니까, 내 돈만 보면 8배예요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["여러분의 연금은 얼마일까요? 좋아요 누르고, 친구한테도 물어보세요."]},
]


# ── 쇼츠 2: 연예인 vs 직장인 ────────────────────────────────────
def badge(name, d=380, ring=GOLD):
    from PIL import Image as I
    fig = cut(name, int(d * 1.15))
    c = I.new("RGBA", (d, d), (30, 34, 48, 255))
    c.alpha_composite(fig, ((d - fig.width) // 2, int(d * 0.08)))
    m = I.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    c.putalpha(m)
    o = I.new("RGBA", (d + 24, d + 24), (0, 0, 0, 0))
    ImageDraw.Draw(o).ellipse((0, 0, d + 23, d + 23), fill=ring + (255,))
    o.alpha_composite(c, (12, 12))
    return o


def vs_top(f, t, show_nums=False, lt="연예인 · 프리랜서", rt="평범한 직장인"):
    G.blit(f, badge("kimjanghoon_cut", ring=BLUE), (W * 0.27, 420), pop(t, 0.0), "mt")
    G.blit(f, badge("worker_stressed_cut", ring=CORAL), (W * 0.73, 420), pop(t, 0.1), "mt")
    big(f, "VS", 610, 120, col=GOLD)
    for x, s in ((W * 0.27, lt), (W * 0.73, rt)):
        G.blit(f, G.pill(s, "Black", 44, (14, 16, 24), (236, 240, 248), pad=(20, 8), radius=12), (x, 840), 1, "mt")


def b1(f, t, sc):
    bgp(f, "noryangjin_cross", t, 0.65)
    big(f, "국민연금, 낸 돈 대비", 170, 92)
    vs_top(f, t)
    k = pop(t, 0.5)
    big(f, "3.1배", 960, 170, col=BLUE, o=k, anchor="mt") if False else None
    G.blit(f, T("3.1배", 170, BLUE, "Black", stroke=8, stroke_fill=(0, 0, 0)), (W * 0.27, 960), k, "mt")
    G.blit(f, T("8.3배", 170, CORAL, "Black", stroke=8, stroke_fill=(0, 0, 0)), (W * 0.73, 960), k, "mt")
    pill(f, "왜 직장인이 더 남길까?", 1200, t, 0.9, bg=GOLD, size=58)


def b2(f, t, sc):
    bgp(f, "seoul_subway", t, 0.6)
    big(f, "직장인은", 300, 120)
    big(f, "회사가\n절반을 내 준다", 480, 150, hl="절반", o=pop(t, 0.15))


def b3(f, t, sc):
    bgp(f, "seoul_night_still", t, 0.6)
    person(f, "kimjanghoon_cut", 1000, W * 0.5, t, 0.0)
    big(f, "연예인 · 프리랜서는", 230, 96)
    big(f, "혼자 다 낸다", 380, 150, col=RED, o=pop(t, 0.2))


def b4(f, t, sc):
    bgp(f, "worker_stressed", t, 0.62, (0.5, 0.3))
    big(f, "평범한 직장인 · 30년", 240, 88)
    big(f, "내 돈 3,234만", 520, 110, o=pop(t, 0.1))
    big(f, "↓", 680, 100, col=GOLD, o=pop(t, 0.3))
    big(f, "연금 2.68억", 800, 150, col=GREEN, o=pop(t, 0.45))
    big(f, "8.3배", 1030, 180, col=CORAL, o=pop(t, 0.8))


def b5(f, t, sc):
    bgp(f, "seoul_night_still", t, 0.65)
    big(f, "소득 2배 프리랜서 · 30년", 240, 84)
    big(f, "내 돈 1.29억", 520, 110, o=pop(t, 0.1))
    big(f, "↓", 680, 100, col=GOLD, o=pop(t, 0.3))
    big(f, "연금 4.02억", 800, 150, col=GREEN, o=pop(t, 0.45))
    big(f, "3.1배", 1030, 180, col=BLUE, o=pop(t, 0.8))
    G.blit(f, T("가정 계산 · 실제 연예인 개인의 금액 아님", 32, (190, 196, 214), "SemiBold"), (W / 2, 1290), 1, "mt")


def b6(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 30, 255)))
    big(f, "국민연금은 원래", 480, 100)
    big(f, "소득이 적을수록\n더 후하게", 660, 150, hl="더 후하게", hlc=GREEN, o=pop(t, 0.2))


def b7(f, t, sc):
    bgp(f, "noryangjin_cross", t, 0.6)
    vs_top(f, t)
    big(f, "낸 돈 대비 승자", 1000, 96)
    big(f, "평범한 직장인", 1140, 150, col=CORAL, o=pop(t, 0.3))


S2 = [
    {"draw": b1, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "accent_low", 0.6), (0.5, "pop", 0.5), (0.95, "accent", 0.5)],
     "narr": ["국민연금, 낸 돈 대비 연예인은 3배, 평범한 직장인은 8배? 왜 그럴까요?"]},
    {"draw": b2, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.15, "pop", 0.5)],
     "narr": ["직장인은 보험료 절반을 회사가 내 줘요."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "accent_low", 0.5)],
     "narr": ["연예인이나 프리랜서는, 혼자 다 내고요."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.45, "mx:2841", 0.6), (0.8, "accent", 0.5)],
     "narr": ["평범한 직장인은 내 돈 3천2백만 원으로, 연금 2억 6천8백만 원. 8.3배예요."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.45, "mx:1999", 0.6), (0.8, "accent_low", 0.5)],
     "narr": ["소득이 두 배인 프리랜서는, 1억 3천만 원 내고 4억 원. 금액은 크지만 3.1배죠."]},
    {"draw": b6, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "reveal", 0.5)],
     "narr": ["국민연금은 원래, 소득이 적은 사람에게 더 후하게 계산하거든요."]},
    {"draw": b7, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "sparkle", 0.5)],
     "narr": ["낸 돈 대비로는, 평범한 직장인이 이기는 구조예요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["여러분의 연금은 얼마일까요? 좋아요 누르고, 친구한테도 물어보세요."]},
]


# ── 쇼츠 3: 노후 소득 피라미드 ─────────────────────────────────
LAYERS = [("1층 국민연금", "103만", (150, 160, 190)), ("2층 퇴직연금", "+77만", BLUE), ("3층 연금저축", "+46만", GREEN)]


def c1(f, t, sc):
    bgp(f, "pensioner_bench", t, 0.6)
    big(f, "국민연금 한 달", 200, 96)
    k = pop(t, 0.05, 0.3)
    v = 103 + (226 - 103) * min(1, max(0, (t - 0.3) / 0.9))
    big(f, "103만", 420, 150, col=(220, 224, 236), o=k)
    big(f, "↓", 590, 100, col=GOLD, o=k)
    big(f, f"{v:.0f}만 원", 700, 240, col=GREEN, o=k)
    pill(f, "평범한 월급으로 만드는 법", 1050, t, 0.8, bg=GOLD, size=58)


def c2(f, t, sc):
    bgp(f, "worker_stressed", t, 0.62, (0.5, 0.3))
    big(f, "혼자 사는 노후 적정 생활비", 240, 80)
    big(f, "198만 원", 400, 170, o=pop(t, 0.1))
    big(f, "모자라는 돈", 760, 100, o=pop(t, 0.5))
    big(f, "95만 원", 900, 200, col=RED, o=pop(t, 0.7))


def c3(f, t, sc):
    bgp(f, "pensioner_bench", t, 0.7)
    big(f, "한국 노인 10명 중", 420, 100)
    big(f, "4명이\n가난하다", 590, 190, col=RED, o=pop(t, 0.2))
    G.blit(f, T("OECD 한눈에 보는 연금 2025 · 소득 빈곤율 39.7%", 34, (190, 196, 214), "SemiBold"), (W / 2, 1090), 1, "mt")


def pyr(step):
    def d(f, t, sc):
        f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 30, 255)))
        big(f, "노후 소득 피라미드", 200, 100, hl="피라미드")
        t0s = [(-9, -9, 0.1)[k] if False else (0.1 if k == step else -9) for k in range(3)]
        t0s = [(-9 if k < step else (0.1 if k == step else 99)) for k in range(3)]
        pyramid(f, t, LAYERS, t0s=t0s, ghost=(step == 2))
        y = 1500
        if step == 2:
            big(f, "합계 월 226만 원", y, 110, col=GOLD, o=pop(t, 1.2))
    return d


def c7(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 30, 255)))
    big(f, "2층 + 3층, 언제 시작했나", 230, 80)
    for i, (lab, v, txt) in enumerate([("30년", 123, "월 123만"), ("20년", 78, "월 78만"), ("10년", 31, "월 31만")]):
        k = pop(t, 0.15 + i * 0.3, 0.45)
        x = 220 + i * 320
        hh = int(700 * v / 123 * k)
        col = GREEN if i == 0 else (RED if i == 2 else (200, 206, 220))
        ImageDraw.Draw(f).rounded_rectangle((x - 110, 1250 - hh, x + 110, 1250), 18, fill=col + (255,))
        G.blit(f, T(txt, 52, col, "Black", stroke=5, stroke_fill=(0, 0, 0)), (x, 1230 - hh), k, "mb")
        G.blit(f, T(lab, 56, CREAM, "Black"), (x, 1280), k, "mt")
    big(f, "시작은 오늘", 1420, 120, col=GOLD, o=pop(t, 1.3))


S3 = [
    {"draw": c1, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.05, "mx:2003", 0.7), (1.2, "accent", 0.5)],
     "narr": ["국민연금 103만 원을, 226만 원으로 만드는 방법. 평범한 월급으로도 돼요."]},
    {"draw": c2, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.7, "mx:2182", 0.7)],
     "narr": ["혼자 사는 노후에 필요한 돈은 한 달 198만 원. 95만 원이 모자라요."]},
    {"draw": c3, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "mx:2782", 0.6)],
     "narr": ["그래서 우리나라 노인 열 명 중 네 명이 가난해요."]},
    {"draw": pyr(0), "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "drum", 0.6)],
     "narr": ["1층은 국민연금, 한 달 103만 원."]},
    {"draw": pyr(1), "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "drum", 0.6)],
     "narr": ["2층은 퇴직연금. 30년 동안 지수에 굴렸다면 77만 원이 더 생겨요."]},
    {"draw": pyr(2), "nohead": True, "flash": True, "min": 3.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.1, "drum", 0.6), (1.2, "mx:2841", 0.7)],
     "narr": ["3층은 연금저축. 월급의 5%만 지수 펀드로 쌓아도 46만 원. 합치면 226만 원이에요."]},
    {"draw": c7, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.75, "accent_low", 0.6), (1.3, "sparkle", 0.5)],
     "narr": ["다만 10년 늦게 시작하면 한 달 31만 원. 시작은 오늘이에요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["여러분은 지금 몇 층까지 쌓았나요? 좋아요 누르고, 친구한테도 물어보세요."]},
]

HEAD = {"kicker": "주식 악어새", "title": "국민연금", "highlight": ""}
SETS = {1: (S1, [(0, "tense"), (5, "hope")]), 2: (S2, [(0, "tense"), (5, "hope")]), 3: (S3, [(0, "dark"), (3, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, cues = SETS[n]
    K.run(sc, HEAD, OUT / f"s{n}", say=dict(SAY), argv=[a for a in sys.argv[2:]], bgm_cues=cues)
