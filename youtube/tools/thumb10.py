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


def bottom_two(f, top, bottom, top_size=150, bot_size=230, top_col=WHITE, bot_col=YEL, hl="", y_bottom=None, x=None):
    """가운데 아래 두 줄 (2026-11-12: 가운데 정렬 · 글자 크게 — 작은 줄 150, 큰 줄 230 기준, 화면 폭에 맞춰 자동 축소)"""
    b = txt(bottom, bot_size, bot_col, hl=hl, maxw=1820)
    t = txt(top, top_size, top_col, maxw=1820)
    yb = (y_bottom or H - 50) - b.height
    if x is None:
        TH.shadowed(f, t, (W / 2, yb - t.height + 14), "mt")
        TH.shadowed(f, b, (W / 2, yb), "mt")
    else:
        TH.shadowed(f, t, (x, yb - t.height + 14))
        TH.shadowed(f, b, (x, yb))


def shade_bottom(f, strength=230, start=0.35):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    y0 = int(H * start)
    for y in range(y0, H, 4):
        d.rectangle((0, y, W, y + 4), fill=(0, 0, 0, int(strength * ((y - y0) / (H - y0)) ** 1.3)))
    f.alpha_composite(g)


def bg(name, focus=(0.5, 0.5), dark=0.3, gray=0.2, theme="red", chart=None):
    """매콤한 배경 (2026-11-12): 사진 대비 · 채도 올림 + 테마색 그라데이션 + 가운데 빛 + 강한 비네트 + (선택) 빛나는 폭락 차트"""
    from PIL import ImageEnhance
    im = TH.photo_fill(name, W, H, focus, max(0.0, dark - 0.15), 0, 0.0).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.35)
    im = ImageEnhance.Color(im).enhance(1.35)
    f = im.convert("RGBA")
    c1 = {"red": (190, 20, 20), "gold": (230, 150, 20), "blue": (20, 70, 200), "green": (20, 150, 90)}[theme]
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(0, H, 6):  # 위는 테마색, 아래는 검정으로
        k = y / H
        d.rectangle((0, y, W, y + 6), fill=c1 + (int(80 * (1 - k)),))
    f.alpha_composite(g)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W * 0.2, -H * 0.2, W * 0.8, H * 0.6), fill=(255, 230, 180, 50))
    f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    if chart:
        ch = TH.chart_line(chart["series"], chart.get("start"), chart.get("end"), tuple(chart.get("color", (255, 50, 50))), 1700, 620)
        ch = ch.resize((W, int(ch.height * W / ch.width)), Image.LANCZOS)
        a = ch.getchannel("A").point(lambda v: int(v * chart.get("alpha", 0.75)))
        ch.putalpha(a)
        f.alpha_composite(ch, (0, chart.get("y", 40)))
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v)
    for i in range(30):
        vd.rectangle((i * 14, i * 9, W - i * 14, H - i * 9), outline=(0, 0, 0, int(200 * (1 - i / 30) ** 2)), width=16)
    f.alpha_composite(v.filter(ImageFilter.GaussianBlur(30)))
    return f


def cutout(name, h):
    p = TH.ROOT / "assets" / "people" / f"{name}.png"
    im = Image.open(p).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def stamp(text, size=64, bgc=RED, fg=WHITE, rot=-6):
    p = G.pill(text, "Black", size, fg, bgc, pad=(30, 12), radius=14)
    return p.rotate(rot, expand=True, resample=Image.BICUBIC)


# ── 패턴별 (2026-11-12 v2: 가운데 정렬 · 큰 글씨 · 매콤한 배경) ─────────────────
def B(sp, name, focus=(0.5, 0.5), dark=0.3, theme="red"):
    f = bg(sp.get("photo", name), tuple(sp.get("focus", focus)), sp.get("dark", dark), 0.0, sp.get("theme", theme), sp.get("chart"))
    if sp.get("person"):
        add_person(f, sp["person"])
    return f


def add_person(f, pp):
    """인물 누끼(assets/people/<file>.png)를 한쪽에 크게 세움 — 글자는 그 위에 얹히되 얼굴은 비켜 가게 (2026-11-12)"""
    fig = cutout(pp["file"], pp.get("h", 1000))
    x = pp.get("x", W - fig.width - 20) if pp.get("side", "right") == "right" else pp.get("x", 20)
    y = H - fig.height + pp.get("dy", 120)
    f.alpha_composite(TH.rim(fig, tuple(pp.get("rim", (255, 214, 40))), 26), (int(x - 78 - fig.width * 0.02), int(y - 78 - fig.height * 0.02)))
    f.alpha_composite(fig, (x, y))


def p01(sp):
    f = B(sp, "tesla_chargers")
    shade_bottom(f, 240, 0.3)
    bottom_two(f, sp["top"], sp["bottom"], hl=sp.get("hl", ""))
    if sp.get("sticker"):
        TH.shadowed(f, stamp(sp["sticker"], 96), (W - 70, 60), "rt")
    return f


def p02(sp):
    f = B(sp, "bess_site", dark=0.45, theme="gold")
    fig = cutout(sp.get("figure", "thinker_cut"), 900)
    f.alpha_composite(TH.rim(fig, (255, 200, 80), 34), (W - fig.width + 30 - 70, H - fig.height + 60 - 70))
    f.alpha_composite(fig, (W - fig.width + 30, H - fig.height + 60))
    shade_bottom(f, 200, 0.5)
    t = txt(sp["top"], 150, WHITE, maxw=1400)
    TH.shadowed(f, t, (80, 50))   # 읽는 순서: 위 문장 → 큰 숫자
    u = txt(sp["unit"], 230, WHITE, maxw=900)
    ns = 600
    n = TH.T(sp["num"], ns, YEL)
    while n.width + u.width + 60 > W - 60 and ns > 300:   # 숫자 + 단위가 화면 안에 들어오게
        ns -= 30
        n = TH.T(sp["num"], ns, YEL)
    TH.shadowed(f, n, (90, 60 + t.height - 40))
    TH.shadowed(f, u, (120 + n.width, 60 + t.height - 40 + n.height - u.height - 100))
    return f


def p03(sp):
    f = B(sp, "tesla_chargers", dark=0.45)
    a = TH.T(sp["before"], 260, WHITE)
    b = TH.T(sp["after"], 300, RED)
    arr = TH.big_arrow(330, 240, YEL)
    total = a.width + 30 + arr.width + 30 + b.width
    sc = min(1.0, 1820 / total)
    if sc < 1:
        a, b, arr = (im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS) for im in (a, b, arr))
    x = (W - (a.width + 30 + arr.width + 30 + b.width)) // 2
    y = 250
    TH.shadowed(f, a, (x, y + b.height - a.height))
    TH.shadowed(f, arr, (x + a.width + 30, y + b.height // 2 - arr.height // 2))
    TH.shadowed(f, b, (x + a.width + 60 + arr.width, y))
    shade_bottom(f, 220, 0.6)
    s_ = txt(sp["sub"], 150, YEL, maxw=1820)
    TH.shadowed(f, s_, (W / 2, H - 50), "mb")
    if sp.get("label"):
        TH.shadowed(f, TH.tag(sp["label"], size=70), (W / 2, 70), "mt")
    return f


def p04(sp):
    f = B(sp, "musk", (0.62, 0.25), dark=0.15)
    shade_bottom(f, 245, 0.35)
    if sp.get("quote_w"):  # 인물이 옆에 있으면 따옴표는 반대쪽에 (얼굴 가리지 않게)
        q = txt(f"\u201c{sp['quote']}\u201d", sp.get("quote_size", 120), MINT, maxw=sp["quote_w"])
        TH.shadowed(f, q, (60, 50), "lt")
    else:
        q = txt(f"\u201c{sp['quote']}\u201d", 110, MINT, maxw=1820)
        TH.shadowed(f, q, (W / 2, 50), "mt")
    if sp.get("who"):
        TH.shadowed(f, TH.tag(sp["who"], size=56), (W / 2, 70 + q.height), "mt")
    bottom_two(f, sp["top"], sp["bottom"], hl=sp.get("hl", ""))
    return f


def p05(sp):
    f = B(sp, "ev_snow", dark=0.35)
    shade_bottom(f, 230, 0.2)
    r = txt(sp["line3"], 280, YEL, maxw=1820)
    m = txt(sp["line2"], 190, WHITE, maxw=1820)
    t = txt(sp["line1"], 130, WHITE, maxw=1820)
    y = H - 40 - r.height
    TH.shadowed(f, r, (W / 2, y), "mt")
    TH.shadowed(f, m, (W / 2, y - m.height + 20), "mt")
    TH.shadowed(f, t, (W / 2, y - m.height - t.height + 34), "mt")
    if sp.get("sticker"):
        TH.shadowed(f, stamp(sp["sticker"], 80, YEL, BLACK, 5), (W - 70, 60), "rt")
    return f


def p06(sp):
    f = B(sp, "krx_building", dark=0.35)
    f.alpha_composite(Image.new("RGBA", (W, H), (140, 0, 0, 80)))
    shade_bottom(f, 240, 0.3)
    bottom_two(f, sp["top"], sp["bottom"], top_col=WHITE, bot_col=RED)
    TH.shadowed(f, stamp(sp.get("sticker", "경고!"), 130, RED, WHITE, -8), (W - 80, 60), "rt")
    return f


def p07(sp):
    f = B(sp, "server_rack", dark=0.3, theme="blue")
    shade_bottom(f, 240, 0.3)
    lab = G.pill(sp["label"], "Black", 70, BLACK, WHITE, pad=(30, 12), radius=12)
    TH.shadowed(f, lab, (W / 2, 70), "mt")
    bottom_two(f, sp["top"], sp["bottom"], hl=sp.get("hl", ""))
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
    """두 사진을 반씩 + 가운데 VS (사진이 없으면 아이콘)"""
    f = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    left = bg(sp.get("left", "tesla_chargers"), (0.5, 0.5), 0.3, 0.0, "blue").crop((W // 4, 0, W // 4 + W // 2, H))
    right = bg(sp.get("right", "server_rack"), (0.5, 0.5), 0.3, 0.0, "green").crop((W // 4, 0, W // 4 + W // 2, H))
    f.alpha_composite(left, (0, 0))
    f.alpha_composite(right, (W // 2, 0))
    for pp in sp.get("persons", []):
        add_person(f, pp)
    ImageDraw.Draw(f).polygon([(W / 2 - 20, 0), (W / 2 + 40, 0), (W / 2 + 20, H), (W / 2 - 40, H)], fill=(255, 214, 40, 255))
    TH.shadowed(f, TH.T("VS", 220, YEL), (W / 2, 330), "mm")
    shade_bottom(f, 240, 0.35)
    bottom_two(f, sp["top"], sp["bottom"])
    return f


def p09(sp):
    f = B(sp, "ev_snow", dark=0.35, theme="blue")
    shade_bottom(f, 235, 0.25)
    bub = TH.T(sp["bubble"], 110, BLACK, stroke=0)
    pad = 40
    card = Image.new("RGBA", (bub.width + pad * 2, bub.height + pad * 2 + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width - 1, card.height - 51), 50, fill=(255, 255, 255, 250))
    d.polygon([(card.width // 2 - 40, card.height - 52), (card.width // 2 + 40, card.height - 52), (card.width // 2, card.height - 2)], fill=(255, 255, 255, 250))
    card.alpha_composite(bub, (pad, pad))
    TH.shadowed(f, card, (W / 2, 50), "mt")
    bottom_two(f, sp["top"], sp["bottom"], hl=sp.get("hl", ""))
    return f


def p10(sp):
    f = B(sp, "bess_site", dark=0.1, theme="gold")
    shade_bottom(f, 235, 0.4)
    lab = txt(sp["label"], 90, WHITE, maxw=1820)
    TH.shadowed(f, lab, (W / 2, 60), "mt")
    bottom_two(f, sp["top"], sp["bottom"], hl=sp.get("hl", ""))
    return f


P = {"P01": p01, "P02": p02, "P03": p03, "P04": p04, "P05": p05, "P06": p06, "P07": p07, "P08": p08, "P09": p09, "P10": p10}




# ══ v3 (2026-11-12): 패턴마다 화면 구조 · 밝기 · 글자 배치를 다르게 (THUMB_PATTERNS.md) ══════════
def bright(name, focus=(0.5, 0.5), dark=0.0, gray=0.0, blur=0, sat=1.3, contrast=1.2):
    """밝은 실사 배경 (아웃라이어 썸네일처럼 사진을 누르지 않음)"""
    from PIL import ImageEnhance
    im = TH.photo_fill(name, W, H, focus, dark, blur, gray).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(sat)
    f = im.convert("RGBA")
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v)
    for i in range(16):
        vd.rectangle((i * 12, i * 8, W - i * 12, H - i * 8), outline=(0, 0, 0, int(120 * (1 - i / 16) ** 2)), width=14)
    f.alpha_composite(v.filter(ImageFilter.GaussianBlur(24)))
    return f


def band(f, y0, alpha=200, color=(0, 0, 0), fade=120):
    """y0 아래 띠 (위쪽은 부드럽게)"""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(max(0, y0 - fade), H, 3):
        a = alpha if y >= y0 else int(alpha * (y - (y0 - fade)) / fade)
        d.rectangle((0, y, W, y + 3), fill=color + (a,))
    f.alpha_composite(g)


def left_two(f, top, bottom, top_size=140, bot_size=210, top_col=WHITE, bot_col=YEL, x=70, y_bottom=None, hl="", hl_color=RED):
    b = txt(bottom, bot_size, bot_col, hl=hl, hl_color=hl_color, maxw=W - 2 * x)
    t = txt(top, top_size, top_col, maxw=W - 2 * x)
    yb = (y_bottom or H - 40) - b.height
    TH.shadowed(f, t, (x, yb - t.height + 12))
    TH.shadowed(f, b, (x, yb))
    return yb - t.height


def person_at(f, name, h, x, y_bottom=None, rim=(255, 214, 40)):
    fig = cutout(name, h)
    y = (y_bottom or H + 40) - fig.height
    f.alpha_composite(TH.rim(fig, rim, 26), (int(x - 78 - fig.width * 0.02), int(y - 78 - fig.height * 0.02)))
    f.alpha_composite(fig, (int(x), int(y)))
    return fig


def pyramid_icon(w=760, h=620, labels=("1층", "2층", "3층"), cols=((120, 132, 160), (74, 144, 255), (90, 220, 170))):
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(labels)
    gap = 14 * k
    lh = (h * k - gap * (n - 1) - 120 * k) / n
    for i in range(n):
        yb = h * k - i * (lh + gap)
        yt = yb - lh
        wb_ = w * k * (1 - i * 0.26)
        wt_ = w * k * (1 - (i + 1) * 0.26) + 40 * k
        cx = w * k / 2
        d.polygon([(cx - wb_ / 2, yb), (cx + wb_ / 2, yb), (cx + wt_ / 2, yt), (cx - wt_ / 2, yt)], fill=cols[i] + (255,))
        d.text((cx, (yb + yt) / 2), labels[i], fill=(14, 16, 24) if i == n - 1 else WHITE, anchor="mm", font=TH.S.font("Black", int(lh * 0.42)))
    yt = h * k - n * (lh + gap) + gap
    cx = w * k / 2
    top_w = w * k * (1 - n * 0.26) + 40 * k
    for j in range(0, 24, 2):  # 꼭대기 점선
        for (xa, ya), (xb, yb2) in (((cx - top_w / 2, yt), (cx, yt - 110 * k)), ((cx, yt - 110 * k), (cx + top_w / 2, yt))):
            d.line([(xa + (xb - xa) * j / 24, ya + (yb2 - ya) * j / 24), (xa + (xb - xa) * (j + 1) / 24, ya + (yb2 - ya) * (j + 1) / 24)], fill=(240, 240, 248, 200), width=5 * k)
    return im.resize((w, h), Image.LANCZOS)


def v3_p01(sp):
    """상식과 반대: 밝은 실사 + 아래 검은 띠 위 왼쪽 두 줄(상식 흰 · 뒤집기 노랑) + 결과 단어 스티커"""
    f = bright(sp.get("photo", "seoul_subway"), tuple(sp.get("focus", (0.5, 0.5))))
    band(f, int(H * 0.55), 215)
    left_two(f, sp["top"], sp["bottom"], hl=sp.get("hl", ""))
    if sp.get("sticker"):
        TH.shadowed(f, stamp(sp["sticker"], 110, YEL, BLACK, -7), (60, 50))
    return f


def v3_p02(sp):
    """숫자 목록: 담백한 수식어(작게 위) + 화면에서 가장 큰 숫자 + 오른쪽 도식(피라미드) 또는 누끼"""
    f = bg(sp.get("photo", "bess_site"), tuple(sp.get("focus", (0.5, 0.5))), 0.75, 0.0, sp.get("theme", "blue"))
    x = 70
    t = txt(sp["top"], 120, WHITE, maxw=1050)
    TH.shadowed(f, t, (x, 60))
    n = TH.T(sp["num"], sp.get("num_size", 640), YEL)
    ny = 60 + t.height - 70
    TH.shadowed(f, n, (x - 10, ny))
    u = txt(sp["unit"], 300, WHITE, maxw=700)
    TH.shadowed(f, u, (x + n.width + 10, ny + n.height * 0.55 - u.height / 2))
    if sp.get("bottom"):
        TH.shadowed(f, txt(sp["bottom"], 120, YEL, maxw=1050), (x, H - 50), "lb")
    if sp.get("diagram") == "pyramid":
        TH.shadowed(f, pyramid_icon(), (W - 800, H - 680))
    elif sp.get("person"):
        add_person(f, sp["person"])
    return f


def v3_p03(sp):
    """화살표 변화: 회색 '전' → 굵은 화살표 → 크게 '후' + 아래 빨간 알약 '바꾼 건 ○○ 하나'"""
    f = bg(sp.get("photo", "tesla_chargers"), tuple(sp.get("focus", (0.5, 0.5))), 0.55, 0.0, sp.get("theme", "green"))
    a = TH.T(sp["before"], 250, (200, 204, 214))
    b = TH.T(sp["after"], 340, YEL)
    arr = TH.big_arrow(300, 230, WHITE)
    total = a.width + 30 + arr.width + 30 + b.width
    sc = min(1.0, 1840 / total)
    if sc < 1:
        a, b, arr = (im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS) for im in (a, b, arr))
    x = (W - (a.width + 30 + arr.width + 30 + b.width)) // 2
    y = sp.get("y", 330)
    TH.shadowed(f, a, (x, y + b.height - a.height - 20))
    TH.shadowed(f, arr, (x + a.width + 30, y + b.height // 2 - arr.height // 2))
    TH.shadowed(f, b, (x + a.width + 60 + arr.width, y))
    if sp.get("label"):
        TH.shadowed(f, txt(sp["label"], 100, WHITE, maxw=1800), (W / 2, 70), "mt")
    pill = G.pill(sp["sub"], "Black", 110, WHITE, (220, 40, 40), pad=(44, 18), radius=24)
    TH.shadowed(f, pill, (W / 2, H - 60), "mb")
    return f


def v3_p05(sp):
    """해본 사람 + 결과 감추기: 오르는 차트의 끝을 '?' 패널로 가림 + '결과는…'"""
    f = bg(sp.get("photo", "stock_monitor"), (0.5, 0.5), 0.7, 0.3, sp.get("theme", "blue"))
    ch = sp.get("chart")
    if ch:
        im = TH.chart_line(ch["series"], ch.get("start"), ch.get("end"), tuple(ch.get("color", (255, 70, 70))), 1500, 640)
        im = im.resize((W + 60, int(im.height * (W + 60) / im.width)), Image.LANCZOS)
        f.alpha_composite(im, (-60, H - im.height - 20))
    px = int(W * sp.get("hide_from", 0.66))
    pn = Image.new("RGBA", (W - px, H), (14, 16, 24, 235))
    d = ImageDraw.Draw(pn)
    for i in range(0, H, 40):
        d.line([(0, i), (W - px, i + 200)], fill=(40, 44, 60, 255), width=10)
    f.alpha_composite(pn, (px, 0))
    ImageDraw.Draw(f).line([(px, 0), (px, H)], fill=YEL + (255,), width=10)
    TH.shadowed(f, TH.T("?", 620, YEL), (px + (W - px) / 2, H / 2 - 40), "mm")
    t1 = txt(sp["line1"], 120, WHITE, maxw=px - 120)
    t2 = txt(sp["line2"], 170, YEL, maxw=px - 120)
    TH.shadowed(f, t1, (70, 60))
    TH.shadowed(f, t2, (70, 60 + t1.height - 10))
    TH.shadowed(f, txt(sp["line3"], 190, WHITE, maxw=px - 120), (70, H - 60), "lb")
    if sp.get("sticker"):
        TH.shadowed(f, stamp(sp["sticker"], 70, YEL, BLACK, 4), (px - 40, H - 330), "rt")
    return f


def v3_p06(sp):
    """몰락 · 경고: 흑백에 가까운 사진 + 위 '한때' 흰 줄 + 아래 빨간 띠 위 흰 결론 + 경고 스티커"""
    from PIL import ImageEnhance
    f = bright(sp.get("photo", "krx_building"), tuple(sp.get("focus", (0.5, 0.5))), dark=0.2, gray=0.9, sat=0.4)
    t = txt(sp["top"], 150, WHITE, maxw=1800)
    rb = txt(sp["bottom"], 200, WHITE, maxw=1780)
    by = H - rb.height - 90
    ImageDraw.Draw(f).rectangle((0, by - 30, W, H), fill=(205, 20, 20, 255))
    TH.shadowed(f, t, (W / 2, by - 50 - t.height), "mt")
    f.alpha_composite(rb, (int((W - rb.width) / 2), by + 10))
    TH.shadowed(f, stamp(sp.get("sticker", "경고!"), 130, YEL, BLACK, -8), (W - 70, 50), "rt")
    return f


def v3_p07(sp):
    """전문가 · 기관 한마디: 작은 직함/출처 라벨(얼굴 · 실물 옆) + 꾸밈없는 말투 큰 글씨"""
    f = bright(sp.get("photo", "server_rack"), tuple(sp.get("focus", (0.5, 0.5))), dark=0.15)
    band(f, int(H * 0.5), 225)
    lab = G.pill(sp["label"], "Black", 58, BLACK, WHITE, pad=(26, 10), radius=10)
    TH.shadowed(f, lab, tuple(sp.get("label_xy", (70, 60))))
    left_two(f, sp["top"], sp["bottom"], top_size=150, bot_size=200, bot_col=sp.get("bot_col", YEL) if not sp.get("red") else RED)
    if sp.get("person"):
        add_person(f, sp["person"])
    return f


def badge(name, d=460, ring=YEL, bgc=(30, 34, 48)):
    fig = cutout(name, int(d * 1.15))
    c = Image.new("RGBA", (d, d), bgc + (255,))
    c.alpha_composite(fig, ((d - fig.width) // 2, int(d * 0.08)))
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    c.putalpha(m)
    out = Image.new("RGBA", (d + 30, d + 30), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, d + 29, d + 29), fill=ring + (255,))
    out.alpha_composite(c, (15, 15))
    return out


def v3_p08(sp):
    """대결: 좌우 색 반반 + 위 두 원형 배지(인물/로고) + 가운데 VS + 아래 비교 기준 (승자 숨김)"""
    f = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    left = bg(sp.get("left", "tesla_chargers"), (0.5, 0.5), 0.45, 0.2, "blue").crop((W // 4, 0, W // 4 + W // 2, H))
    right = bg(sp.get("right", "server_rack"), (0.5, 0.5), 0.45, 0.2, "red").crop((W // 4, 0, W // 4 + W // 2, H))
    f.alpha_composite(left, (0, 0))
    f.alpha_composite(right, (W // 2, 0))
    ImageDraw.Draw(f).polygon([(W / 2 - 14, 0), (W / 2 + 26, 0), (W / 2 + 14, H), (W / 2 - 26, H)], fill=YEL + (255,))
    bl = badge(sp["badge_l"], ring=(90, 160, 255))
    br = badge(sp["badge_r"], ring=(255, 90, 90))
    TH.shadowed(f, bl, (W / 4, 60), "mt")
    TH.shadowed(f, br, (W * 3 / 4, 60), "mt")
    for x_, t_ in ((W / 4, sp.get("name_l", "")), (W * 3 / 4, sp.get("name_r", ""))):
        if t_:
            TH.shadowed(f, G.pill(t_, "Black", 64, BLACK, WHITE, pad=(26, 8), radius=12), (x_, 530), "mt")
    TH.shadowed(f, TH.T("VS", 230, YEL), (W / 2, 300), "mm")
    band(f, H - 260, 210, fade=60)
    TH.shadowed(f, txt(sp["bottom"], 170, WHITE, maxw=1820), (W / 2, H - 45), "mb")
    return f


def v3_p09(sp):
    """시청자 속마음: 사람 누끼 + 큰 말풍선(대사, 물음표 겹치기) + 아래 작은 단서"""
    f = bg(sp.get("photo", "seoul_subway"), tuple(sp.get("focus", (0.5, 0.5))), 0.5, 0.3, sp.get("theme", "blue"))
    if sp.get("person"):
        add_person(f, sp["person"])
    bub = TH.T(sp["bubble"], sp.get("bubble_size", 130), BLACK, stroke=0, max_w=sp.get("bubble_w", 1100), align="left")
    pad = 50
    card = Image.new("RGBA", (bub.width + pad * 2, bub.height + pad * 2 + 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width - 1, card.height - 71), 60, fill=(255, 255, 255, 252))
    d.polygon([(card.width - 260, card.height - 72), (card.width - 140, card.height - 72), (card.width - 60, card.height - 2)], fill=(255, 255, 255, 252))
    card.alpha_composite(bub, (pad, pad))
    TH.shadowed(f, card, (60, 50))
    if sp.get("bottom"):
        TH.shadowed(f, txt(sp["bottom"], 130, YEL, maxw=1150), (70, H - 50), "lb")
    return f


def v3_p10(sp):
    """실물 꽉 채우기: 밝은 실물 사진 그대로 + (작은 라벨) + 짧은 두 줄"""
    f = bright(sp.get("photo", "bess_site"), tuple(sp.get("focus", (0.5, 0.5))), dark=0.0, sat=1.15, contrast=1.15)
    if sp.get("person"):
        add_person(f, sp["person"])
    band(f, int(H * 0.6), 200)
    lab = txt(sp["label"], 80, WHITE, maxw=1800)
    y = left_two(f, sp["top"], sp["bottom"], top_size=140, bot_size=200) if sp.get("align") == "left" else None
    if y is None:
        bottom_two(f, sp["top"], sp["bottom"], top_size=140, bot_size=200)
        TH.shadowed(f, lab, (W / 2, H - 450), "mb")
    else:
        TH.shadowed(f, lab, (70, y - 10), "lb")
    return f


P.update({"P01": v3_p01, "P02": v3_p02, "P03": v3_p03, "P05": v3_p05, "P06": v3_p06, "P07": v3_p07,
          "P08": v3_p08, "P09": v3_p09, "P10": v3_p10})

def main(ep_dir):
    import render as R
    ep_dir = Path(ep_dir).resolve()
    ep, _ = R.load(ep_dir)
    od = TH.ROOT / "out" / ep_dir.name / "thumbs10"
    od.mkdir(parents=True, exist_ok=True)
    outs = []
    for sp in ep["thumbs10"]:
        f = TH.finish(P[sp["p"]](sp), frame=False)
        nm = sp.get("name", sp["p"])   # 같은 패턴 여러 시안: name: P04b
        path = od / f"{nm}.png"
        f.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path)
        outs.append((nm, path))
        print("썸네일 →", path)
    # 비교표 (2열 × 5행, 휴대폰 크기 확인용)
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * 2 + 30, (th + 50) * ((len(outs) + 1) // 2) + 10), (16, 16, 20))
    for i, (p, path) in enumerate(outs):
        x, y = 10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 50)
        sheet.paste(Image.open(path).resize((tw, th)), (x, y))
        G.blit(sheet := sheet.convert("RGBA"), TH.T(p, 30, (180, 255, 60), stroke=0), (x, y + th + 6))
        sheet = sheet.convert("RGB")
    sheet.save(od / "비교표.jpg", quality=90)
    print("비교표 →", od / "비교표.jpg")


if __name__ == "__main__":
    main(sys.argv[1])
