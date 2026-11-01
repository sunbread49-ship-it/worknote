"""분위기 전환용 풀스크린 '컷어웨이' 장면들 (밝은 배경 · 밈 스타일).

  meme      집중선/만화 배경 + 거대 이모지 + 위·아래 밈 자막 (짤 한 장 느낌)
  twopanel  좌우 2컷 밈 (기대 vs 현실, 레딧 vs 데이터)
  phone     스마트폰 화면 연출: account(증권앱 계좌가 녹는 화면) / chat(단톡방 대화)
  news      속보 화면 연출 (가상의 뉴스 그래픽, 실제 방송사 아님)
  media     직접 넣은 사진·AI 이미지·GIF·짧은 영상 풀스크린 (assets/media/)
"""
import math
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import draw as G
from . import illust as I
from . import style as S
from .scenes import Scene, col

BRIGHT = {
    "yellow": ((255, 214, 64), (255, 170, 30)),
    "red": ((255, 92, 92), (200, 30, 50)),
    "blue": ((90, 160, 255), (40, 80, 220)),
    "mint": ((80, 220, 180), (20, 150, 140)),
    "purple": ((170, 120, 255), (100, 50, 200)),
    "pink": ((255, 130, 190), (220, 60, 130)),
    "white": ((250, 248, 240), (225, 222, 210)),
}
INK = (18, 18, 24)


def _bg_colors(name):
    return BRIGHT.get(name, BRIGHT["yellow"])


@lru_cache(maxsize=16)
def _halftone(color):
    """만화 망점 패턴"""
    im = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(0, S.H, 28):
        for x in range(0, S.W, 28):
            r = 2 + 6 * (x / S.W)
            ox = 14 if (y // 28) % 2 else 0
            d.ellipse((x + ox - r, y - r, x + ox + r, y + r), fill=color + (40,))
    return im


def burst(colors, t, cx=S.W / 2, cy=S.H / 2, rays=22, spin=0.15):
    """회전하는 집중선 배경"""
    c1, c2 = colors
    im = Image.new("RGBA", (S.W, S.H), c1 + (255,))
    d = ImageDraw.Draw(im)
    R = 2400
    a0 = t * spin
    for i in range(rays):
        a = a0 + i * 2 * math.pi / rays
        b = a + math.pi / rays
        d.polygon([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a)), (cx + R * math.cos(b), cy + R * math.sin(b))],
                  fill=c2 + (255,))
    im.alpha_composite(_halftone(INK))
    return im


def punch(t, t0, dur=0.3, over=1.25):
    """줌 펀치: 크게 튀어나왔다가 제자리"""
    k = (t - t0) / dur
    if k <= 0:
        return 0.0
    if k < 0.6:
        return over * G.ease_out(k / 0.6)
    if k < 1:
        return over - (over - 1) * G.ease_out((k - 0.6) / 0.4)
    return 1.0


def meme_text(text, size=110, fill=(255, 255, 255), max_w=1700):
    return G.text_img(text, "Black", size, fill, max_w=max_w, align="center", stroke=max(4, size // 12),
                      stroke_fill=INK, line_gap=1.12)


def scaled(im, s):
    if s <= 0.01:
        return None
    if abs(s - 1) < 0.01:
        return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)


class Cutaway(Scene):
    default_transition = "flash"

    def draw_bg(self, f, t, colors=None):
        sp = self.spec
        colors = colors or _bg_colors(sp.get("bg", "yellow"))
        if sp.get("bg_style", "burst") == "burst":
            f.alpha_composite(burst(colors, t, *sp.get("burst_center", (S.W / 2, S.H / 2))))
        else:
            f.alpha_composite(Image.new("RGBA", (S.W, S.H), colors[0] + (255,)))
            f.alpha_composite(_halftone(INK))

    def emoji_layer(self, f, t):
        for e in self.spec.get("emojis", []):
            t0 = self._t_of(e)
            s = punch(t, t0)
            if s <= 0:
                continue
            size = e.get("size", 520)
            wob = math.sin((t - t0) * e.get("wobble", 3.0)) * e.get("swing", 6)
            im = I.emoji(e["e"], size)
            im = im.rotate(e.get("rot", 0) + wob, resample=Image.BICUBIC, expand=True)
            im = scaled(im, s)
            if im is not None:
                G.blit(f, im, e.get("pos", [S.W / 2, S.H / 2]), 1, "mm")

    def sfx_events(self):
        ev = super().sfx_events()
        for e in self.spec.get("emojis", []):
            if e.get("sfx", "pop") != "none":
                ev.append((self._t_of(e), e.get("sfx", "pop"), 0.9))
        return ev


class Meme(Cutaway):
    """top / bottom: 밈 자막, emojis: [{e, pos, size, on, rot}], caption_on"""

    def draw(self, f, t):
        sp = self.spec
        self.draw_bg(f, t)
        self.emoji_layer(f, t)
        if sp.get("top"):
            s = punch(t, self.line_start(sp.get("top_on", 1)) + sp.get("top_offset", 0.05), 0.25, 1.15)
            im = scaled(meme_text(sp["top"], sp.get("top_size", 104)), s)
            if im:
                G.blit(f, im, (S.W / 2, sp.get("top_y", 70)), 1, "mt")
        if sp.get("bottom"):
            s = punch(t, self.line_start(sp.get("bottom_on", 1)) + sp.get("bottom_offset", 0.3), 0.25, 1.15)
            im = scaled(meme_text(sp["bottom"], sp.get("bottom_size", 96), col(sp.get("bottom_color"), (255, 255, 255))), s)
            if im:
                G.blit(f, im, (S.W / 2, sp.get("bottom_y", 900)), 1, "mb")
        self.draw_fun(f, t)


class TwoPanel(Cutaway):
    """left/right: {label, caption, e, bg, on}"""
    default_transition = "slide"

    def draw(self, f, t):
        sp = self.spec
        for i, side in enumerate(("left", "right")):
            c = sp[side]
            t0 = self.line_start(c.get("on", 1))
            x0 = 0 if i == 0 else S.W // 2
            k = G.ease_out((t - t0) / 0.3) if t >= t0 else 0
            if k <= 0:
                continue
            colors = _bg_colors(c.get("bg", "mint" if i == 0 else "red"))
            panel = burst(colors, t, S.W / 4, S.H / 2, rays=16).crop((0, 0, S.W // 2, S.H))
            px = x0 + (1 - k) * (-S.W // 2 if i == 0 else S.W // 2)
            f.alpha_composite(panel, (int(px), 0))
            cx = px + S.W / 4
            lab = G.pill(c["label"], "Black", 54, (255, 255, 255), INK, pad=(34, 14))
            G.blit(f, lab, (cx, 70), 1, "mt")
            s = punch(t, t0 + 0.1)
            em = scaled(I.emoji(c["e"], c.get("size", 380)), s)
            if em:
                G.blit(f, em, (cx, 480), 1, "mm")
            if c.get("caption"):
                cap = meme_text(c["caption"], 64, max_w=S.W // 2 - 80)
                G.blit(f, cap, (cx, 870), 1, "mb")
        line = Image.new("RGBA", (12, S.H), INK + (255,))
        if t >= self.line_start(sp["right"].get("on", 1)):
            G.blit(f, line, (S.W / 2, 0), 1, "mt")
        self.draw_fun(f, t)

    def sfx_events(self):
        return super().sfx_events() + [(self.line_start(self.spec[s].get("on", 1)), "whoosh" if s == "left" else "pop", 0.8)
                                       for s in ("left", "right")]


def _phone_frame(w=500, h=880):
    im, d = G.supersample(w, h, 2)
    d.rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), radius=110, fill=(24, 24, 30, 255))
    d.rounded_rectangle((18, 18, w * 2 - 19, h * 2 - 19), radius=94, fill=(250, 250, 252, 255))
    d.rounded_rectangle((w - 120, 40, w + 120, 92), radius=26, fill=(24, 24, 30, 255))
    return G.finish(im)


class Phone(Cutaway):
    """mode: account | chat
    account: {app, title, from, to (원), drop_on, drop_dur, holdings:[{name, pct}], notes:[{text, on}]}
    chat:    {room, messages:[{who: me|other, name, text, on}]}
    side_text: 오른쪽 큰 문구, side_e: 오른쪽 이모지"""
    default_transition = "zoom"

    def draw(self, f, t):
        sp = self.spec
        self.draw_bg(f, t)
        ph = _phone_frame()
        px, py = sp.get("phone_x", 470), 30
        rise = (1 - G.ease_out(t / 0.35)) * 300
        scr = Image.new("RGBA", (ph.width - 40, ph.height - 40), (0, 0, 0, 0))
        (self._account if sp.get("mode", "account") == "account" else self._chat)(scr, t)
        phone = ph.copy()
        mask = Image.new("L", phone.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((20, 20, phone.width - 21, phone.height - 21), radius=48, fill=255)
        layer = Image.new("RGBA", phone.size, (0, 0, 0, 0))
        layer.paste(scr, (20, 20))
        phone.paste(layer, (0, 0), Image.composite(layer.getchannel("A"), Image.new("L", phone.size, 0), mask))
        shadow = Image.new("RGBA", (phone.width + 80, phone.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((40, 50, phone.width + 40, phone.height + 50), radius=60, fill=(0, 0, 0, 110))
        G.blit(f, shadow.filter(ImageFilter.GaussianBlur(24)), (px, py + rise + phone.height / 2 + 10), 1, "mm")
        G.blit(f, phone, (px, py + rise), 1, "mt")
        if sp.get("side_text"):
            s = punch(t, self.line_start(sp.get("side_on", 1)) + 0.1, 0.25, 1.12)
            im = scaled(meme_text(sp["side_text"], sp.get("side_size", 92), max_w=900), s)
            if im:
                G.blit(f, im, (1300, sp.get("side_y", 330)), 1, "mm")
        self.emoji_layer(f, t)
        self.draw_fun(f, t)

    # 증권앱 계좌 (가상의 앱 화면)
    def _account(self, scr, t):
        sp = self.spec
        d = ImageDraw.Draw(scr)
        W = scr.width
        scr.paste((248, 249, 252, 255), (0, 0, W, scr.height))
        scr.alpha_composite(G.text_img(sp.get("app", "내 주식 계좌"), "ExtraBold", 34, INK), (36, 90))
        scr.alpha_composite(G.text_img("총 평가금액", "SemiBold", 26, (120, 124, 140)), (36, 160))
        t0 = self.line_start(sp.get("drop_on", 1)) + 0.2
        k = G.ease_in_out((t - t0) / sp.get("drop_dur", 2.2)) if t >= t0 else 0
        a, b = sp["from"], sp["to"]
        v = a * (b / a) ** k if a > 0 and b > 0 else a + (b - a) * k
        scr.alpha_composite(G.text_img(_won(v), "Black", 60, INK), (36, 196))
        pct = (v / a - 1) * 100
        c = S.UP if pct >= 0 else S.DOWN
        scr.alpha_composite(G.text_img(f"{pct:+.1f}%  ({_won(v - a, sign=True)})", "Bold", 30, c), (36, 280))
        # 미니 차트
        cw, ch, cy = W - 72, 230, 350
        n = 60
        rng = np.random.default_rng(4)
        path = np.cumsum(rng.normal(0, 1, n))
        path = path - np.linspace(0, path[-1], n)
        target = np.log(np.linspace(1, max(b / a, 1e-3), n)) if b < a else np.log(np.linspace(1, b / a, n))
        y = target + path * 0.04 * abs(target).max()
        m = max(2, int(n * max(k, 0.02)))
        ys = y[:m]
        lo, hi = y.min(), max(y.max(), 0)
        pts = [(36 + i / (n - 1) * cw, cy + ch - (yy - lo) / (hi - lo + 1e-9) * ch) for i, yy in enumerate(ys)]
        if len(pts) > 1:
            d.line(pts, fill=c + (255,), width=5, joint="curve")
        d.line((36, cy + ch + 6, 36 + cw, cy + ch + 6), fill=(220, 222, 230, 255), width=2)
        # 보유 종목
        yy = 620
        for h in sp.get("holdings", []):
            hp = h["pct"] * k
            hc = S.UP if hp >= 0 else S.DOWN
            d.rounded_rectangle((28, yy, W - 28, yy + 92), radius=18, fill=(255, 255, 255, 255), outline=(232, 234, 240, 255))
            scr.alpha_composite(G.text_img(h["name"], "Bold", 32, INK), (52, yy + 26))
            pt = G.text_img(f"{hp:+.1f}%", "ExtraBold", 32, hc)
            scr.alpha_composite(pt, (W - 52 - pt.width, yy + 26))
            yy += 108
        # 알림 배너
        for nt in sp.get("notes", []):
            n0 = self.line_start(nt.get("on", 1)) + nt.get("offset", 0)
            if t < n0:
                continue
            kk = G.ease_out((t - n0) / 0.3)
            ban = Image.new("RGBA", (W - 40, 110), (0, 0, 0, 0))
            ImageDraw.Draw(ban).rounded_rectangle((0, 0, W - 41, 109), radius=24, fill=(40, 42, 52, 240))
            ban.alpha_composite(G.text_img(nt["text"], "Bold", 28, (255, 255, 255), max_w=W - 100), (26, 26))
            scr.alpha_composite(ban, (20, int(-120 + 170 * kk)))

    # 단톡방
    def _chat(self, scr, t):
        sp = self.spec
        W, H = scr.size
        scr.paste((186, 206, 224, 255), (0, 0, W, H))  # 메신저 느낌 하늘색
        ImageDraw.Draw(scr).rectangle((0, 0, W, 150), fill=(170, 192, 212, 255))
        scr.alpha_composite(G.text_img(sp.get("room", "주식 단톡방 (4)"), "Bold", 32, INK), (36, 92))
        shown = [m for m in sp["messages"] if t >= self.line_start(m.get("on", 1)) + m.get("offset", 0)]
        imgs = []
        for m in shown:
            me = m.get("who", "other") == "me"
            tx = G.text_img(m["text"], "SemiBold", 28, INK, max_w=W - 190)
            bw, bh = tx.width + 40, tx.height + 26
            b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
            ImageDraw.Draw(b).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=22,
                                                fill=(255, 235, 51, 255) if me else (255, 255, 255, 255))
            b.alpha_composite(tx, (20, 13))
            imgs.append((me, m.get("name", ""), b, m))
        total = sum(b.height + (40 if (not me and nm) else 0) + 18 for me, nm, b, _ in imgs)
        y = max(170, H - 40 - total)
        for me, nm, b, m in imgs:
            m0 = self.line_start(m.get("on", 1)) + m.get("offset", 0)
            k = G.ease_out((t - m0) / 0.2)
            if not me and nm:
                scr.alpha_composite(G.text_img(nm, "Medium", 22, (60, 66, 80)), (110, int(y)))
                y += 32
                av = I.emoji(m.get("avatar", "monocle"), 64)
                scr.alpha_composite(av, (30, int(y)))
            x = W - 30 - b.width if me else 110
            bb = scaled(b, 0.85 + 0.15 * k)
            if bb:
                scr.alpha_composite(bb, (int(x + (b.width - bb.width) * (1 if me else 0)), int(y)))
            y += b.height + 18

    def sfx_events(self):
        ev = super().sfx_events()
        sp = self.spec
        if sp.get("mode", "account") == "chat":
            ev += [(self.line_start(m.get("on", 1)) + m.get("offset", 0), "bubble", 0.7) for m in sp["messages"]]
        else:
            ev += [(self.line_start(n.get("on", 1)) + n.get("offset", 0), "ding", 0.5) for n in sp.get("notes", [])]
            ev.append((self.line_start(sp.get("drop_on", 1)) + 0.2, "riser", 0.4))
        return ev


def _won(v, sign=False):
    s = "-" if v < 0 else ("+" if sign else "")
    v = abs(v)
    if v >= 1e8:
        x = v / 1e8
        return f"{s}{x:,.2f}억 원".replace(".00억", "억")
    if v >= 1e4:
        return f"{s}{v / 1e4:,.0f}만 원"
    return f"{s}{v:,.0f}원"


class News(Cutaway):
    """속보 화면: tag, headline, sub, ticker"""
    default_transition = "flash"

    def draw(self, f, t):
        sp = self.spec
        f.alpha_composite(burst(((30, 34, 52), (22, 26, 40)), t * 0.3, S.W * 0.75, S.H * 0.3, rays=30))
        k = G.ease_out(t / 0.3)
        bar = Image.new("RGBA", (S.W, 300), (200, 24, 40, 255))
        G.blit(f, bar, (int(-S.W * (1 - k)), 520))
        tag = G.pill(sp.get("tag", "속보"), "Black", 60, (200, 24, 40), (255, 255, 255), pad=(36, 12), radius=10)
        G.blit(f, tag, (140, 470), 1, "lb")
        if t > 0.2:
            G.blit(f, G.text_img(sp["headline"], "Black", sp.get("size", 84), (255, 255, 255), max_w=1640), (140, 560))
        if sp.get("sub"):
            G.blit(f, G.text_img(sp["sub"], "SemiBold", 40, (255, 220, 220), max_w=1640), (140, 720), G.appear(t, 0.5))
        # 하단 티커
        tk = G.text_img("   ·   ".join(sp.get("ticker", [])) + "   ·   ", "Bold", 34, (255, 255, 255))
        strip = Image.new("RGBA", (S.W, 70), (12, 14, 22, 255))
        off = int((t * 260) % max(1, tk.width))
        for x in range(-off, S.W, tk.width):
            strip.alpha_composite(tk, (x, 14))
        G.blit(f, strip, (0, 860))
        G.blit(f, G.text_img("※ 연출 화면 (실제 방송 아님)", "Medium", 22, (170, 175, 190)), (S.W - 120, 440), 1, "rb")
        self.emoji_layer(f, t)
        self.draw_fun(f, t)

    def sfx_events(self):
        return super().sfx_events() + [(0.0, "drum", 0.8)]


class Media(Cutaway):
    """직접 넣은 이미지/GIF/영상 풀스크린.
    file: assets/media/ 안 파일명, caption, kenburns(줌 정도), fit: cover|contain"""
    default_transition = "zoom"
    _frames = {}

    def prepare(self):
        p = S.ROOT / "assets" / "media" / self.spec["file"]
        self.path = p
        self.missing = not p.exists()
        if self.missing:
            return
        if p.suffix.lower() in (".gif", ".mp4", ".mov", ".webm"):
            raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-vf",
                                  f"fps={S.FPS},scale={S.W}:{S.H}:force_original_aspect_ratio=increase,crop={S.W}:{S.H}",
                                  "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True, check=True).stdout
            n = len(raw) // (S.W * S.H * 4)
            self.frames = [Image.frombuffer("RGBA", (S.W, S.H), raw[i * S.W * S.H * 4:(i + 1) * S.W * S.H * 4])
                           for i in range(min(n, 30 * S.FPS))]
        else:
            im = Image.open(p).convert("RGBA")
            s = max(S.W / im.width, S.H / im.height)
            im = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
            self.frames = [im]

    def draw(self, f, t):
        sp = self.spec
        if self.missing:
            self.draw_bg(f, t, _bg_colors("white"))
            G.blit(f, meme_text(f"[이미지 자리]\n{sp['file']}", 70), (S.W / 2, S.H / 2), 1, "mm")
        else:
            fr = self.frames[int(t * S.FPS) % len(self.frames)]
            z = 1 + sp.get("kenburns", 0.08) * G.clamp(t / max(self.dur, 0.1))
            im = fr.resize((int(fr.width * z), int(fr.height * z)), Image.BILINEAR) if z > 1.001 else fr
            G.blit(f, im, (S.W / 2, S.H / 2), 1, "mm")
        if sp.get("credit"):
            G.blit(f, G.text_img(sp["credit"], "Medium", 22, (255, 255, 255), stroke=3), (S.W - 40, S.H - 120), 1, "rb")
        if sp.get("caption"):
            s = punch(t, self.line_start(sp.get("caption_on", 1)) + 0.2, 0.25, 1.12)
            im = scaled(meme_text(sp["caption"], sp.get("caption_size", 90)), s)
            if im:
                G.blit(f, im, (S.W / 2, sp.get("caption_y", 120)), 1, "mt")
        self.emoji_layer(f, t)
        self.draw_fun(f, t)


TYPES = {"meme": Meme, "twopanel": TwoPanel, "phone": Phone, "news": News, "media": Media}
