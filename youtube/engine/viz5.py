"""sci05 지구 관통 편 — '말하는 건 전부 그림으로' 장면 모음 (2026-11-24 사용자 피드백)
모든 장면은 어두운 우주 배경(dive와 같은 톤) + 직접 그린 모션 그래픽.

type: globe     mode: pierce(지구본에 구멍 → 반대편) · antipode(서울 → 반대편으로 지구본 회전) · chord3d(속이 보이는 지구본 + 직선 터널) · spin3d(자전 → 벽에 쾅 / 북극→남극)
type: stopwatch 스톱워치(바늘 쌩쌩 · 숫자 굴림 · 보기 카드) · stop_at: 42.2 → 딱 멈춤
type: drill     땅 단면(입체 윗면) + 드릴이 돌며 파 내려감 → 악어새 뛰어듦
type: rabbit    토끼굴 낙하(시계 · 찻잔 · 책 · 카드가 둥둥) — 앨리스 이야기
type: mic       구멍에 마이크 내림 → 소리 파형 → '가짜' 도장 쾅
type: digrace   땅속 경쟁: 나라별 국기 + 시추 깊이 막대 경주(바다층 포함)
type: thermo    거대 온도계 + 깊이별 정거장 온도 + 태양 비교
type: elephants 손톱 1cm² 위에 코끼리가 쌓이며 600까지
type: speedrace 레인 경주: 기차 · 비행기 · 총알 · 악어새
type: swing     그네 비유(가장 낮은 곳이 가장 빠름 · 끝에서 멈춤)
type: twin      속이 고른 지구 42분 vs 진짜 지구 38분 동시 낙하
type: ruler     지구 반지름 = 서울↔부산 왕복 7번(기차가 왕복하며 쌓임)
"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from . import draw as G
from . import style as S
from .dive import GOLD, SKY, PERIOD, R_KM, _space, _earth_section, fall_state
from .editorial import Editorial, T, TYPES, _col, _mascot_img
from .globe import CITIES, globe_img, xyz, project

RED = (235, 70, 60)
WHITE = (240, 242, 248)


@lru_cache(maxsize=64)
def _globe(r, lon, lat, alpha=255, grid=True):
    return globe_img(r, lon, lat, alpha=alpha, grid=grid)


def _lerp(a, b, k):
    return a + (b - a) * k


def _ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


class Viz(Editorial):
    def base(self, f):
        f.alpha_composite(_space())
        self.fg, self.acc, self.dim, self.off = S.FG, GOLD, (190, 196, 210), (90, 94, 108)
        self.paper = False

    def draw(self, f, t):
        self.base(f)
        self.scene(f, t)
        if self.spec.get("title"):
            self.hdr(f, t, y=self.spec.get("title_y", 60))
        if self.spec.get("note"):
            G.blit(f, T(self.spec["note"], 26, (190, 196, 212), "SemiBold"), (S.W / 2, S.H - 150), 1, "mm")
        self.finish(f, t)

    def ls(self, n, off=0.0):
        return self.line_start(n) + off

    def mascot(self, h):
        return _mascot_img(getattr(self, "channel", {}), h)


# ── 지구본 ─────────────────────────────────────────────
class Globe(Viz):
    def scene(self, f, t):
        sp = self.spec
        mode = sp.get("mode", "pierce")
        r = sp.get("r", 330)
        cx, cy = sp.get("cx", S.W // 2), sp.get("cy", 580)
        d = ImageDraw.Draw(f)
        if mode == "antipode":
            a = CITIES["서울"]
            b = CITIES["서울 반대편"]
            st = self.ls(sp.get("turn_on", 1), 0.6)
            k = _ease((t - st) / 2.6)
            lon = a[0] + ((b[0] - a[0] + 540) % 360 - 180) * k
            lat = _lerp(a[1], b[1], k)
            g = _globe(r, round(lon), round(lat))
            G.blit(f, g, (cx, cy), 1, "mm")
            for name, c, col in (("서울", a, GOLD), ("서울 반대편", b, SKY)):
                x, y, v = project(c[0], c[1], lon, lat, r)
                if v:
                    pulse = 10 + 4 * math.sin(t * 6)
                    d.ellipse((cx + x - pulse, cy + y - pulse, cx + x + pulse, cy + y + pulse), fill=col + (255,), outline=(255, 255, 255, 255), width=3)
                    lab = sp.get("labels", {}).get(name, name)
                    G.blit(f, G.pill(lab, "Black", 34, (20, 22, 30) if col == GOLD else (255, 255, 255), col if col == GOLD else (40, 110, 210), pad=(18, 8)), (cx + x + 26, cy + y), 1, "lm")
            if k >= 1 and sp.get("tag"):
                G.blit(f, G.pill(sp["tag"], "Black", 40, (255, 255, 255), (40, 110, 210), pad=(22, 10)), (cx, cy + r + 30), G.appear(t, st + 2.7, 0.3), "mt")
            return
        if mode == "pierce":
            r, cy = sp.get("r", 270), sp.get("cy", 520)
            lon, lat = sp.get("lon", 127 + t * 4), sp.get("lat", 30)
            g = _globe(r, round(lon) % 360 - 180 if lon > 180 else round(lon), lat)
            G.blit(f, g, (cx, cy), G.appear(t, 0, 0.5), "mm")
            x, y, v = project(*CITIES["서울"], lon, lat, r)
            # 구멍 + 점선 화살표(지구를 뚫고 아래로)
            k = _ease((t - self.ls(sp.get("arrow_on", 1), 0.5)) / 1.6)
            if v:
                d.ellipse((cx + x - 16, cy + y - 10, cx + x + 16, cy + y + 10), fill=(10, 10, 14, 255), outline=GOLD + (255,), width=3)
                G.blit(f, G.pill("서울", "Black", 32, (20, 22, 30), GOLD, pad=(16, 6)), (cx + x, cy + y - 22), 1, "mb")
                ex, ey = cx - x, cy - y + 2 * r * 0.15
                if k > 0:
                    px, py = _lerp(cx + x, cx - x * 0.2, k), _lerp(cy + y, cy + r + 30, k)
                    for s in range(0, 40):
                        q = s / 40
                        if q > k:
                            break
                        qx, qy = _lerp(cx + x, cx - x * 0.2, q), _lerp(cy + y, cy + r + 30, q)
                        if s % 2 == 0:
                            d.ellipse((qx - 5, qy - 5, qx + 5, qy + 5), fill=GOLD + (230,))
                    G.blit(f, self.mascot(80).rotate(180), (px, py), 1, "mm")
                    if k >= 1:
                        G.blit(f, G.pill("?", "Black", 52, (255, 255, 255), (40, 110, 210), pad=(22, 6)), (cx - x * 0.2, cy + r + 50), 1, "mt")
            return
        if mode == "chord3d":
            lon0, lat0 = sp.get("lon", 160 + 10 * math.sin(t * 0.3)), sp.get("lat", 25)
            g = _globe(r, round(lon0), round(lat0), alpha=150, grid=False)
            # 속이 보이는 단면 느낌: 안쪽 맨틀 색 원
            inner = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
            ImageDraw.Draw(inner).ellipse((r * 0.1, r * 0.1, r * 1.9, r * 1.9), fill=(230, 110, 40, 70))
            G.blit(f, inner.filter(ImageFilter.GaussianBlur(30)), (cx, cy), 1, "mm")
            G.blit(f, g, (cx, cy), 1, "mm")
            for i, tn in enumerate(sp.get("tunnels", [])):
                st = self.ls(tn.get("on", 1), tn.get("offset", 0))
                o = G.appear(t, st, 0.4)
                if o <= 0:
                    continue
                a, b = CITIES[tn["a"]], CITIES[tn["b"]]
                p1 = xyz(a[0], a[1], lon0, lat0, r)
                p2 = xyz(b[0], b[1], lon0, lat0, r)
                c = _col(tn["color"]) if tn.get("color") else GOLD
                n = 30
                for s in range(n):
                    q0, q1 = s / n, (s + 1) / n
                    x0, y0 = _lerp(p1[0], p2[0], q0), _lerp(p1[1], p2[1], q0)
                    x1, y1 = _lerp(p1[0], p2[0], q1), _lerp(p1[1], p2[1], q1)
                    d.line((cx + x0, cy + y0, cx + x1, cy + y1), fill=c + (int(255 * o),), width=9)
                for (nm, p) in ((tn["a"], p1), (tn["b"], p2)):
                    d.ellipse((cx + p[0] - 11, cy + p[1] - 11, cx + p[0] + 11, cy + p[1] + 11), fill=c + (255,), outline=(255, 255, 255, 255), width=3)
                    G.blit(f, T(nm, 32, c, "Black", stroke=5, stroke_fill=(10, 12, 20)), (cx + p[0] + 18, cy + p[1] - 18), o, "lb")
                dur = max(1.0, self.dur - st - 0.6)
                kk = min(1.0, max(0.0, (t - st) / dur))
                tau = 42.2 * kk
                u = (1 - math.cos(2 * math.pi * tau / PERIOD)) / 2
                bx, by = _lerp(p1[0], p2[0], u), _lerp(p1[1], p2[1], u)
                d.ellipse((cx + bx - 16, cy + by - 16, cx + bx + 16, cy + by + 16), fill=WHITE + (255,), outline=c + (255,), width=5)
                m, s_ = int(tau), int((tau - int(tau)) * 60)
                lab = G.pill(f"{tn['a']}→{tn['b']}  {m:02d}분 {s_:02d}초", "Black", 34, (20, 22, 30) if c == GOLD else (255, 255, 255), c if c == GOLD else (40, 110, 210), pad=(18, 8))
                G.blit(f, lab, (S.W - 120, 300 + i * 80), o, "rm")
                if kk >= 1:
                    G.blit(f, G.pill("도착!", "Black", 30, (255, 255, 255), RED, pad=(14, 6)), (S.W - 120 - lab.width - 14, 300 + i * 80), 1, "rm")
            if sp.get("slides_on"):
                o = G.appear(t, self.ls(sp["slides_on"]), 0.4)
                if o > 0:
                    bx0, by0 = 1250, 520
                    pnl = Image.new("RGBA", (560, 380), (0, 0, 0, 0))
                    pd = ImageDraw.Draw(pnl)
                    pd.rounded_rectangle((0, 0, 559, 379), 24, fill=(14, 18, 34, 230), outline=(255, 255, 255, 60), width=2)
                    q = (math.sin(t * 2.4) + 1) / 2
                    for j, (ang, lab, cc) in enumerate(((12, "짧은 터널 = 완만한 미끄럼틀", GOLD), (40, "긴 터널 = 가파른 미끄럼틀", SKY))):
                        yb = 120 + j * 190
                        L = 300 if j == 0 else 230
                        ex, ey = 60 + L * math.cos(math.radians(ang)), yb - L * math.sin(math.radians(ang))
                        pd.line((60, yb, ex, ey), fill=cc + (255,), width=8)
                        bxx, byy = ex + (60 - ex) * q, ey + (yb - ey) * q
                        pd.ellipse((bxx - 12, byy - 24, bxx + 12, byy), fill=(255, 255, 255, 255))
                        lt = T(lab, 28, cc, "Black")
                        pnl.alpha_composite(lt, (40, yb + 10))
                    G.blit(f, pnl, (bx0, by0), o, "lt")
            return
        if mode == "spin3d":
            # 왼쪽: 적도 터널 + 자전 → 벽에 쾅 / 오른쪽: 북극→남극
            for j, polar in enumerate((False, True)):
                st = self.ls(sp.get("on2", 2)) if polar else 0
                o = G.appear(t, st, 0.4)
                if o <= 0:
                    continue
                gx = 560 if not polar else 1360
                rr = 250
                lon = (t * 25) % 360 - 180
                g = _globe(rr, round(lon), 20 if not polar else 10)
                G.blit(f, g, (gx, cy), o, "mm")
                # 자전 화살표(3D 고리)
                ring = Image.new("RGBA", (2 * rr + 160, 140), (0, 0, 0, 0))
                ImageDraw.Draw(ring).arc((10, 10, 2 * rr + 150, 130), 10, 170, fill=SKY + (230,), width=6)
                G.blit(f, ring, (gx, cy + 10), o, "mm")
                G.blit(f, T("빙글", 30, SKY, "Black"), (gx + rr + 40, cy + 70), o, "lm")
                if polar:
                    d.rectangle((gx - 8, cy - rr - 30, gx + 8, cy + rr + 30), fill=(14, 16, 24, 230), outline=GOLD + (255,), width=3)
                    q = (1 - math.cos(min(math.pi, (t - st) * 0.9))) / 2
                    G.blit(f, self.mascot(80), (gx, cy - rr + 2 * rr * q), o, "mm")
                    G.blit(f, G.pill("북극 → 남극 OK", "Black", 36, (20, 22, 30), GOLD, pad=(20, 8)), (gx, cy - rr - 40), o, "mb")
                else:
                    # 터널이 지구와 함께 기울며 돎(앞에서 본 적도 터널)
                    ang = math.radians(20 + 18 * math.sin(t * 0.9))
                    x1, y1 = gx - rr * math.cos(ang), cy - rr * math.sin(ang)
                    x2, y2 = gx + rr * math.cos(ang), cy + rr * math.sin(ang)
                    d.line((x1, y1, x2, y2), fill=(14, 16, 24, 255), width=18)
                    d.line((x1, y1, x2, y2), fill=(255, 255, 255, 90), width=2)
                    hit = min(1.0, t / 2.4)
                    bx, by = _lerp(x1, gx, hit), _lerp(y1, cy, hit) - 70 * math.sin(math.pi * hit) * 0.6
                    if hit >= 1:
                        bx += 6 * math.sin(t * 60) * max(0, 1 - (t - 2.4))
                        G.blit(f, G.pill("쾅!", "Black", 52, (255, 255, 255), RED, pad=(22, 8)), (bx + 30, by - 80), 1, "mm")
                        for k in range(8):
                            a2 = k * math.pi / 4 + t
                            d.line((bx + 40 * math.cos(a2), by + 40 * math.sin(a2), bx + 70 * math.cos(a2), by + 70 * math.sin(a2)), fill=GOLD + (220,), width=5)
                    G.blit(f, self.mascot(80), (bx, by), o, "mm")
                    G.blit(f, G.pill("적도로 뚫으면 벽에 쾅", "Black", 36, (255, 255, 255), (60, 64, 80), pad=(20, 8)), (gx, cy - rr - 40), o, "mb")


# ── 스톱워치 ───────────────────────────────────────────
def _stopwatch(size, ang, face=(250, 250, 252), ring=GOLD):
    s = size
    im = Image.new("RGBA", (s, int(s * 1.18)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top = int(s * 0.18)
    d.rounded_rectangle((s * 0.42, 0, s * 0.58, top * 0.7), 8, fill=(200, 204, 214, 255))
    d.rectangle((s * 0.47, top * 0.6, s * 0.53, top + 10), fill=(180, 184, 196, 255))
    d.ellipse((0, top, s - 1, top + s - 1), fill=ring + (255,))
    m = s * 0.06
    d.ellipse((m, top + m, s - m, top + s - m), fill=face + (255,))
    c = (s / 2, top + s / 2)
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = s / 2 - m - (s * 0.07 if k % 5 == 0 else s * 0.035)
        r1 = s / 2 - m - 6
        d.line((c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a), c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a)), fill=(40, 44, 60, 255), width=5 if k % 5 == 0 else 2)
    a = math.radians(ang - 90)
    L = s / 2 - m - 18
    d.line((c[0], c[1], c[0] + L * math.cos(a), c[1] + L * math.sin(a)), fill=RED + (255,), width=8)
    d.ellipse((c[0] - 14, c[1] - 14, c[0] + 14, c[1] + 14), fill=(30, 32, 44, 255))
    return im


class Stopwatch(Viz):
    def scene(self, f, t):
        sp = self.spec
        stop = sp.get("stop_at")      # 분
        cx, cy = sp.get("cx", 640), sp.get("cy", 500)
        if stop is None:
            ang = (t * 540) % 360
            mm = int((t * 37) % 99)
            ss = int((t * 913) % 60)
            txt = f"{mm:02d}:{ss:02d}"
        else:
            st = self.ls(sp.get("stop_on", 1), sp.get("stop_offset", 0.0))
            k = _ease(t / max(0.3, st + 0.01)) if t < st else 1.0
            val = stop * k
            ang = (val % 1) * 360 * 1 + val * 6 * 60 if t < st else (stop % 1) * 360
            mm, ss = int(val), int((val - int(val)) * 60)
            txt = f"{mm:02d}:{ss:02d}"
        sw = _stopwatch(440, ang)
        shake = 4 * math.sin(t * 50) if stop is None else 0
        G.blit(f, sw, (cx + shake, cy), G.appear(t, 0, 0.3), "mm")
        G.blit(f, T(txt, 96, GOLD, "Black"), (cx, cy + 300), 1, "mm")
        if stop is not None and t >= self.ls(sp.get("stop_on", 1), sp.get("stop_offset", 0.0)):
            G.blit(f, G.pill(sp.get("stop_label", "딱!"), "Black", 56, (255, 255, 255), RED, pad=(26, 10)), (cx + 250, cy - 230), G.appear(t, self.ls(sp.get("stop_on", 1), sp.get("stop_offset", 0.0)), 0.25), "mm")
        # 보기 카드
        for i, ch in enumerate(sp.get("choices", [])):
            o = G.appear(t, self.ls(ch.get("on", 1), ch.get("offset", 0.0)), 0.3)
            if o <= 0:
                continue
            card = G.pill(ch["text"], "Black", 64, (20, 22, 30) if not ch.get("x") else (255, 255, 255), WHITE if not ch.get("x") else (70, 74, 90), pad=(40, 18), radius=24)
            y = 320 + i * 180
            G.blit(f, card, (1340 + (1 - o) * 200, y), o, "mm")
            if ch.get("x") and t >= self.ls(ch.get("x_on", ch.get("on", 1)), ch.get("x_offset", 0.8)):
                dd = ImageDraw.Draw(f)
                xx, yy = 1340, y
                dd.line((xx - card.width / 2, yy - 30, xx + card.width / 2, yy + 30), fill=RED + (255,), width=10)


# ── 드릴 ──────────────────────────────────────────────
class Drill(Viz):
    def scene(self, f, t):
        sp = self.spec
        d = ImageDraw.Draw(f)
        x0, x1, ytop, ybot = 360, 1560, 520, 960
        skew = 160
        # 윗면(입체) — 잔디
        d.polygon(((x0, ytop), (x1, ytop), (x1 - skew, ytop - 120), (x0 - skew, ytop - 120)), fill=(98, 160, 84, 255))
        # 앞면 층
        bands = [(0, 0.12, (130, 96, 66)), (0.12, 0.45, (152, 128, 104)), (0.45, 0.8, (110, 100, 108)), (0.8, 1.0, (200, 90, 44))]
        for a, b, c in bands:
            d.rectangle((x0, ytop + (ybot - ytop) * a, x1, ytop + (ybot - ytop) * b), fill=c + (255,))
        # 옆면
        d.polygon(((x1, ytop), (x1, ybot), (x1 - skew, ybot - 120), (x1 - skew, ytop - 120)), fill=(70, 56, 44, 255))
        hx = (x0 + x1) / 2 - 80
        dur = max(1.0, self.dur * 0.62)
        k = min(1.0, t / dur)
        depth = (ybot - ytop - 30) * _ease(k)
        # 구멍(윗면 타원 + 앞면 단면 기둥)
        d.ellipse((hx - 46, ytop - 76, hx + 46, ytop - 44), fill=(16, 14, 14, 255))
        d.rectangle((hx - 36, ytop, hx + 36, ytop + depth), fill=(18, 16, 18, 255))
        # 드릴 비트(돌아가는 줄무늬)
        by = ytop + depth
        if k < 1:
            bit = Image.new("RGBA", (90, 180), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bit)
            bd.polygon(((0, 0), (90, 0), (45, 180)), fill=(200, 206, 220, 255))
            for s in range(0, 220, 26):
                off = (t * 300) % 26
                bd.line((0, s + off - 40, 90, s + off), fill=(120, 126, 140, 255), width=8)
            m = Image.new("L", bit.size, 0)
            ImageDraw.Draw(m).polygon(((0, 0), (90, 0), (45, 180)), fill=255)
            bit.putalpha(m)
            G.blit(f, bit, (hx, by - 150), 1, "mt")
            d.rectangle((hx - 10, ytop - 230, hx + 10, by - 150), fill=(170, 176, 190, 255))
            # 드릴 몸통(땅 위)
            d.rounded_rectangle((hx - 70, ytop - 310, hx + 70, ytop - 230), 18, fill=(240, 180, 40, 255))
            G.blit(f, T("드릴", 30, (20, 22, 30), "Black"), (hx, ytop - 270), 1, "mm")
            rnd = random.Random(int(t * 20))
            for _ in range(14):   # 흙 튀김
                a = rnd.uniform(-2.6, -0.5)
                rr = rnd.uniform(20, 90)
                px, py = hx + rr * math.cos(a), ytop - 60 + rr * math.sin(a)
                d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(120, 90, 60, 230))
        else:
            # 악어새 점프 → 구멍 속으로
            j = min(1.0, (t - dur) / 1.2)
            mx = _lerp(hx + 240, hx, j)
            my = ytop - 160 - 120 * math.sin(math.pi * min(1, j * 1.1)) + (j ** 2) * 520
            G.blit(f, self.mascot(110).rotate(-200 * j, expand=True), (mx, my), 1, "mm")
            if j >= 0.95:
                G.blit(f, G.pill("출발!", "Black", 48, (20, 22, 30), GOLD, pad=(22, 8)), (hx + 230, ytop - 260), 1, "mm")
        # 깊이 표시
        G.blit(f, T(f"깊이 {int(_ease(k) * sp.get('to_m', 100))} m", 44, GOLD, "Black"), (x1 + 40, by), 1, "lm")


# ── 토끼굴 ────────────────────────────────────────────
def _icon(kind, s):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "clock":
        d.ellipse((4, 4, s - 4, s - 4), fill=(250, 230, 150, 255), outline=(120, 80, 30, 255), width=5)
        c = s / 2
        d.line((c, c, c, c - s * 0.3), fill=(40, 30, 20, 255), width=5)
        d.line((c, c, c + s * 0.22, c), fill=(40, 30, 20, 255), width=5)
    elif kind == "cup":
        d.rounded_rectangle((s * 0.15, s * 0.3, s * 0.7, s * 0.85), 10, fill=(255, 255, 255, 255), outline=(220, 90, 120, 255), width=5)
        d.arc((s * 0.6, s * 0.4, s * 0.92, s * 0.72), -90, 90, fill=(220, 90, 120, 255), width=6)
        d.ellipse((s * 0.1, s * 0.86, s * 0.78, s * 0.98), fill=(220, 90, 120, 255))
    elif kind == "book":
        d.rectangle((s * 0.15, s * 0.2, s * 0.85, s * 0.8), fill=(90, 120, 220, 255))
        d.rectangle((s * 0.2, s * 0.25, s * 0.8, s * 0.75), outline=(255, 255, 255, 200), width=3)
    elif kind == "card":
        d.rounded_rectangle((s * 0.25, s * 0.1, s * 0.75, s * 0.9), 8, fill=(255, 255, 255, 255), outline=(40, 40, 40, 255), width=3)
        d.polygon(((s * 0.5, s * 0.32), (s * 0.62, s * 0.5), (s * 0.5, s * 0.68), (s * 0.38, s * 0.5)), fill=(220, 40, 40, 255))
    elif kind == "key":
        d.ellipse((s * 0.1, s * 0.3, s * 0.45, s * 0.65), outline=(240, 190, 40, 255), width=7)
        d.rectangle((s * 0.42, s * 0.44, s * 0.9, s * 0.52), fill=(240, 190, 40, 255))
        d.rectangle((s * 0.75, s * 0.52, s * 0.82, s * 0.66), fill=(240, 190, 40, 255))
    return im


class Rabbit(Viz):
    def scene(self, f, t):
        d = ImageDraw.Draw(f)
        cx = S.W / 2
        # 굴 벽(흙 + 둥근 테두리) — 아래로 갈수록 깊어 보이게 원근
        for k in range(10, 0, -1):
            w = 300 + k * 60
            col = (70 + k * 6, 48 + k * 4, 34 + k * 3, 255)
            d.rounded_rectangle((cx - w / 2, 0, cx + w / 2, S.H), 60, fill=col)
        d.rounded_rectangle((cx - 300, 0, cx + 300, S.H), 80, fill=(26, 20, 22, 255))
        rnd = random.Random(5)
        kinds = ["clock", "cup", "book", "card", "key", "clock", "book", "card"]
        for i, kd in enumerate(kinds):
            sx = cx + rnd.uniform(-240, 240)
            sp_ = rnd.uniform(120, 220)
            y = (rnd.uniform(0, S.H) - t * sp_) % (S.H + 200) - 100
            ic = _icon(kd, 110).rotate((t * 60 + i * 40) % 360, expand=True)
            G.blit(f, ic, (sx, y), 0.95, "mm")
        m = self.mascot(170).rotate(25 * math.sin(t * 2.2), expand=True)
        G.blit(f, m, (cx, 560 + 14 * math.sin(t * 3)), 1, "mm")
        for k in range(6):   # 바람 선
            x = cx - 200 + k * 80
            yy = (k * 170 - t * 900) % S.H
            d.line((x, yy, x, yy + 90), fill=(255, 255, 255, 60), width=3)
        bub = self.spec.get("bubble")
        if bub:
            o = G.appear(t, self.ls(self.spec.get("bubble_on", 1), 0.4), 0.3)
            G.blit(f, G.pill(bub, "Black", 40, (20, 22, 30), WHITE, pad=(26, 14), radius=30), (cx + 330, 420), o, "lm")
        if self.spec.get("tag"):
            G.blit(f, G.pill(self.spec["tag"], "Bold", 30, (255, 255, 255), (90, 60, 140), pad=(18, 8)), (cx, 900), 1, "mm")


# ── 마이크 ────────────────────────────────────────────
class Mic(Viz):
    def scene(self, f, t):
        sp = self.spec
        d = ImageDraw.Draw(f)
        hx = 520
        d.rectangle((hx - 60, 300, hx + 60, S.H), fill=(20, 18, 20, 255))
        d.rectangle((0, 290, S.W, 300), fill=(98, 160, 84, 255))
        d.rectangle((hx - 60, 300, hx - 54, S.H), fill=(120, 96, 70, 255))
        d.rectangle((hx + 54, 300, hx + 60, S.H), fill=(120, 96, 70, 255))
        k = _ease(t / 2.0)
        my = _lerp(250, 780, k)
        d.line((hx, 160, hx, my - 40), fill=(200, 200, 210, 255), width=4)
        d.rounded_rectangle((hx - 24, my - 60, hx + 24, my + 10), 22, fill=(60, 64, 80, 255), outline=(200, 206, 220, 255), width=4)
        d.rectangle((hx - 6, my + 10, hx + 6, my + 50), fill=(60, 64, 80, 255))
        G.blit(f, T("12km 아래", 30, (200, 204, 214), "Bold"), (hx + 80, 820), 1, "lm")
        # 파형
        x0, x1, yc = 860, 1700, 560
        o = G.appear(t, self.ls(1, 1.5), 0.3)
        if o > 0:
            d.rounded_rectangle((x0 - 30, yc - 200, x1 + 30, yc + 200), 26, fill=(14, 18, 34, 230), outline=(255, 255, 255, 50), width=2)
            pts = []
            for i in range(160):
                x = x0 + (x1 - x0) * i / 159
                a = 140 * (0.4 + 0.6 * abs(math.sin(i * 0.13 + t * 3))) * math.sin(i * 0.9 + t * 25) * o
                pts.append((x, yc + a))
            d.line(pts, fill=(255, 90, 80, 255), width=4)
            G.blit(f, T("'지옥의 비명' 녹음?", 40, (255, 120, 110), "Black"), ((x0 + x1) / 2, yc - 240), o, "mb")
        st = self.ls(sp.get("stamp_on", 2), 0.3)
        if t >= st:
            k2 = min(1.0, (t - st) / 0.25)
            sz = int(_lerp(240, 150, k2))
            stamp = G.pill("가짜", "Black", sz, (255, 255, 255), RED, pad=(50, 10), radius=26).rotate(-12, expand=True)
            G.blit(f, stamp, ((x0 + x1) / 2, yc), min(1, k2 * 1.5), "mm")
            G.blit(f, T("공포 영화 소리를 이어 붙인 것", 36, WHITE, "Bold"), ((x0 + x1) / 2, yc + 260), G.appear(t, st + 0.4, 0.3), "mm")

    def extra_sfx(self):
        return [(self.ls(self.spec.get("stamp_on", 2), 0.3), "boom", 1.0), (self.ls(1, 1.5), "eerie", 0.6)]


# ── 국기 ──────────────────────────────────────────────
def flag(kind, w=180):
    h = int(w * 0.62)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "us":
        for i in range(13):
            d.rectangle((0, h * i / 13, w, h * (i + 1) / 13), fill=(190, 30, 45, 255) if i % 2 == 0 else (255, 255, 255, 255))
        d.rectangle((0, 0, w * 0.42, h * 7 / 13), fill=(40, 50, 110, 255))
        for r in range(5):
            for c in range(6):
                x, y = w * 0.42 * (c + 0.5) / 6, h * 7 / 13 * (r + 0.5) / 5
                d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 255))
    elif kind == "ussr":
        d.rectangle((0, 0, w, h), fill=(205, 20, 20, 255))
        cx, cy, R = w * 0.2, h * 0.2, h * 0.1
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = R if k % 2 == 0 else R * 0.45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, outline=(255, 215, 0, 255), width=2)
        d.arc((cx - R * 1.2, cy + R * 0.9, cx + R * 1.2, cy + R * 3.3), 200, 40, fill=(255, 215, 0, 255), width=4)
        d.line((cx - R * 0.9, cy + R * 3.2, cx + R * 0.9, cy + R * 1.4), fill=(255, 215, 0, 255), width=4)
    elif kind == "jp":
        d.rectangle((0, 0, w, h), fill=(255, 255, 255, 255))
        d.ellipse((w / 2 - h * 0.3, h / 2 - h * 0.3, w / 2 + h * 0.3, h / 2 + h * 0.3), fill=(190, 0, 40, 255))
    d.rectangle((0, 0, w - 1, h - 1), outline=(0, 0, 0, 80), width=2)
    return im


class DigRace(Viz):
    def scene(self, f, t):
        sp = self.spec
        d = ImageDraw.Draw(f)
        y0, y1 = 330, 840
        mx = sp.get("max_m", 13000)
        teams = sp["teams"]
        n = len(teams)
        x0, x1 = 300, S.W - 200
        # 눈금
        for m in range(0, mx + 1, 2000):
            yy = y0 + (y1 - y0) * m / mx
            d.line((x0 - 20, yy, x1, yy), fill=(255, 255, 255, 25), width=2)
            G.blit(f, T(f"{m // 1000}km", 26, (190, 196, 212), "Bold"), (x0 - 30, yy), 1, "rm")
        for i, tm in enumerate(teams):
            st = self.ls(tm.get("on", 1), tm.get("offset", 0))
            o = G.appear(t, st, 0.3)
            if o <= 0:
                continue
            cx = x0 + 120 + (x1 - x0 - 240) * (i + 0.5) / n
            G.blit(f, flag(tm["flag"], 170), (cx, y0 - 130), o, "mm")
            G.blit(f, T(tm["name"], 34, WHITE, "Black"), (cx, y0 - 60), o, "mm")
            sea = tm.get("sea_m", 0)
            if sea:
                ys = y0 + (y1 - y0) * sea / mx
                d.rectangle((cx - 90, y0, cx + 90, ys), fill=(40, 100, 200, int(200 * o)))
                G.blit(f, T("바다", 24, (200, 230, 255), "Bold"), (cx + 86, y0 + 10), o, "rt")
            dur = tm.get("grow", 2.5)
            k = _ease((t - st - 0.3) / dur)
            depth = sea + tm["m"] * k
            yy = y0 + (y1 - y0) * depth / mx
            ys = y0 + (y1 - y0) * sea / mx
            d.rectangle((cx - 20, ys, cx + 20, yy), fill=(26, 22, 22, 255), outline=GOLD + (255,), width=3)
            d.polygon(((cx - 26, yy), (cx + 26, yy), (cx, yy + 34)), fill=(210, 214, 226, 255))
            G.blit(f, T(f"{int(tm['m'] * k):,}m", 40, GOLD, "Black"), (cx + 40, yy), 1, "lm")
            if k >= 1 and tm.get("badge"):
                bc = RED if tm.get("bad") else ((20, 22, 30) if not tm.get("win") else (20, 22, 30))
                bg = (90, 94, 110) if tm.get("bad") else (GOLD if tm.get("win") else (60, 120, 220))
                G.blit(f, G.pill(tm["badge"], "Black", 32, (255, 255, 255) if bg != GOLD else (20, 22, 30), bg, pad=(16, 6)), (cx + 40, yy + 50), G.appear(t, st + 0.3 + dur, 0.3), "lm")
            G.blit(f, T(tm.get("year", ""), 28, (200, 204, 214), "Bold"), (cx, y0 - 24), o, "mm")


# ── 온도계 ────────────────────────────────────────────
class Thermo(Viz):
    def scene(self, f, t):
        sp = self.spec
        d = ImageDraw.Draw(f)
        rows = sp["rows"]
        vmax = sp.get("vmax", 6000)
        tx, ty0, ty1 = 330, 260, 860
        d.rounded_rectangle((tx - 40, ty0, tx + 40, ty1), 40, fill=(240, 242, 248, 255))
        d.ellipse((tx - 80, ty1 - 60, tx + 80, ty1 + 100), fill=(240, 242, 248, 255))
        cur = 0
        cur_i = -1
        for i, r in enumerate(rows):
            st = self.ls(r.get("on", 1), r.get("offset", 0))
            if t >= st:
                cur_i = i
        if cur_i >= 0:
            r = rows[cur_i]
            st = self.ls(r.get("on", 1), r.get("offset", 0))
            prev = rows[cur_i - 1]["value"] if cur_i > 0 else 0
            cur = _lerp(prev, r["value"], _ease((t - st) / 0.8))
        level = ty1 - (ty1 - ty0 - 40) * min(1.0, cur / vmax)
        heat = min(1.0, cur / vmax)
        col = (int(_lerp(255, 255, heat)), int(_lerp(120, 60, heat)), int(_lerp(60, 30, heat)))
        d.rounded_rectangle((tx - 24, level, tx + 24, ty1), 24, fill=col + (255,))
        d.ellipse((tx - 62, ty1 - 42, tx + 62, ty1 + 82), fill=col + (255,))
        G.blit(f, T(f"{int(cur):,}도", 64, col, "Black"), (tx + 70, level), 1, "lm")
        # 뜨거움 빛(화면 전체가 점점 붉게)
        glow = Image.new("RGBA", (S.W, S.H), (255, 90, 30, int(70 * heat)))
        f.alpha_composite(glow)
        # 정거장 카드
        for i, r in enumerate(rows):
            st = self.ls(r.get("on", 1), r.get("offset", 0))
            o = G.appear(t, st, 0.3)
            if o <= 0:
                continue
            y = 300 + i * 100
            hh = min(1.0, r["value"] / vmax)
            c = _col(r["color"]) if r.get("color") else (int(_lerp(255, 255, hh)), int(_lerp(220, 90, hh)), int(_lerp(120, 40, hh)))
            box = Image.new("RGBA", (760, 84), (0, 0, 0, 0))
            ImageDraw.Draw(box).rounded_rectangle((0, 0, 759, 83), 20, fill=(14, 18, 34, 220), outline=c + (255,), width=4 if i == cur_i else 2)
            box.alpha_composite(T(r["label"], 36, WHITE, "Black"), (28, 18))
            vt = T(r["text"], 44, c, "Black")
            box.alpha_composite(vt, (730 - vt.width, 14))
            G.blit(f, box, (820 + (1 - o) * 120, y), o, "lt")
        if sp.get("sun_on"):
            o = G.appear(t, self.ls(sp["sun_on"], sp.get("sun_offset", 0)), 0.5)
            if o > 0:
                sun = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
                sd = ImageDraw.Draw(sun)
                sd.ellipse((40, 40, 320, 320), fill=(255, 190, 60, 255))
                sun = sun.filter(ImageFilter.GaussianBlur(6))
                ImageDraw.Draw(sun).ellipse((70, 70, 290, 290), fill=(255, 230, 120, 255))
                G.blit(f, sun, (1740, 220 + 10 * math.sin(t * 2)), o, "mm")
                G.blit(f, T("태양 표면", 30, (255, 220, 120), "Black"), (1740, 410), o, "mm")


# ── 코끼리 ────────────────────────────────────────────
@lru_cache(maxsize=4)
def _elephant(w, col=(170, 176, 196)):
    h = int(w * 0.72)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (255,)
    d.ellipse((w * 0.18, h * 0.12, w * 0.92, h * 0.72), fill=c)          # 몸
    d.ellipse((0, h * 0.02, w * 0.42, h * 0.5), fill=c)                  # 머리
    d.ellipse((w * 0.14, h * 0.06, w * 0.42, h * 0.44), fill=tuple(int(v * 0.85) for v in col) + (255,))   # 귀
    d.rounded_rectangle((w * 0.0, h * 0.3, w * 0.1, h * 0.85), int(w * 0.04), fill=c)   # 코
    for x in (0.26, 0.42, 0.66, 0.8):
        d.rectangle((w * x, h * 0.6, w * (x + 0.1), h * 0.98), fill=c)
    d.ellipse((w * 0.12, h * 0.16, w * 0.17, h * 0.22), fill=(30, 30, 40, 255))
    return im


class Elephants(Viz):
    def scene(self, f, t):
        sp = self.spec
        d = ImageDraw.Draw(f)
        n_total = sp.get("n", 600)
        # 손가락 끝(살구색) + 손톱
        fx, fy = S.W / 2, 980
        d.rounded_rectangle((fx - 120, fy - 40, fx + 120, S.H + 200), 110, fill=(240, 196, 170, 255))
        d.rounded_rectangle((fx - 70, fy - 20, fx + 70, fy + 70), 30, fill=(255, 226, 224, 255), outline=(220, 170, 160, 255), width=4)
        G.blit(f, T("손톱 1cm²", 30, (120, 70, 60), "Black"), (fx, fy + 25), 1, "mm")
        st = self.ls(sp.get("on", 1), 0.3)
        k = _ease((t - st) / max(1.0, self.dur - st - 1.0))
        n = int(n_total * k)
        # 피라미드로 쌓기(작은 코끼리)
        ew = 30
        el = _elephant(ew)
        rows_ = []
        left = n
        width = 40
        while left > 0:
            m = min(width, left)
            rows_.append(m)
            left -= m
            width = max(6, width - 2)
        y = fy - 40
        for m in rows_:
            y -= el.height * 0.8
            x0 = fx - m * ew * 0.42
            for j in range(m):
                f.alpha_composite(el, (int(x0 + j * ew * 0.84), int(y)))
        G.blit(f, T(f"코끼리 {n}마리", 80, GOLD, "Black"), (S.W - 140, 420), 1, "rm")
        G.blit(f, T("= 지구 한가운데 누르는 힘", 36, WHITE, "Bold"), (S.W - 140, 500), 1, "rm")


# ── 속도 경주 ──────────────────────────────────────────
def _vehicle(kind, w):
    h = int(w * 0.38)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "train":
        d.rounded_rectangle((0, h * 0.15, w * 0.92, h * 0.85), int(h * 0.3), fill=(235, 240, 248, 255))
        d.polygon(((w * 0.75, h * 0.15), (w, h * 0.6), (w * 0.92, h * 0.85), (w * 0.75, h * 0.85)), fill=(235, 240, 248, 255))
        d.rectangle((w * 0.05, h * 0.62, w * 0.9, h * 0.7), fill=(40, 90, 200, 255))
        for k in range(4):
            d.rectangle((w * (0.1 + k * 0.15), h * 0.28, w * (0.2 + k * 0.15), h * 0.48), fill=(60, 70, 90, 255))
    elif kind == "plane":
        d.ellipse((0, h * 0.35, w, h * 0.65), fill=(235, 240, 248, 255))
        d.polygon(((w * 0.4, h * 0.5), (w * 0.62, h * 0.5), (w * 0.38, h * 1.0), (w * 0.28, h * 1.0)), fill=(200, 206, 220, 255))
        d.polygon(((w * 0.4, h * 0.5), (w * 0.62, h * 0.5), (w * 0.38, 0), (w * 0.28, 0)), fill=(200, 206, 220, 255))
        d.polygon(((0, h * 0.5), (w * 0.12, h * 0.5), (w * 0.04, h * 0.1)), fill=(40, 90, 200, 255))
    elif kind == "bullet":
        d.rectangle((0, h * 0.3, w * 0.6, h * 0.7), fill=(200, 150, 60, 255))
        d.pieslice((w * 0.2, h * 0.3, w * 1.0, h * 0.7), -90, 90, fill=(220, 170, 80, 255))
    return im


class SpeedRace(Viz):
    def scene(self, f, t):
        sp = self.spec
        d = ImageDraw.Draw(f)
        lanes = sp["lanes"]
        vmax = max(l["kmh"] for l in lanes)
        x0, x1 = 360, S.W - 120
        for i, ln in enumerate(lanes):
            y = 300 + i * 150
            o = G.appear(t, self.ls(ln.get("on", 1), ln.get("offset", 0)), 0.3)
            d.line((x0, y + 50, x1, y + 50), fill=(255, 255, 255, 40), width=2)
            G.blit(f, T(ln["label"], 36, WHITE, "Black"), (x0 - 30, y), o, "rm")
            G.blit(f, T(f"시속 {ln['kmh']:,}km", 26, (190, 196, 212), "Bold"), (x0 - 30, y + 38), o, "rm")
            if o <= 0:
                continue
            st = self.ls(ln.get("on", 1), ln.get("offset", 0))
            prog = (t - st) * 0.12 * (ln["kmh"] / vmax) * 8
            x = x0 + (x1 - x0) * (min(1.0, prog) if ln.get("kind") == "me" else min(1.2, prog))
            if ln.get("kind") == "me":
                im = self.mascot(110)
                for k in range(8):
                    d.line((x - 60 - k * 40, y - 10 + k * 3, x - 30 - k * 40, y - 10 + k * 3), fill=GOLD + (200 - k * 20,), width=6)
            else:
                im = _vehicle(ln["kind"], 160)
            G.blit(f, im, (x, y), 1, "mm")
            if ln.get("kind") == "me" and prog >= 1:
                G.blit(f, G.pill("총알의 10배", "Black", 44, (20, 22, 30), GOLD, pad=(22, 8)), (x1 - 40, y - 80), 1, "rm")

    def extra_sfx(self):
        out = []
        for ln in self.spec["lanes"]:
            if ln.get("kind") == "me":
                out.append((self.ls(ln.get("on", 1), ln.get("offset", 0)) + 0.1, "flyby", 1.0))
            elif ln.get("kind") == "bullet":
                out.append((self.ls(ln.get("on", 1), ln.get("offset", 0)) + 0.1, "whoosh", 0.7))
        return out


# ── 그네 ──────────────────────────────────────────────
class Swing(Viz):
    def scene(self, f, t):
        d = ImageDraw.Draw(f)
        px, py, L = 620, 230, 520
        d.rectangle((px - 300, py - 20, px + 300, py), fill=(150, 110, 70, 255))
        d.line((px - 280, py, px - 340, 960), fill=(150, 110, 70, 255), width=14)
        d.line((px + 280, py, px + 340, 960), fill=(150, 110, 70, 255), width=14)
        amp = math.radians(55)
        th = amp * math.cos(t * 2.2)
        om = -amp * 2.2 * math.sin(t * 2.2)
        bx, by = px + L * math.sin(th), py + L * math.cos(th)
        d.arc((px - L, py - L, px + L, py + L), 90 - 55, 90 + 55, fill=(255, 255, 255, 60), width=3)
        d.line((px, py, bx, by), fill=(220, 220, 230, 255), width=5)
        d.rounded_rectangle((bx - 60, by - 10, bx + 60, by + 10), 6, fill=(240, 180, 40, 255))
        G.blit(f, self.mascot(110), (bx, by - 60), 1, "mm")
        v = abs(om) / (amp * 2.2)
        L2 = 40 + 200 * v
        sgn = 1 if om > 0 else -1
        ax = bx + sgn * math.cos(th) * L2
        ay = by - sgn * math.sin(th) * L2
        d.line((bx, by + 30, ax, ay + 30), fill=GOLD + (255,), width=10)
        G.blit(f, T("가장 빠름", 40, GOLD, "Black"), (px, py + L + 70), 1, "mm")
        G.blit(f, T("멈춤", 36, SKY, "Black"), (px - L * math.sin(amp) - 30, py + L * math.cos(amp) - 40), 1, "rm")
        G.blit(f, T("멈춤", 36, SKY, "Black"), (px + L * math.sin(amp) + 30, py + L * math.cos(amp) - 40), 1, "lm")
        # 오른쪽: 터널 축소판(같은 리듬)
        sec = _earth_section(200)
        G.blit(f, sec, (1480, 560), 1, "mm")
        d.rectangle((1474, 340, 1486, 780), fill=(14, 16, 24, 235))
        my = 560 - 200 * math.cos(t * 2.2)
        G.blit(f, self.mascot(60), (1480, my), 1, "mm")
        G.blit(f, T("지구 터널도 똑같다", 36, WHITE, "Black"), (1480, 850), 1, "mm")


# ── 쌍둥이 지구(42분 vs 38분) ──────────────────────────
class Twin(Viz):
    def scene(self, f, t):
        d = ImageDraw.Draw(f)
        dur = max(1.0, self.dur - 1.2)
        for j, (label, period, cx, col) in enumerate((("속이 고른 지구", 84.4, 560, (180, 120, 80)), ("진짜 지구(속이 무거움)", 76.4, 1360, None))):
            r = 250
            if col:
                im = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
                ImageDraw.Draw(im).ellipse((20, 20, 20 + 2 * r, 20 + 2 * r), fill=col + (255,), outline=(110, 170, 90, 255), width=5)
                G.blit(f, im, (cx, 580), 1, "mm")
            else:
                G.blit(f, _earth_section(r), (cx, 580), 1, "mm")
                pulse = 1 + 0.06 * math.sin(t * 5)
                rr = r * 0.546 * pulse
                d.ellipse((cx - rr, 580 - rr, cx + rr, 580 + rr), outline=(255, 240, 160, 200), width=4)
                G.blit(f, T("무거운 쇠 속", 28, (255, 240, 180), "Black", stroke=4, stroke_fill=(40, 20, 10)), (cx, 580 + rr + 26), 1, "mm")
            d.rectangle((cx - 7, 580 - r - 10, cx + 7, 580 + r + 10), fill=(14, 16, 24, 235))
            tau = min(period / 2, 42.2 * min(1.0, t / dur))
            u = (1 - math.cos(2 * math.pi * tau / period)) / 2
            G.blit(f, self.mascot(70), (cx, 580 - r + 2 * r * u), 1, "mm")
            m, s = int(tau), int((tau - int(tau)) * 60)
            G.blit(f, T(label, 34, WHITE, "Black"), (cx, 250), 1, "mm")
            G.blit(f, T(f"{m:02d}분 {s:02d}초", 56, GOLD if tau < period / 2 else (255, 120, 100), "Black"), (cx, 310), 1, "mm")
            if tau >= period / 2 - 0.01:
                G.blit(f, G.pill("도착!", "Black", 40, (255, 255, 255), RED, pad=(18, 8)), (cx + r - 20, 580 + r - 10), 1, "mm")


# ── 자(서울↔부산 왕복 7번) ─────────────────────────────
class Ruler(Viz):
    def scene(self, f, t):
        d = ImageDraw.Draw(f)
        gx, gy0, gy1 = 560, 250, 930
        sec = _earth_section(340)
        G.blit(f, sec.crop((0, 0, sec.width, sec.height // 2 + 10)), (gx, gy0 - 20), 0.9, "mt")
        d.line((gx, gy0 + 20, gx, gy1 - 30), fill=GOLD + (255,), width=6)
        G.blit(f, T("6,371km", 44, GOLD, "Black"), (gx + 20, (gy0 + gy1) / 2), 1, "lm")
        # 오른쪽: 서울↔부산 왕복 쌓기
        st = self.ls(self.spec.get("on", 2))
        k = max(0.0, (t - st) / max(1.0, self.dur - st - 0.5))
        trips = min(7, int(k * 7 + 0.999)) if k > 0 else 0
        x0, x1 = 1080, 1700
        for i in range(7):
            y = 300 + i * 82
            on = i < trips
            c = GOLD if on else (80, 86, 104)
            d.line((x0, y, x1, y), fill=c + (255,), width=5)
            d.ellipse((x0 - 10, y - 10, x0 + 10, y + 10), fill=c + (255,))
            d.ellipse((x1 - 10, y - 10, x1 + 10, y + 10), fill=c + (255,))
            if i == 0:
                G.blit(f, T("서울", 28, WHITE, "Bold"), (x0, y - 18), 1, "mb")
                G.blit(f, T("부산", 28, WHITE, "Bold"), (x1, y - 18), 1, "mb")
            if on and i == trips - 1 and trips <= 7:
                q = (k * 7) % 1 if trips < 7 or k < 1 else 1
                tx = x0 + (x1 - x0) * (1 - abs(1 - 2 * q))
                G.blit(f, _vehicle("train", 120), (tx, y - 6), 1, "mm")
        G.blit(f, T(f"왕복 {trips}번", 64, GOLD, "Black"), ((x0 + x1) / 2, 900), 1, "mm")


TYPES.update({"globe": Globe, "stopwatch": Stopwatch, "drill": Drill, "rabbit": Rabbit, "mic": Mic, "digrace": DigRace,
              "thermo": Thermo, "elephants": Elephants, "speedrace": SpeedRace, "swing": Swing, "twin": Twin, "ruler": Ruler})
