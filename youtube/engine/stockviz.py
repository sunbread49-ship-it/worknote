"""주식 채널 그림 장면 (2026-11-26 사용자: 같은 템플릿 반복 금지 · 직관적이고 가독성 높게)

type: building  회사 = 건물. 층마다 사업(아이콘 + 이름 + 한 줄), 말할 때 그 층에 불이 켜짐
  floors: [{name, sub, tag, hl, on, icon: chip|phone|tv|box}] (위층부터 적기)
type: drop      '바닥인 줄 알았는데' — 산 가격 → 화살표가 뚝 떨어져 → 최저 가격 · 바닥 아래 지하층이 열림
  buy: {label, value}  low: {label, value}  pct: '-52%'  floor_text: '바닥인 줄 알았던 곳'  basement_text: '지하실'
type: dominoes  도미노 3개가 차례로 넘어짐 (원인 → 결과 → 결과)
  items: [{label, sub, on}]  note
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from . import draw as G
from . import style as S
from .editorial import Editorial, T, TYPES, _col

RED = S.RED_L if S.THEME == "08" else (235, 70, 60)
GRN = S.GREEN_L if S.THEME == "08" else (90, 220, 150)
WHITE = (240, 242, 248)


def _ease_in(x):
    x = max(0.0, min(1.0, x))
    return x * x

DIM = (150, 156, 172)


def _icon(kind, s, col):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (255,)
    if kind == "chip":
        m = s * 0.22
        d.rounded_rectangle((m, m, s - m, s - m), 8, outline=c, width=5)
        d.rounded_rectangle((s * 0.38, s * 0.38, s * 0.62, s * 0.62), 4, fill=c)
        for i in range(4):
            q = s * (0.3 + i * 0.13)
            d.line((q, m - 12, q, m), fill=c, width=4); d.line((q, s - m, q, s - m + 12), fill=c, width=4)
            d.line((m - 12, q, m, q), fill=c, width=4); d.line((s - m, q, s - m + 12, q), fill=c, width=4)
    elif kind == "phone":
        d.rounded_rectangle((s * 0.3, s * 0.12, s * 0.7, s * 0.88), 12, outline=c, width=5)
        d.ellipse((s * 0.47, s * 0.76, s * 0.53, s * 0.82), fill=c)
    elif kind == "tv":
        d.rounded_rectangle((s * 0.12, s * 0.22, s * 0.88, s * 0.72), 8, outline=c, width=5)
        d.line((s * 0.4, s * 0.86, s * 0.6, s * 0.86), fill=c, width=5)
        d.line((s * 0.5, s * 0.72, s * 0.5, s * 0.86), fill=c, width=5)
    else:
        d.rectangle((s * 0.2, s * 0.3, s * 0.8, s * 0.8), outline=c, width=5)
    return im


class Building(Editorial):
    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        floors = sp["floors"]
        n = len(floors)
        bx0, bx1 = 260, 1200
        top, fh = 400, sp.get("floor_h", 150)
        d = ImageDraw.Draw(f)
        # 지붕 · 기둥
        roof = G.appear(t, 0.0, 0.4)
        d.polygon([(bx0 - 30, top), (bx1 + 30, top), ((bx0 + bx1) / 2, top - 90)], fill=(40, 46, 62, int(255 * roof)))
        sign = T(sp.get("sign", "삼성전자"), 40, WHITE, "Black")
        G.blit(f, sign, ((bx0 + bx1) / 2, top - 34), roof, "mm")
        cur = -1
        for i, fl in enumerate(floors):
            if t >= self.line_start(fl.get("on", 1)) + fl.get("offset", 0):
                cur = i
        for i, fl in enumerate(floors):
            y0 = top + i * fh
            ts = self.line_start(fl.get("on", 1)) + fl.get("offset", 0)
            lit = G.appear(t, ts, 0.35)
            active = i == cur
            base_col = (30, 34, 48)
            col = RED if fl.get("hl") else GRN
            fill = tuple(int(base_col[j] + (col[j] * 0.35 - base_col[j]) * lit * (1 if active else 0.45)) for j in range(3))
            d.rectangle((bx0, y0, bx1, y0 + fh - 10), fill=fill + (255,), outline=(70, 76, 96, 255), width=3)
            # 창문
            for w in range(6):
                wx = bx0 + 40 + w * 70
                wc = (255, 220, 120) if lit > 0 else (60, 66, 84)
                d.rectangle((wx, y0 + 30, wx + 40, y0 + 70), fill=wc + (int(120 + 135 * lit) if lit > 0 else 255,))
            G.blit(f, T(fl.get("floor", f"{n - i}층"), 34, DIM, "Black"), (bx0 + 40, y0 + fh - 50), 1, "lm")
            if lit > 0:
                ic = _icon(fl.get("icon", "box"), 96, col)
                G.blit(f, ic, (bx0 + 560, y0 + (fh - 10) / 2), lit, "mm")
                G.blit(f, T(fl["name"], 52 if active else 44, WHITE, "Black"), (bx1 + 50, y0 + 40), lit, "lt")
                if fl.get("sub"):
                    G.blit(f, T(fl["sub"], 32, col if active else DIM, "Bold"), (bx1 + 50, y0 + 104), lit, "lt")
                if fl.get("tag") and active:
                    G.blit(f, G.pill(fl["tag"], "Black", 30, (255, 255, 255), col, pad=(16, 6)), (bx0 + 760, y0 + 50), lit, "mm")
        self.finish(f, t)


class Drop(Editorial):
    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        d = ImageDraw.Draw(f)
        cx = sp.get("cx", 620)
        y_buy, y_floor, y_low = 370, 600, 800
        # 바닥 판(부서짐)
        t_buy = self.line_start(sp.get("buy_on", 1))
        t_fall = self.line_start(sp.get("fall_on", 2))
        G.blit(f, T(sp["buy"]["label"], 34, DIM, "Bold"), (cx + 180, y_buy), G.appear(t, t_buy, 0.3), "lm")
        tag = G.pill(sp["buy"]["value"], "Black", 52, (20, 22, 30), WHITE, pad=(26, 10), radius=18)
        G.blit(f, tag, (cx, y_buy), G.appear(t, t_buy, 0.3), "mm")
        crack = G.appear(t, t_fall, 0.3)
        # 바닥 선
        if crack < 1:
            d.line((cx - 520, y_floor, cx + 520, y_floor), fill=(200, 204, 214, 255), width=8)
        else:
            d.line((cx - 520, y_floor, cx - 90, y_floor), fill=(200, 204, 214, 255), width=8)
            d.line((cx + 90, y_floor, cx + 520, y_floor), fill=(200, 204, 214, 255), width=8)
            for k, (a, b) in enumerate(((-90, 20), (90, 30))):
                d.line((cx + a, y_floor, cx + a * 0.6, y_floor + b), fill=(200, 204, 214, 200), width=6)
        G.blit(f, T(sp.get("floor_text", "바닥인 줄 알았던 곳"), 32, (200, 204, 214), "Bold"), (cx - 520, y_floor - 16), G.appear(t, t_buy + 0.4, 0.3), "lb")
        # 지하
        if crack >= 1:
            ob = G.appear(t, t_fall + 0.2, 0.4)
            ov = Image.new("RGBA", (1040, y_low - y_floor + 80), (120, 20, 24, int(70 * ob)))
            f.alpha_composite(ov, (cx - 520, y_floor + 4))
            G.blit(f, T(sp.get("basement_text", "지하실"), 34, RED, "Black"), (cx + 540, y_low - 20), ob, "lm")
        # 떨어지는 화살표
        k = _ease_in((t - t_fall) / 0.9) if t >= t_fall else 0
        if k > 0:
            ya = y_buy + 50 + (y_low - y_buy - 60) * min(1, k)
            d.line((cx, y_buy + 50, cx, ya), fill=RED + (255,), width=14)
            d.polygon([(cx, ya + 30), (cx - 28, ya - 10), (cx + 28, ya - 10)], fill=RED + (255,))
            if k >= 1:
                low = G.pill(sp["low"]["value"], "Black", 52, (255, 255, 255), RED, pad=(26, 10), radius=18)
                G.blit(f, low, (cx, y_low + 30), G.appear(t, t_fall + 0.9, 0.25), "mm")
                G.blit(f, T(sp["low"]["label"], 34, DIM, "Bold"), (cx + 180, y_low + 30), G.appear(t, t_fall + 0.9, 0.25), "lm")
                big = T(sp["pct"], 150, RED, "Black")
                G.blit(f, big, (cx + 820, (y_buy + y_floor) / 2 + 20), G.appear(t, t_fall + 1.0, 0.3), "mm")
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec.get("fall_on", 2)) + 0.05, "boom", 0.9)]


class Dominoes(Editorial):
    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        items = sp["items"]
        n = len(items)
        gap = 430
        x0 = S.W / 2 - gap * (n - 1) / 2
        yb = 760
        bw, bh = 120, 300
        for i, it in enumerate(items):
            ts = self.line_start(it.get("on", 1)) + it.get("offset", 0)
            o = G.appear(t, ts - 0.4, 0.3)
            if o <= 0:
                continue
            fall = _ease_in(min(1.0, max(0.0, (t - ts) / 0.6)))
            ang = -62 * fall
            hl = it.get("hl")
            col = RED if hl else (GRN if i == 0 else (90, 100, 130))
            blk = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
            bd = ImageDraw.Draw(blk)
            bd.rounded_rectangle((0, 0, bw - 1, bh - 1), 18, fill=col + (255,), outline=(255, 255, 255, 200), width=4)
            for dy in (0.3, 0.7):
                bd.ellipse((bw / 2 - 12, bh * dy - 12, bw / 2 + 12, bh * dy + 12), fill=(255, 255, 255, 230))
            big = Image.new("RGBA", (bh * 2, bh * 2), (0, 0, 0, 0))
            big.alpha_composite(blk, (bh - bw // 2, bh - bh))
            rot = big.rotate(ang, center=(bh, bh), resample=Image.BICUBIC)
            x = x0 + i * gap
            G.blit(f, rot, (x - bh, yb - bh), o, "lt")
            G.blit(f, T(it["label"], 48, WHITE, "Black"), (x, yb + 40), o, "mt")
            if it.get("sub"):
                G.blit(f, T(it["sub"], 30, col if fall > 0.5 else DIM, "Bold"), (x, yb + 104), o, "mt")
            if i < n - 1:
                d = ImageDraw.Draw(f)
                ax = x + 120
                d.line((ax, yb - 120, ax + gap - 260, yb - 120), fill=(200, 204, 214, int(160 * o)), width=4)
                d.polygon([(ax + gap - 240, yb - 120), (ax + gap - 266, yb - 134), (ax + gap - 266, yb - 106)], fill=(200, 204, 214, int(160 * o)))
        if sp.get("note"):
            G.blit(f, T(sp["note"], 44, WHITE, "Black", highlight=sp.get("note_hl", ""), hl_fill=RED), (S.W / 2, 950), G.appear(t, self.line_start(sp.get("note_on", 3)), 0.3), "mm")
        self.finish(f, t)

    own_note = True

    def extra_sfx(self):
        return [(self.line_start(it.get("on", 1)) + it.get("offset", 0) + 0.4, "pop", 0.5) for it in self.spec["items"]]


TYPES.update({"building": Building, "drop": Drop, "dominoes": Dominoes})


class Ladder(Editorial):
    """가격 자(세로 눈금) — 지금 가격에 악어새 · 아래 정거장(13만 · 10만)에 깃발이 차례로 꽂힘
    now: {value, label}  stops: [{value, label, sub, on}]  vmax · vmin"""

    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        self.hdr(f, t, y=sp.get("title_y", 150), center=False)
        d = ImageDraw.Draw(f)
        vmax, vmin = sp.get("vmax", 220000), sp.get("vmin", 80000)
        x, y0, y1 = 760, 380, 900
        Y = lambda v: y0 + (vmax - v) / (vmax - vmin) * (y1 - y0)
        d.rounded_rectangle((x - 14, y0, x + 14, y1), 14, fill=(52, 58, 76, 255))
        for v in range(int(vmin), int(vmax) + 1, 20000):
            yy = Y(v)
            d.line((x - 34, yy, x - 16, yy), fill=(150, 156, 172, 255), width=3)
            G.blit(f, T(f"{v // 10000}만", 26, DIM, "Bold"), (x - 46, yy), 1, "rm")
        nw = sp["now"]
        yn = Y(nw["value"])
        d.rounded_rectangle((x - 14, y0, x + 14, yn), 14, fill=(200, 204, 214, 255))
        G.blit(f, G.pill(nw["label"], "Black", 44, (20, 22, 30), WHITE, pad=(22, 8)), (x + 60, yn), 1, "lm")
        from .editorial import _mascot_img
        m = _mascot_img(getattr(self, "channel", {}), 110)
        G.blit(f, m, (x - 180, yn + 6 * math.sin(t * 3)), 1, "mm")
        for i, st in enumerate(sp["stops"]):
            ts = self.line_start(st.get("on", 1)) + st.get("offset", 0)
            o = G.appear(t, ts, 0.35)
            if o <= 0:
                continue
            ys = Y(st["value"])
            k = G.ease_out(o)
            d.line((x - 200, ys, x - 200 + (900) * k, ys), fill=RED + (200,), width=4)
            for xx in range(int(x - 200), int(x + 700), 30):
                pass
            fl = G.pill(st["label"], "Black", 52, (255, 255, 255), RED, pad=(24, 8), radius=14)
            G.blit(f, fl, (x + 60, ys), o, "lm")
            if st.get("sub"):
                G.blit(f, T(st["sub"], 30, (220, 224, 234), "Bold"), (x + 80 + fl.width, ys), o, "lm")
            dy = (ys - yn)
            G.blit(f, T(f"{(st['value'] / nw['value'] - 1) * 100:.0f}%", 40, RED, "Black"), (x - 220, ys), o, "rm")
        self.finish(f, t)


TYPES.update({"ladder": Ladder})
