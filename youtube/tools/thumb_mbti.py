"""지식창고 롱폼 'MBTI는 가짜일 수 있다' 썸네일 10종 — 아이보리 종이 · 큰 명조 · 4글자 카드 · 실제 사진/논문 카드 폴라로이드
  python tools/thumb_mbti.py → out/sci04_mbti/thumbs10/T01~T10 + 비교표
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import editorial as E  # noqa: E402
import thumb_seoul as TS  # noqa: E402
from thumb_subway import title, sticker  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out/sci04_mbti/thumbs10"
W, H = 1920, 1080
INK, RED, BLUE = (34, 36, 48), (196, 36, 40), (30, 62, 178)
TYPES = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]


def letters(word, size=300, cols=None, strike=None, tilt=0):
    """4글자 카드 (각 글자 타일) · strike: 줄 그을 글자 인덱스"""
    tw = int(size * 0.92)
    im = Image.new("RGBA", (len(word) * (tw + 20), int(size * 1.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ch in enumerate(word):
        x = i * (tw + 20)
        c = (cols or {}).get(i, (255, 255, 255))
        d.rounded_rectangle((x, 0, x + tw, im.height - 1), 28, fill=c + (255,), outline=(210, 200, 182, 255), width=5)
        t = TS.text(ch, "NanumMyeongjo-ExtraBold.ttf", size, INK if sum(c) > 400 else (255, 255, 255))
        im.alpha_composite(t, (x + (tw - t.width) // 2, (im.height - t.height) // 2))
        if strike and i in strike:
            d.line((x + 20, im.height - 40, x + tw - 20, 40), fill=RED + (255,), width=22)
    return im.rotate(tilt, expand=True, resample=Image.BICUBIC)


def make(sp):
    f = E.paper_bg((247, 241, 228)).convert("RGBA").resize((W, H))
    v = sp["v"]
    if v == "letters":
        L = letters(sp["word"], sp.get("ls", 260), sp.get("cols"), sp.get("strike"), sp.get("tilt", -3))
        f.alpha_composite(L, (W - L.width - 60, sp.get("ly", 560)))
        if sp.get("kicker"):
            f.alpha_composite(TS.text(sp["kicker"], "NanumPenScript-Regular.ttf", 96, RED), (70, 60))
        title(f, sp["title"], (60, 170), sp.get("size", 180))
    elif v == "photo":
        p = TS.polaroid(sp["photo"], sp.get("pw", 760), sp.get("ph", 520), sp["cap"], sp.get("tilt", -4))
        f.alpha_composite(p, (W - p.width - 30, sp.get("py", 220)))
        if sp.get("kicker"):
            f.alpha_composite(TS.text(sp["kicker"], "NanumPenScript-Regular.ttf", 92, RED), (70, 70))
        y = title(f, sp["title"], (60, 180), sp.get("size", 160))
        if sp.get("big"):
            f.alpha_composite(TS.text(sp["big"], "NanumMyeongjo-ExtraBold.ttf", 260, BLUE, stroke=8), (60, y))
    elif v == "grid":
        cw = 200
        x0 = (W - 8 * cw - 7 * 16) // 2
        d = ImageDraw.Draw(f)
        for i, tname in enumerate(TYPES):
            x, y = x0 + (i % 8) * (cw + 16), 480 + (i // 8) * 130
            hl = tname in sp.get("hl", [])
            d.rounded_rectangle((x, y, x + cw, y + 110), 18, fill=(RED if hl else (255, 255, 255)) + (255,), outline=(210, 200, 182, 255), width=3)
            t = TS.text(tname, "NanumMyeongjo-ExtraBold.ttf", 58, (255, 255, 255) if hl else INK)
            f.alpha_composite(t, (x + (cw - t.width) // 2, y + 18))
        title(f, sp["title"], (60, 60), sp.get("size", 160))
    elif v == "bubble":
        L = letters(sp["word"], 220, sp.get("cols"), sp.get("strike"), 4)
        f.alpha_composite(L, (W - L.width - 70, 300))
        b = TS.text(sp["bubble"], "NanumMyeongjo-ExtraBold.ttf", 110, INK)
        card = Image.new("RGBA", (b.width + 100, b.height + 140), (0, 0, 0, 0))
        dd = ImageDraw.Draw(card)
        dd.rounded_rectangle((0, 0, card.width - 1, card.height - 60), 50, fill=(255, 255, 255, 255), outline=(210, 200, 182, 255), width=4)
        dd.polygon([(120, card.height - 62), (220, card.height - 62), (90, card.height - 2)], fill=(255, 255, 255, 255))
        card.alpha_composite(b, (50, 40))
        f.alpha_composite(card, (60, 60))
        title(f, sp["title"], (60, 640), sp.get("size", 150))
    s = sticker(190)
    f.alpha_composite(s, sp.get("sxy", (40, H - s.height - 30)))
    tag = TS.text("악어새 지식창고, 한 번에 정리", "NanumPenScript-Regular.ttf", 46, (120, 110, 92))
    f.alpha_composite(tag, (W - tag.width - 40, 20))
    return f.convert("RGB")


SPECS = [
    {"name": "T01", "v": "letters", "word": "ENFP", "strike": [0], "kicker": "할 때마다 바뀐다?", "title": "당신의 MBTI\n가짜일 수 있다", "size": 170},
    {"name": "T02", "v": "letters", "word": "E→I", "cols": {0: (214, 70, 46), 2: (30, 62, 178)}, "kicker": "어제는 E, 오늘은 I", "title": "MBTI 할 때마다\n바뀌는 이유", "size": 160},
    {"name": "T03", "v": "photo", "photo": "mb_mother_daughter", "cap": "MBTI를 만든 엄마와 딸", "kicker": "심리학 학위 0명", "title": "MBTI 만든 사람은\n심리학자가\n아니었다", "size": 140, "ph": 560, "pw": 560, "py": 260},
    {"name": "T04", "v": "photo", "photo": "mb_paper_pittenger", "cap": "피텐저 (2005) 논문", "kicker": "학술지가 밝힌", "title": "5주 뒤 다시 하면\n절반이 바뀐다", "size": 150, "pw": 620, "ph": 420, "py": 420},
    {"name": "T05", "v": "grid", "hl": ["ENFP", "INFP"], "title": "당신의 4글자\n진짜일까?", "size": 150, "sxy": (1690, 40)},
    {"name": "T06", "v": "photo", "photo": "mb_paper_forer", "cap": "포러 (1949) 실험", "kicker": "모두 같은 결과지였는데", "title": "내 얘기 같다\n5점 만점에", "big": "4.26", "size": 140},
    {"name": "T07", "v": "bubble", "bubble": "어제는 ENFP였는데…", "word": "INFP", "cols": {0: (30, 62, 178)}, "title": "MBTI가 바뀌는\n진짜 이유 3가지", "size": 140, "sxy": (1690, 840)},
    {"name": "T08", "v": "photo", "photo": "mb_phone_friends", "cap": "우리가 하는 그 검사", "kicker": "몰랐죠?", "title": "무료 검사는\n공식 MBTI가\n아니다", "size": 150},
    {"name": "T09", "v": "letters", "word": "????", "kicker": "세 번 해 보면 보인다", "title": "진짜 내 MBTI\n찾는 법", "size": 180},
    {"name": "T10", "v": "photo", "photo": "mb_barnum", "cap": "P. T. 바넘", "kicker": "MBTI 결과지의 비밀", "title": "누구에게나\n맞는 말", "size": 170, "pw": 560, "ph": 640},
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
