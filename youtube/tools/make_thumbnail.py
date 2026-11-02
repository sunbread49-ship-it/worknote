"""조회수형 썸네일 (큰 숫자 + 급락 차트 + 화살표). 1280x720 PNG.

  python tools/make_thumbnail.py episodes/ep002_tqqq_reddit
에피소드 yaml 의 thumbnail_v2 블록을 읽는다.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import render  # noqa: E402
from engine import charts, scenes  # noqa: E402
from engine import draw as G  # noqa: E402
from engine import style as S  # noqa: E402


def arrow(w, h, color, width=70):
    """아래로 꺾여 내려가는 굵은 화살표"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0, h * 0.05), (w * 0.35, h * 0.35), (w * 0.5, h * 0.25), (w * 0.86, h * 0.78)]
    d.line(pts, fill=color + (255,), width=width, joint="curve")
    ex, ey = pts[-1]
    ang = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
    L = width * 2.2
    tip = (ex + math.cos(ang) * L * 0.9, ey + math.sin(ang) * L * 0.9)
    left = (ex + math.cos(ang + 2.2) * L, ey + math.sin(ang + 2.2) * L)
    right = (ex + math.cos(ang - 2.2) * L, ey + math.sin(ang - 2.2) * L)
    d.polygon([tip, left, right], fill=color + (255,))
    return im


def main(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    ep, channel = render.load(ep_dir)
    th = ep["thumbnail_v2"]
    W, H = S.W, S.H
    f = Image.new("RGBA", (W, H), (8, 10, 20, 255))
    # 배경: 오른쪽 붉은 글로우 + 왼쪽 어둡게
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((900, -200, 2300, 1200), fill=(200, 30, 50, 120))
    gd.ellipse((-400, 500, 700, 1500), fill=(40, 90, 220, 70))
    f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(180)))
    # 차트 (오른쪽, 크게)
    ch = th["chart"]
    lc = charts.LineChart(dict(ch, draw={"on": 1, "dur": 0.01}), rect=tuple(th.get("chart_rect", (860, 170, 1000, 760))))
    line = lc.line
    # 선을 굵게 보이도록 살짝 번지게 한 번 더
    f.alpha_composite(line.filter(ImageFilter.GaussianBlur(6)))
    f.alpha_composite(line)
    f.alpha_composite(line)
    # 화살표
    if th.get("arrow", True):
        a = arrow(760, 620, scenes.col(th.get("arrow_color", "up"), S.UP), 64)
        G.blit(f, a.filter(ImageFilter.GaussianBlur(1)), (1080, 230))
    # 왼쪽 그라데이션으로 글자 가독성 확보
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(0, 1100, 4):
        sd.rectangle((x, 0, x + 4, H), fill=(6, 8, 16, int(235 * max(0, 1 - x / 1100) ** 0.7)))
    f.alpha_composite(shade)
    # 배지
    y = 70
    if th.get("badge"):
        b = G.pill(th["badge"], "Black", 58, (16, 18, 28), S.GOLD, pad=(30, 12), radius=14)
        G.blit(f, b, (80, y))
        y += b.height + 30
    # 큰 글자 (외곽선 + 그림자)
    for ln in th["lines"]:
        size = ln.get("size", 200)
        color = scenes.col(ln.get("color"), S.FG)
        t = G.text_img(ln["text"], "Black", size, color, stroke=max(6, size // 18), stroke_fill=(0, 0, 0))
        sh = G.text_img(ln["text"], "Black", size, (0, 0, 0), stroke=max(6, size // 18), stroke_fill=(0, 0, 0))
        G.blit(f, sh.filter(ImageFilter.GaussianBlur(10)), (80 + 8, y + 12), 0.8)
        G.blit(f, t, (80, y))
        y += t.height - int(size * 0.12)
    if th.get("sub"):
        s_ = G.text_img(th["sub"], "ExtraBold", 64, (255, 255, 255), stroke=5, stroke_fill=(0, 0, 0))
        G.blit(f, s_, (86, y + 24))
    out = ROOT / "out" / ep_dir.name / "thumbnail.png"
    f.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out)
    print("썸네일 →", out)


if __name__ == "__main__":
    main(sys.argv[1])
