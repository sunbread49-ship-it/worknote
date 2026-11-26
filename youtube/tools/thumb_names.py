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


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ims = []
    for k, fn in enumerate((t01, t02, t03, t04), 1):
        im = fn().convert("RGB")
        im.save(OUT / f"T0{k}.png")
        ims.append(im.resize((960, 540)))
    sheet = Image.new("RGB", (1920, 1080), "black")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sheet.save(OUT / "비교표.jpg", quality=88)
    print("→", OUT)
