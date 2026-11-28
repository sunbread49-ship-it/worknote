"""sci05 '지구를 뚫고 뛰어내리면' 썸네일 10종 — 우주 배경 · 실제 대륙 3D 지구본 · 지구 단면 · 떨어지는 악어새 (영상과 같은 그림)
  python tools/thumb_earth.py → out/sci05_earth_tunnel/thumbs10/T01~T10 + 비교표.jpg
패턴(THUMB_PATTERNS): 궁금(P05 결과 감추기) · 놀람(P01 상식 반대) · 실감(P10 꽉 채우기) · 승부(P08 대결)
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import editorial as E  # noqa: E402
from engine.dive import _earth_section, _space  # noqa: E402
from engine.globe import CITIES, globe_img, project  # noqa: E402
from engine.viz5 import _stopwatch, _vehicle  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out/sci05_earth_tunnel/thumbs10"
W, H = 1920, 1080
GOLD, WHITE, RED, SKY = (255, 204, 40), (255, 255, 255), (235, 70, 60), (120, 200, 255)


def txt(s, size, col=WHITE, stroke=10):
    return E.T(s, size, col, "Black", stroke=stroke, stroke_fill=(8, 10, 20))


def lines(f, rows, x, y, anchor="l", gap=8):
    for s, size, col in rows:
        im = txt(s, size, col)
        xx = x if anchor == "l" else (x - im.width // 2 if anchor == "m" else x - im.width)
        f.alpha_composite(im, (int(xx), int(y)))
        y += im.height + gap
    return y


def mascot(h, rot=0):
    m = E._mascot_img({"name": "악어새 지식창고"}, h)
    return m.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else m


def section(f, cx, cy, r, faller_y=None, rot=180, fh=150):
    sec = _earth_section(r)
    f.alpha_composite(sec, (int(cx - sec.width / 2), int(cy - sec.height / 2)))
    d = ImageDraw.Draw(f)
    d.rectangle((cx - 12, cy - r - 30, cx + 12, cy + r + 30), fill=(10, 12, 18, 255))
    d.line((cx - 13, cy - r - 30, cx - 13, cy + r + 30), fill=(255, 255, 255, 140), width=3)
    d.line((cx + 13, cy - r - 30, cx + 13, cy + r + 30), fill=(255, 255, 255, 140), width=3)
    if faller_y is not None:
        m = mascot(fh, rot)
        f.alpha_composite(m, (int(cx - m.width / 2), int(faller_y - m.height / 2)))
        for k in range(6):
            yy = faller_y - fh * 0.7 - k * 34
            d.line((cx - 60 + k * 24, yy, cx - 60 + k * 24, yy - 70), fill=(255, 255, 255, 120), width=5)


def globe(f, cx, cy, r, lon, lat, alpha=255):
    g = globe_img(r, lon, lat, alpha=alpha)
    f.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    return g


def pin(f, cx, cy, r, name, lon0, lat0, label, col=GOLD):
    x, y, v = project(*CITIES[name], lon0, lat0, r)
    d = ImageDraw.Draw(f)
    d.ellipse((cx + x - 16, cy + y - 16, cx + x + 16, cy + y + 16), fill=col + (255,), outline=WHITE + (255,), width=5)
    p = E.G.pill(label, "Black", 48, (20, 22, 30) if col == GOLD else WHITE, col if col == GOLD else (40, 110, 210), pad=(22, 10))
    f.alpha_composite(p, (int(cx + x + 30), int(cy + y - p.height / 2)))
    return cx + x, cy + y


def qmark(f, x, y, size=260, col=GOLD):
    q = txt("?", size, col, 14)
    f.alpha_composite(q, (int(x - q.width / 2), int(y - q.height / 2)))


def tag(f):
    t = E.T("악어새 지식창고 · 상상 실험", 40, (200, 206, 222), "Bold")
    f.alpha_composite(t, (W - t.width - 40, H - t.height - 30))


def make(v):
    f = _space().copy().resize((W, H))
    d = ImageDraw.Draw(f)
    if v == "T01":   # 궁금: 단면 + 떨어지는 악어새 + 몇 분?
        section(f, 1400, 560, 430, 330, 160, 170)
        y = lines(f, [("지구를 뚫고", 120, WHITE), ("뛰어내리면", 120, WHITE)], 80, 160)
        lines(f, [("몇 분?", 250, GOLD)], 70, y + 10)
    elif v == "T02":   # 스톱워치 + 결과 감추기
        globe(f, 1450, 560, 380, 127, 25)
        sw = _stopwatch(420, 250)
        f.alpha_composite(sw, (980, 300))
        y = lines(f, [("서울 → 지구 반대편", 92, WHITE)], 80, 150)
        lines(f, [("??분", 300, GOLD)], 70, y + 30)
    elif v == "T03":   # 지구본 관통 화살표
        cx, cy, r = 1320, 560, 420
        globe(f, cx, cy, r, 127, 30)
        sx, sy = pin(f, cx, cy, r, "서울", 127, 30, "서울")
        for k in range(18):
            q = k / 18
            px, py = sx, sy + (cy + r - 40 - sy) * q
            d.ellipse((px - 10, py - 10, px + 10, py + 10), fill=GOLD + (240,))
        qmark(f, sx, cy + r - 10, 220)
        lines(f, [("땅을 계속 파면", 110, WHITE), ("반대편으로", 130, GOLD), ("나갈 수", 130, GOLD), ("있을까?", 130, GOLD)], 70, 150)
    elif v == "T04":   # 총알 10배
        section(f, 1480, 560, 400, 560, 180, 170)
        b = _vehicle("bullet", 360)
        f.alpha_composite(b, (900, 820))
        lines(f, [("지구 한가운데", 100, WHITE), ("총알보다", 140, WHITE), ("10배 빠르다", 160, GOLD)], 70, 150)
    elif v == "T05":   # 상식 반대: 도착해도 끝이 아니다
        section(f, 1440, 560, 410, 940, 0, 150)
        for k in range(5):
            y0 = 220 + k * 150
            d.line((1660, y0, 1660, y0 + 90), fill=GOLD + (200,), width=10)
            d.polygon(((1640, y0 + 90), (1680, y0 + 90), (1660, y0 + 120)), fill=GOLD + (220,))
        lines(f, [("지구 반대편 도착", 100, WHITE), ("근데", 120, WHITE), ("끝이 아니다", 170, RED)], 70, 180)
    elif v == "T06":   # 서울 반대편은 바다
        cx, cy, r = 1360, 560, 430
        lon0, lat0 = -53, -30
        globe(f, cx, cy, r, lon0, lat0)
        pin(f, cx, cy, r, "서울 반대편", lon0, lat0, "서울의 정반대편", SKY)
        lines(f, [("서울에서", 110, WHITE), ("똑바로 뚫으면", 110, WHITE), ("여기 나온다", 150, GOLD)], 70, 200)
    elif v == "T07":   # 인류 12km vs 6,371km
        d.rectangle((0, 760, W, H), fill=(120, 92, 66, 255))
        d.rectangle((0, 740, W, 760), fill=(98, 160, 84, 255))
        d.rectangle((1500, 760, 1530, 800), fill=(10, 10, 14, 255))
        f.alpha_composite(txt("12km", 90, GOLD), (1560, 780))
        f.alpha_composite(txt("인류가 판 가장 깊은 구멍", 44, WHITE, 6), (1300, 900))
        lines(f, [("지구 반대편까지", 110, WHITE), ("12,742km", 230, GOLD), ("인류는 12km에서 멈췄다", 70, WHITE)], 70, 90)
    elif v == "T08":   # 실감: 악어새가 화면 가득 떨어짐
        sec = _earth_section(700)
        f.alpha_composite(sec, (int(W / 2 - sec.width / 2), 150))
        d.rectangle((W / 2 - 14, 0, W / 2 + 14, H), fill=(10, 12, 18, 255))
        m = mascot(340, 170)
        f.alpha_composite(m, (int(W / 2 - m.width / 2), 420))
        lines(f, [("뛰어내렸더니", 120, WHITE)], 80, 120)
        lines(f, [("42분?!", 220, GOLD)], W - 80, 120, "r")
    elif v == "T09":   # 대결: 42분 vs 38분
        for cx, lab, col in ((520, "42분?", WHITE), (1400, "38분?", GOLD)):
            sec = _earth_section(320)
            f.alpha_composite(sec, (int(cx - sec.width / 2), 470))
            d.rectangle((cx - 8, 480, cx + 8, 1140), fill=(10, 12, 18, 255))
            f.alpha_composite(txt(lab, 170, col), (int(cx - 200), 250))
        f.alpha_composite(txt("VS", 120, RED), (900, 600))
        lines(f, [("지구 반대편까지 진짜 정답은", 90, WHITE)], W / 2, 70, "m")
    elif v == "T10":   # 미니멀: 지구본 반 갈라짐
        g = globe_img(430, 127, 25)
        half = g.crop((0, 0, g.width // 2, g.height))
        f.alpha_composite(half, (int(W / 2 - g.width / 2 + 260), 100))
        sec = _earth_section(430)
        rh = sec.crop((sec.width // 2, 0, sec.width, sec.height))
        f.alpha_composite(rh, (int(W / 2 + 260), int(100 + (g.height - sec.height) / 2)))
        m = mascot(170, 180)
        f.alpha_composite(m, (int(W / 2 + 260 - m.width / 2), 420))
        lines(f, [("지구 속으로", 110, WHITE), ("뛰어내리면", 110, WHITE), ("몇 분?", 200, GOLD)], 60, 170)
    tag(f)
    return f.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    names = [f"T{i:02d}" for i in range(1, 11)]
    outs = []
    for nm in names:
        im = make(nm).resize((1280, 720), Image.LANCZOS)
        p = OUT / f"{nm}.png"
        im.save(p)
        outs.append((nm, p))
    sheet = Image.new("RGB", (2 * 650 + 10, 5 * 400 + 10), (20, 20, 24))
    for i, (nm, p) in enumerate(outs):
        x, y = 10 + (i % 2) * 650, 10 + (i // 2) * 400
        sheet.paste(Image.open(p).resize((640, 360)), (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + 364), nm, fill=(180, 255, 60))
    sheet.save(OUT / "비교표.jpg", quality=90)
    print("비교표 →", OUT / "비교표.jpg")
