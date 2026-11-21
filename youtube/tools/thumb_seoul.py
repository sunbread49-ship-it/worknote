"""지식창고 롱폼 '서울 25개 구' 썸네일 — 탐사 수첩 톤(종이 · 가족색 지도 · 명조 · 손글씨 · 도장 · 폴라로이드)
  python tools/thumb_seoul.py → out/sci01_seoul25/thumbs/T01~ + 비교표
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import editorial as E  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out/sci01_seoul25/thumbs"
W, H = 1920, 1080
INK = (34, 36, 48)
RED = (186, 30, 34)
FAM = {"원조": ((226, 160, 50), ["종로구", "중구", "용산구"]),
       "성동": ((232, 96, 76), ["성동구", "광진구", "강남구", "서초구", "송파구", "강동구"]),
       "동대문": ((70, 140, 220), ["동대문구", "성북구", "도봉구", "노원구", "강북구", "중랑구"]),
       "서대문": ((150, 110, 210), ["서대문구", "마포구", "은평구"]),
       "영등포": ((60, 170, 110), ["영등포구", "관악구", "동작구", "강서구", "양천구", "구로구", "금천구"])}


def seoul_map(box, only=None, hl=None, names=False):
    d0 = E._seoul()
    gs = [n for n in d0 if not n.startswith("_")]
    pts = [p for n in gs for poly in d0[n] for p in poly]
    lon0, lon1 = min(p[0] for p in pts), max(p[0] for p in pts)
    lat0, lat1 = min(p[1] for p in pts), max(p[1] for p in pts)
    kx = math.cos(math.radians(37.55))
    sc = min((box[2] - box[0]) / ((lon1 - lon0) * kx), (box[3] - box[1]) / (lat1 - lat0))
    ox = box[0] + ((box[2] - box[0]) - (lon1 - lon0) * kx * sc) / 2
    oy = box[1] + ((box[3] - box[1]) - (lat1 - lat0) * sc) / 2
    P = lambda lo, la: (ox + (lo - lon0) * kx * sc, oy + (lat1 - la) * sc)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for n in gs:
        col = next(c for c, l in FAM.values() if n in l)
        if only and n not in only:
            col = (226, 216, 196)
        for poly in d0[n]:
            d.polygon([P(*p) for p in poly], fill=col + (255,), outline=INK + (255,), width=4 if n != hl else 7)
    sh = im.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.4))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(Image.merge("RGBA", (Image.new("L", (W, H), 0),) * 3 + (sh,)), (10, 16))
    out.alpha_composite(im)
    if names:
        for n in gs:
            big = max(d0[n], key=len)
            xs = [P(*p) for p in big]
            cx, cy = sum(p[0] for p in xs) / len(xs), sum(p[1] for p in xs) / len(xs)
            t = E._ink(n, "NanumMyeongjo-ExtraBold.ttf", 30, (255, 255, 255), stroke=3, sfill=INK)
            out.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))
    return out


def polaroid(name, w, h, cap, tilt):
    im, _ = E.photo_backdrop({"file": name, "dark": 0.0, "gray": 0.0})
    im = im.convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    im = im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))
    pol = Image.new("RGBA", (w + 40, h + 110), (252, 250, 244, 255))
    pol.paste(im, (20, 20))
    c = E._ink(cap, "NanumPenScript-Regular.ttf", 52, INK)
    pol.alpha_composite(c, ((pol.width - c.width) // 2, h + 34))
    pol = pol.rotate(tilt, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", pol.size, (0, 0, 0, 0))
    sh.putalpha(pol.split()[3].filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.4)))
    out = Image.new("RGBA", (pol.width + 24, pol.height + 30), (0, 0, 0, 0))
    out.alpha_composite(sh, (14, 20))
    out.alpha_composite(pol)
    return out


def seal(top, big, bottom, R=150, tilt=12):
    stp = Image.new("RGBA", (R * 2 + 24, R * 2 + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(stp)
    d.ellipse((12, 12, R * 2 + 12, R * 2 + 12), outline=RED + (235,), width=12)
    d.ellipse((30, 30, R * 2 - 6, R * 2 - 6), outline=RED + (235,), width=4)
    for t, fs, yy in ((top, 34, R - 62), (big, 84, R), (bottom, 34, R + 64)):
        im = E._ink(t, "NanumMyeongjo-ExtraBold.ttf", fs, RED + (235,))
        stp.alpha_composite(im, ((stp.width - im.width) // 2, int(yy - im.height / 2 + 12)))
    return stp.rotate(tilt, expand=True, resample=Image.BICUBIC)


def text(t, font, size, col, stroke=0):
    return E._ink(t, font, size, col, stroke=stroke, sfill=(252, 250, 244))


def base():
    return E.paper_bg().convert("RGBA").resize((W, H))


def make(spec):
    f = base()
    v = spec["v"]
    if v == "map_big":   # 지도 크게 + 큰 명조 + 손글씨 질문 + 도장
        f.alpha_composite(seoul_map((760, 60, 1880, 1020), names=spec.get("names", False)))
        f.alpha_composite(text(spec["kicker"], "NanumPenScript-Regular.ttf", 96, RED), (70, 90))
        y = 200
        for i, ln in enumerate(spec["title"].split("\n")):
            im = text(ln, "NanumMyeongjo-ExtraBold.ttf", spec.get("size", 190), INK if i == 0 else RED, stroke=6)
            f.alpha_composite(im, (60, y))
            y += im.height - 10
        if spec.get("sub"):
            f.alpha_composite(text(spec["sub"], "NanumPenScript-Regular.ttf", 84, INK), (80, y + 20))
        if spec.get("seal"):
            s = seal(*spec["seal"])
            f.alpha_composite(s, (W - s.width - 30, H - s.height - 20))
    elif v == "family":   # 한 가족만 색칠 + 폴라로이드 + 질문
        fam = FAM[spec["fam"]][1]
        f.alpha_composite(seoul_map((60, 260, 900, 1060), only=fam, hl=spec.get("hl")))
        p = polaroid(spec["photo"], 640, 430, spec["cap"], -4)
        f.alpha_composite(p, (W - p.width - 40, 260))
        y = 40
        for i, ln in enumerate(spec["title"].split("\n")):
            im = text(ln, "NanumMyeongjo-ExtraBold.ttf", spec.get("size", 150), INK if i == 0 else RED, stroke=6)
            f.alpha_composite(im, (60, y))
            y += im.height - 10
        if spec.get("seal"):
            s = seal(*spec["seal"], R=120)
            f.alpha_composite(s, (W - s.width - 30, H - s.height - 10))
    elif v == "collage":   # 폴라로이드 3장 + 지도 + 제목
        f.alpha_composite(seoul_map((1060, 380, 1890, 1060)))
        for (ph, cap, tl, xy) in spec["photos"]:
            p = polaroid(ph, 420, 290, cap, tl)
            f.alpha_composite(p, xy)
        y = 560
        for i, ln in enumerate(spec["title"].split("\n")):
            im = text(ln, "NanumMyeongjo-ExtraBold.ttf", spec.get("size", 150), INK if i == 0 else RED, stroke=6)
            f.alpha_composite(im, (60, y))
            y += im.height - 14
    # 채널 꼬리표
    tag = text("악어새 지식창고, 한 번에 정리", "NanumPenScript-Regular.ttf", 46, (120, 110, 92))
    f.alpha_composite(tag, (W - tag.width - 40, 20))
    return f.convert("RGB")


SPECS = [
    {"name": "T01", "v": "map_big", "kicker": "지도로 보는", "title": "서울 25개 구\n한 번에", "sub": "뿌리는 딱 7개?", "seal": ("구의 족보", "25", "서울")},
    {"name": "T02", "v": "family", "fam": "성동", "hl": "성동구", "photo": "sp_seongsu4", "cap": "성수동 골목", "title": "강남 3구의 엄마는\n성수동?", "seal": ("성동구 가족", "1943", "성동구")},
    {"name": "T03", "v": "map_big", "kicker": "서울 25개 구 한 번에", "title": "동대문구엔\n동대문이 없다", "size": 140, "sub": "구의 족보, 궁궐, 4대문", "seal": ("반전", "4대문", "한양도성")},
    {"name": "T04", "v": "collage", "title": "서울 25개 구\n한 번에 정리", "photos": [("sp_gyeongbok", "종로구 경복궁", -5, (60, 40)), ("gu_songpa", "송파구 롯데월드타워", 4, (560, 70)), ("sp_dobongsan", "도봉구 도봉산", -3, (1080, 30))]},
    {"name": "T05", "v": "map_big", "kicker": "우리 구는", "title": "어느 집안?", "size": 210, "sub": "서울 25개 구의 족보", "names": True, "seal": ("1943", "7", "→ 25")},
    {"name": "T06", "v": "family", "fam": "영등포", "hl": "영등포구", "photo": "gu_yeongdeungpo", "cap": "여의도 국회의사당", "title": "서남권 7개 구가\n한 집안?", "seal": ("영등포구 가족", "7", "형제")},
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    outs = []
    for sp in SPECS:
        im = make(sp).resize((1280, 720), Image.LANCZOS)
        p = OUT / f"{sp['name']}.png"
        im.save(p)
        outs.append(p)
        print("썸네일 →", p)
    sheet = Image.new("RGB", (2 * 650 + 10, 3 * 380 + 10), (20, 20, 24))
    for i, p in enumerate(outs):
        sheet.paste(Image.open(p).resize((640, 360)), (10 + (i % 2) * 650, 10 + (i // 2) * 380))
    sheet.save(OUT / "비교표.jpg", quality=90)
