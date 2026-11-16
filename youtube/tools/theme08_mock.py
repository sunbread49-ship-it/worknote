"""주식 채널 색 시안 — 08 Bright White #FBFBF9 · Dark Green #01422B · Deep Red #A3161A (2026-11-16 사용자)
원칙: 실사 · 3D는 그대로, 08은 '요소'에만 (카드 · 막대 · 띠 · 자막 · 라벨) — 화면 전체를 칠하는 건 일부 장면만
  python3 tools/theme08_mock.py <프레임 폴더>   → out/theme08/
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import draw as G, style as S  # noqa: E402

WHITE, GREEN, RED = (251, 251, 249), (1, 66, 43), (163, 22, 26)
INK = (20, 24, 22)
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = S.ROOT / "out" / "theme08"
T = lambda s, sz, c, w="Black", **k: G.text_img(s, w, sz, c, **k)


def grain(im, amt=6, seed=3):
    a = np.asarray(im.convert("RGB"), dtype=np.int16)
    a = np.clip(a + np.random.default_rng(seed).normal(0, amt, a.shape[:2])[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA")


def paper(w, h, border=True):
    p = grain(Image.new("RGBA", (w, h), WHITE + (255,)), 5)
    if border:
        d = ImageDraw.Draw(p)
        d.rectangle((0, 0, w - 1, h - 1), outline=GREEN + (255,), width=5)
        d.rectangle((12, 12, w - 13, h - 13), outline=GREEN + (255,), width=2)
    return p


def offset_card(f, card, xy, off=14):
    """잉크(초록) 판을 살짝 어긋나게 깔아 인쇄물 느낌"""
    f.alpha_composite(Image.new("RGBA", card.size, GREEN + (255,)), (xy[0] + off, xy[1] + off))
    f.alpha_composite(card, xy)


def bg(name, w, h, dark=0.35, blur=0):
    im = Image.open(SRC / name).convert("RGB").resize((w, h), Image.BICUBIC)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(im).enhance(1 - dark).convert("RGBA")


def chrome(f, chapter="세금 반전"):
    """공통 머리 · 자막 요소 (롱폼)"""
    G.blit(f, G.pill("주식 악어새", "Black", 30, WHITE, GREEN, pad=(18, 8), radius=6), (60, 50), 1, "lt")
    G.blit(f, G.pill(chapter, "Bold", 28, GREEN, WHITE, pad=(18, 8), radius=6), (f.width - 60, 50), 1, "rt")


def subtitle(f, text, hl=""):
    tx = T(text, 52, WHITE, highlight=hl, hl_fill=(255, 196, 190))
    box = Image.new("RGBA", (tx.width + 64, tx.height + 30), GREEN + (240,))
    ImageDraw.Draw(box).rectangle((0, box.height - 6, box.width, box.height), fill=RED + (255,))
    box.alpha_composite(tx, (32, 14))
    G.blit(f, box, (f.width / 2, f.height - 150), 1, "mt")


# ── 롱폼 ─────────────────────────────────────────────
def L1_punch():
    """큰 숫자: 실사 영상 그대로 + 흰 숫자 · 빨간 밑줄 띠 · 초록 라벨"""
    f = bg("f_money.png", 1920, 1080, 0.45)
    chrome(f, "인트로")
    G.blit(f, G.pill("국내 1위 커버드콜 · 1,000만 원이 받은 분배금 중", "Black", 40, WHITE, GREEN, pad=(26, 12), radius=8), (960, 230), 1, "mt")
    big = T("72% 비과세", 250, WHITE, stroke=0)
    bar = Image.new("RGBA", (int(big.width * 1.04), int(big.height * 0.32)), RED + (240,))
    G.blit(f, bar, (960, 560), 1, "mm")
    G.blit(f, big, (960, 470), 1, "mm")
    G.blit(f, T("세금이 안 붙었다", 64, WHITE), (960, 690), 1, "mt")
    subtitle(f, "같은 월배당인데, 분배금 72%에 세금이 안 붙어요.", "72%")
    return f


def L2_card():
    """데이터 카드: 흐린 실사 위에 흰 종이 카드 (막대 초록/빨강)"""
    f = bg("f_decline.png", 1920, 1080, 0.5, blur=10)
    chrome(f, "1000만 원의 결과")
    card = paper(1300, 640)
    d = ImageDraw.Draw(card)
    card.alpha_composite(T("상장일에 1,000만 원 → 지금 (세후)", 34, GREEN, "Bold"), (50, 40))
    card.alpha_composite(T("분배금까지 다 더하면", 64, INK), (50, 90))
    rows = [("서학개미 1위 · JEPQ", 1548, RED), ("QQQ · 같은 4년 6개월 · 달러 기준", 2119, GREEN),
            ("국내 2위 · TIGER 나스닥100CC", 1262, RED), ("TIGER 미국나스닥100 · 같은 2년 5개월", 1396, GREEN)]
    for i, (lab, v, c) in enumerate(rows):
        y = 210 + i * 100
        card.alpha_composite(T(lab, 30, INK, "Bold"), (50, y))
        w = int(760 * v / 2119)
        d.rectangle((50, y + 44, 50 + w, y + 80), fill=c + (255,))
        card.alpha_composite(T(f"{v:,}만", 44, c), (70 + w, y + 36))
    offset_card(f, card, (310, 190))
    subtitle(f, "같은 기간 나스닥은 2,119만 원이었어요.", "2,119만 원")
    return f


def L3_full():
    """가끔 쓰는 '08 전면' 장면 (요약 · 전환용) — 종이 포스터"""
    f = paper(1920, 1080, border=False)
    d = ImageDraw.Draw(f)
    d.rectangle((40, 40, 1879, 1039), outline=GREEN + (255,), width=6)
    d.rectangle((58, 58, 1861, 1021), outline=GREEN + (255,), width=2)
    G.blit(f, T("주식 악어새 · 오늘의 결론", 34, GREEN, "Bold"), (960, 110), 1, "mt")
    sh = T("월배당은\n월급이 아니라 월세다", 120, GREEN, align="center", line_gap=1.1)
    tx = T("월배당은\n월급이 아니라 월세다", 120, RED, align="center", line_gap=1.1)
    G.blit(f, sh, (968, 268), 1, "mt")
    G.blit(f, tx, (960, 260), 1, "mt")
    G.blit(f, G.pill("집값 오를 몫을 미리 팔고 받는 돈", "Black", 46, WHITE, GREEN, pad=(28, 12), radius=8), (960, 640), 1, "mt")
    subtitle(f, "집값 오를 몫을 미리 팔고 받는, 월세예요.")
    return f


def L4_3d():
    """3D 동전 탑은 그대로 · 라벨만 08 (흰 판 + 초록/빨강 숫자)"""
    f = Image.open(SRC / "f_coins.png").convert("RGBA").resize((1920, 1080))
    chrome(f, "1000만 원의 결과")
    for x, lab, val, c in ((0.30, "그냥 나스닥100", "1,396만", GREEN), (0.56, "커버드콜 원금", "953만", RED), (0.725, "분배금(세후)", "308만", RED)):
        tag = paper(280, 120)
        tag.alpha_composite(T(lab, 28, INK, "Bold"), (24, 16))
        tag.alpha_composite(T(val, 50, c), (24, 54))
        G.blit(f, tag, (1920 * x, 760), 1, "mt")
    subtitle(f, "그냥 나스닥은 1,396만 원까지 자랐어요.", "1,396만 원")
    return f


# ── 쇼츠 ─────────────────────────────────────────────
def banner(f, l1, l2):
    """위쪽 고정 제목 띠: 검정 → 진초록, 빨간 상자 → 딥레드"""
    b = Image.new("RGBA", (1080, 330), GREEN + (255,))
    G.blit(b, T(l1, 76, WHITE), (540, 52), 1, "mt")
    l2i = T(l2, 86, WHITE)
    box = Image.new("RGBA", (l2i.width + 44, l2i.height + 22), RED + (255,))
    box.alpha_composite(l2i, (22, 11))
    G.blit(b, box, (540, 160), 1, "mt")
    ImageDraw.Draw(b).rectangle((0, 322, 1080, 330), fill=WHITE + (255,))
    f.alpha_composite(b, (0, 0))


def caption(f, text):
    tx = T(text, 92, WHITE, stroke=12, stroke_fill=GREEN)
    G.blit(f, tx, (540, 1150), 1, "mt")


def S1():
    f = Image.new("RGBA", (1080, 1920), (12, 14, 24, 255))
    coins = Image.open(SRC / "f_coins.png").convert("RGBA")
    w, h = coins.size
    crop = coins.crop((int(w * 0.15), int(h * 0.155), int(w * 0.85), int(h * 0.95))).resize((1080, 696))
    f.alpha_composite(crop, (0, 410))
    banner(f, "월배당 받는 동안", "원금은 -5%?")
    tag = paper(420, 110)
    tag.alpha_composite(T("커버드콜 합계 1,262만", 40, RED), (24, 30))
    G.blit(f, tag, (540, 1300), 1, "mt")
    caption(f, "분배금까지 다 쌓아도,")
    return f


def S2():
    f = bg("f_money.png", 1920, 1080, 0.4).crop((420, 0, 1500, 1080)).resize((1080, 1080))
    full = Image.new("RGBA", (1080, 1920), (12, 14, 24, 255))
    full.alpha_composite(f, (0, 330))
    banner(full, "같은 월배당인데", "세금 107만 vs 22만")
    rc = paper(900, 360)
    d = ImageDraw.Draw(rc)
    rc.alpha_composite(T("분배금 영수증 · 1,000만 원", 36, GREEN, "Bold"), (40, 30))
    for i, (lab, v, c) in enumerate((("TIGER 배당CC 세금", "-107만", RED), ("KODEX 200타겟위클리 세금", "-22만", GREEN))):
        y = 110 + i * 110
        rc.alpha_composite(T(lab, 40, INK, "Bold"), (40, y))
        vt = T(v, 56, c)
        rc.alpha_composite(vt, (860 - vt.width, y - 8))
        d.line((40, y + 80, 860, y + 80), fill=(200, 200, 196, 255), width=2)
    offset_card(full, rc, (80, 420))
    caption(full, "세금이 22만 원 대 107만 원.")
    return full


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    longs = [L1_punch(), L2_card(), L4_3d(), L3_full()]
    shorts = [S1(), S2()]
    for i, im in enumerate(longs):
        im.convert("RGB").save(OUT / f"long_{i + 1}.png")
    for i, im in enumerate(shorts):
        im.convert("RGB").save(OUT / f"short_{i + 1}.png")
    sheet = Image.new("RGB", (960 * 2 + 30 + 2 * 290 + 40, 540 * 2 + 30), (20, 20, 24))
    for i, im in enumerate(longs):
        sheet.paste(im.convert("RGB").resize((960, 540)), ((i % 2) * 970, (i // 2) * 560))
    for i, im in enumerate(shorts):
        sheet.paste(im.convert("RGB").resize((300, 533)), (1950 + i * 310, 0))
    sheet.save(OUT / "시안.jpg", quality=90)
    print("→", OUT)


if __name__ == "__main__":
    main()
