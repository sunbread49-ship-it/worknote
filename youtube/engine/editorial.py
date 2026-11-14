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

import json

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
TEXT_SCALE = 1.12  # 2026-11-11: 화면 글자 전반 키우기 (직관 · 가독성)


def T(text, size, color=S.FG, weight="Black", **kw):
    return G.text_img(text, weight, int(round(size * TEXT_SCALE)), color, **kw)


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


@lru_cache(maxsize=24)
def _photo(name, dark, blur, gray, focus):
    from pathlib import Path
    import json
    d = Path(__file__).resolve().parents[1] / "assets" / "photos"
    meta = json.loads((d / f"{name}.json").read_text())
    im = Image.open(d / meta["file"]).convert("RGB")
    # 화면 비율로 채우기 (focus: 0~1 가로 · 세로 중심)
    sc = max(S.W / im.width, S.H / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    fx, fy = focus
    x0 = int((im.width - S.W) * fx)
    y0 = int((im.height - S.H) * fy)
    im = im.crop((x0, y0, x0 + S.W, y0 + S.H))
    if gray:
        im = ImageEnhance.Color(im).enhance(1 - gray)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.array(im, np.float32) * (1 - dark)
    a = a * _vignette(S.W, S.H, 0.5)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return out, meta["credit"]


def photo_backdrop(bg):
    return _photo(bg["file"], bg.get("dark", 0.62), bg.get("blur", 0), bg.get("gray", 0.85), tuple(bg.get("focus", (0.5, 0.4))))


def photo_card(name, w, h, gray=0.0, focus=(0.5, 0.35)):
    """사진을 w×h 카드로 잘라 반환 (테두리 · 그림자 포함)"""
    from pathlib import Path
    import json
    d = Path(__file__).resolve().parents[1] / "assets" / "photos"
    meta = json.loads((d / f"{name}.json").read_text())
    im = Image.open(d / meta["file"]).convert("RGB")
    sc = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = int((im.width - w) * focus[0]), int((im.height - h) * focus[1])
    im = im.crop((x0, y0, x0 + w, y0 + h))
    if gray:
        im = ImageEnhance.Color(im).enhance(1 - gray)
    card = Image.new("RGBA", (w + 8, h + 8), (230, 232, 238, 255))
    card.paste(im, (4, 4))
    return card, meta["credit"]


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
        bg = self.spec.get("bg") or {"kind": "grain", "tone": "navy"}
        self.paper = bg.get("kind") == "paper"
        if bg.get("kind") in ("video", "motion", "parallax"):  # 움직이는 배경 (2026-11-11)
            from . import bgvideo
            f.paste(bgvideo.at(bg, getattr(self, "_now", 0.0)).convert("RGBA"), (0, 0))
            if bg.get("kind") == "video" and not self.spec.get("credit"):
                self.spec["credit"] = bgvideo.credit(bg["file"])
            elif bg.get("kind") == "parallax" and not self.spec.get("credit"):
                _, cr = photo_backdrop({"kind": "photo", "file": bg["file"]})
                self.spec["credit"] = cr
            self.paper = False
            self.fg, self.acc, self.dim, self.off = S.FG, Y, (200, 204, 214), (90, 94, 108)
        elif bg.get("kind") == "photo":
            im, cr = photo_backdrop(bg)
            f.paste(im, (0, 0))
            if cr and not self.spec.get("credit"):
                self.spec["credit"] = cr
            self.fg, self.acc, self.dim, self.off = S.FG, Y, (200, 204, 214), (90, 94, 108)
        elif self.paper:
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
        bh, gap = sp.get("bar_h", 58), sp.get("row_gap", 40)
        lab_h = T("가", 36, self.fg, "ExtraBold").height + 10
        need = len(rows) * (lab_h + bh + gap) - gap
        if y + need > 860:  # 글자가 커진 만큼 줄 간격을 줄여 자막 위에서 끝나게
            room = max(200, 860 - y)
            sc_ = room / need
            bh, gap = max(22, int(bh * sc_)), max(8, int(gap * sc_))
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
                G.blit(f, Image.new("RGBA", (bw, bh), c + (255,)), (x0, y))
                txt = T(counter(r.get("text", str(r["value"])), (t - t0) / 0.7), 64, self.acc if hl else self.fg, "Black")
                if bw + txt.width + 30 < wmax + 220:
                    shadow(f, txt, (x0 + bw + 24, y + bh / 2), "lm", min(1, k * 2), alpha=0 if self.paper else 0.6)
                else:
                    shadow(f, txt, (x0 + bw, y - 8), "rb", min(1, k * 2), alpha=0 if self.paper else 0.6)
            y += bh + gap
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
    """종이 포스터: 왼쪽 위 제목 + 실제 지수로 만든 산(남색 + 코랄 어긋난 판 + 가로 결).
    해 · 동물 실루엣은 쓰지 않음(사용자 요청). 대신 모션:
      산이 왼→오른쪽으로 그려지며 맨 앞에 빛나는 점(파동) · 줄무늬가 천천히 흐름 · 산이 살짝 솟아오름
    ridge: {series, start, end, log, height, draw(그리는 시간 초), money(시작 금액, 만 원 → 앞 점에 잔고 표시)}
    pin: {at, label, on} 동그란 표식 + 말풍선"""

    def draw(self, f, t):
        sp = self.spec
        f.paste(paper_bg(), (0, 0))
        riso_header(f, sp, t)
        rg = sp["ridge"]
        from . import data as D
        s = D.series(rg["series"], rg.get("start"), rg.get("end")).dropna()
        raw = s.values
        v = np.log(raw) if rg.get("log") else raw
        n = 240
        idx = np.linspace(0, len(v) - 1, n)
        v = np.interp(idx, np.arange(len(v)), v)
        v = np.convolve(np.pad(v, 3, mode="edge"), np.ones(7) / 7, mode="valid")
        lo, hi = v.min(), v.max()
        nv = 0.15 + 0.85 * (v - lo) / (hi - lo + 1e-9)
        rise = (1 - G.ease_out(t / 0.9)) * 60
        x0, x1, base, hh = 0, S.W, 1000 + rise, rg.get("height", 420)
        xs = np.linspace(x0, x1, n)
        ys = base - nv * hh
        dur = rg.get("draw", 2.6)
        u = G.clamp((t - 0.15) / dur)
        kd = u * u * (3 - 2 * u)
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
        # 산 안쪽 가로 결(인쇄 줄무늬) — 천천히 아래로 흐름
        hatch = Image.new("RGBA", f.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hatch)
        off = (t * 14) % 18
        for yy in np.arange(int(ys.min()) + 12 + off, S.H, 18):
            hd.line((0, yy, S.W, yy), fill=PAPER + (34,), width=3)
        mask = Image.new("L", f.size, 0)
        ImageDraw.Draw(mask).polygon([(x, y + 24) for x, y in zip(xs[:m], ys[:m])] + [(xs[m - 1], S.H), (0, S.H)], fill=255)
        hatch.putalpha(Image.fromarray(np.minimum(np.array(hatch.getchannel("A")), np.array(mask))))
        f.alpha_composite(hatch)
        # 맨 앞 빛나는 점 + 파동 (+ 잔고)
        hx, hy = min(xs[m - 1], S.W - 30), ys[m - 1]
        d = ImageDraw.Draw(f)
        ph = (t * 0.9) % 1.0
        rr = 14 + 40 * ph
        ring = Image.new("RGBA", f.size, (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((hx - rr, hy - rr, hx + rr, hy + rr), outline=GOLD + (int(220 * (1 - ph)),), width=5)
        f.alpha_composite(ring)
        d.ellipse((hx - 18, hy - 18, hx + 18, hy + 18), fill=PAPER + (255,))
        d.ellipse((hx - 12, hy - 12, hx + 12, hy + 12), fill=GOLD + (255,))
        if rg.get("money"):
            j = int(idx[m - 1])
            val = rg["money"] * raw[j] / raw[0]
            txt = f"{val / 10000:,.1f}억 원" if val >= 10000 else f"{val:,.0f}만 원"
            lb = G.pill(txt, "Black", 40, PAPER, CORAL, pad=(22, 10), radius=26)
            G.blit(f, lb, (min(hx, S.W - 40 - lb.width / 2), hy - 34), 1, "mb")
        pin = sp.get("pin")
        if pin:
            o = G.appear(t, self.line_start(pin.get("on", 1)) + 0.3, 0.3)
            i = int(pin.get("at", 0.3) * (n - 1))
            if o > 0 and i < m:
                px, py = xs[i], ys[i]
                r = 16
                d.ellipse((px - r - 6, py - r - 6, px + r + 6, py + r + 6), fill=PAPER + (int(255 * o),))
                d.ellipse((px - r, py - r, px + r, py + r), fill=GOLD + (int(255 * o),))
                ty = py - 130 - (1 - o) * 20
                d.line((px, py - r - 6, px, ty + 40), fill=NAVY + (int(255 * o),), width=4)
                lb = G.pill(pin["label"], "ExtraBold", 36, PAPER, NAVY, pad=(22, 10), radius=26)
                G.blit(f, lb, (min(max(px, 60 + lb.width / 2), S.W - 60 - lb.width / 2), ty + 40), o, "mb")
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
        self.base(f)
        if self.paper:
            riso_header(f, sp, t)
        else:
            self.hdr(f, t, y=180, center=False)
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
        self.finish(f, t)

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
            lab = T(kp["label"], 38, self.fg, "ExtraBold", max_w=660)
            G.blit(f, lab, (180, y), o)
            y += lab.height + 6
            kc = _rc(kp.get("color"), CORAL)
            if not self.paper and kc == NAVY:
                kc = (205, 210, 222)
            vs = 132
            while True:  # 왼쪽 칸(660px)을 넘으면 줄여서 막대와 겹치지 않게
                v = riso_text(counter(kp["value"], (t - self.line_start(kp.get("on", 1))) / 0.9), vs, kc, NAVY if self.paper else (0, 0, 0), off=(5, 5))
                if v.width <= 680 or vs <= 70:
                    break
                vs -= 8
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
        kb = G.ease_out((t - t0) / 0.4)   # 막대가 나올 때 기준선도 같이 (미리 그어져 있지 않게 · EP015 피드백)
        if kb > 0:
            d = ImageDraw.Draw(f)
            d.line((x0 - 10, base, x0 - 10 + (x1 - x0 + 20) * kb, base), fill=self.fg + (160,), width=3)
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
        self.base(f)
        if sp.get("heading"):
            h = T(sp["heading"], 64, S.FG, "Black", highlight=sp.get("highlight", ""), hl_fill=Y)
            shadow(f, h, (S.W / 2, 170), "mt", G.appear(t, 0.0, 0.3))
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
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec[s].get("on", 1)), "pop", 0.35) for s in ("left", "right")]


TYPES.update({"duel": Duel})


# ════════════════════════════════════════════════════════════════
# 어두운 톤 도식화 변주 (사진 배경 · 분할 · 체크리스트 · 인물 카드 · 사람 아이콘+진행 막대)
# ════════════════════════════════════════════════════════════════
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
        self.base(f)
        if self.paper:
            riso_header(f, sp, t)
        else:
            self.hdr(f, t, y=180, center=False)
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
        self.finish(f, t)

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
            lab = T(kp["label"], 38, self.fg, "ExtraBold", max_w=660)
            G.blit(f, lab, (180, y), o)
            y += lab.height + 6
            kc = _rc(kp.get("color"), CORAL)
            if not self.paper and kc == NAVY:
                kc = (205, 210, 222)
            vs = 132
            while True:  # 왼쪽 칸(660px)을 넘으면 줄여서 막대와 겹치지 않게
                v = riso_text(counter(kp["value"], (t - self.line_start(kp.get("on", 1))) / 0.9), vs, kc, NAVY if self.paper else (0, 0, 0), off=(5, 5))
                if v.width <= 680 or vs <= 70:
                    break
                vs -= 8
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
        self.base(f)
        if sp.get("heading"):
            h = T(sp["heading"], 64, S.FG, "Black", highlight=sp.get("highlight", ""), hl_fill=Y)
            shadow(f, h, (S.W / 2, 170), "mt", G.appear(t, 0.0, 0.3))
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
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec[s].get("on", 1)), "pop", 0.35) for s in ("left", "right")]


TYPES.update({"duel": Duel})


# ════════════════════════════════════════════════════════════════
# 어두운 톤 도식화 변주 (사진 배경 · 분할 · 체크리스트 · 인물 카드 · 사람 아이콘+진행 막대)
# ════════════════════════════════════════════════════════════════
class PhotoTitle(Editorial):
    """어둡게 깐 사진 위 가운데 큰 제목 + 작은 부제 (장 전환용)"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        k = G.ease_out(t / 0.5)
        if sp.get("kicker"):
            G.blit(f, T(sp["kicker"], 40, Y, "ExtraBold"), (S.W / 2, 380), k, "mb")
        tt = T(sp["title"], sp.get("size", 150), S.FG, "Black", highlight=sp.get("highlight", ""), hl_fill=Y, align="center", line_gap=1.1)
        sc = 1.06 - 0.06 * k
        tt2 = tt.resize((int(tt.width * sc), int(tt.height * sc)), Image.BICUBIC)
        shadow(f, tt2, (S.W / 2, S.H / 2 - 20), "mm", k, blur=16, alpha=0.8)
        if sp.get("sub"):
            o = G.appear(t, self.line_start(sp.get("sub_on", 1)) + 0.3, 0.35)
            shadow(f, T(sp["sub"], 48, S.FG, "ExtraBold", highlight=sp.get("sub_hl", ""), hl_fill=Y), (S.W / 2, S.H / 2 + tt.height / 2 + 30), "mt", o)
        self.finish(f, t)


class Split(Editorial):
    """왼쪽 1/3: 흑백 사진 패널 + 큰 이름표 / 노란 세로선 / 오른쪽: 어두운 사진 위 제목.
    left: {photo, label, label_color}, right: {photo, kicker, title, sub}"""

    def draw(self, f, t):
        sp = self.spec
        L, R = sp["left"], sp["right"]
        bgR, cr2 = _photo(R["photo"], R.get("dark", 0.55), 0, R.get("gray", 0.6), tuple(R.get("focus", (0.6, 0.35))))
        f.paste(bgR, (0, 0))
        lw = 600
        card, cr1 = photo_card(L["photo"], lw, S.H, gray=1.0, focus=tuple(L.get("focus", (0.5, 0.4))))
        card = card.crop((4, 4, lw + 4, S.H + 4))
        card = Image.blend(card.convert("RGB"), Image.new("RGB", card.size, (20, 22, 30)), 0.45).convert("RGBA")
        kL = G.ease_out(t / 0.5)
        G.blit(f, card, (-(1 - kL) * 120, 0), kL)
        ImageDraw.Draw(f).rectangle((lw, 0, lw + 6, S.H), fill=Y + (255,))
        if L.get("label"):
            lab = T(L["label"], L.get("size", 110), _col(L.get("label_color"), (80, 170, 255)), "Black")
            shadow(f, lab, (lw / 2, S.H / 2 - 40), "mm", kL)
        if L.get("sub"):
            G.blit(f, T(L["sub"], 36, S.FG, "ExtraBold"), (lw / 2, S.H / 2 + 60), kL, "mt")
        o = G.appear(t, self.line_start(sp.get("on", 1)) + 0.2, 0.4)
        x = lw + 90
        y = S.H / 2 - 170
        if R.get("kicker"):
            shadow(f, T(R["kicker"], 52, S.FG, "Black"), (x, y), "lt", o)
            y += 80
        tt = T(R["title"], R.get("size", 150), Y, "Black")
        shadow(f, tt, (x - 6, y + (1 - o) * 20), "lt", o)
        y += tt.height + 10
        if R.get("sub"):
            shadow(f, T(R["sub"], 52, S.FG, "Black"), (x, y), "lt", G.appear(t, self.line_start(sp.get("sub_on", 1)) + 0.4, 0.35))
        self.spec.setdefault("credit", " · ".join(dict.fromkeys([cr1, cr2])))
        self.finish(f, t)


class Checklist(Editorial):
    """흐린 사진 배경 · 왼쪽: 작은 노란 순번 + 큰 제목 + 부제 + 체크 항목 / 오른쪽: 그림(icon: chip|emoji이름|photo카드)"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        x, y = 230, 230
        if sp.get("kicker"):
            G.blit(f, T(sp["kicker"], 44, Y, "Black"), (x, y), G.appear(t, 0.0, 0.3))
            y += 64
        tt = T(sp["title"], sp.get("title_size", 120), S.FG, "Black")
        shadow(f, tt, (x - 4, y), "lt", G.ease_out(t / 0.4))
        y += tt.height + 4
        if sp.get("sub"):
            G.blit(f, T(sp["sub"], 40, (220, 224, 232), "ExtraBold"), (x, y), G.appear(t, 0.2, 0.3))
            y += 90
        for it in sp["items"]:
            o = G.appear(t, self.line_start(it.get("on", 1)) + it.get("offset", 0), 0.3)
            if o <= 0:
                y += 96
                continue
            ck = _check(52)
            G.blit(f, ck, (x, y + 8), o)
            mw = (sp.get("icon_x", 1450) - 300 - x - 78) if sp.get("icon") else 1500
            tx = T(it["text"], 62, S.FG, "Black", highlight=it.get("highlight", ""), hl_fill=Y)
            if tx.width > mw:  # 그림과 겹치면 한 줄을 유지한 채 줄이기
                tx = tx.resize((int(mw), int(tx.height * mw / tx.width)), Image.LANCZOS)
            shadow(f, tx, (x + 78, y), "lt", o)
            y += 96
        ic = sp.get("icon")
        if ic:
            o = G.ease_out((t - self.line_start(sp.get("icon_on", 1)) - 0.2) / 0.5)
            if o > 0:
                if ic == "chip":
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
                    from thumbs import chip_icon
                    im = chip_icon(520, (118, 185, 0))
                elif ic.startswith("photo:"):
                    im, cr = photo_card(ic[6:], 520, 380, focus=tuple(sp.get("icon_focus", (0.5, 0.4))))
                    self.spec.setdefault("credit", cr)
                else:
                    im = silhouette(ic, 440, Y)
                G.blit(f, im, (sp.get("icon_x", 1450), 600 + (1 - o) * 40), o, "mm")
        self.finish(f, t)


def _check(s, c=Y):
    k = 3
    im = Image.new("RGBA", (s * k, s * k), (0, 0, 0, 0))
    ImageDraw.Draw(im).line([(s * k * 0.12, s * k * 0.55), (s * k * 0.4, s * k * 0.82), (s * k * 0.9, s * k * 0.2)], fill=c + (255,), width=int(s * k * 0.16), joint="curve")
    return im.resize((s, s), Image.LANCZOS)


class Portrait(Editorial):
    """흐린 배경 · 왼쪽 사진 카드 / 오른쪽: 노란 작은 설명 · 큰 이름 · 노란 강조 줄 · 정보 칩(2~6개)"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        card, cr = photo_card(sp["photo"], sp.get("pw", 440), sp.get("ph", 560), gray=sp.get("gray", 0.0), focus=tuple(sp.get("focus", (0.5, 0.25))))
        self.spec.setdefault("credit", cr)
        k = G.ease_out(t / 0.5)
        shadow(f, card, (230, 210 + (1 - k) * 30), "lt", k, blur=20, alpha=0.7)
        x, y = 230 + card.width + 90, 250
        if sp.get("kicker"):
            G.blit(f, T(sp["kicker"], 40, Y, "ExtraBold"), (x, y), G.appear(t, 0.15, 0.3))
            y += 62
        nm = T(sp["name"], 110, S.FG, "Black")
        shadow(f, nm, (x - 4, y), "lt", G.appear(t, 0.25, 0.35))
        y += nm.height + 16
        if sp.get("line"):
            G.blit(f, T(sp["line"], 48, S.FG, "Black", highlight=sp.get("line_hl", ""), hl_fill=Y), (x, y), G.appear(t, 0.4, 0.3))
            y += 90
        cx = x
        for j, ch in enumerate(sp.get("chips", [])):
            o = G.appear(t, self.line_start(ch.get("on", 1)) + j * 0.12 if isinstance(ch, dict) else self.line_start(1) + j * 0.12, 0.25)
            txt = ch["text"] if isinstance(ch, dict) else ch
            tx = T(txt, 40, S.FG, "ExtraBold")
            w = max(250, tx.width + 60)
            box = Image.new("RGBA", (w, 74), (0, 0, 0, 0))
            ImageDraw.Draw(box).rectangle((0, 0, w - 1, 73), fill=(16, 18, 26, 235), outline=(110, 114, 128, 255), width=2)
            box.alpha_composite(tx, ((w - tx.width) // 2, (74 - tx.height) // 2))
            if cx + w > S.W - 180:
                cx = x
                y += 92
            G.blit(f, box, (cx, y), o)
            cx += w + 18
        self.finish(f, t)


class People(Editorial):
    """사람 아이콘 n개 중 k개 노랑 + 문구 / 아래 진행 막대(값/최대) + 끝 눈금 라벨"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        n, kk = sp["n"], sp["k"]
        s = sp.get("icon", 92)
        gap = 22
        w = n * s + (n - 1) * gap
        x0, y0 = (S.W - w) / 2, 230
        t0 = self.line_start(sp.get("on", 1))
        for i in range(n):
            o = G.appear(t, t0 + i * 0.08, 0.2)
            on = i < kk and t > t0 + 0.5 + i * 0.08
            G.blit(f, _person(s, Y if on else (90, 94, 108)), (x0 + i * (s + gap), y0), o)
        if sp.get("headline"):
            shadow(f, T(sp["headline"], 76, S.FG, "Black", highlight=sp.get("headline_hl", ""), hl_fill=Y), (S.W / 2, y0 + s * 1.25 + 40), "mt", G.appear(t, t0 + 0.6, 0.3))
        b = sp.get("bar")
        if b:
            tb = self.line_start(b.get("on", 2))
            k = G.ease_out((t - tb) / 0.8)
            bx0, bx1, by = 330, S.W - 330, 690
            ImageDraw.Draw(f).rectangle((bx0, by, bx1, by + 44), fill=(90, 94, 108, 200))
            if k > 0:
                fw = (bx1 - bx0) * b["value"] / b["max"] * k
                ImageDraw.Draw(f).rectangle((bx0, by, bx0 + fw, by + 44), fill=Y + (255,))
                lab = T(b["label"], 58, S.FG, "Black", highlight=b.get("label_hl", ""), hl_fill=Y)
                shadow(f, lab, (bx0 + fw, by - 18), "rb", min(1, k * 1.5))
            ImageDraw.Draw(f).line((bx1, by - 20, bx1, by + 64), fill=(240, 240, 240, 255), width=4)
            G.blit(f, T(b["max_label"], 38, S.FG, "ExtraBold"), (bx1, by + 76), 1, "mt")
        self.finish(f, t)


TYPES.update({"photo_title": PhotoTitle, "split": Split, "checklist": Checklist, "portrait": Portrait, "people": People})


class PhotoLine(Editorial):
    """실제 사진(산 · 도시 등) 위에 실제 지수 선이 그려지는 모션 차트.
    bg: {kind: photo, file, dark}, kicker/title/highlight, line: {series, start, end, log, color, draw},
    rect: [x, y, w, h], pins: [{date, label, sub, on, color, dy}], fill: true(선 아래 반투명)"""

    def prepare(self):
        from . import data as D
        ln = self.spec["line"]
        s = D.series(ln["series"], ln.get("start"), ln.get("end")).dropna()
        self.s = s
        v = np.log(s.values) if ln.get("log") else s.values.astype(float)
        self.v = v
        self.lo, self.hi = v.min(), v.max()

    def _xy(self, i):
        x, y, w, h = self.spec.get("rect", [140, 330, 1640, 560])
        n = len(self.v)
        return x + w * i / (n - 1), y + h - h * (self.v[i] - self.lo) / (self.hi - self.lo + 1e-9)

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        x, y, w, h = sp.get("rect", [140, 330, 1640, 560])
        # 아래쪽을 살짝 어둡게 (선 · 글자 가독성)
        sh = Image.new("RGBA", f.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        for yy in range(0, S.H, 6):
            sd.rectangle((0, yy, S.W, yy + 6), fill=(4, 6, 14, int(150 * max(0, (yy - 200) / (S.H - 200)) ** 1.2)))
        f.alpha_composite(sh)
        self.hdr(f, t, y=sp.get("title_y", 120), center=False)
        ln = sp["line"]
        col = _col(ln.get("color"), Y)
        dur = ln.get("draw", 3.0)
        u = G.clamp((t - 0.3) / dur)
        kd = u * u * (3 - 2 * u)
        n = len(self.v)
        step = max(1, n // 900)
        m = max(2, int((n - 1) * kd) + 1)
        pts = [self._xy(i) for i in range(0, m, step)] + [self._xy(m - 1)]
        k = 2
        if sp.get("fill", True) and len(pts) > 1:
            lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
            ImageDraw.Draw(lay).polygon([(px * k, py * k) for px, py in pts] + [(pts[-1][0] * k, (y + h) * k), (pts[0][0] * k, (y + h) * k)],
                                        fill=col + (46,))
            f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
        glow = Image.new("RGBA", f.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).line(pts, fill=col + (170,), width=16, joint="curve")
        f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
        lay = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
        ImageDraw.Draw(lay).line([(px * k, py * k) for px, py in pts], fill=col + (255,), width=5 * k, joint="curve")
        f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
        hx, hy = pts[-1]
        ph = (t * 0.9) % 1.0
        rr = 12 + 36 * ph
        ring = Image.new("RGBA", f.size, (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((hx - rr, hy - rr, hx + rr, hy + rr), outline=col + (int(230 * (1 - ph)),), width=4)
        f.alpha_composite(ring)
        d = ImageDraw.Draw(f)
        d.ellipse((hx - 12, hy - 12, hx + 12, hy + 12), fill=(255, 255, 255, 255))
        d.ellipse((hx - 7, hy - 7, hx + 7, hy + 7), fill=col + (255,))
        for pn in sp.get("pins", []):
            i = int(np.argmin(np.abs((self.s.index - np.datetime64(pn["date"])).days)))
            if i > m - 1:
                continue
            o = G.appear(t, self.line_start(pn.get("on", 1)) + 0.2, 0.3)
            if o <= 0:
                continue
            px, py = self._xy(i)
            pc = _col(pn.get("color"), Y)
            d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=pc + (int(255 * o),), outline=(255, 255, 255, int(255 * o)), width=3)
            dy = pn.get("dy", 70)
            lb = G.pill(pn["label"], "Black", 36, (14, 16, 24), pc, pad=(20, 8))
            ty = py + dy
            d.line((px, py + (14 if dy > 0 else -14), px, ty), fill=pc + (int(220 * o),), width=3)
            G.blit(f, lb, (px, ty), o, "mt" if dy > 0 else "mb")
            if pn.get("sub"):
                st = T(pn["sub"], 26, (230, 232, 240), "SemiBold")
                G.blit(f, st, (px, ty + (lb.height + 6 if dy > 0 else 6)), o, "mt")
        self.finish(f, t)


TYPES.update({"photoline": PhotoLine})


class DepthPhoto(Editorial):
    """사진 · 명화를 깊이 지도로 입체화 → 카메라가 천천히 파고드는 다큐 장면 (engine/depth.py).
    photo, move: {zoom, dx, dy, strength}, focus, dark(0~1), gray(0~1),
    kicker/title/highlight (pos: bottom|center|top), caption(작품 설명 · 왼쪽 아래 작은 글씨), chips: [{text, on}]"""

    def prepare(self):
        from . import depth as DP
        sp = self.spec
        self.clip = DP.Parallax(sp["photo"], S.W, S.H, move=sp.get("move"), focus=tuple(sp.get("focus", (0.5, 0.5))))
        yy, xx = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
        r = np.sqrt(((xx - S.W / 2) / (S.W / 2)) ** 2 + ((yy - S.H / 2) / (S.H / 2)) ** 2)
        vg = 1 - 0.55 * np.clip((r - 0.6) / 0.8, 0, 1) ** 1.4
        pos = sp.get("pos", "bottom")
        if pos == "bottom":
            grad = 1 - 0.65 * np.clip((yy / S.H - 0.45) / 0.55, 0, 1) ** 1.3
        elif pos == "top":
            grad = 1 - 0.6 * np.clip((0.5 - yy / S.H) / 0.5, 0, 1) ** 1.3
        else:
            grad = 1 - 0.35 * np.exp(-((yy / S.H - 0.5) / 0.22) ** 2)
        self.mul = (vg * grad * (1 - sp.get("dark", 0.25)))[..., None]
        import json
        from pathlib import Path
        meta = json.loads((Path(__file__).resolve().parents[1] / "assets" / "photos" / f"{sp['photo']}.json").read_text())
        sp.setdefault("credit", meta["credit"])

    def draw(self, f, t):
        sp = self.spec
        im = np.asarray(self.clip.at(t / max(self.dur, 0.1)).convert("RGB"), np.float32)
        g = sp.get("gray", 0.15)
        if g:
            lum = (im * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
            im = im * (1 - g) + lum * g
        im = np.clip(im * self.mul, 0, 255).astype(np.uint8)
        f.paste(Image.fromarray(im, "RGB").convert("RGBA"), (0, 0))
        self.fg, self.acc, self.dim = S.FG, Y, (210, 212, 222)
        pos = sp.get("pos", "bottom")
        if sp.get("title"):
            o = G.appear(t, self.line_start(sp.get("title_on", 1)) + 0.2, 0.5)
            tt = T(sp["title"], sp.get("title_size", 96), S.FG, "Black", highlight=sp.get("highlight", ""), hl_fill=Y,
                   align="center" if pos == "center" else "left", line_gap=1.12)
            kk = T(sp["kicker"], 40, Y, "ExtraBold") if sp.get("kicker") else None
            if pos == "center":
                y = S.H / 2 - tt.height / 2
                if kk:
                    G.blit(f, kk, (S.W / 2, y - 70 + (1 - o) * 14), o, "mt")
                G.blit(f, tt, (S.W / 2, y + (1 - o) * 20), o, "mt")
            else:
                y = (S.H - 250 - tt.height) if pos == "bottom" else 170
                x = S.SAFE_X + 20
                if kk:
                    G.blit(f, kk, (x, y - 64 + (1 - o) * 14), o, "lt")
                G.blit(f, tt, (x, y + (1 - o) * 20), o, "lt")
        for i, ch in enumerate(sp.get("chips", [])):
            o = G.appear(t, self.line_start(ch.get("on", 1)) + 0.3, 0.3)
            p = G.pill(ch["text"], "ExtraBold", 34, (14, 16, 24), _col(ch.get("color"), Y), pad=(22, 10))
            G.blit(f, p, (S.W - S.SAFE_X - 20, 200 + i * 70), o, "rt")
        if sp.get("caption"):
            G.blit(f, T(sp["caption"], 26, (225, 222, 210), "SemiBold"), (S.SAFE_X + 20, S.H - 190), 0.9, "lb")
        pt = sp.get("pointer")  # {at: [원본 비율 x, y], on, label} → 깜빡이는 원 + 화살표
        if pt:
            o = G.appear(t, self.line_start(pt.get("on", 1)) + 0.2, 0.3)
            if o > 0:
                px, py = self.clip.project(pt["at"][0], pt["at"][1], t / max(self.dur, 0.1))
                ph = (t * 1.1) % 1.0
                lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
                dl = ImageDraw.Draw(lay)
                r0 = pt.get("r", 70)
                dl.ellipse((px - r0, py - r0, px + r0, py + r0), outline=Y + (int(255 * o),), width=7)
                rr = r0 + 40 * ph
                dl.ellipse((px - rr, py - rr, px + rr, py + rr), outline=Y + (int(200 * o * (1 - ph)),), width=4)
                ax, ay = px - r0 - 150, py - r0 - 120   # 왼쪽 위에서 가리키는 화살표
                dl.line((ax, ay, px - r0 * 0.75, py - r0 * 0.75), fill=Y + (int(255 * o),), width=8)
                import math as _m
                ang = _m.atan2((py - r0 * 0.75) - ay, (px - r0 * 0.75) - ax)
                tip = (px - r0 * 0.75, py - r0 * 0.75)
                for da in (2.6, -2.6):
                    dl.line((tip, (tip[0] + 34 * _m.cos(ang + da), tip[1] + 34 * _m.sin(ang + da))), fill=Y + (int(255 * o),), width=8)
                f.alpha_composite(lay)
                if pt.get("label"):
                    lb = G.pill(pt["label"], "Black", 36, (14, 16, 24), Y, pad=(20, 8))
                    G.blit(f, lb, (ax, ay - 10), o, "mb")
        credit(f, sp)
        self.draw_common(f, t)


TYPES.update({"depthphoto": DepthPhoto})


# ── 새 비교 템플릿 (EP011): 순위표 · 폭포형 손익 ─────────────────────────
class Leaderboard(Editorial):
    """순위표: 결과가 큰 순서로 1·2·3·4위 줄이 차례로 올라오고, 메달 원 + 가로 막대 + 금액.
    rows: [{label, sub, value, text, color}] (자동 정렬), on(첫 줄 등장 문장), step(줄 간격 초), unit_note"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        yy = self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        rows = sorted(sp["rows"], key=lambda r: -float(r["value"]))
        vmax = max(float(r["value"]) for r in rows) * 1.08
        t0 = self.line_start(sp.get("on", 1))
        step = sp.get("step", 0.45)
        x0, y0, rh, bw = S.SAFE_X + 40, sp.get("top", 330), sp.get("row_h", 132), 860
        medal = [(255, 204, 40), (210, 214, 224), (205, 140, 80), (120, 128, 150), (100, 108, 128)]
        n = len(rows)
        for i, r in enumerate(rows):
            # 꼴찌부터 차례로 등장 → 1위가 마지막에 '쾅'
            ti = t0 + (n - 1 - i) * step
            k = G.ease_out((t - ti) / 0.5)
            if k <= 0:
                continue
            y = y0 + i * rh + (1 - k) * 40
            c = _col(r.get("color"), S.FG)
            # 줄 배경 (얇은 유리판)
            pane = Image.new("RGBA", (S.W - 2 * S.SAFE_X, rh - 22), (255, 255, 255, 0))
            ImageDraw.Draw(pane).rounded_rectangle((0, 0, pane.width - 1, pane.height - 1), 22,
                                                   fill=(255, 255, 255, 30 if i else 46),
                                                   outline=(255, 214, 120, 150) if i == 0 else (255, 255, 255, 40), width=2)
            G.blit(f, pane, (S.SAFE_X, y), k)
            # 메달
            cx, cy, rr = x0 + 30, y + (rh - 22) / 2, 40
            md = Image.new("RGBA", (rr * 2 + 8, rr * 2 + 8), (0, 0, 0, 0))
            ImageDraw.Draw(md).ellipse((4, 4, rr * 2 + 4, rr * 2 + 4), fill=medal[min(i, 4)] + (255,))
            num = T(str(i + 1), 46, (20, 22, 30), "Black")
            md.alpha_composite(num, (md.width // 2 - num.width // 2, md.height // 2 - num.height // 2 - 2))
            G.blit(f, md, (cx, cy), k, "mm")
            lab = T(r["label"], 44, S.FG, "Black")
            G.blit(f, lab, (x0 + 100, cy - 6), k, "lb")
            if r.get("sub"):
                G.blit(f, T(r["sub"], 26, (190, 196, 212), "SemiBold"), (x0 + 102, cy + 6), k, "lt")
            # 막대 + 금액 (세어 올라감)
            kb = G.ease_out((t - ti - 0.15) / 0.7)
            w = int(bw * float(r["value"]) / vmax * max(kb, 0))
            bx = x0 + 500
            if w > 4:
                bar = Image.new("RGBA", (w, 34), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bar)
                for yb in range(34):
                    cc = tuple(min(255, int(v * (1.15 - yb / 34 * 0.4))) for v in c)
                    bd.line((0, yb, w, yb), fill=cc + (255,))
                m = Image.new("L", bar.size, 0)
                ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, 33), 17, fill=255)
                bar.putalpha(m)
                G.blit(f, bar, (bx, cy - 17), 1)
            txt = T(counter(r["text"], max(kb, 0)), 52, c if i == 0 else S.FG, "Black")
            G.blit(f, txt, (bx + max(w, 0) + 22, cy), min(1, kb * 2), "lm")
        if sp.get("note"):
            G.blit(f, T(sp["note"], 24, (180, 186, 204), "SemiBold"), (S.W - S.SAFE_X, S.H - 170), 1, "rb")
        self.finish(f, t)


class Waterfall(Editorial):
    """폭포형 손익: 출발 금액 → +/- 항목들 → 최종(순이익). steps: [{label, value(+/-), text, on}] , start: {label, value, text}, end: {label, text}"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        items = [dict(sp["start"], kind="start")] + [dict(s_, kind="step") for s_ in sp["steps"]]
        tot = float(sp["start"]["value"])
        levels = []
        cur = tot
        for it in items[1:]:
            a = cur
            cur += float(it["value"])
            levels.append((a, cur))
        items.append(dict(sp["end"], kind="end", value=cur))
        hi = max([float(sp["start"]["value"])] + [max(a, b) for a, b in levels]) * 1.12
        n = len(items)
        x0, x1 = S.SAFE_X + 40, S.W - S.SAFE_X - 40
        base, H = sp.get("base", 790), sp.get("height", 420)
        slot = (x1 - x0) / n
        bw = slot * 0.56
        yv = lambda v: base - H * v / hi
        d = ImageDraw.Draw(f)
        d.line((x0 - 20, base, x1 + 20, base), fill=(255, 255, 255, 70), width=2)
        prev_top = None
        for i, it in enumerate(items):
            on = it.get("on", 1 if i == 0 else None)
            ti = self.line_start(on) + 0.1 if on else self.line_start(sp.get("on", 1)) + 0.35 * i
            k = G.ease_out((t - ti) / 0.5)
            if k <= 0:
                continue
            cx = x0 + slot * (i + 0.5)
            if it["kind"] == "start":
                a, b, col = 0, float(it["value"]), (150, 160, 190)
            elif it["kind"] == "end":
                a, b, col = 0, float(it["value"]), Y
            else:
                a, b = levels[i - 1]
                col = (90, 200, 140) if b >= a else (236, 96, 82)
            top, bot = yv(max(a, b)), yv(min(a, b))
            hh = max(4, (bot - top) * k)
            blk = Image.new("RGBA", (int(bw), int(hh)), col + (255,))
            sh = Image.new("RGBA", (int(bw), int(hh)), (255, 255, 255, 0))
            ImageDraw.Draw(sh).rectangle((0, 0, int(bw) - 1, int(hh * 0.18)), fill=(255, 255, 255, 46))
            blk.alpha_composite(sh)
            ybar = bot - hh if (it["kind"] != "step" or b >= a) else top
            G.blit(f, blk, (cx - bw / 2, ybar), 1)
            # 연결선
            if i > 0 and prev_top is not None:
                d.line((cx - slot + bw / 2, yv(prev_top), cx - bw / 2, yv(prev_top)), fill=(255, 255, 255, 90), width=2)
            prev_top = b if it["kind"] != "start" else b
            if it["kind"] == "end":
                prev_top = b
            vt = T(it["text"], 46 if it["kind"] != "end" else 58, col if it["kind"] != "start" else S.FG, "Black")
            G.blit(f, vt, (cx, yv(max(a, b)) - 14), min(1, k * 2), "mb")
            G.blit(f, T(it["label"], 30, S.FG, "ExtraBold", max_w=int(slot - 10), align="center"), (cx, base + 16), k, "mt")
        if sp.get("note"):
            G.blit(f, T(sp["note"], 24, (180, 186, 204), "SemiBold"), (S.W - S.SAFE_X, S.H - 170), 1, "rb")
        self.finish(f, t)


TYPES.update({"leaderboard": Leaderboard, "waterfall": Waterfall})



class Matrix(Editorial):
    """비교표: 열이 차례로 채워짐. 기본은 열마다 최댓값 칸을 금색으로(best: true).
    cols: [{label, on}], rows: [{label, sub, values, texts, subs(칸 아래 작은 글씨), total(true면 합계 줄)}]
    font(칸 글자 크기) · row_h · top · label_w · best(false면 열 최댓값 강조 안 함) · note"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        cols, rows = sp["cols"], sp["rows"]
        x0, y0 = S.SAFE_X + 20, sp.get("top", 340)
        lw = sp.get("label_w", 520)
        cw = (S.W - 2 * S.SAFE_X - 40 - lw) / len(cols)
        rh = sp.get("row_h", 118)
        fs = sp.get("font", 50)
        for j, c in enumerate(cols):
            oj = G.appear(t, self.line_start(c.get("on", 1)) + 0.1, 0.35)
            cx = x0 + lw + cw * (j + 0.5)
            G.blit(f, T(c["label"], sp.get("head_font", 40), Y, "Black"), (cx, y0 - 16), max(oj, 0.35), "mb")
            vals = [float(r["values"][j]) for r in rows]
            best = max(range(len(rows)), key=lambda i: vals[i]) if sp.get("best", True) else -1
            for i, r in enumerate(rows):
                y = y0 + i * rh
                tot = r.get("total")
                if j == 0:
                    pane = Image.new("RGBA", (int(S.W - 2 * S.SAFE_X - 20), rh - 12), (255, 255, 255, 0))
                    ImageDraw.Draw(pane).rounded_rectangle((0, 0, pane.width - 1, pane.height - 1), 14,
                                                           fill=(255, 204, 40, 40) if tot else (255, 255, 255, 24))
                    G.blit(f, pane, (x0 - 10, y), 1)
                    lab = T(r["label"], int(fs * 0.84), Y if tot else S.FG, "Black")
                    cym = y + (rh - 12) / 2
                    G.blit(f, lab, (x0 + 16, cym), 1, "lm")
                    if r.get("sub"):  # 작은 설명은 같은 줄 오른쪽에 (두 줄로 쌓지 않음)
                        G.blit(f, T(r["sub"], 24, (190, 196, 212), "SemiBold"), (x0 + 30 + lab.width, cym + 2), 1, "lm")
                if oj <= 0:
                    continue
                win = i == best
                if win:
                    cell = Image.new("RGBA", (int(cw - 20), rh - 26), (0, 0, 0, 0))
                    ImageDraw.Draw(cell).rounded_rectangle((0, 0, cell.width - 1, cell.height - 1), 16, fill=Y + (235,))
                    G.blit(f, cell, (cx - cell.width / 2, y + 7), oj)
                txt_s = str(r["texts"][j])
                col = (16, 18, 28) if win else (Y if tot else ((255, 140, 130) if txt_s.startswith("-") else S.FG))
                txt = T(counter(txt_s, oj), fs if not tot else int(fs * 1.1), col, "Black")
                cy = y + (rh - 12) / 2
                if r.get("subs"):
                    G.blit(f, txt, (cx, cy - 2), oj, "mb")
                    G.blit(f, T(r["subs"][j], 24, (16, 18, 28) if win else (190, 196, 212), "SemiBold"), (cx, cy + 4), oj, "mt")
                else:
                    G.blit(f, txt, (cx, cy), oj, "mm")
        if sp.get("note"):
            G.blit(f, T(sp["note"], 24, (180, 186, 204), "SemiBold"), (S.W - S.SAFE_X, S.H - 170), 1, "rb")
        self.finish(f, t)


TYPES.update({"matrix": Matrix})



# ── EP012 벤치마킹: 인용 카드 · X 게시물 카드 · 도미노 ───────────────────
def _hl_text(text, size, weight="Black", fg=None, max_w=1500, align="center", line_gap=1.2, emph=1.12):
    """'**노랑**' · '!!빨강!!' 강조가 들어간 여러 줄 텍스트.
    2026-11-11: 글자 전반 TEXT_SCALE배 · 강조 부분은 emph배 더 크게(아래선 맞춤) · 가장 긴 줄이 max_w를 넘으면 전체를 줄여 한 줄 유지"""
    import re
    fg = fg or S.FG
    size = int(round(size * TEXT_SCALE))
    lines = text.replace("\\n", "\n").split("\n")
    rows = []
    for ln in lines:
        segs = []
        for part in re.split(r"(\*\*.+?\*\*|!!.+?!!)", ln):
            if not part:
                continue
            if part.startswith("**"):
                segs.append((part[2:-2], Y, True))
            elif part.startswith("!!"):
                segs.append((part[2:-2], (255, 96, 96), True))
            else:
                segs.append((part, fg, False))
        rows.append(segs)

    def measure(sz):
        f0, f1 = S.font(weight, sz), S.font(weight, int(sz * emph))
        return f0, f1, [sum((f1 if e else f0).getlength(t) for t, _, e in r) for r in rows]

    f0, f1, widths = measure(size)
    while max(widths) > max_w and size > 24:
        size = int(size * 0.94)
        f0, f1, widths = measure(size)
    has_emph = any(e for r in rows for *_, e in r)
    asc0, desc0 = f0.getmetrics()
    asc1, desc1 = f1.getmetrics()
    asc = asc1 if has_emph else asc0
    lh = int(size * (emph if has_emph else 1) * line_gap)
    W_ = int(max(widths)) + 8
    im = Image.new("RGBA", (W_, lh * (len(rows) - 1) + asc + max(desc0, desc1) + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (r, w) in enumerate(zip(rows, widths)):
        x = 4 if align == "left" else (W_ - w) / 2
        base = 4 + i * lh + asc   # 아래선(기준선) 맞춤
        for t_, c, e in r:
            fnt = f1 if e else f0
            d.text((x, base - (asc1 if e else asc0)), t_, font=fnt, fill=c)
            x += fnt.getlength(t_)
    return im


def _circle(img, d, ring=Y, rw=6):
    img = img.resize((d, d), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    img.putalpha(m)
    out = Image.new("RGBA", (d + rw * 2, d + rw * 2), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, d + rw * 2 - 1, d + rw * 2 - 1), fill=ring + (255,))
    out.alpha_composite(img, (rw, rw))
    return out


def _person_crop(name, focus=(0.5, 0.3), zoom=1.0):
    import json
    from pathlib import Path
    base = Path(__file__).resolve().parents[1] / "assets" / "photos"
    m = json.loads((base / f"{name}.json").read_text())
    im = Image.open(base / m["file"]).convert("RGB")
    s_ = int(min(im.size) / zoom)
    cx, cy = int(im.width * focus[0]), int(im.height * focus[1])
    x0 = max(0, min(im.width - s_, cx - s_ // 2))
    y0 = max(0, min(im.height - s_, cy - s_ // 2))
    return im.crop((x0, y0, x0 + s_, y0 + s_)), m["credit"]


class QuoteCard(DepthPhoto):
    """인물 발언 인용 (원본 영상 대신, 자유 이용 사진 + 문장).
    photo(인물 사진 · 깊이감), name, role, source(어디서 · 언제), en(원문), ko(번역 · **강조** !!빨강!!), ko_on"""

    def prepare(self):
        self.spec.setdefault("pos", "none")
        self.spec.setdefault("dark", 0.35)
        super().prepare()

    def draw(self, f, t):
        sp = self.spec
        title, sp["title"] = sp.get("title"), None
        ptr, sp["pointer"] = sp.get("pointer"), None
        super().draw(f, t)
        sp["title"], sp["pointer"] = title, ptr
        # 아래쪽 어둡게
        import numpy as np
        g = np.clip((np.arange(S.H) / S.H - 0.3) / 0.55, 0, 1) ** 1.1
        lay = Image.new("RGBA", f.size, (4, 6, 14, 0))
        lay.putalpha(Image.fromarray((np.tile(g[:, None], (1, S.W)) * 225).astype("uint8")))
        f.alpha_composite(lay)
        # 이름표 (왼쪽 위)
        o = G.appear(t, 0.15, 0.35)
        if sp.get("name"):
            face, _ = _person_crop(sp.get("face", sp["photo"]), tuple(sp.get("face_focus", (0.5, 0.3))), sp.get("face_zoom", 1.6))
            c = _circle(face, 92, Y, 4)
            G.blit(f, c, (S.SAFE_X - 40, 190), o)
            G.blit(f, T(sp["name"], 50, S.FG, "Black"), (S.SAFE_X + 80, 196), o)
            if sp.get("role"):
                G.blit(f, G.pill(sp["role"], "ExtraBold", 26, (14, 16, 24), Y, pad=(14, 5), radius=8), (S.SAFE_X + 82, 262), o)
        if sp.get("source"):
            G.blit(f, T(sp["source"], 24, (215, 218, 228), "SemiBold"), (S.SAFE_X + 82, 306), o)
        # 원문 (작게, 기울임 느낌)
        ok = G.appear(t, self.line_start(sp.get("ko_on", 1)) + 0.1, 0.4)
        if sp.get("ko"):
            ko = _hl_text(sp["ko"], sp.get("ko_size", 100), max_w=1700, line_gap=1.12)
            ky = S.H - 190 - ko.height
            if sp.get("en"):
                en = T("“" + sp["en"] + "”", 40, (232, 234, 240), "SemiBold", max_w=1600, align="center")
                G.blit(f, en, (S.W / 2, ky - 26), max(o * 0.95, 0), "mb")
            G.blit(f, ko, (S.W / 2, ky + (1 - ok) * 20), ok, "mt")
        self.draw_common(f, t)


class XPost(Editorial):
    """X(트위터) 게시물 인용 카드 — 원문 재현 + 한글 번역 강조. 실제 화면 캡처가 아니라 우리 디자인 카드.
    photo(아바타용 자유 이용 사진), name, handle, date, en(원문), ko(번역), big(원문 중 핵심 단어 크게), big_ko"""

    def draw(self, f, t):
        sp = self.spec
        bg = sp.get("bg") or {"kind": "photo", "file": sp["photo"], "dark": 0.78, "blur": 18, "gray": 0.6}
        self.spec["bg"] = bg
        self.base(f)
        k = G.ease_out(t / 0.45)
        cw = 1320
        plain = sp.get("plain", False)
        est = 190 + (T(sp["big"], 96, S.FG, "Black").height + 10 if sp.get("big") else 0)
        if sp.get("en") and not plain:
            est += T(sp["en"], 34, (210, 214, 226), "Medium", max_w=cw - 120, line_gap=1.35).height + 24
        if sp.get("ko"):
            est += _hl_text(sp["ko"], sp.get("ko_size", 76 if plain else 52), max_w=cw - 120, align="left").height + (10 if plain else 44)
        ch = max(sp.get("card_h", 0), est + 40)  # 글자 크기에 맞춰 카드 높이 자동
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, cw - 1, ch - 1), 30, fill=(16, 18, 26, 240), outline=(70, 76, 96, 255), width=2)
        face, _ = _person_crop(sp.get("face", sp["photo"]), tuple(sp.get("face_focus", (0.5, 0.3))), sp.get("face_zoom", 1.6))
        card.alpha_composite(_circle(face, 96, (60, 64, 80), 2), (44, 40))
        card.alpha_composite(T(sp["name"], 40, S.FG, "Black"), (164, 46))
        card.alpha_composite(T(f"{sp.get('handle', '')} · {sp.get('date', '')}", 28, (140, 146, 164), "SemiBold"), (166, 100))
        pf = T(sp.get("platform", "X"), 40 if sp.get("platform", "X") == "X" else 28, (230, 232, 240), "Black")
        card.alpha_composite(pf, (cw - 50 - pf.width, 50))
        y = 180
        if sp.get("big"):
            bt = T(sp["big"], 96, S.FG, "Black")
            card.alpha_composite(bt, (60, y)); y += bt.height + 10
        if sp.get("en") and not plain:
            en = T(sp["en"], 34, (210, 214, 226), "Medium", max_w=cw - 120, line_gap=1.35)
            card.alpha_composite(en, (60, y)); y += en.height + 24
        ok = G.appear(t, self.line_start(sp.get("ko_on", 1)) + 0.15, 0.35)
        if sp.get("ko") and ok > 0:
            if not plain:
                lab = G.pill("번역", "ExtraBold", 24, (14, 16, 24), Y, pad=(12, 4), radius=8)
                card.alpha_composite(lab, (60, y))
            ko = _hl_text(sp["ko"], sp.get("ko_size", 76 if plain else 52), max_w=cw - 120, align="left")
            card.alpha_composite(G.with_opacity(ko, ok), (60, y + (10 if plain else 44)))
        card = card.rotate((1 - k) * 3, resample=Image.BICUBIC, expand=True)
        G.blit(f, card, (S.W / 2, sp.get("y", 470) + (1 - k) * 40), k, "mm")
        credit(f, sp)
        self.draw_common(f, t)


class Domino(Editorial):
    """도미노: 막대가 문장마다 하나씩 오른쪽으로 쓰러지며 아래에 하락률. items: [{label, text, on, delay}], headline"""

    def draw(self, f, t):
        import math
        sp = self.spec
        self.base(f)
        if sp.get("headline"):
            G.blit(f, T(sp["headline"], 52, S.FG, "Black"), (S.W / 2, 150), 1, "mt")
        items = sp["items"]
        n = len(items)
        gap = sp.get("gap", 330)
        x0 = S.W / 2 - gap * (n - 1) / 2
        base = sp.get("base", 700)
        bw, bh = 90, 340
        k2 = 2
        lay = Image.new("RGBA", (S.W * k2, S.H * k2), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.line(((x0 - 200) * k2, base * k2, (x0 + gap * (n - 1) + 260) * k2, base * k2), fill=(255, 255, 255, 90), width=3 * k2)
        texts = []
        for i, it in enumerate(items):
            ti = self.line_start(it.get("on", 1)) + it.get("delay", 0.0)
            k = G.clamp((t - ti) / 0.55)
            k = k * k * (3 - 2 * k)
            th = math.radians(68 * k)
            cx = x0 + gap * i
            px, py = cx + bw / 2, base   # 오른쪽 아래 모서리가 축
            col = (236, 96, 96) if k > 0.02 else (214, 218, 230)
            pts = []
            for (x, y) in ((-bw, 0), (0, 0), (0, -bh), (-bw, -bh)):
                xr = x * math.cos(th) - y * math.sin(th)
                yr = x * math.sin(th) + y * math.cos(th)
                pts.append(((px + xr) * k2, (py + yr) * k2))
            d.polygon(pts, fill=col + (255,))
            hl = [pts[3], pts[2], ((pts[2][0] * 0.75 + pts[1][0] * 0.25), (pts[2][1] * 0.75 + pts[1][1] * 0.25)),
                  ((pts[3][0] * 0.75 + pts[0][0] * 0.25), (pts[3][1] * 0.75 + pts[0][1] * 0.25))]
            d.polygon(hl, fill=(255, 255, 255, 60))
            texts.append((cx, it, k))
        f.alpha_composite(lay.resize((S.W, S.H), Image.LANCZOS))
        for cx, it, k in texts:
            G.blit(f, T(it["label"], 44, S.FG, "ExtraBold"), (cx, base + 24), 1, "mt")
            if k > 0.02:
                G.blit(f, T(it["text"], 76, (255, 96, 96), "Black"), (cx, base + 88), min(1, k * 2), "mt")
        credit(f, sp)
        self.draw_common(f, t)


TYPES.update({"saying": QuoteCard, "xpost": XPost, "domino": Domino})



class DropCards(Editorial):
    """급락 카드: 종목 카드가 문장마다 아래로 '툭' 떨어지며 빨간 화살표와 하락률이 세어 내려감.
    items: [{label, value(음수 %), text, on, delay}], headline, scale(낙폭 픽셀 배율)"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        if sp.get("headline"):
            G.blit(f, T(sp["headline"], 56, S.FG, "Black"), (S.W / 2, 140), 1, "mt")
        items = sp["items"]
        n = len(items)
        cw, ch, gap = 330, 300, 40
        x0 = S.W / 2 - (n * cw + (n - 1) * gap) / 2
        top = sp.get("top", 270)
        scale = sp.get("scale", 9)
        for i, it in enumerate(items):
            ti = self.line_start(it.get("on", 1)) + it.get("delay", 0.0)
            k = G.ease_out(G.clamp((t - ti) / 0.6))
            hit = k > 0.01
            drop = min(abs(float(it["value"])) * scale, 300) * k
            x = x0 + i * (cw + gap)
            y = top + drop
            card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            d = ImageDraw.Draw(card)
            edge = (236, 96, 96) if hit else (90, 100, 130)
            d.rounded_rectangle((0, 0, cw - 1, ch - 1), 26, fill=(22, 26, 40, 245), outline=edge + (255,), width=4)
            nm = T(it["label"], 46, S.FG, "Black")
            card.alpha_composite(nm, ((cw - nm.width) // 2, 34))
            # 화살표 + 숫자
            if hit:
                ar = Image.new("RGBA", (90, 90), (0, 0, 0, 0))
                ImageDraw.Draw(ar).polygon([(10, 20), (80, 20), (45, 80)], fill=(236, 96, 96, 255))
                card.alpha_composite(ar, ((cw - 90) // 2, 104))
                val = counter(it["text"], k)
                vt = T(val, 70, (255, 110, 110), "Black")
                card.alpha_composite(vt, ((cw - vt.width) // 2, 196))
            else:
                dash = T("—", 70, (120, 128, 150), "Black")
                card.alpha_composite(dash, ((cw - dash.width) // 2, 150))
            # 원래 자리 점선
            if hit:
                gd = ImageDraw.Draw(f)
                for xx in range(int(x), int(x + cw), 22):
                    gd.line((xx, top, xx + 10, top), fill=(255, 255, 255, 80), width=3)
            sh, (dx, dy) = None, (0, 0)
            G.blit(f, card, (x, y), 1)
        credit(f, sp)
        self.draw_common(f, t)


TYPES.update({"dropcards": DropCards})



# ── 문답 (EP013 피드백 v2): 화보형 — 왼쪽 인물(누끼 · 듀오톤) + 오른쪽 QUESTION / ANSWER + 작은 도식 ──────
@lru_cache(maxsize=8)
def _figure(name, h, warm=(214, 172, 96), cool=(16, 22, 44)):
    from pathlib import Path
    im = Image.open(Path(__file__).resolve().parents[1] / "assets/people" / f"{name}.png").convert("RGBA")
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    g = np.asarray(im.convert("L"), np.float32) / 255
    g = np.clip((g - 0.08) / 0.8, 0, 1) ** 0.85
    c0, c1 = np.array(cool, np.float32), np.array(warm, np.float32)
    rgb = (c0[None, None] * (1 - g[..., None]) + c1[None, None] * g[..., None]).astype(np.uint8)
    out = Image.fromarray(rgb, "RGB").convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


@lru_cache(maxsize=8)
def _visual_src(name):
    from pathlib import Path
    d = Path(__file__).resolve().parents[1] / "assets/photos"
    p = next((d / f"{name}{e}" for e in (".png", ".jpg", ".jpeg") if (d / f"{name}{e}").exists()))
    return Image.open(p).convert("RGB")


def _visual_card(name, t, w=780, h=560):
    """둥근 모서리 그림 카드 + 그림자 · 천천히 다가감(켄 번스)"""
    src = _visual_src(name)
    z = 1.0 + 0.06 * min(1.0, t / 6)
    sc = max(w / src.width, h / src.height) * z
    im = src.resize((int(src.width * sc), int(src.height * sc)), Image.BILINEAR)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((x0, y0, x0 + w, y0 + h)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=255)
    im.putalpha(m)
    out = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 52, w + 40, h + 52), 28, fill=(0, 0, 0, 150))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    out.alpha_composite(im, (40, 40))
    return out


class QA(Editorial):
    """문답(화보형). figure(assets/people/*.png 누끼, 기본 thinker_cut), q, a(**노랑** !!빨강!!), a_on, sub,
    compare: [{label, value, text, color}] (답 아래 가로 막대 도식), vmax"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        # 스포트라이트
        gl = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse((-120, 160, 980, 1200), fill=(214, 172, 96, 46))
        f.alpha_composite(gl.filter(ImageFilter.GaussianBlur(160)))
        k = G.ease_out(t / 0.6)
        if sp.get("visual"):   # 2026-11-14: 사람 대신 그림 카드(AI 디오라마 · 사진) — 한 장면에 그림 하나 + 짧은 문답
            fig = None
            ph = _visual_card(sp["visual"], t)
            G.blit(f, ph, (470, 540 + (1 - k) * 30), k, "mm")
        else:
            fig = _figure(sp.get("figure", "thinker_cut"), sp.get("figure_h", 900))
        if fig is None:
            pass
        elif fig.width > fig.height * 1.6:   # 배 · 차처럼 옆으로 긴 누끼는 왼쪽 가운데에 크게 (바닥에 붙이면 자막에 가림)
            if fig.width > 820:
                fig = fig.resize((820, int(fig.height * 820 / fig.width)), Image.LANCZOS)
            G.blit(f, fig, (440 - (1 - k) * 40, 520), k, "mm")
        else:
            G.blit(f, fig, (430 - (1 - k) * 40, S.H + 10), k, "mb")
        x, y = 880, sp.get("top", 170)
        lw = 860
        # 글자 크기에 맞춰 전체 높이를 재고, 자막(약 940) 위에서 끝나도록 위로 당김
        if sp.get("compare"):  # 도식(막대)까지 들어가면 글자를 한 단계 낮춰 전체가 자막 위에 들어오게
            sp.setdefault("q_size", 64)
            sp.setdefault("a_size", 56)
        _q = _hl_text(sp["q"], sp.get("q_size", 74), max_w=lw, align="left", line_gap=1.22)
        _a = _hl_text(sp["a"], sp.get("a_size", 64), max_w=lw, align="left", line_gap=1.22)
        step = 70
        _h = 60 + _q.height + 60 + 56 + _a.height + 30 + len(sp.get("compare", [])) * step + (60 if sp.get("sub") else 0)
        y = max(130, min(y, 790 - _h))
        G.blit(f, T("QUESTION", 30, (214, 172, 96), "ExtraBold"), (x, y), k)
        ImageDraw.Draw(f).line((x + 190, y + 18, x + 190 + 120 * k, y + 18), fill=(214, 172, 96, 255), width=2)
        q = _hl_text(sp["q"], sp.get("q_size", 74), max_w=lw, align="left", line_gap=1.22)
        shadow(f, q, (x, y + 60 + (1 - k) * 20), "lt", k)
        y2 = y + 60 + q.height + 60
        a0 = self.line_start(sp.get("a_on", 2))
        ka = G.ease_out((t - a0) / 0.5)
        if ka > 0:
            ImageDraw.Draw(f).line((x, y2 - 30, x + lw * ka, y2 - 30), fill=(70, 78, 100, 255), width=2)
            G.blit(f, T("ANSWER", 30, (110, 214, 176), "ExtraBold"), (x, y2), ka)
            a = _hl_text(sp["a"], sp.get("a_size", 64), max_w=lw, align="left", line_gap=1.22)
            shadow(f, a, (x, y2 + 56 + (1 - ka) * 20), "lt", ka)
            yy = y2 + 56 + a.height + 34
            if sp.get("sub"):
                st = T(sp["sub"], 36, (190, 196, 210), "Medium", max_w=lw)
                G.blit(f, st, (x, yy), G.appear(t, a0 + 0.4, 0.4))
                yy += st.height + 30
            cmp_ = sp.get("compare")
            if cmp_:
                vmax = sp.get("vmax") or max(abs(c["value"]) for c in cmp_)
                for n, c in enumerate(cmp_):
                    kc = G.ease_out((t - a0 - 0.5 - n * 0.35) / 0.6)
                    if kc <= 0:
                        continue
                    col = _col(c.get("color"), (190, 196, 210))
                    G.blit(f, T(c["label"], 32, (200, 206, 220), "SemiBold"), (x, yy), kc)
                    bw = int((lw - 220) * abs(c["value"]) / vmax * kc)
                    ImageDraw.Draw(f).rounded_rectangle((x, yy + 44, x + max(bw, 6), yy + 44 + 26), 6, fill=col + (255,))
                    G.blit(f, T(c.get("text", ""), 40, col, "Black"), (x + max(bw, 6) + 18, yy + 57), kc, "lm")
                    yy += step
        if sp.get("visual"):
            import json as _j
            from pathlib import Path as _P
            src = _P(__file__).resolve().parents[1] / "assets/photos" / (sp["visual"] + ".json")
            if src.exists():
                self.spec.setdefault("credit", _j.loads(src.read_text()).get("credit", ""))
        elif sp.get("figure_credit", True):
            fn = sp.get("figure", "thinker_cut")
            if fn == "thinker_cut":
                self.spec.setdefault("credit", "조각: 오귀스트 로댕 '생각하는 사람' · 사진 AndrewHorne, Public domain (Wikimedia Commons)")
            else:   # 다른 누끼는 원본 사진의 출처 (assets/photos/<이름>.json)
                import json as _j
                from pathlib import Path as _P
                src = _P(__file__).resolve().parents[1] / "assets/photos" / (fn.replace("_cut", "") + ".json")
                if src.exists():
                    self.spec.setdefault("credit", _j.loads(src.read_text()).get("credit", ""))
        self.finish(f, t)


def _badge(ch, bg, fg, s=118):
    k = 3
    im = Image.new("RGBA", (s * k, s * k), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, s * k - 1, s * k - 1), 28 * k, fill=bg + (255,))
    im = im.resize((s, s), Image.LANCZOS)
    G.blit(im, T(ch, 84, fg, "Black"), (s / 2, s / 2 - 4), 1, "mm")
    return im


# ── 원리 도식 (EP013 피드백): 노드(입체 블록) 사이로 전기가 흐르는 그림 + 아래 수요 그래프 ──────
def _iso_box(d, cx, by, w, dp, h, top, left, right, k=2):
    """cx, by = 바닥 앞 꼭짓점. w(오른쪽 방향 길이) · dp(왼쪽 방향 길이) · h(높이)"""
    c, sn = 0.866, 0.5
    A = (cx, by)
    B = (cx + w * c, by - w * sn)
    D = (cx - dp * c, by - dp * sn)
    Cc = (B[0] - dp * c, B[1] - dp * sn)
    up = lambda p: (p[0], p[1] - h)
    d.polygon([D, A, up(A), up(D)], fill=left)
    d.polygon([A, B, up(B), up(A)], fill=right)
    d.polygon([up(A), up(B), up(Cc), up(D)], fill=top)
    return A, B, Cc, D


@lru_cache(maxsize=4)
def _flow_layer(key):
    nodes = json.loads(key)
    k = 2
    L = Image.new("RGBA", (S.W * k, S.H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    for n in nodes:
        cx, by = n["x"] * k, n.get("y", 560) * k
        kind = n["kind"]
        if kind == "grid":  # 발전소 + 송전탑
            _iso_box(d, cx - 40 * k, by, 150 * k, 120 * k, 70 * k, (120, 130, 150), (70, 78, 96), (92, 100, 120))
            _iso_box(d, cx + 40 * k, by - 120 * k, 40 * k, 40 * k, 120 * k, (150, 156, 170), (90, 96, 112), (110, 116, 132))
            px, py = cx - 150 * k, by - 40 * k  # 송전탑
            for a, b in (((px - 40 * k, py), (px, py - 210 * k)), ((px + 40 * k, py), (px, py - 210 * k)),
                         ((px - 70 * k, py - 150 * k), (px + 70 * k, py - 150 * k)), ((px - 55 * k, py - 110 * k), (px + 55 * k, py - 110 * k))):
                d.line([a, b], fill=(200, 205, 215), width=6 * k)
            bolt = [(cx + 10 * k, by - 200 * k), (cx - 30 * k, by - 120 * k), (cx + 5 * k, by - 120 * k), (cx - 25 * k, by - 50 * k), (cx + 45 * k, by - 140 * k), (cx + 10 * k, by - 140 * k)]
            d.polygon(bolt, fill=Y + (255,))
        elif kind == "battery":  # ESS 컨테이너 2개
            for i, off in enumerate((-150, 20)):
                A, B, Cc, D = _iso_box(d, cx + off * k, by - i * 10 * k, 170 * k, 80 * k, 100 * k,
                                       (226, 232, 240), (150, 160, 176), (190, 198, 212))
                for j in range(6):  # 옆면 줄무늬
                    t0 = (j + 1) / 7
                    xa = A[0] + (B[0] - A[0]) * t0
                    ya = A[1] + (B[1] - A[1]) * t0
                    d.line([(xa, ya - 12 * k), (xa, ya - 98 * k)], fill=(150, 160, 176), width=3 * k)
            bx, byy = cx - 10 * k, by - 235 * k  # 배터리 기호
            d.rounded_rectangle((bx - 70 * k, byy - 34 * k, bx + 70 * k, byy + 34 * k), 12 * k, outline=(90, 220, 170), width=7 * k)
            d.rectangle((bx + 72 * k, byy - 14 * k, bx + 84 * k, byy + 14 * k), fill=(90, 220, 170))
            d.rectangle((bx - 58 * k, byy - 22 * k, bx + 30 * k, byy + 22 * k), fill=(90, 220, 170))
        elif kind == "datacenter":  # 서버 랙 3개
            for i in range(3):
                A, B, Cc, D = _iso_box(d, cx - 100 * k + i * 75 * k, by - i * 30 * k, 55 * k, 80 * k, 170 * k,
                                       (70, 80, 110), (30, 36, 56), (44, 52, 78))
                for j in range(7):
                    yy = A[1] - 20 * k - j * 21 * k
                    d.line([(A[0] + 8 * k, yy - 4 * k), (B[0] - 8 * k, yy - 4 * k - (B[1] - A[1]) * -0.0)], fill=(60, 70, 96), width=2 * k)
                    d.ellipse((A[0] + 10 * k, yy - 10 * k, A[0] + 18 * k, yy - 2 * k), fill=(90, 220, 170) if (i + j) % 3 else Y)
        elif kind == "salary":  # 지폐 다발 3묶음 (EP014)
            for i, (ox, oy) in enumerate(((-120, 0), (10, -10), (-55, -70))):
                A, B, Cc, D = _iso_box(d, cx + ox * k, by + oy * k, 150 * k, 80 * k, 46 * k,
                                       (150, 214, 160), (70, 140, 92), (100, 176, 120))
                mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2  # 띠지
                d.polygon([(mx - 16 * k, my - 8 * k), (mx + 16 * k, my - 26 * k), (mx + 16 * k, my - 72 * k), (mx - 16 * k, my - 54 * k)], fill=(240, 236, 220))
            d.ellipse((cx - 10 * k, by - 250 * k, cx + 70 * k, by - 170 * k), fill=Y + (255,))
            d.text((cx + 30 * k, by - 210 * k), "₩", fill=(120, 90, 10), anchor="mm", font=S.font("Black", 54 * k))
        elif kind == "fund":  # 기금: 기둥 있는 금고 건물
            _iso_box(d, cx - 30 * k, by, 240 * k, 140 * k, 30 * k, (220, 224, 236), (130, 136, 156), (170, 176, 196))
            for j in range(5):
                tx = cx - 30 * k + j * 46 * k * 0.866 + 20 * k
                ty = by - 30 * k - j * 46 * k * 0.5 - 10 * k
                d.rectangle((tx - 9 * k, ty - 150 * k, tx + 9 * k, ty), fill=(236, 238, 246))
                d.rectangle((tx + 3 * k, ty - 150 * k, tx + 9 * k, ty), fill=(176, 182, 200))
            A, B, Cc, D = _iso_box(d, cx - 30 * k, by - 185 * k, 240 * k, 140 * k, 26 * k, (236, 238, 246), (140, 146, 166), (186, 192, 210))
            top = [(A[0], A[1] - 26 * k), (B[0], B[1] - 26 * k), (Cc[0], Cc[1] - 26 * k), (D[0], D[1] - 26 * k)]
            pk = ((top[0][0] + top[2][0]) / 2, (top[0][1] + top[2][1]) / 2 - 90 * k)
            d.polygon([top[0], top[1], pk], fill=(200, 206, 222))
            d.polygon([top[3], top[0], pk], fill=(150, 156, 176))
            d.polygon([top[1], top[2], pk], fill=(176, 182, 200))
        elif kind == "pension":  # 매달 받는 동전 기둥 (달력 위)
            _iso_box(d, cx - 60 * k, by, 200 * k, 150 * k, 18 * k, (236, 240, 248), (150, 156, 176), (190, 196, 214))
            for i, (ox, n_) in enumerate(((-90, 3), (-20, 5), (50, 7), (120, 9))):
                x_, y_ = cx + ox * k, by - 40 * k - i * 12 * k
                for j in range(n_):
                    yy = y_ - j * 16 * k
                    d.ellipse((x_ - 34 * k, yy - 12 * k, x_ + 34 * k, yy + 12 * k), fill=(196, 150, 30))
                    d.ellipse((x_ - 34 * k, yy - 18 * k, x_ + 34 * k, yy + 6 * k), fill=Y + (255,))
            d.polygon([(cx + 150 * k, by - 260 * k), (cx + 110 * k, by - 225 * k), (cx + 135 * k, by - 225 * k), (cx + 135 * k, by - 180 * k),
                       (cx + 165 * k, by - 180 * k), (cx + 165 * k, by - 225 * k), (cx + 190 * k, by - 225 * k)], fill=(90, 220, 170))
    return L.resize((S.W, S.H), Image.LANCZOS)


class Flow(Editorial):
    """원리 도식. nodes: [{kind: grid|battery|datacenter, x, y, label, sub, on}], links: [{a, b, label, on, color}]
    chart: {on, limit, label_over, label_under, title} — 아래에 '전기 수요(출렁임) vs 전력망 한도' 그래프, 넘치는 부분은 배터리가 메움"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 120))
        nodes = sp["nodes"]
        key = json.dumps([{kk: n[kk] for kk in ("kind", "x", "y") if kk in n} for n in nodes])
        lay = _flow_layer(key)
        # 노드별 등장: 해당 영역만 잘라 보이기
        for n in nodes:
            o = G.ease_out((t - self.line_start(n.get("on", 1)) - n.get("offset", 0)) / 0.45)
            if o <= 0:
                continue
            x0, y0 = int(n["x"] - 260), int(n.get("y", 560) - 330)
            crop = lay.crop((x0, y0, x0 + 520, y0 + 400))
            G.blit(f, crop, (x0, y0 + (1 - o) * 30), o)
            lb = G.pill(n["label"], "Black", 44, (14, 16, 24), Y if n.get("hl") else (236, 240, 248), pad=(22, 8), radius=12)
            G.blit(f, lb, (n["x"], n.get("y", 560) + 50), o, "mt")
            if n.get("sub"):
                G.blit(f, T(n["sub"], 32, (200, 206, 220), "SemiBold"), (n["x"], n.get("y", 560) + 125), o, "mt")
        for ln in sp.get("links", []):
            o = G.ease_out((t - self.line_start(ln.get("on", 1)) - ln.get("offset", 0)) / 0.4)
            if o <= 0:
                continue
            a = next(n for n in nodes if n["label"] == ln["a"])
            b = next(n for n in nodes if n["label"] == ln["b"])
            xa, xb = a["x"] + ln.get("pad_a", 190), b["x"] - ln.get("pad_b", 200)
            yy = (a.get("y", 560) + b.get("y", 560)) / 2 - ln.get("dy", 60)
            col = _col(ln.get("color"), (90, 220, 170))
            ov = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
            dd = ImageDraw.Draw(ov)
            xe = xa + (xb - xa) * o
            dd.line([(xa, yy), (xe, yy)], fill=col + (120,), width=6)
            if o >= 1:
                dd.polygon([(xb, yy), (xb - 28, yy - 18), (xb - 28, yy + 18)], fill=col + (255,))
                for j in range(4):  # 흐르는 전기
                    ph = ((t * 0.7 + j / 4) % 1.0)
                    px = xa + (xb - xa - 30) * ph
                    dd.ellipse((px - 11, yy - 11, px + 11, yy + 11), fill=col + (255,))
            f.alpha_composite(ov)
            if ln.get("label"):
                G.blit(f, T(ln["label"], 34, col, "ExtraBold"), ((xa + xb) / 2, yy - 24), o, "mb")
        ch = sp.get("chart")
        if ch:
            self._chart(f, t, ch)
        self.finish(f, t)

    def _chart(self, f, t, ch):
        t0 = self.line_start(ch.get("on", 3))
        o = G.ease_out((t - t0) / 0.5)
        if o <= 0:
            return
        x0, y0, w, h = 300, ch.get("y", 790), 1320, ch.get("h", 130)
        n = 240
        rng = np.random.default_rng(7)
        xs = np.linspace(0, 1, n)
        v = 0.42 + 0.06 * np.sin(xs * 9) + 0.03 * np.sin(xs * 37)
        for c in (0.15, 0.38, 0.62, 0.85):  # AI 계산이 몰리는 순간
            v += 0.48 * np.exp(-((xs - c) / 0.03) ** 2)
        v = np.clip(v, 0.2, 0.97)
        lim = ch.get("limit", 0.66)
        kk = min(1, max(0, (t - t0) / ch.get("dur", 2.4)))
        m = max(2, int(n * kk))
        X = x0 + xs * w
        Yv = y0 + h - v * h
        ly = y0 + h - lim * h
        ov = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rectangle((x0 - 20, y0 - 64, x0 + w + 20, y0 + h + 16), fill=(10, 14, 26, 190))
        for i in range(m - 1):
            if v[i] > lim:
                d.polygon([(X[i], ly), (X[i], Yv[i]), (X[i + 1], Yv[i + 1]), (X[i + 1], ly)], fill=(90, 220, 170, 200))
            else:
                d.polygon([(X[i], Yv[i]), (X[i], ly), (X[i + 1], ly), (X[i + 1], Yv[i + 1])], fill=Y + (45,))
        d.line([(x0, ly), (x0 + w, ly)], fill=(240, 84, 84, 255), width=4)
        d.line(list(zip(X[:m], Yv[:m])), fill=(236, 240, 248, 255), width=5, joint="curve")
        f.alpha_composite(G.with_opacity(ov, o))
        G.blit(f, T(ch.get("title", "AI 데이터센터 전기 사용량"), 34, S.FG, "Black"), (x0, y0 - 50), o)
        G.blit(f, T(ch.get("limit_label", "전력망 한도"), 28, (240, 84, 84), "ExtraBold"), (x0 + 6, ly - 6), o, "lb")
        if kk > 0.6:
            o2 = G.appear(t, t0 + ch.get("dur", 2.4) * 0.6, 0.4)
            p1 = G.pill(ch.get("label_over", "넘치는 순간 → 배터리가 메움"), "Black", 30, (10, 30, 24), (90, 220, 170), pad=(14, 5), radius=10)
            p2 = G.pill(ch.get("label_under", "남는 전기 → 배터리 충전"), "Black", 30, (14, 16, 24), Y, pad=(14, 5), radius=10)
            G.blit(f, p2, (x0 + w, y0 - 52), o2, "rt")
            G.blit(f, p1, (x0 + w - p2.width - 16, y0 - 52), o2, "rt")


TYPES.update({"qa": QA, "flow": Flow})


# ── 논문 하이라이트 (2026-11-11 사용자 요청): 원문 일부를 재구성한 논문 지면 + 형광펜 + 확대 + 번역 카드 + 빨간 강조 ──────
@lru_cache(maxsize=8)
def _paper_page(key):
    sp = json.loads(key)
    pw, ph = 980, 1300
    pg = Image.new("RGBA", (pw, ph), (246, 244, 238, 255))
    d = ImageDraw.Draw(pg)
    x, y = 70, 60
    G.blit(pg, T(sp.get("journal", ""), 24, (110, 110, 120), "SemiBold"), (x, y))
    G.blit(pg, T(str(sp.get("year", "")), 24, (110, 110, 120), "SemiBold"), (pw - 70, y), 1, "rt")
    y += 60
    tt = T(sp["title"], 40, (24, 26, 34), "ExtraBold", max_w=pw - 140, line_gap=1.25)
    G.blit(pg, tt, (x, y))
    y += tt.height + 22
    G.blit(pg, T(sp.get("authors", ""), 24, (90, 92, 104), "Medium", max_w=pw - 140), (x, y))
    y += 70
    d.line((x, y, pw - 70, y), fill=(200, 196, 186, 255), width=2)
    y += 30
    G.blit(pg, T(sp.get("section") or "Abstract", 28, (24, 26, 34), "ExtraBold"), (x, y))
    y += 56
    rng = np.random.default_rng(len(sp["quote_en"]))
    hl_y = None
    for i in range(22):
        if i == (sp.get("quote_row") or 6):
            q = T(sp["quote_en"], 27, (24, 26, 34), "SemiBold", max_w=pw - 140, line_gap=1.45)
            hl_y = (y, q.width, q.height)
            G.blit(pg, q, (x, y))
            y += q.height + 18
            continue
        wl = int((pw - 140) * (0.55 + 0.45 * rng.random())) if i % 5 != 4 else int((pw - 140) * 0.4)
        d.rounded_rectangle((x, y + 8, x + wl, y + 20), 6, fill=(206, 204, 198, 255))
        y += 36
        if y > ph - 60:
            break
    return pg, hl_y


class PaperQuote(Editorial):
    """논문 하이라이트. journal, year, title(원제), authors, quote_en(인용 문장 그대로), quote_ko(번역, **강조**),
    red(빨간 강조 문구 — 'stamp'는 공통 장치 이름이라 피함), on: [형광펜, 번역 카드, 강조] 등장 문장, note(출처 표기)"""

    def draw(self, f, t):
        sp = self.spec
        sp.setdefault("bg", {"kind": "motion", "style": "particles", "tone": "navy", "dark": 0.2})
        self.base(f)
        key = json.dumps({k: sp.get(k) for k in ("journal", "year", "title", "authors", "quote_en", "quote_row", "section")},
                         ensure_ascii=False, sort_keys=True)
        pg, (qy, qw, qh) = _paper_page(key)
        on = sp.get("on", [1, 2, 3])
        t_hl, t_card, t_st = (self.line_start(o) for o in (on + [on[-1]] * 3)[:3])
        # 형광펜이 문장을 따라 칠해짐
        k = G.ease_out(G.clamp((t - t_hl - 0.2) / 1.0))
        page = pg.copy()
        if k > 0:
            hl = Image.new("RGBA", page.size, (0, 0, 0, 0))
            ImageDraw.Draw(hl).rectangle((64, qy - 4, 64 + (qw + 12) * k, qy + qh + 2), fill=(255, 214, 60, 120))
            page = Image.alpha_composite(page, hl)
        # 카메라: 지면 전체 → 인용 문장 쪽으로 확대
        z = 1.0 + 0.45 * G.ease_out(G.clamp((t - t_hl) / 2.2))
        sc = 0.78 * z
        pw, ph = int(page.width * sc), int(page.height * sc)
        im = page.resize((pw, ph), Image.LANCZOS).rotate(-1.5, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
        fx = sp.get("page_x", 520)
        e = (z - 1) / 0.45
        cy = (qy + qh / 2) * sc
        y0 = 150 * (1 - e) + (S.H * 0.5 - cy) * e
        k0 = G.ease_out(G.clamp(t / 0.5))
        shadow(f, im, (fx, y0 + (1 - k0) * 60), "mt", k0, blur=30, alpha=0.7)
        # 번역 카드
        kc = G.ease_out(G.clamp((t - t_card) / 0.4))
        if kc > 0:
            cw = 780
            en = T(sp["quote_en"], 26, (200, 206, 220), "Medium", max_w=cw - 80, line_gap=1.35)
            ko = _hl_text(sp["quote_ko"], sp.get("ko_size", 48), max_w=cw - 80, align="left", line_gap=1.25)
            chh = en.height + ko.height + 120
            card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
            ImageDraw.Draw(card).rounded_rectangle((0, 0, cw - 1, chh - 1), 26, fill=(14, 16, 26, 238), outline=(255, 214, 60, 255), width=3)
            card.alpha_composite(en, (40, 36))
            card.alpha_composite(ko, (40, 36 + en.height + 34))
            shadow(f, card, (S.W - 80, 260 + (1 - kc) * 30), "rt", kc, blur=24, alpha=0.7)
        ks = G.ease_out(G.clamp((t - t_st - 0.3) / 0.3))
        if ks > 0 and sp.get("red"):
            st = G.pill(sp["red"], "Black", 64, (255, 255, 255), (220, 40, 40), pad=(30, 12), radius=10)
            st = st.rotate(-3, expand=True, resample=Image.BICUBIC)
            shadow(f, st, (S.W - 120, 750 + (1 - ks) * 20), "rt", ks, blur=16, alpha=0.6)
        G.blit(f, T(sp.get("note", "논문 원문 일부를 재구성한 화면 · 인용 문장만 원문 그대로"), 22, (170, 176, 192), "SemiBold"),
               (S.W - 80, 205), 1, "rt")
        self.finish(f, t)

    def extra_sfx(self):
        on = self.spec.get("on", [1, 2, 3])
        on = (on + [on[-1]] * 3)[:3]
        return [(self.line_start(on[0]) + 0.2, "accent", 0.4), (self.line_start(on[1]), "reveal", 0.5),
                (self.line_start(on[2]) + 0.3, "accent_low", 0.55)]


TYPES.update({"paper": PaperQuote})


class Pyramid(Editorial):
    """노후 소득 피라미드(2026-11-12 사용자 요청: 사다리 · 피라미드로 쌓는 그림).
    layers: [{label, sub, value, text, color, on}] (아래층부터) · target: {value, label, on} 목표선 · ghost: {label, value} 맨 위 점선 층 · total: {text, on}"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 120))
        layers = sp["layers"]
        gh = sp.get("ghost")
        tot = sum(float(l["value"]) for l in layers)
        vmax = tot + (float(gh["value"]) if gh else 0)
        cx, base, Hh = sp.get("cx", 960), sp.get("base", 850), sp.get("height", 560)
        wb, wt = sp.get("w_bottom", 980), sp.get("w_top", 160)
        yv = lambda v: base - Hh * v / vmax
        wv = lambda v: wb - (wb - wt) * v / vmax
        ov = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        acc = 0.0
        tops = []
        for i, l in enumerate(layers):
            v = float(l["value"])
            ti = self.line_start(l.get("on", i + 1)) + l.get("offset", 0)
            k = G.ease_out((t - ti) / 0.55)
            if k > 0:
                a, b = acc, acc + v * k
                c = _col(l.get("color"), [(120, 132, 160), (74, 144, 255), (90, 220, 170), Y][i % 4])
                y0, y1 = yv(a), yv(b)
                w0, w1 = wv(a), wv(b)
                d.polygon([(cx - w0 / 2, y0 - 3), (cx + w0 / 2, y0 - 3), (cx + w1 / 2, y1 + 3), (cx - w1 / 2, y1 + 3)], fill=c + (255,))
                d.polygon([(cx - w1 / 2, y1 + 3), (cx + w1 / 2, y1 + 3), (cx + w1 / 2 - 6, y1 + 14), (cx - w1 / 2 + 6, y1 + 14)], fill=(255, 255, 255, 60))
                tops.append((i, l, (y0 + y1) / 2, w0, w1, k))
            acc += v
        if gh:
            o = G.appear(t, self.line_start(gh.get("on", len(layers))) + 0.4, 0.4)
            if o > 0:
                y0, y1 = yv(tot), yv(vmax)
                w0 = wv(tot)
                pts = [(cx - w0 / 2, y0), (cx, y1), (cx + w0 / 2, y0)]
                for (xa, ya), (xb, yb) in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
                    n = 18
                    for j in range(0, n, 2):
                        d.line([(xa + (xb - xa) * j / n, ya + (yb - ya) * j / n), (xa + (xb - xa) * (j + 1) / n, ya + (yb - ya) * (j + 1) / n)], fill=(236, 240, 248, int(170 * o)), width=4)
        f.alpha_composite(ov)
        if gh:
            o = G.appear(t, self.line_start(gh.get("on", len(layers))) + 0.4, 0.4)
            G.blit(f, T(gh["label"], 34, (210, 214, 226), "ExtraBold"), (cx, yv(tot + float(gh["value"]) * 0.42)), o, "mm")
        tg = sp.get("target")
        if tg:
            o = G.appear(t, self.line_start(tg.get("on", 1)) + 0.3, 0.4)
            if o > 0:
                y = yv(float(tg["value"]))
                ov = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
                dd = ImageDraw.Draw(ov)
                for x in range(S.SAFE_X, S.W - S.SAFE_X - 260, 34):
                    dd.line([(x, y), (x + 20, y)], fill=(240, 84, 84, 230), width=4)
                f.alpha_composite(G.with_opacity(ov, o))
                G.blit(f, G.pill(tg["label"], "Black", 32, S.FG, (240, 84, 84), pad=(16, 6), radius=10), (S.W - S.SAFE_X, y), o, "rm")
        for i, l, ym, w0, w1, k in tops:
            o = min(1, k * 1.6)
            lab = T(l["label"], 44, (14, 16, 24) if i % 4 == 3 else S.FG, "Black")
            if lab.width > min(w0, w1) - 40:   # 좁은 층은 글자 줄임
                lab = T(l["label"], 36, (14, 16, 24) if i % 4 == 3 else S.FG, "Black")
            G.blit(f, lab, (cx, ym), o, "mm")
            xr = cx + max(w0, w1) / 2 + 30
            vt = T(l["text"], 56, _col(l.get("color"), [(190, 196, 210), (120, 180, 255), (90, 220, 170), Y][i % 4]), "Black")
            G.blit(f, vt, (xr, ym), o, "lm")
            if l.get("sub"):
                G.blit(f, T(l["sub"], 26, (190, 196, 214), "SemiBold"), (cx - max(w0, w1) / 2 - 30, ym), o, "rm")
        tl = sp.get("total")
        if tl:
            o = G.appear(t, self.line_start(tl.get("on", len(layers))) + 0.3, 0.35)
            G.blit(f, G.pill(tl["text"], "Black", 52, (14, 16, 24), Y, pad=(28, 12), radius=14), (S.W - S.SAFE_X, sp.get("total_y", 300)), o, "rt")
        self.finish(f, t)


TYPES.update({"pyramid": Pyramid})
