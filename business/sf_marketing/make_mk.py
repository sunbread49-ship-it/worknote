"""쇼츠 팩토리 마케팅 샘플 슬라이드 3종
1) 릴스/쇼츠 홍보 영상 스토리보드 (1080x1920 · 7장)
2) 인스타 게시물 캐러셀 (1080x1350 · 6장)
3) 가입자용 사용설명서 영상 슬라이드 (1920x1080 · 9장)
재료: 실제 서비스 화면 캡처(d_*.png) · 템플릿 시안 · 우리 지폐 롱폼으로 만든 쇼츠
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = Path(__file__).resolve().parent
SF = next((p for p in (Path("/home/user/Shorts-Factory"), Path("/home/user/shorts-factory")) if p.exists()), Path("/home/user/Shorts-Factory"))
FD = SF / "server/fonts"
TPL = Path(__file__).resolve().parent / "mock"   # 2026-11-23 사용자: 우리 채널 샘플 말고 요즘 장르(드라마 · 아이돌 · 예능)
OUT = D / ("out_video" if __import__("os").environ.get("MK_VIDEO") else "out")
OUT.mkdir(exist_ok=True)

BG = (6, 8, 14)
CY = (34, 229, 255)
PK = (255, 61, 129)
YL = (255, 212, 0)
WH = (255, 255, 255)
DIM = (160, 172, 198)
PANEL = (16, 22, 36)


def F(size, w="Black"):
    if w == "Han":
        return ImageFont.truetype(str(FD / "BlackHanSans-Regular.ttf"), size)
    return ImageFont.truetype(str(FD / f"Pretendard-{w}.otf"), size)


def canvas(w, h, glow=True):
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, w, 48):
        d.line((x, 0, x, h), fill=(13, 18, 30))
    for y in range(0, h, 48):
        d.line((0, y, w, y), fill=(13, 18, 30))
    if glow:
        g = Image.new("RGB", (w, h), (0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse((-w * 0.3, -h * 0.25, w * 0.7, h * 0.35), fill=(0, 70, 90))
        gd.ellipse((w * 0.45, h * 0.6, w * 1.4, h * 1.3), fill=(80, 10, 50))
        g = g.filter(ImageFilter.GaussianBlur(min(w, h) // 5))
        im = Image.blend(im, Image.eval(g, lambda v: v), 0.0)
        im = Image.fromarray(__import__("numpy").clip(__import__("numpy").asarray(im, "int16") + __import__("numpy").asarray(g, "int16"), 0, 255).astype("uint8"))
    return im


def rich(d, x, y, text, f, base=WH, hl=CY, anchor="l", stroke=0):
    """[강조] 표시 부분은 hl 색. anchor: l / m(가운데)"""
    parts, cur, on = [], "", False
    for ch in text:
        if ch == "[":
            parts.append((cur, on)); cur, on = "", True
        elif ch == "]":
            parts.append((cur, on)); cur, on = "", False
        else:
            cur += ch
    parts.append((cur, on))
    wsum = sum(f.getlength(t) for t, _ in parts)
    if anchor == "m":
        x -= wsum / 2
    for t, h in parts:
        col = (hl if isinstance(hl, tuple) else hl) if h else base
        d.text((x, y), t, font=f, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += f.getlength(t)
    return wsum


def lines(d, x, y, txt, f, lh=1.25, **kw):
    for ln in txt.split("\n"):
        rich(d, x, y, ln, f, **kw)
        y += f.size * lh
    return y


def shot(im, src, box, radius=28, border=None, shadow=True, crop=None, fit="width"):
    """스크린샷 붙이기 (둥근 모서리 · 그림자 · 테두리)"""
    s = Image.open(src).convert("RGB")
    if crop:
        s = s.crop(crop)
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    if fit == "width":
        s = s.resize((bw, int(s.height * bw / s.width)), Image.LANCZOS)
        if s.height > bh:
            s = s.crop((0, 0, bw, bh))
    elif fit == "height":
        s = s.resize((int(s.width * bh / s.height), bh), Image.LANCZOS)
        if s.width > bw:
            off = (s.width - bw) // 2
            s = s.crop((off, 0, off + bw, bh))
    else:   # cover
        r = max(bw / s.width, bh / s.height)
        s = s.resize((int(s.width * r) + 1, int(s.height * r) + 1), Image.LANCZOS)
        ox, oy = (s.width - bw) // 2, (s.height - bh) // 2
        s = s.crop((ox, oy, ox + bw, oy + bh))
    w, h = s.size
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((x0 + 6, y0 + 18, x0 + w + 6, y0 + h + 18), radius, fill=(0, 0, 0, 160))
        im.paste(Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(22))).convert("RGB"))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    im.paste(s, (x0, y0), m)
    if border:
        ImageDraw.Draw(im).rounded_rectangle((x0 - 3, y0 - 3, x0 + w + 2, y0 + h + 2), radius + 3, outline=border, width=5)
    return (x0, y0, x0 + w, y0 + h)


def phone(im, src, cx, top, w, crop=None):
    """휴대폰 틀 안에 9:16 화면"""
    h = int(w * 16 / 9)
    d = ImageDraw.Draw(im)
    pad = int(w * 0.05)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((cx - w // 2 - pad + 10, top - pad + 30, cx + w // 2 + pad + 10, top + h + pad + 30), int(w * 0.14), fill=(0, 0, 0, 170))
    im.paste(Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(30))).convert("RGB"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((cx - w // 2 - pad, top - pad, cx + w // 2 + pad, top + h + pad), int(w * 0.14), fill=(0, 0, 0), outline=(40, 52, 78), width=4)
    shot(im, src, (cx - w // 2, top, cx + w // 2, top + h), radius=int(w * 0.09), shadow=False, crop=crop, fit="cover")


def chip(d, x, y, txt, f, bg=WH, fg=(10, 13, 22), padx=26, pady=12, anchor="l"):
    w = f.getlength(txt)
    if anchor == "m":
        x -= (w + padx * 2) / 2
    d.rounded_rectangle((x, y, x + w + padx * 2, y + f.size + pady * 2), (f.size + pady * 2) // 2, fill=bg)
    d.text((x + padx, y + pady - f.size * 0.08), txt, font=f, fill=fg)
    return x + w + padx * 2


def badge(d, x, y, n, r=34, col=PK):
    d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=WH, width=4)
    f = F(int(r * 1.15))
    d.text((x - f.getlength(str(n)) / 2, y - r * 0.68), str(n), font=f, fill=WH)


def logo(im, x, y, s=1.0):
    d = ImageDraw.Draw(im)
    sz = int(84 * s)
    g = Image.new("RGB", (sz, sz))
    gd = ImageDraw.Draw(g)
    for i in range(sz):
        t = i / sz
        gd.line((0, i, sz, i), fill=(int(34 + (255 - 34) * t), int(229 + (61 - 229) * t), int(255 + (129 - 255) * t)))
    m = Image.new("L", (sz, sz), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sz - 1, sz - 1), int(sz * 0.26), fill=255)
    im.paste(g, (x, y), m)
    bw = sz * 0.14
    for i, hh in enumerate((0.55, 0.7, 0.55)):
        bx = x + sz * (0.24 + i * 0.2)
        d.rounded_rectangle((bx, y + sz * (1 - hh) / 2, bx + bw, y + sz * (1 + hh) / 2), int(bw / 2), fill=(10, 12, 20))
    d.text((x + sz + 22 * s, y + 4 * s), "쇼츠 팩토리", font=F(int(46 * s)), fill=WH)
    d.text((x + sz + 24 * s, y + 58 * s), "SHORTS FACTORY", font=F(int(20 * s), "Bold"), fill=CY)


def tag(d, x, y, txt, f=None):
    f = f or F(30, "Bold")
    d.text((x, y), txt, font=f, fill=CY)


def foot_note(d, w, h, txt):
    f = F(26, "Bold")
    d.text((w - 40 - f.getlength(txt), h - 60), txt, font=f, fill=(90, 100, 124))


SHOTS = {k: str(D / f"d_{k}.png") for k in ("home", "working", "results", "editor", "phone", "consent", "voice", "count", "tpl", "tpled", "boxmove")}

# ───────────────────────── 1) 릴스 / 쇼츠 홍보 영상 (1080x1920) ─────────────────────────
REEL = []   # (파일, 시간, 화면 자막/내레이션)


def reel(n, t, say, draw):
    im = canvas(1080, 1920)
    draw(im, ImageDraw.Draw(im))
    d = ImageDraw.Draw(im)
    if not __import__("os").environ.get("MK_VIDEO"):   # 영상용(make_video.py)은 장면 표시 없이
        chip(d, 40, 40, f"SCENE {n:02d} · {t}", F(28, "Bold"), bg=(20, 28, 46), fg=CY, padx=18, pady=8)
    p = OUT / f"reel_{n:02d}.jpg"
    im.save(p, quality=90)
    REEL.append((p, t, say))


def r1(im, d):
    lines(d, 540, 330, "아직도 쇼츠\n[직접] 자르세요?", F(150, "Han"), lh=1.2, anchor="m", hl=PK)
    rich(d, 540, 760, "롱폼 1편 → 구간 찾기 → 자르기 → 자막", F(46, "Bold"), base=DIM, anchor="m")
    rich(d, 540, 830, "한 편에 [몇 시간]씩", F(56), base=WH, hl=YL, anchor="m")
    # 지친 타임라인 그림
    y0 = 1040
    for i in range(6):
        x = 120 + i * 140
        d.rounded_rectangle((x, y0 + (i % 2) * 40, x + 110, y0 + 520 - (i % 3) * 60), 16, fill=(24, 32, 52), outline=(50, 64, 96), width=3)
        d.line((x + 20, y0 + 230, x + 90, y0 + 230), fill=PK, width=5)
        d.text((x + 26, y0 + 160), "컷", font=F(54), fill=(90, 100, 124))
    d.line((80, 1700, 1000, 1700), fill=PK, width=6)
    rich(d, 540, 1740, "편집 시간 3:00:00", F(64), base=PK, anchor="m")


def r2(im, d):
    lines(d, 540, 250, "[링크/파일] 하나\n넣으면 끝", F(130, "Han"), anchor="m", hl=CY)
    shot(im, SHOTS["home"], (60, 720, 1020, 720 + int(960 * 400 / 1680)), crop=(600, 760, 2280, 1160), border=CY)
    rich(d, 540, 1300, "링크 붙여넣기 · 파일 끌어다 놓기 모두 OK", F(46, "Bold"), base=DIM, anchor="m")
    d.polygon([(860, 960), (860, 1070), (890, 1042), (912, 1090), (930, 1082), (908, 1034), (948, 1032)], fill=WH, outline=(0, 0, 0))
    chip(d, 540, 1420, "최대 30분 영상", F(44, "Bold"), anchor="m")
    chip(d, 540, 1520, "쇼츠 1~5개 골라서", F(44, "Bold"), bg=CY, anchor="m")


def r3(im, d):
    lines(d, 540, 250, "AI가 [재밌는 구간]만\n골라 잘라요", F(112, "Han"), anchor="m", hl=YL)
    shot(im, SHOTS["working"], (40, 640, 1040, 1250), crop=(400, 180, 2480, 1449), border=PK)
    for i, t in enumerate(["받아쓰기 · 원본 자막 읽기", "30~60초 · 기승전결", "훅 점수 높은 순"]):
        y = 1360 + i * 100
        d.ellipse((140, y + 4, 196, y + 60), fill=CY)
        d.line((154, y + 32, 166, y + 46, 184, y + 18), fill=BG, width=7)
        rich(d, 220, y, t, F(52, "Bold"), base=WH)


def r4(im, d):
    lines(d, 540, 230, "자막, 헤드 문구\n[자동으로] 쾅", F(120, "Han"), anchor="m", hl=CY)
    for i, (src, ang) in enumerate([(TPL / "tpl3.jpg", 0), (TPL / "tpl1.jpg", 0), (TPL / "tpl4.jpg", 0)]):
        pass
    phone(im, str(TPL / "tpl1.jpg"), 250, 760, 330, crop=(0, 0, 1080, 1920))
    phone(im, str(TPL / "tpl4.jpg"), 830, 760, 330, crop=(0, 0, 1080, 1920))
    phone(im, str(TPL / "tpl3.jpg"), 540, 690, 380, crop=(0, 0, 1080, 1920))
    rich(d, 540, 1450 + 230, "숫자 · 핵심어는 [노란색] 강조", F(52, "Bold"), base=WH, hl=YL, anchor="m")


def r5(im, d):
    lines(d, 540, 220, "템플릿 [5종]\n목소리 [10종]", F(130, "Han"), anchor="m", hl=PK)
    for i in range(5):
        x = 50 + i * 200
        shot(im, str(TPL / f"tpl{i + 1}.jpg"), (x, 600, x + 180, 900), crop=(0, 0, 1080, 1800), radius=14, fit="cover", border=CY if i == 2 else None)
    d = ImageDraw.Draw(im)
    shot(im, SHOTS["voice"], (90, 980, 990, 1560), crop=(0, 0, 1564, 560), border=CY)
    rich(d, 540, 1640, "배속 0.5~2배 · [내 스타일 고정]", F(52, "Bold"), base=WH, hl=YL, anchor="m")


def r6(im, d):
    lines(d, 540, 220, "수정은\n[손가락으로 쓱]", F(130, "Han"), anchor="m", hl=CY)
    phone(im, SHOTS["phone"], 540, 640, 470, crop=(24, 24, 656, 1142))
    # 위아래 화살표
    for y, s in ((1060, -1), (1360, 1)):
        d.polygon([(900, y), (960, y + 70 * s), (840, y + 70 * s)], fill=YL)
    rich(d, 540, 1560 + 140, "자막 박스 위아래 · 문구 · 구간 자르기", F(46, "Bold"), base=DIM, anchor="m")


def r7(im, d):
    s = 2.1   # 로고 크게 (11/23 사용자)
    lw = int(84 * s) + 22 * s + F(int(46 * s)).getlength("쇼츠 팩토리")
    logo(im, int(540 - lw / 2), 250, s)
    lines(d, 540, 600, "롱폼 1편 =\n[쇼츠 1~5개]", F(140, "Han"), anchor="m", hl=CY)
    d.rounded_rectangle((90, 1020, 990, 1420), 40, fill=(16, 22, 36), outline=YL, width=6)
    rich(d, 540, 1070, "쇼츠 월 [25편]", F(120, "Han"), base=WH, hl=YL, anchor="m")
    rich(d, 540, 1235, "[9,900원]", F(120, "Han"), base=WH, hl=PK, anchor="m")
    rich(d, 540, 1450, "* 업그레이드 요금제 별도", F(40, "Bold"), base=DIM, anchor="m")
    chip(d, 540, 1600, "프로필 링크에서 시작하기 →", F(56), bg=PK, fg=WH, anchor="m", padx=44, pady=22)


SAY = [
    (r1, "0~2초", "아직도 쇼츠, 직접 자르세요? 롱폼 한 편에 몇 시간씩."),
    (r2, "2~5초", "이제 풀영상 링크나 파일 하나만 넣으면 끝."),
    (r3, "5~8초", "AI가 재밌는 구간만 골라서 30~60초로 잘라 줘요."),
    (r4, "8~11초", "자막이랑 헤드 문구까지 자동으로."),
    (r5, "11~14초", "템플릿 5종, 목소리 10종. 내 스타일로 고정까지."),
    (r6, "14~17초", "고칠 건 손가락으로 쓱."),
    (r7, "17~20초", "롱폼 한 편으로 쇼츠 최대 다섯 개. 한 달 쇼츠 25편이 9,900원. 쇼츠 팩토리, 프로필 링크에서."),
]
for i, (fn, t, say) in enumerate(SAY, 1):
    reel(i, t, say, fn)

# ───────────────────────── 2) 인스타 캐러셀 (1080x1350) ─────────────────────────
CARDS = []


def card(n, draw):
    im = canvas(1080, 1350)
    draw(im, ImageDraw.Draw(im))
    d = ImageDraw.Draw(im)
    d.text((1080 - 150, 1350 - 70), f"{n} / 6", font=F(30, "Bold"), fill=(90, 100, 124))
    if n < 6:
        d.text((1080 - 80, 1350 - 72), "→", font=F(34), fill=CY)
    p = OUT / f"card_{n}.jpg"
    im.save(p, quality=92)
    CARDS.append(p)


def c1(im, d):
    chip(d, 70, 90, "유튜버 저장 필수", F(36, "Bold"), bg=YL)
    lines(d, 70, 200, "롱폼 1편이\n[쇼츠 1~5개]로\n찍혀 나오는 곳", F(118, "Han"), lh=1.18, hl=CY)
    phone(im, str(TPL / "tpl3.jpg"), 330, 830, 230)
    phone(im, str(TPL / "tpl1.jpg"), 600, 760, 250)
    phone(im, str(TPL / "tpl5.jpg"), 870, 830, 230)
    logo(im, 70, 1230, 0.75)


def c2(im, d):
    lines(d, 70, 110, "쇼츠 만들 때\n제일 귀찮은 [3가지]", F(96, "Han"), hl=PK)
    items = [("01", "재밌는 구간 찾기", "롱폼 처음부터 끝까지 다시 보기"), ("02", "한 줄 자막 달기", "한 글자씩 받아 적고 타이밍 맞추기"),
             ("03", "세로 화면 맞추기", "9:16으로 자르고 제목 띠 얹기")]
    y = 470
    for no, t, s in items:
        d.rounded_rectangle((70, y, 1010, y + 220), 30, fill=PANEL, outline=(40, 52, 78), width=3)
        d.text((110, y + 50), no, font=F(80, "Han"), fill=PK)
        d.text((260, y + 48), t, font=F(56), fill=WH)
        d.text((262, y + 128), s, font=F(36, "Bold"), fill=DIM)
        d.line((920, y + 80, 980, y + 140), fill=PK, width=12)
        d.line((980, y + 80, 920, y + 140), fill=PK, width=12)
        y += 250


def c3(im, d):
    lines(d, 70, 100, "쇼츠 팩토리는\n[3단계]로 끝", F(100, "Han"), hl=CY)
    steps = [("1", "풀영상 링크 / 파일 넣기", SHOTS["home"], (600, 760, 2280, 1160)), ("2", "개수 · 템플릿 고르기", SHOTS["count"], None),
             ("3", "편집 · mp4 다운로드", SHOTS["results"], (240, 600, 1720, 1100))]
    y = 420
    for no, t, src, cr in steps:
        badge(d, 120, y + 50, no, 40, PK)
        d.text((190, y + 18), t, font=F(56), fill=WH)
        shot(im, src, (190, y + 100, 1010, y + 250), crop=cr, radius=18, fit="cover" if cr else "width")
        d = ImageDraw.Draw(im)
        y += 300


def c4(im, d):
    lines(d, 70, 100, "템플릿 [5종] 중에\n골라 쓰세요", F(96, "Han"), hl=YL)
    names = ["심플 화이트", "네온 다크", "빅 블랙", "빅 풀스크린", "아이보리 노트"]
    xs = [70, 400, 730]
    for i in range(5):
        r, c = divmod(i, 3)
        x = (xs[c] if r == 0 else xs[c] + 165)
        y = 380 + r * 470
        shot(im, str(TPL / f"tpl{i + 1}.jpg"), (x, y, x + 280, y + 380), crop=(0, 0, 1080, 1470), radius=20, fit="cover", border=CY if i == 2 else None)
        d = ImageDraw.Draw(im)
        f = F(34, "Bold")
        d.text((x + 140 - f.getlength(names[i]) / 2, y + 392), names[i], font=f, fill=WH)


def c5(im, d):
    lines(d, 70, 100, "디테일이\n[다릅니다]", F(110, "Han"), hl=CY)
    feats = [("원본 자막 그대로 읽기", "화면에 자막이 있으면 AI가 읽어서 오타 없이"), ("숫자 · 핵심어 노란 강조", "1,400개 · 20% 같은 숫자는 자동으로 눈에 띄게"),
             ("목소리 10종 · 0.5~2배속", "발음이 이상하면 '읽는 법'만 고치면 기억해요"), ("★ 내 스타일 고정", "템플릿 · 글꼴 · 목소리 저장 → 다음부터 자동")]
    y = 420
    for t, s in feats:
        d.ellipse((70, y + 12, 118, y + 60), fill=CY)
        d.line((82, y + 38, 92, y + 48, 108, y + 24), fill=BG, width=6)
        d.text((150, y), t, font=F(54), fill=WH)
        d.text((152, y + 76), s, font=F(34, "Bold"), fill=DIM)
        y += 205


def c6(im, d):
    lines(d, 70, 100, "한 달 쇼츠 [25편]\n[9,900원]부터", F(96, "Han"), hl=YL)
    plans = [("베이직", "9,900", "25"), ("플러스", "15,900", "50"), ("프로", "22,900", "75")]
    for i, (n, p, c) in enumerate(plans):
        x = 70 + i * 320
        hot = i == 1
        d.rounded_rectangle((x, 400, x + 290, 860), 30, fill=(255, 255, 255) if hot else PANEL, outline=CY if hot else (40, 52, 78), width=4)
        fg = (10, 13, 22) if hot else WH
        d.text((x + 30, 430), n, font=F(46), fill=fg)
        d.text((x + 30, 510), p, font=F(70, "Han"), fill=PK if hot else YL)
        d.text((x + 30, 600), "원 / 월", font=F(32, "Bold"), fill=DIM if not hot else (80, 90, 110))
        d.text((x + 30, 680), f"쇼츠 {c}편", font=F(50), fill=fg)
        if hot:
            chip(d, x + 145, 375, "인기", F(28, "Bold"), bg=PK, fg=WH, anchor="m", padx=18, pady=6)
    chip(d, 540, 1040, "프로필 링크에서 시작하기 →", F(54), bg=PK, fg=WH, anchor="m", padx=44, pady=22)
    logo(im, 70, 1230, 0.75)


for i, fn in enumerate([c1, c2, c3, c4, c5, c6], 1):
    card(i, fn)

# ───────────────────────── 3) 사용설명서 영상 (1920x1080) ─────────────────────────
GUIDE = []


def guide(n, title, say, draw):
    im = canvas(1920, 1080)
    d = ImageDraw.Draw(im)
    if n > 1:
        chip(d, 70, 54, f"STEP {n - 1:02d}" if n < 9 else "TIP", F(30, "Bold"), bg=PK, fg=WH, padx=20, pady=8)
        d.text((240, 44), title, font=F(56), fill=WH)
        # 진행 막대
        for k in range(1, 8):
            d.rounded_rectangle((1380 + (k - 1) * 66, 70, 1380 + (k - 1) * 66 + 54, 80), 5, fill=CY if k <= n - 1 else (40, 52, 78))
    draw(im, ImageDraw.Draw(im))
    p = OUT / f"guide_{n:02d}.jpg"
    im.save(p, quality=90)
    GUIDE.append((p, title, say))


def callout(im, box, n, label, side="r"):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 14, outline=YL, width=6)
    x = box[2] + 44 if side == "r" else box[0] - 44
    y = (box[1] + box[3]) // 2
    badge(d, x, y, n, 32, PK)
    f = F(38)
    if side == "r":
        d.text((x + 48, y - 26), label, font=f, fill=WH, stroke_width=4, stroke_fill=BG)
    else:
        d.text((x - 48 - f.getlength(label), y - 26), label, font=f, fill=WH, stroke_width=4, stroke_fill=BG)


def scale_box(b, src_box, dst):
    """캡처 좌표(b) → 화면에 붙인 위치"""
    sx0, sy0, sx1, sy1 = src_box
    dx0, dy0, dx1, dy1 = dst
    k = (dx1 - dx0) / (sx1 - sx0)
    return (dx0 + (b[0] - sx0) * k, dy0 + (b[1] - sy0) * k, dx0 + (b[2] - sx0) * k, dy0 + (b[3] - sy0) * k)


def g1(im, d):
    logo(im, 640, 250, 1.5)
    lines(d, 960, 450, "사용 설명서", F(150, "Han"), anchor="m")
    rich(d, 960, 660, "풀영상 [링크/파일] 하나로 쇼츠 만들기", F(54, "Bold"), base=DIM, hl=CY, anchor="m")
    f = F(30, "Bold")
    ts = ["링크 / 파일", "개수 · 템플릿", "확인", "제작", "다운로드", "편집", "목소리 · 스타일"]
    tot = sum(f.getlength(t) + 36 for t in ts) + 24 * (len(ts) - 1)
    x = 960 - tot / 2
    for t in ts:
        x = chip(d, x, 820, t, f, bg=PANEL, fg=WH, padx=18) + 24


def g2(im, d):
    src = (500, 160, 2380, 1260)
    dst = shot(im, SHOTS["home"], (150, 170, 1250, 170 + int(1100 * 1100 / 1880)), crop=src, border=None)
    callout(im, scale_box((620, 780, 2260, 940), src, dst), 1, "", "r")
    callout(im, scale_box((620, 960, 2260, 1128), src, dst), 2, "", "r")
    d = ImageDraw.Draw(im)
    y = 260
    for t in ["1. 풀영상 링크 붙여넣고 생성", "2. 또는 파일을 끌어다 놓고 생성", "   (눌러서 골라도 돼요)", "30분 이하 영상까지"]:
        d.text((1360, y), t, font=F(38 if not t.startswith(" ") else 32, "Bold"), fill=DIM if t.startswith(" ") else WH)
        y += 70 if t.startswith("2") else 90
    chip(d, 1360, 640, "링크 · 파일 둘 다 OK", F(36, "Bold"), bg=YL)


def g3(im, d):
    shot(im, SHOTS["count"], (180, 230, 1110, 330), crop=(560, 0, 1810, 130), fit="cover", border=CY)
    for i in range(5):
        x = 180 + i * 188
        shot(im, str(TPL / f"tpl{i + 1}.jpg"), (x, 450, x + 168, 750), crop=(0, 0, 1080, 1920), radius=12, fit="cover", border=CY if i == 2 else None)
    d = ImageDraw.Draw(im)
    badge(d, 110, 290, 1, 32)
    badge(d, 110, 600, 2, 32)
    y = 260
    for t in ["1. 만들 쇼츠 개수 1~5개", "   고른 개수만큼 크레딧이 바로 빠져요", "2. 템플릿 5종 중 하나", "   전체에 적용 · 나중에 바꿔도 돼요"]:
        d.text((1200, y), t, font=F(40 if t[0].isdigit() else 32, "Bold"), fill=WH if t[0].isdigit() else DIM)
        y += 80 if t.startswith(" ") else 64
    chip(d, 1200, 680, "★ 내 스타일이 있으면 자동 선택", F(32, "Bold"), bg=YL)
    chip(d, 1200, 790, "! 같은 영상은 개수를 한 번에", F(32, "Bold"), bg=PK, fg=WH)
    for k, t in enumerate(["따로 1개씩 여러 번 만들면", "같은 구간이 또 나올 수 있어요"]):
        d.text((1210, 880 + k * 46), t, font=F(32, "Bold"), fill=DIM)


def g4(im, d):
    shot(im, SHOTS["consent"], (180, 170, 180 + 760, 170 + int(760 * 1040 / 1120)), border=PK)
    d = ImageDraw.Draw(im)
    y = 250
    for t in ["체크 3개를 모두 해야 생성돼요", "• 권리가 있는 영상만 (내가 만들었거나 허락받은 것)", "• 권리 없는 영상은 본인 책임", "• 올릴 때 원본 출처 표시",
              "동의 내용과 시각은 기록돼요"]:
        big = not t.startswith("•")
        d.text((1040, y), t, font=F(42 if big else 34, "Bold"), fill=YL if big else WH)
        y += 90 if big else 70


def g5(im, d):
    src = (360, 200, 2520, 1420)   # 2026-11-23 사용자: 가운데 · 오와 열 맞게 (콘텐츠 중앙 기준으로 자름)
    shot(im, SHOTS["working"], (120, 170, 1120, 170 + int(1000 * 1220 / 2160)), crop=src)
    d = ImageDraw.Draw(im)
    y = 260
    for t in ["받기 → 받아쓰기 → 구간 분석 → 제작", "원본 자막이 있으면 화면 글자를 읽어요", "영상 길이에 따라 몇 분 걸려요", "창을 닫아도 계속 만들어져요"]:
        d.text((1190, y), "•", font=F(44), fill=CY)
        d.text((1230, y + 4), t, font=F(34, "Bold"), fill=WH)
        y += 100


def g6(im, d):
    src = (220, 480, 1720, 1760)
    dst = shot(im, SHOTS["results"], (150, 160, 1110, 160 + int(960 * 1160 / 1500)), crop=src)
    callout(im, scale_box((262, 1318, 690, 1550), src, dst), 1, "", "l")
    d = ImageDraw.Draw(im)
    y = 240
    for k, t in enumerate(["카드마다 제목 · 설명 추천이 붙어요", "훅 점수(HOOK)가 높을수록 반응 좋을 구간", "'다운로드'로 mp4 바로 받기", "'편집'으로 고치고 싶은 것만 수정"]):
        if k == 0:
            badge(d, 1212, y + 28, 1, 24, PK)   # 화면의 ① 상자와 짝
        else:
            d.text((1200, y), "•", font=F(44), fill=CY)
        d.text((1240, y + 4), t, font=F(36, "Bold"), fill=WH)
        y += 100


def g7(im, d):
    src = (0, 260, 2880, 1800)
    dst = shot(im, SHOTS["editor"], (120, 150, 1300, 150 + int(1180 * 1540 / 2880)), crop=src)
    for n, b, lab in [(1, (1940, 380, 2620, 620), ""), (2, (1940, 680, 2620, 1060), ""), (3, (1940, 1140, 2620, 1660), ""), (4, (240, 360, 940, 1520), "")]:
        callout(im, scale_box(b, src, dst), n, lab, "l" if n == 4 else "r")
    d = ImageDraw.Draw(im)
    y = 220
    for t in ["1. 헤드 문구 고치기", "2. 앞뒤 자르기 · 가운데 빼기", "3. 자막 박스 위아래 · 크기", "4. 미리보기 자막 끌어 옮기기", "다 되면 '저장하고 다운로드'"]:
        d.text((1400, y), t, font=F(38, "Bold"), fill=YL if t.startswith("다") else WH)
        y += 90


def g8(im, d):
    shot(im, SHOTS["voice"], (150, 170, 1050, 170 + int(900 * 1148 / 1564)), border=CY)
    d = ImageDraw.Draw(im)
    y = 220
    for t in ["목소리 10종 · ▶로 미리듣기", "배속 0.5~2배 (0.1 단위)", "문장마다 ▶ 듣기 · ↻ 다시 읽기 3번", "발음이 이상하면 '읽는 법'에 소리 나는 대로",
              "→ 한 번 고치면 다음부터 자동", "★ 내 스타일로 고정 → 다음 영상도 그대로"]:
        d.text((1130, y), t, font=F(36, "Bold"), fill=YL if t.startswith(("→", "★")) else WH)
        y += 92


def g9(im, d):
    qa = [("크레딧은 어떻게 빠지나요?", "쇼츠 1개 = 크레딧 1. 고른 개수만큼 바로 빠져요 (돌려드리지 않아요)."),
          ("같은 영상으로 또 만들면?", "1개씩 따로 만들면 같은 구간이 또 나올 수 있어요. 처음에 개수를 한 번에!"),
          ("요금제를 올리면?", "차이만큼 바로 채워져요 (베이직 → 플러스 +25)."), ("어떤 영상이 되나요?", "30분 이하 · 내가 만들었거나 허락받은 영상.")]
    y = 230
    for q, a in qa:
        d.rounded_rectangle((260, y, 1660, y + 150), 26, fill=PANEL, outline=(40, 52, 78), width=3)
        d.text((300, y + 24), "Q. " + q, font=F(42), fill=CY)
        d.text((300, y + 86), a, font=F(34, "Bold"), fill=WH)
        y += 175


GS = [
    (g1, "", "쇼츠 팩토리 사용법을 알려 드릴게요. 풀영상 링크나 파일 하나로 쇼츠를 만들어 봐요."),
    (g2, "풀영상 링크 / 파일", "먼저 풀영상 링크를 붙여넣고 생성을 누르거나, 아래 칸에 영상 파일을 끌어다 놓고 생성을 눌러요. 30분 이하 영상까지 가능해요."),
    (g3, "개수 · 템플릿 고르기", "만들 쇼츠 개수를 1개부터 5개까지 고르고, 템플릿을 골라요. 고른 개수만큼 크레딧이 바로 빠져요. 같은 영상으로 1개씩 따로 만들면 같은 구간이 또 나올 수 있으니, 필요한 개수를 한 번에 고르세요."),
    (g4, "저작권 확인", "생성 전에 체크 세 개를 해 주세요. 권리가 있는 영상만 올리고, 올릴 때 원본 출처를 꼭 표시해요."),
    (g5, "제작 기다리기", "이제 공장이 돌아가요. AI가 받아쓰고, 재밌는 구간을 골라 쇼츠를 만들어요."),
    (g6, "결과 확인 · 다운로드", "쇼츠가 나오면 카드마다 제목과 설명이 추천돼요. 다운로드를 누르면 바로 받을 수 있어요."),
    (g7, "편집하기", "고치고 싶으면 편집을 눌러요. 헤드 문구, 자르기, 자막 박스 위치까지 바꿀 수 있어요."),
    (g8, "목소리 · 내 스타일", "AI 목소리를 넣고 싶으면 목소리와 배속을 고르세요. 마음에 들면 내 스타일로 고정해 두세요."),
    (g9, "자주 묻는 질문", "크레딧은 쇼츠 한 개에 하나. 고르는 순간 빠지니까, 같은 영상은 필요한 개수를 한 번에 고르세요. 그럼 첫 쇼츠 만들어 볼까요?"),
]
for i, (fn, t, say) in enumerate(GS, 1):
    guide(i, t, say, fn)


# ───────────────────────── 한눈에 보는 시트 ─────────────────────────
def sheet(items, tw, th, cols, path, labels):
    gap, top = 30, 20
    rows = (len(items) + cols - 1) // cols
    lab_h = 120
    S = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * (th + lab_h) + (rows + 1) * gap), (24, 26, 32))
    d = ImageDraw.Draw(S)
    for i, p in enumerate(items):
        r, c = divmod(i, cols)
        x, y = gap + c * (tw + gap), gap + r * (th + lab_h + gap)
        S.paste(Image.open(p).resize((tw, th), Image.LANCZOS), (x, y))
        if labels:
            t = labels[i]
            f = F(22, "Bold")
            words, ln, yy = t, "", y + th + 10
            for ch in words:
                if f.getlength(ln + ch) > tw:
                    d.text((x, yy), ln, font=f, fill=(220, 225, 235)); yy += 28; ln = ""
                ln += ch
            d.text((x, yy), ln, font=f, fill=(220, 225, 235))
    S.save(path, quality=90)


sheet([p for p, _, _ in REEL], 300, 533, 7, OUT / "sheet_1_reel.jpg", [f"{t} · {s}" for _, t, s in REEL])
sheet(CARDS, 420, 525, 6, OUT / "sheet_2_insta.jpg", None)
sheet([p for p, _, _ in GUIDE], 576, 324, 3, OUT / "sheet_3_guide.jpg", [f"{(t or '표지')} · {s}" for _, t, s in GUIDE])
print("ok")
