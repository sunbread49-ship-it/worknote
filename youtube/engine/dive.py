"""dive — 지구 관통 낙하 체험 장면 (2026-11-24 sci05 · 사용자: 리얼 체험 다큐 느낌, 모션이 쉴 새 없이)

type: dive
  mode: section  지구 단면(지각 · 맨틀 · 외핵 · 내핵) + 가운데 세로 터널 + 떨어지는 악어새 + 오른쪽 깊이 게이지 + 왼쪽 위 계기판(경과 시간 · 깊이 · 속도)
        strata   지표~40km 확대 단면(땅 층 + 시추공) · 비교 막대(금광 4km · 에베레스트 8.8km 거꾸로 · 마리아나 11km · 콜라 12.3km · 지각 끝 35km)
        chord    지구 원 + 곧은 터널(두 도시) + 공이 왕복 · 타이머가 같은 42분에 도착
        orbit    터널 속 낙하 vs 지표를 스치는 인공위성 — 높이가 똑같이 맞물려 움직임(84분)
        air      공기 저항: 진폭이 줄어드는 그래프 → 가운데에 갇힘
        spin     지구 자전: 적도 터널은 벽에 부딪힘(쾅) · 북극→남극 터널은 OK
  tau: [시작 분, 끝 분]  — 장면 동안 낙하 시각이 이만큼 흐른다(물리 계산으로 깊이 · 속도 표시)
  stops: [{km, label, sub, on}]  — 게이지 · 단면 위 정거장 표지
  caption / title / highlight — 위쪽 제목
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from . import draw as G
from . import style as S
from .editorial import Editorial, T, TYPES, _col, _mascot_img

R_KM = 6371.0
PERIOD = 84.4          # 균일한 지구 왕복(분)
LAYERS = [             # (바깥 반지름 비율, 안쪽 색, 바깥 색, 이름)
    (1.000, (122, 86, 60), (150, 112, 80), "지각"),
    (0.995, (236, 112, 40), (150, 52, 30), "맨틀"),
    (0.546, (255, 186, 60), (232, 120, 30), "외핵 (액체 쇠)"),
    (0.192, (255, 252, 230), (255, 214, 90), "내핵"),
]
GOLD = (255, 204, 40)
SKY = (120, 200, 255)


def fall_state(tau):
    """균일 밀도 지구 낙하: 분 → (깊이 km, 속도 km/h)"""
    w = 2 * math.pi / PERIOD
    depth = R_KM * (1 - math.cos(w * tau))
    v = R_KM * w * abs(math.sin(w * tau)) * 60   # km/분 → km/h
    return depth, v


def _stars(w, h, seed=7):
    import random
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), (8, 12, 26, 255))
    d = ImageDraw.Draw(im)
    for _ in range(260):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.choice((1, 1, 1, 2))
        c = rnd.randint(120, 230)
        d.ellipse((x, y, x + r, y + r), fill=(c, c, min(255, c + 20), 255))
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((w * 0.15, h * 0.1, w * 0.85, h * 1.2), fill=(30, 60, 120, 70))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
    return im


_BG = {}


def _space():
    if "s" not in _BG:
        _BG["s"] = _stars(S.W, S.H)
    return _BG["s"]


def _earth_section(r, t=0.0):
    """단면 원판(층별 방사형 그라데이션 + 외핵 일렁임)"""
    key = ("sec", r)
    if key not in _BG:
        im = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
        c = r + 20
        d = ImageDraw.Draw(im)
        # 대기 빛
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((c - r - 14, c - r - 14, c + r + 14, c + r + 14), fill=(90, 170, 255, 120))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
        for i, (fo, cin, cout, _) in enumerate(LAYERS):
            fi = LAYERS[i + 1][0] if i + 1 < len(LAYERS) else 0.0
            r0, r1 = r * fi, r * fo
            steps = max(2, int(r1 - r0))
            for k in range(steps, 0, -1):
                rr = r0 + (r1 - r0) * k / steps
                q = k / steps
                col = tuple(int(cin[j] + (cout[j] - cin[j]) * q) for j in range(3))
                d.ellipse((c - rr, c - rr, c + rr, c + rr), fill=col + (255,))
        # 지각은 실제론 너무 얇아 보이지 않으니 테두리로 강조
        d.ellipse((c - r, c - r, c + r, c + r), outline=(110, 170, 90, 255), width=max(4, r // 60))
        _BG[key] = im
    return _BG[key]


def _gauge(f, x, y0, y1, depth, stops, t, scene):
    d = ImageDraw.Draw(f)
    d.rounded_rectangle((x - 9, y0 - 9, x + 9, y1 + 9), 9, fill=(255, 255, 255, 40))
    k = min(1.0, depth / (2 * R_KM))   # 게이지 = 터널 전체(서울 → 반대편 12,742km)
    d.rounded_rectangle((x - 9, y0 - 9, x + 9, y0 + (y1 - y0) * k + 9), 9, fill=GOLD + (230,))
    for s in stops or []:
        if s["km"] > 2 * R_KM:
            continue
        o = G.appear(t, scene.line_start(s.get("on", 1)), 0.3)
        if o <= 0:
            continue
        yy = y0 + (y1 - y0) * s["km"] / (2 * R_KM)
        reached = depth >= s["km"] - 1
        c = GOLD if reached else (200, 206, 220)
        d.line((x - 22, yy, x + 22, yy), fill=c + (int(255 * o),), width=4)
        G.blit(f, T(f"{s['km']:,}km" if s["km"] >= 1 else "0km", 26, c, "Black"), (x - 34, yy), o, "rm")
        if s.get("label"):
            G.blit(f, T(s["label"], 30, c, "ExtraBold"), (x + 34, yy), o, "lm")


def _panel(f, tau, depth, v, extra=None):
    """왼쪽 위 계기판"""
    pw, ph = 470, 230 if not extra else 280
    p = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, pw - 1, ph - 1), 22, fill=(10, 16, 34, 205), outline=(255, 255, 255, 60), width=2)
    m, s = int(tau), int((tau - int(tau)) * 60)
    p.alpha_composite(T("경과", 26, (170, 180, 200), "Bold"), (28, 22))
    p.alpha_composite(T(f"{m:02d}분 {s:02d}초", 64, GOLD, "Black"), (28, 52))
    p.alpha_composite(T(f"이동  {depth:,.0f} km", 34, (235, 238, 245), "ExtraBold"), (28, 140))
    p.alpha_composite(T(f"속도  시속 {v:,.0f} km", 34, (235, 238, 245), "ExtraBold"), (28, 184))
    if extra:
        p.alpha_composite(T(extra, 28, SKY, "Bold"), (28, 232))
    G.blit(f, p, (S.SAFE_X + 20, 150), 1, "lt")


def _layer_col(depth):
    dd = depth if depth <= R_KM else 2 * R_KM - depth
    if dd < 35:
        return (130, 100, 70)
    if dd < 2900:
        return (200, 80, 30)
    if dd < 5150:
        return (240, 150, 40)
    return (255, 230, 150)


def _cam(depth, v, t, faller, bg=None):
    """악어새 시점 동그라미: 지금 지나는 층 색 + 위로 쏜살같이 지나가는 돌 알갱이"""
    s = 300
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    inner = Image.new("RGBA", (s, s), _layer_col(depth) + (255,))
    d = ImageDraw.Draw(inner)
    import random
    rnd = random.Random(3)
    spd = min(1.0, v / 28000)
    for i in range(46):
        x = rnd.uniform(0, s)
        y = (rnd.uniform(0, s) - t * (200 + 2400 * spd)) % (s + 120) - 60
        ln = 6 + 80 * spd
        c = tuple(min(255, int(v_ * rnd.uniform(0.6, 1.4))) for v_ in _layer_col(depth))
        d.line((x, y, x, y + ln), fill=c + (255,), width=rnd.choice((3, 4, 6)))
    fl = faller.rotate(15 * math.sin(t * 3), expand=True)
    inner.alpha_composite(fl, ((s - fl.width) // 2, (s - fl.height) // 2))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255)
    im.paste(inner, (0, 0), m)
    ImageDraw.Draw(im).ellipse((0, 0, s - 1, s - 1), outline=(255, 255, 255, 230), width=6)
    lab = T("악어새 시점", 26, (20, 22, 30), "Black")
    pill = Image.new("RGBA", (lab.width + 28, lab.height + 12), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, pill.height - 1), 14, fill=GOLD + (255,))
    pill.alpha_composite(lab, (14, 6))
    out = Image.new("RGBA", (s, s + 40), (0, 0, 0, 0))
    out.alpha_composite(im, (0, 40))
    out.alpha_composite(pill, ((s - pill.width) // 2, 20))
    return out


def _compass(s, ang):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, s - 4, s - 4), fill=(245, 246, 250, 255), outline=(200, 160, 60, 255), width=8)
    c = s / 2
    a = math.radians(ang)
    L = s * 0.36
    tip = (c + L * math.sin(a), c - L * math.cos(a))
    tail = (c - L * math.sin(a), c + L * math.cos(a))
    side = (c + 12 * math.cos(a), c + 12 * math.sin(a))
    side2 = (c - 12 * math.cos(a), c - 12 * math.sin(a))
    d.polygon((tip, side, side2), fill=(220, 50, 50, 255))
    d.polygon((tail, side, side2), fill=(60, 64, 80, 255))
    d.text((c - 8, 10), "N", fill=(220, 50, 50, 255))
    return im


def _scale_img(kg):
    w, h = 300, 220
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 40, w - 1, h - 1), 30, fill=(235, 238, 245, 255))
    d.rounded_rectangle((40, 70, w - 40, 150), 14, fill=(20, 24, 36, 255))
    num = T(f"{kg:,.0f} kg", 54, GOLD if kg > 1 else (120, 220, 255), "Black")
    im.alpha_composite(num, ((w - num.width) // 2, 80))
    lab = T("서 있다면 몸무게", 24, (60, 64, 80), "Bold")
    im.alpha_composite(lab, ((w - lab.width) // 2, 170))
    return im


class Dive(Editorial):
    def base(self, f):
        f.alpha_composite(_space())
        self.fg, self.acc, self.dim, self.off = S.FG, GOLD, (190, 196, 210), (90, 94, 108)
        self.paper = False

    def head(self, f, t):
        sp = self.spec
        if sp.get("title"):
            self.hdr(f, t, y=sp.get("title_y", 60))

    def tau_at(self, t):
        a, b = self.spec.get("tau", [0, 0])
        dur = max(0.1, self.dur - 0.3)
        k = min(1.0, max(0.0, t / dur))
        k = k if self.spec.get("linear", True) else G.ease_out(k)
        return a + (b - a) * k

    def faller(self, h):
        return _mascot_img(getattr(self, "channel", {}), h)

    # ── 모드들 ─────────────────────────────────────────
    def draw(self, f, t):
        sp = self.spec
        self.base(f)
        getattr(self, "m_" + sp.get("mode", "section"))(f, t)
        self.head(f, t)
        self.finish(f, t)

    def m_section(self, f, t):
        sp = self.spec
        r = sp.get("r", 300)
        cx, cy = sp.get("cx", S.W // 2 - 40), sp.get("cy", 560)
        zin = G.ease_out(t / 0.8)
        sec = _earth_section(r)
        G.blit(f, sec, (cx, cy + (1 - zin) * 60), zin, "mm")
        d = ImageDraw.Draw(f)
        # 터널
        d.rectangle((cx - 7, cy - r - 20, cx + 7, cy + r + 20), fill=(14, 16, 24, 235))
        d.line((cx - 8, cy - r - 20, cx - 8, cy + r + 20), fill=(255, 255, 255, 120), width=2)
        d.line((cx + 8, cy - r - 20, cx + 8, cy + r + 20), fill=(255, 255, 255, 120), width=2)
        top, bot = sp.get("from", "서울"), sp.get("to", "반대편")
        G.blit(f, G.pill(top, "Black", 32, (20, 22, 30), GOLD, pad=(18, 8)), (cx, cy - r - 24), zin, "mb")
        G.blit(f, G.pill(bot, "Black", 32, (255, 255, 255), (40, 120, 220), pad=(18, 8)), (cx + 30, cy + r + 10), zin, "lm")
        # 층 이름(오른쪽 위 사선 표지)
        if sp.get("layers", True):
            for i, (fo, _, _, name) in enumerate(LAYERS[1:], 1):
                fi = LAYERS[i + 1][0] if i + 1 < len(LAYERS) else 0.0
                rr = r * (fo + fi) / 2
                a = math.radians(-35 - i * 12)
                px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
                o = G.appear(t, 0.4 + i * 0.15, 0.3)
                G.blit(f, T(name, 28, (255, 255, 255), "Black", stroke=4, stroke_fill=(20, 20, 30)), (px, py), o, "mm")
        tau = self.tau_at(t)
        depth, v = fall_state(tau) if not sp.get("depth") else (sp["depth"], 0)
        y = cy - r + r * depth / R_KM
        fh = sp.get("faller_h", 120)
        fl = self.faller(fh).rotate(180 if sp.get("head_down") else 0, expand=True)
        wob = 6 * math.sin(t * 7) + (10 * math.sin(t * 70) if v > 25000 else 0)
        G.blit(f, fl, (cx + wob, y), 1, "mm")
        if v > 0:   # 속도선
            for k in range(5):
                yy = y - fh * 0.6 - k * 22
                d.line((cx - 40 + k * 18, yy, cx - 40 + k * 18, yy - min(80, v / 400)), fill=(255, 255, 255, 90), width=3)
        if sp.get("field"):      # 지구 자석: 움직이는 자기력선 + 나침반
            for k in (1.25, 1.5, 1.8):
                for sgn in (-1, 1):
                    pts = []
                    for a in range(-80, 81, 4):
                        th = math.radians(a)
                        rr = r * k * math.cos(th) ** 2
                        if rr < r:
                            continue
                        pts.append((cx + sgn * rr * math.cos(th), cy - rr * math.sin(th)))
                    if len(pts) > 1:
                        for i in range(len(pts) - 1):
                            if (i + int(t * 8)) % 3:
                                d.line((pts[i], pts[i + 1]), fill=SKY + (170,), width=3)
            G.blit(f, _compass(150, 10 * math.sin(t * 3)), (cx - r - 220, cy - 120), G.appear(t, 0.5, 0.4), "mm")
            G.blit(f, T("나침반", 28, SKY, "Black"), (cx - r - 220, cy - 20), 1, "mm")
        if sp.get("swirl", True):   # 외핵 출렁임
            ro = r * 0.37
            for k in range(10):
                a0 = (t * 40 + k * 36) % 360
                d.arc((cx - ro, cy - ro, cx + ro, cy + ro), a0, a0 + 14, fill=(255, 240, 170, 120), width=4)
        if sp.get("trail"):
            for k in range(1, 8):
                tk = max(sp.get("tau", [0, 0])[0], tau - k * 0.6)
                dk, _ = fall_state(tk)
                yk = cy - r + r * dk / R_KM
                G.blit(f, self.faller(fh), (cx, yk), 0.08 * (8 - k), "mm")
        if sp.get("cam", True) and v > 0:
            G.blit(f, _cam(depth, v, t, self.faller(110), sp.get("cam_bg")), (S.SAFE_X + 200, 760), 1, "mm")
        if sp.get("scale"):
            kg = 60 * abs(R_KM - depth) / R_KM
            G.blit(f, _scale_img(kg), (S.SAFE_X + 200, 490), 1, "mm")
        _gauge(f, S.W - 360, cy - r, cy + r, depth, sp.get("stops"), t, self)
        if sp.get("panel", True):
            _panel(f, tau, depth, v, sp.get("extra"))
        if sp.get("note"):
            G.blit(f, T(sp["note"], 26, (190, 196, 212), "SemiBold"), (S.W / 2, S.H - 150), 1, "mm")

    def m_strata(self, f, t):
        """지표~max_km 확대 단면 + 비교 막대"""
        sp = self.spec
        mx = sp.get("max_km", 40)
        x0, x1, y0, y1 = 520, S.W - 220, 250, 900
        d = ImageDraw.Draw(f)
        bands = sp.get("bands", [(0, 2, (124, 96, 70)), (2, 20, (150, 128, 110)), (20, 35, (92, 86, 96)), (35, 60, (196, 84, 40))])
        for a, b, c in bands:
            if a >= mx:
                continue
            ya, yb = y0 + (y1 - y0) * a / mx, y0 + (y1 - y0) * min(b, mx) / mx
            d.rectangle((x0, ya, x1, yb), fill=tuple(c) + (255,))
        # 결 무늬
        for k in range(0, int(y1 - y0), 18):
            d.line((x0, y0 + k, x1, y0 + k + 6), fill=(0, 0, 0, 28), width=2)
        d.rectangle((x0, y0 - 16, x1, y0), fill=(90, 150, 80, 255))
        G.blit(f, T("땅 위", 26, (220, 240, 210), "Bold"), (x1 - 10, y0 - 22), 1, "rb")
        # 눈금
        for km in range(0, mx + 1, sp.get("tick", 5)):
            yy = y0 + (y1 - y0) * km / mx
            d.line((x0 - 16, yy, x0, yy), fill=(220, 224, 236, 200), width=3)
            G.blit(f, T(f"{km}km", 26, (210, 214, 226), "Bold"), (x0 - 24, yy), 1, "rm")
        items = sp.get("stops", [])
        n = len(items)
        for i, s in enumerate(items):
            o = G.appear(t, self.line_start(s.get("on", 1)) + s.get("offset", 0), 0.5)
            if o <= 0:
                continue
            xx = x0 + 120 + (x1 - x0 - 240) * (i + 0.5) / max(1, n)
            km = s["km"]
            yy = y0 + (y1 - y0) * min(km, mx) / mx * G.ease_out(o)
            c = _col(s["color"]) if s.get("color") else (GOLD if s.get("hl") else (235, 238, 245))
            if s.get("up"):   # 에베레스트처럼 '높이'를 거꾸로 꽂아 비교
                d.polygon(((xx - 44, y0), (xx + 44, y0), (xx, yy)), fill=(235, 240, 250, int(220 * o)))
            else:
                d.rectangle((xx - 10, y0, xx + 10, yy), fill=(12, 14, 20, int(255 * o)))
                d.rectangle((xx - 10, y0, xx + 10, yy), outline=c + (int(255 * o),), width=3)
            d.ellipse((xx - 12, yy - 12, xx + 12, yy + 12), fill=c + (int(255 * o),))
            lab = T(s["label"], 34 if s.get("hl") else 30, c, "Black", stroke=4, stroke_fill=(10, 12, 20))
            G.blit(f, lab, (xx, yy + 22), o, "mt")
            if s.get("sub"):
                G.blit(f, T(s["sub"], 24, (230, 232, 240), "Bold", stroke=3, stroke_fill=(10, 12, 20)), (xx, yy + 26 + lab.height), o, "mt")
        if sp.get("faller", True):
            dk = sp.get("faller_km", items[-1]["km"] if items else 10)
            k = G.ease_out(min(1, t / max(0.5, self.dur - 0.5)))
            yy = y0 + (y1 - y0) * min(dk, mx) / mx * k
            G.blit(f, self.faller(90), (x0 + 60, yy), 1, "mm")
        if sp.get("note"):
            G.blit(f, T(sp["note"], 26, (190, 196, 212), "SemiBold"), (S.W / 2, S.H - 150), 1, "mm")

    def m_chord(self, f, t):
        sp = self.spec
        r = sp.get("r", 320)
        cx, cy = S.W // 2, 620
        d = ImageDraw.Draw(f)
        glob = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glob)
        gd.ellipse((20, 20, 20 + 2 * r, 20 + 2 * r), fill=(26, 70, 140, 255), outline=(120, 190, 255, 255), width=5)
        G.blit(f, glob, (cx, cy), G.appear(t, 0, 0.4), "mm")
        tunnels = sp.get("tunnels", [{"a": 250, "b": 290, "label": "서울→부산"}])
        tau_a, tau_b = sp.get("tau", [0, 42.2])
        for i, tn in enumerate(tunnels):
            o = G.appear(t, self.line_start(tn.get("on", 1)), 0.4)
            if o <= 0:
                continue
            a, b = math.radians(tn["a"]), math.radians(tn["b"])
            p1 = (cx + r * math.cos(a), cy + r * math.sin(a))
            p2 = (cx + r * math.cos(b), cy + r * math.sin(b))
            c = _col(tn["color"]) if tn.get("color") else GOLD
            d.line((p1, p2), fill=c + (int(255 * o),), width=10)
            for p in (p1, p2):
                d.ellipse((p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12), fill=c + (255,))
            st = self.line_start(tn.get("on", 1))
            dur = max(1.0, self.dur - st - 0.5)
            k = min(1.0, max(0.0, (t - st) / dur))
            tau = tau_a + (tau_b - tau_a) * k
            u = (1 - math.cos(2 * math.pi * tau / PERIOD)) / 2   # 0 → 1 (반대편)
            bx, by = p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u
            d.ellipse((bx - 18, by - 18, bx + 18, by + 18), fill=(255, 255, 255, 255), outline=c + (255,), width=5)
            mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            lab = f"{tn['label']}  {int(tau):02d}분"
            G.blit(f, T(lab, 38, c, "Black", stroke=5, stroke_fill=(10, 12, 20)), (mid[0], mid[1] + tn.get("dy", -40)), o, "mb")

    def m_orbit(self, f, t):
        sp = self.spec
        r = sp.get("r", 330)
        cx, cy = S.W // 2 - 60, 590
        sec = _earth_section(r)
        G.blit(f, sec, (cx, cy), G.appear(t, 0, 0.4), "mm")
        d = ImageDraw.Draw(f)
        d.rectangle((cx - 6, cy - r - 10, cx + 6, cy + r + 10), fill=(14, 16, 24, 235))
        ro = r + 26
        for k in range(0, 360, 4):
            a = math.radians(k)
            d.point((cx + ro * math.cos(a), cy + ro * math.sin(a)), fill=(180, 210, 255, 200))
        tau = self.tau_at(t)
        th = 2 * math.pi * tau / PERIOD
        y = cy - r * math.cos(th)
        sx, sy = cx + ro * math.sin(th), cy - ro * math.cos(th)
        G.blit(f, self.faller(90), (cx, y), 1, "mm")
        sat = Image.new("RGBA", (90, 40), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sat)
        sd.rectangle((0, 12, 30, 28), fill=(80, 140, 230, 255)); sd.rectangle((60, 12, 89, 28), fill=(80, 140, 230, 255))
        sd.rectangle((32, 6, 58, 34), fill=(230, 230, 240, 255))
        G.blit(f, sat, (sx, sy), 1, "mm")
        if G.appear(t, self.line_start(sp.get("link_on", 1)), 0.3) > 0:
            for xx in range(int(min(cx, sx)), int(max(cx, sx)), 18):
                d.line((xx, y, xx + 9, y), fill=GOLD + (200,), width=3)
        m, s = int(tau), int((tau - int(tau)) * 60)
        G.blit(f, T(f"{m:02d}분 {s:02d}초", 64, GOLD, "Black"), (S.W - 260, 330), 1, "mm")
        G.blit(f, T("터널 속 악어새", 30, (235, 238, 245), "Bold"), (S.W - 260, 420), 1, "mm")
        G.blit(f, T("땅을 스치는 인공위성", 30, SKY, "Bold"), (S.W - 260, 466), 1, "mm")
        if tau >= PERIOD - 0.5:
            G.blit(f, G.pill("둘 다 84분", "Black", 44, (20, 22, 30), GOLD, pad=(24, 10)), (S.W - 260, 560), G.appear(t, t - 0.01, 0.3), "mm")

    def m_air(self, f, t):
        """공기 저항: 진폭이 줄어드는 곡선 → 가운데"""
        sp = self.spec
        x0, x1, y0, y1 = 300, S.W - 240, 280, 860
        d = ImageDraw.Draw(f)
        ym = (y0 + y1) / 2
        d.line((x0, ym, x1, ym), fill=(255, 140, 60, 200), width=3)
        G.blit(f, T("지구 한가운데", 30, (255, 160, 80), "Black"), (x0 - 20, ym), 1, "rm")
        G.blit(f, T("서울", 30, GOLD, "Black"), (x0 - 20, y0), 1, "rm")
        G.blit(f, T("반대편", 30, SKY, "Black"), (x0 - 20, y1), 1, "rm")
        k = G.ease_out(min(1.0, t / max(0.5, self.dur * 0.8)))
        pts_free, pts_air = [], []
        for i in range(0, 401):
            u = i / 400
            if u > k:
                break
            ph = u * 4 * math.pi
            pts_free.append((x0 + (x1 - x0) * u, ym - (y1 - y0) / 2 * math.cos(ph)))
            pts_air.append((x0 + (x1 - x0) * u, ym - (y1 - y0) / 2 * math.cos(ph) * math.exp(-u * 4.2)))
        if len(pts_free) > 1 and sp.get("show_free", True):
            d.line(pts_free, fill=(255, 255, 255, 70), width=4)
        if len(pts_air) > 1:
            d.line(pts_air, fill=GOLD + (255,), width=7)
            G.blit(f, self.faller(80), pts_air[-1], 1, "mm")
        G.blit(f, T("공기 없을 때", 26, (200, 204, 214), "Bold"), (x1, y0 - 10), G.appear(t, 0.3, 0.3), "rb")
        G.blit(f, T("공기 있을 때", 30, GOLD, "Black"), (x1, ym + 120), G.appear(t, 0.6, 0.3), "rb")

    def m_spin(self, f, t):
        sp = self.spec
        r = 260
        for j, (cx, polar) in enumerate(((560, False), (1360, True))):
            o = G.appear(t, self.line_start(sp.get("on2", 2)) if polar else 0, 0.4)
            if o <= 0:
                continue
            cy = 580
            ang = t * 30 if not polar else 0
            glob = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glob)
            gd.ellipse((20, 20, 20 + 2 * r, 20 + 2 * r), fill=(26, 70, 140, 255), outline=(120, 190, 255, 255), width=5)
            c = r + 20
            if polar:
                gd.rectangle((c - 7, 10, c + 7, 2 * r + 30), fill=(14, 16, 24, 255))
            else:
                gd.rectangle((10, c - 7, 2 * r + 30, c + 7), fill=(14, 16, 24, 255))
            glob = glob.rotate(ang % 360 if not polar else 0, resample=Image.BICUBIC)
            G.blit(f, glob, (cx, cy), o, "mm")
            d = ImageDraw.Draw(f)
            # 자전 화살표
            d.arc((cx - r - 40, cy - 60, cx + r + 40, cy + 60), 200, 340, fill=SKY + (int(220 * o),), width=5)
            if polar:
                G.blit(f, self.faller(80), (cx, cy - r + (2 * r) * ((1 - math.cos(min(math.pi, t * 0.9))) / 2)), o, "mm")
                G.blit(f, G.pill("북극 → 남극 OK", "Black", 36, (20, 22, 30), GOLD, pad=(20, 8)), (cx, cy - r - 30), o, "mb")
            else:
                hit = min(1.0, t / 2.2)
                bx = cx - r + r * 0.9 * hit
                by = cy - 60 * hit * hit
                G.blit(f, self.faller(80), (bx, by), o, "mm")
                if hit >= 1:
                    G.blit(f, G.pill("쾅!", "Black", 48, (255, 255, 255), (220, 50, 50), pad=(20, 8)), (bx + 40, by - 70), o, "mm")
                G.blit(f, G.pill("적도로 뚫으면 벽에 쾅", "Black", 36, (255, 255, 255), (60, 64, 80), pad=(20, 8)), (cx, cy - r - 30), o, "mb")


TYPES.update({"dive": Dive})
