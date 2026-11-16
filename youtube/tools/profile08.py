"""채널 프로필 시안 (주식 악어새) — 색 조합 08만 사용: #FBFBF9 · #01422B · #A3161A
  python3 tools/profile08.py   (3D는 먼저 tools/blender_profile.py → out/profile/p4_3d_raw.png)
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FD = ROOT / "assets" / "fonts"
OUT = ROOT / "out" / "profile"
WHITE, GREEN, RED = (251, 251, 249), (1, 66, 43), (163, 22, 26)
N = 800


def font(name, size):
    return ImageFont.truetype(str(FD / name), size)


def centered(d, text, f, cy, fill, cx=N / 2):
    b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2), text, font=f, fill=fill)
    return b


def p1_word():
    """글자형: 진초록 바탕 + 흰 '악어새' + 딥레드 점"""
    im = Image.new("RGB", (N, N), GREEN); d = ImageDraw.Draw(im)
    f = font("Pretendard-Black.otf", 225)
    b = d.textbbox((0, 0), "악어새", font=f); w = b[2] - b[0]
    x0 = N / 2 - (w + 70) / 2
    d.text((x0 - b[0], N / 2 - (b[1] + b[3]) / 2 - 10), "악어새", font=f, fill=WHITE)
    d.ellipse((x0 + w + 22, 470, x0 + w + 72, 520), fill=RED)
    return im


def p2_bird():
    """기하 도형형: 원(몸) · 삼각형(꼬리) · 위로 향한 빨간 부리(상승) — 흰 바탕"""
    im = Image.new("RGB", (N, N), WHITE); d = ImageDraw.Draw(im)
    cx, cy, r = 360, 470, 165
    d.polygon([(cx - 110, cy + 60), (cx - 250, cy + 175), (cx - 185, cy - 30)], fill=GREEN)        # 꼬리
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)                                           # 몸
    hx, hy, hr = cx + 118, cy - 140, 90
    d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=GREEN)                                      # 머리
    a = math.radians(-35)
    tip = (hx + 190 * math.cos(a), hy + 190 * math.sin(a))
    d.polygon([(hx + 50, hy - 62), tip, (hx + 82, hy + 38)], fill=RED)                               # 부리(우상향)
    d.ellipse((hx + 6, hy - 40, hx + 52, hy + 6), fill=WHITE)
    d.ellipse((hx + 20, hy - 26, hx + 44, hy - 2), fill=GREEN)
    d.rectangle((190, 650, 620, 663), fill=GREEN)                                                     # 바닥선
    return im


def p3_sign():
    """사인형: 손글씨 '악어새' 진초록 + 빨간 붓 밑줄 — 흰 바탕"""
    im = Image.new("RGB", (N * 2, N * 2), WHITE); d = ImageDraw.Draw(im)
    f = font("NanumPenScript-Regular.ttf", 680)
    centered(d, "악어새", f, 720, GREEN, cx=N)
    pts = [(300 + t * 1000, 1130 - 70 * math.sin(t * math.pi * 0.9) + 40 * t) for t in [i / 60 for i in range(61)]]
    for i, p in enumerate(pts):
        r = 14 + 30 * math.sin(i / 60 * math.pi)
        d.ellipse((p[0] - r, p[1] - r * 0.7, p[0] + r, p[1] + r * 0.7), fill=RED)
    return im.resize((N, N), Image.LANCZOS)


def p4_3d():
    im = Image.open(OUT / "p4_3d_raw.png").convert("RGB")
    return im.crop((20, 0, 780, 760)).resize((N, N), Image.LANCZOS)


def circle(im, s):
    im = im.resize((s * 4, s * 4), Image.LANCZOS)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse((0, 0, *im.size), fill=255)
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); o.paste(im, (0, 0), m)
    return o.resize((s, s), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = [("① 글자", p1_word()), ("② 기하 도형", p2_bird()), ("③ 사인", p3_sign()), ("④ 3D", p4_3d())]
    lab = font("Pretendard-Bold.otf", 34)
    sheet = Image.new("RGB", (4 * 440 + 40, 760), (235, 235, 232))
    dark = Image.new("RGB", (sheet.width, 160), (15, 15, 15)); sheet.paste(dark, (0, 600))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(items):
        im.save(OUT / f"profile_{i + 1}.png")
        x = 40 + i * 440
        sheet.paste(c := circle(im, 400), (x, 60), c)
        d.text((x, 10), name, font=lab, fill=(30, 30, 30))
        for s, dx, y in ((88, 0, 488), (40, 110, 512)):                       # 실제 표시 크기 (밝은 화면)
            sheet.paste(c := circle(im, s), (x + dx, y), c)
        for s, dx, y in ((88, 0, 636), (40, 110, 660)):                       # 다크 모드
            sheet.paste(c := circle(im, s), (x + dx, y), c)
    sheet.save(OUT / "프로필_시안.jpg", quality=92)
    print("→", OUT)


if __name__ == "__main__":
    main()
