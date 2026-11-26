"""지식채널 그림 장면 (2026-11-26 서울 동네 이름 편 · 사용자: 글보다 영상 효과로 눈을 사로잡기 · 매 장면 변주)
종이 톤(ivory) 위 손그림 느낌.

type: hanja     한자 타일이 하나씩 툭 떨어져 → 뒤집히며 뜻 카드 → 마지막에 그림(icon)이 튀어나옴
  name: 압구정 · chars: [{h: 狎, ko: 친할 압}, ...] · meaning: '갈매기와 친한 정자' · icon: gull|pavilion|silkworm|hemp|egret|grass|flag|hill|island|pear|pond
type: thennow   옛날 그림 ↔ 지금 그림을 가르는 슬라이더가 좌→우로 쓸고 지나감
  then: {scene: river|mulberry|ferry|island|grass, label} · now: {scene: city, label} · year
type: signflip  도로 표지판(파란 판) — 옛 이름 판이 뜯겨 떨어지고 새 이름이 나타남 (여러 개 차례로)
  signs: [{old, new, sub, on}]
type: quizcard  카드 3장(보기) 중 정답이 뒤집혀 빛남 · 오답은 흐려짐
  question · choices: [텍스트 3개] · answer: 인덱스 · reveal_on
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

from . import draw as G
from . import style as S
from .editorial import Editorial, TYPES, _ink, _marker_text, _sci_frame, _sci_tone, _ff

MJ = "NanumMyeongjo-ExtraBold.ttf"
PEN = "NanumPenScript-Regular.ttf"


def _e(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


# ── 손그림 아이콘 ────────────────────────────────────────
def icon(kind, s, ink, acc, t=0.0):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, a = ink + (255,), acc + (255,)
    w = max(4, s // 40)
    if kind == "gull":
        for k, (x, y, sc) in enumerate(((0.35, 0.45, 1.0), (0.65, 0.3, 0.7), (0.7, 0.62, 0.55))):
            flap = 0.12 * math.sin(t * 6 + k)
            cx, cy, r = s * x, s * y, s * 0.18 * sc
            d.arc((cx - r * 2, cy - r * (0.9 + flap), cx, cy + r * (0.9 + flap)), 200, 340, fill=c, width=w)
            d.arc((cx, cy - r * (0.9 + flap), cx + r * 2, cy + r * (0.9 + flap)), 200, 340, fill=c, width=w)
        d.line((s * 0.05, s * 0.85, s * 0.95, s * 0.85), fill=(90, 150, 210, 255), width=w)
    elif kind == "pavilion":
        d.polygon([(s * 0.15, s * 0.42), (s * 0.85, s * 0.42), (s * 0.7, s * 0.26), (s * 0.3, s * 0.26)], fill=a)
        d.line((s * 0.12, s * 0.42, s * 0.2, s * 0.36), fill=a, width=w)
        d.line((s * 0.88, s * 0.42, s * 0.8, s * 0.36), fill=a, width=w)
        for x in (0.25, 0.42, 0.58, 0.75):
            d.line((s * x, s * 0.42, s * x, s * 0.72), fill=c, width=w)
        d.rectangle((s * 0.18, s * 0.72, s * 0.82, s * 0.78), fill=c)
        d.line((0, s * 0.9, s, s * 0.9), fill=(90, 150, 210, 255), width=w)
    elif kind == "silkworm":
        for i in range(6):
            r = s * (0.09 - i * 0.008)
            x = s * (0.25 + i * 0.1)
            y = s * 0.5 + s * 0.05 * math.sin(t * 4 + i * 0.8)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 246, 236, 255), outline=c, width=w)
        d.ellipse((s * 0.64, s * 0.38, s * 0.86, s * 0.56), fill=(110, 170, 90, 255))   # 뽕잎
    elif kind == "hemp":
        for i in range(5):
            x = s * (0.2 + i * 0.15)
            d.line((x, s * 0.9, x + s * 0.03 * math.sin(t * 2 + i), s * 0.2), fill=(110, 160, 80, 255), width=w)
            for j in range(3):
                y = s * (0.3 + j * 0.18)
                d.line((x, y, x - s * 0.08, y - s * 0.06), fill=(110, 160, 80, 255), width=w)
                d.line((x, y, x + s * 0.08, y - s * 0.06), fill=(110, 160, 80, 255), width=w)
    elif kind == "egret":
        d.ellipse((s * 0.3, s * 0.4, s * 0.65, s * 0.62), fill=(255, 255, 255, 255), outline=c, width=w)
        d.line((s * 0.6, s * 0.45, s * 0.7, s * 0.22), fill=c, width=w)
        d.ellipse((s * 0.66, s * 0.16, s * 0.78, s * 0.26), fill=(255, 255, 255, 255), outline=c, width=w)
        d.line((s * 0.78, s * 0.21, s * 0.92, s * 0.23), fill=a, width=w)
        d.line((s * 0.45, s * 0.62, s * 0.43, s * 0.88), fill=c, width=w)
        d.line((s * 0.52, s * 0.62, s * 0.54, s * 0.88), fill=c, width=w)
        d.line((0, s * 0.88, s, s * 0.88), fill=(90, 150, 210, 255), width=w)
    elif kind == "grass":
        for i in range(9):
            x = s * (0.1 + i * 0.1)
            h = s * (0.3 + 0.25 * ((i * 37) % 5) / 5)
            sway = s * 0.03 * math.sin(t * 3 + i)
            d.line((x, s * 0.88, x + sway, s * 0.88 - h), fill=(110, 160, 80, 255), width=w)
        for i in range(3):
            x = s * (0.25 + i * 0.25)
            d.ellipse((x - 8, s * 0.48 - 8, x + 8, s * 0.48 + 8), fill=(250, 250, 255, 230))   # 서리
    elif kind == "flag":
        d.line((s * 0.3, s * 0.1, s * 0.3, s * 0.9), fill=c, width=w)
        wv = s * 0.04 * math.sin(t * 5)
        d.polygon([(s * 0.3, s * 0.12), (s * 0.78, s * 0.2 + wv), (s * 0.3, s * 0.45)], fill=a)
    elif kind == "hill":
        d.polygon([(0, s * 0.85), (s * 0.5, s * 0.2), (s, s * 0.85)], fill=(140, 170, 110, 255), outline=c)
        d.line((s * 0.2, s * 0.85, s * 0.5, s * 0.45, s * 0.8, s * 0.85), fill=(200, 170, 120, 255), width=w)
    elif kind == "island":
        d.ellipse((s * 0.1, s * 0.5, s * 0.9, s * 0.8), fill=(220, 200, 150, 255), outline=c, width=w)
        for k in range(3):
            y = s * (0.86 + k * 0.04)
            d.arc((s * 0.05, y - 20, s * 0.95, y + 20), 0, 180, fill=(90, 150, 210, 255), width=w // 2 + 1)
    elif kind == "pond":
        d.ellipse((s * 0.12, s * 0.45, s * 0.88, s * 0.85), fill=(150, 200, 230, 255), outline=c, width=w)
        for k in range(2):
            r = s * (0.1 + 0.12 * ((t * 0.8 + k * 0.5) % 1))
            d.ellipse((s * 0.5 - r, s * 0.65 - r * 0.4, s * 0.5 + r, s * 0.65 + r * 0.4), outline=(255, 255, 255, 200), width=3)
    elif kind == "pear":
        for i, (x, y) in enumerate(((0.3, 0.5), (0.55, 0.42), (0.7, 0.62))):
            d.ellipse((s * x - s * 0.1, s * y - s * 0.12, s * x + s * 0.1, s * y + s * 0.12), fill=(230, 210, 110, 255), outline=c, width=w)
        d.line((s * 0.5, s * 0.1, s * 0.5, s * 0.35), fill=(120, 90, 60, 255), width=w)
    elif kind == "walk":
        for i in range(5):
            x = s * (0.15 + i * 0.17)
            d.ellipse((x, s * 0.55 + (i % 2) * s * 0.1, x + s * 0.09, s * 0.62 + (i % 2) * s * 0.1), fill=c)
        G.blit(im, _ink("十里", MJ, int(s * 0.28), acc), (s * 0.5, s * 0.25), 1, "mm")
    return im


# ── 장면 ────────────────────────────────────────────────
class SciBase(Editorial):
    def frame(self, f, t):
        self.tone = _sci_tone(self.spec, getattr(self, "channel", {}))
        _sci_frame(f, self.tone, t)
        self.paper = True

    def title(self, f, t):
        sp = self.spec
        if sp.get("kicker"):
            G.blit(f, _ink(sp["kicker"], PEN, 52, self.tone["acc"]), (S.W / 2, 70), G.appear(t, 0, 0.3), "mt")
        if sp.get("title"):
            tt = _marker_text(sp["title"], sp.get("title_size", 84), self.tone["ink"], self.tone["mark"], sp.get("highlight", ""))
            G.blit(f, tt, (S.W / 2, 130), G.appear(t, 0.05, 0.3), "mt")


class Hanja(SciBase):
    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        chars = sp["chars"]
        n = len(chars)
        tw = 240
        gap = 40
        x0 = S.W / 2 - (n * tw + (n - 1) * gap) / 2
        y = 330
        t0 = self.line_start(sp.get("on", 1))
        flip_t = self.line_start(sp.get("flip_on", 1)) + sp.get("flip_offset", 1.2)
        for i, ch in enumerate(chars):
            ti = t0 + 0.25 * i
            k = _e((t - ti) / 0.45)
            if k <= 0:
                continue
            fk = (t - flip_t - 0.25 * i) / 0.4
            x = x0 + i * (tw + gap)
            yy = y - (1 - k) * 220
            # 뒤집기: 가로 폭을 1 → 0 → 1
            if fk < 0.5:
                sx = 1 - max(0.0, fk) * 2
                front = True
            else:
                sx = min(1.0, (fk - 0.5) * 2)
                front = False
            card = Image.new("RGBA", (tw, tw + 60), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            if front:
                cd.rounded_rectangle((0, 0, tw - 1, tw + 59), 24, fill=(255, 253, 246, 255), outline=tone["ink"] + (255,), width=5)
                hz = _ink(ch["h"], MJ, 170, tone["ink"])
                card.alpha_composite(hz, ((tw - hz.width) // 2, (tw + 60 - hz.height) // 2))
            else:
                cd.rounded_rectangle((0, 0, tw - 1, tw + 59), 24, fill=tone["acc"] + (255,))
                hz = _ink(ch["h"], MJ, 90, (255, 255, 255))
                card.alpha_composite(hz, ((tw - hz.width) // 2, 30))
                ko = _ink(ch["ko"], MJ, 44, (255, 255, 255))
                card.alpha_composite(ko, ((tw - ko.width) // 2, tw - 40))
            if sx < 1:
                cw = max(2, int(tw * sx))
                card = card.resize((cw, card.height), Image.LANCZOS)
            G.blit(f, card, (x + tw / 2, yy), 1, "mt")
            # 아래 한글 음
            G.blit(f, _ink(sp["name"][i] if i < len(sp["name"]) else "", MJ, 60, tone["sub"]), (x + tw / 2, y + tw + 90), k, "mt")
        mt = self.line_start(sp.get("meaning_on", 2))
        mo = _e((t - mt) / 0.45)
        if mo > 0:
            box = _marker_text(sp["meaning"], 72, tone["ink"], tone["mark"], sp.get("meaning_hl", ""))
            G.blit(f, box, (S.W / 2 - 160, 880 + (1 - mo) * 30), mo, "mm")
            if sp.get("icon"):
                ic = icon(sp["icon"], 230, tone["ink"], tone["acc"], t)
                bounce = 1 + 0.08 * math.sin(max(0, t - mt) * 8) * max(0, 1 - (t - mt))
                ic2 = ic.resize((int(230 * mo * bounce) + 1, int(230 * mo * bounce) + 1), Image.LANCZOS)
                G.blit(f, ic2, (S.W - 330, 840), 1, "mm")
        self.finish(f, t)

    def extra_sfx(self):
        t0 = self.line_start(self.spec.get("on", 1))
        return [(t0 + 0.25 * i, "pop", 0.4) for i in range(len(self.spec["chars"]))] + [(self.line_start(self.spec.get("meaning_on", 2)), "ding", 0.6)]


def _scene(kind, w, h, t, tone):
    """옛날/지금 손그림 풍경"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "city":
        d.rectangle((0, 0, w, h), fill=(200, 214, 230, 255))
        rnd = random.Random(3)
        x = 0
        while x < w:
            bw = rnd.randint(60, 130)
            bh = rnd.randint(int(h * 0.35), int(h * 0.85))
            col = rnd.choice(((120, 130, 150), (150, 160, 178), (100, 110, 130)))
            d.rectangle((x, h - bh, x + bw - 6, h), fill=col + (255,))
            for yy in range(h - bh + 16, h - 20, 26):
                for xx in range(x + 10, x + bw - 16, 22):
                    if rnd.random() < 0.6:
                        d.rectangle((xx, yy, xx + 10, yy + 12), fill=(255, 236, 160, 255))
            x += bw
        d.rectangle((0, h - 40, w, h), fill=(80, 84, 96, 255))
        for i in range(4):   # 지나가는 차
            cx = (t * 220 + i * w / 4) % (w + 100) - 50
            d.rounded_rectangle((cx, h - 34, cx + 70, h - 14), 8, fill=(220, 70, 60, 255))
    else:
        d.rectangle((0, 0, w, h), fill=(236, 226, 196, 255))
        d.polygon([(0, h * 0.55), (w * 0.3, h * 0.25), (w * 0.55, h * 0.5), (w * 0.8, h * 0.3), (w, h * 0.5), (w, h), (0, h)], fill=(170, 186, 140, 255))
        d.rectangle((0, h * 0.7, w, h), fill=(130, 180, 220, 255))
        for k in range(5):
            yy = h * 0.74 + k * 18
            off = (t * 40 + k * 30) % 80
            for xx in range(-80, w, 80):
                d.arc((xx + off, yy - 8, xx + off + 60, yy + 8), 0, 180, fill=(255, 255, 255, 160), width=3)
        ic = icon(kind if kind != "river" else "pavilion", int(h * 0.55), tone["ink"], tone["acc"], t)
        im.alpha_composite(ic, (int(w * 0.25), int(h * 0.2)))
    return im


class ThenNow(SciBase):
    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        w, h = 1440, 620
        x0, y0 = (S.W - w) // 2, 300
        then = _scene(sp["then"].get("scene", "river"), w, h, t, tone)
        now = _scene("city", w, h, t, tone)
        st = self.line_start(sp.get("wipe_on", 2))
        k = _e((t - st) / 1.4) if t >= st else 0
        cut = int(w * (1 - k))
        canvas = now.copy()
        canvas.paste(then.crop((0, 0, cut, h)), (0, 0)) if cut > 0 else None
        frame = Image.new("RGBA", (w + 24, h + 24), (255, 253, 246, 255))
        frame.alpha_composite(canvas, (12, 12))
        G.blit(f, frame.rotate(-1, expand=True, resample=Image.BICUBIC), (S.W / 2, y0 + h / 2), G.appear(t, 0, 0.4), "mm")
        d = ImageDraw.Draw(f)
        if 0 < k < 1:
            xs = x0 + cut
            d.line((xs, y0, xs, y0 + h), fill=tone["acc"] + (255,), width=8)
            d.ellipse((xs - 26, y0 + h / 2 - 26, xs + 26, y0 + h / 2 + 26), fill=tone["acc"] + (255,))
        lab_then = G.pill(sp["then"]["label"], "Black", 36, (255, 255, 255), tone["ink"], pad=(18, 8))
        G.blit(f, lab_then, (x0 + 30, y0 + 30), max(0.0, 1 - k * 1.5), "lt")
        if k > 0.6:
            lab_now = G.pill(sp["now"]["label"], "Black", 36, (255, 255, 255), tone["acc"], pad=(18, 8))
            G.blit(f, lab_now, (x0 + w - 30, y0 + 30), min(1.0, (k - 0.6) * 2.5), "rt")
        if sp.get("caption"):
            G.blit(f, _ink(sp["caption"], PEN, 56, tone["ink"]), (S.W / 2, y0 + h + 60), G.appear(t, self.line_start(sp.get("caption_on", 1)), 0.3), "mt")
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(self.spec.get("wipe_on", 2)), "whoosh", 0.7)]


def _sign(text, sub, w=620, h=200, col=(30, 80, 160)):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=col + (255,), outline=(255, 255, 255, 255), width=8)
    tx = _ink(text, "Pretendard-Black.otf" if False else MJ, 90, (255, 255, 255))
    im.alpha_composite(tx, ((w - tx.width) // 2, 24))
    if sub:
        sb = _ink(sub, MJ, 30, (220, 230, 245))
        im.alpha_composite(sb, ((w - sb.width) // 2, h - 54))
    return im


class SignFlip(SciBase):
    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        signs = sp["signs"]
        for i, sg in enumerate(signs):
            ts = self.line_start(sg.get("on", 1)) + sg.get("offset", 0)
            o = G.appear(t, ts - 0.6, 0.3)
            if o <= 0:
                continue
            cx = S.W / 2 + (i - (len(signs) - 1) / 2) * 560
            cy = 560
            d = ImageDraw.Draw(f)
            d.rectangle((cx - 12, cy + 100, cx + 12, 980), fill=(150, 156, 170, 255))
            new = _sign(sg["new"], sg.get("sub", ""), 500, 190)
            G.blit(f, new, (cx, cy), o, "mm")
            k = (t - ts) / 0.9
            if k < 1:
                old = _sign(sg["old"], "일제강점기 이름", 500, 190, col=(110, 100, 90))
                ang = -40 * max(0.0, k) ** 2
                drop = 600 * max(0.0, k) ** 2
                o2 = 1 - max(0.0, k - 0.5) * 2
                G.blit(f, old.rotate(ang, expand=True, resample=Image.BICUBIC), (cx + 40 * max(0.0, k), cy + drop), o * max(0.0, o2), "mm")
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(s.get("on", 1)) + s.get("offset", 0), "whoosh", 0.5) for s in self.spec["signs"]]


class QuizCard(SciBase):
    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        ch = sp["choices"]
        n = len(ch)
        cw, chh = 460, 300
        rv = self.line_start(sp.get("reveal_on", 2)) + sp.get("reveal_offset", 0)
        for i, c in enumerate(ch):
            ts = 0.2 + i * 0.25
            o = G.appear(t, ts, 0.3)
            if o <= 0:
                continue
            cx = S.W / 2 + (i - (n - 1) / 2) * (cw + 50)
            cy = 600
            ans = i == sp["answer"]
            k = _e((t - rv) / 0.5) if t >= rv else 0
            card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            if ans and k > 0:
                cd.rounded_rectangle((0, 0, cw - 1, chh - 1), 28, fill=tone["acc"] + (255,))
                tx = _ink(c, MJ, 54, (255, 255, 255))
            else:
                cd.rounded_rectangle((0, 0, cw - 1, chh - 1), 28, fill=(255, 253, 246, 255), outline=tone["ink"] + (255,), width=5)
                tx = _ink(c, MJ, 54, tone["ink"])
            card.alpha_composite(tx, ((cw - tx.width) // 2, (chh - tx.height) // 2))
            num = _ink("①②③④"[i], MJ, 50, tone["sub"])
            card.alpha_composite(num, (24, 16))
            sc = 1 + (0.08 * k if ans else 0)
            alpha = o * (1 - 0.6 * k if not ans else 1)
            if sc != 1:
                card = card.resize((int(cw * sc), int(chh * sc)), Image.LANCZOS)
            G.blit(f, card, (cx, cy - (12 * math.sin(t * 3 + i) if k == 0 else 0)), alpha, "mm")
        if sp.get("question"):
            G.blit(f, _ink(sp["question"], PEN, 64, tone["ink"]), (S.W / 2, 860), G.appear(t, 0.1, 0.3), "mt")
        # 11/26 사용자: 퀴즈 카운트다운 '3 · 2 · 1' (countdown_on 줄에서 시작 · 대사로도 '3, 2, 1')
        if sp.get("countdown_on"):
            c0 = self.line_start(sp["countdown_on"]) + sp.get("countdown_offset", 0.3)
            n = sp.get("countdown", 3)
            if c0 <= t < min(rv, c0 + n + 0.3):
                left = n - int(t - c0)
                ph = (t - c0) % 1
                cx, cy, r = S.W - 210, 230, 110
                d = ImageDraw.Draw(f)
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 253, 246, 240), outline=tone["ink"] + (255,), width=6)
                d.arc((cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10), -90, -90 + 360 * (1 - ph), fill=tone["acc"] + (255,), width=14)
                num = _ink(str(max(1, left)), MJ, int(130 * (1.25 - 0.25 * min(1, ph * 4))), tone["acc"])
                G.blit(f, num, (cx, cy), 1, "mm")
        self.finish(f, t)

    def extra_sfx(self):
        ev = [(self.line_start(self.spec.get("reveal_on", 2)) + self.spec.get("reveal_offset", 0), "ding", 0.8)]
        if self.spec.get("countdown_on"):
            c0 = self.line_start(self.spec["countdown_on"]) + self.spec.get("countdown_offset", 0.3)
            ev += [(c0 + i, "tick", 0.7) for i in range(self.spec.get("countdown", 3))]
        return ev


TYPES.update({"hanja": Hanja, "thennow": ThenNow, "signflip": SignFlip, "quizcard": QuizCard})
