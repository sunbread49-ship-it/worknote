"""새 채널 테스트 쇼츠 #1 · 최단강하선 (1080x1920, 30fps)
  python3 science/brachistochrone.py            # 전체 렌더 → science/out/brachistochrone/short.mp4
  python3 science/brachistochrone.py --stills   # 장면별 정지 화면만
물리값은 science/physics.py 로 계산(마찰 없음, R=1m → 높이 2m, 가로 3.14m)
"""
import argparse
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "youtube"))
sys.path.insert(0, str(HERE))
from engine import draw as G          # noqa: E402
from engine import sfx as SFX         # noqa: E402
from engine import tts as TTS         # noqa: E402
import physics as P                   # noqa: E402

W, H, FPS = 1080, 1920, 30
OUT = HERE / "out" / "brachistochrone"
VOICE, RATE = "ko-KR-Chirp3-HD-Sadaltager", 1.12
SAY = {"2미터면": "이미터면", "둥근 길": "둥근길"}  # 붙여 읽기 (피드백)

# ── 새 채널 팔레트 (주식 채널과 다르게: 잉크 남색 모눈종이 + 코랄 · 바이올렛 · 블루) ──
BG1, BG2 = (14, 18, 34), (6, 8, 16)
CREAM = (244, 236, 220)
DIM = (150, 160, 190)
CORAL = (255, 112, 88)
VIOLET = (186, 140, 255)
BLUE = (96, 168, 255)
MINT = (120, 230, 190)

# 애니메이션 좌표: 물리 (x∈[0,π], y∈[-2,0]) → 화면
SX = 290.0
OX, OY = (W - math.pi * SX) / 2, 560


def to_px(x, y, s=SX, ox=None, oy=None):
    return (OX if ox is None else ox) + x * s, (OY if oy is None else oy) - y * s


# ── 경로 + 시간 ──────────────────────────────────────────────────
PATHS = []
for name, color, (x, y) in (("직선", BLUE, P.line()), ("원호", VIOLET, P.arc()), ("사이클로이드", CORAL, P.cycloid())):
    PATHS.append({"name": name, "color": color, "x": x, "y": y, "t": P.times(x, y)})
SLOW = 3.2  # 실제 1초 → 영상 3.2초


def pos_at(p, tt):
    tt = min(tt, p["t"][-1])
    return np.interp(tt, p["t"], p["x"]), np.interp(tt, p["t"], p["y"])


def speed_at(p, tt):
    _, y = pos_at(p, tt)
    return math.sqrt(2 * P.G * max(0.0, -y))


# ── 배경 ────────────────────────────────────────────────────────
def _bg():
    y = np.linspace(0, 1, H)[:, None, None]
    a = np.array(BG1) * (1 - y) + np.array(BG2) * y
    a = np.broadcast_to(a, (H, W, 3)).astype(np.uint8)
    im = Image.fromarray(a, "RGB").convert("RGBA")
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)
    for gx in range(0, W, 60):
        d.line((gx, 0, gx, H), fill=(255, 255, 255, 14))
    for gy in range(0, H, 60):
        d.line((0, gy, W, gy), fill=(255, 255, 255, 14))
    im.alpha_composite(grid)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W * 0.1, 500, W * 0.9, 1300), fill=(60, 80, 160, 60))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    return im


BG = _bg()


def T(text, size, color=CREAM, weight="Black", **kw):
    return G.text_img(text, weight, size, color, **kw)


def header(f):
    k = T("1696년, 수학자들의 난제", 40, MINT, "ExtraBold")
    G.blit(f, k, (W / 2, 140), 1, "mt")
    t = T("직선이 가장\n빠른 길일까?", 104, CREAM, "Black", highlight="빠른 길일까?", hl_fill=CORAL, align="center", line_gap=1.12)
    G.blit(f, t, (W / 2, 195), 1, "mt")


def thick_line(d, pts, color, width, k=2):
    d.line([(x * k, y * k) for x, y in pts], fill=color, width=width * k, joint="curve")


def draw_paths(f, prog=1.0, which=(0, 1, 2), alpha=255, labels=True):
    k = 2
    lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in which:
        p = PATHS[i]
        n = max(2, int(len(p["x"]) * prog))
        pts = [to_px(x, y) for x, y in zip(p["x"][:n:8], p["y"][:n:8])]
        thick_line(d, pts, p["color"] + (alpha,), 7)
    lay = lay.resize((W, H), Image.LANCZOS)
    f.alpha_composite(G.with_opacity(lay.filter(ImageFilter.GaussianBlur(8)), 0.55))
    f.alpha_composite(lay)
    if not labels:
        return
    # 출발점 · 도착점
    ax, ay = to_px(0, 0)
    bx, by = to_px(math.pi, -2)
    d2 = ImageDraw.Draw(f, "RGBA")
    d2.line((ax - 40, ay, ax + 40, ay), fill=CREAM + (200,), width=4)
    d2.line((bx - 50, by + 26, bx + 50, by + 26), fill=CREAM + (200,), width=4)
    G.blit(f, T("출발", 42, CREAM, "ExtraBold"), (ax + 10, ay - 60), 1, "mb")
    G.blit(f, T("도착", 42, CREAM, "ExtraBold"), (bx, by + 40), 1, "mt")
    if labels:
        for i, (fr, dx, dy) in zip(which, ((0.62, 40, -42), (0.42, 0, 46), (0.58, -10, -44))):
            p = PATHS[i]
            j = int(fr * (len(p["x"]) - 1))
            px, py = to_px(p["x"][j], p["y"][j])
            px, py = px + dx, py + dy
            G.blit(f, G.pill(p["name"], "ExtraBold", 40, BG2, p["color"], pad=(20, 8), radius=22), (px, py), min(1, prog * 1.5), "mm")


def ball(f, x, y, color, r=22, s=SX, ox=None, oy=None, trail=None):
    px, py = to_px(x, y, s, ox, oy)
    if trail:
        for j, (tx, ty) in enumerate(trail):
            qx, qy = to_px(tx, ty, s, ox, oy)
            a = int(110 * (j + 1) / len(trail))
            rr = r * (0.4 + 0.5 * (j + 1) / len(trail))
            ImageDraw.Draw(f, "RGBA").ellipse((qx - rr, qy - rr, qx + rr, qy + rr), fill=color + (a,))
    k = 3
    im = Image.new("RGBA", (int(r * 2 * k) + 6, int(r * 2 * k) + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((3, 3, 3 + r * 2 * k, 3 + r * 2 * k), fill=color + (255,), outline=CREAM + (255,), width=3 * k)
    d.ellipse((r * 0.5 * k, r * 0.4 * k, r * 1.0 * k, r * 0.9 * k), fill=(255, 255, 255, 170))
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    G.blit(f, im, (px, py - r * 0.95), 1, "mm")


def race_frame(f, tt, trails=True):
    """tt: 실제 물리 시간(초)"""
    draw_paths(f, labels=True)
    winner = None
    for i, p in enumerate(PATHS):
        tr = [pos_at(p, max(0, tt - j * 0.035)) for j in range(6, 0, -1)] if trails and tt > 0 else None
        x, y = pos_at(p, tt)
        ball(f, x, y, p["color"], trail=tr)
        if tt >= p["t"][-1] and winner is None:
            winner = i
    return winner


def finish_badges(f, tt):
    bx, by = to_px(math.pi, -2)
    order = sorted(range(3), key=lambda i: PATHS[i]["t"][-1])
    for rank, i in enumerate(order):
        p = PATHS[i]
        if tt >= p["t"][-1]:
            o = G.appear(tt, p["t"][-1], 0.08)
            lab = G.pill(f"{rank + 1}등", "Black", 40, BG2, p["color"], pad=(14, 6), radius=8)
            G.blit(f, lab, (bx - 60, by - 250 + rank * 66), o, "lm")


# ── 장면 ────────────────────────────────────────────────────────
# 각 장면: narration(문장 목록), min(최소 길이), draw(f, t, sc)
def s_hook(f, t, sc):
    prog = G.ease_out(t / 2.2)
    draw_paths(f, prog)
    for p in PATHS:
        ball(f, 0, 0, p["color"])
    if t > sc["L"][1] if len(sc["L"]) > 1 else False:
        q = T("?", 260, CORAL, "Black")
        G.blit(f, q, (W - 150, 930 + math.sin(t * 4) * 8), G.appear(t, sc["L"][1], 0.3), "mm")


def s_race(f, t, sc):
    t0 = sc["L"][0] + 0.6
    tt = max(0.0, (t - t0) / SLOW)
    race_frame(f, tt)
    finish_badges(f, tt)
    clock = T(f"{tt:0.2f}초", 52, CREAM, "Black")
    G.blit(f, clock, (W - 70, 560), 1, "rt")
    G.blit(f, T("슬로 모션 ×3", 32, DIM, "SemiBold"), (W - 70, 620), 1, "rt")


def s_times(f, t, sc):
    race_frame(f, 9.0, trails=False)
    order = sorted(range(3), key=lambda i: PATHS[i]["t"][-1])
    y = 1215
    G.blit(f, T("높이 2m · 가로 3.14m · 마찰 없음", 32, DIM, "SemiBold"), (110, y - 50), G.appear(t, 0.1))
    for rank, i in enumerate(order):
        p = PATHS[i]
        o = G.ease_out((t - 0.2 - rank * 0.35) / 0.4)
        if o <= 0:
            continue
        bw = int(560 * (p["t"][-1] / 1.25) * o)
        bw = int(bw * 0.68)
        G.blit(f, T(f"{rank + 1}. {p['name']}", 42, p["color"], "ExtraBold"), (110, y), o)
        bar = Image.new("RGBA", (max(4, bw), 30), p["color"] + (255,))
        G.blit(f, bar, (440, y + 12), o)
        G.blit(f, T(f"{p['t'][-1]:.2f}초", 44, CREAM, "Black"), (440 + bw + 16, y + 2), o)
        y += 60


def s_why(f, t, sc):
    tt = (t % 4.2) / SLOW * 1.0 if t > 0.3 else 0
    tt = min(tt, 1.2)
    race_frame(f, tt, trails=True)
    y = 1190
    for i in (2, 0):
        p = PATHS[i]
        v = speed_at(p, tt)
        G.blit(f, T(p["name"], 42, p["color"], "ExtraBold"), (110, y))
        bw = int(v / 6.3 * 440)
        G.blit(f, Image.new("RGBA", (max(4, bw), 30), p["color"] + (255,)), (440, y + 12))
        G.blit(f, T(f"{v * 3.6:0.0f}km/h", 42, CREAM, "Black"), (440 + bw + 14, y + 2))
        y += 66
    G.blit(f, T("속도", 32, DIM, "SemiBold"), (110, 1140))
    # 출발 직후 '가파른 낙하' 강조
    if t > sc["L"][0] + 0.3:
        o = G.appear(t, sc["L"][0] + 0.3, 0.3)
        px, py = to_px(0.25, -0.55)
        d = ImageDraw.Draw(f, "RGBA")
        r = 95
        d.ellipse((px - r, py - r, px + r, py + r), outline=MINT + (int(230 * o),), width=6)
        G.blit(f, G.pill("가파른 출발", "ExtraBold", 40, BG2, MINT, pad=(20, 8), radius=22), (px + 120, py - 90), o, "lm")


def s_wheel(f, t, sc):
    th = min(0.82 * math.pi, max(0.0, (t - 0.3) / 3.0 * 0.82 * math.pi))
    R = 1.0
    ax, ay = to_px(0, 0)
    d = ImageDraw.Draw(f, "RGBA")
    d.line((OX - 40, ay, OX + math.pi * SX + 80, ay), fill=CREAM + (210,), width=5)  # 천장 레일
    # 지나간 자국
    x, y = P.cycloid(R, 0, max(th, 1e-3), 600)
    k = 2
    lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    thick_line(ImageDraw.Draw(lay), [to_px(a, b) for a, b in zip(x[::4], y[::4])], CORAL + (255,), 7)
    f.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    cx, cy = to_px(R * th, -R)
    rr = R * SX
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=BLUE + (230,), width=6)
    for a in np.linspace(0, 2 * math.pi, 8, endpoint=False):
        ang = a - th
        d.line((cx, cy, cx + rr * math.sin(ang), cy - rr * math.cos(ang) * -1), fill=BLUE + (90,), width=3)
    px, py = to_px(R * (th - math.sin(th)), -R * (1 - math.cos(th)))
    d.line((cx, cy, px, py), fill=CORAL + (255,), width=5)
    d.ellipse((px - 16, py - 16, px + 16, py + 16), fill=CORAL + (255,), outline=CREAM + (255,), width=4)
    if t > sc["L"][-1]:
        o = G.appear(t, sc["L"][-1], 0.4)
        G.blit(f, T("사이클로이드", 72, CORAL, "Black"), (W / 2, 1170), o, "mt")
        G.blit(f, T("x = R(θ − sin θ),  y = −R(1 − cos θ)", 40, DIM, "SemiBold"), (W / 2, 1265), o, "mt")


def _card(name, role, year, color, w=860, h=170):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=24, fill=(24, 30, 54, 240), outline=color + (255,), width=4)
    d.ellipse((30, 30, 140, 140), fill=color + (255,))
    ini = T(name[0], 60, BG2, "Black")
    im.alpha_composite(ini, (85 - ini.width // 2, 85 - ini.height // 2))
    im.alpha_composite(T(name, 46, CREAM, "Black"), (170, 30))
    im.alpha_composite(T(role, 32, DIM, "SemiBold"), (170, 100))
    yt = T(year, 40, color, "Black")
    im.alpha_composite(yt, (w - 40 - yt.width, 40))
    return im


def s_history(f, t, sc):
    draw_paths(f, which=(2,), alpha=120, labels=False)
    L = sc["L"]
    G.blit(f, _card("요한 베르누이", "공개 문제를 냄 · 스위스 수학자", "1696", MINT), (W / 2, 640), G.appear(t, L[0], 0.35), "mm")
    G.blit(f, _card("아이작 뉴턴", "하룻밤 만에 풀어 이름 없이 보냄", "1697", CORAL), (W / 2, 840), G.appear(t, L[1] if len(L) > 1 else 2, 0.35), "mm")
    if len(L) > 2 and t > L[2]:
        o = G.appear(t, L[2], 0.4)
        G.blit(f, T("“tanquam ex ungue leonem”", 42, DIM, "SemiBold"), (W / 2, 1000), o, "mt")
        G.blit(f, T("발톱만 봐도 사자를 알겠다", 62, CREAM, "Black", highlight="사자", hl_fill=CORAL), (W / 2, 1065), o, "mt")


TAU_STARTS = (0.25, 0.9, 1.55, 2.2)
TAU_COLORS = (CORAL, (255, 170, 90), MINT, BLUE)
TS, TOX, TOY = 150.0, (W - 2 * math.pi * 150) / 2, 680


def s_tauto(f, t, sc):
    # 사이클로이드 그릇(θ 0~2π) · 왼쪽 여러 높이에서 동시에 출발 → 바닥에 동시 도착
    x, y = P.cycloid(1.0, 0, 2 * math.pi, 800)
    k = 2
    lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    thick_line(ImageDraw.Draw(lay), [to_px(a, b, TS, TOX, TOY) for a, b in zip(x[::4], y[::4])], CREAM + (220,), 6)
    f.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    bx, by = to_px(math.pi, -2, TS, TOX, TOY)
    ImageDraw.Draw(f, "RGBA").line((bx, by + 10, bx, by + 60), fill=MINT + (200,), width=4)
    G.blit(f, T("바닥", 40, MINT, "ExtraBold"), (bx, by + 66), 1, "mt")
    t0 = sc["L"][0] + 0.8
    tt = max(0.0, (t - t0) / SLOW)
    arrived = False
    for th0, col in zip(TAU_STARTS, TAU_COLORS):
        cx, cy = P.cycloid(1.0, th0, math.pi, 3000)
        tm = P.times(cx, cy)
        u = min(tt, tm[-1])
        px, py = np.interp(u, tm, cx), np.interp(u, tm, cy)
        ball(f, px, py, col, r=20, s=TS, ox=TOX, oy=TOY)
        arrived = tt >= tm[-1]
    G.blit(f, T(f"{tt:0.2f}초", 52, CREAM, "Black"), (W - 110, 1080), 1, "rt")
    if arrived:
        o = G.appear(tt, 1.0029, 0.1)
        G.blit(f, G.pill("4개 모두 동시 도착!", "Black", 52, BG2, MINT, pad=(30, 14), radius=40), (W / 2, 1170), o, "mt")


def s_end(f, t, sc):
    x, y = P.cycloid(1.0, 0, math.pi, 600)
    k = 2
    lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    thick_line(ImageDraw.Draw(lay), [to_px(a, b) for a, b in zip(x[::4], y[::4])], CORAL + (255,), 7)
    f.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    G.blit(f, T("가장 빠른 길은\n가장 짧은 길이 아니었다", 64, CREAM, "Black", highlight="가장 짧은 길", hl_fill=CORAL, align="center", line_gap=1.2),
           (W / 2, 1170), G.appear(t, 0.1, 0.4), "mt")


SCENES = [
    {"draw": s_hook, "min": 3.5, "narr": ["같은 높이에서, 공 세 개를 동시에 놓습니다.",
                                         "직선, 둥근 길, 그리고 이상하게 휜 길. | 어느 공이 가장 먼저 도착할까요?"]},
    {"draw": s_race, "min": 5.2, "sfx": [(0.6, "pop", 0.4)], "narr": ["가장 짧은 건 당연히 직선이죠.", "그런데 1등은, 이 휜 길입니다."]},
    {"draw": s_times, "min": 3.0, "narr": ["높이 2미터면, 휜 길은 1초. | 둥근 길은 1.03초. | 직선은 1.19초예요."]},
    {"draw": s_why, "min": 4.2, "narr": ["비밀은 출발에 있어요. | 처음에 가파르게 떨어지면서 속도를 먼저 붙이고,", "그 빠른 속도로 남은 길을 달려 나가는 거죠."]},
    {"draw": s_wheel, "min": 4.0, "narr": ["이 곡선의 이름은 사이클로이드.", "굴러가는 바퀴 위의 한 점이 그리는 곡선이에요."]},
    {"draw": s_history, "min": 3.0, "narr": ["1696년, 요한 베르누이가 이 문제를 공개적으로 냈는데,",
                                            "뉴턴이 하룻밤 만에 풀어서, 이름도 없이 답을 보냈다고 해요.",
                                            "베르누이는 답을 보자마자 말했죠. | 발톱만 봐도 사자를 알겠다."]},
    {"draw": s_tauto, "min": 5.5, "narr": ["더 놀라운 건, 이 곡선 위라면 어디서 놓아도, | 바닥까지 걸리는 시간이 똑같다는 거예요."]},
    {"draw": s_end, "min": 2.5, "narr": ["가장 빠른 길은, 가장 짧은 길이 아니었던 거죠.", "더 재밌고 신기한 지식은, 채널 구독하고 우리 함께 봐요!"]},
]


# ── 음성 · 타이밍 ────────────────────────────────────────────────
def pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    nz = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0] - 480):nz[-1] + 2400] if len(nz) else a


def plan():
    cache = OUT / "tts_cache"
    t, clips, cues = 0.0, [], []
    for sc in SCENES:
        sc["start"], cur, sc["L"] = t, 0.25, []
        for line in sc["narr"]:
            a = pcm(TTS.synth(TTS.speakable(line, SAY), VOICE, RATE, 0.0, cache))
            sc["L"].append(cur)
            clips.append((t + cur, a))
            d = len(a) / 48000
            cues.append((t + cur, t + cur + d, line.replace(" | ", " ").replace("|", "")))
            cur += d + 0.25
        sc["dur"] = max(sc["min"], cur + 0.3)
        t += sc["dur"]
    total = t
    buf = np.zeros(int(total * 48000) + 48000, np.float32)
    for st, a in clips:
        s = int(st * 48000)
        buf[s:s + len(a)] += a
    return total, buf, cues


def sub_frames(cues):
    """긴 자막은 글자 수 비례로 나눠 보여 주기 (한 화면 최대 2줄)"""
    out = []
    for s, e, txt in cues:
        parts = [p.strip() for p in txt.replace("? ", "?|").replace(". ", ".|").replace(", ", ",|").split("|") if p.strip()]
        chunks, cur = [], ""
        for p in parts:
            if len(cur) + len(p) > 26 and cur:
                chunks.append(cur)
                cur = p
            else:
                cur = (cur + " " + p).strip()
        chunks.append(cur)
        n = sum(len(c) for c in chunks)
        tt = s
        for c in chunks:
            d = (e - s) * len(c) / n
            out.append((tt, tt + d, c))
            tt += d
    return out


_subc = {}


def subtitle(f, text):
    if text not in _subc:
        tx = T(text, 62, (14, 16, 24), "Bold", max_w=920, align="center", line_gap=1.25)
        px, py = 34, 16
        box = Image.new("RGBA", (tx.width + px * 2, tx.height + py * 2), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), radius=18, fill=(255, 255, 255, 232))
        box.alpha_composite(tx, (px, py))
        _subc[text] = box
    G.blit(f, _subc[text], (W / 2, 1420), 1, "mt")


def frame(t, subs):
    f = BG.copy()
    header(f)
    sc = next((s for s in SCENES if s["start"] <= t < s["start"] + s["dur"]), SCENES[-1])
    lt = t - sc["start"]
    sc["draw"](f, lt, sc)
    # 장면 전환: 앞 0.18초 살짝 아래에서 올라오며 밝아짐
    if lt < 0.18 and sc is not SCENES[0]:
        f.alpha_composite(Image.new("RGBA", (W, H), BG2 + (int(200 * (1 - lt / 0.18)),)), (0, 0))
        header(f)
    cue = next((c for c in subs if c[0] <= t < c[1] + 0.1), None)
    if cue:
        subtitle(f, cue[2])
    return f.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    total, voice, cues = plan()
    subs = sub_frames(cues)
    print(f"길이 {total:.1f}초 · 장면 {len(SCENES)}개")
    if a.stills:
        (OUT / "stills").mkdir(exist_ok=True)
        for i, sc in enumerate(SCENES):
            frame(sc["start"] + min(sc["dur"] - 0.1, sc["L"][-1] + 0.8), subs).save(OUT / "stills" / f"{i + 1:02d}.png")
        return
    # 오디오: 음성 + 효과음 + 잔잔한 배경음
    with wave.open(str(OUT / "voice.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype("<i2").tobytes())
    ev = []
    for sc in SCENES:
        for at, nm, vol in sc.get("sfx", []):
            ev.append((sc["start"] + sc["L"][0] + at, nm, vol))
        ev.append((sc["start"], "whoosh", 0.18))
    race = SCENES[1]
    for p in PATHS:
        ev.append((race["start"] + race["L"][0] + 0.6 + p["t"][-1] * SLOW, "ding", 0.35))
    tau = SCENES[6]
    ev.append((tau["start"] + tau["L"][0] + 0.8 + 1.0029 * SLOW, "ding", 0.5))
    SFX.build_track(ev, total, OUT / "sfx.wav")
    from engine import bgm
    bgm.generate(total, OUT / "bgm.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(OUT / "voice.wav"), "-i", str(OUT / "sfx.wav"), "-i", str(OUT / "bgm.wav"),
           "-filter_complex", "[3:a]volume=0.10[b];[1:a][2:a][b]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT / "short.mp4")]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS)
    for i in range(n):
        pr.stdin.write(frame(i / FPS, subs).tobytes())
        if i % 300 == 0:
            print(f"  {i}/{n}")
    pr.stdin.close()
    pr.wait()
    print("완료 →", OUT / "short.mp4")


if __name__ == "__main__":
    main()
