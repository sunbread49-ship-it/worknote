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


def price_panel(f, n, x=60, y=520, o=1.0):
    items = [("니트", "39,900원"), ("셔츠", "29,900원"), ("티셔츠", "14,900원"), ("바지", "49,900원"), ("양말", "5,900원")]
    card = Image.new("RGBA", (420, 120 + 70 * n), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 24, fill=(255, 255, 255, 240))
    card.alpha_composite(T("자동 인식", 40, RED, "Black"), (30, 26))
    for i, (a, b) in enumerate(items[:n]):
        card.alpha_composite(T(a, 36, (30, 32, 40), "ExtraBold"), (30, 96 + i * 70))
        tb = T(b, 36, (30, 32, 40), "Black")
        card.alpha_composite(tb, (card.width - 30 - tb.width, 96 + i * 70))
    K.drop(f, card, (x, y), "lt", o, blur=18)


# ── 장면 ─────────────────────────────────────────────────────────
def s_hook(f, t, sc):
    """결과 먼저: 통에 옷이 우수수 → 가격이 바로 뜸"""
    f.alpha_composite(Image.new("RGBA", (W, H), (14, 16, 24, 255)))
    bin_box(f, CX + 120, 560, 640, 480, glow=0.5 + 0.5 * math.sin(t * 8))
    for i, col in enumerate(CLOTHES[:5]):
        st = G.clamp((t + 0.6 - i * 0.18) / 0.5)
        y = 120 + 640 * G.ease_out(st)
        G.blit(f, tshirt(col, 230, (i * 37) % 60 - 30), (CX + 120 - 160 + i * 80, y), 1 if st > 0 else 0, "mm")
    n = min(5, int(max(0, t + 0.6) / 0.25))
    if n:
        price_panel(f, n, 30, 360)
    big(f, "던져 넣기만 했는데\n가격이 뜬다?", 1190, 108, hl="가격이 뜬다")


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
    """통 속 옷 6벌의 칩이 아주 빠르게 차례로 대답"""
    f.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 26, 255)))
    bin_box(f, CX, 600, 860, 700, glow=1.0)
    for i, col in enumerate(CLOTHES):
        x = CX - 300 + (i % 3) * 300
        y = 820 + (i // 3) * 240
        G.blit(f, tshirt(col, 200, (i * 41) % 50 - 25), (x, y), 1, "mm")
        lit = int(t * 10) % 6 == i or t > 1.6
        if lit:
            ImageDraw.Draw(f).ellipse((x + 30, y - 10, x + 66, y + 26), fill=(255, 230, 120, 255))
    k = G.ease_out(G.clamp((t - 1.6) / 0.3))
    big(f, "한 번에\n전부 인식", 1420, 110, hl="전부", o=k)
    pill_tag(f, "눈 깜짝할 새 차례로 대답", t, y=400)


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
        K.drop(f, card, (CX - 255 + i * 510, 860 + (1 - k) * 30), "mm", k, blur=20)
    G.blit(f, T("VS", 90, CORAL, "Black", stroke=6, stroke_fill=(6, 8, 14)), (CX, 860), k2, "mm")


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
     "sfx_t": [(0.05, "pop", 0.5), (0.25, "pop", 0.5), (0.45, "pop", 0.5), (0.65, "pop", 0.5), (0.9, "ding", 0.55)],
     "narr": ["옷을 통에 던져 넣기만 했는데, / 가격이 바로 뜬다?"]},
    {"draw": s_store, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "accent", 0.45)],
     "narr": ["유니클로 셀프계산대, / 바코드도 안 찍었는데 말이죠."]},
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
    {"draw": s_vs, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "accent", 0.45), (0.6, "accent", 0.45)],
     "narr": ["빛으로 하나씩 비추는 바코드와 달리, / 전파는 옷 속까지 통과하니까요."]},
    {"draw": s_gate, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.6, "accent_low", 0.5), (0.8, "fail", 0.35)],
     "narr": ["같은 원리로, 계산 안 한 물건을 / 출입구에서 잡아내는 매장도 있어요."]},
    {"draw": s_share, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.75, "pop", 0.6)],
     "narr": [K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["옷을 통에 던져 넣기만 했는데, / 가격이 바로 뜬다?"]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover)
