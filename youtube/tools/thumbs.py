"""썸네일 템플릿 모음 (클릭 유도형). 1920x1080으로 그려 1280x720으로 저장.

  python tools/thumbs.py episodes/ep004_templeton_vix          # episode.yaml 의 thumbs: 목록 전부
  python tools/thumbs.py --gallery                              # 템플릿 견본 한 장씩 (out/thumb_gallery/)

템플릿 (template: 이름) — 모두 채널 고유 디자인(남색 모눈 배경·금색·개미 캐릭터·계산기 모티프)
  calc        기울어진 계산기 LCD 화면에 결과 숫자 + 오른쪽 헤드라인 + 개미
  receipt     '백테스트 영수증'에 항목별 결과 + 왼쪽 헤드라인
  clipping    오래된 가상 신문 스크랩 + 큰 원형 도장 + 오른쪽 헤드라인
  diagonal    대각선 분할(왼쪽 위 vs 오른쪽 아래) 두 숫자 + 가운데 개미
  question    "~였다는데" + 초대형 "진짜일까?" + 큰 물음표
  big_number  큰 숫자 + 강조 문구 + 차트
  vs_numbers  숫자 대비
※ 다른 채널 썸네일의 구도·배색·소품 배치를 그대로 옮기지 않는다(레퍼런스는 '문구 공식'만 참고).

문구 공식: "~해라!", "~였다는데 진짜일까?", "~ 다 알려준다", "~ 따라만 해라", "~ 미쳤다…!"
단, 채널 원칙상 매수 권유로 읽히면 안 되므로 '해라' 계열은 따옴표·물음표로 '남들이 하는 말'임을 드러낸다.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from engine import charts  # noqa: E402
from engine import draw as G  # noqa: E402
from engine import illust as I  # noqa: E402
from engine import style as S  # noqa: E402

W, H = 1920, 1080
YELLOW = (255, 225, 40)
RED = (255, 52, 52)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (70, 230, 210)
NAMED = {"yellow": YELLOW, "red": RED, "white": WHITE, "teal": TEAL, "gold": S.GOLD, "up": S.UP, "down": S.DOWN,
         "blue": (60, 140, 255)}


def C(c, default=WHITE):
    if c is None:
        return default
    return tuple(c) if isinstance(c, (list, tuple)) else NAMED.get(c, default)


# ── 글자 ─────────────────────────────────────────────────────────
def T(text, size, color=WHITE, stroke=None, hl="", hl_color=YELLOW, max_w=0, align="left", weight="Black"):
    sw = stroke if stroke is not None else max(6, size // 11)
    return G.text_img(text, weight, size, C(color), stroke=sw, stroke_fill=BLACK, highlight=hl, hl_fill=C(hl_color),
                      max_w=max_w, align=align, line_gap=1.08)


def fit(text, size, maxw, **kw):
    im = T(text, size, **kw)
    while im.width > maxw and size > 40:
        size -= 6
        im = T(text, size, **kw)
    return im


def shadowed(f, im, xy, anchor="lt", blur=14, off=(8, 12), alpha=0.85):
    a = im.getchannel("A")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha)))
    G.blit(f, sh.filter(ImageFilter.GaussianBlur(blur)), (xy[0] + off[0], xy[1] + off[1]), 1, anchor)
    G.blit(f, im, xy, 1, anchor)


def lines_block(f, lines, y, x=None, maxw=1800, gap=-10):
    """[{text, size, color, hl, hl_color}] 를 가운데(또는 x) 정렬로 쌓기. 끝난 y 반환"""
    for ln in lines:
        im = fit(ln["text"], ln.get("size", 140), maxw, color=ln.get("color", "white"), hl=ln.get("hl", ""),
                 hl_color=ln.get("hl_color", "yellow"))
        shadowed(f, im, (W / 2 if x is None else x, y), "mt" if x is None else "lt")
        y += im.height + ln.get("gap", gap)
    return y


# ── 배경 ─────────────────────────────────────────────────────────
def bg_dark(glow=None, glow_pos=(0.5, 0.45)):
    f = Image.new("RGBA", (W, H), (10, 12, 20, 255))
    if glow:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cx, cy = W * glow_pos[0], H * glow_pos[1]
        ImageDraw.Draw(g).ellipse((cx - 700, cy - 450, cx + 700, cy + 450), fill=C(glow) + (110,))
        f.alpha_composite(g.filter(ImageFilter.GaussianBlur(200)))
    return f


def bg_burst(c1=(255, 60, 40), c2=(200, 0, 20), center=(0.5, 0.45)):
    f = Image.new("RGBA", (W, H), c2 + (255,))
    d = ImageDraw.Draw(f)
    cx, cy = W * center[0], H * center[1]
    for i in range(28):
        a = i * 2 * math.pi / 28
        b = a + math.pi / 28
        d.polygon([(cx, cy), (cx + 2600 * math.cos(a), cy + 2600 * math.sin(a)), (cx + 2600 * math.cos(b), cy + 2600 * math.sin(b))],
                  fill=c1 + (255,))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((cx - 520, cy - 420, cx + 520, cy + 420), fill=(255, 255, 255, 170))
    f.alpha_composite(g.filter(ImageFilter.GaussianBlur(140)))
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))  # 아래쪽 어둡게 → 글자 가독성
    vd = ImageDraw.Draw(vg)
    for y in range(H // 2, H, 4):
        vd.rectangle((0, y, W, y + 4), fill=(0, 0, 0, int(200 * ((y - H / 2) / (H / 2)) ** 1.4)))
    f.alpha_composite(vg)
    return f


def bg_split(left=(150, 30, 30), right=(20, 110, 110)):
    f = Image.new("RGBA", (W, H), (12, 14, 20, 255))
    for side, col, x0 in (("l", left, 0), ("r", right, W // 2)):
        g = Image.new("RGBA", (W // 2, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((-200, 100, W // 2 + 200, H + 300), fill=col + (200,))
        f.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)), (x0, 0))
    ImageDraw.Draw(f).line((W / 2, 0, W / 2, H), fill=(0, 0, 0, 255), width=10)
    return f


# ── 소품 ─────────────────────────────────────────────────────────
def big_arrow(w=420, h=300, color=WHITE):
    k = 3
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W2, H2 = w * k, h * k
    d.polygon([(0, H2 * 0.3), (W2 * 0.55, H2 * 0.3), (W2 * 0.55, 0), (W2, H2 / 2), (W2 * 0.55, H2), (W2 * 0.55, H2 * 0.7), (0, H2 * 0.7)],
              fill=color + (255,))
    im = im.reduce(k)
    fade = Image.linear_gradient("L").rotate(90).resize(im.size)  # 왼쪽 투명 → 오른쪽 불투명
    a = Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), fade.point(lambda v: 255 - v))
    im.putalpha(a)
    return im


def rising_arrow(w=900, h=600, color=(60, 150, 255)):
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0.02, 0.95), (0.3, 0.75), (0.55, 0.55), (0.78, 0.28), (0.9, 0.12)]
    P = [(x * w * k, y * h * k) for x, y in pts]
    d.line(P, fill=color + (255,), width=60 * k, joint="curve")
    ex, ey = P[-1]
    ang = math.atan2(P[-1][1] - P[-2][1], P[-1][0] - P[-2][0])
    L = 120 * k
    d.polygon([(ex + math.cos(ang) * L, ey + math.sin(ang) * L), (ex + math.cos(ang + 2.3) * L, ey + math.sin(ang + 2.3) * L),
               (ex + math.cos(ang - 2.3) * L, ey + math.sin(ang - 2.3) * L)], fill=color + (255,))
    im = im.reduce(k)
    glow = im.filter(ImageFilter.GaussianBlur(18))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


def order_screen(title="매수주문이 정상적으로\n접수되었습니다.", sub="TQQQ · 시장가", w=560, h=420):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=28, fill=(250, 250, 250, 255))
    d.rounded_rectangle((0, h - 100, w - 1, h - 1), radius=28, fill=(40, 170, 80, 255))
    d.rectangle((0, h - 100, w - 1, h - 72), fill=(40, 170, 80, 255))
    cx = w / 2
    d.ellipse((cx - 44, 36, cx + 44, 124), outline=(40, 160, 80, 255), width=8)
    d.line([(cx - 20, 82), (cx - 4, 98), (cx + 24, 64)], fill=(40, 160, 80, 255), width=9, joint="curve")
    t = G.text_img(title, "Bold", 38, (30, 30, 30), align="center", max_w=w - 60)
    im.alpha_composite(t, (int(cx - t.width / 2), 150))
    if sub:
        s = G.text_img(sub, "SemiBold", 28, (120, 120, 120))
        im.alpha_composite(s, (int(cx - s.width / 2), 150 + t.height + 8))
    ok = G.text_img("확인", "Bold", 40, WHITE)
    im.alpha_composite(ok, (int(cx - ok.width / 2), h - 72))
    return im


def icon_box(inner, size=440, bg=(232, 120, 80), radius=70, label=None):
    """둥근 사각 앱 아이콘 상자 + 안쪽 그림(이모지 이름/텍스트/이미지)"""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=C(bg) + (255,))
    if isinstance(inner, Image.Image):
        x = inner.copy()
        x.thumbnail((int(size * 0.8), int(size * 0.8)))
        im.alpha_composite(x, ((size - x.width) // 2, (size - x.height) // 2))
    elif isinstance(inner, str) and (ROOT / "assets" / "emoji" / f"{inner}.png").exists():
        e = I.emoji(inner, int(size * 0.72))
        im.alpha_composite(e, ((size - e.width) // 2, (size - e.height) // 2))
    else:
        t = fit(str(inner), int(size * 0.34), int(size * 0.86), color="white")
        im.alpha_composite(t, ((size - t.width) // 2, (size - t.height) // 2))
    if label:
        lb = T(label, 54, "white")
        out = Image.new("RGBA", (max(size, lb.width), size + lb.height + 10), (0, 0, 0, 0))
        out.alpha_composite(im, ((out.width - size) // 2, 0))
        out.alpha_composite(lb, ((out.width - lb.width) // 2, size + 10))
        return out
    return im


def chart_line(series, start=None, end=None, color=(255, 80, 80), w=800, h=420, log=False, glow=True):
    spec = {"lines": [{"series": series, "color": list(color), "fill": True}], "start": start, "end": end,
            "log": log, "draw": {"on": 1, "dur": 0.01}}
    lc = charts.LineChart(spec, rect=(60, 60, w, h))
    im = lc.line.crop((40, 20, w + 90, h + 90))
    if glow:
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(im.filter(ImageFilter.GaussianBlur(8)))
        out.alpha_composite(im)
        return out
    return im


def prop(spec):
    """소품 하나 만들기: {kind: ant|money|order|rising|emoji|chart|calculator|image, ...}"""
    k = spec["kind"]
    if k == "ant":
        from engine.character import ant_side
        return ant_side(spec.get("size", 600), spec.get("carry", "money"), mood=spec.get("mood", "smile"))
    if k == "money":
        from engine.character import money_stack
        n = spec.get("stacks", 1)
        one = money_stack(spec.get("w", 420), spec.get("h", 300))
        if n == 1:
            return one
        out = Image.new("RGBA", (one.width + (n - 1) * 60, one.height + (n - 1) * 80), (0, 0, 0, 0))
        for i in range(n):
            out.alpha_composite(one, (i * 60, (n - 1 - i) * 80))
        return out
    if k == "order":
        return order_screen(spec.get("title", "매수주문이 정상적으로\n접수되었습니다."), spec.get("sub", ""))
    if k == "rising":
        return rising_arrow(spec.get("w", 900), spec.get("h", 600), C(spec.get("color"), (60, 150, 255)))
    if k == "emoji":
        return I.emoji(spec["name"], spec.get("size", 400))
    if k == "chart":
        return chart_line(spec["series"], spec.get("start"), spec.get("end"), C(spec.get("color"), (255, 80, 80)),
                          spec.get("w", 800), spec.get("h", 420), spec.get("log", False))
    if k == "calculator":
        sys.path.insert(0, str(ROOT / "tools"))
        from make_branding import calculator
        return calculator(spec.get("w", 260), spec.get("h", 360), spec.get("display", "×3"))
    if k == "image":
        return Image.open(ROOT / "assets" / "media" / spec["file"]).convert("RGBA")
    raise KeyError(k)


def place_props(f, props):
    for p in props or []:
        im = prop(p)
        if p.get("scale"):
            im = im.resize((int(im.width * p["scale"]), int(im.height * p["scale"])), Image.LANCZOS)
        if p.get("rot"):
            im = im.rotate(p["rot"], resample=Image.BICUBIC, expand=True)
        if p.get("flip"):
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        shadowed(f, im, tuple(p.get("pos", (W / 2, H / 2))), p.get("anchor", "mm"), blur=20, off=(10, 16), alpha=0.6)


# ── 템플릿 ───────────────────────────────────────────────────────

# ── 채널 고유 템플릿 (계산기 · 영수증 · 신문 스크랩 · 대각선 분할) ─────────────
NAVY = (14, 20, 38)
CREAM = (250, 244, 226)
LCD_BG = (38, 52, 34)
LCD_FG = (170, 255, 140)


def bg_brand(glow=S.GOLD, pos=(0.3, 0.4)):
    f = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(f)
    for x in range(0, W, 60):   # 모눈종이 패턴 (계산 노트 느낌)
        d.line((x, 0, x, H), fill=(255, 255, 255, 10))
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(255, 255, 255, 10))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = W * pos[0], H * pos[1]
    ImageDraw.Draw(g).ellipse((cx - 650, cy - 450, cx + 650, cy + 450), fill=C(glow) + (70,))
    f.alpha_composite(g.filter(ImageFilter.GaussianBlur(180)))
    return f


def tag(text, color=S.GOLD, fg=NAVY, size=44):
    return G.pill(text, "Black", size, fg, C(color), pad=(26, 10), radius=12)


def t_calc(sp):
    """계산기 LCD에 결과 숫자. 오른쪽에 헤드라인 + 개미"""
    f = bg_brand(sp.get("glow", S.GOLD), (0.25, 0.5))
    k = 2
    bw, bh = 1040, 1180
    body = Image.new("RGBA", (bw * k, bh * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, bw * k - 1, bh * k - 1), radius=90 * k, fill=(34, 38, 52, 255))
    d.rounded_rectangle((18 * k, 18 * k, bw * k - 18 * k, bh * k - 18 * k), radius=76 * k, fill=(52, 58, 80, 255))
    d.rounded_rectangle((70 * k, 80 * k, bw * k - 70 * k, 420 * k), radius=30 * k, fill=LCD_BG + (255,))
    cols = [(220, 224, 236)] * 3 + [S.GOLD]
    for r in range(4):
        for c in range(4):
            x0, y0 = (80 + c * 225) * k, (490 + r * 170) * k
            d.rounded_rectangle((x0, y0, x0 + 190 * k, y0 + 135 * k), radius=26 * k,
                                fill=(S.UP if (r == 3 and c == 3) else cols[c]) + (255,))
    body = body.reduce(k)
    ghost = G.text_img("8888", "Black", 250, (60, 80, 56))
    body.alpha_composite(ghost, (bw - 90 - ghost.width, 120))
    val = fit(sp["value"], 260, bw - 180, color=sp.get("value_color", LCD_FG), stroke=0)
    glow = val.filter(ImageFilter.GaussianBlur(12))
    body.alpha_composite(glow, (bw - 95 - val.width, 250 - val.height // 2))
    body.alpha_composite(val, (bw - 95 - val.width, 250 - val.height // 2))
    if sp.get("lcd_label"):
        body.alpha_composite(G.text_img(sp["lcd_label"], "Bold", 40, LCD_FG), (100, 100))
    body = body.rotate(sp.get("rot", 7), resample=Image.BICUBIC, expand=True)
    shadowed(f, body, (40, 150), "lt", blur=30, off=(20, 30), alpha=0.7)
    y = 110
    if sp.get("tag"):
        tg = tag(sp["tag"])
        G.blit(f, tg, (1120, y))
        y += tg.height + 30
    lines_block(f, sp["lines"], y, x=1110, maxw=780, gap=0)
    if sp.get("ant", True):
        from engine.character import ant_side
        a = ant_side(380, sp.get("carry", "money"), mood=sp.get("mood", "smile"))
        shadowed(f, a, (W - 40, H + 30), "rb", blur=16, alpha=0.5)
    return f


def _zigzag(im, top=True, bottom=True, tooth=26):
    w, h = im.size
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for x in range(0, w + tooth, tooth):
        if top:
            d.polygon([(x, 0), (x + tooth / 2, tooth * 0.6), (x + tooth, 0)], fill=0)
        if bottom:
            d.polygon([(x, h), (x + tooth / 2, h - tooth * 0.6), (x + tooth, h)], fill=0)
    a = im.getchannel("A")
    im.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").array(a), __import__("numpy").array(m))))
    return im


def t_receipt(sp):
    """영수증에 매매 결과를 항목별로. 왼쪽 헤드라인"""
    f = bg_brand(sp.get("glow", S.UP), (0.75, 0.5))
    rw = 820
    rows = sp["rows"]
    rh = 210 + len(rows) * 104 + 170
    r = Image.new("RGBA", (rw, rh), CREAM + (255,))
    d = ImageDraw.Draw(r)
    ttl = G.text_img(sp.get("receipt_title", "개미의 계산기"), "Black", 52, (30, 30, 30))
    r.alpha_composite(ttl, ((rw - ttl.width) // 2, 50))
    sub = G.text_img(sp.get("receipt_sub", "백테스트 영수증"), "SemiBold", 32, (110, 110, 110))
    r.alpha_composite(sub, ((rw - sub.width) // 2, 120))
    for x in range(40, rw - 40, 22):
        d.line((x, 185, x + 12, 185), fill=(120, 120, 120, 255), width=3)
    y = 215
    for row in rows:
        c = C(row.get("color"), (30, 30, 30))
        a = G.text_img(row["k"], "Bold", 48, (50, 50, 50))
        b = G.text_img(row["v"], "Black", row.get("size", 64), c)
        r.alpha_composite(a, (50, y + (b.height - a.height) // 2))
        r.alpha_composite(b, (rw - 50 - b.width, y))
        y += 104
    for x in range(40, rw - 40, 22):
        d.line((x, y + 10, x + 12, y + 10), fill=(120, 120, 120, 255), width=3)
    tot = G.text_img(sp.get("total", ""), "Black", 54, C(sp.get("total_color"), S.UP))
    r.alpha_composite(tot, ((rw - tot.width) // 2, y + 40))
    r = _zigzag(r)
    r = r.rotate(sp.get("rot", -6), resample=Image.BICUBIC, expand=True)
    shadowed(f, r, (W - 120, H / 2 + 10), "rm", blur=26, off=(18, 26), alpha=0.6)
    y = 120
    if sp.get("tag"):
        tg = tag(sp["tag"])
        G.blit(f, tg, (90, y))
        y += tg.height + 30
    lines_block(f, sp["lines"], y, x=80, maxw=1000, gap=0)
    return f


def t_clipping(sp):
    """오래된 신문 스크랩 + 큰 도장. 오른쪽 헤드라인 (가상 신문, 실제 매체 아님)"""
    f = bg_brand(sp.get("glow", S.GOLD), (0.3, 0.5))
    pw, ph = 860, 900
    pap = Image.new("RGBA", (pw, ph), (236, 226, 196, 255))
    d = ImageDraw.Draw(pap)
    mast = G.text_img(sp.get("masthead", "THE DAILY MARKET"), "Black", 64, (40, 34, 26))
    pap.alpha_composite(mast, ((pw - mast.width) // 2, 40))
    d.line((40, 130, pw - 40, 130), fill=(40, 34, 26, 255), width=5)
    d.line((40, 140, pw - 40, 140), fill=(40, 34, 26, 255), width=2)
    dt = G.text_img(sp.get("date", ""), "Bold", 30, (90, 80, 60))
    pap.alpha_composite(dt, (40, 152))
    hl = G.text_img(sp["headline"], "Black", 84, (30, 26, 20), max_w=pw - 80, line_gap=1.05)
    pap.alpha_composite(hl, (40, 210))
    yy = 210 + hl.height + 40
    import random
    rnd = random.Random(3)
    while yy < ph - 60:
        for col in (0, 1):
            x0 = 40 + col * (pw - 80) // 2
            ww = (pw - 120) // 2 * (0.6 if rnd.random() < 0.15 else 1.0)
            d.rounded_rectangle((x0, yy, x0 + ww, yy + 14), radius=7, fill=(160, 148, 120, 255))
        yy += 34
    import numpy as np  # 오래된 종이 얼룩
    noise = Image.fromarray((np.random.default_rng(1).normal(0, 12, (ph, pw)) + 128).clip(0, 255).astype("uint8"), "L")
    pap = Image.composite(pap, Image.new("RGBA", (pw, ph), (200, 186, 150, 255)), noise.point(lambda v: 255 if v > 100 else 210))
    pap = pap.rotate(sp.get("rot", 5), resample=Image.BICUBIC, expand=True)
    shadowed(f, pap, (60, H / 2), "lm", blur=26, off=(18, 26), alpha=0.6)
    st = sp.get("stamp")
    if st:
        s_ = 500
        k = 3
        stamp = Image.new("RGBA", (s_ * k, s_ * k), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        col = C(st.get("color"), (220, 40, 40))
        sd.ellipse((10, 10, s_ * k - 10, s_ * k - 10), outline=col + (235,), width=24 * k // 2)
        sd.ellipse((60, 60, s_ * k - 60, s_ * k - 60), outline=col + (235,), width=8 * k // 2)
        stamp = stamp.reduce(k)
        t = G.text_img(st["text"], "Black", st.get("size", 120), col)
        stamp.alpha_composite(t, ((s_ - t.width) // 2, (s_ - t.height) // 2 - 6))
        if st.get("sub"):
            u = G.text_img(st["sub"], "Black", 56, col)
            stamp.alpha_composite(u, ((s_ - u.width) // 2, s_ - 140))
        stamp = stamp.rotate(-14, resample=Image.BICUBIC, expand=True)
        G.blit(f, stamp, tuple(st.get("pos", (760, 760))), 0.95, "mm")
    y = 120
    if sp.get("tag"):
        tg = tag(sp["tag"])
        G.blit(f, tg, (1060, y))
        y += tg.height + 30
    lines_block(f, sp["lines"], y, x=1050, maxw=830, gap=0)
    return f


def t_diagonal(sp):
    """대각선 분할: 왼쪽 위 vs 오른쪽 아래, 가운데 개미"""
    a, b = C(sp.get("a_color"), (120, 20, 30)), C(sp.get("b_color"), (16, 110, 100))
    f = Image.new("RGBA", (W, H), b + (255,))
    top = Image.new("RGBA", (W, H), a + (255,))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, 0), (W * 0.72, 0), (W * 0.28, H), (0, H)], fill=255)
    f = Image.composite(top, f, m)
    for side in ("a", "b"):
        c = sp[side]
        if c.get("chart"):
            ch = dict(c["chart"])
            im = chart_line(ch.pop("series"), ch.get("start"), ch.get("end"), C(ch.get("color"), WHITE), 820, 360)
            G.blit(f, G.with_opacity(im, 0.55), (40, 560) if side == "a" else (W - 40, 100), 1, "lt" if side == "a" else "rt")
    d = ImageDraw.Draw(f)
    d.line([(W * 0.72, 0), (W * 0.28, H)], fill=(255, 255, 255, 255), width=14)
    A, B = sp["a"], sp["b"]
    shadowed(f, fit(A["label"], 70, 820), (80, 70), "lt")
    shadowed(f, fit(A["value"], 260, 880, color=A.get("color", "red")), (70, 160), "lt")
    shadowed(f, fit(B["label"], 70, 820), (W - 80, H - 400), "rt")
    shadowed(f, fit(B["value"], 260, 880, color=B.get("color", "teal")), (W - 70, H - 60), "rb")
    if sp.get("ant", True):
        from engine.character import ant_side
        an = ant_side(420, None, mood="wow")
        shadowed(f, an, (W / 2 + 30, H / 2 + 30), "mm", blur=16, alpha=0.5)
    if sp.get("center"):
        shadowed(f, fit(sp["center"], 80, 700, color="yellow"), (W - 80, 60), "rt")
    if sp.get("bottom"):
        shadowed(f, fit(sp["bottom"], 80, 760, color="white"), (80, H - 60), "lb")
    return f


def t_question(sp):
    f = bg_dark(sp.get("glow", (40, 60, 160)), (0.72, 0.5))
    q = T("?", 900, "yellow", stroke=24)
    G.blit(f, q.rotate(-12, resample=Image.BICUBIC, expand=True), (W - 380, H / 2 + 40), 0.95, "mm")
    place_props(f, sp.get("props"))
    lines_block(f, sp["lines"], 90, x=90, maxw=1250, gap=0)
    return f


def t_big_number(sp):
    f = bg_dark(sp.get("glow", (150, 20, 40)), (0.8, 0.5))
    place_props(f, sp.get("props"))
    lines_block(f, sp["lines"], 80, x=90, maxw=1100, gap=-10)
    return f


def t_vs_numbers(sp):
    f = bg_split(C(sp.get("left_color"), (150, 30, 30)), C(sp.get("right_color"), (20, 50, 150)))
    if sp.get("top"):
        shadowed(f, fit(sp["top"], 96, 1800, hl=sp.get("top_hl", ""), hl_color="yellow"), (W / 2, 40), "mt")
    for side, x in (("left", W * 0.25), ("right", W * 0.75)):
        c = sp[side]
        shadowed(f, fit(c["label"], 64, 860, color="white"), (x, 230), "mt")
        shadowed(f, fit(c["value"], 230, 720, color=c.get("color", "red")), (x, 560), "mm")
        if c.get("sub"):
            shadowed(f, fit(c["sub"], 64, 860), (x, 760), "mt")
    shadowed(f, T("VS", 150, "yellow"), (W / 2, 560), "mm")
    return f


TEMPLATES = {"calc": t_calc, "receipt": t_receipt, "clipping": t_clipping, "diagonal": t_diagonal,
             "question": t_question, "big_number": t_big_number, "vs_numbers": t_vs_numbers}



def render(sp, out):
    f = TEMPLATES[sp["template"]](sp)
    f.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out)
    return out


def main(argv):
    import render as R
    ep_dir = Path(argv[0]).resolve()
    ep, _ = R.load(ep_dir)
    od = ROOT / "out" / ep_dir.name / "thumbs"
    od.mkdir(parents=True, exist_ok=True)
    for i, sp in enumerate(ep["thumbs"], 1):
        print("썸네일 →", render(sp, od / f"thumb{i}_{sp['template']}.png"))


if __name__ == "__main__":
    main(sys.argv[1:])
