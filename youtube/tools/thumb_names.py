"""sci06 '서울 동네 이름의 비밀' 썸네일 4종 — 종이 톤(지식창고 생활상식) · 영상 속 한자 카드 · 이름표 카드 그림 그대로
  python tools/thumb_names.py → out/sci06_seoul_names/thumbs/T01~T04 + 비교표.jpg
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import editorial as E  # noqa: E402
from engine.sciviz import icon, _hz, MJ, PEN  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out/sci06_seoul_names/thumbs"
W, H = 1920, 1080
INK, RED, ORG, SUB = (34, 36, 48), (200, 40, 40), (226, 92, 64), (120, 110, 94)


def base():
    f = E.paper_bg((247, 241, 228)).convert("RGBA").resize((W, H))
    G = E._ink("악어새 지식창고 · 생활상식", PEN, 46, SUB)
    f.alpha_composite(G, (W - G.width - 40, 26))
    return f


def shadow(f, im, xy, rot=0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.3)))
    f.alpha_composite(sh, (int(xy[0] + 12), int(xy[1] + 16)))
    f.alpha_composite(im, (int(xy[0]), int(xy[1])))


def hanja_card(h, ko, s=300):
    c = Image.new("RGBA", (s, int(s * 1.25)), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, s - 1, int(s * 1.25) - 1), 30, fill=ORG + (255,))
    hz = _hz(h, int(s * 0.62), (255, 255, 255))
    c.alpha_composite(hz, ((s - hz.width) // 2, int(s * 0.1)))
    k = E._ink(ko, MJ, int(s * 0.17), (255, 255, 255))
    c.alpha_composite(k, ((s - k.width) // 2, int(s * 0.95)))
    return c


def tag(name, h, mean, ic, s=360):
    c = Image.new("RGBA", (s, int(s * 1.3)), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, s - 1, int(s * 1.3) - 1), 24, fill=(255, 253, 246, 255), outline=INK + (255,), width=6)
    i = icon(ic, int(s * 0.5), INK, ORG, 0.3)
    c.alpha_composite(i, ((s - i.width) // 2, 20))
    n = E._ink(name, MJ, int(s * 0.21), INK)
    c.alpha_composite(n, ((s - n.width) // 2, int(s * 0.6)))
    m = E._ink(mean, PEN, int(s * 0.15), RED)
    c.alpha_composite(m, ((s - m.width) // 2, int(s * 0.92)))
    return c


def headline(f, rows, x, y):
    for s, size, col in rows:
        im = E._ink(s, MJ, size, col)
        f.alpha_composite(im, (x, y))
        y += int(size * 1.12)


def t01():   # 압구정 한자 3장 + 질문
    f = base()
    for i, (h, ko) in enumerate((("狎", "친할 압"), ("鷗", "갈매기 구"), ("亭", "정자 정"))):
        shadow(f, hanja_card(h, ko, 270), (980 + i * 300, 210 + (i % 2) * 40), rot=(-4, 3, -2)[i])
    headline(f, [("압구정의", 140, INK), ("'압'은", 190, RED), ("무슨 뜻?", 150, INK)], 90, 200)
    g = icon("gull", 300, INK, ORG, 0.4)
    f.alpha_composite(g, (1250, 700))
    return f


def t02():   # 이름표 4장 + 동네 이름 뜻
    f = base()
    cards = [("압구정", "", "갈매기 정자", "gull"), ("잠실", "", "누에 방", "silkworm"), ("여의도", "", "너나 가져라?", "island"), ("대치", "", "큰 고개", "hill")]
    for i, (n, h, m, ic) in enumerate(cards):
        shadow(f, tag(n, h, m, ic, 330), (90 + i * 440, 470 + (i % 2) * 30), rot=(-3, 2, -2, 3)[i])
    headline(f, [("서울 동네 이름, 뜻 알면 소름", 118, INK)], 90, 120)
    headline(f, [("압구정 · 잠실 · 여의도", 90, RED)], 90, 270)
    return f


def t03():   # 왕십리 퀴즈 카드
    f = base()
    headline(f, [("왕십리는", 150, INK), ("왜 왕십리?", 170, RED)], 90, 190)
    ch = ["왕이 살던 마을", "십 리를 더 가라", "열 개의 마을"]
    for i, c in enumerate(ch):
        card = Image.new("RGBA", (640, 170), (0, 0, 0, 0))
        ok = False   # 정답은 감춤(궁금증)
        ImageDraw.Draw(card).rounded_rectangle((0, 0, 639, 169), 26, fill=(ORG if ok else (255, 253, 246)) + (255,), outline=INK + (255,), width=0 if ok else 5)
        t = E._ink(f"{'①②③'[i]} {c}", MJ, 64, (255, 255, 255) if ok else INK)
        card.alpha_composite(t, (36, (170 - t.height) // 2))
        shadow(f, card, (1180, 230 + i * 220), rot=(2 if ok else 0))
    q = E._ink("3초 안에 맞혀 보세요", PEN, 80, SUB)
    f.alpha_composite(q, (100, 640))
    qm = E._ink("?", MJ, 260, ORG)
    f.alpha_composite(qm.rotate(12, expand=True, resample=Image.BICUBIC), (1700, 40))
    return f


def t04():   # 잠실 = 누에 방 + 한자 2장
    f = base()
    for i, (h, ko) in enumerate((("蠶", "누에 잠"), ("室", "집 실"))):
        shadow(f, hanja_card(h, ko, 320), (1060 + i * 380, 200 + i * 40), rot=(-4, 3)[i])
    headline(f, [("잠실의 '잠'은", 130, INK), ("누에였다", 190, RED)], 90, 220)
    s = icon("silkworm", 360, INK, ORG, 0.2)
    f.alpha_composite(s, (1200, 680))
    return f


# ── 11/26 사용자: 이름표 그림 퀄리티 ↑ (색감 · 귀엽게) — 4배 크게 그려 줄여서 매끈하게 ──
def _cute(kind, s):
    S4 = s * 4
    im = Image.new("RGBA", (S4, S4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    OL = (60, 52, 48, 255)
    w = S4 // 60
    if kind == "silkworm":
        # 뽕잎
        d.ellipse((S4 * .08, S4 * .45, S4 * .92, S4 * .95), fill=(126, 190, 96, 255), outline=(70, 130, 60, 255), width=w)
        d.line((S4 * .12, S4 * .72, S4 * .9, S4 * .68), fill=(90, 150, 70, 255), width=w)
        for k in range(4):
            x = S4 * (.25 + k * .17)
            d.line((x, S4 * .71, x + S4 * .08, S4 * .55), fill=(90, 150, 70, 255), width=w // 2 + 2)
            d.line((x, S4 * .71, x + S4 * .08, S4 * .86), fill=(90, 150, 70, 255), width=w // 2 + 2)
        # 누에 몸통(뒤→앞)
        for i in range(6):
            r = S4 * (.085 + .012 * i)
            cx = S4 * (.18 + .115 * i)
            cy = S4 * (.5 - .05 * __import__("math").sin(i * 1.1))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 248, 232, 255), outline=OL, width=w)
            d.arc((cx - r * .6, cy - r * .2, cx + r * .6, cy + r * .9), 200, 340, fill=(232, 210, 180, 255), width=w // 2 + 1)
        hx, hy, hr = S4 * .8, S4 * .36, S4 * .15
        d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(255, 250, 238, 255), outline=OL, width=w)
        for ex in (-.45, .35):
            d.ellipse((hx + hr * ex - S4 * .02, hy - S4 * .03, hx + hr * ex + S4 * .02, hy + S4 * .02), fill=OL)
        for ex in (-.62, .55):
            d.ellipse((hx + hr * ex - S4 * .03, hy + S4 * .03, hx + hr * ex + S4 * .03, hy + S4 * .06), fill=(255, 150, 150, 200))
        d.arc((hx - S4 * .04, hy + S4 * .01, hx + S4 * .03, hy + S4 * .06), 20, 160, fill=OL, width=w // 2 + 1)
    elif kind == "sign":
        # 갈림길 나무 표지판 + 점선 길
        for k in range(7):
            x = S4 * (.08 + k * .13)
            d.ellipse((x, S4 * .86, x + S4 * .07, S4 * .9), fill=(200, 170, 120, 255))
        d.rounded_rectangle((S4 * .45, S4 * .3, S4 * .53, S4 * .9), S4 // 50, fill=(150, 104, 66, 255), outline=OL, width=w)
        d.polygon([(S4 * .12, S4 * .16), (S4 * .78, S4 * .16), (S4 * .94, S4 * .3), (S4 * .78, S4 * .44), (S4 * .12, S4 * .44)],
                  fill=(222, 166, 98, 255), outline=OL)
        d.line([(S4 * .12, S4 * .16), (S4 * .78, S4 * .16), (S4 * .94, S4 * .3), (S4 * .78, S4 * .44), (S4 * .12, S4 * .44), (S4 * .12, S4 * .16)], fill=OL, width=w)
        t = _hz("十里", int(S4 * .2), (120, 40, 30))
        im.alpha_composite(t, (int(S4 * .2), int(S4 * .17)))
        a = E._ink("→", MJ, int(S4 * .18), (120, 40, 30))
        im.alpha_composite(a, (int(S4 * .64), int(S4 * .16)))
        # 작은 풀
        for x in (.2, .75):
            for k in (-1, 0, 1):
                d.line((S4 * x, S4 * .86, S4 * (x + .03 * k), S4 * .76), fill=(110, 170, 80, 255), width=w)
    elif kind == "island":
        for k in range(3):
            y = S4 * (.7 + k * .08)
            for x in range(0, S4, S4 // 5):
                d.arc((x, y - S4 * .04, x + S4 // 5, y + S4 * .04), 0, 180, fill=(90, 160, 220, 255), width=w)
        d.ellipse((S4 * .1, S4 * .55, S4 * .9, S4 * .82), fill=(240, 214, 150, 255), outline=OL, width=w)
        d.ellipse((S4 * .2, S4 * .58, S4 * .55, S4 * .66), fill=(250, 232, 186, 255))
        # 야자수
        d.line((S4 * .6, S4 * .62, S4 * .64, S4 * .28), fill=(140, 96, 60, 255), width=w * 2)
        for ang in (-150, -110, -60, -20):
            import math as _m
            x2 = S4 * .64 + S4 * .2 * _m.cos(_m.radians(ang)); y2 = S4 * .28 + S4 * .2 * _m.sin(_m.radians(ang)) + S4 * .08
            d.line((S4 * .64, S4 * .28, x2, y2), fill=(90, 170, 90, 255), width=w * 2)
        # 작은 깃발 '너'
        d.line((S4 * .3, S4 * .62, S4 * .3, S4 * .36), fill=OL, width=w)
        d.polygon([(S4 * .3, S4 * .36), (S4 * .46, S4 * .42), (S4 * .3, S4 * .48)], fill=(226, 92, 64, 255))
    return im.resize((s, s), Image.LANCZOS)


def mini(name, s=230, ic=None):
    c = Image.new("RGBA", (s, int(s * 0.95)), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, s - 1, c.height - 1), 20, fill=(255, 253, 246, 255), outline=INK + (255,), width=5)
    n = E._ink(name, MJ, int(s * 0.24), INK)
    c.alpha_composite(n, ((s - n.width) // 2, int(c.height * 0.14)))
    if ic:   # 11/26 사용자: '?' 대신 그림 힌트
        g = _cute(ic, int(c.height * 0.66))
        c.alpha_composite(g, ((s - g.width) // 2, int(c.height * 0.32)))
    else:
        q = E._ink("?", MJ, int(s * 0.26), ORG)
        c.alpha_composite(q, ((s - q.width) // 2, int(c.height * 0.5)))
    return c


def bubble(text, size=64, col=INK, fill=(255, 214, 120)):
    t = E._ink(text, MJ, size, col)
    w, h = t.width + 70, t.height + 44
    b = Image.new("RGBA", (w, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=fill + (255,), outline=INK + (255,), width=5)
    d.polygon([(w * 0.22, h - 4), (w * 0.3, h - 4), (w * 0.2, h + 36)], fill=fill + (255,), outline=INK + (255,))
    d.line((w * 0.22, h - 3, w * 0.3, h - 3), fill=fill + (255,), width=8)
    b.alpha_composite(t, (35, 20))
    return b


def t05():   # T01 + 다른 동네도(말풍선 + 미니 이름표 3장)
    f = base()
    for i, (h, ko) in enumerate((("狎", "친할 압"), ("鷗", "갈매기 구"), ("亭", "정자 정"))):
        shadow(f, hanja_card(h, ko, 250), (1000 + i * 280, 120 + (i % 2) * 34), rot=(-4, 3, -2)[i])
    headline(f, [("압구정의", 140, INK), ("'압'은", 190, RED), ("무슨 뜻?", 150, INK)], 90, 200)
    for i, (n, ic) in enumerate((("잠실", "silkworm"), ("왕십리", "sign"), ("여의도", "island"))):
        shadow(f, mini(n, 250, ic), (1000 + i * 290, 740 + (i % 2) * 16), rot=(3, -2, 2)[i])
    shadow(f, bubble("다른 동네들도 알고 보면 소름", 58), (980, 610))
    return f


def t06():   # T01 + 아래 띠 박스
    f = base()
    for i, (h, ko) in enumerate((("狎", "친할 압"), ("鷗", "갈매기 구"), ("亭", "정자 정"))):
        shadow(f, hanja_card(h, ko, 270), (980 + i * 300, 150 + (i % 2) * 40), rot=(-4, 3, -2)[i])
    headline(f, [("압구정의", 130, INK), ("'압'은", 175, RED), ("무슨 뜻?", 140, INK)], 90, 130)
    box = Image.new("RGBA", (1740, 190), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, 1739, 189), 30, fill=INK + (255,))
    t = E._ink("잠실 · 왕십리 · 여의도 · 대치", MJ, 74, (255, 255, 255))
    box.alpha_composite(t, (50, (190 - t.height) // 2))
    t2 = E._ink("알고 보면 소름", MJ, 74, (255, 214, 120))
    box.alpha_composite(t2, (1740 - t2.width - 50, (190 - t2.height) // 2))
    shadow(f, box, (90, 820))
    return f


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ims = []
    for k, fn in enumerate((t01, t02, t03, t04, t05, t06), 1):
        im = fn().convert("RGB")
        im.save(OUT / f"T0{k}.png")
        ims.append(im.resize((960, 540)))
    sheet = Image.new("RGB", (1920, 540 * ((len(ims) + 1) // 2)), "black")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sheet.save(OUT / "비교표.jpg", quality=88)
    print("→", OUT)
