"""색 조합 샘플 슬라이드 (2026-11-16 사용자 레퍼런스: 레트로 포스터 3색 조합 11종)
같은 내용(EP017 '72% 비과세' + 세금 막대 비교)을 조합별로 칠해 비교 → out/palettes/
  python3 tools/palette_samples.py
역할: paper(바탕) · ink(글자 · 선) · accent(포인트) — 조합마다 사람이 지정
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import draw as G, style as S  # noqa: E402

W, H = 1920, 1080
OUT = S.ROOT / "out" / "palettes"


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# (번호, 이름, paper, ink, accent, 세 번째 보조) — 사용자 첨부 순서
PALETTES = [
    (1, "Lilac · Greige · Deep Navy", "#B8B0A6", "#1B2A49", "#C8A2C8"),
    (2, "Vanilla · Flamingo · Brown", "#F3E5AB", "#6B4423", "#FC8EAC"),
    (3, "Butter Yellow · Cream · Mocha", "#FFF6D6", "#8B6B5A", "#F6D77A"),
    (4, "Peach · Sand · Forest Green", "#F5C0A0", "#2E5E3E", "#DCCBAA"),
    (5, "Sage Green · Oatmeal · Terracotta", "#9CAF88", "#C8643C", "#E3D9C6"),
    (6, "Rust Red · Tan · Flame Orange", "#B7410E", "#D2B48C", "#E25822"),
    (7, "Coffee Brown · Apple Red · Vanilla Beige", "#4B3621", "#EDE0C8", "#C8322B"),
    (8, "Bright White · Dark Green · Deep Red", "#FBFBF9", "#01422B", "#A3161A"),
    (9, "Linen · Parsley Green · Tomato Red", "#FAF0E6", "#4A7C3F", "#FF6347"),
    (10, "Sky Blue · Lemon · Coral Red", "#8CC8EA", "#F2544B", "#FFF44F"),
    (11, "Butter Cream · Coral · Deep Green", "#F5E6B8", "#1F4D3A", "#FF7F50"),
]


def grain(img, amt=10, seed=1):
    """종이 질감 (잔 노이즈 + 아주 옅은 얼룩)"""
    rng = np.random.default_rng(seed)
    a = np.asarray(img.convert("RGB"), dtype=np.int16)
    n = rng.normal(0, amt, a.shape[:2])[..., None]
    a = np.clip(a + n, 0, 255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA")


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def slide(p):
    num, name, paper, ink, acc = p
    paper, ink, acc = hx(paper), hx(ink), hx(acc)
    f = Image.new("RGBA", (W, H), paper + (255,))
    f = grain(f, 7, num)
    d = ImageDraw.Draw(f)
    # 포스터 테두리 (이중선)
    d.rectangle((40, 40, W - 41, H - 41), outline=ink + (255,), width=6)
    d.rectangle((58, 58, W - 59, H - 59), outline=ink + (255,), width=2)
    # 위쪽 띠: 채널 · 꼭지
    G.blit(f, G.text_img("주식 악어새  ·  주식 궁금증, 숫자로 풀기", "Bold", 30, ink), (100, 92), 1, "lt")
    G.blit(f, G.text_img("EP.017", "Black", 30, ink), (W - 100, 92), 1, "rt")
    d.line((100, 146, W - 100, 146), fill=ink + (255,), width=3)
    # 왼쪽: 제목 + 큰 숫자
    G.blit(f, G.text_img("국내 1위 커버드콜 · 받은 분배금 중", "Bold", 40, ink), (110, 200), 1, "lt")
    big = G.text_img("72%", "Black", 330, acc)
    # 잉크색 그림자(오프셋 인쇄 느낌)
    sh = G.text_img("72%", "Black", 330, ink)
    G.blit(f, sh, (118, 268), 1, "lt")
    G.blit(f, big, (104, 254), 1, "lt")
    G.blit(f, G.text_img("세금이 안 붙었다", "Black", 92, ink), (110, 640), 1, "lt")
    pl = G.pill("이렇게만 사면 된다", "Black", 44, paper, ink, pad=(28, 12), radius=10)
    G.blit(f, pl, (110, 780), 1, "lt")
    # 오른쪽: 영수증 카드 (세금 비교)
    cx0, cy0, cw, ch = 1080, 210, 700, 640
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rectangle((0, 0, cw - 1, ch - 1), fill=paper + (255,), outline=ink + (255,), width=4)
    card.alpha_composite(G.text_img("같은 1,000만 원 · 떼인 세금", "Black", 38, ink), (36, 34))
    cd.line((36, 100, cw - 36, 100), fill=ink + (255,), width=2)
    rows = [("TIGER 배당CC", 107, "107만", ink), ("KODEX 200타겟위클리", 22, "22만", acc)]
    for i, (lab, v, txt, c) in enumerate(rows):
        y = 140 + i * 210
        card.alpha_composite(G.text_img(lab, "Bold", 34, ink), (36, y))
        bw = int((cw - 260) * v / 107)
        cd.rectangle((36, y + 60, 36 + bw, y + 130), fill=c + (255,), outline=ink + (255,), width=3)
        card.alpha_composite(G.text_img(txt, "Black", 56, ink), (56 + bw, y + 64))
    card.alpha_composite(G.text_img("세금 5배 차이", "Black", 64, acc if abs(lum(acc) - lum(paper)) > 70 else ink), (36, ch - 120))
    sh2 = Image.new("RGBA", (cw, ch), ink + (255,))
    f.alpha_composite(sh2, (cx0 + 14, cy0 + 14))
    f.alpha_composite(card, (cx0, cy0))
    # 아래: 자막 자리 (영상과 같은 위치)
    sub = G.text_img("같은 월배당인데, 분배금 72%에 세금이 안 붙어요.", "Black", 52, paper)
    box = Image.new("RGBA", (sub.width + 60, sub.height + 30), ink + (235,))
    box.alpha_composite(sub, (30, 15))
    G.blit(f, box, (W / 2, H - 150), 1, "mt")
    # 조합 이름 (샘플 라벨)
    G.blit(f, G.text_img(f"{num:02d}  {name}", "Bold", 30, ink), (W / 2, 92), 1, "mt")
    return f.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ims = []
    for p in PALETTES:
        im = slide(p)
        im.save(OUT / f"palette_{p[0]:02d}.png")
        ims.append(im)
    cols = 3
    th = [im.resize((640, 360)) for im in ims]
    rows = (len(th) + cols - 1) // cols
    sheet = Image.new("RGB", (640 * cols + 20 * (cols + 1), 360 * rows + 20 * (rows + 1)), (20, 20, 24))
    for i, im in enumerate(th):
        sheet.paste(im, (20 + (i % cols) * 660, 20 + (i // cols) * 380))
    sheet.save(OUT / "비교표.jpg", quality=90)
    print("→", OUT)


if __name__ == "__main__":
    main()
