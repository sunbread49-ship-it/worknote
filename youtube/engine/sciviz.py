"""지식채널 그림 장면 (2026-11-26 서울 동네 이름 편 · 사용자: 글보다 영상 효과로 눈을 사로잡기 · 매 장면 변주)
종이 톤(ivory) 위 손그림 느낌.

type: hanja     한자 타일이 하나씩 툭 떨어져 → 뒤집히며 뜻 카드 → 마지막에 그림(icon)이 튀어나옴
  name: 압구정 · chars: [{h: 狎, ko: 친할 압}, ...] · meaning: '갈매기와 친한 정자' · icon: gull|pavilion|silkworm|hemp|egret|grass|flag|hill|island|pear|pond
type: thennow   옛날 그림 ↔ 지금 그림을 가르는 슬라이더가 좌→우로 쓸고 지나감
  then: {scene: river|mulberry|ferry|island|grass, label} · now: {scene: city, label} · year
type: signflip  도로 표지판(파란 판) — 옛 이름 판이 뜯겨 떨어지고 새 이름이 나타남 (여러 개 차례로)
  signs: [{old, new, sub, on}]
type: nametags  이름표 카드 2~4장 (그림 · 이름 · 한자 · 뜻) · type: riverline 한강 띠 + 강변 동네 핀 + 작은 배
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


HZ = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"   # 명조 폰트엔 한자가 없음 → 한자는 이 글꼴로


def _hz(text, size, color):
    from PIL import ImageFont
    fnt = ImageFont.truetype(HZ, size)
    l, t_, r, b = fnt.getbbox(text)
    im = Image.new("RGBA", (r - l + 8, b - t_ + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t_), text, font=fnt, fill=color)
    return im


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
        G.blit(im, _hz("十里", int(s * 0.28), acc), (s * 0.5, s * 0.25), 1, "mm")
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
                hz = _hz(ch["h"], 170, tone["ink"])
                card.alpha_composite(hz, ((tw - hz.width) // 2, (tw + 60 - hz.height) // 2))
            else:
                cd.rounded_rectangle((0, 0, tw - 1, tw + 59), 24, fill=tone["acc"] + (255,))
                hz = _hz(ch["h"], 90, (255, 255, 255))
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
        from .editorial import _photo_fit
        crs = []

        def side(dd, default):
            if dd.get("photo"):   # 11/26 사용자: 실사
                im, cr = _photo_fit(dd["photo"], w, h, tuple(dd.get("focus", (0.5, 0.5))))
                if cr:
                    crs.append(cr.replace("사진: ", ""))
                return im
            return _scene(dd.get("scene", default), w, h, t, tone)
        then = side(sp["then"], "river")
        now = side(sp["now"], "city")
        if crs and not sp.get("credit"):
            sp["credit"] = "사진: " + " · ".join(dict.fromkeys(crs))
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
    def _c0(self):
        sp = self.spec
        bt = sp.get("_beats") or []
        k = sp.get("countdown_beat", 1)   # beat_line 줄의 몇 번째 말 덩어리부터 카운트(0='3초 드릴게요', 1='셋')
        if bt and sp.get("beat_line") == sp.get("countdown_on") and k < len(bt):
            return self.line_start(sp["countdown_on"]) + bt[k]
        return self.line_start(sp["countdown_on"]) + sp.get("countdown_offset", 0.3)

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
            c0 = self._c0()
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
            c0 = self._c0()
            ev += [(c0 + i, "tick", 0.7) for i in range(self.spec.get("countdown", 3))]
        return ev


TYPES.update({"hanja": Hanja, "thennow": ThenNow, "signflip": SignFlip, "quizcard": QuizCard})


# ── 11/26 서울 동네 이름 편 추가 도안 ─────────────────────
class NameTags(SciBase):
    """동네 이름표 카드: 2~4장이 차례로 위에서 툭 떨어져 비뚤게 붙음(테이프) · 그림 + 이름 + 한자 + 뜻
    cards: [{name, h, meaning, hl, icon, on, offset}]"""

    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        cards = sp["cards"]
        n = len(cards)
        cw, chh = (400, 540) if n >= 4 else (440, 560)
        gap = 40
        x0 = S.W / 2 - (n * cw + (n - 1) * gap) / 2
        tilts = (-3, 2.5, -2, 3)
        starts = [self.line_start(c.get("on", 1)) + c.get("offset", 0) for c in cards]
        cur = max([i for i, st in enumerate(starts) if t >= st] or [-1])
        for i, c in enumerate(cards):
            k = _e((t - starts[i]) / 0.5)
            if k <= 0:
                continue
            card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            now = i == cur
            cd.rounded_rectangle((0, 0, cw - 1, chh - 1), 22, fill=(255, 253, 246, 255),
                                 outline=(tone["acc"] if now else tone["ink"]) + (255,), width=7 if now else 4)
            ic = icon(c.get("icon", "pond"), 210, tone["ink"], tone["acc"], t)
            card.alpha_composite(ic, ((cw - 210) // 2, 26))
            nm = _ink(c["name"], MJ, 84, tone["ink"])
            card.alpha_composite(nm, ((cw - nm.width) // 2, 248))
            if c.get("h"):
                hz = _hz(c["h"], 42, tone["sub"])
                card.alpha_composite(hz, ((cw - hz.width) // 2, 352))
            mo = _e((t - starts[i] - 0.35) / 0.4)
            if mo > 0:
                lines = c["meaning"].split("\n")
                yy = 418
                for ln in lines:
                    mt = _ink(ln, PEN, 54, tone["ink"])
                    if c.get("hl") and c["hl"] in ln:
                        bar = Image.new("RGBA", (int(mt.width * mo), 22), tone["mark"] + (220,))
                        card.alpha_composite(bar, ((cw - mt.width) // 2, yy + mt.height - 26))
                    card.alpha_composite(mt, ((cw - mt.width) // 2, yy))
                    yy += 56
            ang = tilts[i % 4] + (1 - k) * 18
            rc = card.rotate(ang, expand=True, resample=Image.BICUBIC)
            cx = x0 + i * (cw + gap) + cw / 2
            cy = 600 - (1 - k) * 380
            sh = Image.new("RGBA", rc.size, (0, 0, 0, 0))
            sh.putalpha(rc.split()[3].filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.25)))
            G.blit(f, sh, (cx + 10, cy + 14), k, "mm")
            G.blit(f, rc, (cx, cy), k, "mm")
            tp = Image.new("RGBA", (150, 42), tone["mark"] + (190,)).rotate(-tilts[i % 4] * 2, expand=True, resample=Image.BICUBIC)
            G.blit(f, tp, (cx, cy - chh / 2 + 4), k, "mm")
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(c.get("on", 1)) + c.get("offset", 0), "pop", 0.5) for c in self.spec["cards"]]


class RiverLine(SciBase):
    """한강 띠(서→동)가 그려지고 강변 동네 핀이 차례로 꽂힘 · 작은 배가 최신 핀으로 이동
    spots: [{name, x(0~1), side: n|s|mid, sub, icon, on, offset}]"""

    def _ry(self, x):
        return 610 + 46 * math.sin(x / 260.0) + 22 * math.sin(x / 97.0 + 1)

    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        d = ImageDraw.Draw(f)
        xa, xb = 70, S.W - 70
        dk = _e(t / 1.2)
        xe = xa + (xb - xa) * dk
        water = (120, 178, 222, 255)
        pts_top = [(x, self._ry(x) - 62) for x in range(xa, int(xe) + 1, 8)]
        pts_bot = [(x, self._ry(x) + 62) for x in range(int(xe), xa - 1, -8)]
        if len(pts_top) > 1:
            d.polygon(pts_top + pts_bot, fill=water)
            d.line(pts_top, fill=tone["ink"] + (255,), width=4)
            d.line(pts_bot[::-1], fill=tone["ink"] + (255,), width=4)
            for k in range(3):
                for x in range(xa, int(xe) - 60, 120):
                    off = (t * 50 + k * 40) % 120
                    yy = self._ry(x + off) - 30 + k * 30
                    d.arc((x + off, yy - 8, x + off + 50, yy + 8), 0, 180, fill=(255, 255, 255, 170), width=3)
        G.blit(f, _ink(sp.get("west", "서쪽"), PEN, 48, tone["sub"]), (xa + 10, 470), G.appear(t, 0.3, 0.3), "lm")
        G.blit(f, _ink(sp.get("east", "동쪽 →"), PEN, 48, tone["sub"]), (xb - 10, 470), G.appear(t, 0.9, 0.3), "rm")
        G.blit(f, _ink("강북", MJ, 40, tone["sub"]), (S.W / 2, 300), G.appear(t, 0.6, 0.3), "mm")
        G.blit(f, _ink("강남", MJ, 40, tone["sub"]), (S.W / 2, 1000), G.appear(t, 0.6, 0.3), "mm")
        pins = sp["spots"]
        starts = [self.line_start(p.get("on", 1)) + p.get("offset", 0) for p in pins]
        cur = max([i for i, st in enumerate(starts) if t >= st] or [-1])
        # 배
        if cur >= 0:
            prev = pins[cur - 1]["x"] if cur > 0 else 0.0
            kb = _e((t - starts[cur]) / 0.8)
            bx = xa + (xb - xa) * (prev + (pins[cur]["x"] - prev) * kb)
        else:
            bx = xa + 20
        by = self._ry(bx) + 4 * math.sin(t * 4)
        if dk > 0.2:
            d.polygon([(bx - 44, by - 6), (bx + 44, by - 6), (bx + 30, by + 16), (bx - 30, by + 16)], fill=tone["acc"] + (255,))
            d.line((bx, by - 6, bx, by - 64), fill=tone["ink"] + (255,), width=4)
            d.polygon([(bx + 2, by - 62), (bx + 40, by - 18), (bx + 2, by - 18)], fill=(255, 253, 246, 255), outline=tone["ink"] + (255,))
        for i, p in enumerate(pins):
            k = _e((t - starts[i]) / 0.45)
            if k <= 0:
                continue
            x = xa + (xb - xa) * p["x"]
            side = p.get("side", "n")
            ry = self._ry(x)
            if side == "mid":
                d.ellipse((x - 70, ry - 26, x + 70, ry + 26), fill=(226, 206, 150, 255), outline=tone["ink"] + (255,), width=3)
                base, sgn = ry - 26, -1
            elif side == "n":
                base, sgn = ry - 62, -1
            else:
                base, sgn = ry + 62, 1
            tip = base + sgn * 70 * k
            d.line((x, base, x, tip), fill=tone["ink"] + (255,), width=4)
            d.ellipse((x - 10, base - 10, x + 10, base + 10), fill=tone["acc"] + (255,), outline=tone["ink"] + (255,), width=3)
            # 카드
            now = i == cur
            nm = _ink(p["name"], MJ, 58 if now else 50, tone["acc"] if now else tone["ink"])
            sb = _ink(p.get("sub", ""), PEN, 40, tone["ink"]) if p.get("sub") else None
            iw = 0
            cw = max(nm.width, sb.width if sb else 0) + 40
            chh = nm.height + (sb.height if sb else 0) + 30
            card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
            ImageDraw.Draw(card).rounded_rectangle((0, 0, cw - 1, chh - 1), 16, fill=(255, 253, 246, 245),
                                                   outline=(tone["acc"] if now else tone["ink"]) + (255,), width=4 if now else 3)
            card.alpha_composite(nm, ((cw - nm.width) // 2, 10))
            if sb:
                card.alpha_composite(sb, ((cw - sb.width) // 2, 10 + nm.height))
            cy = tip + sgn * chh / 2
            G.blit(f, card, (x, cy), k, "mm")
            if p.get("icon") and now:
                ic = icon(p["icon"], 150, tone["ink"], tone["acc"], t)
                G.blit(f, ic, (x + cw / 2 + 80, cy), k, "mm")
        self.finish(f, t)

    def extra_sfx(self):
        return [(0.1, "whoosh", 0.5)] + [(self.line_start(p.get("on", 1)) + p.get("offset", 0), "pop", 0.45) for p in self.spec["spots"]]


TYPES.update({"nametags": NameTags, "riverline": RiverLine})


class CheatSheet(SciBase):
    """수첩 한 장 '이 글자만 알면 동네 이름이 읽힌다': 줄마다 한자 도장 쾅 → 뜻 → 예시 동네가 손글씨로 써짐 → 빨간 체크
    rows: [{h, ko, ex, on, offset}]"""

    def draw(self, f, t):
        sp = self.spec
        self.frame(f, t)
        tone = self.tone
        self.title(f, t)
        rows = sp["rows"]
        n = len(rows)
        top, bot = 320, 870   # 11/26 사용자: 자막과 겹침 → 아래 여백
        rh = min(130, (bot - top) / n)
        # 수첩 종이
        d = ImageDraw.Draw(f)
        px0, px1 = 260, S.W - 260
        d.rounded_rectangle((px0 + 10, top - 30 + 12, px1 + 10, top + rh * n + 20 + 12), 20, fill=(0, 0, 0, 30))
        dark = sum(tone["paper"]) < 200   # 11/27 밤 톤: 카드도 어둡게(글자가 밝은 색이라)
        cardc = (26, 32, 58) if dark else (255, 253, 246)
        d.rounded_rectangle((px0, top - 30, px1, top + rh * n + 20), 20, fill=cardc + (255,), outline=tone["ink"] + (255,), width=4)
        d.line((px0 + 230, top - 30, px0 + 230, top + rh * n + 20), fill=tone["acc"] + (160,), width=3)
        for i, r in enumerate(rows):
            ts = self.line_start(r.get("on", 1)) + r.get("offset", 0)
            y = top + i * rh + rh / 2
            d.line((px0 + 20, top + (i + 1) * rh - 4, px1 - 20, top + (i + 1) * rh - 4), fill=((60, 70, 100) if dark else (200, 210, 230)) + (255,), width=2)
            k = (t - ts) / 0.35
            if k <= 0:
                continue
            sc = 1 + 0.6 * max(0.0, 1 - k) ** 2   # 도장 쾅
            st = Image.new("RGBA", (int(rh * 0.82), int(rh * 0.82)), (0, 0, 0, 0))
            ImageDraw.Draw(st).rounded_rectangle((0, 0, st.width - 1, st.height - 1), 14, fill=tone["acc"] + (255,))
            hz = _hz(r["h"], int(rh * 0.56), (255, 255, 255))
            st.alpha_composite(hz, ((st.width - hz.width) // 2, (st.height - hz.height) // 2))
            st = st.rotate(-4 + 3 * (i % 2), expand=True, resample=Image.BICUBIC)
            st = st.resize((int(st.width * sc), int(st.height * sc)), Image.LANCZOS)
            G.blit(f, st, (px0 + 115, y), min(1.0, k), "mm")
            ko = _ink(r["ko"], MJ, int(rh * 0.42), tone["ink"])
            G.blit(f, ko, (px0 + 270, y), G.appear(t, ts + 0.2, 0.25), "lm")
            # 예시: 왼→오 손글씨로 써지듯(가로로 열림)
            ex = _ink(r["ex"], PEN, int(rh * 0.4), tone["sub"])
            kw = _e((t - ts - 0.45) / 0.7)
            if kw > 0:
                cut = ex.crop((0, 0, max(1, int(ex.width * kw)), ex.height))
                G.blit(f, cut, (px0 + 300 + ko.width, y + 4), 1, "lm")
            if t > ts + 1.1:
                cx = px1 - 70
                kc = _e((t - ts - 1.1) / 0.3)
                d.line((cx - 26, y, cx - 26 + 18 * kc, y + 20 * kc), fill=tone["acc"] + (255,), width=9)
                if kc >= 1:
                    d.line((cx - 8, y + 20, cx + 30, y - 26), fill=tone["acc"] + (255,), width=9)
        self.finish(f, t)

    def extra_sfx(self):
        return [(self.line_start(r.get("on", 1)) + r.get("offset", 0), "pop", 0.55) for r in self.spec["rows"]]


TYPES.update({"cheatsheet": CheatSheet})
