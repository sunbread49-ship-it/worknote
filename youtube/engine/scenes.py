"""장면 타입별 렌더러. 에피소드 YAML의 각 scene → 여기 클래스 하나.

공통 키:
  type, chapter, narration(리스트: 녹음·자막 단위 문장)
  callouts: [{on, label, value, sub, pos:[x,y], color}]   숫자 강조 박스
  illust:   {name: gauge|newspaper|warning, pos:[x,y], size, on, until, needle:[[줄번호, 값], ...]}
  (callouts/illust 의 until: N = N번째 줄에서 사라짐)
  note:     화면 하단 작은 각주
시간 지정 `on: N` = 내레이션 N번째 줄(1부터)이 시작될 때 등장.
"""
from PIL import Image, ImageDraw

from . import charts as C
from . import draw as G
from . import illust as I
from . import style as S

COLORS = {"gold": S.GOLD, "up": S.UP, "down": S.DOWN, "fg": S.FG, "muted": S.MUTED, "neutral": S.NEUTRAL}


def col(c, default=S.FG):
    if c is None:
        return default
    return COLORS.get(c, tuple(c) if isinstance(c, (list, tuple)) else default)


class Scene:
    def __init__(self, spec, idx, channel):
        self.spec, self.idx, self.channel = spec, idx, channel
        self.narration = spec.get("narration", [])
        self.dur = 0.0
        self.lines = []          # [(start, end)] 장면 기준 초

    def line_start(self, n):
        if not self.lines:
            return 0.0
        n = max(1, min(int(n), len(self.lines)))
        return self.lines[n - 1][0] if n > 1 else min(0.25, self.lines[0][0])

    def prepare(self):
        pass

    # 장면마다 공통으로 붙는 것들
    def draw_common(self, f, t):
        il = self.spec.get("illust")
        if il:
            o = G.appear(t, self.line_start(il.get("on", 1)), 0.6)
            if il.get("until"):
                o *= 1 - G.appear(t, self.line_start(il["until"]), 0.4)
            kw = {}
            if il["name"] == "gauge":
                v = il.get("needle", [[1, 0]])[0][1]
                for n, val in il.get("needle", []):
                    t0 = self.line_start(n)
                    if t >= t0:
                        prev = v
                        v = prev + (val - prev) * G.ease_in_out((t - t0) / 1.4)
                kw["value"] = round(v, 3)
            img = _illust_cached(il["name"], il.get("size", 600), tuple(sorted(kw.items())))
            y_off = (1 - o) * 30
            G.blit(f, img, (il["pos"][0], il["pos"][1] + y_off), o, "mm")
        for c in self.spec.get("callouts", []):
            o = G.appear(t, self.line_start(c.get("on", 1)))
            if c.get("until"):
                o *= 1 - G.appear(t, self.line_start(c["until"]), 0.4)
            if o > 0:
                G.blit(f, _callout(c.get("label", ""), c.get("value", ""), c.get("sub", ""),
                                   col(c.get("color"), S.GOLD), c.get("width", 440)),
                       (c["pos"][0], c["pos"][1] + (1 - o) * 24), o, c.get("anchor", "lt"))
        if self.spec.get("note"):
            G.blit(f, G.text_img(self.spec["note"], "Regular", 22, S.MUTED), (S.W - S.SAFE_X, 898), 1, "rt")

    def draw(self, f, t):
        raise NotImplementedError


_ill = {}


def _illust_cached(name, size, kw):
    key = (name, size, kw)
    if key not in _ill:
        if len(_ill) > 400:
            _ill.clear()
        _ill[key] = I.get(name, size, **dict(kw))
    return _ill[key]


_co = {}


def _callout(label, value, sub, color, width):
    key = (label, value, sub, color, width)
    if key not in _co:
        parts = []
        if label:
            parts.append(G.text_img(label, "SemiBold", 28, S.MUTED, max_w=width - 64))
        if value:
            parts.append(G.text_img(value, "Black", 76, color))
        if sub:
            parts.append(G.text_img(sub, "Medium", 26, S.FG, max_w=width - 64))
        h = sum(p.height for p in parts) + 14 * (len(parts) - 1) + 60
        im = G.panel(width, h, S.PANEL, 24, outline=color + (120,))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, 8, h - 1), radius=4, fill=color + (255,))
        y = 30
        for p in parts:
            im.alpha_composite(p, (36, y))
            y += p.height + 14
        _co[key] = im
    return _co[key]


# ── 장면 타입 ─────────────────────────────────────────────────────
class Title(Scene):
    def prepare(self):
        bg = self.spec.get("bgchart")
        self.chart = C.LineChart(dict(bg, draw={"on": 1, "dur": 0.01}),
                                 rect=(0, 300, S.W, 700)) if bg else None

    def draw(self, f, t):
        sp = self.spec
        if self.chart:
            G.blit(f, self.chart.line, (0, 0), 0.22)
        y = 300
        if sp.get("kicker"):
            o = G.appear(t, 0.1)
            k = G.pill(sp["kicker"], "Bold", 32, (16, 20, 32), S.GOLD, pad=(26, 10))
            G.blit(f, k, (S.W / 2, y + (1 - o) * 20), o, "mt")
            y += k.height + 40
        o = G.appear(t, 0.35, 0.6)
        tt = G.text_img(sp["title"], "Black", sp.get("size", 104), S.FG, max_w=1600, align="center",
                        highlight=sp.get("highlight", ""))
        G.blit(f, tt, (S.W / 2, y + (1 - o) * 40), o, "mt")
        y += tt.height + 36
        if sp.get("subtitle"):
            o = G.appear(t, self.line_start(sp.get("subtitle_on", 1)) + 0.6)
            G.blit(f, G.text_img(sp["subtitle"], "SemiBold", 46, S.MUTED, max_w=1500, align="center"),
                   (S.W / 2, y), o, "mt")
        self.draw_common(f, t)


class Quote(Scene):
    def draw(self, f, t):
        sp = self.spec
        o = G.appear(t, 0.1)
        G.blit(f, G.text_img("“", "Black", 300, S.GOLD), (S.SAFE_X + 40, 110), o * 0.9)
        x, y = S.SAFE_X + 220, 250
        if sp.get("original"):
            e = G.text_img(sp["original"], "Medium", 34, S.MUTED, max_w=1400)
            G.blit(f, e, (x, y), o)
            y += e.height + 46
        o2 = G.appear(t, self.line_start(sp.get("text_on", 1)) + 0.3, 0.7)
        k = G.text_img(sp["text"], "ExtraBold", 62, S.FG, max_w=1420, highlight=sp.get("highlight", ""))
        G.blit(f, k, (x, y + (1 - o2) * 30), o2)
        y += k.height + 50
        o3 = G.appear(t, self.line_start(sp.get("source_on", 1)) + 0.9)
        G.blit(f, G.text_img("— " + sp.get("source", ""), "SemiBold", 34, S.GOLD), (x, y), o3)
        self.draw_common(f, t)


class Card(Scene):
    """heading + bullets. split 레이아웃이면 왼쪽에 일러스트(illust.pos 사용)."""

    def draw(self, f, t):
        sp = self.spec
        x = sp.get("x", S.SAFE_X + 20)
        y = sp.get("y", 190)
        maxw = sp.get("width", S.W - x - S.SAFE_X)
        o = G.appear(t, self.line_start(sp.get("heading_on", 1)))
        h = G.text_img(sp["heading"], "Black", sp.get("heading_size", 72), S.FG, max_w=maxw,
                       highlight=sp.get("highlight", ""))
        G.blit(f, h, (x, y + (1 - o) * 24), o)
        y += h.height + 60
        for i, b in enumerate(sp.get("bullets", [])):
            if isinstance(b, str):
                b = {"text": b}
            o = G.appear(t, self.line_start(b.get("on", 1)))
            if sp.get("numbered"):
                icon = I.number_badge(i + 1, 64)
            elif sp.get("icon") == "dash":
                icon = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                ImageDraw.Draw(icon).rounded_rectangle((8, 28, 40, 36), radius=4, fill=S.GOLD + (255,))
            else:
                icon = I.check(56, col(b.get("color"), S.GOLD))
            tx = G.text_img(b["text"], "Bold", sp.get("size", 46), S.FG, max_w=maxw - 100,
                            highlight=b.get("highlight", ""), hl_fill=col(b.get("hl_color"), S.GOLD))
            dy = (1 - o) * 24
            G.blit(f, icon, (x, y + dy + 2), o)
            G.blit(f, tx, (x + 92, y + dy + 4), o)
            yy = y + tx.height + 4
            if b.get("sub"):
                st = G.text_img(b["sub"], "Medium", 30, S.MUTED, max_w=maxw - 100)
                G.blit(f, st, (x + 92, yy + 6 + dy), o)
                yy += st.height + 6
            y = yy + sp.get("gap", 44)
        self.draw_common(f, t)


class Chart(Scene):
    def prepare(self):
        self.chart = C.LineChart(self.spec["chart"])

    def draw(self, f, t):
        self.chart.render(f, t, self)
        self.draw_common(f, t)


class Bars(Scene):
    def prepare(self):
        self.chart = C.BarChart(self.spec["bars"])

    def draw(self, f, t):
        sp = self.spec
        if sp.get("heading"):
            o = G.appear(t, 0.1)
            G.blit(f, G.text_img(sp["heading"], "ExtraBold", 50, S.FG, max_w=1600), (S.SAFE_X + 20, 150), o)
        if sp.get("subheading"):
            o = G.appear(t, self.line_start(sp.get("subheading_on", 1)))
            G.blit(f, G.text_img(sp["subheading"], "Medium", 32, S.MUTED, max_w=1600), (S.SAFE_X + 20, 222), o)
        self.chart.render(f, t, self)
        self.draw_common(f, t)


class Outro(Scene):
    def draw(self, f, t):
        sp = self.spec
        o = G.appear(t, 0.1, 0.7)
        h = G.text_img(sp["heading"], "Black", 84, S.FG, max_w=1500, align="center", highlight=sp.get("highlight", ""))
        G.blit(f, h, (S.W / 2, 260 + (1 - o) * 30), o, "mt")
        y = 260 + h.height + 50
        if sp.get("sub"):
            s = G.text_img(sp["sub"], "SemiBold", 42, S.MUTED, max_w=1500, align="center")
            G.blit(f, s, (S.W / 2, y), G.appear(t, 0.6), "mt")
            y += s.height + 60
        o = G.appear(t, self.line_start(sp.get("subscribe_on", len(self.narration))))
        p = G.pill("구독  ·  좋아요  ·  알림 설정", "ExtraBold", 40, (16, 20, 32), S.GOLD, pad=(44, 18))
        G.blit(f, p, (S.W / 2, y + 20), o, "mt")
        if sp.get("disclaimer"):
            G.blit(f, G.text_img(sp["disclaimer"], "Medium", 26, S.MUTED, max_w=1400, align="center"),
                   (S.W / 2, 840), G.appear(t, 0.8), "mt")
        self.draw_common(f, t)


TYPES = {"title": Title, "quote": Quote, "card": Card, "chart": Chart, "bars": Bars, "outro": Outro}


def make(spec, idx, channel):
    return TYPES[spec["type"]](spec, idx, channel)


# ── 화면 위에 항상 붙는 것들(로고·챕터·자막·진행바·면책) ─────────────
def chrome(f, scene, t_global, total, channel):
    G.blit(f, G.text_img(channel.get("name", "채널명"), "ExtraBold", 28, S.GOLD), (S.SAFE_X - 40, 48), 0.9)
    ch = scene.spec.get("chapter")
    if ch:
        G.blit(f, G.pill(ch, "Bold", 26, S.FG, S.PANEL, pad=(22, 9)), (S.W - S.SAFE_X + 40, 44), 0.95, "rt")
    if channel.get("disclaimer_corner"):
        G.blit(f, G.text_img(channel["disclaimer_corner"], "Regular", 20, S.MUTED), (S.W - S.SAFE_X + 40, 96), 0.7, "rt")
    p = t_global / max(total, 1e-6)
    bar = Image.new("RGBA", (max(1, int(S.W * p)), 6), S.GOLD + (230,))
    G.blit(f, bar, (0, S.H - 6))


def subtitle(f, text):
    if not text:
        return
    t = _sub_img(text)
    G.blit(f, t, (S.W / 2, S.SUB_Y), 1, "mb")


_subs = {}


def _sub_img(text):
    if text not in _subs:
        fnt_size = 46
        tx = G.text_img(text, "Bold", fnt_size, S.FG, max_w=1500, align="center")
        pad = (34, 14)
        bg = G.panel(tx.width + pad[0] * 2, tx.height + pad[1] * 2, (6, 8, 16), 16, alpha=200)
        bg.alpha_composite(tx, pad)
        _subs[text] = bg
    return _subs[text]
