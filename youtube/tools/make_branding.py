"""채널 프로필 이미지(800x800)와 배너(2560x1440) 생성.

  python tools/make_branding.py
channel.yaml 의 name / tagline 을 사용. 결과: out/branding/
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from engine import draw as G  # noqa: E402
from engine import illust as I  # noqa: E402
from engine import style as S  # noqa: E402

OUT = ROOT / "out" / "branding"
NAVY = (14, 20, 38)
CREAM = (255, 244, 214)


def radial(size, inner, outer):
    w, h = size
    im = Image.new("RGB", size, outer)
    d = ImageDraw.Draw(im)
    steps = 60
    for i in range(steps):
        r = max(w, h) * 0.75 * (1 - i / steps)
        c = tuple(int(outer[j] + (inner[j] - outer[j]) * (i / steps)) for j in range(3))
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(20)).convert("RGBA")


def shadow(im, blur=18, alpha=110, off=(10, 16)):
    a = im.getchannel("A").point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255))
    blk.putalpha(a)
    sh.alpha_composite(blk, (40 + off[0], 40 + off[1]))
    return sh.filter(ImageFilter.GaussianBlur(blur))


def calculator(w, h, display="×3 = ?"):
    k = 3
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W, H = w * k, h * k
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=int(W * 0.12), fill=(40, 46, 66, 255))
    d.rounded_rectangle((W * 0.03, H * 0.02, W * 0.97, H * 0.96), radius=int(W * 0.1), fill=(56, 64, 90, 255))
    d.rounded_rectangle((W * 0.1, H * 0.07, W * 0.9, H * 0.27), radius=int(W * 0.05), fill=(196, 226, 190, 255))
    colors = [(230, 232, 240)] * 3 + [S.GOLD]
    for r in range(4):
        for c in range(4):
            x0 = W * (0.1 + c * 0.205)
            y0 = H * (0.33 + r * 0.155)
            col = S.UP if (r == 3 and c == 3) else colors[c]
            d.rounded_rectangle((x0, y0, x0 + W * 0.17, y0 + H * 0.12), radius=int(W * 0.03), fill=col + (255,))
    out = im.reduce(k)
    t = G.text_img(display, "Black", int(h * 0.12), (30, 50, 30))
    out.alpha_composite(t, (int(w * 0.86 - t.width), int(h * 0.17 - t.height / 2)))
    return out


def ant_with_money(size):
    """채널 캐릭터: 돈주머니를 든 안경 개미 (engine/character.py)"""
    from engine.character import ant_character
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(ant_character(size, "moneybag"))
    sp = I.emoji("sparkles", int(size * 0.16))
    canvas.alpha_composite(sp, (int(size * 0.78), int(size * 0.12)))
    coin = I.emoji("coin", int(size * 0.16)).rotate(-15, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(coin, (int(size * 0.04), int(size * 0.56)))
    return canvas


def _old_ant_with_money(size):
    """(이전) Fluent 3D 이모지 조합"""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ant = I.emoji("ant", int(size * 0.86)).rotate(-8, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(ant, (int(size * 0.0), int(size * 0.06)))
    bag = I.emoji("moneybag", int(size * 0.5)).rotate(8, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(bag, (int(size * 0.47), int(size * 0.42)))
    coin = I.emoji("coin", int(size * 0.2)).rotate(-15, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(coin, (int(size * 0.74), int(size * 0.3)))
    sp = I.emoji("sparkles", int(size * 0.18))
    canvas.alpha_composite(sp, (int(size * 0.66), int(size * 0.08)))
    return canvas


def profile(ch):
    N = 800
    bg = radial((N, N), (255, 220, 110), (250, 178, 50))
    d = ImageDraw.Draw(bg)
    d.ellipse((22, 22, N - 22, N - 22), outline=NAVY + (255,), width=20)
    a = ant_with_money(640)
    bg.alpha_composite(shadow(a, 14, 90, (6, 12)), (80 - 40, 110 - 40))
    bg.alpha_composite(a, (80, 110))
    c = calculator(140, 196, "×3").rotate(-12, resample=Image.BICUBIC, expand=True)
    bg.alpha_composite(c, (575, 420))
    bg.convert("RGB").save(OUT / "profile.png")
    # 원형 미리보기
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse((0, 0, N, N), fill=255)
    prev = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    prev.paste(bg, (0, 0), m)
    prev.save(OUT / "profile_preview_circle.png")


def banner(ch):
    W, H = 2560, 1440
    bg = radial((W, H), (34, 44, 80), NAVY)
    # 배경 상승 차트 라인
    d = ImageDraw.Draw(bg)
    import random
    rnd = random.Random(4)
    pts, y = [], 1150
    for x in range(0, W + 40, 40):
        y += rnd.uniform(-38, 22) - 4
        pts.append((x, y))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).line(pts, fill=S.GOLD + (60,), width=10, joint="curve")
    bg.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    # 격자
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for x in range(0, W, 120):
        gd.line((x, 0, x, H), fill=(255, 255, 255, 8))
    for yy in range(0, H, 120):
        gd.line((0, yy, W, yy), fill=(255, 255, 255, 8))
    bg.alpha_composite(g)
    # 안전 영역(모든 기기에서 보이는 곳): 가운데 1546x423 → x 507~2053, y 508~931
    sx0, sy0, sx1, sy1 = 507, 508, 2053, 931
    a = ant_with_money(400)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))  # 어두운 개미가 묻히지 않게 뒤에 금색 원
    ImageDraw.Draw(glow).ellipse((sx0 + 10, sy0 + 20, sx0 + 390, sy0 + 400), fill=S.GOLD + (255,))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4)))
    bg.alpha_composite(shadow(a), (sx0 - 10 - 40, sy0 + 10 - 40))
    bg.alpha_composite(a, (sx0 - 10, sy0 + 10))
    calc = calculator(150, 210, "×3").rotate(-8, resample=Image.BICUBIC, expand=True)
    bg.alpha_composite(calc, (sx1 - 190, sy0 + 120))
    name = G.text_img(ch["name"], "Black", 150, (255, 255, 255), stroke=0)
    tx = sx0 + 420
    bg.alpha_composite(name, (tx, sy0 + 50))
    # 이름 중 '계산기' 강조 밑줄
    tag = G.text_img(ch.get("tagline", ""), "ExtraBold", 58, S.GOLD)
    bg.alpha_composite(tag, (tx + 6, sy0 + 50 + name.height + 10))
    sub = G.text_img(ch.get("banner_sub", ""), "SemiBold", 40, (190, 198, 220))
    bg.alpha_composite(sub, (tx + 6, sy0 + 50 + name.height + 10 + tag.height + 22))
    bg.convert("RGB").save(OUT / "banner.png")
    # 안전 영역 확인용
    chk = bg.copy()
    ImageDraw.Draw(chk).rectangle((sx0, sy0, sx1, sy1), outline=(255, 0, 0, 255), width=6)
    chk.convert("RGB").resize((1280, 720)).save(OUT / "banner_safearea_check.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ch = yaml.safe_load((ROOT / "channel.yaml").read_text(encoding="utf-8"))
    profile(ch)
    banner(ch)
    print("완료 →", OUT)
