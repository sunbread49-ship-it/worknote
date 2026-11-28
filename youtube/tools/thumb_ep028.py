"""EP028 삼성 배당 '보너스의 함정' 썸네일 시안 6종 (A~F) + 비교표
  python3 tools/thumb_ep028.py → out/ep028_samsung_dividend/thumb_A~F.png · thumbs_compare.jpg
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thumbs as TH  # noqa: E402
import thumb_retitle as RT  # noqa: E402
from thumb_ep027 import plaque  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out/ep028_samsung_dividend"
W, H = TH.W, TH.H
YEL, RED, WHITE, GREEN = (255, 214, 40), (255, 60, 60), (255, 255, 255), (70, 230, 150)


def frame(scene, dark=0.5, last=True):
    fs = sorted((OUT / "hf" / scene / "frames").glob("*.jpg"))
    im = Image.open(fs[-1] if last else fs[len(fs) // 2]).convert("RGB").resize((W, H))
    return ImageEnhance.Brightness(im).enhance(1 - dark).convert("RGBA")


def make_a():   # 판정 장면 배경 + '배당 파이어?' 질문
    f = frame("07_verdict", 0.9)
    TH.shadowed(f, plaque("logo_samsung", 420, 150), (W // 2, 70), "mt")
    TH.shadowed(f, TH.T("삼성전자로 배당 파이어?", 130, WHITE, hl="파이어?", hl_color=YEL), (W // 2, 300), "mt")
    TH.shadowed(f, TH.T("1억 = 월 5만 8천 원", 190, RED, hl="5만 8천", hl_color=YEL), (W // 2, 560), "mt")
    return f


def make_b():   # S2 · 만 원권 실사 + 빨간 띠
    return RT.make_s2({"photo": "krw_10000", "l1": "삼성 배당 4,601원", "l2": "또 나올까?", "hl": "4,601원",
                       "bubble": "다음 보너스는 1월", "badge": None})


def make_c():   # S4 · 폰 실사 + 노란 상자
    return RT.make_s4({"photo": "me_phone_city", "l1": "삼성전자로 월 300만?", "l2": "51억 필요", "hl": "51억",
                       "bubble": "통장 숫자 믿으면 틀려요", "badge": None})


def make_d():   # P03 화살표 · 보너스 → 평소
    f = frame("03_divcal", 0.9)
    TH.shadowed(f, TH.T("삼성전자 배당", 100, WHITE), (W // 2, 90), "mt")
    a, arr, b = TH.T("4,601원", 230, YEL), TH.T("→", 190, WHITE), TH.T("370원", 230, RED)
    x = (W - (a.width + arr.width + b.width + 80)) // 2
    TH.shadowed(f, a, (x, 330)); TH.shadowed(f, arr, (x + a.width + 40, 350)); TH.shadowed(f, b, (x + a.width + arr.width + 80, 330))
    TH.shadowed(f, TH.T("보너스였습니다", 150, WHITE, hl="보너스", hl_color=YEL), (W // 2, 720), "mt")
    return f


def make_e():   # 입금 알림 폰 + '1월에 또?'
    f = frame("01_bankpush", 0.35)
    ImageDraw.Draw(f).rectangle((820, 0, W, H), fill=(14, 22, 48, 255))
    TH.shadowed(f, TH.T("+389,245원", 150, GREEN), (880, 230))
    TH.shadowed(f, TH.T("1월에\n또 들어올까?", 170, WHITE, hl="또", hl_color=YEL), (880, 470))
    return f


def make_f():   # S3 · 서초 실사 + 왼쪽 검은 패널
    return RT.make_s3({"photo": "gu_seocho", "l1": "배당 파이어", "l2": "삼성은 안 된다", "hl": "안 된다",
                       "bubble": "1억이면 월 5만 8천 원", "badge": None})


if __name__ == "__main__":
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
