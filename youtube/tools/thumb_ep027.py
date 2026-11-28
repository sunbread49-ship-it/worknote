"""EP027 시스코 닷컴 결말 썸네일 (THUMB_PATTERNS: 실사 어둡게 + 큰 글씨 2줄 + 숫자 하나 + 질문 꼬리표)
  python3 tools/thumb_ep027.py → out/ep027_cisco_dotcom/thumbnail.png (A) · thumb_B.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/ep027_cisco_dotcom"
W, H = TH.W, TH.H
YEL, RED, WHITE = (255, 214, 40), (255, 60, 60), (255, 255, 255)


def plaque(name, w, h, pad=26):
    lg = Image.open(ROOT / f"assets/photos/{name}.png").convert("RGBA")
    k = min((w - 2 * pad) / lg.width, (h - 2 * pad) / lg.height)
    lg = lg.resize((int(lg.width * k), int(lg.height * k)), Image.LANCZOS)
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=(255, 255, 255, 255))
    p.alpha_composite(lg, ((w - lg.width) // 2, (h - lg.height) // 2))
    return p


def base():
    f = Image.new("RGBA", (W, H), (10, 12, 20, 255))
    L = TH.photo_fill("cisco_hq", W // 2, H, (0.5, 0.5), dark=0.62, gray=1.0)
    R = TH.photo_fill("nvidia_hq", W // 2, H, (0.5, 0.5), dark=0.55, gray=0.3)
    f.paste(L, (0, 0)); f.paste(R, (W // 2, 0))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # 아래쪽 어둡게(글자)
    d = ImageDraw.Draw(g)
    for y in range(H // 3, H):
        d.line((0, y, W, y), fill=(0, 0, 0, int(200 * (y - H // 3) / (H * 2 / 3))))
    f.alpha_composite(g)
    ImageDraw.Draw(f).rectangle((W // 2 - 4, 0, W // 2 + 4, H), fill=YEL + (255,))
    return f


def make_a():
    f = base()
    TH.shadowed(f, plaque("logo_cisco", 430, 170), (W // 4, 120), "mt")
    TH.shadowed(f, plaque("logo_nvidia", 430, 170), (W * 3 // 4, 120), "mt")
    TH.shadowed(f, TH.T("2000", 90, WHITE), (W // 4, 310), "mt")
    TH.shadowed(f, TH.T("2026", 90, WHITE), (W * 3 // 4, 310), "mt")
    eq = Image.new("RGBA", (190, 190), (0, 0, 0, 0))
    ImageDraw.Draw(eq).ellipse((0, 0, 189, 189), fill=RED + (255,))
    eq.alpha_composite(TH.T("=", 150, WHITE, stroke=0), (48, 0))
    TH.shadowed(f, eq, (W // 2, 150), "mt")
    TH.shadowed(f, TH.T("꼭대기 1,000만 원", 120, WHITE), (W // 2, 560), "mt")
    TH.shadowed(f, TH.T("원금까지 25년", 230, YEL, hl="25년", hl_color=RED), (W // 2, 700), "mt")
    tag = TH.T(" AI 거품 꺼지면? ", 64, (20, 20, 20), stroke=0)
    bg = Image.new("RGBA", (tag.width + 30, tag.height + 16), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), 18, fill=YEL + (255,))
    bg.alpha_composite(tag, (15, 8))
    f.alpha_composite(bg.rotate(4, expand=True, resample=Image.BICUBIC), (W - bg.width - 90, 440))
    return f


def make_b():
    f = base()
    TH.shadowed(f, plaque("logo_nvidia", 520, 200), (W // 2, 120), "mt")
    TH.shadowed(f, TH.T("제2의 시스코?", 150, WHITE, hl="시스코", hl_color=YEL), (W // 2, 380), "mt")
    TH.shadowed(f, TH.T("원금까지 25년", 230, RED), (W // 2, 640), "mt")
    return f


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_a().convert("RGB").save(OUT / "thumbnail.png")
    make_b().convert("RGB").save(OUT / "thumb_B.png")
    print("썸네일 →", OUT / "thumbnail.png", "·", OUT / "thumb_B.png")
