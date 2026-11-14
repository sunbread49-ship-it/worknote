"""지식창고 쇼츠 · 드론 이렇게 만들면 뜨자마자 팽이 됩니다 (2026-11-15 20:00)
  python3 science/drone.py [--stills]
사실 근거 (일반 물리 · 멀티콥터 기본):
  - 프로펠러가 공기를 한 방향으로 돌리면 모터 · 몸통에는 반대 방향 회전력(반작용 토크)이 걸린다 (뉴턴 3법칙)
  - 쿼드콥터는 대각선끼리 같은 방향, 이웃끼리 반대 방향(시계 2 · 반시계 2)으로 돌려 반작용을 서로 상쇄
  - 방향 전환(요): 한 쌍은 빠르게, 다른 쌍은 느리게 → 남는 반작용만큼 몸통이 돈다 (총 양력은 유지)
  - 프로펠러가 하나인 헬리콥터는 꼬리 날개(테일 로터)가 옆으로 밀어 반작용을 막는다
영상 (Pixabay 라이선스): orlandoalan · EliasW98 · Matthias_Groeneveld / 그림: AI 생성 (Gemini)
규칙: 첫 1초 결과 · 3초 질문 · 5초 약속 · 2~3초 컷 · 위쪽 제목 띠 · 큰 한 줄 자막 · Gemini Umbriel 빠르게 1.12배 · 움직이는 영상 배경
"""
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, GOLD, MINT  # noqa: E402

OUT = K.HERE / "out" / "drone"
VID = K.HERE.parent / "youtube" / "assets" / "video"
HEAD = {"kicker": "생활 속 과학", "title": "드론 팽이", "highlight": "팽이",
        "banner": ["드론 이렇게 만들면", "뜨자마자 팽이 됩니다"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}}
CX = W / 2
RED = (255, 72, 72)
BLUE = (80, 160, 255)
DARK = (14, 16, 24)


# ── 배경 ─────────────────────────────────────────────
@lru_cache(maxsize=4)
def _vframes(name, secs=12, ss=0.0):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(ss), "-i", str(VID / f"{name}.mp4"), "-t", str(secs), "-vf",
                          "fps=15,scale=360:640:force_original_aspect_ratio=increase,crop=360:640", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 640, 360, 3)


def vbg(f, name, t, dark=0.5, blur=2, ss=0.0):
    """세로 영상 배경 (핑퐁 재생)"""
    fr = _vframes(name, 12, ss)
    n = len(fr)
    i = int(t * 15) % (2 * n - 2)
    i = i if i < n else 2 * n - 2 - i
    im = Image.fromarray(fr[i]).resize((W, H), Image.BILINEAR)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(im).enhance(1 - dark)
    f.alpha_composite(im.convert("RGBA"))


def pbg(f, name, t, dark=0.35, zoom=0.06, focus=(0.5, 0.5)):
    z = 1 + zoom * G.clamp(t / 3)
    im = K.photo(name, int(W * z), int(H * z), focus, dark)
    f.alpha_composite(im, (int((W - im.width) / 2), int((H - im.height) / 2)))


def big(f, text, y, size=130, hl="", col=CREAM, hlc=GOLD, o=1.0, anchor="mt"):
    im = T(text, size, col, "Black", highlight=hl, hl_fill=hlc, align="center", line_gap=1.08, stroke=9, stroke_fill=(0, 0, 0))
    if im.width > W - 60:
        im = im.resize((W - 60, int(im.height * (W - 60) / im.width)), Image.LANCZOS)
    K.drop(f, im, (CX, y), anchor, o, blur=24, alpha=0.75)


def pop(t, t0=0.0, d=0.25):
    return G.ease_out((t - t0) / d)


def pill(f, text, x, y, t, t0=0.0, bg=GOLD, fg=DARK, size=56, anchor="mm"):
    k = pop(t, t0)
    if k <= 0:
        return
    p = G.pill(text, "Black", size, fg, bg, pad=(30, 12), radius=18)
    G.blit(f, p, (x, y + (1 - k) * 24), k, anchor)


# ── 드론 그림 (위에서 본 X자 쿼드콥터) ─────────────────
def arc_arrow(d, cx, cy, r, a0, a1, col, w=12, cw=True):
    """PIL 각도(3시 = 0, 시계 방향 +). cw면 a1 끝에, 아니면 a0 끝에 화살촉"""
    d.arc((cx - r, cy - r, cx + r, cy + r), a0, a1, fill=col, width=w)
    a = math.radians(a1 if cw else a0)
    px, py = cx + r * math.cos(a), cy + r * math.sin(a)
    tx, ty = (-math.sin(a), math.cos(a)) if cw else (math.sin(a), -math.cos(a))   # 진행 방향
    nx, ny = math.cos(a), math.sin(a)
    s = w * 2.4
    d.polygon([(px + tx * s, py + ty * s), (px + nx * s * 0.8 - tx * s * 0.3, py + ny * s * 0.8 - ty * s * 0.3),
               (px - nx * s * 0.8 - tx * s * 0.3, py - ny * s * 0.8 - ty * s * 0.3)], fill=col)


def drone_img(S, prop, dirs=(1, 1, 1, 1), arrows=True, fast=(1, 1, 1, 1), only=None):
    """S: 한 변 크기. prop: 프로펠러 각도(도). dirs: 로터별 +1 시계 / -1 반시계 (왼위 · 오른위 · 오른아래 · 왼아래)"""
    k = 2
    s = S * k
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    off = s * 0.29
    pos = [(c - off, c - off), (c + off, c - off), (c + off, c + off), (c - off, c + off)]
    # 팔
    for x, y in pos:
        d.line((c, c, x, y), fill=(52, 56, 66, 255), width=int(s * 0.045))
    # 몸통 + 앞쪽 표시
    d.rounded_rectangle((c - s * 0.11, c - s * 0.13, c + s * 0.11, c + s * 0.13), int(s * 0.04), fill=(236, 238, 242, 255),
                        outline=(60, 64, 76, 255), width=int(s * 0.008))
    d.ellipse((c - s * 0.035, c - s * 0.11, c + s * 0.035, c - s * 0.04), fill=(40, 44, 54, 255))
    d.ellipse((c - s * 0.02, c - s * 0.097, c + s * 0.02, c - s * 0.057), fill=(90, 140, 220, 255))
    rr = s * 0.17
    for i, ((x, y), dr) in enumerate(zip(pos, dirs)):
        if only is not None and i not in only:
            continue
        col = RED if dr > 0 else BLUE
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (46,), outline=col + (150,), width=int(s * 0.006))
        d.ellipse((x - s * 0.03, y - s * 0.03, x + s * 0.03, y + s * 0.03), fill=(40, 44, 54, 255))
        a = math.radians(prop * dr * fast[i] + i * 37)
        for b in (0, math.pi):
            ex, ey = math.cos(a + b) * rr * 0.95, math.sin(a + b) * rr * 0.95
            d.line((x, y, x + ex, y + ey), fill=(30, 32, 40, 230), width=int(s * 0.022))
        if arrows:
            r2 = rr * 1.18
            arc_arrow(d, x, y, r2, 200, 320, col + (255,), int(s * 0.016 * (1.25 if fast[i] > 1 else 1)), dr > 0)
    return im.resize((S, S), Image.LANCZOS)


def drone_at(f, x, y, S, body, prop, trail=0, **kw):
    """body: 몸통 회전(도, +는 시계 방향). trail: 잔상 개수"""
    im = drone_img(S, prop, **kw)
    for j in range(trail, 0, -1):
        g = im.rotate(-(body - j * 14), resample=Image.BICUBIC)
        G.blit(f, g, (x, y), 0.18 * (trail - j + 1) / trail, "mm")
    K.drop(f, im.rotate(-body, resample=Image.BICUBIC), (x, y), "mm", 1, blur=22, alpha=0.55)


def body_arrow(f, x, y, r, col, cw, t, t0=0.0, label=None, w=16):
    k = G.clamp((t - t0) / 0.35)
    if k <= 0:
        return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    sweep = 110 * k
    for base in (0, 180):
        if cw:
            arc_arrow(d, x, y, r, base + 200, base + 200 + sweep, col + (255,), w, True)
        else:
            arc_arrow(d, x, y, r, base + 330 - sweep, base + 330, col + (255,), w, False)
    f.alpha_composite(ov)
    if label:
        pill(f, label, x, y + r + 60, t, t0 + 0.2, bg=col, fg=(255, 255, 255) if col == BLUE else DARK, size=50)


def dark_panel(f, y0=60, y1=1240, a=150):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle((40, y0, W - 40, y1), 40, fill=(8, 10, 18, a))
    f.alpha_composite(ov)


def vcredit(f, *names):
    K.credit(f, "영상: " + " · ".join(names) + " (Pixabay)")


# ── 장면 ─────────────────────────────────────────────
def s_hook(f, t, sc):
    """결과 먼저: 첫 프레임부터 드론이 팽이처럼 돎"""
    vbg(f, "drone_fly_v", t, 0.45, 3)
    spin = 120 * t + 260 * t * t   # 점점 빨라짐
    drone_at(f, CX, 760, 700, spin, 2000 * t, trail=4, dirs=(1, 1, 1, 1), arrows=False)
    big(f, "뜨자마자\n팽이?", 60, 150, hl="팽이?")
    vcredit(f, "EliasW98")


def s_promise(f, t, sc):
    pbg(f, "ai_drone_top", t, 0.3, 0.08, (0.6, 0.35))
    big(f, "프로펠러 방향\n딱 하나 실수", 70, 120, hl="딱 하나")
    pill(f, "이유는 30초면 끝", CX, 1100, t, 1.0, size=64)
    K.credit(f, "그림: AI 생성 (Gemini)")


def s_action(f, t, sc):
    """프로펠러 한 개: 공기는 시계 방향 → 몸통은 반시계 방향"""
    vbg(f, "drone_hover_v", t, 0.7, 6)
    big(f, "작용 반작용", 60, 110, hl="반작용")
    L = sc["L"]
    rot = -40 * max(0.0, t - L[-1] - 0.2) ** 1.3
    im = drone_img(700, 1800 * t, dirs=(1, 1, 1, 1), arrows=True, only=(0,))
    K.drop(f, im.rotate(-rot, resample=Image.BICUBIC), (CX, 700), "mm", 1, blur=22, alpha=0.55)
    pill(f, "공기 → 시계 방향", CX, 250, t, 0.3, bg=RED, size=50)
    body_arrow(f, CX, 700, 380, BLUE, False, t, L[-1], label="몸통 ← 반대로")
    vcredit(f, "orlandoalan")


def s_chair(f, t, sc):
    pbg(f, "ai_office_chair", t, 0.25, 0.08, (0.5, 0.4))
    big(f, "회전의자\n실험", 60, 130, hl="회전의자")
    L = sc["L"]
    body_arrow(f, CX - 20, 980, 250, BLUE, False, t, L[-1] if len(L) > 1 else 1.0, label="의자는 반대로 빙글")
    K.credit(f, "그림: AI 생성 (Gemini)")


def s_four(f, t, sc):
    """네 개 모두 시계 방향 → 반작용 × 4 → 몸통이 점점 빠르게 반시계로"""
    vbg(f, "drone_fly_v", t, 0.72, 8)
    L = sc["L"]
    t1 = L[1] if len(L) > 1 else 1.2
    u = max(0.0, t - t1)
    body = -(90 * u + 220 * u * u)
    drone_at(f, CX, 620, 660, body, 1800 * t, trail=3 if u > 0.2 else 0, dirs=(1, 1, 1, 1))
    pill(f, "4개 모두 시계 방향", CX, 120, t, 0.1, bg=RED, size=60)
    if t > t1:
        big(f, "반작용 × 4", 1040, 120, hl="× 4", hlc=BLUE)
    vcredit(f, "EliasW98")


def s_fix(f, t, sc):
    """대각선끼리 짝: 시계 2 · 반시계 2 → 상쇄 → 똑바로"""
    vbg(f, "drone_fly_v", t, 0.55, 3, ss=5.0)
    L = sc["L"]
    wob = 6 * math.sin(t * 9) * max(0.0, 1 - t / 0.8)
    drone_at(f, CX, 620, 700, wob, 1800 * t, dirs=(1, -1, 1, -1))
    pill(f, "대각선끼리 짝!", CX, 110, t, 0.1, size=64)
    if len(L) > 1 and t > L[1]:
        k = pop(t, L[1])
        G.blit(f, T("시계 2  +  반시계 2  =  0", 76, CREAM, "Black", highlight="0", hl_fill=MINT, stroke=7, stroke_fill=(0, 0, 0)),
               (CX, 1060), k, "mm")
    vcredit(f, "EliasW98")


def s_turn(f, t, sc):
    """한 쌍만 빠르게 → 몸통이 반대로 슬쩍 회전 (방향 전환)"""
    vbg(f, "drone_hover_v", t, 0.65, 5, ss=20.0)
    L = sc["L"]
    t1 = L[1] if len(L) > 1 else 1.0
    u = max(0.0, t - t1)
    body = -min(70.0, 55 * u)
    fast = (1.9, 0.7, 1.9, 0.7) if t > t1 else (1, 1, 1, 1)
    drone_at(f, CX, 620, 680, body, 1500 * t, dirs=(1, -1, 1, -1), fast=fast)
    pill(f, "방향 틀기는?", CX, 110, t, 0.1, size=64)
    if t > t1:
        pill(f, "빨간 쌍 빠르게 → 몸통 슬쩍 반대로", CX, 1060, t, t1 + 0.1, bg=CREAM, size=50)
    vcredit(f, "orlandoalan")


def heli_img(S, t):
    """옆에서 본 헬리콥터 (본 로터 + 꼬리 로터 강조)"""
    k = 2
    w, h = int(S * k), int(S * 0.6 * k)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = w / 100
    body = (40, 46, 58, 255)
    d.ellipse((18 * u, 22 * u, 52 * u, 44 * u), fill=body)                      # 몸통
    d.polygon([(46 * u, 28 * u), (88 * u, 31 * u), (88 * u, 34 * u), (46 * u, 40 * u)], fill=body)   # 꼬리
    d.ellipse((21 * u, 25 * u, 33 * u, 35 * u), fill=(120, 180, 230, 255))       # 창
    d.line((34 * u, 22 * u, 34 * u, 16 * u), fill=body, width=int(1.6 * u))
    ph = math.sin(t * 40)
    d.line((34 * u - 30 * u * ph, 15 * u, 34 * u + 30 * u * ph, 15 * u), fill=(30, 32, 40, 255), width=int(1.4 * u))   # 본 로터
    d.line((20 * u, 47 * u, 50 * u, 47 * u), fill=body, width=int(1.2 * u))
    for x in (26, 44):
        d.line((x * u, 43 * u, x * u, 47 * u), fill=body, width=int(1 * u))
    tr = 7 * u                                                                  # 꼬리 로터
    d.ellipse((88 * u - tr, 32 * u - tr, 88 * u + tr, 32 * u + tr), fill=GOLD + (90,), outline=GOLD + (255,), width=int(0.5 * u))
    a = t * 50
    d.line((88 * u + tr * math.cos(a), 32 * u + tr * math.sin(a), 88 * u - tr * math.cos(a), 32 * u - tr * math.sin(a)),
           fill=(30, 32, 40, 255), width=int(0.9 * u))
    return im.resize((w // k, h // k), Image.LANCZOS)


def s_heli(f, t, sc):
    vbg(f, "heli_v", t, 0.35, 0)
    L = sc["L"]
    pill(f, "프로펠러가 하나면?", CX, 110, t, 0.1, size=64)
    if len(L) > 1 and t > L[1] - 0.2:
        dark_panel(f, 640, 1220, 170)
        hi = heli_img(900, t)
        K.drop(f, hi, (CX - 30, 930), "mm", pop(t, L[1] - 0.2), blur=18)
        pill(f, "꼬리 날개가 옆으로 밀어서 버팀", CX, 700, t, L[1], bg=GOLD, size=50)
    vcredit(f, "Matthias_Groeneveld")


def s_cta(f, t, sc):
    vbg(f, "drone_fly_v", t, 0.55, 3, ss=8.0)
    big(f, "다음에 드론 보면\n프로펠러 방향 체크!", 120, 108, hl="방향 체크!")
    pill(f, "좋아요 누르고 친구한테도 물어보세요", CX, 1060, t, 0.4, size=50)
    vcredit(f, "EliasW98")


def draw_cover(f):
    s_hook(f, 1.6, {"L": [0]})


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1,
     "sfx_t": [(0.0, "whoosh", 0.5), (0.5, "flyby", 0.45), (1.6, "accent", 0.45)],
     "narr": ["드론을 이렇게 만들면, / 뜨자마자 팽이처럼 돌아요."]},
    {"draw": s_promise, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(1.0, "ding", 0.5)],
     "narr": ["프로펠러를 전부 같은 방향으로 돌렸을 뿐인데요? 이유는 30초면 끝나요."]},
    {"draw": s_action, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.2, "glide", 0.45), (sc["L"][-1], "accent_low", 0.5)],
     "narr": ["프로펠러가 공기를 한쪽으로 돌리면,", "몸통은 반대쪽으로 밀려요."]},
    {"draw": s_chair, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.2,
     "sfx_fn": lambda sc: [(sc["L"][-1], "whoosh", 0.4)],
     "narr": ["회전의자에 앉아 바퀴를 돌리면,", "의자가 반대로 도는 것처럼요."]},
    {"draw": s_four, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.3,
     "sfx_fn": lambda sc: [(sc["L"][1], "riser", 0.45), (sc["L"][-1] + 0.4, "fail", 0.35)],
     "narr": ["네 개가 다 같은 방향이면,", "반작용이 네 배로 쌓여서 빙글빙글."]},
    {"draw": s_fix, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.1, "pop", 0.5), (sc["L"][1], "sparkle", 0.5)],
     "narr": ["그래서 진짜 드론은 대각선끼리 짝을 지어 반대로 돌려요.", "반작용이 서로 지워지죠."]},
    {"draw": s_turn, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.1, "pop", 0.5), (sc["L"][1], "zip", 0.45)],
     "narr": ["방향을 틀고 싶을 땐?", "한 쌍만 살짝 더 빨리 돌리면 끝."]},
    {"draw": s_heli, "flash": True, "nohead": True, "min": 2.6, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.1, "accent", 0.4), (sc["L"][1], "reveal", 0.5)],
     "narr": ["그럼 프로펠러가 하나인 헬리콥터는?", "꼬리 날개가 반작용을 막아요."]},
    {"draw": s_cta, "flash": True, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.75, "pop", 0.6)],
     "narr": [K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15,
     "narr": ["드론을 이렇게 만들면, / 뜨자마자 팽이처럼 돌아요."]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "drive"), (5, "hope")])
