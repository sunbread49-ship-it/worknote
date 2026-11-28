"""EP029 배당주 5종 비교 썸네일 시안 6종 — '실제로 까봤더니 반전' (사용자 11/28)
  python3 tools/thumb_ep029.py → out/ep029_dividend_compare/thumb_A~F.png · thumbs_compare.jpg
숫자 근거(공통 기간 2024.12.3 → 2026.11.27 · 배당 재투자): JEPQ 주가 -5.5% · 최근 1년 배당 12.9% · 총수익 +17% / 코카콜라 배당 2.2% · 총수익 +61%
          KODEX 200타겟위클리커버드콜 2026년 고점 대비 -49% (코스피 반토막)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402
import thumb_retitle as RT  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/ep029_dividend_compare"
W, H = TH.W, TH.H
YEL, RED, WHITE, GREEN, DARK = (255, 214, 40), (255, 60, 60), (255, 255, 255), (70, 230, 150), (12, 16, 30)
LOGOS = [("logo_schwab", "SCHD"), ("logo_jpmorgan", "JEPQ"), ("logo_kodex", "커버드콜"), ("logo_realty", "리츠"), ("logo_coke", "코카콜라")]


def plaque(name, w, h, pad=22, label=None, gray=False):
    src = next(p for p in (ROOT / "assets/photos").glob(name + ".*") if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    lg = Image.open(src).convert("RGBA")
    if gray:
        lg = lg.convert("LA").convert("RGBA")
    k = min((w - 2 * pad) / lg.width, (h - 2 * pad - (36 if label else 0)) / lg.height)
    lg = lg.resize((max(1, int(lg.width * k)), max(1, int(lg.height * k))), Image.LANCZOS)
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, w - 1, h - 1), 24, fill=(255, 255, 255, 255))
    p.alpha_composite(lg, ((w - lg.width) // 2, (h - lg.height - (36 if label else 0)) // 2))
    if label:
        t = TH.T(label, 30, (30, 30, 30), stroke=0)
        p.alpha_composite(t, ((w - t.width) // 2, h - t.height - 12))
    return p


def bg(glow=(255, 60, 60)):
    f = Image.new("RGBA", (W, H), DARK + (255,))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((W * 0.15, H * 0.1, W * 0.85, H * 1.1), fill=glow + (70,))
    f.alpha_composite(g.filter(ImageFilter.GaussianBlur(160)))
    return f


def sticker(text, color=YEL, rot=6, size=70, fg=(20, 20, 20)):
    t = TH.T(text, size, fg, stroke=0)
    b = Image.new("RGBA", (t.width + 50, t.height + 26), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle((0, 0, b.width - 1, b.height - 1), 20, fill=color + (255,))
    b.alpha_composite(t, (25, 13))
    return b.rotate(rot, expand=True, resample=Image.BICUBIC)


def make_a():   # 5개 로고 + '까봤더니 1등이…?'
    f = bg((255, 170, 40))
    pw, gap = 300, 40
    x0 = (W - (5 * pw + 4 * gap)) // 2
    for i, (n, lab) in enumerate(LOGOS):
        TH.shadowed(f, plaque(n, pw, 190, label=lab), (x0 + i * (pw + gap), 90))
    TH.shadowed(f, TH.T("배당주 5개, 1,000만 원씩 넣고", 96, WHITE), (W // 2, 360), "mt")
    TH.shadowed(f, TH.T("까봤더니 1등이…", 210, YEL, hl="1등이…", hl_color=RED), (W // 2, 540), "mt")
    f.alpha_composite(sticker("반전 주의", RED, -8, 64, WHITE), (W - 420, 820))
    return f


def make_b():   # 화살표 반전: 월배당 12% → 원금 -5%
    f = bg((255, 60, 60))
    TH.shadowed(f, plaque("logo_jpmorgan", 380, 170, label="JEPQ"), (90, 80))
    TH.shadowed(f, TH.T("서학개미 1위 월배당", 80, WHITE), (520, 130))
    a, arr, b = TH.T("배당 12%", 165, GREEN), TH.T("→", 150, WHITE), TH.T("원금 -5%", 165, RED)
    x = (W - (a.width + arr.width + b.width + 80)) // 2
    TH.shadowed(f, a, (x, 400)); TH.shadowed(f, arr, (x + a.width + 40, 410)); TH.shadowed(f, b, (x + a.width + arr.width + 80, 400))
    TH.shadowed(f, TH.T("까봤더니 벌어진 일", 150, YEL), (W // 2, 720), "mt")
    return f


def make_c():   # '배당 2등이 수익 꼴찌' · 누군지는 숨김
    f = bg((120, 80, 255))
    pw, gap = 270, 36
    x0 = (W - (5 * pw + 4 * gap)) // 2
    for i, (n, lab) in enumerate(LOGOS):
        p = plaque(n, pw, 170, label=lab, gray=True)
        if lab == "JEPQ":   # 정답은 가림
            p = Image.new("RGBA", (pw, 170), (0, 0, 0, 0))
            ImageDraw.Draw(p).rounded_rectangle((0, 0, pw - 1, 169), 24, fill=(40, 46, 70, 255), outline=YEL + (255,), width=6)
            q = TH.T("?", 130, YEL); p.alpha_composite(q, ((pw - q.width) // 2, (170 - q.height) // 2))
        TH.shadowed(f, p, (x0 + i * (pw + gap), 80))
    TH.shadowed(f, TH.T("배당 2등이", 170, WHITE), (W // 2, 330), "mt")
    TH.shadowed(f, TH.T("수익 꼴찌?!", 250, RED), (W // 2, 560), "mt")
    return f


def make_d():   # 월배당의 배신 -49%
    f = bg((255, 40, 40))
    TH.shadowed(f, plaque("logo_kodex", 420, 170, label="국내 커버드콜 시총 1위"), (90, 80))
    TH.shadowed(f, TH.T("월배당의 배신", 150, WHITE, hl="배신", hl_color=YEL), (90, 300))
    TH.shadowed(f, TH.T("하락장에 까봤더니", 90, YEL), (90, 500))
    big = TH.T("-49%", 380, RED)
    bx = W - big.width - 60
    TH.shadowed(f, big, (bx, 600))
    d = ImageDraw.Draw(f)   # 금 간 선 (숫자 위 오른쪽)
    d.line([(bx + big.width * 0.55, 610), (bx + big.width * 0.62, 760), (bx + big.width * 0.5, 860), (bx + big.width * 0.6, 1000)], fill=(255, 255, 255, 220), width=9)
    return f


def make_e():   # 결말형 S2 · 만 원권 실사
    return RT.make_s2({"photo": "krw_10000", "l1": "배당 많이 주는 순서", "l2": "= 수익 순서?", "hl": "수익",
                       "bubble": "직접 까봤습니다", "badge": None})


def make_f():   # 배당 12% vs 배당 2% · 2년 뒤 웃은 쪽은? (승자 숨김)
    f = Image.new("RGBA", (W, H), DARK + (255,))
    ImageDraw.Draw(f).rectangle((0, 0, W // 2, H), fill=(20, 60, 40, 255))
    ImageDraw.Draw(f).rectangle((W // 2, 0, W, H), fill=(70, 18, 24, 255))
    TH.shadowed(f, plaque("logo_jpmorgan", 400, 170, label="JEPQ"), (W // 4, 70), "mt")
    TH.shadowed(f, plaque("logo_coke", 400, 170, label="코카콜라"), (W * 3 // 4, 70), "mt")
    TH.shadowed(f, TH.T("배당 12%", 170, GREEN), (W // 4, 290), "mt")
    TH.shadowed(f, TH.T("배당 2%", 170, WHITE), (W * 3 // 4, 290), "mt")
    vs = TH.T("VS", 140, YEL); TH.shadowed(f, vs, (W // 2, 300), "mt")
    TH.shadowed(f, TH.T("2년 뒤 웃은 쪽은?", 180, YEL, hl="웃은", hl_color=RED), (W // 2, 640), "mt")
    return f


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fns = dict(A=make_a, B=make_b, C=make_c, D=make_d, E=make_e, F=make_f)
    for k, fn in fns.items():
        im = fn(); (im if im.mode == "RGB" else im.convert("RGB")).save(OUT / f"thumb_{k}.png")
    tw, th_ = 560, 315
    sh = Image.new("RGB", (tw * 3 + 40, (th_ + 50) * 2 + 10), (245, 245, 245))
    for i, k in enumerate(fns):
        x, y = 10 + (i % 3) * (tw + 10), 10 + (i // 3) * (th_ + 50)
        sh.paste(Image.open(OUT / f"thumb_{k}.png").convert("RGB").resize((tw, th_)), (x, y))
        lab = TH.T(k, 34, (20, 20, 20), stroke=0); sh.paste(lab, (x, y + th_ + 4), lab)
    sh.save(OUT / "thumbs_compare.jpg", quality=88)
    print("썸네일 6종 →", OUT / "thumbs_compare.jpg")
