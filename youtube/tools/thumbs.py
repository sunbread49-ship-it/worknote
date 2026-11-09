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
  silhouette  인물(상반신) 또는 사물 실루엣 + 테두리 빛 + 큰 물음표 + 힌트 아이콘(칩 · 이모지 실루엣)
※ 답(결과 숫자)은 비워 두거나 ???로 가린다 — 궁금증 유발 (EP009 피드백)
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


# ── 사진 배경 (위키미디어) + 고급 마감 ───────────────────────────
def _photo_src(name):
    import json
    m = json.loads((ROOT / "assets" / "photos" / f"{name}.json").read_text())
    return Image.open(ROOT / "assets" / "photos" / m["file"]).convert("RGB")


def grade(im, dark=0.35, gray=0.35, sh=(10, 18, 44), hi=(255, 214, 168), split=0.32, contrast=1.08):
    """시네마틱 색보정: 채도 낮추고 그림자는 남색 · 밝은 곳은 따뜻하게(split toning)"""
    import numpy as np
    a = np.asarray(im.convert("RGB"), np.float32) / 255
    lum = (a * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
    a = a * (1 - gray) + lum * gray
    a = np.clip((a - 0.5) * contrast + 0.5, 0, 1)
    tone = np.array(sh, np.float32) / 255 * (1 - lum) + np.array(hi, np.float32) / 255 * lum
    a = a * (1 - split) + tone * a * 2 * split
    a = a * (1 - dark)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8"), "RGB").convert("RGBA")


def photo_fill(name, w, h, focus=(0.5, 0.5), dark=0.35, blur=0, gray=0.35, tint=None, tint_amt=0.0, mirror=False):
    im = _photo_src(name)
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    sc = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = int((im.width - w) * focus[0]), int((im.height - h) * focus[1])
    im = im.crop((x0, y0, x0 + w, y0 + h))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    out = grade(im, dark=dark, gray=gray)
    if tint is not None and tint_amt > 0:
        out = Image.blend(out, Image.new("RGBA", out.size, C(tint) + (255,)), tint_amt)
    return out


def photo_bg(ph, shade=None):
    """ph: 파일명 또는 {file, focus, dark, blur, gray, tint, tint_amt}. shade: left|right|bottom 글자 쪽을 더 어둡게"""
    if isinstance(ph, str):
        ph = {"file": ph}
    f = photo_fill(ph["file"], W, H, tuple(ph.get("focus", (0.5, 0.5))), ph.get("dark", 0.35), ph.get("blur", 0),
                   ph.get("gray", 0.35), ph.get("tint"), ph.get("tint_amt", 0.0), ph.get("mirror", False))
    shade = ph.get("shade", shade)
    if shade:
        import numpy as np
        if shade in ("left", "right"):
            g = np.linspace(1, 0, W) if shade == "left" else np.linspace(0, 1, W)
            g = np.clip(g * 1.5 - 0.25, 0, 1) ** 1.3
            a = np.tile(g[None, :], (H, 1))
        else:
            g = np.clip(np.linspace(-0.4, 1, H), 0, 1) ** 1.2
            a = np.tile(g[:, None], (1, W))
        lay = Image.new("RGBA", (W, H), (6, 8, 16, 0))
        lay.putalpha(Image.fromarray((a * 215).astype("uint8")))
        f.alpha_composite(lay)
    return f


def finish(f, frame=True):
    """고급 마감: 비네팅 · 필름 그레인 · 얇은 금색 안쪽 테두리"""
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip((r - 0.75) / 0.75, 0, 1) ** 1.5
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vg.putalpha(Image.fromarray((v * 150).astype("uint8")))
    f.alpha_composite(vg)
    n = np.random.default_rng(7).normal(0, 1, (H // 2, W // 2))
    gr = Image.fromarray(((n * 0.5 + 0.5).clip(0, 1) * 255).astype("uint8"), "L").resize((W, H), Image.BILINEAR)
    lay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    lay.putalpha(gr.point(lambda x: int(abs(x - 128) * 0.14)))
    f.alpha_composite(lay)
    if frame:
        ImageDraw.Draw(f).rectangle((26, 26, W - 27, H - 27), outline=(232, 196, 120, 120), width=3)
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
        from engine.character import croc_bird
        return croc_bird(int(spec.get("size", 600) * 0.75))
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
    f = photo_bg(sp["photo"], "right") if sp.get("photo") else bg_brand(sp.get("glow", S.GOLD), (0.25, 0.5))
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
        from engine.character import croc_bird
        a = croc_bird(260)
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
    f = photo_bg(sp["photo"], "left") if sp.get("photo") else bg_brand(sp.get("glow", S.UP), (0.75, 0.5))
    rw = 820
    rows = sp["rows"]
    rh = 210 + len(rows) * 104 + 170
    r = Image.new("RGBA", (rw, rh), CREAM + (255,))
    d = ImageDraw.Draw(r)
    ttl = G.text_img(sp.get("receipt_title", "주식 악어새"), "Black", 52, (30, 30, 30))
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
    f = photo_bg(sp["photo"], "right") if sp.get("photo") else bg_brand(sp.get("glow", S.GOLD), (0.3, 0.5))
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
    A_, B_ = sp["a"], sp["b"]
    f = (photo_fill(B_["photo"], W, H, tuple(B_.get("focus", (0.5, 0.5))), B_.get("dark", 0.3), 0, 0.5, b, B_.get("tint_amt", 0.45))
         if B_.get("photo") else Image.new("RGBA", (W, H), b + (255,)))
    top = (photo_fill(A_["photo"], W, H, tuple(A_.get("focus", (0.5, 0.5))), A_.get("dark", 0.3), 0, 0.5, a, A_.get("tint_amt", 0.45))
           if A_.get("photo") else Image.new("RGBA", (W, H), a + (255,)))
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
    # EP010 피드백: 대각선 안 문구는 더 크고 직관적으로 (라벨 110 · 숫자 300 · 위/아래 문구 120)
    shadowed(f, fit(A["label"], sp.get("label_size", 110), 900), (80, 60), "lt", blur=18)
    shadowed(f, fit(A["value"], sp.get("value_size", 300), 900, color=A.get("color", "red")), (70, 190), "lt", blur=18)
    shadowed(f, fit(B["label"], sp.get("label_size", 110), 900), (W - 80, H - 600), "rt", blur=18)
    shadowed(f, fit(B["value"], sp.get("value_size", 300), 900, color=B.get("color", "teal")), (W - 70, H - 60), "rb", blur=18)
    if sp.get("ant", True):
        from engine.character import croc_bird
        an = croc_bird(300)
        shadowed(f, an, (W / 2 + 30, H / 2 + 30), "mm", blur=16, alpha=0.5)
    if sp.get("center"):
        shadowed(f, fit(sp["center"], sp.get("center_size", 120), 820, color="yellow"), (W - 80, 60), "rt", blur=18)
    if sp.get("bottom"):
        shadowed(f, fit(sp["bottom"], sp.get("bottom_size", 120), 860, color="white"), (80, H - 60), "lb", blur=18)
    return f


def t_question(sp):
    f = photo_bg(sp["photo"], "left") if sp.get("photo") else bg_dark(sp.get("glow", (40, 60, 160)), (0.72, 0.5))
    q = T("?", 900, "yellow", stroke=24)
    G.blit(f, q.rotate(-12, resample=Image.BICUBIC, expand=True), (W - 380, H / 2 + 40), 0.95, "mm")
    place_props(f, sp.get("props"))
    lines_block(f, sp["lines"], 90, x=90, maxw=1250, gap=0)
    return f


def t_big_number(sp):
    f = photo_bg(sp["photo"], "left") if sp.get("photo") else bg_dark(sp.get("glow", (150, 20, 40)), (0.8, 0.5))
    place_props(f, sp.get("props"))
    lines_block(f, sp["lines"], 80, x=90, maxw=1100, gap=-10)
    return f


def t_vs_numbers(sp):
    f = bg_split(C(sp.get("left_color"), (150, 30, 30)), C(sp.get("right_color"), (20, 50, 150)))
    for side, x0, colk, dflt in (("left", 0, "left_color", (150, 30, 30)), ("right", W // 2, "right_color", (20, 50, 150))):
        c = sp[side]
        if c.get("photo"):
            im = photo_fill(c["photo"], W // 2, H, tuple(c.get("focus", (0.5, 0.5))), c.get("dark", 0.4), 0, 0.5,
                            C(sp.get(colk), dflt), c.get("tint_amt", 0.4))
            f.alpha_composite(im, (x0, 0))
    ImageDraw.Draw(f).line((W / 2, 0, W / 2, H), fill=(232, 196, 120, 255), width=6)
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



# ── 실루엣 (인물 · 사물) ─────────────────────────────────────────
def person_bust(h=900, jacket=True, color=(8, 9, 14)):
    """정면 상반신 실루엣(얼굴 없음). 가죽 재킷 깃 옵션"""
    k = 2
    w = int(h * 0.9)
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w * k / 2
    hr = h * k * 0.14                                     # 머리 반지름
    hy = h * k * 0.26
    d.ellipse((cx - hr * 0.86, hy - hr * 1.08, cx + hr * 0.86, hy + hr * 1.08), fill=color + (255,))
    # 머리카락 볼륨
    d.ellipse((cx - hr * 0.95, hy - hr * 1.2, cx + hr * 0.95, hy + hr * 0.2), fill=color + (255,))
    d.rectangle((cx - hr * 0.42, hy + hr * 0.6, cx + hr * 0.42, hy + hr * 1.6), fill=color + (255,))   # 목
    top = hy + hr * 1.35
    d.polygon([(cx - hr * 0.55, top - 4), (cx + hr * 0.55, top - 4), (cx + w * k * 0.33, top + h * k * 0.08),
               (cx - w * k * 0.33, top + h * k * 0.08)], fill=color + (255,))
    d.rounded_rectangle((cx - w * k * 0.49, top + h * k * 0.05, cx + w * k * 0.49, h * k + w * k * 0.3), radius=int(w * k * 0.2), fill=color + (255,))
    if jacket:  # 재킷 깃 하이라이트(아주 옅게)
        hl = (40, 42, 52, 255)
        d.polygon([(cx - hr * 0.5, top + 10), (cx - hr * 1.5, top + h * k * 0.32), (cx - hr * 0.2, top + h * k * 0.2)], fill=hl)
        d.polygon([(cx + hr * 0.5, top + 10), (cx + hr * 1.5, top + h * k * 0.32), (cx + hr * 0.2, top + h * k * 0.2)], fill=hl)
    return im.resize((w, h), Image.LANCZOS)


def chip_icon(size=300, glow=(118, 185, 0)):
    """반도체 칩 아이콘(특정 회사 로고 아님)"""
    k = 2
    S2 = size * k
    im = Image.new("RGBA", (S2, S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = S2 * 0.18
    for i in range(6):
        p = m + (S2 - 2 * m) * (i + 0.5) / 6
        for a, b in (((p - 8, 0), (p + 8, m)), ((p - 8, S2 - m), (p + 8, S2)), ((0, p - 8), (m, p + 8)), ((S2 - m, p - 8), (S2, p + 8))):
            d.rectangle((a, b), fill=(200, 205, 215, 255))
    d.rounded_rectangle((m, m, S2 - m, S2 - m), radius=24, fill=(24, 26, 34, 255), outline=glow + (255,), width=10)
    d.rounded_rectangle((S2 * 0.34, S2 * 0.34, S2 * 0.66, S2 * 0.66), radius=12, fill=glow + (255,))
    return im.resize((size, size), Image.LANCZOS)


def rim(im, color, blur=26, grow=1.04):
    """실루엣 뒤 테두리 빛"""
    a = im.getchannel("A").resize((int(im.width * grow), int(im.height * grow)))
    pad = blur * 3
    big = Image.new("L", (a.width + pad * 2, a.height + pad * 2), 0)
    big.paste(a, (pad, pad))
    g = Image.new("RGBA", big.size, color + (0,))
    g.putalpha(big.filter(ImageFilter.GaussianBlur(blur)))
    return g


def t_silhouette(sp):
    rc = C(sp.get("rim", "gold"))
    f = photo_bg(sp["photo"], "left") if sp.get("photo") else bg_dark(sp.get("glow", (40, 50, 90)), (0.72, 0.55))
    fig = sp.get("figure", "person")
    if str(fig).endswith(".png"):  # 실제 사진에서 따낸 실루엣 (assets/people/*.png)
        im = Image.open(ROOT / "assets" / fig).convert("RGBA")
        h = sp.get("fig_h", 1000)
        im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
        im.putalpha(im.getchannel("A"))
        dark = Image.new("RGBA", im.size, (8, 9, 14, 255))
        dark.putalpha(im.getchannel("A"))
        im = dark
    elif fig == "person":
        im = person_bust(sp.get("fig_h", 960))
    else:
        from engine.editorial import silhouette
        im = silhouette(fig, sp.get("fig_h", 700), (8, 9, 14))
    x, y = sp.get("fig_x", W - 520), sp.get("fig_y", H + 20)
    gl = rim(im, rc)
    gx, gy = int(x - gl.width / 2), int(y - gl.height + 10 + 26 * 3)
    G.blit(f, gl, (gx, gy))
    G.blit(f, gl, (gx, gy), 0.6)
    G.blit(f, im, (x, y), 1, "mb")
    if sp.get("mark", "?"):
        q = T(sp.get("mark", "?"), sp.get("mark_size", 300), "yellow", stroke=14)
        shadowed(f, q, (x, y - im.height * sp.get("mark_at", 0.74)), "mm")
    hint = sp.get("hint")
    if hint:
        if hint.get("kind") == "chip":
            hi = chip_icon(hint.get("size", 260), C(hint.get("color"), (118, 185, 0)))
        else:
            from engine.editorial import silhouette
            hi = silhouette(hint["emoji"], hint.get("size", 240), C(hint.get("color"), YELLOW))
        hg = rim(hi, C(hint.get("color"), (118, 185, 0)), blur=30, grow=1.15)
        hx, hy = hint.get("pos", [x - 470, 300])
        G.blit(f, hg, (hx, hy), 0.9, "mm")
        hi = hi.rotate(hint.get("rot", -10), expand=True, resample=Image.BICUBIC)
        G.blit(f, hi, (hx, hy), 1, "mm")
    yy = 90
    if sp.get("tag"):
        tg = tag(sp["tag"])
        G.blit(f, tg, (90, yy))
        yy += tg.height + 30
    lines_block(f, sp["lines"], yy, x=80, maxw=sp.get("text_w", 1000), gap=sp.get("gap", -4))
    return f


def render(sp, out):
    f = TEMPLATES[sp["template"]](sp)
    if sp.get("stickers") and sp["template"] != "hook":
        place_stickers(f, sp["stickers"])
    if sp.get("finish", True):
        f = finish(f, sp.get("frame", True))
    f.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out)
    return out


TEMPLATES["silhouette"] = t_silhouette


def main(argv):
    import render as R
    ep_dir = Path(argv[0]).resolve()
    ep, _ = R.load(ep_dir)
    od = ROOT / "out" / ep_dir.name / "thumbs"
    od.mkdir(parents=True, exist_ok=True)
    for i, sp in enumerate(ep["thumbs"], 1):
        print("썸네일 →", render(sp, od / f"thumb{i}_{sp['template']}.png"))



# ── 3자 대결 (EP011) — 화두 크게 + 세 칸 나란히 ─────────────────────────
def t_versus3(sp):
    """hook: 위 큰 화두(예: '1990년에 1억을 넣었다면') · cols: [{photo, label, value, color, focus}] 3칸 · bottom: 아래 한 줄"""
    f = Image.new("RGBA", (W, H), (8, 10, 18, 255))
    cols = sp["cols"]
    n = len(cols)
    top_h = sp.get("top_h", 330)
    cw = W // n
    for i, c in enumerate(cols):
        x0 = i * cw
        if c.get("photo"):
            im = photo_fill(c["photo"], cw, H - top_h, tuple(c.get("focus", (0.5, 0.5))), c.get("dark", 0.45), 0, 0.5,
                            C(c.get("tint"), (20, 24, 40)), c.get("tint_amt", 0.25))
            f.alpha_composite(im, (x0, top_h))
        # 아래 그라데이션
        import numpy as np
        g = np.clip(np.linspace(-0.2, 1, H - top_h), 0, 1) ** 1.4
        lay = Image.new("RGBA", (cw, H - top_h), (6, 8, 16, 0))
        lay.putalpha(Image.fromarray((np.tile(g[:, None], (1, cw)) * 200).astype("uint8")))
        f.alpha_composite(lay, (x0, top_h))
        cx = x0 + cw / 2
        shadowed(f, fit(c["label"], sp.get("label_size", 104), cw - 60), (cx, top_h + 60), "mt", blur=16)
        shadowed(f, fit(c["value"], sp.get("value_size", 230), cw - 50, color=c.get("color", "yellow")), (cx, H - 120), "mb", blur=18)
        if i:
            ImageDraw.Draw(f).line((x0, top_h, x0, H), fill=(232, 196, 120, 255), width=6)
    # VS 배지
    for i in range(1, n):
        x = i * cw
        b = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
        ImageDraw.Draw(b).ellipse((0, 0, 129, 129), fill=(232, 196, 120, 255))
        vs = T("VS", 58, (16, 18, 28), weight="Black")
        b.alpha_composite(vs, (65 - vs.width // 2, 65 - vs.height // 2 - 4))
        G.blit(f, b, (x, top_h + (H - top_h) * 0.47), 1, "mm")
    # 위 화두 띠
    band = Image.new("RGBA", (W, top_h), (12, 14, 24, 255))
    ImageDraw.Draw(band).line((0, top_h - 4, W, top_h - 4), fill=(232, 196, 120, 255), width=8)
    f.alpha_composite(band, (0, 0))
    hk = fit(sp["hook"], sp.get("hook_size", 190), W - 120, hl=sp.get("hook_hl", ""), hl_color="yellow")
    shadowed(f, hk, (W / 2, top_h / 2 + 6), "mm", blur=16)
    return f


TEMPLATES["versus3"] = t_versus3



# ── 스티커 (사진에서 오린 대상 + 흰 테두리 → 귀여운 스티커) · 말풍선 ─────────
def sticker(png, h, outline=10, rot=0, flip=False):
    im = Image.open(ROOT / "assets" / png).convert("RGBA")
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    pad = outline * 2
    a = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    a.paste(im.getchannel("A"), (pad, pad))
    ring = a.filter(ImageFilter.MaxFilter(outline * 2 + 1)).point(lambda v: 255 if v > 40 else 0)
    out = Image.new("RGBA", a.size, (255, 255, 255, 0))
    out.putalpha(ring)
    white = Image.new("RGBA", a.size, (255, 255, 255, 255))
    out = Image.composite(white, out, ring)
    out.alpha_composite(im, (pad, pad))
    if rot:
        out = out.rotate(rot, expand=True, resample=Image.BICUBIC)
    return out


def bubble(text, size=44, fill=(255, 255, 255), fg=(20, 22, 30)):
    t = T(text, size, fg) if False else G.text_img(text, "Black", size, fg)
    w, h = t.width + 50, t.height + 34
    im = Image.new("RGBA", (w + 10, h + 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, h), radius=h // 2, fill=fill + (255,), outline=(20, 22, 30, 255), width=4)
    d.polygon([(w * 0.3, h - 2), (w * 0.3 + 30, h - 2), (w * 0.3 - 6, h + 30)], fill=fill + (255,), outline=(20, 22, 30, 255))
    d.line((w * 0.3 + 2, h - 3, w * 0.3 + 28, h - 3), fill=fill + (255,), width=6)
    im.alpha_composite(t, (25, 17))
    return im


def place_stickers(f, items):
    for it in items or []:
        if it.get("png"):
            st = sticker(it["png"], it.get("h", 300), it.get("outline", 10), it.get("rot", 0), it.get("flip", False))
            shadowed(f, st, tuple(it["pos"]), it.get("anchor", "mm"), blur=14, off=(8, 12), alpha=0.6)
        elif it.get("bubble"):
            b = bubble(it["bubble"], it.get("size", 44))
            if it.get("rot"):
                b = b.rotate(it["rot"], expand=True, resample=Image.BICUBIC)
            shadowed(f, b, tuple(it["pos"]), it.get("anchor", "mm"), blur=10, off=(6, 8), alpha=0.5)


def t_hook(sp):
    """화두 크게(왼쪽) + 사진 배경 + 모서리 스티커. lines · tag · photo · stickers"""
    f = photo_bg(sp["photo"], "left") if sp.get("photo") else bg_dark(sp.get("glow", (40, 50, 90)))
    place_stickers(f, sp.get("stickers"))
    y = 90
    if sp.get("tag"):
        tg = tag(sp["tag"])
        G.blit(f, tg, (90, y))
        y += tg.height + 30
    lines_block(f, sp["lines"], y, x=80, maxw=sp.get("text_w", 1150), gap=sp.get("gap", -4))
    return f


TEMPLATES["hook"] = t_hook



# ── 인물 인용형 (EP012 벤치마킹): 얼굴 사진 + 따옴표 한 줄 + 등락 배지 ───────────
def t_face_quote(sp):
    """faces: [{photo, focus, name}] 1~2명 오른쪽 · quote(따옴표 문구, 여러 줄, **강조**) 왼쪽 · badge: {label, value, dir:down|up} · tag"""
    f = Image.new("RGBA", (W, H), (10, 12, 20, 255))
    faces = sp.get("faces", [])
    n = len(faces)
    fw = 760 if n == 1 else 520
    x = W - fw * n
    for fc in faces:
        im = photo_fill(fc["photo"], fw, H, tuple(fc.get("focus", (0.5, 0.25))), fc.get("dark", 0.1), 0, fc.get("gray", 0.15))
        f.alpha_composite(im, (x, 0))
        if fc.get("name"):
            nm = G.pill(fc["name"], "Black", 40, (16, 18, 28), (255, 210, 60), pad=(18, 8), radius=10)
            G.blit(f, nm, (x + 30, 40))
        x += fw
    import numpy as np
    # 왼쪽 → 오른쪽 어둡게 전환
    g = np.clip((np.linspace(0, 1, W) - (1 - (fw * n) / W) + 0.18) / 0.3, 0, 1)
    a = (1 - g) * 245
    lay = Image.new("RGBA", (W, H), (10, 12, 20, 0))
    lay.putalpha(Image.fromarray(np.tile(a[None, :], (H, 1)).astype("uint8")))
    f.alpha_composite(lay)
    y = 90
    if sp.get("tag"):
        tg = tag(sp["tag"])
        G.blit(f, tg, (80, y))
        y += tg.height + 34
    from engine.editorial import _hl_text
    q = _hl_text(sp["quote"], sp.get("quote_size", 150), max_w=1200, align="left", line_gap=1.12)
    shadowed(f, q, (70, y), "lt", blur=16)
    b = sp.get("badge")
    if b:
        col = (60, 130, 255) if b.get("dir", "down") == "down" else (240, 70, 70)
        arrow = "▼" if b.get("dir", "down") == "down" else "▲"
        lab = G.text_img(b["label"], "Black", 58, (255, 255, 255))
        val = G.text_img(f"{arrow}{b['value']}", "Black", 82, col)
        bw_, bh_ = lab.width + val.width + 90, max(lab.height, val.height) + 40
        box = Image.new("RGBA", (bw_, bh_), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, bw_ - 1, bh_ - 1), 18, fill=(20, 24, 36, 240), outline=(90, 100, 130, 255), width=3)
        box.alpha_composite(lab, (30, (bh_ - lab.height) // 2))
        box.alpha_composite(val, (60 + lab.width, (bh_ - val.height) // 2))
        shadowed(f, box, (70, H - 70), "lb", blur=14)
    return f


TEMPLATES["face_quote"] = t_face_quote


# ── 회의형 큰 질문 (EP013): 화면 절반 넘게 차지하는 질문 + 거의 방전된 배터리 아이콘 ──────
def battery_icon(w=520, h=260, pct=0.04, color=(240, 60, 60), label="", label_size=110, frost=False):
    """가로 배터리 아이콘(특정 제품 아님). pct = 남은 칸 비율"""
    k = 2
    W2, H2 = w * k, h * k
    im = Image.new("RGBA", (W2 + 60 * k, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = 18 * k
    body = (lw // 2, lw // 2, W2 - lw // 2, H2 - lw // 2)
    d.rounded_rectangle(body, radius=40 * k, fill=(16, 18, 26, 235), outline=(235, 238, 245, 255), width=lw)
    d.rounded_rectangle((W2 + 6 * k, H2 * 0.32, W2 + 46 * k, H2 * 0.68), radius=10 * k, fill=(235, 238, 245, 255))
    inner = (lw * 2, lw * 2, W2 - lw * 2, H2 - lw * 2)
    fw = max(int((inner[2] - inner[0]) * pct), 22 * k)
    d.rounded_rectangle((inner[0], inner[1], inner[0] + fw, inner[3]), radius=18 * k, fill=color + (255,))
    if frost:  # 얼음 낀 느낌: 위쪽 흰 결정
        for i in range(14):
            x = inner[0] + (inner[2] - inner[0]) * (i + 0.5) / 14
            d.polygon([(x - 26 * k, inner[1]), (x + 26 * k, inner[1]), (x, inner[1] + (40 + (i * 37) % 50) * k)], fill=(200, 230, 255, 200))
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    if label:
        t = G.text_img(label, "Black", label_size, color, stroke=8, stroke_fill=(0, 0, 0))
        G.blit(im, t, (w * 0.58, h / 2), 1, "mm")
    return im


def t_bold_q(sp):
    """lines(큰 질문, 왼쪽) · bg: dark|photo · battery: {pct, label, frost, x, y, rot, scale} · chip: {x, y, size, label}
    stamp: {text, x, y, rot, color} · tag · split: true면 왼쪽 따뜻(AI) / 오른쪽 차갑게(배터리)"""
    if sp.get("photo"):
        f = photo_bg(sp["photo"], "left")
    elif sp.get("split"):
        f = bg_split(left=tuple(sp.get("left_glow", (20, 90, 60))), right=tuple(sp.get("right_glow", (30, 70, 140))))
    else:
        f = bg_dark(sp.get("glow", (40, 60, 120)), (0.75, 0.55))
    ch = sp.get("chip")
    if ch:
        ic = chip_icon(ch.get("size", 300), tuple(ch.get("glow", (90, 230, 160))))
        f.alpha_composite(rim(ic, tuple(ch.get("glow", (90, 230, 160))), 30), (ch["x"] - 90, ch["y"] - 90))
        G.blit(f, ic, (ch["x"], ch["y"]))
        if ch.get("label"):
            t = G.text_img(ch["label"], "Black", ch.get("label_size", 110), (255, 255, 255), stroke=8, stroke_fill=(0, 0, 0))
            G.blit(f, t, (ch["x"] + ic.width / 2, ch["y"] + ic.height / 2), 1, "mm")
    b = sp.get("battery")
    if b:
        bi = battery_icon(int(520 * b.get("scale", 1)), int(260 * b.get("scale", 1)), b.get("pct", 0.04),
                          tuple(b.get("color", (240, 60, 60))), b.get("label", ""), b.get("label_size", 110), b.get("frost", False))
        if b.get("rot"):
            bi = bi.rotate(b["rot"], expand=True, resample=Image.BICUBIC)
        f.alpha_composite(rim(bi, tuple(b.get("rim", (240, 60, 60))), 34), (b["x"] - 100, b["y"] - 100))
        G.blit(f, bi, (b["x"], b["y"]))
    y = sp.get("y", 80)
    if sp.get("tag"):
        tg = tag(sp["tag"], size=sp.get("tag_size", 52))
        G.blit(f, tg, (sp.get("x", 80), y))
        y += tg.height + 24
    lines_block(f, sp["lines"], y, x=sp.get("x", 80), maxw=sp.get("text_w", 1200), gap=sp.get("gap", -14))
    for st in ([sp["stamp"]] if sp.get("stamp") else []) + sp.get("stamps", []):
        col = C(st.get("color", "red"))
        t = G.text_img(st["text"], "Black", st.get("size", 120), C(st.get("fg", "white")))
        sub = G.text_img(st["sub"], "Black", st.get("sub_size", 54), C(st.get("fg", "white"))) if st.get("sub") else None
        pad = 34
        bw = max(t.width, sub.width if sub else 0) + pad * 2
        bh = t.height + pad + (sub.height + 6 if sub else 0)
        box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, bw - 1, bh - 1), 20, fill=col + (255,), outline=(255, 255, 255, 255), width=8)
        box.alpha_composite(t, ((bw - t.width) // 2, pad // 2))
        if sub:
            box.alpha_composite(sub, ((bw - sub.width) // 2, pad // 2 + t.height + 2))
        box = box.rotate(st.get("rot", -8), expand=True, resample=Image.BICUBIC)
        shadowed(f, box, (st["x"], st["y"]), "mm", blur=16)
    return f


TEMPLATES["bold_q"] = t_bold_q


if __name__ == "__main__":
    main(sys.argv[1:])
