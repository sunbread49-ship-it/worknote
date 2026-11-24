"""11/25 망한 롱폼 A그룹 10편 재포장 — 제목 · 썸네일 2종(A: 실사 + 말풍선 + 2줄 / B: 큰 숫자 · 결말 카드)
나스닥 -20% 편(클릭률 8%) 공식: 실사 어둡게 + 말풍선 질문 + 큰 글씨 2줄(흰 + 노랑, 숫자는 빨강) + '결말' 배지
  python tools/thumb_retitle.py            → out/retitle/<ep>_A.png · _B.png + 비교표.jpg
  python tools/thumb_retitle.py --apply    → 제목 변경 + 썸네일 A 업로드 (YouTube API) · B는 Studio '테스트 및 비교'용
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/retitle"
W, H = TH.W, TH.H
YEL, RED, WHITE = (255, 214, 40), (255, 60, 60), (255, 255, 255)

ITEMS = [
    dict(ep="ep004_templeton_vix", id="fOkegCj4T9Q", photo="nyse_floor",
         title="나스닥 공포 최고조일 때 3배로 산 사람들, 11번의 결말 (평균 +117%, 최악 -80%)",
         bubble="다들 팔 때 샀다면?", l1="공포에 3배로 산", l2="11번의 결말", hl="11번", big="11번", big_sub="공포 최고조에 산 결말"),
    dict(ep="ep003_midterm_cycle", id="KBMQw7_aHFk", photo="ev_wallst",
         title="중간선거 끝났다, 76년간 19번 중 19번 오른 다음 1년 (미국 주식 백테스트)",
         bubble="선거 끝났는데 사도 돼?", l1="중간선거 다음 1년", l2="19번 중 19번", hl="19번", big="19/19", big_sub="선거 다음 1년의 결말"),
    dict(ep="ep006_lameduck_gridlock", id="aNpRLkol8LQ", photo="trump",
         title="트럼프 힘 빠지면 내 미국 주식은? 레임덕 5번, 1년 뒤의 결말",
         bubble="내 미국 주식 괜찮아?", l1="대통령 힘 빠지면", l2="5번의 결말", hl="5번", big="5번", big_sub="레임덕 1년 뒤"),
    dict(ep="ep007_halloween", id="tcQvg1c15F0", photo="stock_monitor",
         title="11월에 산 사람들의 결말, 76년 동안 진짜 올랐을까? (핼러윈 매매법)",
         bubble="지금 11월, 사도 돼?", l1="11월에 산 사람들", l2="76년의 결말", hl="76년", big="76년", big_sub="11월에 산 결말"),
    dict(ep="ep010_korea_us", id="gGp7apOKjUo", photo="krx_building",
         title="코스피 일주일 -10% 폭락 16번, 그때 산 사람들의 결말 (1년 · 3년 뒤)",
         bubble="내 국내 주식 돌아와?", l1="코스피 -10% 일주일", l2="16번의 결말", hl="-10%", big="16번", big_sub="코스피 폭락 주의 결말"),
    dict(ep="ep012_chip_crash", id="Blomyp9dPeE", photo="skhynix_art",
         title="반도체 폭락 때 산 사람들의 결말, 2002년 이후 8번은 이랬다 (SK하이닉스 -60%)",
         bubble="반도체 이대로 끝?", l1="하이닉스 -60%", l2="그때 샀다면?", hl="-60%", big="8번", big_sub="반도체 폭락 때 산 결말"),
    dict(ep="ep018_soxl", id="s395qQjzRno", photo="chip_dark",
         title="반도체 3배 SOXL -84%, 지금 1,000만 원 넣으면? 16년 실험 결과",
         bubble="지금이 바닥일까?", l1="-84%에 1,000만 원", l2="넣었다면?", hl="-84%", big="-84%", big_sub="반도체 3배, 16년 실험"),
    dict(ep="ep008_lump_vs_dca", id="2erL2xkbvFk", photo="money_burning",
         title="목돈 1,200만 원, 한 번에 넣을까 나눠 넣을까? 76년 910번 실험의 결말",
         bubble="지금 넣으면 물릴까?", l1="한 번에? 나눠서?", l2="910번 실험", hl="910번", big="910번", big_sub="목돈 1,200만 원의 결말"),
    dict(ep="ep009_jensen_huang", id="yeU6aJzjtr8", photo="jensen_010",
         title="엔비디아에 100만 원 넣고 -90%를 버텼다면? 젠슨 황 33년, 4,975배의 결말",
         bubble="-90%를 버텼다면?", l1="엔비디아 100만 원", l2="33년의 결말", hl="100만 원", big="-90%", big_sub="버틴 사람의 결말"),
    dict(ep="ep016_ceo_ousted", id="aIgNBazE-y4", photo="jobs_1984",
         title="CEO가 쫓겨난 날 그 주식을 샀다면? 스티브 잡스 · 젠슨 황 · 9개 회사의 결말",
         bubble="회사 망하는 거 아냐?", l1="CEO 쫓겨난 날", l2="샀다면?", hl="쫓겨난", big="9개", big_sub="CEO 쫓겨난 회사의 결말"),
]


def photo_bg(name, dark=0.55):
    p = next(q for q in (ROOT / "assets/photos").glob(name + ".*") if q.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    im = Image.open(p).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    im = ImageOps.grayscale(im).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Brightness(im).enhance(1 - dark)
    f = im.convert("RGBA")
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vg)
    for y in range(H // 3, H, 4):   # 아래쪽을 더 어둡게 → 글자
        vd.rectangle((0, y, W, y + 4), fill=(0, 0, 0, int(210 * ((y - H / 3) / (2 * H / 3)) ** 1.3)))
    f.alpha_composite(vg)
    return f


def bubble(text):
    t = TH.T(text, 78, (20, 22, 30), stroke=0)
    w, h = t.width + 80, t.height + 60
    im = Image.new("RGBA", (w, h + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=(255, 255, 255, 255))
    d.polygon(((70, h - 2), (150, h - 2), (60, h + 48)), fill=(255, 255, 255, 255))
    im.alpha_composite(t, (40, 26))
    return im


def badge(text="결말 시리즈"):
    t = TH.T(text, 44, (20, 22, 30), stroke=0)
    im = Image.new("RGBA", (t.width + 48, t.height + 22), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 16, fill=YEL + (255,))
    im.alpha_composite(t, (24, 11))
    return im


def make_a(it):
    f = photo_bg(it["photo"])
    TH.shadowed(f, bubble(it["bubble"]), (60, 50))
    b = badge()
    f.alpha_composite(b, (W - b.width - 40, 40))
    l1 = TH.fit(it["l1"], 170, 1800, color=WHITE, hl=it["hl"], hl_color=RED)
    l2 = TH.fit(it["l2"], 200, 1800, color=YEL, hl=it["hl"], hl_color=RED)
    y = H - l2.height - 50
    TH.shadowed(f, l2, (60, y))
    TH.shadowed(f, l1, (60, y - l1.height + 10))
    return f.convert("RGB")


def make_b(it):
    f = photo_bg(it["photo"], dark=0.75)
    big = TH.fit(it["big"], 420, 1500, color=RED if it["big"].startswith("-") else YEL)
    TH.shadowed(f, big, (W / 2, 260), "mt")
    sub = TH.fit(it["big_sub"], 120, 1700, color=WHITE)
    TH.shadowed(f, sub, (W / 2, 260 + big.height + 10), "mt")
    TH.shadowed(f, bubble(it["bubble"]), (60, 50))
    b = badge()
    f.alpha_composite(b, (W - b.width - 40, 40))
    return f.convert("RGB")


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (2 * 650 + 10, len(ITEMS) * 400 + 10), (20, 20, 24))
    for i, it in enumerate(ITEMS):
        for j, fn in enumerate((make_a, make_b)):
            im = fn(it).resize((1280, 720), Image.LANCZOS)
            p = OUT / f"{it['ep']}_{'AB'[j]}.jpg"
            im.save(p, quality=92)
            sheet.paste(im.resize((640, 360)), (10 + j * 650, 10 + i * 400))
            ImageDraw.Draw(sheet).text((14 + j * 650, 372 + i * 400), f"{it['ep']} {'AB'[j]}", fill=(180, 255, 60))
    sheet.save(OUT / "비교표.jpg", quality=88)
    print("비교표 →", OUT / "비교표.jpg")


def apply():
    import urllib.request
    import upload as U
    tok = U.access_token()
    log = []
    for it in ITEMS:
        v = U.call("GET", f"{U.API}/youtube/v3/videos?part=snippet&id={it['id']}", tok)["items"][0]
        sn = v["snippet"]
        old = sn["title"]
        body = {"id": it["id"], "snippet": {"title": it["title"], "description": sn.get("description", ""), "tags": sn.get("tags", []),
                                            "categoryId": sn["categoryId"], "defaultLanguage": sn.get("defaultLanguage", "ko")}}
        U.call("PUT", f"{U.API}/youtube/v3/videos?part=snippet", tok, body)
        data = (OUT / f"{it['ep']}_A.jpg").read_bytes()
        req = urllib.request.Request(f"{U.API}/upload/youtube/v3/thumbnails/set?videoId={it['id']}", data=data, method="POST",
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "image/jpeg"})
        urllib.request.urlopen(req).read()
        log.append({"id": it["id"], "ep": it["ep"], "old": old, "new": it["title"]})
        print("✔", it["id"], it["title"][:40])
    (ROOT / "retitle_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))


# ── 11/25 사용자: B는 너무 요약 느낌 → A의 문구 · 톤은 그대로, 색 · 배치만 다른 파생 3종(정기 구독자가 같은 썸네일만 보는 느낌 방지)
def photo_tint(name, tint, dark=0.45, gray=True):
    f = photo_bg(name, dark=dark) if gray else None
    if not gray:
        p = next(q for q in (ROOT / "assets/photos").glob(name + ".*") if q.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
        im = Image.open(p).convert("RGB")
        r = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
        im = ImageEnhance.Color(im).enhance(0.55)
        f = ImageEnhance.Brightness(im).enhance(1 - dark).convert("RGBA")
    if tint:
        f.alpha_composite(Image.new("RGBA", (W, H), tint + (70,)))
    return f


def make_s2(it):   # 컬러 사진(채도 낮춤) + 아래 빨간 띠에 결말 줄 · 말풍선 오른쪽 위
    f = photo_tint(it["photo"], None, dark=0.45, gray=False)
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(vg).rectangle((0, H // 2, W, H), fill=(0, 0, 0, 120))
    f.alpha_composite(vg.filter(ImageFilter.GaussianBlur(80)))
    l2 = TH.fit(it["l2"], 170, 1700, color=WHITE, hl=it["hl"], hl_color=YEL)
    band = Image.new("RGBA", (l2.width + 120, l2.height + 50), (210, 30, 40, 255)).rotate(-2, expand=True, resample=Image.BICUBIC)
    f.alpha_composite(band, (20, H - band.height - 40))
    TH.shadowed(f, l2, (80, H - band.height - 40 + (band.height - l2.height) // 2))
    l1 = TH.fit(it["l1"], 150, 1700, color=WHITE, hl=it["hl"], hl_color=YEL)
    TH.shadowed(f, l1, (70, H - band.height - 50 - l1.height))
    bb = bubble(it["bubble"])
    TH.shadowed(f, bb, (W - bb.width - 60, 50))
    b = badge()
    f.alpha_composite(b, (60, 50))
    return f.convert("RGB")


def make_s3(it):   # 왼쪽 검은 패널에 문구 세로로 크게 · 오른쪽 사진 · 노랑 테두리
    f = Image.new("RGBA", (W, H), (12, 14, 20, 255))
    ph = photo_bg(it["photo"], dark=0.35).crop((W - 1000, 0, W, H))
    f.alpha_composite(ph, (W - 1000, 0))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for x in range(0, 500):
        gd.line((W - 1000 + x, 0, W - 1000 + x, H), fill=(12, 14, 20, int(255 * (1 - x / 500))))
    f.alpha_composite(g)
    ImageDraw.Draw(f).rectangle((0, 0, W - 1, H - 1), outline=YEL + (255,), width=14)
    TH.shadowed(f, bubble(it["bubble"]), (70, 70))
    l1 = TH.fit(it["l1"], 150, 1150, color=WHITE, hl=it["hl"], hl_color=RED)
    l2 = TH.fit(it["l2"], 190, 1150, color=YEL, hl=it["hl"], hl_color=RED)
    TH.shadowed(f, l1, (70, 420))
    TH.shadowed(f, l2, (70, 430 + l1.height))
    b = badge()
    f.alpha_composite(b, (W - b.width - 50, H - b.height - 50))
    return f.convert("RGB")


def make_s4(it):   # 남색 톤 사진 · 위 흰 줄 · 아래 검은 상자 속 노랑 결말 · 말풍선 가운데 왼쪽
    f = photo_tint(it["photo"], (20, 50, 140), dark=0.5)
    l1 = TH.fit(it["l1"], 160, 1800, color=WHITE, hl=it["hl"], hl_color=YEL)
    TH.shadowed(f, l1, (W / 2, 60), "mt")
    l2 = TH.fit(it["l2"], 190, 1700, color=YEL, hl=it["hl"], hl_color=RED)
    box = Image.new("RGBA", (l2.width + 100, l2.height + 50), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), 30, fill=(8, 10, 16, 235), outline=YEL + (255,), width=6)
    f.alpha_composite(box, (int(W / 2 - box.width / 2), H - box.height - 60))
    TH.shadowed(f, l2, (W / 2, H - box.height - 60 + 25), "mt")
    TH.shadowed(f, bubble(it["bubble"]), (60, 330))
    b = badge()
    f.alpha_composite(b, (W - b.width - 40, 340))
    return f.convert("RGB")


def build_variants():
    OUT.mkdir(parents=True, exist_ok=True)
    fns = [("S2", make_s2), ("S3", make_s3), ("S4", make_s4)]
    sheet = Image.new("RGB", (3 * 650 + 10, len(ITEMS) * 400 + 10), (20, 20, 24))
    for i, it in enumerate(ITEMS):
        for j, (nm, fn) in enumerate(fns):
            im = fn(it).resize((1280, 720), Image.LANCZOS)
            im.save(OUT / f"{it['ep']}_{nm}.jpg", quality=92)
            sheet.paste(im.resize((640, 360)), (10 + j * 650, 10 + i * 400))
            ImageDraw.Draw(sheet).text((14 + j * 650, 372 + i * 400), f"{it['ep']} {nm}", fill=(180, 255, 60))
    sheet.save(OUT / "파생_비교표.jpg", quality=85)
    print("파생 →", OUT / "파생_비교표.jpg")


if __name__ == "__main__":
    if "--variants" in sys.argv:
        build_variants()
        sys.exit()
    build()
    if "--apply" in sys.argv:
        apply()
