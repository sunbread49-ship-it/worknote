"""장면 타입별 렌더러. 에피소드 YAML의 각 scene → 여기 클래스 하나.

공통 키:
  type, chapter, narration(리스트: 녹음·자막 단위 문장)
  callouts: [{on, label, value, sub, pos:[x,y], color}]   숫자 강조 박스
  illust:   {name: gauge|newspaper|warning, pos:[x,y], size, on, until, needle:[[줄번호, 값], ...]}
  (callouts/illust 의 until: N = N번째 줄에서 사라짐)
  note:     화면 하단 작은 각주
시간 지정 `on: N` = 내레이션 N번째 줄(1부터)이 시작될 때 등장.
"""
import math

from PIL import Image, ImageDraw

from . import charts as C
from . import draw as G
from . import illust as I
from . import style as S

COLORS = {"gold": S.GOLD, "up": S.UP, "down": S.DOWN, "fg": S.FG, "muted": S.MUTED, "neutral": S.NEUTRAL}


def col(c, default=S.FG):
    if c is None:
        return default
    if isinstance(c, (list, tuple)):
        return tuple(c)
    return COLORS.get(c, default)


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
            o = G.appear(t, self.line_start(il.get("on", 1)), 0.35)
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
        self.draw_fun(f, t)

    def draw(self, f, t):
        raise NotImplementedError

    # ── 재미 요소 ──────────────────────────────────────────────
    def _t_of(self, item, key="on"):
        return self.line_start(item.get(key, 1)) + item.get("offset", 0.0)

    def draw_fun(self, f, t):
        for st in self.spec.get("stickers", []):
            t0 = self._t_of(st)
            if t < t0:
                continue
            o = 1.0
            if st.get("until"):
                o = 1 - G.appear(t, self.line_start(st["until"]), 0.3)
                if o <= 0:
                    continue
            k = (t - t0) / 0.25
            sc = 0 if k <= 0 else (1.18 * G.ease_out(k / 0.6) if k < 0.6 else 1.18 - 0.18 * G.ease_out((k - 0.6) / 0.4))
            sc = min(sc, 1.18) if k < 1 else 1.0
            bob = math.sin((t - t0) * 2.4 + st["pos"][0]) * 6 if st.get("float", True) else 0
            size = max(4, int(st.get("size", 180) * sc))
            im = I.emoji(st["e"], size)
            if st.get("rot"):
                im = im.rotate(st["rot"], resample=Image.BICUBIC, expand=True)
            G.blit(f, im, (st["pos"][0], st["pos"][1] + bob), o, "mm")
        m = self.spec.get("mascot")
        if m:
            t0 = self._t_of(m)
            o = G.appear(t, t0, 0.35)
            if m.get("until"):
                o *= 1 - G.appear(t, self.line_start(m["until"]), 0.3)
            if o > 0:
                size = m.get("size", 170)
                x, y = m.get("pos", [S.W - S.SAFE_X - size // 2, 760])
                hop = -abs(math.sin((t - t0) * 9)) * 10 * max(0, 1 - (t - t0) / 0.8)
                G.blit(f, _mascot(size), (x, y + hop + (1 - o) * 40), o, "mm")
                if m.get("say"):
                    ob = G.appear(t, t0 + 0.25, 0.3)
                    b = _bubble(m["say"], m.get("side", "left"))
                    bx = x - size / 2 - 10 if m.get("side", "left") == "left" else x + size / 2 + 10
                    G.blit(f, b, (bx, y - size / 2 + 10), o * ob, "rb" if m.get("side", "left") == "left" else "lb")
        stp = self.spec.get("stamp")
        if stp:
            t0 = self._t_of(stp)
            if t >= t0:
                k = G.clamp((t - t0) / 0.22)
                sc = 2.2 - 1.2 * G.ease_out(k)
                im = _stamp(stp["text"], col(stp.get("color"), S.UP), stp.get("size", 64))
                im = im.resize((max(2, int(im.width * sc)), max(2, int(im.height * sc))), Image.BICUBIC)
                im = im.rotate(stp.get("rot", -8), resample=Image.BICUBIC, expand=True)
                G.blit(f, im, stp.get("pos", [S.W / 2, S.H / 2]), min(1, k * 1.5), "mm")

    # ── 카메라: 문장마다 줌/팬 → 정지 화면 없애기 ─────────────────
    def camera_keys(self):
        """[(시각, cx, cy, zoom)] — spec.camera 로 직접 지정하거나 자동 생성"""
        if hasattr(self, "_cam"):
            return self._cam
        sp = self.spec
        cam = sp.get("camera", "off")
        keys = [(0.0, S.W / 2, S.H / 2, 1.0)]
        if cam == "off":
            keys = []
        elif isinstance(cam, list):
            for c in cam:
                keys.append((self.line_start(c.get("on", 1)) + c.get("offset", 0), c.get("x", S.W / 2),
                             c.get("y", S.H / 2), c.get("zoom", 1.0)))
        else:
            keys += self.auto_camera()
        self._cam = sorted(keys)
        return self._cam

    def auto_camera(self):
        """기본: 문장이 바뀔 때마다 살짝 다른 구도로 밀고 당기기"""
        out = []
        n = len(self.lines)
        pattern = [(1.07, -60, -20), (1.0, 0, 0), (1.1, 70, 10), (1.03, -30, 20)]
        for i in range(1, n):
            z, dx, dy = pattern[(i - 1 + self.idx) % len(pattern)]
            out.append((self.lines[i][0], S.W / 2 + dx, S.H / 2 + dy, z))
        return out

    def camera_at(self, t):
        keys = self.camera_keys()
        if not keys:
            return S.W / 2, S.H / 2, 1.0
        prev = keys[0]
        cur = keys[0]
        for k in keys:
            if k[0] <= t:
                prev, cur = cur, k
        if cur is keys[0]:
            return cur[1:]
        e = G.ease_in_out((t - cur[0]) / self.spec.get("cam_dur", 0.8))
        return tuple(prev[i] + (cur[i] - prev[i]) * e for i in (1, 2, 3))

    def shake_at(self, t):
        for sh in self.spec.get("shake", []):
            t0 = self._t_of(sh)
            d = sh.get("dur", 0.45)
            if t0 <= t < t0 + d:
                a = sh.get("amp", 14) * (1 - (t - t0) / d)
                return int(a * math.sin(t * 93)), int(a * math.cos(t * 71))
        return 0, 0

    def sfx_events(self):
        """[(장면 기준 시간, 효과음 이름, 볼륨)]"""
        ev = []
        for st in self.spec.get("stickers", []):
            if st.get("sfx", "pop") != "none":
                ev.append((self._t_of(st), st.get("sfx", "pop"), st.get("vol", 0.8)))
        m = self.spec.get("mascot")
        if m and m.get("say"):
            ev.append((self._t_of(m) + 0.25, m.get("sfx", "bubble"), 0.7))
        stp = self.spec.get("stamp")
        if stp:
            ev.append((self._t_of(stp) + 0.15, stp.get("sfx", "boom"), 0.9))
        for x in self.spec.get("sfx", []):
            ev.append((self._t_of(x), x["name"], x.get("vol", 1.0)))
        for sh in self.spec.get("shake", []):
            if sh.get("sfx"):
                ev.append((self._t_of(sh), sh["sfx"], 1.0))
        return ev + self.extra_sfx()

    def extra_sfx(self):
        return []


_ill = {}


def _illust_cached(name, size, kw):
    key = (name, size, kw)
    if key not in _ill:
        if len(_ill) > 400:
            _ill.clear()
        _ill[key] = I.get(name, size, **dict(kw))
    return _ill[key]


_co = {}
_cache2 = {}


def _logo(name):
    """모든 슬라이드 왼쪽 위 채널 로고(개미 배지 + 채널명) — 재업로드·도용 방지용 각인"""
    k = ("logo", name)
    if k not in _cache2:
        from .character import logo_badge
        b = logo_badge(110)
        t = G.text_img(name, "Black", 24, (255, 255, 255), stroke=3, stroke_fill=(10, 12, 20))
        im = Image.new("RGBA", (max(b.width, t.width) + 4, b.height + t.height + 4), (0, 0, 0, 0))
        im.alpha_composite(b, ((im.width - b.width) // 2, 0))
        im.alpha_composite(t, ((im.width - t.width) // 2, b.height + 2))
        _cache2[k] = im
    return _cache2[k]


def _mascot(size):
    k = ("m", size)
    if k not in _cache2:
        _cache2[k] = I.mascot(size)
    return _cache2[k]


def _bubble(text, side="left"):
    k = ("b", text, side)
    if k not in _cache2:
        tx = G.text_img(text, "ExtraBold", 34, (20, 22, 30), max_w=520)
        w, h = tx.width + 48, tx.height + 30
        im, d = G.supersample(w + 30, h + 26, 2)
        d.rounded_rectangle((0, 0, w * 2, h * 2), radius=36, fill=(255, 255, 255, 255))
        if side == "left":  # 꼬리: 오른쪽 아래(마스코트 쪽)
            d.polygon([(w * 2 - 70, h * 2 - 6), (w * 2 + 50, h * 2 + 46), (w * 2 - 10, h * 2 - 30)], fill=(255, 255, 255, 255))
        else:
            d.polygon([(70, h * 2 - 6), (-0, h * 2 + 46), (10, h * 2 - 30)], fill=(255, 255, 255, 255))
        out = G.finish(im)
        out.alpha_composite(tx, (24, 15))
        _cache2[k] = out
    return _cache2[k]


def _stamp(text, color, size):
    k = ("s", text, color, size)
    if k not in _cache2:
        tx = G.text_img(text, "Black", size, color)
        w, h = tx.width + 60, tx.height + 30
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((3, 3, w - 4, h - 4), radius=14, outline=color + (255,), width=8, fill=(10, 12, 20, 200))
        im.alpha_composite(tx, (30, 14))
        _cache2[k] = im
    return _cache2[k]


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
        if sp.get("skyline"):
            if not hasattr(self, "_sky"):
                self._sky = I.skyline()
            G.blit(f, self._sky, (0, S.H - self._sky.height + 170 - 20 * G.clamp(t / 8)), 0.75)
        if self.chart:
            G.blit(f, self.chart.line, (0, 0), 0.22)
        y = sp.get("y", 300)
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
    """heading + bullets. 항목이 2개 이하면 자동으로 화면 가운데에 크게 배치."""

    def _items(self):
        sp = self.spec
        out = []
        for i, b in enumerate(sp.get("bullets", [])):
            out.append({"text": b} if isinstance(b, str) else b)
        return out

    def draw(self, f, t):
        sp = self.spec
        items = self._items()
        few = len(items) <= 2 and not sp.get("illust") and sp.get("center", True)
        size = sp.get("size", 46) if not few else max(sp.get("size", 46), 58)
        hsize = sp.get("heading_size", 72) if not few else max(sp.get("heading_size", 72), 84)
        x = sp.get("x", S.SAFE_X + 20)
        maxw = sp.get("width", S.W - x - S.SAFE_X)
        h = G.text_img(sp["heading"], "Black", hsize, S.FG, max_w=maxw, highlight=sp.get("highlight", ""))
        rows = []
        for i, b in enumerate(items):
            tx = G.text_img(b["text"], "Bold", size, S.FG, max_w=maxw - 110,
                            highlight=b.get("highlight", ""), hl_fill=col(b.get("hl_color"), S.GOLD))
            st = G.text_img(b["sub"], "Medium", int(size * 0.68), S.MUTED, max_w=maxw - 110) if b.get("sub") else None
            rows.append((b, tx, st))
        gap = sp.get("gap", 44)
        block = h.height + 60 + sum(tx.height + (st.height + 10 if st else 0) + gap for _, tx, st in rows)
        if few:
            x = S.W / 2 - max([h.width] + [tx.width + 92 for _, tx, _ in rows]) / 2
            y = (S.H - block) / 2 - 40
        else:
            y = sp.get("y", 190)
        o = G.appear(t, self.line_start(sp.get("heading_on", 1)))
        G.blit(f, h, (x, y + (1 - o) * 24), o)
        y += h.height + 60
        for i, (b, tx, st) in enumerate(rows):
            o = G.appear(t, self.line_start(b.get("on", 1)) + b.get("offset", 0))
            if sp.get("numbered"):
                icon = I.number_badge(i + 1, 64)
            elif sp.get("icon") == "dash":
                icon = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                ImageDraw.Draw(icon).rounded_rectangle((8, 28, 40, 36), radius=4, fill=S.GOLD + (255,))
            else:
                icon = I.check(56, col(b.get("color"), S.GOLD))
            dy = (1 - o) * 24
            G.blit(f, icon, (x, y + dy + 2 + max(0, (tx.height - 64) // 2 if few else 0)), o)
            G.blit(f, tx, (x + 92, y + dy + 4), o)
            yy = y + tx.height + 4
            if st:
                G.blit(f, st, (x + 92, yy + 6 + dy), o)
                yy += st.height + 6
            y = yy + gap
        self.draw_common(f, t)


class Chart(Scene):
    def prepare(self):
        self.chart = C.LineChart(self.spec["chart"])

    def auto_camera(self):
        marks = self.spec["chart"].get("marks", [])
        if not marks:
            return super().auto_camera()
        out = []
        used = set()
        rx, ry, rw, rh = self.chart.rect
        for i, m in enumerate(marks):
            on = m.get("on", 1)
            if on in used:  # 같은 줄에 여러 마커면 첫 번째로만
                continue
            used.add(on)
            (mx, my), _ = self.chart.point_at(m["date"], m.get("line", 0))
            z = m.get("zoom", self.spec.get("mark_zoom", 1.45))
            t0 = self.line_start(on) + 0.15
            out.append((t0, mx + m.get("dx", 0) * 0.5, my + m.get("dy", 0) * 0.5, z))
            # 다음 줄에서 한 발 물러나기
            nxt = on + 1
            if nxt <= len(self.lines) and not any(mm.get("on", 1) == nxt for mm in marks):
                out.append((self.line_start(nxt) + 0.1, S.W / 2, S.H / 2, 1.04))
        # 그려지는 동안은 선 끝을 따라 천천히
        return out

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
            G.blit(f, G.text_img(sp["heading"], "ExtraBold", 50, S.FG, max_w=1500), (200, 150), o)
        if sp.get("subheading"):
            o = G.appear(t, self.line_start(sp.get("subheading_on", 1)))
            G.blit(f, G.text_img(sp["subheading"], "Medium", 32, S.MUTED, max_w=1500), (200, 222), o)
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
        if sp.get("signature"):
            so = G.appear(t, self.line_start(sp.get("signature_on", len(self.narration))), 0.5)
            G.blit(f, G.text_img(sp["signature"], "Black", 52, S.GOLD, max_w=1500, align="center"),
                   (S.W / 2, y + 140 + (1 - so) * 20), so, "mt")
        if sp.get("disclaimer"):
            G.blit(f, G.text_img(sp["disclaimer"], "Medium", 24, S.MUTED, max_w=1400, align="center"),
                   (S.W / 2, 870), G.appear(t, 0.8), "mt")
        self.draw_common(f, t)


class Reddit(Scene):
    """커뮤니티 글 카드 (실제 글 캡처가 아니라 '자주 보이는 글 유형'을 재구성).
    posts: [{title, en, up, comments, flair, on, color}]"""

    def draw(self, f, t):
        sp = self.spec
        o = G.appear(t, 0.1)
        hdr = _sub_header(sp.get("community", "r/wallstreetbets"), sp.get("community_sub", "미국 최대 주식 커뮤니티"))
        G.blit(f, hdr, (S.SAFE_X + 20, 140), o)
        y = 140 + hdr.height + 30
        for i, p in enumerate(sp["posts"]):
            t0 = self.line_start(p.get("on", 1)) + p.get("offset", 0)
            k = (t - t0) / 0.3
            if k <= 0:
                continue
            card = _post_card(p, sp.get("width", 1080))
            x = S.SAFE_X + 20 + (1 - G.ease_out(k)) * -60
            G.blit(f, card, (x, y), G.ease_out(k))
            y += card.height + 22
        G.blit(f, G.text_img(sp.get("disclaimer", "※ 자주 보이는 글 유형을 재구성한 예시 (실제 게시글·작성자 아님)"),
                             "Regular", 22, S.MUTED), (S.SAFE_X + 20, y), o)
        self.draw_common(f, t)

    def extra_sfx(self):
        return [(self.line_start(p.get("on", 1)) + p.get("offset", 0), "pop", 0.6) for p in self.spec["posts"]]


def _sub_header(name, sub):
    k = ("hdr", name, sub)
    if k not in _cache2:
        a = G.text_img(name, "Black", 46, S.FG)
        b = G.text_img(sub, "SemiBold", 28, S.MUTED)
        icon, d = G.supersample(72, 72, 3)
        d.ellipse((0, 0, 215, 215), fill=(255, 88, 30, 255))
        icon = G.finish(icon, 3)
        r = G.text_img("r/", "Black", 34, (255, 255, 255))
        icon.alpha_composite(r, ((72 - r.width) // 2, (72 - r.height) // 2 - 2))
        im = Image.new("RGBA", (72 + 20 + a.width + 18 + b.width + 4, 80), (0, 0, 0, 0))
        im.alpha_composite(icon, (0, 4))
        im.alpha_composite(a, (92, -4))
        im.alpha_composite(b, (92 + a.width + 18, 12))
        _cache2[k] = im
    return _cache2[k]


FLAIR = {"Gain": (64, 190, 120), "Loss": (240, 84, 84), "YOLO": (255, 160, 40), "DD": (90, 150, 255),
         "Meme": (180, 120, 255), "Discussion": (130, 140, 160)}


def _post_card(p, width):
    k = ("post", p["title"], p.get("en", ""), width)
    if k not in _cache2:
        x = 150
        title = G.text_img(p["title"], "Bold", 36, S.FG, max_w=width - x - 40)
        en = G.text_img(p["en"], "Medium", 22, S.MUTED, max_w=width - x - 40) if p.get("en") else None
        meta = G.text_img("u/●●●●●  ·  " + p.get("ago", "3시간 전") + "  ·  댓글 " + p.get("comments", ""),
                          "Medium", 22, S.MUTED)
        fl = p.get("flair")
        pill = G.pill(fl, "ExtraBold", 22, (16, 20, 32), FLAIR.get(fl, S.GOLD), pad=(12, 4)) if fl else None
        h = 22 + meta.height + 8 + (pill.height + 8 if pill else 0) + title.height + (en.height + 4 if en else 0) + 22
        h = max(h, 170)
        im = G.panel(width, h, (26, 30, 44), 22, outline=(60, 66, 90, 255), alpha=245)
        cy = h // 2
        up = G.text_img("▲", "Black", 32, (255, 110, 60))
        im.alpha_composite(up, (60 - up.width // 2, cy - 62))
        cnt = G.text_img(p.get("up", ""), "ExtraBold", 28, S.FG)
        im.alpha_composite(cnt, (60 - cnt.width // 2, cy - 20))
        dn = G.text_img("▼", "Black", 32, (110, 130, 200))
        im.alpha_composite(dn, (60 - dn.width // 2, cy + 22))
        y = 22
        im.alpha_composite(meta, (x, y))
        y += meta.height + 8
        if pill:
            im.alpha_composite(pill, (x, y))
            y += pill.height + 8
        im.alpha_composite(title, (x, y))
        y += title.height + 4
        if en:
            im.alpha_composite(en, (x, y))
        _cache2[k] = im
    return _cache2[k]


class BigNum(Scene):
    """숫자 카운트업 공개.  label / from / to / fmt("×{:.0f}") / on / dur / sub / color / sub_on"""

    def draw(self, f, t):
        sp = self.spec
        o = G.appear(t, 0.1)
        if sp.get("label"):
            G.blit(f, G.text_img(sp["label"], "ExtraBold", 54, S.FG, max_w=1600, align="center",
                                 highlight=sp.get("highlight", "")), (S.W / 2, sp.get("y", 250)), o, "mt")
        t0 = self.line_start(sp.get("on", 1)) + sp.get("offset", 0.2)
        dur = sp.get("dur", 1.0)
        k = G.clamp((t - t0) / dur)
        if t >= t0:
            e = 1 - (1 - k) ** 4
            if sp.get("log_count"):
                a, b = math.log10(abs(sp["from"]) + 1e-9), math.log10(abs(sp["to"]) + 1e-9)
                v = math.copysign(10 ** (a + (b - a) * e), sp["to"])
            else:
                v = sp["from"] + (sp["to"] - sp["from"]) * e
            txt = sp.get("fmt", "{:,.0f}").format(v)
            if k >= 1 and sp.get("final"):
                txt = sp["final"]
            c = col(sp.get("color"), S.GOLD)
            num = G.text_img(txt, "Black", sp.get("size", 200), c)
            pop = 1 + 0.08 * math.sin(G.clamp((t - t0 - dur) / 0.25) * math.pi) if k >= 1 else 1
            if pop != 1:
                num = num.resize((int(num.width * pop), int(num.height * pop)), Image.BICUBIC)
            G.blit(f, num, (S.W / 2, sp.get("num_y", 520)), 1, "mm")
        if sp.get("sub"):
            so = G.appear(t, self.line_start(sp.get("sub_on", 1)) + (0 if sp.get("sub_on") else t0 + dur))
            G.blit(f, G.text_img(sp["sub"], "SemiBold", 40, S.MUTED, max_w=1500, align="center"),
                   (S.W / 2, sp.get("sub_y", 690)), so, "mt")
        self.draw_common(f, t)

    def extra_sfx(self):
        sp = self.spec
        t0 = self.line_start(sp.get("on", 1)) + sp.get("offset", 0.2)
        ev = [(t0 - 0.1, "riser", 0.5)] if sp.get("riser", True) else []
        return ev + [(t0 + sp.get("dur", 1.0), sp.get("sfx_end", "ding"), 1.0)]


class Versus(Scene):
    """좌우 비교 카드. left/right: {title, value, sub, color, on, emoji}"""

    def draw(self, f, t):
        sp = self.spec
        if sp.get("heading"):
            G.blit(f, G.text_img(sp["heading"], "ExtraBold", 54, S.FG, max_w=1600, align="center",
                                 highlight=sp.get("highlight", "")), (S.W / 2, 150), G.appear(t, 0.1), "mt")
        for i, side in enumerate(("left", "right")):
            c = sp[side]
            o = G.appear(t, self.line_start(c.get("on", 1)))
            if o <= 0:
                continue
            card = _vs_card(c)
            x = S.W / 2 + (-1 if i == 0 else 1) * (card.width / 2 + 95)
            G.blit(f, card, (x, 330 + (1 - o) * 40), o, "mt")
        ov = G.appear(t, self.line_start(sp["right"].get("on", 1)))
        if ov > 0:
            G.blit(f, G.text_img("VS", "Black", 80, S.GOLD), (S.W / 2, 570), ov, "mm")
        self.draw_common(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec[s].get("on", 1)), "pop", 0.7) for s in ("left", "right")]


def _vs_card(c):
    k = ("vs", str(c))
    if k not in _cache2:
        color = col(c.get("color"), S.GOLD)
        w, h = 660, 480
        im = G.panel(w, h, S.PANEL, 30, outline=color + (160,))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, 12), radius=6, fill=color + (255,))
        y = 40
        if c.get("emoji"):
            e = I.emoji(c["emoji"], 110)
            im.alpha_composite(e, (w - 150, 34))
        tt = G.text_img(c["title"], "ExtraBold", 46, S.FG, max_w=w - 200)
        im.alpha_composite(tt, (44, y + 10))
        y += tt.height + 70
        vs = 110
        v = G.text_img(c["value"], "Black", vs, color)
        while v.width > w - 88 and vs > 50:
            vs -= 8
            v = G.text_img(c["value"], "Black", vs, color)
        im.alpha_composite(v, (44, y))
        y += v.height + 16
        if c.get("sub"):
            st = G.text_img(c["sub"], "SemiBold", 32, S.MUTED, max_w=w - 88)
            im.alpha_composite(st, (44, y))
        _cache2[k] = im
    return _cache2[k]


class Kinetic(Scene):
    default_transition = "up"
    """핵심 문장을 크게 한 줄씩 (키네틱 타이포그래피). 화면 전환용.
    items: [{text, on, size, color, highlight, hl_color, sub}], bg_word: 배경 워터마크, stack: 이전 줄 유지"""

    def draw(self, f, t):
        sp = self.spec
        if sp.get("bg_word"):
            wm = G.text_img(sp["bg_word"], "Black", sp.get("bg_size", 420), col(sp.get("bg_color"), S.GOLD))
            G.blit(f, wm, (S.W / 2 + 40 - t * 12, S.H / 2 - 40), 0.07, "mm")
        items = sp["items"]
        starts = [self.line_start(it.get("on", 1)) + it.get("offset", 0) for it in items]
        cur = max([i for i, st in enumerate(starts) if t >= st] or [-1])
        if cur < 0:
            return self.draw_common(f, t)
        stack = sp.get("stack", False)
        shown = list(range(cur + 1)) if stack else [cur]
        total_h = 0
        imgs = []
        for i in shown:
            it = items[i]
            im = G.text_img(it["text"], "Black", it.get("size", 110), col(it.get("color"), S.FG), max_w=1640,
                            align="center", highlight=it.get("highlight", ""), hl_fill=col(it.get("hl_color"), S.GOLD),
                            line_gap=1.15)
            sub = G.text_img(it["sub"], "SemiBold", 40, S.MUTED, max_w=1500, align="center") if it.get("sub") else None
            imgs.append((i, im, sub))
            total_h += im.height + (sub.height + 18 if sub else 0) + 40
        y = S.H / 2 - total_h / 2 - 30
        for i, im, sub in imgs:
            k = G.ease_out((t - starts[i]) / 0.3)
            op = 1.0 if (i == cur or not stack) else 0.35
            sc_ = 1.08 - 0.08 * k
            im2 = im.resize((max(1, int(im.width * sc_)), max(1, int(im.height * sc_))), Image.BILINEAR) if k < 1 else im
            G.blit(f, im2, (S.W / 2, y + (1 - k) * 50), op * k, "mt")
            # 밑줄 강조 바
            if i == cur:
                bw = int(min(im.width, 900) * G.ease_out((t - starts[i] - 0.15) / 0.4))
                if bw > 2:
                    bar = Image.new("RGBA", (bw, 8), col(items[i].get("hl_color"), S.GOLD) + (255,))
                    G.blit(f, bar, (S.W / 2, y + im.height + 10), op, "mt")
            y += im.height + 40
            if sub:
                G.blit(f, sub, (S.W / 2, y), op * G.ease_out((t - starts[i] - 0.2) / 0.3), "mt")
                y += sub.height + 18
        self.draw_common(f, t)

    def auto_camera(self):
        out = []
        for i, it in enumerate(self.spec["items"]):
            z = 1.0 if i % 2 == 0 else 1.05
            out.append((self.line_start(it.get("on", 1)) + it.get("offset", 0), S.W / 2, S.H / 2, z))
        return out

    def extra_sfx(self):
        return [(self.line_start(it.get("on", 1)) + it.get("offset", 0), it.get("sfx", "whoosh"), 0.18)
                for it in self.spec["items"] if it.get("sfx", "whoosh") != "none"]


class Punch(Scene):
    """훅 비주얼: 컬러 풀스크린 + 큰 숫자 '쾅' (engine/punch.py). 롱폼에 3~6번만, 핵심 포인트에서.
    spec: tone(up|down|gold), label, big, sub, on(큰 글자 등장 문장), sub_on, mascot"""
    default_transition = "cut"

    def draw(self, f, t):
        from . import punch as P
        sp = self.spec
        t0 = self.line_start(sp.get("on", 1))
        k = G.clamp((t - t0) / 0.28)
        k_sub = G.appear(t, self.line_start(sp.get("sub_on", sp.get("on", 1))) + 0.35, 0.3)
        k_m = G.appear(t, t0 + 0.3, 0.45)
        im = P.compose(S.W, S.H, sp, k, k_sub, k_m)
        f.paste(im, (0, 0))
        # 등장 순간 흰 번쩍임 (0.12초)
        fl = 1 - G.clamp((t - t0) / 0.12)
        if t >= t0 and fl > 0:
            f.alpha_composite(Image.new("RGBA", f.size, (255, 255, 255, int(150 * fl))))
        self.draw_common(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec.get("on", 1)), self.spec.get("sfx", "boom"), 0.45)]


class YearBars(Scene):
    """연도별 막대 (예: 중간선거일 → 1년 뒤 수익률). spec: which(midterm|pres), heading, on, mark: {연도: 라벨}"""

    def prepare(self):
        from . import data as D
        sp = self.spec
        w = sp.get("which", "midterm")
        if sp.get("items"):  # 직접 값 목록 [[라벨, 값], ...]
            self.items = [tuple(x) for x in sp["items"]]
        elif w.startswith("cycle"):
            self.items = D.cycle_years_list(int(w[-1]))
        elif w == "dd":  # 하락장 매수: 연도 → years년 뒤 수익률
            self.items = [(e[0].year, e[2]) for e in D.dd_events(sp.get("th", -0.3), sp.get("since", "1927"), sp.get("years", 5))]
        elif w == "season":  # 같은 해 겨울 - 여름 (%p)
            wv = dict(D.seasons(sp.get("series", "spx"), "winter", sp.get("y0", 1950), sp.get("y1", 2025)))
            sv = dict(D.seasons(sp.get("series", "spx"), "summer", sp.get("y0", 1950), sp.get("y1", 2025)))
            self.items = [(y, (wv[y] - sv[y]) * 100) for y in sorted(wv) if y in sv]
        elif w == "crash":  # 나스닥100 -6% 하락일 → 1년(252거래일) 뒤 수익률
            self.items = [(e[0].strftime("%y.%m"), e[2]) for e in D.crash_days(sp.get("th", -0.06))]
        elif w == "vix":  # VIX 첫 돌파일 → 3배 레버리지 1년 수익률
            self.items = [(e[0].strftime("%y.%m"), e[3]) for e in D.vix_events(sp.get("level", 40))]
        else:
            self.items = D.elec_fwd(w, sp.get("y0", 1950), sp.get("y1", 2022))

    def draw(self, f, t):
        sp = self.spec
        if sp.get("heading"):
            G.blit(f, G.text_img(sp["heading"], "ExtraBold", 50, S.FG, max_w=1500, highlight=sp.get("highlight", "")),
                   (200, 150), G.appear(t, 0.1))
        if sp.get("sub"):
            G.blit(f, G.text_img(sp["sub"], "Medium", 30, S.MUTED), (200, 222), G.appear(t, 0.2))
        x0, base, w, hmax = 200, sp.get("base", 820), 1560, sp.get("hmax", 470)
        label_y = sp.get("label_y")
        n = len(self.items)
        slot = w / n
        vmax = sp.get("vmax") or max(abs(v) for _, v in self.items) * 1.15
        zero = Image.new("RGBA", (w + 40, 3), S.MUTED + (200,))
        G.blit(f, zero, (x0 - 20, base))
        t0 = self.line_start(sp.get("on", 1))
        step = sp.get("step", 0.12)
        for i, (y, v) in enumerate(self.items):
            k = G.ease_out((t - t0 - i * step) / 0.35)
            if k <= 0:
                continue
            c = S.UP if v >= 0 else S.DOWN
            if str(y) in {str(m) for m in sp.get("mark", {})}:
                c = S.GOLD
            bh = max(3, min(abs(v), vmax) / vmax * hmax * k)
            bw = int(slot * 0.62)
            cx = x0 + slot * (i + 0.5)
            bar = Image.new("RGBA", (bw, int(bh)), c + (255,))
            G.blit(f, bar, (cx, base) if v < 0 else (cx, base - bh), 1, "mt" if v < 0 else "mt")
            if n <= 24 or sp.get("values", False):
                G.blit(f, G.text_img(sp.get("fmt", "{:+.0f}").format(v), "Bold", sp.get("val_size", 22), c), (cx, base - bh - 8 if v >= 0 else base + bh + 8),
                   min(1, k * 2), "mb" if v >= 0 else "mt")
            lab = str(y)[2:] if (isinstance(y, int) and n > 14) else str(y)
            if n > 24:  # 막대가 많으면 연도는 10년마다, 'YY.MM 은 연도가 바뀔 때만
                if isinstance(y, int):
                    lab = f"'{y % 100:02d}" if y % 10 == 0 else ""
                else:
                    yy = str(y)[:2]
                    lab = "" if (i and str(self.items[i - 1][0])[:2] == yy) else "'" + yy
            if lab:
                if v < 0 and not label_y:  # 음수 막대는 라벨을 기준선 위로 (막대·값과 겹치지 않게)
                    G.blit(f, G.text_img(lab, "Medium", 22, S.MUTED), (cx, base - 12), min(1, k * 2), "mb")
                else:
                    G.blit(f, G.text_img(lab, "Medium", 22, S.MUTED), (cx, label_y or base + 14), min(1, k * 2), "mt")
        for y, lab in sp.get("mark", {}).items():
            idx = next((i for i, (yy, _) in enumerate(self.items) if str(yy) == str(y)), None)
            if idx is None:
                continue
            o = G.appear(t, self.line_start(sp.get("mark_on", 1)))
            cx = x0 + slot * (idx + 0.5)
            v = self.items[idx][1]
            G.blit(f, G.pill(lab, "Bold", 26, (16, 20, 32), S.GOLD, pad=(14, 6)),
                   (cx, base - min(abs(v), vmax) / vmax * hmax - sp.get("val_size", 26) - 40) if v >= 0 else (cx, base - 50), o, "mb")
        G.blit(f, G.text_img(sp.get("source", "자료: S&P500 지수(배당 제외) · 선거일 종가 → 1년 뒤"), "Regular", 20, S.MUTED),
               (x0 + w, (label_y or base + max([min(abs(v), vmax) / vmax * hmax for _, v in self.items if v < 0] or [0]) + (40 if any(v < 0 for _, v in self.items) else 0)) + 60), 1, "rt")
        self.draw_common(f, t)

    def extra_sfx(self):
        t0 = self.line_start(self.spec.get("on", 1))
        return [(t0 + i * self.spec.get("step", 0.12), "tick", 0.5) for i in range(len(self.items))]


TYPES = {"punch": Punch, "yearbars": YearBars, "kinetic": Kinetic, "reddit": Reddit, "bignum": BigNum, "versus": Versus, "title": Title, "quote": Quote, "card": Card, "chart": Chart, "bars": Bars, "outro": Outro}


def make(spec, idx, channel):
    from . import cutaways, editorial
    types = {**TYPES, **cutaways.TYPES, **editorial.TYPES}
    return types[spec["type"]](spec, idx, channel)


# ── 화면 위에 항상 붙는 것들(로고·챕터·자막·진행바·면책) ─────────────
def chrome(f, scene, t_global, total, channel):
    lg = _logo(channel.get("name", "채널명"))
    G.blit(f, lg, (34, 26), 0.95)
    if channel.get("_series_tag") and scene.spec["type"] not in ("chart", "bars", "yearbars", "versus"):  # 로고 옆 주제 태그 (상단 제목 있는 장면 제외)
        G.blit(f, G.pill(channel["_series_tag"], "SemiBold", 28, S.FG, (40, 46, 62), pad=(20, 8)),
               (34 + lg.width + 18, 26 + lg.height / 2 - 20), 0.85, "lt")
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


def _sub_segments(text):
    """'**노랑**' · '!!빨강!!' 표시를 색 구간으로 (EP012 벤치마킹: 핵심 단어 색 강조)"""
    import re
    out = []
    for part in re.split(r"(\*\*.+?\*\*|!!.+?!!)", text):
        if not part:
            continue
        if part.startswith("**"):
            out.append((part[2:-2], S.GOLD))
        elif part.startswith("!!"):
            out.append((part[2:-2], (255, 96, 96)))
        else:
            out.append((part, S.FG))
    return out


def _sub_img(text):
    if text not in _subs:
        segs = _sub_segments(text)
        fnt = S.font("Bold", 62)   # 자막 크게 (EP012 피드백)
        w = int(sum(fnt.getlength(t) for t, _ in segs)) + 4
        asc, desc = fnt.getmetrics()
        tx = Image.new("RGBA", (w, asc + desc + 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(tx)
        x = 2
        for t_, c in segs:
            d.text((x, 2), t_, font=fnt, fill=c)
            x += fnt.getlength(t_)
        pad = (34, 14)
        bg = G.panel(tx.width + pad[0] * 2, tx.height + pad[1] * 2, (6, 8, 16), 16, alpha=205)
        bg.alpha_composite(tx, pad)
        _subs[text] = bg
    return _subs[text]
