"""지식창고 롱폼 '지폐 속 숨은 그림' 썸네일 10종 — 아이보리 종이 · 한국은행 공식 지폐 이미지 · 돋보기 줌 · 실제 그림 폴라로이드
  python tools/thumb_banknote.py → out/sci03_banknotes/thumbs10/T01~T10 + 비교표
  화폐도안 이용기준: 진폐 오인 X(기울임·종이 위 연출) · 인물 분리/변형 X (초상만 따로 자르지 않음)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import editorial as E  # noqa: E402
import thumb_seoul as TS  # noqa: E402
from thumb_subway import title, sticker  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out/sci03_banknotes/thumbs10"
PH = Path(__file__).resolve().parents[1] / "assets/photos"
W, H = 1920, 1080
INK, RED = (34, 36, 48), (196, 36, 40)


def note(name, w, tilt=0):
    src = Image.open(PH / f"{name}.jpg").convert("RGB")
    im = src.resize((w, int(src.height * w / src.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 80, 2)).convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 14, fill=255); im.putalpha(m)
    im = im.rotate(tilt, expand=True, resample=Image.BICUBIC)
    return E._shadowed(im, 18, 0.35, (12, 20))


def lens(name, box, d=560, ring=RED):
    src = Image.open(PH / f"{name}.jpg").convert("RGB")
    bw, bh = (box[2] - box[0]) * src.width, (box[3] - box[1]) * src.height
    cx, cy = (box[0] + box[2]) / 2 * src.width, (box[1] + box[3]) / 2 * src.height
    hs = max(bw, bh) / 2
    c = src.crop((int(cx - hs), int(cy - hs), int(cx + hs), int(cy + hs))).resize((d, d), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 90, 2)).convert("RGBA")
    mk = Image.new("L", (d, d), 0); ImageDraw.Draw(mk).ellipse((0, 0, d - 1, d - 1), fill=255); c.putalpha(mk)
    r = Image.new("RGBA", (d + 30, d + 30), (0, 0, 0, 0))
    ImageDraw.Draw(r).ellipse((0, 0, d + 29, d + 29), fill=(255, 255, 255, 255))
    r.alpha_composite(c, (15, 15))
    ImageDraw.Draw(r).ellipse((4, 4, d + 25, d + 25), outline=ring + (255,), width=12)
    return E._shadowed(r, 18, 0.35, (10, 18))


def crop_card(name, box, w, h, rot=0, tag=None, tilt=0):
    src = Image.open(PH / f"{name}.jpg").convert("RGB")
    c = E._crop01(src, box).rotate(rot, expand=True)
    c = E._fit(c, w, h).filter(ImageFilter.UnsharpMask(2, 90, 2))
    card = Image.new("RGBA", (w + 30, h + 30), (255, 255, 255, 255)); card.paste(c, (15, 15))
    if tag:
        t = E.G.pill(tag, "Black", 44, (255, 255, 255), RED, pad=(26, 10)); card.alpha_composite(t, (24, 24))
    return E._shadowed(card.rotate(tilt, expand=True, resample=Image.BICUBIC), 18, 0.35, (10, 18))


def make(sp):
    f = E.paper_bg((247, 241, 228)).convert("RGBA").resize((W, H))
    v = sp["v"]
    if v == "note":   # 지폐 크게 + 제목
        n = note(sp["note"], sp.get("w", 1120), sp.get("tilt", -6))
        f.alpha_composite(n, (W - n.width + 40, sp.get("ny", 300)))
        if sp.get("lens"):
            L = lens(sp["note"], sp["lens"], sp.get("d", 460))
            f.alpha_composite(L, sp.get("lxy", (W - L.width - 10, 20)))
        if sp.get("kicker"):
            f.alpha_composite(TS.text(sp["kicker"], "NanumPenScript-Regular.ttf", 92, RED), (70, 70))
        y = title(f, sp["title"], (60, 180), sp.get("size", 170))
        if sp.get("sub"):
            f.alpha_composite(TS.text(sp["sub"], "NanumPenScript-Regular.ttf", 84, INK), (80, y + 10))
    elif v == "pair":
        for i, (nm, tl, xy) in enumerate(sp["notes"]):
            f.alpha_composite(note(nm, 900, tl), xy)
        title(f, sp["title"], (60, 40), sp.get("size", 160))
    elif v == "compare":
        a = crop_card(sp["note"], sp["box"], 700, 560, sp.get("rot", 0), "지폐 속", -4)
        f.alpha_composite(a, (40, 400))
        p = TS.polaroid(sp["real"], 640, 500, sp["cap"], 4)
        f.alpha_composite(p, (W - p.width - 30, 330))
        f.alpha_composite(TS.text("=", "NanumMyeongjo-ExtraBold.ttf", 200, RED), (820, 560))
        title(f, sp["title"], (60, 30), sp.get("size", 150))
    elif v == "big":
        t = TS.text(sp["big"], "NanumMyeongjo-ExtraBold.ttf", 330, (150, 150, 160))
        f.alpha_composite(t, (W - t.width - 80, 620))
        d = ImageDraw.Draw(f)
        d.line((W - t.width - 110, 900, W - 50, 700), fill=RED + (255,), width=26)
        f.alpha_composite(TS.text("발행 중지", "NanumPenScript-Regular.ttf", 120, RED), (W - 560, 380))
        y = title(f, sp["title"], (60, 80), sp.get("size", 180))
    elif v == "collage":
        for (ph, cap, tl, xy) in sp["photos"]:
            f.alpha_composite(TS.polaroid(ph, 400, 300, cap, tl), xy)
        title(f, sp["title"], (60, 600), sp.get("size", 150))
    elif v == "sizes":
        for i, nm in enumerate(["bok2_1000_f", "bok2_5000_f", "bok2_10000_f", "bok2_50000_f"]):
            mm = [136, 142, 148, 154][i]
            n = note(nm, int(mm * 6.4))
            f.alpha_composite(n, (720, 110 + i * 160))
        title(f, sp["title"], (60, 200), sp.get("size", 160))
    s = sticker(sp.get("sticker", 190))
    f.alpha_composite(s, sp.get("sxy", (40, H - s.height - 30)))
    tag = TS.text("악어새 지식창고, 한 번에 정리", "NanumPenScript-Regular.ttf", 46, (120, 110, 92))
    if not sp.get("lens"):
        f.alpha_composite(tag, (W - tag.width - 40, 20))
    return f.convert("RGB")


SPECS = [
    {"name": "T01", "v": "note", "note": "bok2_10000_b", "kicker": "매일 쓰는데 몰랐던", "title": "만 원 뒷면,\n보셨나요?", "sub": "600년 전 하늘이 숨어 있다"},
    {"name": "T02", "v": "note", "note": "bok2_10000_b", "lens": [0.13, 0.2, 0.46, 1.0], "kicker": "만 원 속", "title": "600년 전\n하늘", "size": 200, "lxy": (1300, 30), "ny": 470, "w": 1000},
    {"name": "T03", "v": "pair", "notes": [("bok2_5000_f", -5, (80, 430)), ("bok2_50000_f", 5, (960, 520))], "title": "지갑 속\n엄마와 아들", "size": 170, "sxy": (1690, 40)},
    {"name": "T04", "v": "compare", "note": "bok2_5000_b", "box": [0.14, 0.4, 0.48, 1.0], "real": "bn_cc_watermelon", "cap": "신사임당 「초충도」", "title": "오천 원 뒷면은\n엄마의 그림", "sxy": (1690, 40)},
    {"name": "T05", "v": "big", "big": "100,000", "title": "끝내\n못 나온\n10만 원", "size": 190},
    {"name": "T06", "v": "note", "note": "bok2_1000_b", "lens": [0.43, 0.38, 0.66, 0.72], "kicker": "천 원 뒷면", "title": "이 그림\n어디일까?", "size": 190, "lxy": (1300, 30), "ny": 470, "w": 1000},
    {"name": "T07", "v": "collage", "title": "지폐 속 숨은 그림\n한 번에 정리", "photos": [("bn_cheonsang", "천상열차분야지도", -5, (40, 30)), ("bn_cc_watermelon", "초충도", 4, (500, 60)), ("bn_wolmae", "월매도", -3, (960, 30)), ("bn_myeongnyun", "명륜당", 5, (1420, 70))], "sxy": (1690, 840)},
    {"name": "T08", "v": "sizes", "title": "지폐\n키 재기", "sub": "", "size": 190},
    {"name": "T09", "v": "compare", "note": "bok2_50000_b", "box": [0.08, 0.12, 0.5, 0.96], "rot": 90, "real": "bn_wolmae", "cap": "어몽룡 「월매도」", "title": "오만 원 뒷면은\n세워서 보세요", "sxy": (1690, 40)},
    {"name": "T10", "v": "note", "note": "bok_10000_1973_f", "kicker": "1973년 첫 만 원", "title": "부처님이\n들어갈 뻔", "size": 190, "sub": "만 원의 원래 도안"},
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    outs = []
    for sp in SPECS:
        im = make(sp).resize((1280, 720), Image.LANCZOS)
        p = OUT / f"{sp['name']}.png"
        im.save(p)
        outs.append((sp["name"], p))
    sheet = Image.new("RGB", (2 * 650 + 10, 5 * 400 + 10), (20, 20, 24))
    for i, (nm, p) in enumerate(outs):
        x, y = 10 + (i % 2) * 650, 10 + (i // 2) * 400
        sheet.paste(Image.open(p).resize((640, 360)), (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + 364), nm, fill=(180, 255, 60))
    sheet.save(OUT / "비교표.jpg", quality=90)
    print("비교표 →", OUT / "비교표.jpg")
