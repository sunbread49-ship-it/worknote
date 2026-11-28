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


def swoosh(d, x0, x1, y, k, rise=70, thick=30):
    """붓 밑줄 (가운데 굵고 양끝 가는) — 빨강"""
    for i in range(61):
        t = i / 60
        x, yy = x0 + t * (x1 - x0), y - rise * math.sin(t * math.pi * 0.9) + 40 * t
        r = (thick * 0.45 + thick * math.sin(t * math.pi)) * k
        d.ellipse((x - r, yy - r * 0.7, x + r, yy + r * 0.7), fill=RED)


def s1_sign_green():
    """사인 · 반전: 진초록 바탕 + 흰 손글씨 + 빨간 붓 밑줄"""
    im = Image.new("RGB", (N * 2, N * 2), GREEN); d = ImageDraw.Draw(im)
    centered(d, "악어새", font("NanumPenScript-Regular.ttf", 700), 720, WHITE, cx=N)
    swoosh(d, 280, 1320, 1130, 1)
    return im.resize((N, N), Image.LANCZOS)


def s2_sign_mono():
    """사인 · 한 글자: 크게 쓴 '악' + 빨간 붓 밑줄 — 작게 봐도 읽힘"""
    im = Image.new("RGB", (N * 2, N * 2), WHITE); d = ImageDraw.Draw(im)
    centered(d, "악", font("NanumPenScript-Regular.ttf", 1250), 700, GREEN, cx=N)
    swoosh(d, 380, 1230, 1230, 1.3, rise=60)
    return im.resize((N, N), Image.LANCZOS)


def s3_sign_seal():
    """사인 + 낙관: 붓글씨 '악어새' + 딥레드 도장(흰 '악')"""
    im = Image.new("RGB", (N * 2, N * 2), WHITE); d = ImageDraw.Draw(im)
    centered(d, "악어새", font("EastSeaDokdo-Regular.ttf", 720), 720, GREEN, cx=N - 40)
    sx, sy, ss = 1080, 1000, 250
    d.rounded_rectangle((sx, sy, sx + ss, sy + ss), radius=24, fill=RED)
    d.rounded_rectangle((sx + 16, sy + 16, sx + ss - 16, sy + ss - 16), radius=14, outline=WHITE, width=6)
    centered(d, "악", font("NanumMyeongjo-ExtraBold.ttf", 170), sy + ss / 2, WHITE, cx=sx + ss / 2)
    return im.resize((N, N), Image.LANCZOS)


def autocrop(name, bg, pad=0.16):
    """3D 렌더에서 물체 둘레만 정사각형으로 잘라 가운데 배치"""
    im = Image.open(OUT / name).convert("RGB")
    import numpy as np
    a = np.asarray(im).astype(int); diff = np.abs(a - a[5, 5]).sum(2) > 60
    ys, xs = np.where(diff)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    half = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 * (1 + pad * 2)
    box = [int(cx - half), int(cy - half), int(cx + half), int(cy + half)]
    out = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), tuple(int(v) for v in a[5, 5]))
    out.paste(im.crop(box), (0, 0))
    return out.resize((N, N), Image.LANCZOS)


def t1_word():
    return autocrop("p4a.png", WHITE, 0.08)


def t2_dark():
    return Image.open(OUT / "p4b.png").convert("RGB").crop((90, 40, 730, 680)).resize((N, N), Image.LANCZOS)


def t3_coin():
    return autocrop("p4c.png", WHITE, 0.03)


def circle(im, s):
    im = im.resize((s * 4, s * 4), Image.LANCZOS)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse((0, 0, *im.size), fill=255)
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); o.paste(im, (0, 0), m)
    return o.resize((s, s), Image.LANCZOS)


def sheet(items, path):
    lab = font("Pretendard-Bold.otf", 34)
    sh = Image.new("RGB", (len(items) * 440 + 40, 760), (235, 235, 232))
    sh.paste(Image.new("RGB", (sh.width, 160), (15, 15, 15)), (0, 600))
    d = ImageDraw.Draw(sh)
    for i, (name, im) in enumerate(items):
        x = 40 + i * 440
        sh.paste(c := circle(im, 400), (x, 60), c)
        d.text((x, 10), name, font=lab, fill=(30, 30, 30))
        for s, dx, y in ((88, 0, 488), (40, 110, 512), (88, 0, 636), (40, 110, 660)):
            sh.paste(c := circle(im, s), (x + dx, y), c)
    sh.save(path, quality=92)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    v1 = [("① 글자", p1_word()), ("② 기하 도형", p2_bird()), ("③ 사인", p3_sign()), ("④ 3D", p4_3d())]
    for i, (_, im) in enumerate(v1):
        im.save(OUT / f"profile_{i + 1}.png")
    sheet(v1, OUT / "프로필_시안.jpg")
    v2 = [("③-A 사인 반전", s1_sign_green()), ("③-B 사인 한 글자", s2_sign_mono()), ("③-C 사인 + 낙관", s3_sign_seal())]
    v3 = [("④-A 3D 단어", t1_word()), ("④-B 3D 진초록", t2_dark()), ("④-C 3D 동전", t3_coin())]
    for tag, items in (("3", v2), ("4", v3)):
        for i, (_, im) in enumerate(items):
            im.save(OUT / f"profile_{tag}{'abc'[i]}.png")
    sheet(v2, OUT / "프로필_v2_사인.jpg")
    sheet(v3, OUT / "프로필_v2_3D.jpg")
    print("→", OUT)


if __name__ == "__main__":
    main()
