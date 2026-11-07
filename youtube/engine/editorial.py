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


def header(f, sp, t, t0, y=210, center=True, fg=S.FG, acc=Y):
    """kicker(노랑, 작게) + title(흰, 크게, 부분 노랑)"""
    x = S.W / 2 if center else 200
    anc = "mt" if center else "lt"
    yy = y
    if sp.get("kicker"):
        k = T(sp["kicker"], 40, acc, "ExtraBold")
        shadow(f, k, (x, yy), anc, G.appear(t, t0, 0.3), alpha=0.6 if fg == S.FG else 0)
        yy += k.height + 6
    if sp.get("title"):
        k = G.ease_out((t - t0 - 0.05) / 0.35)
        if fg == S.FG:
            tt = T(sp["title"], sp.get("title_size", 84), fg, "Black", highlight=sp.get("highlight", ""), hl_fill=acc,
                   align="center" if center else "left", line_gap=1.15)
            shadow(f, tt, (x, yy + (1 - k) * 24), anc, k)
        else:
            tt = riso_text(sp["title"], sp.get("title_size", 84), fg, CORAL, highlight=sp.get("highlight", ""), hl_fill=acc,
                           align="center" if center else "left", line_gap=1.15)
            G.blit(f, tt, (x, yy + (1 - k) * 24), k, anc)
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
        bg = self.spec.get("bg") or {"kind": "paper"}
        self.paper = bg.get("kind") == "paper"
        if self.paper:
            f.paste(paper_bg(), (0, 0))
            self.fg, self.acc, self.dim, self.off = NAVY, CORAL, (120, 112, 98), (196, 186, 166)
        else:
            bd, _ = backdrop(bg)
            f.paste(bd, (0, 0))
            self.fg, self.acc, self.dim, self.off = S.FG, Y, (190, 196, 210), (90, 94, 108)

    def hdr(self, f, t, **kw):
        return header(f, self.spec, t, 0.0, fg=self.fg, acc=self.acc, **kw)

    def finish(self, f, t):
        (riso_credit if getattr(self, "paper", False) else credit)(f, self.spec)
        self.draw_common(f, t)


class Timeline(Editorial):
    """ticks: [{label, sub}] · band: [i0, i1, label, color] · marker_to: 인덱스 · tag: {text, at, color} · bottom"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 200))
        ticks = sp["ticks"]
        x0, x1, yl = 300, S.W - 300, sp.get("line_y", 600)
        n = len(ticks)
        xs = [x0 + (x1 - x0) * i / max(1, n - 1) for i in range(n)]
        d = ImageDraw.Draw(f)
        kl = G.ease_out(t / 0.6)
        d.line((x0, yl, x0 + (x1 - x0) * kl, yl), fill=self.fg + (235,), width=5)
        for i, (x, tk) in enumerate(zip(xs, ticks)):
            o = G.appear(t, 0.1 + i * 0.06, 0.2)
            if o <= 0:
                continue
            d.line((x, yl - 18, x, yl + 18), fill=self.fg + (int(235 * o),), width=5)
            hl = tk.get("hl")
            lab = T(tk["label"], 38, self.acc if hl else self.fg, "ExtraBold")
            G.blit(f, lab, (x, yl + 34), o, "mt")
            if tk.get("sub"):
                G.blit(f, T(tk["sub"], 26, self.dim, "SemiBold"), (x, yl + 34 + lab.height + 4), o, "mt")
        for b in sp.get("bands", []):
            i0, i1 = b["from"], b["to"]
            tb = self.line_start(b.get("on", 1))
            kb = G.ease_out((t - tb) / 0.6)
            if kb <= 0:
                continue
            c = _col(b.get("color"), self.acc)
            bx0, bx1 = xs[i0], xs[i0] + (xs[i1] - xs[i0]) * kb
            band = Image.new("RGBA", (max(2, int(bx1 - bx0)), 22), c + (235,))
            G.blit(f, band, (bx0, yl - 11))
            if b.get("label"):
                lb = G.pill(b["label"], "ExtraBold", 32, PAPER, c, pad=(20, 8))
                G.blit(f, lb, ((xs[i0] + xs[i1]) / 2, yl - 40), min(1, kb * 1.5), "mb")
        tg = sp.get("tag")
        if tg:
            o = G.appear(t, self.line_start(tg.get("on", 1)) + 0.2, 0.3)
            c = _col(tg.get("color"), S.UP)
            p = G.pill(tg["text"], "ExtraBold", 36, S.FG, c, pad=(26, 12), radius=4)
            G.blit(f, p, (xs[tg.get("at", n - 1)], yl - 100), o, "mb")
        if sp.get("bottom"):
            o = G.appear(t, self.line_start(sp.get("bottom_on", 1)) + 0.3, 0.35)
            b = T(sp["bottom"], 64, self.fg, "Black", highlight=sp.get("bottom_hl", ""), hl_fill=self.acc)
            G.blit(f, b, (S.W / 2, yl + 190), o, "mt")
        self.finish(f, t)


class Grid(Editorial):
    """n칸 중 k칸 강조 (예: 76년 중 58년). cols, labels(선택), headline, bar: {value, max, label}"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        yy = self.hdr(f, t, y=sp.get("title_y", 170))
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
            colr = _col(sp.get("hit_color"), self.acc) if on else self.off
            im = _person(cell, colr) if person else _cell(cell, colr, sp.get("labels", [None] * n)[i])
            G.blit(f, im, (gx + c * (cell + gap), gy + r * (cell + gap)), o)
        yb = gy + rows * (cell + gap) + 40
        if sp.get("headline"):
            o = G.appear(t, self.line_start(sp.get("headline_on", 1)) + 0.4, 0.35)
            h = T(sp["headline"], 68, self.fg, "Black", highlight=sp.get("headline_hl", ""), hl_fill=self.acc)
            G.blit(f, h, (S.W / 2, yb), o, "mt")
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
        yy = self.hdr(f, t, y=sp.get("title_y", 200))
        rows = sp["rows"]
        vmax = sp.get("vmax") or max(abs(r["value"]) for r in rows)
        x0, wmax = 300, S.W - 600
        y = yy + 70
        for r in rows:
            t0 = self.line_start(r.get("on", 1)) + r.get("offset", 0)
            k = G.ease_out((t - t0) / 0.7)
            hl = r.get("hl")
            c = _col(r.get("color"), self.acc if hl else (self.off if self.paper else (200, 204, 214)))
            lab = T(r["label"], 36, self.acc if hl else (self.dim if self.paper else (230, 200, 120)), "ExtraBold")
            G.blit(f, lab, (x0, y), min(1, k * 2) if k > 0 else 0)
            y += lab.height + 10
            bw = max(8, int(wmax * abs(r["value"]) / vmax * k))
            if k > 0:
                G.blit(f, Image.new("RGBA", (bw, sp.get("bar_h", 58)), c + (255,)), (x0, y))
                txt = T(counter(r.get("text", str(r["value"])), (t - t0) / 0.7), 64, self.acc if hl else self.fg, "Black")
                if bw + txt.width + 30 < wmax + 220:
                    shadow(f, txt, (x0 + bw + 24, y + sp.get("bar_h", 58) / 2), "lm", min(1, k * 2), alpha=0 if self.paper else 0.6)
                else:
                    shadow(f, txt, (x0 + bw, y - 8), "rb", min(1, k * 2), alpha=0 if self.paper else 0.6)
            y += sp.get("bar_h", 58) + sp.get("row_gap", 40)
        self.finish(f, t)


class Profile(Editorial):
    """values: 곡선 점들, labels: x축 라벨(같은 개수 또는 양끝), hl: [i0, i1] 노랗게 채울 구간, marker: 인덱스"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 200))
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
        d.line([(x * k, y * k) for x, y in zip(fx[:m], fy[:m])], fill=(self.dim if self.paper else (200, 204, 214)) + (230,), width=4 * k)
        d.line((x0 * k, base * k, x1 * k, base * k), fill=self.fg + (220,), width=3 * k)
        if sp.get("hl"):
            i0, i1 = sp["hl"]
            th = self.line_start(sp.get("hl_on", 1))
            kh = G.ease_out((t - th) / 0.9)
            if kh > 0:
                a, b = xs[i0], xs[i0] + (xs[i1] - xs[i0]) * kh
                sel = (fx >= a) & (fx <= b)
                pts = [(x * k, y * k) for x, y in zip(fx[sel], fy[sel])]
                if len(pts) > 1:
                    d.polygon(pts + [(pts[-1][0], base * k), (pts[0][0], base * k)], fill=self.acc + (150,))
                    d.line(pts, fill=self.acc + (255,), width=6 * k)
                    ex, ey = pts[-1]
                    r = 14 * k
                    d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=self.acc + (255,))
                    d.ellipse((ex - 2.2 * r, ey - 2.2 * r, ex + 2.2 * r, ey + 2.2 * r), outline=self.acc + (200,), width=3 * k)
        f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
        labels = sp.get("labels", [])
        for i, lab in enumerate(labels):
            if not lab:
                continue
            hl = sp.get("hl") and sp["hl"][0] <= i <= sp["hl"][1]
            G.blit(f, T(lab, 32, self.acc if hl else self.fg, "ExtraBold"), (xs[i], base + 22), kd, "mt")
        for c in sp.get("pins", []):
            o = G.appear(t, self.line_start(c.get("on", 1)) + 0.3, 0.3)
            p = G.pill(c["text"], "ExtraBold", 34, PAPER if self.paper else INK, self.acc, pad=(20, 8), radius=4)
            G.blit(f, p, (xs[c["at"]], ys[c["at"]] - 40), o, "mb")
        self.finish(f, t)


TYPES = {"timeline": Timeline, "grid": Grid, "hbars": HBars, "profile": Profile}


# ── 포스터형: 컬러 배경 + 무늬 띠 + 실제 차트로 만든 검은 '산' 실루엣 ─────────
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




# ════════════════════════════════════════════════════════════════
# 채널 고유 '리소 인쇄' 스타일 — 크림색 종이 + 남색·코랄·금색 2~3도 인쇄 + 살짝 어긋난 판(오프셋)
# ════════════════════════════════════════════════════════════════
PAPER = (243, 235, 218)
NAVY = (30, 42, 92)
CORAL = (236, 96, 82)
GOLD = (240, 176, 40)
RISO = {"navy": NAVY, "coral": CORAL, "gold": GOLD, "teal": (22, 140, 140), "ink": (30, 30, 36)}


def _rc(c, default=NAVY):
    if isinstance(c, (list, tuple)):
        return tuple(c)
    return RISO.get(c, default)


@lru_cache(maxsize=4)
def paper_bg(tint=None):
    w, h = S.W, S.H
    base = np.array(_rc(tint, PAPER) if tint else PAPER, np.float32)
    a = np.ones((h, w, 3), np.float32) * base
    a += _grain(w, h, seed=21, amt=6)[..., None]
    # 종이 섬유 얼룩
    a += (_grain(w // 8, h // 8, seed=22, amt=3).repeat(8, 0).repeat(8, 1)[:h, :w])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(maxsize=8)
def halftone(w, h, color, step=14, rmax=5.0, direction="down"):
    """망점 그라데이션 판"""
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for yy in range(0, h, step):
        frac = yy / max(1, h)
        r = rmax * (frac if direction == "down" else 1 - frac)
        if r < 0.6:
            continue
        off = step / 2 if (yy // step) % 2 else 0
        for xx in range(int(off), w, step):
            d.ellipse(((xx - r) * k, (yy - r) * k, (xx + r) * k, (yy + r) * k), fill=color + (255,))
    return im.resize((w, h), Image.LANCZOS)


def riso_text(text, size, color=NAVY, shadow_c=CORAL, off=(5, 4), weight="Black", **kw):
    """글자 + 어긋난 색판 그림자"""
    a = T(text, size, color, weight, **kw)
    b = T(text, size, shadow_c, weight, **kw)
    im = Image.new("RGBA", (a.width + off[0], a.height + off[1]), (0, 0, 0, 0))
    im.alpha_composite(G.with_opacity(b, 0.85), off)
    im.alpha_composite(a, (0, 0))
    return im


def riso_header(f, sp, t, x=150, y=200):
    if sp.get("kicker"):
        k = T(sp["kicker"], 40, CORAL, "ExtraBold")
        G.blit(f, k, (x + 4, y), G.appear(t, 0.0, 0.3))
        y += k.height + 6
    if sp.get("title"):
        tt = riso_text(sp["title"], sp.get("title_size", 86), NAVY, CORAL, highlight=sp.get("highlight", ""), hl_fill=CORAL,
                       line_gap=1.12)
        kk = G.ease_out(t / 0.4)
        G.blit(f, tt, (x, y + (1 - kk) * 18), kk)
        y += tt.height
    return y


def riso_credit(f, sp):
    if sp.get("credit"):
        G.blit(f, T(sp["credit"], 20, (110, 104, 92), "SemiBold"), (S.W - S.SAFE_X + 40, 128), 0.9, "rt")


class RisoPoster(Editorial):
    """종이 포스터: 왼쪽 위 제목, 해(금색 원), 실제 지수로 만든 산(남색 + 코랄 어긋난 판 + 가로 결),
    pin: {at, label, on} 동그란 표식 + 말풍선, figure: {name, at, size, on} 실루엣"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(paper_bg(), (0, 0))
        sun = sp.get("sun", [1500, 360, 170])
        ks = G.ease_out(t / 0.8)
        if sun:
            r = sun[2] * (0.7 + 0.3 * ks)
            s_im = Image.new("RGBA", (int(r * 2) + 4, int(r * 2) + 4), (0, 0, 0, 0))
            ImageDraw.Draw(s_im).ellipse((2, 2, 2 + r * 2, 2 + r * 2), fill=_rc(sp.get("sun_color"), GOLD) + (255,))
            G.blit(f, s_im, (sun[0], sun[1]), ks, "mm")
        riso_header(f, sp, t)
        rg = sp["ridge"]
        from . import data as D
        s = D.series(rg["series"], rg.get("start"), rg.get("end")).dropna()
        v = np.log(s.values) if rg.get("log") else s.values
        n = 240
        v = np.interp(np.linspace(0, len(v) - 1, n), np.arange(len(v)), v)
        v = np.convolve(np.pad(v, 3, mode="edge"), np.ones(7) / 7, mode="valid")
        lo, hi = v.min(), v.max()
        nv = 0.15 + 0.85 * (v - lo) / (hi - lo + 1e-9)
        x0, x1, base, hh = 0, S.W, 1000, rg.get("height", 420)
        xs = np.linspace(x0, x1, n)
        ys = base - nv * hh
        kd = G.ease_out((t - 0.1) / 1.0)
        m = max(2, int(n * kd))
        k = 2
        main = _rc(sp.get("ridge_color"), NAVY)
        for col_, (dx, dy), op in ((CORAL, (12, -10), 0.9), (main, (0, 0), 1.0)):
            lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            pts = [((x + dx) * k, (y + dy) * k) for x, y in zip(xs[:m], ys[:m])]
            d.polygon(pts + [((xs[m - 1] + dx) * k, S.H * k), ((x0 + dx) * k, S.H * k)], fill=col_ + (255,))
            lay = lay.resize((S.W, S.H), Image.LANCZOS)
            f.alpha_composite(G.with_opacity(lay, op))
        # 산 안쪽 가로 결(인쇄 줄무늬)
        hatch = Image.new("RGBA", f.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hatch)
        for yy in range(int(ys.min()) + 30, S.H, 18):
            hd.line((0, yy, S.W, yy), fill=PAPER + (34,), width=3)
        mask = Image.new("L", f.size, 0)
        ImageDraw.Draw(mask).polygon([(x, y + 24) for x, y in zip(xs[:m], ys[:m])] + [(xs[m - 1], S.H), (0, S.H)], fill=255)
        hatch.putalpha(Image.fromarray(np.minimum(np.array(hatch.getchannel("A")), np.array(mask))))
        f.alpha_composite(hatch)
        pin = sp.get("pin")
        if pin:
            o = G.appear(t, self.line_start(pin.get("on", 1)) + 0.3, 0.3)
            i = int(pin.get("at", 0.3) * (n - 1))
            px, py = xs[i], ys[i]
            if o > 0:
                d = ImageDraw.Draw(f)
                r = 16
                d.ellipse((px - r - 6, py - r - 6, px + r + 6, py + r + 6), fill=PAPER + (int(255 * o),))
                d.ellipse((px - r, py - r, px + r, py + r), fill=GOLD + (int(255 * o),))
                ty = py - 130
                d.line((px, py - r - 6, px, ty + 40), fill=NAVY + (int(255 * o),), width=4)
                lb = G.pill(pin["label"], "ExtraBold", 36, PAPER, NAVY, pad=(22, 10), radius=26)
                G.blit(f, lb, (min(max(px, 60 + lb.width / 2), S.W - 60 - lb.width / 2), ty + 40), o, "mb")
        fg = sp.get("figure")
        if fg:
            o = G.appear(t, self.line_start(fg.get("on", 1)) + 0.2, 0.4)
            i = int(fg.get("at", 0.7) * (n - 1))
            size = fg.get("size", 170)
            a = silhouette(fg["name"], size, CORAL)
            b = silhouette(fg["name"], size, _rc(fg.get("color"), GOLD))
            if fg.get("flip"):
                a, b = a.transpose(Image.FLIP_LEFT_RIGHT), b.transpose(Image.FLIP_LEFT_RIGHT)
            G.blit(f, a, (xs[i] + 8, ys[i] + 14 + (1 - o) * 30), o * 0.9, "mb")
            G.blit(f, b, (xs[i], ys[i] + 8 + (1 - o) * 30), o, "mb")
        riso_credit(f, sp)
        self.draw_common(f, t)


class DotMap(Editorial):
    """점(망점)으로 찍은 미국 지도. states: {주: 색}, title/kicker 왼쪽 위, stat: {value, label} 오른쪽 아래"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(paper_bg(), (0, 0))
        riso_header(f, sp, t)
        dots = _us_dots(sp.get("step", 15))
        hl = sp.get("states", {})
        ton = self.line_start(sp.get("states_on", 1)) + 0.3
        k = 2
        lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        kk = G.ease_out(t / 0.9)
        for (x, y, nm) in dots:
            if (x - 420) / 1400 > kk * 1.2:
                continue
            c = _rc(hl[nm]) if (nm in hl and t >= ton) else (150, 160, 190)
            r = 6.0 if (nm in hl and t >= ton) else 4.6
            d.ellipse(((x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k), fill=c + (255,))
        f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
        st = sp.get("stat")
        if st:
            o = G.appear(t, self.line_start(st.get("on", 1)) + 0.3, 0.3)
            v = riso_text(st["value"], 140, CORAL, NAVY, off=(6, 5))
            G.blit(f, v, (150, 850), o, "lb")
            G.blit(f, T(st["label"], 38, NAVY, "ExtraBold"), (156, 862), o, "lt")
        riso_credit(f, sp)
        self.draw_common(f, t)


@lru_cache(maxsize=2)
def _us_dots(step=15):
    from PIL import ImageDraw as D2
    shapes = _us_shapes()
    allp = [p for polys in shapes.values() for poly in polys for p in poly]
    xs_, ys_ = [p[0] for p in allp], [p[1] for p in allp]
    mnx, mxx, mny, mxy = min(xs_), max(xs_), min(ys_), max(ys_)
    W, H = 1180, 660
    sc = min(W / (mxx - mnx), H / (mxy - mny))
    ox, oy = S.W - W - 110, 250
    lab = Image.new("I", (S.W, S.H), 0)
    d = D2.Draw(lab)
    names = list(shapes)
    for j, nm in enumerate(names):
        for poly in shapes[nm]:
            d.polygon([(ox + (p[0] - mnx) * sc, oy + (mxy - p[1]) * sc) for p in poly], fill=j + 1)
    a = np.array(lab)
    out = []
    for yy in range(oy, oy + H + 1, step):
        off = step // 2 if ((yy - oy) // step) % 2 else 0
        for xx in range(ox + off, ox + W + 1, step):
            v = a[yy, xx]
            if v:
                out.append((xx, yy, names[v - 1]))
    return tuple(out)


class SplitFlap(Editorial):
    """공항 출발 안내판처럼 글자 타일이 한 칸씩 넘어가며 나타나는 큰 단어"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(paper_bg(), (0, 0))
        word = sp["word"]
        lines = word.split("\n")
        tile_w, tile_h, gap = sp.get("tile", (118, 168, 12))
        n_max = max(len(l) for l in lines)
        tw = n_max * (tile_w + gap)
        if tw > S.W - 200:
            r = (S.W - 200) / tw
            tile_w, tile_h, gap = int(tile_w * r), int(tile_h * r), max(6, int(gap * r))
        y = sp.get("y", 300)
        idx = 0
        for li, line in enumerate(lines):
            x = (S.W - len(line) * (tile_w + gap) + gap) / 2
            for ch in line:
                t0 = 0.1 + idx * 0.06
                k = G.clamp((t - t0) / 0.18)
                if ch != " " and k > 0:
                    tile = _flap(ch, tile_w, tile_h, sp.get("hl_chars", "") and ch in sp.get("hl_chars", ""))
                    sy = max(0.05, abs(np.cos((1 - k) * np.pi / 2 * 2)) if k < 1 else 1)
                    th = max(2, int(tile_h * (k if k < 1 else 1)))
                    G.blit(f, tile.resize((tile_w, th)), (x, y + (tile_h - th) / 2))
                x += tile_w + gap
                idx += 1
            y += tile_h + gap * 2
        if sp.get("sub"):
            o = G.appear(t, self.line_start(sp.get("sub_on", 1)) + 0.5, 0.4)
            s = riso_text(sp["sub"], 56, NAVY, CORAL, off=(4, 3), weight="ExtraBold", highlight=sp.get("highlight", ""), hl_fill=CORAL)
            G.blit(f, s, (S.W / 2, y + 30), o, "mt")
        riso_credit(f, sp)
        self.draw_common(f, t)

    def extra_sfx(self):
        return [(0.1, "tick", 0.3), (0.4, "tick", 0.3), (0.7, "tick", 0.3)]


@lru_cache(maxsize=128)
def _flap(ch, w, h, hl=False):
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bg = CORAL if hl else NAVY
    d.rounded_rectangle((0, 0, w * k - 1, h * k - 1), radius=12 * k, fill=bg + (255,))
    d.rounded_rectangle((0, 0, w * k - 1, h * k // 2), radius=12 * k, fill=tuple(min(255, c + 14) for c in bg) + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    g = T(ch, int(h * 0.68), PAPER, "Black")
    im.alpha_composite(g, ((w - g.width) // 2, (h - g.height) // 2 - 2))
    d = ImageDraw.Draw(im)
    d.line((0, h // 2, w, h // 2), fill=(10, 14, 30, 255), width=3)
    return im


class Ticket(Editorial):
    """티켓 모양 카드: 왼쪽(라벨·큰 숫자) | 점선 절취선 | 오른쪽 꼬리(보조 정보). 위에 제목"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(paper_bg(), (0, 0))
        riso_header(f, sp, t)
        t0 = self.line_start(sp.get("on", 1))
        k = G.ease_out((t - t0) / 0.45)
        if k > 0:
            W, H, stub = 1340, 380, 360
            kk = 2
            im = Image.new("RGBA", ((W + 20) * kk, (H + 20) * kk), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((16 * kk, 16 * kk, (W + 16) * kk, (H + 16) * kk), radius=28 * kk, fill=CORAL + (255,))
            d.rounded_rectangle((0, 0, W * kk, H * kk), radius=28 * kk, fill=NAVY + (255,))
            cx = (W - stub) * kk
            for yy in range(30 * kk, (H - 30) * kk, 26 * kk):
                d.line((cx, yy, cx, yy + 12 * kk), fill=PAPER + (200,), width=3 * kk)
            for cy in (0, H * kk):
                d.ellipse((cx - 22 * kk, cy - 22 * kk, cx + 22 * kk, cy + 22 * kk), fill=PAPER + (255,))
            im = im.resize((W + 20, H + 20), Image.LANCZOS)
            if sp.get("label"):
                im.alpha_composite(T(sp["label"], 38, GOLD, "ExtraBold"), (60, 50))
            val = counter(sp["value"], (t - t0) / 0.9)
            v = T(val, sp.get("value_size", 170), PAPER, "Black")
            im.alpha_composite(v, (54, 105))
            if sp.get("unit"):
                u = T(sp["unit"], 64, PAPER, "Black")
                im.alpha_composite(u, (64 + v.width, 105 + v.height - u.height - 20))
            if sp.get("stub"):
                st = T(sp["stub"], 40, PAPER, "ExtraBold", max_w=stub - 60, align="center", line_gap=1.25)
                im.alpha_composite(st, (W - stub + (stub - st.width) // 2, (H - st.height) // 2))
            ang = (1 - k) * 8 - 2
            im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
            G.blit(f, im, (S.W / 2, sp.get("y", 680) + (1 - k) * 60), k, "mm")
        riso_credit(f, sp)
        self.draw_common(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec.get("on", 1)), "pop", 0.4)]


TYPES.update({"poster": RisoPoster, "dotmap": DotMap, "flap": SplitFlap, "ticket": Ticket})


# ════════════════════════════════════════════════════════════════
# 변주 2탄 — 캡슐 숫자 · 아이소메트릭 탑 · KPI+막대 · 액자 비교 (리소 톤 유지)
# ════════════════════════════════════════════════════════════════
class Capsule(Editorial):
    """가운데 큰 알약 모양 카드: 숫자 + 단위 + 강조어, 기울어진 도장. kicker 위, sub 아래"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        if sp.get("ghost"):  # 배경에 아주 큰 옅은 글자
            g = T(sp["ghost"], 420, (self.fg if self.paper else (255, 255, 255)), "Black")
            G.blit(f, g, (S.W / 2 + 30 - t * 10, S.H / 2), 0.06, "mm")
        y = 230
        if sp.get("kicker"):
            k = T(sp["kicker"], 46, self.dim if self.paper else (200, 204, 214), "ExtraBold")
            G.blit(f, k, (S.W / 2, y), G.appear(t, 0.0, 0.3), "mb")
        t0 = self.line_start(sp.get("on", 1))
        kk = G.ease_out((t - t0) / 0.45)
        if kk > 0:
            val = T(counter(sp["value"], (t - t0) / 0.9), sp.get("value_size", 210), NAVY, "Black")
            unit = T(sp.get("unit", ""), 84, NAVY, "Black") if sp.get("unit") else None
            acc = T(sp.get("accent", ""), 84, CORAL, "Black") if sp.get("accent") else None
            w = val.width + (unit.width + 24 if unit else 0) + (acc.width + 20 if acc else 0) + 160
            h = val.height + 70
            k2 = 2
            cap = Image.new("RGBA", ((w + 24) * k2, (h + 24) * k2), (0, 0, 0, 0))
            d = ImageDraw.Draw(cap)
            d.rounded_rectangle((18 * k2, 22 * k2, (w + 18) * k2, (h + 22) * k2), radius=h * k2 // 2, fill=(CORAL if self.paper else (10, 12, 20)) + (255,))
            d.rounded_rectangle((0, 0, w * k2, h * k2), radius=h * k2 // 2, fill=PAPER + (255,), outline=NAVY + (255,), width=6 * k2)
            cap = cap.resize((w + 24, h + 24), Image.LANCZOS)
            x = 80
            cap.alpha_composite(val, (x, (h - val.height) // 2 + 4))
            x += val.width + 24
            if unit:
                cap.alpha_composite(unit, (x, (h + val.height) // 2 - unit.height - 18))
                x += unit.width + 20
            if acc:
                cap.alpha_composite(acc, (x, (h + val.height) // 2 - acc.height - 18))
            sc = 0.85 + 0.15 * kk
            cap2 = cap.resize((int(cap.width * sc), int(cap.height * sc)), Image.BICUBIC)
            G.blit(f, cap2, (S.W / 2, 540), kk, "mm")
            if sp.get("badge"):
                ks = G.clamp((t - t0 - 0.5) / 0.22)
                if ks > 0:
                    st = _riso_stamp(sp["badge"])
                    s2 = 1.8 - 0.8 * G.ease_out(ks)
                    st = st.resize((int(st.width * s2), int(st.height * s2)), Image.BICUBIC).rotate(8, expand=True, resample=Image.BICUBIC)
                    G.blit(f, st, (S.W / 2 + cap.width / 2 - 20, 540 - cap.height / 2 + 10), min(1, ks * 1.5), "mm")
        if sp.get("sub"):
            o = G.appear(t, self.line_start(sp.get("sub_on", 1)) + 0.4, 0.3)
            s = T(sp["sub"], 40, self.fg, "ExtraBold", highlight=sp.get("sub_hl", ""), hl_fill=self.acc)
            G.blit(f, s, (S.W / 2, 770), o, "mt")
        self.finish(f, t)

    def extra_sfx(self):
        t0 = self.line_start(self.spec.get("on", 1))
        return [(t0, "pop", 0.4)] + ([(t0 + 0.5, "boom", 0.25)] if self.spec.get("badge") else [])


def _riso_stamp(text):
    tx = T(text, 54, GOLD, "Black")
    w, h = tx.width + 60, tx.height + 34
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=NAVY + (255,), outline=GOLD + (255,), width=6)
    im.alpha_composite(tx, (30, 14))
    return im


class IsoBars(Editorial):
    """아이소메트릭 탑(블록)이 차례로 솟는 성장 그래프. items: [{label(위), year(아래), sub, value, hl}]"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=sp.get("center", False))
        items = sp["items"]
        n = len(items)
        vmax = max(it["value"] for it in items)
        x0, x1, base = 260, S.W - 220, sp.get("base", 800)
        slot = (x1 - x0) / n
        bw = min(170, slot * 0.62)
        dep = bw * 0.42
        hmax = sp.get("hmax", 440)
        t0 = self.line_start(sp.get("on", 1))
        for i, it in enumerate(items):
            k = G.ease_out((t - t0 - i * sp.get("step", 0.25)) / 0.5)
            if k <= 0:
                continue
            cx = x0 + slot * (i + 0.5)
            hh = max(14, hmax * (it["value"] / vmax) ** sp.get("gamma", 0.55) * k)
            hl = it.get("hl")
            top_c = CORAL if hl else ((92, 150, 120) if not self.paper else (120, 168, 140))
            front = NAVY if self.paper else (40, 46, 62)
            side = tuple(max(0, c - 18) for c in front)
            kk = 2
            im = Image.new("RGBA", (int((bw + dep) * kk) + 4, int((hh + dep) * kk) + 4), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            fx0, fy0 = 0, dep * kk
            d.rectangle((fx0, fy0, bw * kk, (dep + hh) * kk), fill=front + (255,))
            d.polygon([(bw * kk, fy0), ((bw + dep) * kk, 0), ((bw + dep) * kk, hh * kk), (bw * kk, (dep + hh) * kk)], fill=side + (255,))
            d.polygon([(0, fy0), (dep * kk, 0), ((bw + dep) * kk, 0), (bw * kk, fy0)], fill=top_c + (255,))
            if hl:
                d.polygon([(0, fy0), (dep * kk, 0), ((bw + dep) * kk, 0), (bw * kk, fy0)], outline=GOLD + (255,), width=4 * kk)
            # 앞면 줄무늬(리소 결)
            for yy in range(int(fy0 + 20 * kk), int((dep + hh) * kk), 18 * kk):
                d.line((0, yy, bw * kk, yy), fill=(255, 255, 255, 18), width=2 * kk)
            im = im.resize((im.width // kk, im.height // kk), Image.LANCZOS)
            G.blit(f, im, (cx - bw / 2, base - hh - dep))
            lab = T(it["label"], 46 if hl else 38, (CORAL if hl else self.fg), "Black")
            G.blit(f, lab, (cx + dep / 2, base - hh - dep - 14), min(1, k * 2), "mb")
            G.blit(f, T(str(it["year"]), 36, self.fg, "Black"), (cx, base + 20), min(1, k * 2), "mt")
            if it.get("sub"):
                G.blit(f, T(it["sub"], 26, self.dim, "SemiBold"), (cx, base + 64), min(1, k * 2), "mt")
        self.finish(f, t)

    def extra_sfx(self):
        t0 = self.line_start(self.spec.get("on", 1))
        return [(t0 + i * self.spec.get("step", 0.25), "tick", 0.25) for i in range(len(self.spec["items"]))]


class KPI(Editorial):
    """왼쪽: KPI 2~3개(작은 라벨 + 큰 숫자) / 오른쪽: 세로 막대(값 위에 표시, 마지막 강조)"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        y = 300
        for j, kp in enumerate(sp["kpis"]):
            o = G.appear(t, self.line_start(kp.get("on", 1)) + 0.1, 0.35)
            lab = T(kp["label"], 38, self.fg, "ExtraBold")
            G.blit(f, lab, (180, y), o)
            y += lab.height + 6
            v = riso_text(counter(kp["value"], (t - self.line_start(kp.get("on", 1))) / 0.9), 132, _rc(kp.get("color"), CORAL), NAVY if self.paper else (0, 0, 0), off=(5, 5))
            G.blit(f, v, (172, y), o)
            y += v.height + 40
        bars = sp["bars"]
        n = len(bars)
        x0, x1, base, hmax = 880, S.W - 150, 720, 400
        slot = (x1 - x0) / n
        bw = slot * 0.74
        vmax = sp.get("vmax") or max(b["value"] for b in bars) * 1.05
        t0 = self.line_start(sp.get("bars_on", 1))
        for i, b in enumerate(bars):
            k = G.ease_out((t - t0 - i * 0.15) / 0.5)
            if k <= 0:
                continue
            cx = x0 + slot * (i + 0.5)
            hh = max(6, hmax * abs(b["value"]) / vmax * k)
            hl = b.get("hl", i == n - 1)
            c = GOLD if hl else ((214, 206, 188) if self.paper else (214, 218, 226))
            bar = Image.new("RGBA", (int(bw), int(hh)), c + (255,))
            if b["value"] < 0:
                hh = min(hh, 110)
                bar = Image.new("RGBA", (int(bw), int(hh)), (120, 150, 220, 255))
                G.blit(f, bar, (cx - bw / 2, base))
                G.blit(f, T(b.get("text", str(b["value"])), 36, (90, 120, 200), "Black"), (cx, base + hh + 8), min(1, k * 2), "mt")
                G.blit(f, T(b["label"], 30, self.fg, "ExtraBold"), (cx, base - 12), min(1, k * 2), "mb")
            else:
                G.blit(f, bar, (cx - bw / 2, base - hh))
                G.blit(f, T(b.get("text", str(b["value"])), 44 if hl else 36, self.fg, "Black"), (cx, base - hh - 12), min(1, k * 2), "mb")
                G.blit(f, T(b["label"], 30, self.fg, "ExtraBold"), (cx, base + 18), min(1, k * 2), "mt")
        d = ImageDraw.Draw(f)
        d.line((x0 - 10, base, x1 + 10, base), fill=self.fg + (160,), width=3)
        self.finish(f, t)


@lru_cache(maxsize=2)
def _gold_dust():
    """어두운 배경 + 금빛 먼지(보케)"""
    w, h = S.W, S.H
    a = np.ones((h, w, 3), np.float32) * np.array([16, 13, 10], np.float32)
    a = a * _vignette(w, h, 0.4) + _grain(w, h, seed=31, amt=5)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(5)
    for _ in range(90):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(1.5, 7)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 200, 110, int(rng.uniform(40, 150))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2.2)))
    return im


class Frames(Editorial):
    """미술관 액자 두 개(금테) 안에 실제 차트, 아래 캡션. panels: [{series, start, end, color, caption, hl, on}]"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(_gold_dust(), (0, 0))
        if sp.get("title"):
            tt = T(sp["title"], 56, (240, 226, 196), "ExtraBold", highlight=sp.get("highlight", ""), hl_fill=GOLD)
            G.blit(f, tt, (S.W / 2, 150), G.appear(t, 0.0, 0.3), "mt")
        pw, ph = 700, 400
        xs = [S.W / 2 - pw - 40, S.W / 2 + 40]
        for j, pn in enumerate(sp["panels"][:2]):
            o = G.appear(t, self.line_start(pn.get("on", 1)) + 0.15, 0.45)
            if o <= 0:
                continue
            x, y = xs[j], 280
            fr = _frame_panel(pw, ph, pn.get("series", "spx"), pn.get("start"), pn.get("end"), tuple(pn.get("color", (240, 200, 120))), pn.get("log", False))
            G.blit(f, fr, (x, y + (1 - o) * 20), o)
            cap = T(pn["caption"], 38, (230, 216, 190), "SemiBold", highlight=pn.get("hl", ""), hl_fill=GOLD)
            G.blit(f, cap, (x + pw / 2 + 8, y + ph + 50), o, "mt")
            if pn.get("value"):
                v = T(pn["value"], 64, GOLD if pn.get("good") else (130, 170, 240), "Black")
                G.blit(f, v, (x + pw / 2 + 8, y + ph + 108), o, "mt")
        self.finish(f, t)


@lru_cache(maxsize=8)
def _frame_panel(pw, ph, series_, start, end, color, log):
    from . import data as D
    k = 2
    im = Image.new("RGBA", ((pw + 16) * k, (ph + 16) * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, (pw + 16) * k - 1, (ph + 16) * k - 1), fill=(150, 112, 50, 255))
    d.rectangle((5 * k, 5 * k, (pw + 11) * k, (ph + 11) * k), outline=(240, 200, 120, 255), width=2 * k)
    d.rectangle((8 * k, 8 * k, (pw + 8) * k, (ph + 8) * k), fill=(20, 18, 16, 255))
    s = D.series(series_, start, end).dropna()
    v = np.log(s.values) if log else s.values
    xs = np.linspace(40, pw - 40, len(v)) + 8
    lo, hi = v.min(), v.max()
    ys = ph - 50 - (v - lo) / (hi - lo + 1e-9) * (ph - 120) + 8
    pts = [(x * k, y * k) for x, y in zip(xs, ys)]
    d.polygon(pts + [(xs[-1] * k, (ph - 30) * k), (xs[0] * k, (ph - 30) * k)], fill=color + (60,))
    d.line(pts, fill=color + (255,), width=4 * k)
    im = im.resize((pw + 16, ph + 16), Image.LANCZOS)
    lab = T(f"{s.index[0].year} ~ {s.index[-1].year}", 26, (220, 200, 160), "SemiBold")
    im.alpha_composite(lab, (30, 24))
    return im


TYPES.update({"capsule": Capsule, "isobars": IsoBars, "kpi": KPI, "frames": Frames})


class Duel(Editorial):
    """종이 위 두 장의 카드가 엇갈려 놓이는 비교(versus 대체). left/right: {title, value, sub, color, on}, heading"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(paper_bg(), (0, 0))
        if sp.get("heading"):
            h = riso_text(sp["heading"], 64, NAVY, CORAL, off=(4, 3), highlight=sp.get("highlight", ""), hl_fill=CORAL)
            G.blit(f, h, (S.W / 2, 170), G.appear(t, 0.0, 0.3), "mt")
        for j, side in enumerate(("left", "right")):
            c = sp[side]
            t0 = self.line_start(c.get("on", 1))
            k = G.ease_out((t - t0) / 0.45)
            if k <= 0:
                continue
            col = _rc(c.get("color"), CORAL if j else NAVY)
            if c.get("color") in ("up",):
                col = CORAL
            elif c.get("color") in ("down",):
                col = (60, 110, 200)
            elif c.get("color") in ("neutral", None):
                col = NAVY if j == 0 else (120, 112, 98)
            W2, H2 = 680, 420
            kk = 2
            im = Image.new("RGBA", ((W2 + 24) * kk, (H2 + 24) * kk), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rectangle((20 * kk, 22 * kk, (W2 + 20) * kk, (H2 + 22) * kk), fill=(30, 30, 40, 70))
            d.rectangle((0, 0, W2 * kk, H2 * kk), fill=(252, 248, 238, 255), outline=col + (255,), width=6 * kk)
            d.rectangle((0, 0, W2 * kk, 70 * kk), fill=col + (255,))
            im = im.resize((W2 + 24, H2 + 24), Image.LANCZOS)
            tt = T(c.get("title", ""), 40, PAPER, "ExtraBold")
            im.alpha_composite(tt, (34, 35 - tt.height // 2 + 2))
            v = T(counter(c["value"], (t - t0) / 0.8), c.get("size", 120), col, "Black")
            while v.width > W2 - 60:
                v = v.resize((int(v.width * 0.9), int(v.height * 0.9)), Image.LANCZOS)
            im.alpha_composite(v, ((W2 - v.width) // 2, 70 + (H2 - 70 - v.height) // 2 - 24))
            if c.get("sub"):
                sb = T(c["sub"], 32, (110, 104, 92), "SemiBold", max_w=W2 - 60, align="center")
                im.alpha_composite(sb, ((W2 - sb.width) // 2, H2 - 40 - sb.height))
            ang = (-4 if j == 0 else 3) * (0.5 + 0.5 * k) + (1 - k) * (12 if j else -12)
            im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
            cx = S.W / 2 + (-390 if j == 0 else 390)
            G.blit(f, im, (cx, 600 + (1 - k) * 80 + (20 if j else -10)), k, "mm")
        vs = sp.get("mid", "VS")
        if t > self.line_start(sp["right"].get("on", 1)):
            st = _riso_stamp(vs)
            G.blit(f, st.rotate(-8, expand=True, resample=Image.BICUBIC), (S.W / 2, 600), G.appear(t, self.line_start(sp["right"].get("on", 1)) + 0.2, 0.2), "mm")
        riso_credit(f, sp)
        self.draw_common(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec[s].get("on", 1)), "pop", 0.35) for s in ("left", "right")]


TYPES.update({"duel": Duel})
