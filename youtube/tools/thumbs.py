"""썸네일 템플릿 모음 (클릭 유도형). 1920x1080으로 그려 1280x720으로 저장.

  python tools/thumbs.py episodes/ep004_templeton_vix          # episode.yaml 의 thumbs: 목록 전부
  python tools/thumbs.py --gallery                              # 템플릿 견본 한 장씩 (out/thumb_gallery/)

템플릿 (template: 이름)
  quote_bottom  위 "따옴표 인용" + 가운데 소품(주문 화면·돈다발·상승 화살표) + 아래 초대형 2줄 문구   (예: 월 200씩 받으려면 / 매달 '이만큼' 사두세요)
  transform     강렬한 집중선 배경 + 아이콘 A → 큰 화살표 → 아이콘 B + 아래 흰/노랑 2줄           (예: 클로드 MCP 미쳤다…! / 쇼핑쇼츠 100% 자동화)
  minimal       검정 배경 + 노란 헤드라인 + 흰 서브 + 가운데 오브젝트 하나                         (예: 바이브 코딩 1인 창업 / 3시간 통합본)
  split_vs      좌우 반반 색 + 위 라벨 + 가운데 VS + 아래 흰/노랑 결론 문구                        (예: 무겁게 8번 VS 가볍게 25번 / 석 달 뒤 팔 굵기)
  question      "~였다는데" + 초대형 "진짜일까?" + 큰 물음표                                       (호기심형)
  big_number    큰 숫자 + 강조 문구 + 차트                                                           (기존 대표형)
  vs_numbers    큰 숫자 대비 (기존 thumbnails_vs)

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
def t_quote_bottom(sp):
    f = bg_dark(sp.get("glow", (120, 40, 20)), (0.5, 0.35))
    place_props(f, sp.get("props"))
    if sp.get("quote"):
        q = fit(f"\"{sp['quote']}\"", sp.get("quote_size", 120), 1700, color=sp.get("quote_color", "white"),
                hl=sp.get("quote_hl", ""), hl_color=sp.get("quote_hl_color", "yellow"))
        shadowed(f, q, (W / 2, 22), "mt")
    y = H - 30
    ims = []
    for ln in reversed(sp["bottom"]):
        im = fit(ln["text"], ln.get("size", 190), 1860, color=ln.get("color", "white"), hl=ln.get("hl", ""),
                 hl_color=ln.get("hl_color", "red"))
        ims.append((im, y))
        y -= im.height - 20
    for im, yy in ims:
        shadowed(f, im, (W / 2, yy), "mb")
    return f


def t_transform(sp):
    f = bg_burst(C(sp.get("c1"), (255, 70, 50)), C(sp.get("c2"), (210, 10, 30)))
    a = icon_box(prop(sp["left"]) if isinstance(sp["left"], dict) else sp["left"], 440, sp.get("left_bg", (232, 120, 80)),
                 label=sp.get("left_label"))
    b = icon_box(prop(sp["right"]) if isinstance(sp["right"], dict) else sp["right"], 440, sp.get("right_bg", "white"),
                 label=sp.get("right_label"))
    shadowed(f, a, (330, 400), "mm", blur=24, alpha=0.5)
    shadowed(f, b, (W - 330, 400), "mm", blur=24, alpha=0.5)
    G.blit(f, big_arrow(520, 360), (W / 2, 400), 1, "mm")
    if sp.get("top"):
        t = fit(sp["top"], 64, 1500, color="white", hl=sp.get("top_hl", ""), hl_color="yellow")
        shadowed(f, t, (W / 2, 40), "mt")
    lines_block(f, sp["bottom"], sp.get("bottom_y", 660), maxw=1860)
    return f


def t_minimal(sp):
    f = Image.new("RGBA", (W, H), (6, 6, 8, 255))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((W / 2 - 500, 520, W / 2 + 500, 1200), fill=(255, 255, 255, 28))
    f.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
    place_props(f, sp.get("props"))
    lines_block(f, sp["lines"], 70, maxw=1800, gap=10)
    return f


def t_split_vs(sp):
    f = bg_split(C(sp.get("left_color"), (150, 30, 30)), C(sp.get("right_color"), (20, 110, 110)))
    for side, x in (("left", W * 0.25), ("right", W * 0.75)):
        c = sp[side]
        for p in c.get("props", []):
            p = dict(p)
            p.setdefault("pos", (x, 520))
            place_props(f, [p])
        lab = fit(c["label"], c.get("size", 96), 900, color="white", hl=c.get("hl", ""), hl_color=c.get("hl_color", "red"))
        shadowed(f, lab, (x, 50), "mt")
        if c.get("value"):
            shadowed(f, fit(c["value"], c.get("value_size", 200), 880, color=c.get("value_color", "white")), (x, 60 + lab.height + 10), "mt")
    vs = T("VS", 200, "white")
    shadowed(f, vs, (W / 2, 500), "mm")
    lines_block(f, sp["bottom"], sp.get("bottom_y", 770), maxw=1860)
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
        shadowed(f, fit(c["value"], 260, 880, color=c.get("color", "red")), (x, 560), "mm")
        if c.get("sub"):
            shadowed(f, fit(c["sub"], 64, 860), (x, 760), "mt")
    shadowed(f, T("VS", 150, "yellow"), (W / 2, 560), "mm")
    return f


TEMPLATES = {"quote_bottom": t_quote_bottom, "transform": t_transform, "minimal": t_minimal, "split_vs": t_split_vs,
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
