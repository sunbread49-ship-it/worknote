"""트렌디한 장면 사진(Unsplash) → 쇼츠 팩토리 템플릿 5종 결과 화면 목업 (엔진의 실제 배치 · 헤드 레이어 사용)"""
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/user/Shorts-Factory/server")
import pipeline as P  # noqa: E402

PH = Path("/home/user/worknote/business/sf_marketing/photos")
OUT = Path(__file__).resolve().parent / "mock"
OUT.mkdir(exist_ok=True)
FONT = str(next(p for p in (Path("/home/user/Shorts-Factory"), Path("/home/user/shorts-factory")) if p.exists()) / "server/fonts/Pretendard-Black.otf")

# 템플릿 순서: tpl1 심플 화이트 · tpl2 네온 다크 · tpl3 빅 블랙 · tpl4 빅 풀스크린 · tpl5 아이보리 노트
ITEMS = [
    ("simple", "drama", "드라마 엔딩\n결국 고백했다", "고백했다", "[10년] 만에 한 고백"),
    ("neon", "rain", "웹드라마 명장면\n비 오는 날 이별", "이별", "우산 [하나]로 끝난 사이"),
    ("bigblack", "set", "영화 촬영장\nNG 레전드", "레전드", "NG만 [27번] 났대요"),   # 11/23 안무 샘플 → 영화 촬영장
    ("full", "concert", "콘서트 떼창\n소름 돋은 순간", "소름", "[3만 명]이 같이 불렀어요"),
    ("ivory", "talk", "예능 토크\n찐친 폭로전", "폭로전", "[1초] 만에 터진 웃음"),
    ("bigblack", "set", "촬영장 비하인드\nNG 모음", "NG", "NG만 [27번] 났대요"),
]


def cover(im, w, h, fx=0.5, fy=0.5):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x = int((im.width - w) * fx)
    y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def sub(d, key, text, y, size=110):
    st = P.TPL[key]["sub"]
    f = ImageFont.truetype(FONT, size)
    parts, cur, on = [], "", False
    for ch in text:
        if ch in "[]":
            parts.append((cur, on)); cur, on = "", ch == "["
        else:
            cur += ch
    parts.append((cur, on))
    w = sum(f.getlength(t) for t, _ in parts)
    while w > 960:
        size -= 4; f = ImageFont.truetype(FONT, size); w = sum(f.getlength(t) for t, _ in parts)
    x = (1080 - w) / 2
    top = y - size * 0.62
    if st.get("box"):
        pad = max(10, size // 7)
        d.rectangle((x - pad * 1.6, top - pad * 0.5, x + w + pad * 1.6, top + size * 1.18 + pad * 0.5), fill=st["box"])
    for t, h in parts:
        d.text((x, top), t, font=f, fill=st["hl"] if h else st["fg"], stroke_width=0 if st.get("box") else st.get("stroke", 9),
               stroke_fill=(0, 0, 0))
        x += f.getlength(t)


def mock(key, photo, head, hl, text, out):
    g = P.geo(key)
    v = g["video"]
    with tempfile.TemporaryDirectory() as td:
        P.tpl_layers(Path(td), key, head, hl)
        bg = Image.open(Path(td) / "bg.png").convert("RGB")
        top = Image.open(Path(td) / "top.png").convert("RGBA")
    src = Image.open(PH / f"sf_{photo}.jpg").convert("RGB")
    if v["mode"] == "wide":
        frame = cover(src, v["vw"], v["h"])
        x = (v["vw"] - v["w"]) // 2
        frame = frame.crop((x, 0, x + v["w"], v["h"]))
    else:
        frame = cover(src, v["w"], v["h"])
    bg.paste(frame, (v["x"], v["y"]))
    im = Image.alpha_composite(bg.convert("RGBA"), top).convert("RGB")
    sub(ImageDraw.Draw(im), key, text, g["sub_y"])
    im.save(out, quality=92)


for i, (k, ph, head, hl, t) in enumerate(ITEMS, 1):
    mock(k, ph, head, hl, t, OUT / f"tpl{i}.jpg")
print("ok")
