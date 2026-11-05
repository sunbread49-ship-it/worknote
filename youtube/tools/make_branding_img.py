"""사용자 일러스트(assets/media/character_croc_bird_src.png)로 프로필·배너 생성.
흰 배경만 골라 투명 처리 → 따뜻한 노랑 배경 + 색감 보정.

  python tools/make_branding_img.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import yaml  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter  # noqa: E402

from engine import draw as G  # noqa: E402

SRC = ROOT / "assets" / "media" / "character_croc_bird_src.png"
CUT = ROOT / "assets" / "media" / "character_croc_bird_cutout.png"
OUT = ROOT / "out" / "branding"
NAVY = (22, 30, 56)
Y1, Y2 = (255, 224, 128), (250, 196, 84)   # 배경 노랑 그라데이션


def cutout():
    src = Image.open(SRC).convert("RGB")
    W, H = src.size
    m = src.copy()
    for xy in [(5, 5), (W - 6, 5), (5, H - 6), (W - 6, H - 6), (W // 2, 5), (5, H // 2), (300, 500), (1350, 500)]:
        if sum(m.getpixel(xy)) > 690:
            ImageDraw.floodfill(m, xy, (255, 0, 255), thresh=38)
    a = np.array(m)
    bg = (a[:, :, 0] == 255) & (a[:, :, 1] == 0) & (a[:, :, 2] == 255)
    alpha = Image.fromarray((~bg * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2))
    img = ImageEnhance.Contrast(ImageEnhance.Color(src).enhance(1.15)).enhance(1.05).convert("RGBA")
    img.putalpha(alpha)
    img.save(CUT)
    return img


def radial(size, inner, outer, center=(0.5, 0.5)):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w * center[0]) / w) ** 2 + ((yy - h * center[1]) / h) ** 2) / 0.75
    r = np.clip(r, 0, 1)[..., None]
    arr = np.array(inner) * (1 - r) + np.array(outer) * r
    return Image.fromarray(arr.astype("uint8"), "RGB").convert("RGBA")


def profile(ch):
    N = 800
    bg = radial((N, N), Y1, Y2, (0.45, 0.4))
    sc = ch.crop((230, 30, ch.width, 1010))          # 몸통은 오른쪽 화면 밖으로 이어지게
    k = 690 / 1100
    sc = sc.resize((int(sc.width * k), int(sc.height * k)), Image.LANCZOS)
    bg.alpha_composite(sc, (40, 130))
    bg.convert("RGB").save(OUT / "profile.png")
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse((0, 0, N, N), fill=255)
    prev = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    prev.paste(bg, (0, 0), m)
    prev.save(OUT / "profile_preview_circle.png")


def banner(ch, cfg):
    W, H = 2560, 1440
    bg = radial((W, H), (255, 236, 170), (246, 196, 92), (0.35, 0.5))
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 120):
        d.line((x, 0, x, H), fill=(255, 255, 255, 40))
    for y in range(0, H, 120):
        d.line((0, y, W, y), fill=(255, 255, 255, 40))
    # 배경 상승 차트 선
    import random
    rnd = random.Random(7)
    pts, y = [], 1180
    for x in range(0, W + 40, 40):
        y += rnd.uniform(-34, 20) - 3
        pts.append((x, y))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).line(pts, fill=(255, 255, 255, 120), width=10, joint="curve")
    bg.alpha_composite(lay)
    # 안전 영역(모든 기기 공통): x 507~2053, y 508~931
    sx0, sy0, sy1 = 507, 508, 931
    sc = ch.crop((230, 30, 1536, 1024))
    hgt = 440
    sc = sc.resize((int(sc.width * hgt / sc.height), hgt), Image.LANCZOS)
    fade = 140  # 원본 그림 오른쪽 끝(잘린 몸통)을 부드럽게 사라지게
    a = np.array(sc.getchannel("A")).astype(float)
    a[:, -fade:] *= np.linspace(1, 0, fade)[None, :]
    sc.putalpha(Image.fromarray(a.astype("uint8")))
    bg.alpha_composite(sc, (sx0 - 10, sy0 - 10))
    tx = sx0 + sc.width + 30
    name = G.text_img(cfg["name"], "Black", 140, NAVY)
    bg.alpha_composite(name, (tx, sy0 + 40))
    tag = G.text_img(cfg.get("tagline", ""), "ExtraBold", 46, (196, 92, 20))
    bg.alpha_composite(tag, (tx + 6, sy0 + 40 + name.height + 12))
    sub = G.text_img(cfg.get("banner_sub", ""), "SemiBold", 36, (70, 64, 60))
    bg.alpha_composite(sub, (tx + 6, sy0 + 40 + name.height + 12 + tag.height + 22))
    bg.convert("RGB").save(OUT / "banner.png")
    chk = bg.copy()
    ImageDraw.Draw(chk).rectangle((sx0, sy0, 2053, sy1), outline=(255, 0, 0, 255), width=6)
    chk.convert("RGB").resize((1280, 720)).save(OUT / "banner_safearea_check.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load((ROOT / "channel.yaml").read_text(encoding="utf-8"))
    ch = cutout()
    profile(ch)
    banner(ch, cfg)
    print("완료 →", OUT)
