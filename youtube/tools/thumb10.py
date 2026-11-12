"""썸네일 10종 패턴 (2026-11-12 사용자 지정: '월간 아웃라이어' 썸네일 패턴 10가지의 '구조'만 차용, 그림 · 문구는 우리 것)

  python tools/thumb10.py episodes/ep013_battery_lev     → out/<ep>/thumbs10/P01~P10.png + 한 장 비교표

패턴 (구조)
  P01 상식과 반대되는 질문      윗줄 상식 · 아랫줄 뒤집는 결과
  P02 숫자 목록 + 인물          숫자를 가장 크게, 인물(사진 누끼)이 표정 · 시선 담당
  P03 화살표로 보여주는 변화    [전] → [후] 크게, 설명은 작게
  P04 사람 말투 그대로 따옴표   위 작은 따옴표(실제 발언) · 아래 큰 결과
  P05 해본 사람 + 결과 감추기   '~했더니… 결과는?' (실험 · 시뮬레이션)
  P06 몰락 · 경고 + 빨간 결론   '한때 ○○ → 지금 □□' + 경고 스티커, 결론만 빨강
  P07 전문가의 한마디           작은 직함 라벨 + 꾸밈없는 말투 (실제 발언만)
  P08 로고 · 아이콘 대결        A vs B 아이콘 + 비교 기준 한 줄 (승부는 숨김)
  P09 시청자 속마음 먼저        시청자가 속으로 할 말(의심 · 반발)을 말풍선처럼
  P10 실물로 화면 꽉 채우기     실물 사진이 주제를 말하고, 작은 라벨 + 짧은 두 줄
에피소드 yaml의 thumbs10: [{p: P01, ...}] 로 문구를 정한다.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402
from engine import draw as G  # noqa: E402

W, H = TH.W, TH.H
YEL, RED, WHITE, BLACK = (255, 214, 40), (255, 60, 60), (255, 255, 255), (0, 0, 0)
MINT = (90, 230, 170)


def txt(text, size, color=WHITE, hl="", hl_color=YEL, stroke=None, maxw=1760):
    return TH.fit(text, size, maxw, color=color, hl=hl, hl_color=hl_color)


def bottom_two(f, top, bottom, top_size=96, bot_size=150, top_col=WHITE, bot_col=YEL, hl="", y_bottom=None, x=None):
    """아래쪽 두 줄 (작은 윗줄 + 큰 아랫줄) — 왼쪽 정렬"""
    b = txt(bottom, bot_size, bot_col, hl=hl)
    t = txt(top, top_size, top_col)
    yb = (y_bottom or H - 60) - b.height
    xx = x if x is not None else 70
    TH.shadowed(f, t, (xx, yb - t.height + 6))
    TH.shadowed(f, b, (xx, yb))


def shade_bottom(f, strength=230, start=0.35):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    y0 = int(H * start)
    for y in range(y0, H, 4):
        d.rectangle((0, y, W, y + 4), fill=(0, 0, 0, int(strength * ((y - y0) / (H - y0)) ** 1.3)))
    f.alpha_composite(g)


def bg(name, focus=(0.5, 0.5), dark=0.3, gray=0.2):
    return TH.photo_fill(name, W, H, focus, dark, 0, gray).copy()


def cutout(name, h):
    p = TH.ROOT / "assets" / "people" / f"{name}.png"
    im = Image.open(p).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def stamp(text, size=64, bgc=RED, fg=WHITE, rot=-6):
    p = G.pill(text, "Black", size, fg, bgc, pad=(30, 12), radius=14)
    return p.rotate(rot, expand=True, resample=Image.BICUBIC)


# ── 패턴별 ───────────────────────────────────────────────────────
def p01(sp):
    f = bg(sp.get("photo", "ev_snow"), dark=0.35, gray=0.4)
    shade_bottom(f)
    bottom_two(f, sp["top"], sp["bottom"], 100, 158, hl=sp.get("hl", ""))
    if sp.get("sticker"):
        TH.shadowed(f, stamp(sp["sticker"], 70), (W - 80, 70), "rt")
    return f


def p02(sp):
    f = bg(sp.get("photo", "bess_site"), dark=0.55, gray=0.3)
    fig = cutout(sp.get("figure", "thinker_cut"), 760)
    f.alpha_composite(TH.rim(fig, (255, 200, 80), 30), (W - fig.width - 10 - 60, H - fig.height - 60))
    f.alpha_composite(fig, (W - fig.width - 10, H - fig.height + 30))
    t = txt(sp["top"], 92, WHITE, maxw=1150)
    TH.shadowed(f, t, (70, 120))
    n = TH.T(sp["num"], 380, YEL)
    TH.shadowed(f, n, (60, 220))
    u = txt(sp["unit"], 150, WHITE, maxw=700)
    TH.shadowed(f, u, (80 + n.width, 220 + n.height - u.height - 40))
    return f


def p03(sp):
    f = bg(sp.get("photo", "ev_snow"), dark=0.6, gray=0.5)
    a = TH.T(sp["before"], 190, WHITE)
    b = TH.T(sp["after"], 220, RED)
    arr = TH.big_arrow(300, 210, YEL)
    total = a.width + 40 + arr.width + 40 + b.width
    sc = min(1.0, 1780 / total)
    if sc < 1:
        a = a.resize((int(a.width * sc), int(a.height * sc)), Image.LANCZOS)
        b = b.resize((int(b.width * sc), int(b.height * sc)), Image.LANCZOS)
        arr = arr.resize((int(arr.width * sc), int(arr.height * sc)), Image.LANCZOS)
    x = (W - (a.width + 40 + arr.width + 40 + b.width)) // 2
    y = 330
    TH.shadowed(f, a, (x, y))
    TH.shadowed(f, arr, (x + a.width + 40, y + a.height // 2 - arr.height // 2))
    TH.shadowed(f, b, (x + a.width + 80 + arr.width, y + a.height - b.height))
    s = txt(sp["sub"], 96, YEL)
    TH.shadowed(f, s, (W / 2, H - 90), "mb")
    if sp.get("label"):
        TH.shadowed(f, TH.tag(sp["label"], size=54), (80, 80))
    return f


def p04(sp):
    f = bg(sp.get("photo", "musk"), sp.get("focus", (0.6, 0.3)), dark=0.25, gray=0.15)
    shade_bottom(f, 240, 0.3)
    q = txt(f"“{sp['quote']}”", 70, MINT, maxw=1300)
    TH.shadowed(f, q, (W - 70, 70), "rt")
    if sp.get("who"):
        TH.shadowed(f, TH.tag(sp["who"], size=44), (W - 70, 90 + q.height), "rt")
    bottom_two(f, sp["top"], sp["bottom"], 96, 150, hl=sp.get("hl", ""))
    return f


def p05(sp):
    f = bg(sp.get("photo", "ev_snow"), dark=0.45, gray=0.3)
    shade_bottom(f, 220, 0.25)
    t = txt(sp["line1"], 84, WHITE)
    m = txt(sp["line2"], 150, WHITE)
    r = txt(sp["line3"], 190, YEL)
    y = H - 60 - r.height
    TH.shadowed(f, r, (70, y))
    TH.shadowed(f, m, (70, y - m.height + 10))
    TH.shadowed(f, t, (70, y - m.height - t.height + 20))
    if sp.get("sticker"):
        TH.shadowed(f, stamp(sp["sticker"], 64, YEL, BLACK, 5), (W - 80, 80), "rt")
    return f


def p06(sp):
    f = bg(sp.get("photo", "krx_building"), dark=0.4, gray=0.3)
    red = Image.new("RGBA", (W, H), (120, 0, 0, 70))
    f.alpha_composite(red)
    shade_bottom(f, 235, 0.3)
    bottom_two(f, sp["top"], sp["bottom"], 104, 160, top_col=WHITE, bot_col=RED)
    TH.shadowed(f, stamp(sp.get("sticker", "경고!"), 92, RED, WHITE, -8), (W - 90, 80), "rt")
    return f


def p07(sp):
    f = bg(sp.get("photo", "bess_site"), dark=0.4, gray=0.25)
    shade_bottom(f, 235, 0.3)
    lab = G.pill(sp["label"], "Black", 52, BLACK, WHITE, pad=(24, 10), radius=10)
    TH.shadowed(f, lab, (70, 70))
    bottom_two(f, sp["top"], sp["bottom"], 104, 150, hl=sp.get("hl", ""))
    return f


def icon_card(kind, s=330, col=(40, 44, 60)):
    k = 3
    im = Image.new("RGBA", (s * k, s * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s * k - 1, s * k - 1), 60 * k, fill=col + (255,))
    u = s * k
    if kind == "car":   # 전기차: 차 + 번개
        d.rounded_rectangle((u * .15, u * .45, u * .85, u * .68), 30 * k, fill=(240, 240, 245, 255))
        d.polygon([(u * .28, u * .45), (u * .38, u * .3), (u * .64, u * .3), (u * .74, u * .45)], fill=(240, 240, 245, 255))
        for cx in (.3, .7):
            d.ellipse((u * (cx - .08), u * .62, u * (cx + .08), u * .78), fill=(20, 20, 26, 255))
        d.polygon([(u * .52, u * .12), (u * .42, u * .3), (u * .5, u * .3), (u * .45, u * .44), (u * .6, u * .24), (u * .52, u * .24)], fill=YEL + (255,))
    else:               # AI 데이터센터: 서버 랙 + 'AI'
        for i in range(3):
            y0 = u * (.22 + i * .2)
            d.rounded_rectangle((u * .22, y0, u * .78, y0 + u * .15), 12 * k, fill=(240, 240, 245, 255))
            for j in range(4):
                d.ellipse((u * (.28 + j * .06), y0 + u * .055, u * (.31 + j * .06), y0 + u * .085), fill=MINT + (255,))
    im = im.resize((s, s), Image.LANCZOS)
    if kind != "car":
        G.blit(im, TH.T("AI", 90, YEL), (s * 0.72, s * 0.82), 1, "mm")
    return im


def p08(sp):
    f = TH.bg_split(left=(30, 60, 120), right=(30, 110, 80))
    a, b = icon_card(sp.get("a", "car")), icon_card(sp.get("b", "ai"))
    TH.shadowed(f, a, (W / 2 - 230, 290), "mm")
    TH.shadowed(f, b, (W / 2 + 230, 290), "mm")
    TH.shadowed(f, TH.T("VS", 130, YEL), (W / 2, 290), "mm")
    bottom_two(f, sp["top"], sp["bottom"], 96, 150, x=None)
    return f


def p09(sp):
    f = bg(sp.get("photo", "ev_snow"), dark=0.45, gray=0.5)
    shade_bottom(f, 230, 0.25)
    bub = TH.T(sp["bubble"], 76, BLACK, stroke=0)  # 말풍선 글씨는 테두리 없이 (검은 테두리면 뭉개짐)
    pad = 34
    card = Image.new("RGBA", (bub.width + pad * 2, bub.height + pad * 2 + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width - 1, card.height - 41), 40, fill=(255, 255, 255, 250))
    d.polygon([(70, card.height - 42), (130, card.height - 42), (60, card.height - 2)], fill=(255, 255, 255, 250))
    card.alpha_composite(bub, (pad, pad))
    TH.shadowed(f, card, (W - 90, 80), "rt")
    bottom_two(f, sp["top"], sp["bottom"], 96, 168, hl=sp.get("hl", ""))
    return f


def p10(sp):
    f = bg(sp.get("photo", "bess_site"), sp.get("focus", (0.5, 0.5)), dark=0.15, gray=0.05)
    shade_bottom(f, 230, 0.45)
    lab = txt(sp["label"], 58, WHITE)
    b = txt(sp["bottom"], 150, YEL, hl=sp.get("hl", ""))
    t = txt(sp["top"], 100, WHITE)
    yb = H - 60 - b.height
    TH.shadowed(f, b, (70, yb))
    TH.shadowed(f, t, (70, yb - t.height + 6))
    TH.shadowed(f, lab, (70, yb - t.height - lab.height + 6))
    return f


P = {"P01": p01, "P02": p02, "P03": p03, "P04": p04, "P05": p05, "P06": p06, "P07": p07, "P08": p08, "P09": p09, "P10": p10}


def main(ep_dir):
    import render as R
    ep_dir = Path(ep_dir).resolve()
    ep, _ = R.load(ep_dir)
    od = TH.ROOT / "out" / ep_dir.name / "thumbs10"
    od.mkdir(parents=True, exist_ok=True)
    outs = []
    for sp in ep["thumbs10"]:
        f = TH.finish(P[sp["p"]](sp), frame=False)
        path = od / f"{sp['p']}.png"
        f.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path)
        outs.append((sp["p"], path))
        print("썸네일 →", path)
    # 비교표 (2열 × 5행, 휴대폰 크기 확인용)
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * 2 + 30, (th + 50) * 5 + 10), (16, 16, 20))
    for i, (p, path) in enumerate(outs):
        x, y = 10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 50)
        sheet.paste(Image.open(path).resize((tw, th)), (x, y))
        G.blit(sheet := sheet.convert("RGBA"), TH.T(p, 30, (180, 255, 60), stroke=0), (x, y + th + 6))
        sheet = sheet.convert("RGB")
    sheet.save(od / "비교표.jpg", quality=90)
    print("비교표 →", od / "비교표.jpg")


if __name__ == "__main__":
    main(sys.argv[1])
