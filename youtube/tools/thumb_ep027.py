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


# ── 11/28 추가 시안 (THUMB_PATTERNS: 결말형 S2 · S3 · S4 + P03 화살표 · P05 결과 감추기 · P08 같은 날 대결) ──
import thumb_retitle as RT  # noqa: E402
JF = ROOT / "out/ep027_cisco_dotcom/hf/05_journey/frames"


def journey_bg(cover=False, dark=0.45):
    fr = sorted(JF.glob("*.jpg"))[-1]
    im = Image.open(fr).convert("RGB").resize((W, H))
    from PIL import ImageEnhance
    im = ImageEnhance.Brightness(im).enhance(1 - dark).convert("RGBA")
    if cover:   # 끝부분(2010년 이후)을 '?' 패널로 가림
        d = ImageDraw.Draw(im)
        d.rectangle((760, 0, W, H), fill=(14, 18, 34, 255))
        d.line((760, 0, 760, H), fill=YEL + (255,), width=10)
        q = TH.T("?", 520, YEL)
        im.alpha_composite(q, (760 + (W - 760 - q.width) // 2, 120))
    return im


def make_c():   # S2 컬러 사진 + 빨간 띠
    return RT.make_s2({"photo": "cisco_hq", "l1": "한때 세계 1위 시스코", "l2": "원금까지 25년", "hl": "25년",
                       "bubble": "엔비디아도 이렇게 될까?"})


def make_d():   # S3 왼쪽 검은 패널 · 오른쪽 엔비디아 본사
    return RT.make_s3({"photo": "nvidia_hq", "l1": "엔비디아 -37%", "l2": "26년 전 답", "hl": "-37%",
                       "bubble": "지금 사도 돼요?"})


def make_e():   # S4 남색 + 노랑 상자
    return RT.make_s4({"photo": "cisco_hq", "l1": "AI 거품 꺼지면?", "l2": "원금까지 25년", "hl": "25년",
                       "bubble": "2000년에 답이 있다"})


def make_f():   # P03 화살표: 전 → 후
    f = journey_bg(dark=0.82)
    TH.shadowed(f, TH.T("2000년 시스코 꼭대기", 90, WHITE), (W // 2, 120), "mt")
    a = TH.T("1,000만", 210, (170, 170, 170)); b = TH.T("107만", 250, RED)
    arr = TH.T("→", 200, YEL)
    tot = a.width + arr.width + b.width + 80
    x = (W - tot) // 2
    TH.shadowed(f, a, (x, 380)); TH.shadowed(f, arr, (x + a.width + 40, 390)); TH.shadowed(f, b, (x + a.width + arr.width + 80, 360))
    TH.shadowed(f, TH.T("원금까지 25년", 150, YEL, hl="25년", hl_color=RED), (W // 2, 760), "mt")
    TH.shadowed(f, plaque("logo_cisco", 300, 120), (W - 360, 40))
    return f


def make_g():   # P05 결과 감추기: 차트 끝이 '?'
    f = journey_bg(cover=True, dark=0.3)
    ImageDraw.Draw(f).rectangle((0, 0, 755, 240), fill=(14, 18, 34, 255))   # 장면 머리글 · 계기판 가림
    ImageDraw.Draw(f).rectangle((0, 240, 755, 560), fill=(14, 18, 34, 120))
    TH.shadowed(f, plaque("logo_cisco", 300, 120), (60, 60))
    TH.shadowed(f, TH.T("AI 거품 꼭대기에\n1,000만 원 넣었더니", 110, WHITE, hl="꼭대기", hl_color=YEL), (60, 560))
    f.alpha_composite(RT.badge(), (60, 220))
    return f


def make_h():   # P08 같은 날 대결 · 승자는 숨김
    f = Image.new("RGBA", (W, H), (10, 12, 20, 255))
    L = TH.photo_fill("cisco_hq", W // 2, H, dark=0.6, gray=1.0); R = TH.photo_fill("amazon_fc", W // 2, H, dark=0.6, gray=1.0)
    f.paste(L, (0, 0)); f.paste(R, (W // 2, 0))
    TH.shadowed(f, plaque("logo_cisco", 480, 190), (W // 4, 230), "mt")
    TH.shadowed(f, plaque("logo_amazon", 480, 190), (W * 3 // 4, 230), "mt")
    vs = TH.T("VS", 150, YEL); TH.shadowed(f, vs, (W // 2, 250), "mt")
    TH.shadowed(f, TH.T("2000.3.27 같은 날 1,000만 원", 96, WHITE), (W // 2, 60), "mt")
    TH.shadowed(f, TH.T("26년 뒤 결말은?", 190, YEL, hl="결말", hl_color=RED), (W // 2, 640), "mt")
    return f


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_a().convert("RGB").save(OUT / "thumbnail.png")
    make_b().convert("RGB").save(OUT / "thumb_B.png")
    for k, fn in (("C", make_c), ("D", make_d), ("E", make_e), ("F", make_f), ("G", make_g), ("H", make_h)):
        im = fn(); (im if im.mode == "RGB" else im.convert("RGB")).save(OUT / f"thumb_{k}.png")
    # 비교표 (휴대폰 크기 1초 테스트)
    names = ["thumbnail.png"] + [f"thumb_{k}.png" for k in "BCDEFGH"]
    tw, th_ = 480, 270
    sh = Image.new("RGB", (tw * 4 + 50, (th_ + 50) * 2 + 10), (245, 245, 245))
    d = ImageDraw.Draw(sh)
    for i, n in enumerate(names):
        x, y = 10 + (i % 4) * (tw + 10), 10 + (i // 4) * (th_ + 50)
        sh.paste(Image.open(OUT / n).convert("RGB").resize((tw, th_)), (x, y))
        lab = TH.T("ABCDEFGH"[i], 34, (20, 20, 20), stroke=0); sh.paste(lab, (x, y + th_ + 4), lab)
    sh.save(OUT / "thumbs_compare.jpg", quality=88)
    print("썸네일 8종 →", OUT / "thumbs_compare.jpg")
