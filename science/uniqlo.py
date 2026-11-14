"""지식창고 쇼츠 #8 · 옷을 통에 던져 넣기만 했는데 가격이 뜬다? (유니클로 셀프계산대 · RFID)
  python3 science/uniqlo.py [--stills]
사실 근거 (보도): 유니클로 셀프계산대는 가격표 속에 숨은 RFID 칩을 계산대 통 안의 리더가 자동으로 읽는다
  (WSJ 인용 SupplyChainBrain 'Uniqlo Automates Store Checkout with RFID Chips')
RFID 일반 원리: 배터리 없는 수동형 태그가 리더 전파의 에너지로 깨어나 자기 번호를 되돌려 보냄 · 시선(빛)이 필요 없음 ·
  여러 태그는 아주 빠르게 차례로 대답해서 사실상 한꺼번에 읽힘
사진 (Wikimedia Commons): Syced 'Self-checkout at UNIQLO in Tokyo' (CC0) · Kashiwa Satō 'Uniqlo Logo' (CC BY 2.0) ·
  Nielsoncaetanosalmeron 'Inside of UNIQLO Disney Springs' (CC BY 4.0) — 상표는 '그 회사를 가리킬 때만' 사용, 제휴 아님
쇼츠 기조: 전환 빠르게(장면 2~3초) · 첫 1초 결과 장면 · 내용 효과음만 · 밝은 배경음 · 좋아요/친구 → 루프
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K
from shortkit import G, T, W, H, CREAM, DIM, CORAL, GOLD, MINT

OUT = K.HERE / "out" / "uniqlo"
HEAD = {"kicker": "생활 속 과학", "title": "던지면 계산 끝?", "highlight": "계산 끝"}
SAY = {"RFID": "알에프아이디", "39,900원": "삼만 구천 구백 원"}
CX = W / 2
RED = (235, 30, 40)
CLOTHES = [(220, 60, 60), (60, 90, 170), (230, 220, 200), (40, 40, 48), (120, 170, 120), (240, 190, 70)]


def full_photo(f, name, t, dark=0.3, zoom=0.08, focus=(0.5, 0.5)):
    im = K.photo(name, int(W * 1.12), int(H * 1.12), focus, dark)
    z = 1 + zoom * G.clamp(t / 3)
    w, h = int(W * 1.12 / z), int(H * 1.12 / z)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    f.alpha_composite(im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR))


def big(f, text, y, size=120, hl="", col=CREAM, o=1.0, hlc=GOLD):
    im = T(text, size, col, "Black", highlight=hl, hl_fill=hlc, align="center", line_gap=1.08, stroke=9, stroke_fill=(6, 8, 14))
    if im.width > W - 60:
        im = im.resize((W - 60, int(im.height * (W - 60) / im.width)), Image.LANCZOS)
    K.drop(f, im, (CX, y), "mm", o, blur=26, alpha=0.8)


def pill_tag(f, text, t, y=420, col=GOLD, fg=(12, 10, 6)):
    k = G.ease_out(G.clamp(t / 0.25))
    K.drop(f, G.pill(text, "Black", 66, fg, col, pad=(38, 14)), (CX, y - (1 - k) * 20), "mt", k, blur=12)


def tshirt(col, s=220, rot=0):
    k = 2
    im = Image.new("RGBA", (int(s * 1.3) * k, int(s * 1.3) * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = s * 0.15 * k
    u = s * k
    pts = [(0.3, 0.05), (0.42, 0.12), (0.58, 0.12), (0.7, 0.05), (1.0, 0.25), (0.88, 0.42), (0.78, 0.36), (0.78, 1.0),
           (0.22, 1.0), (0.22, 0.36), (0.12, 0.42), (0.0, 0.25)]
    d.polygon([(o + x * u, o + y * u) for x, y in pts], fill=col + (255,), outline=tuple(int(c * 0.7) for c in col) + (255,))
    # 가격표(흰 꼬리표)
    d.rectangle((o + 0.62 * u, o + 0.5 * u, o + 0.74 * u, o + 0.66 * u), fill=(250, 250, 250, 255))
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


def bin_box(f, cx, top, w=700, h=520, glow=0.0):
    """셀프계산대 통 (단면): 흰 통 + 바닥 안테나"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((cx - w / 2, top, cx + w / 2, top + h), 30, fill=(236, 238, 242, 255), outline=(200, 204, 214, 255), width=6)
    d.rounded_rectangle((cx - w / 2 + 30, top + 30, cx + w / 2 - 30, top + h - 30), 20, fill=(214, 218, 226, 255))
    a = int(120 + 135 * glow)
    d.rectangle((cx - w / 2 + 60, top + h - 70, cx + w / 2 - 60, top + h - 50), fill=(255, 200, 80, a))
    f.alpha_composite(ov)
    return (cx, top + h - 60)


# ── 실제 옷 사진(퍼블릭 도메인, rawpixel) 누끼로 '대충 던져 넣는' 장면 ─────────────────
import numpy as np
from functools import lru_cache


@lru_cache(maxsize=2)
def pile_pieces(width=900):
    """구겨진 옷 더미 사진을 물결 모양 경계로 5조각 → 하나씩 던져져 다시 더미가 됨"""
    im = Image.open(K.HERE.parent / "youtube" / "assets" / "people" / "clo_tees_cut.png").convert("RGBA")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    w, h = im.size
    a = np.asarray(im.getchannel("A")).copy()
    n = 5
    yy = np.arange(h)
    bounds = [np.zeros(h)] + [w * k / n + 35 * np.sin(yy / 23 + k * 1.7) for k in range(1, n)] + [np.full(h, w)]
    pieces = []
    xs = np.arange(w)[None, :]
    for k in range(n):
        m = (xs >= bounds[k][:, None]) & (xs < bounds[k + 1][:, None])
        pa = np.where(m, a, 0).astype(np.uint8)
        pc = im.copy()
        pc.putalpha(Image.fromarray(pa))
        bb = pc.getbbox()
        pieces.append((pc.crop(bb), bb[0], bb[1]))
    return pieces, (w, h)


BIN = (560, 1230)   # 사진 속 계산대 통 바닥 가운데 (focus 1.0 기준)


def toss(f, t, t0=0.0, gap=0.2):
    """옷 조각들이 제각각 회전하며 떨어져 통 안에 쌓임. 착지한 개수 반환"""
    pieces, (w, h) = pile_pieces()
    ox, oy = BIN[0] - w / 2, BIN[1] - h / 2
    landed = 0
    for k, (pc, x, y) in enumerate(pieces):
        u = G.clamp((t - t0 - k * gap) / 0.45)
        if u <= 0:
            continue
        e = u * u   # 떨어질수록 빨라짐
        rot = (1 - e) * (70 if k % 2 else -55) * (1 + k * 0.2)
        sx = (1 - e) * (-260 + k * 130)
        sy = (1 - e) * (-1100 - k * 60)
        im = pc.rotate(rot, expand=True, resample=Image.BICUBIC) if abs(rot) > 0.5 else pc
        cx, cy = ox + x + pc.width / 2 + sx, oy + y + pc.height / 2 + sy
        K.drop(f, im, (cx, cy), "mm", 1, blur=18, alpha=0.5)
        if u >= 1:
            landed += 1
    return landed


def price_panel(f, n, x=60, y=520, o=1.0, check=True):
    items = [("니트", "39,900원"), ("셔츠", "29,900원"), ("티셔츠", "14,900원"), ("바지", "49,900원"), ("후드", "39,900원")]
    card = Image.new("RGBA", (460, 130 + 74 * max(n, 1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 26, fill=(255, 255, 255, 246))
    card.alpha_composite(T("자동 인식", 42, RED, "Black"), (30, 28))
    for i, (a, b) in enumerate(items[:n]):
        if check:
            card.alpha_composite(T("✓", 38, (30, 170, 90), "Black"), (28, 100 + i * 74))
        card.alpha_composite(T(a, 38, (30, 32, 40), "ExtraBold"), (78, 100 + i * 74))
        tb = T(b, 38, (30, 32, 40), "Black")
        card.alpha_composite(tb, (card.width - 30 - tb.width, 100 + i * 74))
    K.drop(f, card, (x, y), "lt", o, blur=18)


# ── 장면 ─────────────────────────────────────────────────────────
def s_hook(f, t, sc):
    """결과 먼저: 실제 계산대 통에 옷을 아무렇게나 휙휙 → 떨어지는 족족 가격이 뜸"""
    full_photo(f, "uq_selfcheck", t, dark=0.12, zoom=0.04, focus=(1.0, 0.5))
    n = toss(f, t + 0.55, 0.0, 0.18)
    if n:
        price_panel(f, n, 600, 420)
    big(f, "대충 던졌는데\n가격이 뜬다?", 230, 118, hl="가격이 뜬다")
    K.credit(f, K.credit_of("uq_selfcheck") + " · 옷 사진: rawpixel CC0")


def s_store(f, t, sc):
    if t < 1.0:
        full_photo(f, "uq_logo", t, dark=0.15, zoom=0.15, focus=(0.55, 0.45))
        K.credit(f, K.credit_of("uq_logo"))
    else:
        full_photo(f, "uq_selfcheck", t - 1, dark=0.2, zoom=0.15, focus=(0.6, 0.5))
        K.credit(f, K.credit_of("uq_selfcheck"))
    big(f, "바코드도\n안 찍었는데?", 1150, 120, hl="바코드")


def s_tag(f, t, sc):
    """가격표 확대 → 속이 비치며 칩 + 안테나가 빛남"""
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 24, 255)))
    k = G.ease_out(G.clamp(t / 0.4))
    tw, th = int(560 * (0.8 + 0.2 * k)), int(820 * (0.8 + 0.2 * k))
    tag = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle((0, 0, tw - 1, th - 1), 30, fill=(250, 250, 250, 255))
    d.ellipse((tw / 2 - 22, 40, tw / 2 + 22, 84), fill=(14, 16, 24, 255))
    tag.alpha_composite(T("39,900원", 70, (30, 32, 40), "Black"), (60, 130))
    for i in range(30):  # 바코드
        x = 60 + i * 15
        d.rectangle((x, th - 220, x + (4 if i % 3 else 8), th - 120), fill=(30, 32, 40, 255))
    xr = G.clamp((t - 0.6) / 0.6)  # 엑스레이: 속이 비침
    if xr > 0:
        ins = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        di = ImageDraw.Draw(ins)
        di.rounded_rectangle((0, 0, tw - 1, th - 1), 30, fill=(10, 30, 60, int(230 * xr)))
        cx, cy = tw / 2, th / 2 + 40
        pts = []
        for j in range(60):  # 지그재그 안테나(양쪽)
            u = j / 59
            pts.append((40 + u * (tw - 80), cy + (36 if j % 2 else -36)))
        di.line(pts, fill=(255, 200, 80, int(255 * xr)), width=8)
        di.rectangle((cx - 26, cy - 26, cx + 26, cy + 26), fill=(255, 240, 200, int(255 * xr)))
        ins = Image.alpha_composite(ins.filter(ImageFilter.GaussianBlur(6)), ins)
        tag.alpha_composite(ins)
    K.drop(f, tag, (CX, 820), "mm", 1, blur=30)
    pill_tag(f, "가격표 속 비밀", t)
    if xr >= 1:
        G.blit(f, T("칩", 56, GOLD, "Black", stroke=5, stroke_fill=(6, 8, 14)), (CX + 70, 860 - 120), 1, "lm")
        G.blit(f, T("안테나", 56, GOLD, "Black", stroke=5, stroke_fill=(6, 8, 14)), (CX - 300, 860 + 70), 1, "lm")


def s_nobat(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 24, 255)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((CX - 220, 640, CX + 200, 860), 30, outline=(230, 232, 240, 255), width=16)
    d.rectangle((CX + 200, 710, CX + 236, 790), fill=(230, 232, 240, 255))
    k = G.ease_out(G.clamp((t - 0.3) / 0.3))
    if k > 0:
        d.line((CX - 300, 560 + (1 - k) * 0, CX - 300 + 600 * k, 560 + 380 * k), fill=RED + (255,), width=26)
    f.alpha_composite(ov)
    big(f, "배터리 0개", 1100, 130, col=CREAM)
    pill_tag(f, "그런데", t, col=CORAL)


def s_wave(f, t, sc):
    """리더가 전파를 쏨 → 칩이 깨어나 번호로 대답"""
    L = sc["L"]
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 26, 255)))
    src = bin_box(f, CX, 820, 760, 440, glow=1.0)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for j in range(4):
        ph = ((t * 0.9) + j / 4) % 1
        r = 60 + 520 * ph
        d.arc((src[0] - r, src[1] - r, src[0] + r, src[1] + r), 200, 340, fill=(255, 200, 80, int(220 * (1 - ph))), width=8)
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4)))
    f.alpha_composite(ov)
    tag_xy = (CX, 720)
    on = t > (L[1] if len(L) > 1 else 1.0)
    col = (255, 230, 120) if on else (120, 130, 150)
    d2 = ImageDraw.Draw(f)
    d2.rounded_rectangle((tag_xy[0] - 60, tag_xy[1] - 40, tag_xy[0] + 60, tag_xy[1] + 40), 10, fill=col + (255,))
    if len(L) > 2 and t > L[2]:
        k = G.ease_out(G.clamp((t - L[2]) / 0.3))
        b = G.pill("나는 39,900원 니트!", "Black", 58, (12, 10, 6), MINT, pad=(30, 12))
        K.drop(f, b, (CX, 650 - (1 - k) * 20), "mb", k, blur=14)
    pill_tag(f, "전파로 깨우고, 전파로 대답", t, y=380)


def s_many(f, t, sc):
    """구겨지고 뒤집히고 밑에 깔린 옷까지 — 더미 속 칩들이 차례로 '나 여기!' 하고 빛남"""
    full_photo(f, "uq_selfcheck", t + 2, dark=0.35, zoom=0.05, focus=(1.0, 0.5))
    toss(f, 99)
    pieces, (w, h) = pile_pieces()
    ox, oy = BIN[0] - w / 2, BIN[1] - h / 2
    rng = np.random.default_rng(3)
    spots = [(ox + w * (0.12 + 0.76 * rng.random()), oy + h * (0.25 + 0.6 * rng.random())) for _ in range(7)]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i, (x, y) in enumerate(spots):
        on = t > 0.2 + i * 0.18
        if not on:
            continue
        pulse = 0.5 + 0.5 * math.sin(t * 9 + i)
        r = 18 + 10 * pulse
        d.ellipse((x - r * 2.4, y - r * 2.4, x + r * 2.4, y + r * 2.4), fill=(255, 220, 90, int(70 * pulse)))
        d.rounded_rectangle((x - 16, y - 11, x + 16, y + 11), 4, fill=(255, 236, 150, 255))
    f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
    f.alpha_composite(ov)
    pill_tag(f, "구겨져도 · 뒤집혀도 · 깔려도", t, y=330)
    big(f, "한 번에\n전부 인식", 600, 130, hl="전부", o=G.ease_out(G.clamp((t - 1.4) / 0.3)))


def s_vs(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 24, 255)))
    k1 = G.ease_out(G.clamp(t / 0.3))
    k2 = G.ease_out(G.clamp((t - 0.6) / 0.3))
    for i, (head, body, col, k) in enumerate((("바코드", "하나씩\n빛으로 비춰야", (150, 156, 176), k1),
                                                ("RFID", "한 번에\n옷 속까지 통과", GOLD, k2))):
        card = Image.new("RGBA", (470, 600), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, 469, 599), 30, fill=(24, 28, 40, 245), outline=col + (255,), width=6)
        card.alpha_composite(T(head, 92, col, "Black"), ((470 - T(head, 92, col, "Black").width) // 2, 60))
        bt = T(body, 64, CREAM, "Black", align="center", line_gap=1.2)
        if bt.width > 430:
            bt = bt.resize((430, int(bt.height * 430 / bt.width)), Image.LANCZOS)
        card.alpha_composite(bt, ((470 - bt.width) // 2, 250))
        K.drop(f, card, (CX - 255 + i * 510, 590 + (1 - k) * 30), "mm", k, blur=20)
    G.blit(f, T("VS", 90, CORAL, "Black", stroke=6, stroke_fill=(6, 8, 14)), (CX, 590), k2, "mm")
    # RFID 풀네임 · 우리말 · 원리 한 줄 (2026-11-12 피드백)
    L = sc["L"]
    k3 = G.ease_out(G.clamp((t - (L[-1] if len(L) > 1 else 1.2)) / 0.35))
    if k3 > 0:
        box = Image.new("RGBA", (980, 300), (0, 0, 0, 0))
        dd = ImageDraw.Draw(box)
        dd.rounded_rectangle((0, 0, 979, 299), 28, fill=(255, 214, 80, 250))
        t1 = T("RFID = Radio-Frequency IDentification", 46, (14, 16, 24), "Black")
        t2 = T("무선 주파수 식별", 74, (14, 16, 24), "Black")
        t3 = T("전파로 물건의 이름표를 읽는 기술", 44, (60, 50, 20), "ExtraBold")
        for im_, yy in ((t1, 30), (t2, 100), (t3, 210)):
            if im_.width > 920:
                im_ = im_.resize((920, int(im_.height * 920 / im_.width)), Image.LANCZOS)
            box.alpha_composite(im_, ((980 - im_.width) // 2, yy))
        K.drop(f, box, (CX, 950 - (1 - k3) * 30), "mt", k3, blur=20)


def s_gate(f, t, sc):
    """반전: 같은 원리로 '계산 안 한 물건'을 출입구에서 잡아내는 매장도 있다"""
    full_photo(f, "uq_store", t, dark=0.45, zoom=0.08)
    if t > 0.6 and int(t * 5) % 2 == 0:
        f.alpha_composite(Image.new("RGBA", (W, H), (255, 0, 0, 70)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in (CX - 260, CX + 260):
        d.rounded_rectangle((x - 30, 520, x + 30, 1180), 20, fill=(230, 232, 240, 230))
    f.alpha_composite(ov)
    pill_tag(f, "같은 원리로", t, col=CORAL)
    big(f, "계산 안 한 옷은\n문에서 삐-!", 1170, 112, hl="삐-!", hlc=(255, 90, 90))
    K.credit(f, K.credit_of("uq_store"))


def s_share(f, t, sc):
    full_photo(f, "uq_selfcheck", t, dark=0.6, zoom=0.04, focus=(0.6, 0.5))
    k = G.ease_out(G.clamp(t / 0.3))
    K.drop(f, T("좋아요 누르고", 110, GOLD, "Black", stroke=8, stroke_fill=(6, 8, 14)), (CX, 720 - (1 - k) * 20), "mm", k, blur=20)
    k2 = G.ease_out(G.clamp((t - 0.7) / 0.3))
    K.drop(f, T("친구한테\n물어보세요", 140, CREAM, "Black", highlight="물어보세요", hl_fill=GOLD, align="center", line_gap=1.08,
                stroke=8, stroke_fill=(6, 8, 14)), (CX, 960 - (1 - k2) * 20), "mm", k2, blur=24)
    K.credit(f, K.credit_of("uq_selfcheck"))


def draw_cover(f):
    s_hook(f, 2.5, {"L": [0]})


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.6, "gap": 0.12, "tail": 0.15,
     "sfx_t": [(0.0, "pop", 0.45), (0.18, "pop", 0.45), (0.36, "pop", 0.45), (0.54, "pop", 0.45), (0.72, "pop", 0.45), (0.95, "ding", 0.55)],
     "narr": ["옷을 통에 던져 넣기만 했는데, / 가격이 바로 뜬다?"]},
    {"draw": s_store, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "accent", 0.45)],
     "narr": ["유니클로 셀프계산대, 바코드도 안 찍었는데요? 비밀은 30초면 풀려요."]},
    {"draw": s_tag, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.6, "reveal", 0.55)],
     "narr": ["비밀은 가격표 속에 숨은, / 아주 작은 칩과 안테나예요."]},
    {"draw": s_nobat, "flash": True, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "accent_low", 0.55)],
     "narr": ["그런데 배터리도 없는데, / 어떻게 대답할까요?"]},
    {"draw": s_wave, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.05, "glide", 0.5), (sc["L"][1], "accent", 0.5), (sc["L"][2], "ding", 0.55)],
     "narr": ["통 안의 안테나가 전파를 쏘면,", "그 에너지로 칩이 잠깐 깨어나서,", "자기 번호를 전파로 대답해요."]},
    {"draw": s_many, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.1, "tick", 0.35), (0.4, "tick", 0.35), (0.7, "tick", 0.35), (1.0, "tick", 0.35), (1.3, "tick", 0.35), (1.6, "reveal", 0.55)],
     "narr": ["여러 벌이 눈 깜짝할 새 차례로 대답해서, / 한 번에 읽는 것처럼 보이죠."]},
    {"draw": s_vs, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "accent", 0.45), (0.6, "accent", 0.45)],
     "sfx_fn": lambda sc: [(sc["L"][-1], "sparkle", 0.5)],
     "narr": ["빛으로 하나씩 비추는 바코드와 달리, / 전파는 옷 속까지 통과하니까요.", "알에프아이디, 우리말로 무선 주파수 식별. / 전파로 물건의 이름표를 읽는 기술이에요."]},
    {"draw": s_gate, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.6, "accent_low", 0.5), (0.8, "fail", 0.35)],
     "narr": ["같은 원리로, 계산 안 한 물건을 / 출입구에서 잡아내는 매장도 있어요."]},
    {"draw": s_share, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.75, "pop", 0.6)],
     "narr": [K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["옷을 통에 던져 넣기만 했는데, / 가격이 바로 뜬다?"]},
]

if __name__ == "__main__":
    # 2026-11-14 v2: Gemini 음성(Umbriel · 빠르게) + 5초 안 약속 ("비밀은 30초면 풀려요")
    OUT = OUT.parent / "uniqlo_v2"
    K.run(SCENES, HEAD, OUT, {**SAY, "__gemini__": {"voice": "Umbriel", "speed": "빠르게"}}, cover=draw_cover)
