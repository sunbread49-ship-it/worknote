"""에디토리얼(다큐·PPT형) 장면 — 배경 위에 큼직한 인포그래픽.
참고한 '느낌': 어둡게 깐 배경 + 흰 굵은 제목 + 노란 강조 + 깔끔한 도형(막대·타임라인·아이콘·정보 박스).
배경은 사진 대신 실제 데이터 차트·질감으로 직접 그린다(저작권 문제 없음).

공통 spec
  bg: {kind: chart, series, start, end, color, log} | {kind: grain, tone: navy|ink|rust|olive|plum} | {kind: calendar}
  kicker: 제목 위 작은 노란 글씨 · title: 큰 흰 제목 · highlight: 제목 안 노란 부분
  credit: 오른쪽 아래 자료 출처
타입
  infobox   오른쪽 정보 박스(큰 숫자+단위), 왼쪽은 배경 강조 문구
  knockout  배경 그림으로 채운 거대한 단어 (예: SELL IN MAY)
  timeline  눈금 타임라인 + 구간 강조 + 끝 태그
  grid      칸(연도 등) N개 중 K개 색칠 + 진행 막대
  hbars     가로 막대 비교 (짧은 것 → 긴 것)
  profile   곡선 프로필, 일부 구간만 노랗게 채우기
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from . import draw as G
from . import style as S

Y = (255, 204, 40)          # 강조 노랑
INK = (18, 20, 28)
TONES = {"navy": (22, 34, 64), "ink": (20, 22, 28), "rust": (176, 84, 36), "olive": (60, 64, 40), "plum": (52, 30, 60)}


def _col(c, default=S.FG):
    from .scenes import col
    if c in ("yellow", "y"):
        return Y
    return col(c, default)


# ── 배경 ────────────────────────────────────────────────────────
def _grain(w, h, seed=1, amt=18):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, (h // 2, w // 2)).astype(np.float32)
    n = np.array(Image.fromarray(n).resize((w, h), Image.BILINEAR))
    return n


def _vignette(w, h, strength=0.55):
    y, x = np.ogrid[-1:1:h * 1j, -1:1:w * 1j]
    r = np.sqrt(x * x * 0.8 + y * y)
    return np.clip(1 - strength * (r ** 2) / 1.6, 0.25, 1)[..., None]


def _chart_layer(sp, w, h):
    from . import data as D
    s = D.series(sp["series"], sp.get("start"), sp.get("end")).dropna()
    v = np.log(s.values) if sp.get("log") else s.values
    xs = np.linspace(-0.02 * w, 1.02 * w, len(v))
    lo, hi = v.min(), v.max()
    ys = h * 0.88 - (v - lo) / (hi - lo + 1e-9) * h * 0.62
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(x * k, y * k) for x, y in zip(xs, ys)]
    c = tuple(sp.get("color", (240, 84, 84)))
    d.polygon(pts + [(w * k, h * k), (0, h * k)], fill=c + (90,))
    d.line(pts, fill=c + (255,), width=6 * k)
    return im.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=24)
def _backdrop_cached(key):
    import json
    sp = json.loads(key)
    w, h = S.W, S.H
    kind = sp.get("kind", "grain")
    base = np.array(TONES.get(sp.get("tone", "ink"), TONES["ink"]), np.float32)
    arr = np.ones((h, w, 3), np.float32) * base
    # 은은한 대각 그라데이션
    gy = np.linspace(1.15, 0.75, h)[:, None, None]
    arr = arr * gy
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    bright = None
    if kind == "chart":
        layer = _chart_layer(sp, w, h)
        bright = Image.new("RGBA", (w, h), (30, 30, 36, 255))
        bright.alpha_composite(layer)
        im.alpha_composite(G.with_opacity(layer.filter(ImageFilter.GaussianBlur(sp.get("blur", 2))), sp.get("op", 0.45)))
    elif kind == "calendar":
        cal = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(cal)
        f = S.font("Black", 150)
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        for i, m in enumerate(months):
            x, y = 60 + (i % 4) * 470, 90 + (i // 4) * 330
            hl = m in sp.get("hl", [])
            d.text((x, y), m, font=f, fill=(255, 204, 40, 34) if hl else (255, 255, 255, 12))
        im.alpha_composite(cal.filter(ImageFilter.GaussianBlur(1.5)))
    a = np.array(im.convert("RGB"), np.float32)
    a = a * _vignette(w, h, sp.get("vignette", 0.55)) + _grain(w, h, amt=sp.get("grain", 10))[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return out, bright


def backdrop(sp):
    import json
    return _backdrop_cached(json.dumps(sp or {"kind": "grain"}, sort_keys=True, ensure_ascii=False))


# ── 공통 그리기 도구 ────────────────────────────────────────────
def T(text, size, color=S.FG, weight="Black", **kw):
    return G.text_img(text, weight, size, color, **kw)


def shadow(f, im, xy, anchor="lt", op=1.0, blur=10, alpha=0.6):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").point(lambda a: a * alpha))
    G.blit(f, sh.filter(ImageFilter.GaussianBlur(blur)), (xy[0] + 3, xy[1] + 6), op, anchor)
    G.blit(f, im, xy, op, anchor)


def header(f, sp, t, t0, y=210, center=True):
    """kicker(노랑, 작게) + title(흰, 크게, 부분 노랑)"""
    x = S.W / 2 if center else 200
    anc = "mt" if center else "lt"
    yy = y
    if sp.get("kicker"):
        k = T(sp["kicker"], 40, Y, "ExtraBold")
        shadow(f, k, (x, yy), anc, G.appear(t, t0, 0.3))
        yy += k.height + 6
    if sp.get("title"):
        tt = T(sp["title"], sp.get("title_size", 84), S.FG, "Black", highlight=sp.get("highlight", ""), hl_fill=Y,
               align="center" if center else "left", line_gap=1.15)
        k = G.ease_out((t - t0 - 0.05) / 0.35)
        shadow(f, tt, (x, yy + (1 - k) * 24), anc, k)
        yy += tt.height
    return yy


def credit(f, sp):
    if sp.get("credit"):
        G.blit(f, T(sp["credit"], 20, (200, 204, 214), "SemiBold"), (S.W - S.SAFE_X + 40, 128), 0.75, "rt")


def counter(text, k):
    """'+46.9%' 같은 숫자를 k(0~1) 만큼 세어 올라가는 문자열로"""
    import re
    m = re.search(r"[-+]?\d[\d,]*\.?\d*", text)
    if not m or k >= 1:
        return text
    raw = m.group(0)
    sign = raw[0] if raw[0] in "+-" else ""
    num = float(raw.lstrip("+-").replace(",", ""))
    dec = len(raw.split(".")[1]) if "." in raw else 0
    v = num * G.ease_out(k)
    s = f"{v:,.{dec}f}" if "," in raw else f"{v:.{dec}f}"
    return text[:m.start()] + sign + s + text[m.end():]


# ── 장면들 ──────────────────────────────────────────────────────
from .scenes import Scene  # noqa: E402


class Editorial(Scene):
    default_transition = "cut"

    def base(self, f):
        bd, _ = backdrop(self.spec.get("bg"))
        f.paste(bd, (0, 0))

    def finish(self, f, t):
        credit(f, self.spec)
        self.draw_common(f, t)


class InfoBox(Editorial):
    """왼쪽: 큰 문구(배경 위) / 오른쪽: 노란 띠 정보 박스 (kicker · value+unit · sub)"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        t0 = self.line_start(sp.get("on", 1))
        if sp.get("title"):
            header(f, sp, t, 0.0, y=sp.get("title_y", 300), center=False)
        bw, bh = sp.get("box_w", 620), 360
        x0, y0 = sp.get("box_x", 1180), sp.get("box_y", 420)
        k = G.ease_out((t - t0) / 0.4)
        if k <= 0:
            return self.finish(f, t)
        box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rectangle((14, 14, bw - 1, bh - 1), fill=(10, 10, 14, 120))          # 그림자 판
        d.rectangle((0, 0, bw - 14, bh - 14), fill=INK + (245,))
        d.rectangle((0, 0, bw - 14, 7), fill=Y + (255,))
        y = 44
        if sp.get("box_kicker"):
            kk = T(sp["box_kicker"], 34, Y, "ExtraBold")
            box.alpha_composite(kk, (44, y))
            y += kk.height + 4
        val = counter(sp["value"], (t - t0) / 0.9)
        v = T(val, sp.get("value_size", 150), S.FG, "Black")
        box.alpha_composite(v, (40, y))
        if sp.get("unit"):
            u = T(sp["unit"], 70, S.FG, "Black")
            box.alpha_composite(u, (48 + v.width, y + v.height - u.height - 18))
        y += v.height
        if sp.get("box_sub"):
            ss = T(sp["box_sub"], 38, Y, "ExtraBold")
            box.alpha_composite(ss, (44, y + 2))
        G.blit(f, box, (x0 + (1 - k) * 80, y0), k)
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec.get("on", 1)), "pop", 0.4)]


class Knockout(Editorial):
    """배경 그림으로 채운 거대한 단어 + 아래 작은 설명"""

    def draw(self, f, t):
        sp = self.spec
        bd, bright = backdrop(sp.get("bg"))
        f.paste(bd, (0, 0))
        fill = _paper(sp.get("fill_tone", "gold")).copy()
        if bright is not None:  # 글자 안에 실제 차트가 비치도록
            lay = _chart_layer({**sp["bg"], "color": sp.get("fill_line", (120, 40, 20))}, S.W, S.H)
            fill.alpha_composite(G.with_opacity(lay, 0.8))
        fill = ImageEnhance.Brightness(fill.convert("RGB")).enhance(sp.get("fill_bright", 1.0)).convert("RGBA")
        word = sp["word"]
        size = sp.get("size", 300)
        m = T(word, size, (255, 255, 255), "Black")
        while m.width > S.W - 200 and size > 80:
            size -= 10
            m = T(word, size, (255, 255, 255), "Black")
        k = G.ease_out(t / 0.6)
        sc = 1.08 - 0.08 * k
        mw, mh = int(m.width * sc), int(m.height * sc)
        m2 = m.resize((mw, mh), Image.BICUBIC)
        x, y = (S.W - mw) // 2, int(S.H * 0.42 - mh / 2)
        cut = fill.crop((x, y, x + mw, y + mh))
        cut.putalpha(m2.getchannel("A"))
        sh = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
        sh.putalpha(m2.getchannel("A").point(lambda a: a * 0.7))
        G.blit(f, sh.filter(ImageFilter.GaussianBlur(14)), (x + 6, y + 12), k)
        G.blit(f, cut, (x, y), k)
        if sp.get("sub"):
            o = G.appear(t, self.line_start(sp.get("sub_on", 1)) + 0.4, 0.4)
            s = T(sp["sub"], 52, S.FG, "ExtraBold", highlight=sp.get("highlight", ""), hl_fill=Y)
            shadow(f, s, (S.W / 2, y + mh + 40), "mt", o)
        self.finish(f, t)

    def extra_sfx(self):
        return [(0.05, "boom", 0.35)]


@lru_cache(maxsize=4)
def _paper(tone):
    w, h = S.W, S.H
    base = {"gold": (230, 180, 70), "blue": (80, 140, 230), "red": (220, 80, 80)}.get(tone, (230, 180, 70))
    a = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    a += _grain(w, h, seed=7, amt=16)[..., None]
    a += (_grain(w // 4, h // 4, seed=9, amt=22).repeat(4, 0).repeat(4, 1)[:h, :w])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


class Timeline(Editorial):
    """ticks: [{label, sub}] · band: [i0, i1, label, color] · marker_to: 인덱스 · tag: {text, at, color} · bottom"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        header(f, sp, t, 0.0, y=sp.get("title_y", 200))
        ticks = sp["ticks"]
        x0, x1, yl = 300, S.W - 300, sp.get("line_y", 600)
        n = len(ticks)
        xs = [x0 + (x1 - x0) * i / max(1, n - 1) for i in range(n)]
        d = ImageDraw.Draw(f)
        kl = G.ease_out(t / 0.6)
        d.line((x0, yl, x0 + (x1 - x0) * kl, yl), fill=(255, 255, 255, 235), width=5)
        for i, (x, tk) in enumerate(zip(xs, ticks)):
            o = G.appear(t, 0.1 + i * 0.06, 0.2)
            if o <= 0:
                continue
            d.line((x, yl - 18, x, yl + 18), fill=(255, 255, 255, int(235 * o)), width=5)
            hl = tk.get("hl")
            lab = T(tk["label"], 38, Y if hl else S.FG, "ExtraBold")
            G.blit(f, lab, (x, yl + 34), o, "mt")
            if tk.get("sub"):
                G.blit(f, T(tk["sub"], 26, (190, 196, 210), "SemiBold"), (x, yl + 34 + lab.height + 4), o, "mt")
        for b in sp.get("bands", []):
            i0, i1 = b["from"], b["to"]
            tb = self.line_start(b.get("on", 1))
            kb = G.ease_out((t - tb) / 0.6)
            if kb <= 0:
                continue
            c = _col(b.get("color"), Y)
            bx0, bx1 = xs[i0], xs[i0] + (xs[i1] - xs[i0]) * kb
            band = Image.new("RGBA", (max(2, int(bx1 - bx0)), 22), c + (235,))
            G.blit(f, band, (bx0, yl - 11))
            if b.get("label"):
                lb = G.pill(b["label"], "ExtraBold", 32, INK if c == Y else S.FG, c, pad=(20, 8))
                G.blit(f, lb, ((xs[i0] + xs[i1]) / 2, yl - 40), min(1, kb * 1.5), "mb")
        tg = sp.get("tag")
        if tg:
            o = G.appear(t, self.line_start(tg.get("on", 1)) + 0.2, 0.3)
            c = _col(tg.get("color"), S.UP)
            p = G.pill(tg["text"], "ExtraBold", 36, S.FG, c, pad=(26, 12), radius=4)
            G.blit(f, p, (xs[tg.get("at", n - 1)], yl - 100), o, "mb")
        if sp.get("bottom"):
            o = G.appear(t, self.line_start(sp.get("bottom_on", 1)) + 0.3, 0.35)
            b = T(sp["bottom"], 64, S.FG, "Black", highlight=sp.get("bottom_hl", ""), hl_fill=Y)
            shadow(f, b, (S.W / 2, yl + 190), "mt", o)
        self.finish(f, t)


class Grid(Editorial):
    """n칸 중 k칸 강조 (예: 76년 중 58년). cols, labels(선택), headline, bar: {value, max, label}"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        yy = header(f, sp, t, 0.0, y=sp.get("title_y", 170))
        n, cols = sp["n"], sp.get("cols", 19)
        hits = sp.get("hits")  # 강조할 칸 인덱스(없으면 앞에서부터 k개)
        hit = set(hits) if hits is not None else set(range(sp["k"]))
        cell = sp.get("cell", 56)
        gap = 10
        rows = (n + cols - 1) // cols
        gw = cols * cell + (cols - 1) * gap
        gx, gy = (S.W - gw) / 2, yy + 50
        t0 = self.line_start(sp.get("on", 1))
        person = sp.get("icon") == "person"
        for i in range(n):
            r, c = divmod(i, cols)
            o = G.appear(t, t0 + i * sp.get("step", 0.02), 0.15)
            if o <= 0:
                continue
            on = i in hit and t >= t0 + sp.get("hl_delay", 0.6) + i * sp.get("step", 0.02)
            colr = _col(sp.get("hit_color"), Y) if on else (90, 94, 108)
            im = _person(cell, colr) if person else _cell(cell, colr, sp.get("labels", [None] * n)[i])
            G.blit(f, im, (gx + c * (cell + gap), gy + r * (cell + gap)), o)
        yb = gy + rows * (cell + gap) + 40
        if sp.get("headline"):
            o = G.appear(t, self.line_start(sp.get("headline_on", 1)) + 0.4, 0.35)
            h = T(sp["headline"], 68, S.FG, "Black", highlight=sp.get("headline_hl", ""), hl_fill=Y)
            shadow(f, h, (S.W / 2, yb), "mt", o)
        self.finish(f, t)


def _cell(s, c, label=None):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, s - 1, s - 1), radius=8, fill=c + (255,))
    if label:
        tx = T(str(label), int(s * 0.36), INK if c == Y else (230, 232, 240), "Bold")
        im.alpha_composite(tx, ((s - tx.width) // 2, (s - tx.height) // 2))
    return im


def _person(s, c):
    k = 3
    im = Image.new("RGBA", (s * k, int(s * 1.25) * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W = s * k
    d.ellipse((W * 0.27, 0, W * 0.73, W * 0.46), fill=c + (255,))
    d.rounded_rectangle((W * 0.08, W * 0.52, W * 0.92, W * 1.25), radius=int(W * 0.3), fill=c + (255,))
    return im.resize((s, int(s * 1.25)), Image.LANCZOS)


class HBars(Editorial):
    """rows: [{label, value(숫자), text(표시), hl, on}] — 짧은 것부터 긴 것까지 가로 막대"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        yy = header(f, sp, t, 0.0, y=sp.get("title_y", 200))
        rows = sp["rows"]
        vmax = sp.get("vmax") or max(abs(r["value"]) for r in rows)
        x0, wmax = 300, S.W - 600
        y = yy + 70
        for r in rows:
            t0 = self.line_start(r.get("on", 1)) + r.get("offset", 0)
            k = G.ease_out((t - t0) / 0.7)
            hl = r.get("hl")
            c = _col(r.get("color"), Y if hl else (200, 204, 214))
            lab = T(r["label"], 36, Y if hl else (230, 200, 120), "ExtraBold")
            G.blit(f, lab, (x0, y), min(1, k * 2) if k > 0 else 0)
            y += lab.height + 10
            bw = max(8, int(wmax * abs(r["value"]) / vmax * k))
            if k > 0:
                G.blit(f, Image.new("RGBA", (bw, 58), c + (255,)), (x0, y))
                txt = T(counter(r.get("text", str(r["value"])), (t - t0) / 0.7), 64, Y if hl else S.FG, "Black")
                if bw + txt.width + 30 < wmax + 220:
                    shadow(f, txt, (x0 + bw + 24, y + 29), "lm", min(1, k * 2))
                else:
                    shadow(f, txt, (x0 + bw, y - 8), "rb", min(1, k * 2))
            y += 58 + 40
        self.finish(f, t)


class Profile(Editorial):
    """values: 곡선 점들, labels: x축 라벨(같은 개수 또는 양끝), hl: [i0, i1] 노랗게 채울 구간, marker: 인덱스"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        header(f, sp, t, 0.0, y=sp.get("title_y", 200))
        v = np.array(sp["values"], float)
        n = len(v)
        x0, x1, base, hh = 280, S.W - 280, 820, sp.get("height", 300)
        xs = np.linspace(x0, x1, n)
        lo, hi = min(v.min(), 0) if sp.get("zero") else v.min(), v.max()
        ys = base - (v - lo) / (hi - lo + 1e-9) * hh
        # 부드럽게: 점 사이 보간
        fx = np.linspace(x0, x1, (n - 1) * 24 + 1)
        fy = np.interp(fx, xs, ys)
        k = 3
        lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        kd = G.ease_out(t / 1.0)
        m = max(2, int(len(fx) * kd))
        d.line([(x * k, y * k) for x, y in zip(fx[:m], fy[:m])], fill=(200, 204, 214, 230), width=4 * k)
        d.line((x0 * k, base * k, x1 * k, base * k), fill=(255, 255, 255, 220), width=3 * k)
        if sp.get("hl"):
            i0, i1 = sp["hl"]
            th = self.line_start(sp.get("hl_on", 1))
            kh = G.ease_out((t - th) / 0.9)
            if kh > 0:
                a, b = xs[i0], xs[i0] + (xs[i1] - xs[i0]) * kh
                sel = (fx >= a) & (fx <= b)
                pts = [(x * k, y * k) for x, y in zip(fx[sel], fy[sel])]
                if len(pts) > 1:
                    d.polygon(pts + [(pts[-1][0], base * k), (pts[0][0], base * k)], fill=Y + (150,))
                    d.line(pts, fill=Y + (255,), width=6 * k)
                    ex, ey = pts[-1]
                    r = 14 * k
                    d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=Y + (255,))
                    d.ellipse((ex - 2.2 * r, ey - 2.2 * r, ex + 2.2 * r, ey + 2.2 * r), outline=Y + (200,), width=3 * k)
        f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
        labels = sp.get("labels", [])
        for i, lab in enumerate(labels):
            if not lab:
                continue
            hl = sp.get("hl") and sp["hl"][0] <= i <= sp["hl"][1]
            G.blit(f, T(lab, 32, Y if hl else S.FG, "ExtraBold"), (xs[i], base + 22), kd, "mt")
        for c in sp.get("pins", []):
            o = G.appear(t, self.line_start(c.get("on", 1)) + 0.3, 0.3)
            p = G.pill(c["text"], "ExtraBold", 34, INK, Y, pad=(20, 8), radius=4)
            G.blit(f, p, (xs[c["at"]], ys[c["at"]] - 40), o, "mb")
        self.finish(f, t)


TYPES = {"infobox": InfoBox, "knockout": Knockout, "timeline": Timeline, "grid": Grid, "hbars": HBars, "profile": Profile}


# ── 포스터형: 컬러 배경 + 무늬 띠 + 실제 차트로 만든 검은 '산' 실루엣 ─────────
POSTER = {"rust": ((214, 112, 52), (176, 78, 30)), "teal": ((40, 150, 150), (18, 96, 104)),
          "mustard": ((232, 178, 52), (196, 132, 24)), "navy": ((52, 86, 160), (26, 46, 100)),
          "plum": ((150, 70, 120), (96, 36, 80)), "sage": ((128, 160, 110), (80, 112, 70))}


@lru_cache(maxsize=8)
def _poster_bg(tone):
    w, h = S.W, S.H
    c1, c2 = POSTER.get(tone, POSTER["rust"])
    y, x = np.ogrid[-1:1:h * 1j, -1:1:w * 1j]
    r = np.clip(np.sqrt(x * x * 0.6 + (y + 0.1) ** 2) / 1.3, 0, 1)[..., None]
    a = np.array(c1, np.float32) * (1 - r) + np.array(c2, np.float32) * r
    a += _grain(w, h, seed=11, amt=7)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(maxsize=4)
def _band(color=(26, 20, 18), w=S.W):
    """무늬 띠: 작은 캔들(양봉·음봉) 반복 — 주식 채널 고유 패턴"""
    k = 2
    h = 44
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((0, 3 * k, w * k, 3 * k), fill=color + (255,), width=3 * k)
    d.line((0, (h - 4) * k, w * k, (h - 4) * k), fill=color + (255,), width=3 * k)
    x, i = 14, 0
    pat = [(10, 30), (16, 26), (8, 22), (14, 34), (12, 24), (18, 30)]
    while x < w:
        t, b = pat[i % len(pat)]
        cx = x * k
        d.line((cx, (t - 4) * k, cx, (b + 4) * k), fill=color + (255,), width=2 * k)
        if i % 2 == 0:
            d.rectangle((cx - 5 * k, t * k, cx + 5 * k, b * k), fill=color + (255,))
        else:
            d.rectangle((cx - 5 * k, t * k, cx + 5 * k, b * k), outline=color + (255,), width=2 * k)
        x += 28
        i += 1
    return im.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=16)
def silhouette(name, h, color=(26, 20, 18)):
    """Fluent 3D 이모지 → 단색 실루엣"""
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "assets/emoji" / f"{name}.png"
    im = Image.open(p).convert("RGBA")
    im = im.crop(im.getbbox())
    a = im.getchannel("A").resize((int(im.width * h / im.height), h), Image.LANCZOS)
    a = a.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 110 else int(v * 2.3 * (v > 40)))
    out = Image.new("RGBA", a.size, color + (255,))
    out.putalpha(a)
    return out


class Poster(Editorial):
    """tone, kicker, title(검은 글씨, highlight 흰색), ridge: {series, start, end, log} 실루엣,
    pin: {at(0~1), label, on}, figure: {name, at(0~1), size, on}"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(_poster_bg(sp.get("tone", "rust")), (0, 0))
        dark = (26, 20, 18)
        band = _band(dark)
        G.blit(f, band, (0, 200), 0.95)
        G.blit(f, band, (0, 860), 0.95)
        y = 268
        if sp.get("kicker"):
            k = T(sp["kicker"], 40, dark, "ExtraBold")
            G.blit(f, k, (S.W / 2, y), G.appear(t, 0.0, 0.3), "mt")
            y += k.height + 4
        if sp.get("title"):
            tt = T(sp["title"], 76, dark, "Black", highlight=sp.get("highlight", ""), hl_fill=(255, 255, 255), align="center")
            kk = G.ease_out(t / 0.4)
            G.blit(f, tt, (S.W / 2, y + (1 - kk) * 20), kk, "mt")
        # 능선: 실제 지수 흐름을 평평한 '산'으로
        rg = sp.get("ridge")
        x0, x1, base = 140, S.W - 140, 845
        if rg:
            from . import data as D
            s = D.series(rg["series"], rg.get("start"), rg.get("end")).dropna()
            v = np.log(s.values) if rg.get("log") else s.values
            n = 220
            v = np.interp(np.linspace(0, len(v) - 1, n), np.arange(len(v)), v)
            v = np.convolve(np.pad(v, 2, mode="edge"), np.ones(5) / 5, mode="valid")
            lo, hi = v.min(), v.max()
            hh = rg.get("height", 250)
            xs = np.linspace(x0, x1, n)
            nv = (v - lo) / (hi - lo + 1e-9)
            nv = 0.12 + 0.88 * nv                       # 낮은 곳도 살짝 언덕으로
            taper = np.clip(np.minimum(np.linspace(0, 1, n), np.linspace(1, 0, n)) / 0.07, 0, 1) ** 0.7
            ys = base - 14 - nv * taper * hh
            kd = G.ease_out((t - 0.15) / 0.9)
            m = max(2, int(n * kd))
            k = 2
            lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            pts = [(x * k, y * k) for x, y in zip(xs[:m], ys[:m])]
            d.polygon(pts + [(xs[m - 1] * k, base * k), (x0 * k, base * k)], fill=dark + (255,))
            d.rectangle((x0 * k, (base - 14) * k, xs[m - 1] * k, base * k), fill=dark + (255,))
            f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
            self._ridge = (xs, ys)
        pin = sp.get("pin")
        if pin and rg:
            o = G.appear(t, self.line_start(pin.get("on", 1)) + 0.3, 0.3)
            xs, ys = self._ridge
            i = int(pin.get("at", 0.3) * (len(xs) - 1))
            px, top = xs[i], max(ys[i] - 120, 470)
            d = ImageDraw.Draw(f)
            if o > 0:
                for yy in range(int(top + 40), int(ys[i]), 14):
                    d.line((px, yy, px, yy + 7), fill=dark + (int(255 * o),), width=3)
                lb = G.pill(pin["label"], "ExtraBold", 34, (255, 255, 255), dark, pad=(18, 8), radius=2)
                G.blit(f, lb, (px, top + 34), o, "mb")
        fg = sp.get("figure")
        if fg and rg:
            o = G.appear(t, self.line_start(fg.get("on", 1)) + 0.2, 0.4)
            xs, ys = self._ridge
            i = int(fg.get("at", 0.7) * (len(xs) - 1))
            im = silhouette(fg["name"], int(min(fg.get("size", 150), ys[i] + 8 - 440)), dark)
            if fg.get("flip"):
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            G.blit(f, im, (xs[i], ys[i] + 8 + (1 - o) * 30), o, "mb")
        self.finish(f, t)


# ── 지도: 미국 주 / 세계 ─────────────────────────────────────────
def _albers(lon, lat, lon0=-96, lat0=37.5, p1=29.5, p2=45.5):
    import math
    r = math.radians
    n = (math.sin(r(p1)) + math.sin(r(p2))) / 2
    C = math.cos(r(p1)) ** 2 + 2 * n * math.sin(r(p1))
    rho0 = math.sqrt(C - 2 * n * math.sin(r(lat0))) / n
    th = n * r(lon - lon0)
    rho = math.sqrt(C - 2 * n * math.sin(r(lat))) / n
    return rho * math.sin(th), rho0 - rho * math.cos(th)


@lru_cache(maxsize=2)
def _us_shapes():
    import json
    from pathlib import Path
    g = json.load(open(Path(__file__).resolve().parents[1] / "assets/geo/us_states.json"))
    out = {}
    for ft in g["features"]:
        nm = ft["properties"]["name"]
        if nm in ("Alaska", "Hawaii", "Puerto Rico"):
            continue
        geom = ft["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        out[nm] = [[_albers(x, y) for x, y in poly[0]] for poly in polys]
    return out


class USMap(Editorial):
    """미국 지도. fill: 기본 주 색, states: {주 이름: 색}, kicker/title 왼쪽 아래, bars: 오른쪽 아래 막대
    bars: [{label, left, right, left_color, right_color, mid}]"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(_poster_bg(sp.get("tone", "teal")), (0, 0))
        f.alpha_composite(Image.new("RGBA", f.size, (0, 20, 30, 120)))
        shapes = _us_shapes()
        allp = [p for polys in shapes.values() for poly in polys for p in poly]
        xs_, ys_ = [p[0] for p in allp], [p[1] for p in allp]
        mnx, mxx, mny, mxy = min(xs_), max(xs_), min(ys_), max(ys_)
        W, H = 1240, 700
        ox, oy = (S.W - W) / 2 + 140, 150
        sc = min(W / (mxx - mnx), H / (mxy - mny))

        def P(p):
            return (ox + (p[0] - mnx) * sc) * 2, (oy + (mxy - p[1]) * sc) * 2

        k = 2
        base = sp.get("fill", [44, 70, 150])
        lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        order = list(shapes.keys())
        kk = G.ease_out(t / 0.8)
        hl = sp.get("states", {})
        for j, nm in enumerate(order):
            c = tuple(hl.get(nm, base)) if t >= self.line_start(sp.get("states_on", 1)) + 0.2 else tuple(base)
            for poly in shapes[nm]:
                d.polygon([P(p) for p in poly], fill=c + (255,), outline=(240, 236, 220, 255), width=2 * k)
        lay = lay.resize((S.W, S.H), Image.LANCZOS)
        # 입체감: 그림자 + 질감
        a = lay.getchannel("A")
        sh = Image.new("RGBA", f.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.55)))
        G.blit(f, sh.filter(ImageFilter.GaussianBlur(12)), (10, 16), kk)
        arr = np.array(lay).astype(np.float32)
        arr[..., :3] += _grain(S.W, S.H, seed=5, amt=14)[..., None]
        lay = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
        G.blit(f, lay, (0, (1 - kk) * 20), kk)
        # 아래쪽 어둡게 + 제목
        grad = np.linspace(0, 1, 360)[:, None] ** 1.6 * 220
        g = Image.fromarray(np.repeat(grad, S.W, 1).astype(np.uint8), "L")
        dk = Image.new("RGBA", (S.W, 360), (6, 10, 18, 255))
        dk.putalpha(g)
        f.alpha_composite(dk, (0, S.H - 360))
        y = 760
        if sp.get("kicker"):
            kt = T(sp["kicker"], 40, Y, "ExtraBold")
            G.blit(f, kt, (200, y), G.appear(t, 0.2, 0.3))
            y += kt.height + 4
        if sp.get("title"):
            tt = T(sp["title"], 72, S.FG, "Black", highlight=sp.get("highlight", ""), hl_fill=Y)
            shadow(f, tt, (200, y), "lt", G.appear(t, 0.3, 0.35))
        bx, by = 1180, 760
        for b in sp.get("bars", []):
            o = G.ease_out((t - self.line_start(b.get("on", 1)) - 0.2) / 0.6)
            if o <= 0:
                continue
            tot = b["left"] + b["right"] + b.get("mid", 0)
            bw = 540
            G.blit(f, T(b["label"], 34, S.FG, "ExtraBold"), (bx - 30, by + 6), o, "rt")
            lw = int(bw * b["left"] / tot * o)
            rw = int(bw * b["right"] / tot * o)
            lc, rc = _col(b.get("left_color"), (60, 120, 230)), _col(b.get("right_color"), (226, 70, 60))
            G.blit(f, Image.new("RGBA", (bw, 30), (70, 74, 86, 255)), (bx, by + 8), o)
            if lw:
                G.blit(f, Image.new("RGBA", (lw, 30), lc + (255,)), (bx, by + 8))
            if rw:
                G.blit(f, Image.new("RGBA", (rw, 30), rc + (255,)), (bx + bw - rw, by + 8))
            G.blit(f, Image.new("RGBA", (3, 44), (255, 255, 255, 230)), (bx + bw // 2, by + 1), o)
            G.blit(f, T(str(b["left"]), 52, tuple(min(255, c + 50) for c in lc), "Black"), (bx, by + 44), o)
            G.blit(f, T(str(b["right"]), 52, tuple(min(255, c + 40) for c in rc), "Black"), (bx + bw, by + 44), o, "rt")
            if b.get("note"):
                G.blit(f, T(b["note"], 24, (210, 214, 224), "SemiBold"), (bx + bw / 2, by + 60), o, "mt")
            by += 130
        self.finish(f, t)


TYPES.update({"poster": Poster, "usmap": USMap})
