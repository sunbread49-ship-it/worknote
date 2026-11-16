"""지식창고 쇼츠 · 비밀번호 이렇게 만들면 0.1초 만에 털린다 (2026-11-17 20:00)
  python3 science/password.py [--stills]
트렌드: 구글 트렌드 한국 '보안' 500+ (11.16 · 금융보안원 해킹 공격 IP 차단 보도)
계산 (유출된 비밀번호를 컴퓨터로 하나씩 대입한다고 가정 · 1초에 1,000억 번 = 최신 그래픽카드 한 장 수준의 빠른 해시 기준, 어림):
  숫자 8자리(생일) 10^8 = 1억 → 0.001초 · 영어 소문자 8자리 26^8 ≈ 2,088억 → 약 2초
  대소문자+숫자 8자리 62^8 ≈ 218조 → 약 36분 · +특수문자(94종) 8자리 94^8 ≈ 6,096조 → 약 17시간
  영어 소문자 16자리 26^16 ≈ 4.4×10^22 → 약 1만 3,800년  ⇒ 특수문자보다 '길이'가 세다
  생일 · 이름 · 흔한 단어는 해커가 가장 먼저 넣어 보는 목록(사전 공격) — 실제론 더 빨리 털림
규칙(2026-11-15~16 사용자): 내용 자체를 영상으로 · 중하단 큰 멘트(장면은 y 780~960 비움) · 실사 · 3D · '친구한테 아는 척' · 발음
"""
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shortkit as K  # noqa: E402
from shortkit import G, T, W, H, CREAM, GOLD, MINT  # noqa: E402
from drone import vbg, big, pop, pill  # noqa: E402

OUT = K.HERE / "out" / "password"
MEDIA = K.HERE.parent / "youtube" / "assets" / "media"
HEAD = {"kicker": "생활 속 과학", "title": "비밀번호", "highlight": "비밀번호",
        "banner": ["비밀번호 이렇게 만들면", "0.1초 만에 털린다"]}
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}}
CX = W / 2
RED = (240, 70, 70)
GREEN = (60, 210, 120)
DARK = (14, 16, 24)


def credit(f, text):
    K.credit(f, text)


# ── 내용이 곧 영상: 휴대폰 잠금 화면 ─────────────────────────────
def phone_unlock(f, t, code, t0=0.15, per=0.12, y=120, label="생일 8자리"):
    pw, ph = 620, 700
    ph_im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(ph_im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), 60, fill=(20, 22, 30, 255))
    d.rounded_rectangle((16, 16, pw - 17, ph - 17), 48, fill=(240, 242, 248, 255))
    n = len(code)
    typed = max(0, min(n, int((t - t0) / per) + 1)) if t >= t0 else 0
    done = typed >= n and t > t0 + n * per + 0.15
    ph_im.alpha_composite(T("잠금 해제" if not done else "잠금 풀림!", 40, (40, 42, 52) if not done else (30, 150, 80), "Black"), (60, 70))
    ph_im.alpha_composite(T(label, 30, (120, 124, 140), "Bold"), (60, 130))
    box = Image.new("RGBA", (pw - 120, 110), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, pw - 121, 109), 22, fill=(255, 255, 255, 255), outline=(200, 204, 214, 255), width=3)
    tx = T(code[:typed] + ("|" if not done and int(t * 4) % 2 else ""), 64, (20, 22, 30), "Black")
    box.alpha_composite(tx, (30, 20))
    ph_im.alpha_composite(box, (60, 190))
    # 키패드
    for i in range(12):
        r, c = divmod(i, 3)
        kx, ky = 70 + c * 165, 340 + r * 86
        hit = typed > 0 and not done and str((i + 1) % 10) == code[typed - 1] and int((t - t0) / per) < n
        ImageDraw.Draw(ph_im).rounded_rectangle((kx, ky, kx + 140, ky + 70), 18, fill=(255, 214, 90, 255) if hit else (226, 230, 238, 255))
        lab = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"][i]
        lt = T(lab, 40, (40, 42, 52), "Bold")
        ph_im.alpha_composite(lt, (kx + 70 - lt.width // 2, ky + 12))
    K.drop(f, ph_im, (CX, y), "mt", 1, blur=26, alpha=0.6)
    return done


def s_hook(f, t, sc):
    vbg(f, "typing_hands_v", t, 0.5, 4)
    done = phone_unlock(f, t, "19960513", t0=0.0, per=0.07, y=60)
    if done:
        k = pop(t, 0.75)
        G.blit(f, G.pill("털리는 데 0.001초", "Black", 70, DARK, RED, pad=(30, 14), radius=20), (CX, 1040), k, "mt")
    credit(f, "영상: Coverr-Free-Footage (Pixabay)")


def s_question(f, t, sc):
    vbg(f, "binary_v", t, 0.55, 2)
    big(f, "그럼 몇 자리여야\n안 털릴까?", 120, 120, hl="안 털릴까?", hlc=MINT)
    pill(f, "30초면 계산 끝", CX, 560, t, 0.5, bg=GOLD, size=70)
    credit(f, "영상: geralt (Pixabay)")


def s_speed(f, t, sc):
    """1초에 1,000억 번: 숫자가 미친 듯이 바뀌는 카운터"""
    vbg(f, "code_screen_v", t, 0.55, 2)
    big(f, "그래픽카드 한 장이\n1초에 대입하는 횟수", 80, 80)
    n = int(1e11 * min(1.0, t / 1.6))
    rnd = np.random.default_rng(int(t * 30))
    guess = "".join(rnd.choice(list("abcdefghijklmnopqrstuvwxyz0123456789"), 8))
    G.blit(f, T(guess, 64, (120, 255, 160), "Bold"), (CX, 330), 0.9, "mt")
    G.blit(f, T(f"{n:,}", 110, GOLD, "Black", stroke=7, stroke_fill=(0, 0, 0)), (CX, 440), 1, "mt")
    G.blit(f, T("번", 60, CREAM, "Black"), (CX, 600), pop(t, 1.6), "mt")
    credit(f, "영상: choschos (Pixabay) · 1,000억 번은 어림값(빠른 해시 기준)")


ROWS = [("생일 8자리", "19960513", 1e-3, "0.001초", RED),
        ("영어 소문자 8자리", "monkeyhi", 2.09, "2초", RED),
        ("대소문자 + 숫자 8자리", "Monkey1h", 2183, "36분", (255, 160, 60)),
        ("+ 특수문자 8자리", "Mon!ey1h", 60960, "17시간", GOLD)]


def s_ladder(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 24, 255)))
    vbg(f, "binary_v", t, 0.85, 6)
    big(f, "털리는 데 걸리는 시간", 50, 74)
    L = sc["L"]
    for i, (lab, ex, sec, txt, col) in enumerate(ROWS):
        t0 = (0.1 + i * 0.5) if i < 2 else (L[1] if len(L) > 1 else 1.6) + (i - 2) * 0.6
        k = pop(t, t0, 0.4)
        if k <= 0:
            continue
        y = 170 + i * 150
        G.blit(f, T(lab, 52, CREAM, "Black"), (70, y), k, "lt")
        G.blit(f, T(ex, 38, (150, 160, 190), "Bold"), (W - 70, y + 8), k, "rt")
        g = G.clamp((t - t0) / 0.8)
        w = int((W - 420) * (math.log10(sec * 1e4) / math.log10(60960 * 1e4)) * g)
        ImageDraw.Draw(f).rounded_rectangle((70, y + 70, 70 + max(10, w), y + 120), 14, fill=col + (255,))
        G.blit(f, T(txt, 60, col, "Black", stroke=5, stroke_fill=(0, 0, 0)), (90 + max(10, w), y + 95), min(1, g * 2), "lm")


@lru_cache(maxsize=1)
def _lock_frames():
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(MEDIA / "locks_pw.mp4"), "-vf", "fps=30,scale=1080:698",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 698, 1080, 3)


def s_locks(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 24, 255)))
    fr = _lock_frames()
    i = min(int(t * 30 * 0.9), len(fr) - 1)
    f.alpha_composite(Image.fromarray(fr[i]).convert("RGBA"), (0, 60))
    G.blit(f, G.pill("4자리", "Black", 46, DARK, CREAM, pad=(20, 8), radius=14), (W * 0.3, 40), 1, "mt")
    G.blit(f, G.pill("16자리", "Black", 46, DARK, GOLD, pad=(20, 8), radius=14), (W * 0.68, 40), 1, "mt")
    L = sc["L"]
    if len(L) > 1 and t > L[1]:
        G.blit(f, T("1만 3천 년", 110, GOLD, "Black", stroke=7, stroke_fill=(0, 0, 0)), (W * 0.68, 700), pop(t, L[1]), "mt")
    credit(f, "3D: Blender로 직접 제작")


def s_power(f, t, sc):
    """한 자리 늘 때마다 ×26 — 곱이 눈덩이처럼"""
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 24, 255)))
    vbg(f, "code_screen_v", t, 0.82, 6)
    big(f, "한 자리 늘 때마다", 30, 80)
    steps = [("8자리", "2,088억"), ("10자리", "141조"), ("12자리", "9경"), ("14자리", "6,450경"), ("16자리", "436해")]
    for i, (a, b) in enumerate(steps):
        k = pop(t, 0.3 + i * 0.35, 0.3)
        if k <= 0:
            continue
        y = 260 + i * 104
        sz = 50 + i * 8
        G.blit(f, T(a, 44, CREAM, "Bold"), (90, y + 10), k, "lt")
        G.blit(f, T(b, sz, GOLD if i == 4 else CREAM, "Black", stroke=5, stroke_fill=(0, 0, 0)), (W - 90, y), k, "rt")
    G.blit(f, G.pill("× 26 × 26 …", "Black", 54, DARK, MINT, pad=(24, 10), radius=16), (CX, 150), pop(t, 0.1), "mt")


def s_tip(f, t, sc):
    vbg(f, "typing_hands_v", t, 0.55, 4)
    pill(f, "꿀팁", CX, 60, t, 0.05, bg=GOLD, size=70)
    sent = "내비밀번호아무도모르겠지"
    n = min(len(sent), max(0, int((t - 0.3) / 0.11)))
    box = Image.new("RGBA", (W - 120, 150), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, W - 121, 149), 26, fill=(255, 255, 255, 245))
    box.alpha_composite(T(sent[:n] + ("|" if int(t * 4) % 2 else ""), 66, (20, 22, 30), "Black"), (34, 36))
    K.drop(f, box, (CX, 200), "mt", 1, blur=18)
    if n >= len(sent):
        G.blit(f, T("영문 자판으로 치면 25자리 넘게", 54, MINT, "Black", stroke=5, stroke_fill=(0, 0, 0)), (CX, 400), pop(t, 0.3 + len(sent) * 0.11), "mt")
    G.blit(f, T("✗ 생일 · 이름 · 흔한 단어", 52, RED, "Black", stroke=5, stroke_fill=(0, 0, 0)), (CX, 540), pop(t, 1.8), "mt")
    credit(f, "영상: Coverr-Free-Footage (Pixabay)")


def s_cta(f, t, sc):
    vbg(f, "binary_v", t, 0.6, 3)
    big(f, "내 비밀번호는\n몇 자리?", 120, 140, hl="몇 자리?")
    pill(f, "좋아요 누르고 친구한테 아는 척!", CX, 560, t, 0.4, size=52)
    credit(f, "영상: geralt (Pixabay)")


def draw_cover(f):
    vbg(f, "typing_hands_v", 2.0, 0.5, 4)
    phone_unlock(f, 2.0, "19960513", t0=0.0, per=0.07, y=60)
    G.blit(f, G.pill("털리는 데 0.001초", "Black", 70, DARK, RED, pad=(30, 14), radius=20), (CX, 1040), 1, "mt")


SCENES = [
    {"draw": s_hook, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.0 + 0.07 * i, "tick", 0.35) for i in range(8)] + [(0.75, "accent", 0.6)],
     "narr": ["생일로 만든 비밀번호, / 털리는 데 0.001초예요."]},
    {"draw": s_question, "flash": True, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.5, "ding", 0.5)],
     "narr": ["그럼 어떻게 만들어야 안 털릴까요? / 30초면 계산 끝나요."]},
    {"draw": s_speed, "flash": True, "nohead": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "count_roll", 0.45)],
     "narr": ["요즘 그래픽카드 한 장이면, / 1초에 1,000억 번 넘게 대입해 볼 수 있거든요."]},
    {"draw": s_ladder, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.25,
     "sfx_fn": lambda sc: [(0.1, "pop", 0.45), (0.6, "pop", 0.45), (sc["L"][1], "pop", 0.45), (sc["L"][1] + 0.6, "pop", 0.45)],
     "narr": ["숫자 8자리는 0.001초, / 영어 소문자 8자리는 2초.", "대문자랑 숫자를 섞으면 36분, / 특수문자까지 넣어도 17시간이에요."]},
    {"draw": s_locks, "flash": True, "nohead": True, "min": 3.4, "gap": 0.1, "tail": 0.3,
     "sfx_fn": lambda sc: [(1.4, "ding", 0.5), (sc["L"][1], "reveal", 0.55)],
     "narr": ["그런데 반전. / 특수문자보다 센 게 있어요. 바로 길이예요.", "영어 소문자만 써도 16자리면, / 1만 3천 년이 걸려요."]},
    {"draw": s_power, "flash": True, "nohead": True, "min": 2.8, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.3 + 0.35 * i, "tick", 0.45) for i in range(5)],
     "narr": ["한 자리 늘 때마다, / 경우의 수가 26배씩 곱해지거든요."]},
    {"draw": s_tip, "flash": True, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.3 + 0.11 * i, "tick", 0.3) for i in range(12)],
     "narr": ["그러니까 나만 아는 문장을 길게. / 생일이나 이름은, / 해커가 제일 먼저 넣어 보니까 빼고요."]},
    {"draw": s_cta, "flash": True, "nohead": True, "min": 2.0, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.05, "pop", 0.6), (0.45, "pop", 0.6)],
     "narr": [K.CTA]},
    {"draw": s_hook, "nohead": True, "min": 1.8, "gap": 0.1, "tail": 0.15,
     "narr": ["생일로 만든 비밀번호, / 털리는 데 0.001초예요."]},
]

if __name__ == "__main__":
    K.run(SCENES, HEAD, OUT, SAY, cover=draw_cover, bgm_cues=[(0, "tense"), (4, "drive"), (6, "hope")])
