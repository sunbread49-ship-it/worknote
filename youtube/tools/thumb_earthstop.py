"""sci07 '지구가 딱 1초 멈추면' 썸네일 4종 — 영상 속 HyperFrames 장면(실제 위성사진 3D 지구 · 지평선 입자 · 계기판 · 태양)을 그대로 배경으로
  python tools/thumb_earthstop.py → out/sci07_earth_stop/thumbs/T01~T04 + 비교표.jpg"""
import glob
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/sci07_earth_stop/thumbs"
HF = ROOT / "out/sci07_earth_stop/hf"
F = str(ROOT / "assets/fonts/Pretendard-Black.otf")
Y, W_ = (255, 201, 60), (255, 255, 255)


BG = ROOT / "out/sci07_earth_stop/thumbs/bg"   # 글자 없이 따로 구운 배경(HyperFrames)


def frame(d, k=None):
    return Image.open(BG / f"{d}.jpg").convert("RGBA").resize((1920, 1080))


def txt(f, s, size, xy, col=W_, anchor="la"):
    d = ImageDraw.Draw(f)
    d.text(xy, s, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(6, size // 14), stroke_fill=(5, 8, 18), anchor=anchor)


def shade(f, side="left"):
    g = Image.new("L", (1920, 1080))
    d = ImageDraw.Draw(g)
    for x in range(1920):
        a = int(230 * max(0, 1 - x / 1100)) if side == "left" else int(200 * max(0, (x - 820) / 1100))
        d.line((x, 0, x, 1080), fill=a)
    f.alpha_composite(Image.merge("RGBA", (Image.new("L", (1920, 1080), 0),) * 3 + (g,)))


def t1():
    f = frame("globe")
    f = f.transform(f.size, Image.AFFINE, (1, 0, -430, 0, 1, 0), Image.BICUBIC)
    d = ImageDraw.Draw(f); d.ellipse((1125 - 18, 495 - 18, 1125 + 18, 495 + 18), fill=Y, outline=(5, 8, 18), width=5)
    shade(f)
    txt(f, "지구가 딱 1초", 150, (80, 250)); txt(f, "멈추면?", 230, (80, 430), Y)
    txt(f, "시속 1,330km로 달리는 중", 64, (90, 760))
    return f


def t2():
    f = frame("horizon")
    txt(f, "1초 멈추면", 150, (960, 360), W_, "ma"); txt(f, "우리는 총알처럼 날아간다", 110, (960, 540), Y, "ma")
    return f


def t3():
    f = frame("horizon")
    shade(f, "left")
    txt(f, "시속 1,330km", 150, (80, 200), Y); txt(f, "→ 0", 260, (80, 380), W_); txt(f, "지구가 급정거하면?", 110, (80, 700))
    return f


def t4():
    f = frame("sun")
    txt(f, "지구가 멈추기 전에", 120, (960, 120), W_, "ma"); txt(f, "태양이 먼저 꺼진다?", 150, (960, 280), (255, 110, 60), "ma")
    return f


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ims = []
    for k, fn in enumerate((t1, t2, t3, t4), 1):
        im = fn().convert("RGB"); im.save(OUT / f"T0{k}.png"); ims.append(im.resize((960, 540)))
    sheet = Image.new("RGB", (1920, 1080))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sheet.save(OUT / "비교표.jpg", quality=88)
    print(OUT)
