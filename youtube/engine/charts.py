"""실제 시세로 그리는 애니메이션 차트 (선 차트 / 막대 차트)."""
import math

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from . import data as D
from . import draw as G
from . import style as S

K = 2  # 슈퍼샘플링 배율


def _year(ts) -> float:
    ts = pd.Timestamp(ts)
    return ts.year + (ts.dayofyear - 1) / 365.25


def _fmt(v, unit=""):
    if unit == "%":
        return f"{v:+.0f}%" if v else "0%"
    if unit == "won":  # 만원 단위 값 → 1,000만 / 1억 / 30억
        if v >= 10000:
            x = v / 10000
            return f"{x:,.0f}억" if x >= 10 else f"{x:.1f}억".replace(".0억", "억")
        return f"{v:,.0f}만" if v >= 1 else f"{v * 10000:,.0f}원"
    if unit == "x":
        return f"{v:g}배"
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if abs(v) >= 10:
        return f"{v:.0f}"
    return f"{v:g}"


def _fmt_end(v, unit=""):
    if unit == "won" and v < 1:
        return f"{v * 10000:,.0f}원"
    if unit == "%":
        return f"{v:+.1f}%"
    if unit in ("", "x") and v < 10:
        return f"{v:,.2f}"
    return _fmt(v, unit)


class LineChart:
    """
    spec 예:
      series: sp500 | sp500_drawdown | vix | tqqq | sqqq | qqq | ndx | sim3x_ndx | <이름>_drawdown
      start/end: "1871-01" / "2026-09"
      log: true                      # 로그 스케일
      color: [255,194,70]
      draw: {on: 1, dur: 4}          # 내레이션 1번 줄에서 시작, 4초간 그려짐
      hlines: [{y: 40, label: "VIX 40"}]
      marks:  [{date: 2020-03-16, label: "VIX 82.69", on: 2, dy: -90, line: 0}]
      bands:  [{start: 2008-01, end: 2009-06, label: "금융위기", on: 3}]
      source: "자료: ..."
    여러 선 비교:
      lines: [{series: tqqq, color: up, label: "TQQQ"}, {series: qqq, color: neutral, label: "QQQ"}]
      base: 1000          # 시작값을 1000으로 맞춤(예: 1,000만원 투자)
      unit: won           # 축 표기: won(만원) | x(배) | %
      end_labels: true    # 선 끝에 이름+최종값
    """

    def __init__(self, spec, rect=None):
        self.spec = spec
        self.rect = rect or spec.get("rect") or (S.SAFE_X + 70, 200, S.W - 2 * S.SAFE_X - 70, 620)
        self.log = spec.get("log", False)
        from .scenes import col  # 순환 import 회피
        defs = spec.get("lines") or [{"series": spec["series"], "color": spec.get("color")}]
        first = defs[0]["series"]
        self.unit = "%" if first.endswith("drawdown") else spec.get("unit", "")
        self.fill_to_zero = self.unit == "%"
        self.L = []
        for i, d in enumerate(defs):
            sr = D.series(d["series"], d.get("start", spec.get("start")), d.get("end", spec.get("end"))).dropna()
            if spec.get("base"):
                sr = sr / sr.iloc[0] * spec["base"]
            c = col(d.get("color"), S.DOWN if self.unit == "%" else S.GOLD)
            self.L.append({"s": sr, "color": c, "label": d.get("label", ""), "fill": d.get("fill", i == 0),
                           "label_dy": d.get("label_dy", 0),
                           "xs": np.array([_year(t) for t in sr.index]), "ys": sr.values.astype(float)})
        self.s = self.L[0]["s"]
        self.color = self.L[0]["color"]
        self.xs, self.ys = self.L[0]["xs"], self.L[0]["ys"]
        self._scale()
        self._build()

    # 좌표계
    def _scale(self):
        xs = np.concatenate([l["xs"] for l in self.L])
        ys = np.concatenate([l["ys"] for l in self.L])
        self.x0, self.x1 = xs.min(), xs.max()
        if self.log:
            lo, hi = math.log10(ys.min() * 0.8), math.log10(ys.max() * 1.25)
        elif self.unit == "%":
            lo, hi = min(ys.min() * 1.08, -5), 0
        else:
            pad = (ys.max() - ys.min()) * 0.12
            lo, hi = max(0, ys.min() - pad), ys.max() + pad
            for h in self.spec.get("hlines", []):
                hi = max(hi, h["y"] * 1.1)
        self.lo, self.hi = self.spec.get("ymin", lo), self.spec.get("ymax", hi)
        if self.log and "ymin" in self.spec:
            self.lo = math.log10(self.spec["ymin"])
        if self.log and "ymax" in self.spec:
            self.hi = math.log10(self.spec["ymax"])

    def px(self, x, y):
        rx, ry, rw, rh = self.rect
        yv = math.log10(max(y, 1e-12)) if self.log else y
        return (rx + (x - self.x0) / (self.x1 - self.x0) * rw,
                ry + (1 - (yv - self.lo) / (self.hi - self.lo)) * rh)

    def _ticks_y(self):
        if self.log:
            out = []
            for e in range(int(math.floor(self.lo)), int(math.ceil(self.hi)) + 1):
                v = 10 ** e
                if self.lo <= math.log10(v) <= self.hi:
                    out.append(v)
            return out
        span = self.hi - self.lo
        step = 10 ** math.floor(math.log10(span / 4))
        for m in (1, 2, 2.5, 5, 10):
            if span / (step * m) <= 6:
                step *= m
                break
        start = math.ceil(self.lo / step) * step
        return list(np.arange(start, self.hi + 1e-9, step))

    def _ticks_x(self):
        span = self.x1 - self.x0
        if span < 1.6:
            return []
        step = next(s for s in (1, 2, 5, 10, 20, 25, 50) if span / s <= 9)
        start = math.ceil(self.x0 / step) * step
        return [y for y in range(int(start), int(self.x1) + 1, step)]

    # 정적 레이어(축·격자) + 선 레이어를 미리 렌더
    def _build(self):
        rx, ry, rw, rh = self.rect
        base = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(base)
        for v in self._ticks_y():
            _, y = self.px(self.x0, v)
            d.line((rx, y, rx + rw, y), fill=S.FAINT + (160,), width=1)
            t = G.text_img(_fmt(v, self.unit), "Medium", 24, S.MUTED)
            base.alpha_composite(t, (int(rx - t.width - 16), int(y - t.height / 2)))
        ybot = ry + rh
        for yr in self._ticks_x():
            x, _ = self.px(yr, 1)
            d.line((x, ybot, x, ybot + 8), fill=S.MUTED + (180,), width=2)
            t = G.text_img(str(yr), "Medium", 24, S.MUTED)
            base.alpha_composite(t, (int(x - t.width / 2), int(ybot + 14)))
        if not self._ticks_x():  # 짧은 기간이면 시작·끝 날짜
            for x_, ts in ((rx, self.s.index[0]), (rx + rw, self.s.index[-1])):
                t = G.text_img(ts.strftime("%Y.%m.%d"), "Medium", 24, S.MUTED)
                base.alpha_composite(t, (int(x_ - t.width / 2), int(ybot + 14)))
        d.line((rx, ybot, rx + rw, ybot), fill=S.MUTED + (200,), width=2)
        if self.unit == "%":
            _, y0 = self.px(self.x0, 0)
            d.line((rx, y0, rx + rw, y0), fill=S.MUTED + (220,), width=2)
        for h in self.spec.get("hlines", []):
            _, y = self.px(self.x0, h["y"])
            from .scenes import col
            c = col(h.get("color"), S.UP)
            for x in range(int(rx), int(rx + rw), 22):
                d.line((x, y, min(x + 12, rx + rw), y), fill=c + (230,), width=3)
            if h.get("label"):
                t = G.pill(h["label"], "Bold", 24, (16, 20, 32), c, pad=(14, 6))
                lx = rx + 12 if h.get("label_side", "left") == "left" else rx + rw - t.width
                base.alpha_composite(t, (int(lx), int(y - t.height - 10)))
        if self.spec.get("title"):
            base.alpha_composite(G.text_img(self.spec["title"], "Bold", 34, S.FG), (int(rx - 70), int(ry - 70)))
        if self.spec.get("source"):
            t = G.text_img(self.spec["source"], "Regular", 20, S.MUTED)
            base.alpha_composite(t, (int(rx + rw - t.width), int(ry + rh + 50)))
        self.base = base

        # 선 + 아래 그라데이션 채우기 (2배로 그려 축소 → 매끈한 선)
        w2, h2 = S.W * K, S.H * K
        layer = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
        yy = np.linspace(0, 1, h2)[:, None]
        for ln in self.L:
            pts = [(self.px(x, y)[0] * K, self.px(x, y)[1] * K) for x, y in zip(ln["xs"], ln["ys"])]
            ln["pts"] = [(x / K, y / K) for x, y in pts]
            if ln["fill"]:
                yb = self.px(self.x0, 0)[1] * K if self.fill_to_zero else (ry + rh) * K
                mask = Image.new("L", (w2, h2), 0)
                ImageDraw.Draw(mask).polygon(pts + [(pts[-1][0], yb), (pts[0][0], yb)], fill=255)
                if self.fill_to_zero:
                    grad = np.clip((yy * h2 - yb) / max(1, (ry + rh) * K - yb), 0, 1) * 0.55 + 0.15
                else:
                    grad = np.clip(1 - (yy * h2 - ry * K) / (rh * K), 0, 1) * 0.42 + 0.03
                a = (np.asarray(mask, dtype=np.float32) * grad).astype("uint8")
                fill = Image.new("RGBA", (w2, h2), ln["color"] + (0,))
                fill.putalpha(Image.fromarray(a, "L"))
                layer.alpha_composite(fill)
        for ln in reversed(self.L):  # 첫 번째 선이 맨 위
            lay = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
            ImageDraw.Draw(lay).line([(x * K, y * K) for x, y in ln["pts"]], fill=ln["color"] + (255,),
                                     width=(4 if ln is self.L[0] else 3) * K, joint="curve")
            layer.alpha_composite(lay)
        self.line = layer.reduce(K)
        self.pts = self.L[0]["pts"]

    def point_at(self, date, line=0):
        ln = self.L[line]
        x = _year(date)
        i = int(np.searchsorted(ln["xs"], x))
        i = min(max(i, 0), len(ln["xs"]) - 1)
        return self.px(ln["xs"][i], ln["ys"][i]), ln["ys"][i]

    def render(self, frame, t, sc, op=1.0):
        rx, ry, rw, rh = self.rect
        G.blit(frame, self.base, (0, 0), op)
        dspec = self.spec.get("draw", {})
        t0 = sc.line_start(dspec.get("on", 1)) if dspec.get("on", 1) > 1 else 0.3
        p = G.ease_in_out((t - t0) / dspec.get("dur", 3.0))
        from .scenes import col
        # 밴드(구간 음영)
        for b in self.spec.get("bands", []):
            o = G.appear(t, sc.line_start(b.get("on", 1))) * op
            if o <= 0:
                continue
            bc = col(b.get("color"), S.UP)
            xa, _ = self.px(_year(b["start"]), 1)
            xb, _ = self.px(_year(b["end"]), 1)
            lay = Image.new("RGBA", (max(2, int(xb - xa) + 1), int(rh)), bc + (46,))
            G.blit(frame, lay, (xa, ry), o)
            if b.get("label"):
                G.blit(frame, G.text_img(b["label"], "Bold", 26, bc), ((xa + xb) / 2, ry + 8), o, "mt")
        # 선 그려지기
        if p > 0:
            xr = rx + rw * p
            crop = self.line.crop((0, 0, int(xr) + 3, S.H))
            G.blit(frame, crop, (0, 0), op)
            for ln in self.L:
                xs_px = [q[0] for q in ln["pts"]]
                i = min(int(np.searchsorted(xs_px, xr)), len(ln["pts"]) - 1)
                hx, hy = ln["pts"][i]
                if p < 0.999:
                    G.blit(frame, _dot(16, ln["color"]), (hx, hy), op, "mm")
                    if self.spec.get("live_value"):  # 그려지는 동안 현재 값 표시
                        v = ln["ys"][i]
                        G.blit(frame, G.pill(_fmt_end(v, self.unit), "ExtraBold", 30, (16, 20, 32), ln["color"],
                                             pad=(14, 6)), (hx + 16, hy - 16), op, "lb")
                elif self.spec.get("end_labels"):
                    v = ln["ys"][-1]
                    txt = (ln["label"] + "  " if ln["label"] else "") + _fmt_end(v, self.unit)
                    G.blit(frame, G.pill(txt, "ExtraBold", 30, (16, 20, 32), ln["color"], pad=(16, 7)),
                           (hx + 14, hy + ln["label_dy"]), op, "lm")
        # 마커 + 라벨
        for m in self.spec.get("marks", []):
            o = G.appear(t, sc.line_start(m.get("on", 1))) * op
            if o <= 0:
                continue
            (mx, my), val = self.point_at(m["date"], m.get("line", 0))
            c = col(m.get("color"), S.FG)
            G.blit(frame, _dot(22, c, ring=True), (mx, my), o, "mm")
            dy = m.get("dy", -110)
            dx = m.get("dx", 0)
            lab = G.pill(m["label"], "Bold", m.get("size", 28), (12, 16, 28), c, pad=(18, 8))
            lx, ly = mx + dx, my + dy
            ln_ = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
            ImageDraw.Draw(ln_).line((mx, my + (12 if dy > 0 else -12), lx, ly), fill=c + (220,), width=3)
            G.blit(frame, ln_, (0, 0), o)
            G.blit(frame, lab, (lx, ly), o, "mb" if dy < 0 else "mt")
            if m.get("sub"):
                st = G.text_img(m["sub"], "Medium", 24, S.FG)
                G.blit(frame, st, (lx, ly - lab.height - 8) if dy < 0 else (lx, ly + lab.height + 8), o,
                       "mb" if dy < 0 else "mt")


_dots = {}


def _dot(size, color, ring=False):
    key = (size, color, ring)
    if key not in _dots:
        im, d = G.supersample(size + 16, size + 16, 4)
        c = (size + 16) * 2
        r = size * 2
        d.ellipse((c - r - 24, c - r - 24, c + r + 24, c + r + 24), fill=color + (60,))
        d.ellipse((c - r, c - r, c + r, c + r), fill=color + (255,))
        if ring:
            d.ellipse((c - r // 2, c - r // 2, c + r // 2, c + r // 2), fill=(12, 16, 28, 255))
        _dots[key] = G.finish(im, 4)
    return _dots[key]


class BarChart:
    """
    groups:  (그룹마다 척도가 따로: 수익률·확률처럼 단위가 달라도 됨)
      - label: "1년 뒤 평균 수익률"
        on: 3
        bars:
          - {label: "아무 달에나", stat: {kind: fwd_mean_all, since: 1950}, color: neutral}
          - {label: "고점 대비 -20% 이하", stat: {...}, color: up}
    unit: "%"
    """
    COLORS = {"neutral": S.NEUTRAL, "up": S.UP, "down": S.DOWN, "gold": S.GOLD}

    def __init__(self, spec):
        self.spec = spec
        self.rect = spec.get("rect", (S.SAFE_X + 40, 250, S.W - 2 * S.SAFE_X - 80, 560))
        for g in spec["groups"]:
            for b in g["bars"]:
                if "stat" in b:
                    st = dict(b["stat"])
                    b["value"] = round(D.stat(st.pop("kind"), **st), 1)

    def render(self, frame, t, sc, op=1.0):
        rx, ry, rw, rh = self.rect
        groups = self.spec["groups"]
        gw = rw / len(groups)
        base_y = ry + rh
        ln = Image.new("RGBA", (int(rw), 3), S.MUTED + (200,))
        G.blit(frame, ln, (rx, base_y), op)
        for gi, g in enumerate(groups):
            t0 = sc.line_start(g.get("on", 1))
            go = G.appear(t, t0) * op
            if go <= 0:
                continue
            cx = rx + gw * (gi + 0.5)
            G.blit(frame, G.text_img(g["label"], "Bold", 34, S.FG), (cx, base_y + 26), go, "mt")
            vmax = g.get("vmax") or max(b["value"] for b in g["bars"]) * 1.25  # 그룹별 척도
            n = len(g["bars"])
            bw = min(170, gw / (n + 1.2))
            for bi, b in enumerate(g["bars"]):
                bt0 = t0 + 0.25 + bi * 0.9 + b.get("delay", 0)
                if b.get("on"):
                    bt0 = sc.line_start(b["on"])
                p = G.ease_out((t - bt0) / 1.1)
                if p <= 0:
                    continue
                color = self.COLORS.get(b.get("color", "neutral"), S.NEUTRAL)
                x = cx + (bi - (n - 1) / 2) * (bw + 36)
                full_h = rh * b["value"] / vmax
                h = max(2, full_h * p)
                im, d = G.supersample(int(bw), int(h) + 2, 2)
                d.rounded_rectangle((0, 0, int(bw) * 2 - 1, int(h) * 2 + 3), radius=16, fill=color + (255,))
                G.blit(frame, G.finish(im), (x, base_y), op, "mb")
                val = b["value"] * p
                vt = G.text_img(f"{val:.1f}{self.spec.get('unit', '')}", "ExtraBold", 50, color)
                G.blit(frame, vt, (x, base_y - h - 12), op * min(1, p * 2), "mb")
                lt = G.text_img(b["label"], "SemiBold", 26, S.MUTED, max_w=int(bw + 60), align="center")
                G.blit(frame, lt, (x, base_y - h - 74), op * min(1, p * 2), "mb")
        if self.spec.get("source"):
            G.blit(frame, G.text_img(self.spec["source"], "Regular", 20, S.MUTED), (rx + rw, base_y + 100), op, "rt")
