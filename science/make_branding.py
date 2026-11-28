"""악어새 지식창고 프로필(800x800) · 배너(2560x1440) — 사용자 제공 원형 일러스트 사용
  python3 science/make_branding.py → science/out/branding/
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "youtube"))
from engine import draw as G  # noqa: E402

OUT = HERE / "out" / "branding"
SRC = HERE / "assets" / "character_src.png"
SKY = (151, 215, 253)
SKY2 = (226, 243, 255)
NAVY = (22, 44, 92)
CORAL = (240, 96, 72)


def circle_cut(inset=8):
    im = Image.open(SRC).convert("RGBA")
    cx, cy, r = 624, 618, 620 - inset            # 원 경계(검은 바탕 바깥 제거)
    k = 4
    m = Image.new("L", (im.width * k, im.height * k), 0)
    ImageDraw.Draw(m).ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), fill=255)
    m = m.resize(im.size, Image.LANCZOS)
    im.putalpha(m)
    return im.crop((cx - r, cy - r, cx + r, cy + r))


def grad(w, h, top, bot):
    y = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top) * (1 - y) + np.array(bot) * y
    return Image.fromarray(np.broadcast_to(a, (h, w, 3)).astype(np.uint8), "RGB").convert("RGBA")


def profile(c):
    N = 800
    bg = Image.new("RGBA", (N, N), SKY + (255,))
    pic = c.resize((N, N), Image.LANCZOS)
    bg.alpha_composite(pic)
    bg.convert("RGB").save(OUT / "profile.png")
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse((0, 0, N, N), fill=255)
    prev = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    prev.paste(bg, (0, 0), m)
    prev.save(OUT / "profile_preview_circle.png")


def banner(c):
    W, H = 2560, 1440
    bg = grad(W, H, SKY, SKY2)
    d = ImageDraw.Draw(bg, "RGBA")
    rng = np.random.default_rng(3)
    for _ in range(70):                           # 은은한 물방울 점
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 16)
        if 470 < x < 2090 and 470 < y < 970:   # 글자·캐릭터 영역은 비움
            continue
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(40, 110))))
    for gx in range(0, W, 80):                    # 아주 옅은 모눈(지식 노트 느낌)
        d.line((gx, 0, gx, H), fill=(255, 255, 255, 26))
    for gy in range(0, H, 80):
        d.line((0, gy, W, gy), fill=(255, 255, 255, 26))
    # 캐릭터: 안전 영역(1546x423, 가운데) 왼쪽
    size = 400
    pic = c.resize((size, size), Image.LANCZOS)
    sh = Image.new("RGBA", (size + 60, size + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((30, 40, size + 30, size + 50), fill=(20, 50, 100, 70))
    x0, y0 = 540, (H - size) // 2
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (x0 - 30, y0 - 30))
    ImageDraw.Draw(bg).ellipse((x0 - 8, y0 - 8, x0 + size + 8, y0 + size + 8), fill=(255, 255, 255, 255))
    bg.alpha_composite(pic, (x0, y0))
    tx = x0 + size + 70
    name = G.text_img("악어새 지식창고", "Black", 150, NAVY)
    tag = G.text_img("어려운 지식에서, 알맹이만 쏙쏙", "ExtraBold", 58, CORAL)
    sub = G.text_img("과학 · 수학 · 역사 · 생활 원리를 쉽고 정확하게", "SemiBold", 40, (60, 80, 120))
    total = name.height + 18 + tag.height + 22 + sub.height
    y = H // 2 - total // 2
    bg.alpha_composite(name, (tx, y))
    y += name.height + 18
    bg.alpha_composite(tag, (tx + 6, y))
    y += tag.height + 22
    bg.alpha_composite(sub, (tx + 6, y))
    assert tx + name.width < 2053, f"안전 영역 초과: {tx + name.width}"
    bg.convert("RGB").save(OUT / "banner.png")
    chk = bg.copy()
    ImageDraw.Draw(chk).rectangle(((W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2), outline=(255, 0, 0, 255), width=6)
    chk.convert("RGB").resize((1280, 720)).save(OUT / "banner_safearea_check.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    c = circle_cut()
    profile(c)
    banner(c)
    print("완료 →", OUT)
