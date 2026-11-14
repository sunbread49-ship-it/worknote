"""악어새 지식창고 쇼츠 공통 틀 (1080x1920 · 30fps)
각 편은 SCENES(장면 목록) · HEAD(위 고정 제목) · OUT 만 정하고 shortkit.run(...) 호출.
화면 규칙(channel.yaml layout): 그림은 y≤1280 · 자막 y=1295 · 오른쪽 x>930 / y 900~1700, 아래 y>1480 은 비움
"""
import argparse
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "youtube"))
from engine import draw as G   # noqa: E402
from engine import sfx as SFX  # noqa: E402
from engine import tts as TTS  # noqa: E402

W, H, FPS = 1080, 1920, 30
VOICE, RATE = "ko-KR-Chirp3-HD-Umbriel", 1.15  # 2026-11-10: 주식 악어새와 같은 남자 15번, 쇼츠는 1.15배 (이전: Sadaltager 1.12)
BG1, BG2 = (14, 18, 34), (6, 8, 16)
CREAM = (244, 236, 220)
DIM = (150, 160, 190)
CORAL = (255, 112, 88)
VIOLET = (186, 140, 255)
BLUE = (96, 168, 255)
MINT = (120, 230, 190)
GOLD = (255, 200, 80)
CTA = "좋아요 누르고, / 친구한테도 물어보세요."  # 2026.11.10 변경: 긴 구독 문구는 끝에서 이탈 → 짧게 + 바로 첫 질문으로 루프
CTA_OLD = "더 재밌고 신기한 지식은, 채널 구독하고 우리 함께해요!"  # 2026.11.8~11.10 사용
# 마지막 '봐요'를 힘차게: 쉼표로 끊고 느낌표 두 개 (자막은 그대로)
CTA_SAY = {}


def _bg():
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(BG1) * (1 - y) + np.array(BG2) * y)
    im = Image.fromarray(np.broadcast_to(a, (H, W, 3)).astype(np.uint8), "RGB").convert("RGBA")
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


def header(f, head):
    k = T(head["kicker"], 40, MINT, "ExtraBold")
    G.blit(f, k, (W / 2, 140), 1, "mt")
    t = T(head["title"], head.get("size", 100), CREAM, "Black", highlight=head.get("highlight", ""), hl_fill=CORAL,
          align="center", line_gap=1.12)
    G.blit(f, t, (W / 2, 195), 1, "mt")


def pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    nz = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0] - 480):nz[-1] + 2400] if len(nz) else a


def _gemini_line(line, gem, say, cache):
    sys.path.insert(0, str(HERE.parent / "youtube" / "tools"))
    import voice_check as VC
    txt = TTS.gemini_text(line, say)
    best = None
    for take in range(3):
        a = pcm(TTS.gemini_synth(txt, gem.get("voice", "Umbriel"), gem.get("speed", "빠르게"), cache, take=take))
        try:
            x16 = a[::3]   # 48k → 16k
            ratio, diffs = VC.stt_diff(line, VC.stt(x16, {}))
        except Exception:
            return a
        if best is None or ratio > best[0]:
            best = (ratio, a)
        if ratio >= 0.88:
            break
        print(f"  다시 만듦({ratio:.2f}): {line[:30]} {diffs[:2]}")
    return best[1]


def plan(scenes, out, say):
    say = {**CTA_SAY, **say}
    rate = say.pop("__rate__", RATE)
    voice = say.pop("__voice__", VOICE)
    gem = say.pop("__gemini__", None)   # 예: {"voice": "Umbriel", "speed": "빠르게"}
    cache = out / "tts_cache"
    t, clips, cues = 0.0, [], []
    for sc in scenes:
        sc["start"], cur, sc["L"] = t, 0.25, []
        for line in sc["narr"]:
            if gem:  # 2026-11-14: Gemini 음성 — 줄 통째로 자연스럽게 + 받아쓰기로 확인해 틀리면 다시 (최대 3번)
                sc["L"].append(cur)
                a = _gemini_line(line, gem, say, cache)
                clips.append((t + cur, a))
                cues.append((t + cur, t + cur + len(a) / 48000, line.replace(" // ", " ").replace(" / ", " ").replace(" | ", " ").replace("|", "")))
                cur += len(a) / 48000 + sc.get("gap", 0.25)
                continue
            # ' / ' = 짧게 띄기(0.12초), ' // ' = 한 템포 쉬기(0.3초): 조각마다 따로 읽어 이어 붙임 → 쉼표 쉼 기호가 만드는 이상한 소리 방지
            pieces = [p for p in line.replace(" // ", " /~/ ").split(" /") if p.strip()]
            sc["L"].append(cur)
            seg, st0 = [], cur
            for k, pc in enumerate(pieces):
                long = pc.startswith("~/")
                pc = pc[2:] if long else pc
                pc = pc.lstrip("/ ").strip()
                a = pcm(TTS.synth(TTS.speakable(pc, say), voice, rate, 0.0, cache))
                if k:
                    cur += 0.3 if long else 0.12
                clips.append((t + cur, a))
                cur += len(a) / 48000
            text = line.replace(" // ", " ").replace(" / ", " ").replace(" | ", " ").replace("|", "")
            cues.append((t + st0, t + cur, text))
            cur += sc.get("gap", 0.25)
        sc["dur"] = max(sc.get("min", 2.0), cur + sc.get("tail", 0.3))
        t += sc["dur"]
    buf = np.zeros(int(t * 48000) + 48000, np.float32)
    for st, a in clips:
        s = int(st * 48000)
        buf[s:s + len(a)] += a
    return t, buf, cues


SUB_SIZE, SUB_MAXW, SUB_Y = 72, 960, 1350   # 2026-11-14: 크게 · 한 줄만 (두 줄 금지) → 길면 짧게 끊어 빠르게 넘김
SHIFT = 70  # 영상 내용을 위 고정 제목에서 조금 떼기


def _fits(text):
    from engine import style as St
    return St.font("Black", SUB_SIZE).getlength(text) <= SUB_MAXW


def sub_frames(cues):
    """자막은 항상 한 줄: 구두점 → 단어 단위로 잘라 한 줄 폭에 맞게 여러 번 나눠 보여 줌"""
    out = []
    for s, e, txt in cues:
        parts = [p.strip() for p in txt.replace("? ", "?|").replace(". ", ".|").replace(", ", ",|").split("|") if p.strip()]
        chunks, cur = [], ""
        for p in parts:
            cand = (cur + " " + p).strip()
            if _fits(cand) and (not cur or len(cur) < 8):
                cur = cand
                continue
            if cur:
                chunks.append(cur)
                cur = ""
            if _fits(p):
                cur = p
                continue
            # 한 구절이 한 줄보다 길면 → 단어 단위로 고르게(균형) 나눔
            words = p.split(" ")
            from engine import style as St
            fnt = St.font("Black", SUB_SIZE)
            k = 2
            while True:
                target = fnt.getlength(p) / k
                groups, g = [], ""
                for w_ in words:
                    c2 = (g + " " + w_).strip()
                    if g and fnt.getlength(c2) > target * 1.08 and len(groups) < k - 1:
                        groups.append(g)
                        g = w_
                    else:
                        g = c2
                groups.append(g)
                if all(_fits(x) for x in groups) or k > 6:
                    break
                k += 1
            chunks.extend(groups[:-1])
            cur = groups[-1]
        if cur:
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
        tx = T(text, SUB_SIZE, (14, 16, 24), "Black")
        px, py = 40, 20
        box = Image.new("RGBA", (tx.width + px * 2, tx.height + py * 2), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), radius=22, fill=(255, 255, 255, 242))
        box.alpha_composite(tx, (px, py))
        _subc[text] = box
    G.blit(f, _subc[text], (W / 2, SUB_Y), 1, "mt")


def run(scenes, head, out, say=None, sfx=None, cover=None, argv=None, bgm_cues=None):
    """scenes: [{draw(f, t, sc), narr:[..], min}], head: {kicker, title, highlight}, cover: draw(f) 커버 그림"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    a = ap.parse_args(argv)
    out.mkdir(parents=True, exist_ok=True)
    total, voice, cues = plan(scenes, out, say or {})
    subs = sub_frames(cues)
    print(f"길이 {total:.1f}초 · 장면 {len(scenes)}개")

    def frame(t):
        sc = next((s for s in scenes if s["start"] <= t < s["start"] + s["dur"]), scenes[-1])
        lt = t - sc["start"]
        g = BG.copy()
        sc["draw"](g, lt, sc)
        f = BG.copy()
        if sc.get("nohead"):  # 첫 장면: 고정 제목 없이 화면 가득 (지식창고 v2, 첫 1초 개선)
            f = g
        else:
            f.alpha_composite(g.crop((0, 0, W, H - SHIFT)), (0, SHIFT))
            header(f, head)
        if sc.get("flash") and lt < 0.14:  # 장면 전환 번쩍
            f.alpha_composite(Image.new("RGBA", (W, H), (255, 244, 220, int(170 * (1 - lt / 0.14)))))
        if lt < 0.18 and sc is not scenes[0] and not sc.get("flash"):
            f.alpha_composite(Image.new("RGBA", (W, H), BG2 + (int(200 * (1 - lt / 0.18)),)))
            if not sc.get("nohead"):
                header(f, head)
        cue = next((c for c in subs if c[0] <= t < c[1] + 0.1), None)
        if cue:
            subtitle(f, cue[2])
        return f.convert("RGB")

    def cover_img():
        f = BG.copy()
        cover(f)
        return f.convert("RGB")

    if cover:
        cover_img().save(out / "cover.png")
    if a.stills:
        (out / "stills").mkdir(exist_ok=True)
        for i, sc in enumerate(scenes):
            frame(sc["start"] + min(sc["dur"] - 0.1, sc["L"][-1] + 0.8)).save(out / "stills" / f"{i + 1:02d}.png")
        return
    with wave.open(str(out / "voice.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype("<i2").tobytes())
    ev = []  # 2026-11-11: 장면 전환 효과음 없음 — 내용(경로 · 숫자 · 반전)에 맞춘 효과음만 (장면의 sfx_t: [(장면 시작 기준 초, 이름, 볼륨)] 또는 sfx_fn(sc))
    for sc in scenes:
        for at, nm, vol in sc.get("sfx_t", []) + (sc["sfx_fn"](sc) if sc.get("sfx_fn") else []):
            ev.append((sc["start"] + at, nm, vol))
    for sc in scenes:
        for at, nm, vol in sc.get("sfx", []):
            ev.append((sc["start"] + sc["L"][0] + at, nm, vol))
    ev += (sfx or [])
    tail = 0.3 if cover else 0.0
    SFX.build_track(ev, total + tail, out / "sfx.wav")
    from engine import bgm
    if bgm_cues:  # [(장면 번호, 분위기)] → 장면 시작 시각으로 (2026-11-14 주식 쇼츠: 긴장 → 반전 밝게)
        bgm.scored(total + tail, out / "bgm.wav", [(scenes[i]["start"], k) for i, k in bgm_cues])
    else:
        bgm.bright(total + tail, out / "bgm.wav")  # 2026-11-11: 밝고 두근거리는 배경음
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(out / "voice.wav"), "-i", str(out / "sfx.wav"), "-i", str(out / "bgm.wav"),
           "-filter_complex", "[3:a]volume=0.16[b];[1:a][2:a][b]amix=inputs=3:normalize=0,apad,loudnorm=I=-14:TP=-1.5[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", str(out / "short.mp4")]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS)
    for i in range(n):
        pr.stdin.write(frame(i / FPS).tobytes())
    if cover:  # 끝 0.3초 커버 → 앱에서 '썸네일 선택'으로 고를 수 있게
        cv = cover_img().tobytes()
        for _ in range(int(tail * FPS)):
            pr.stdin.write(cv)
    pr.stdin.close()
    pr.wait()
    print("완료 →", out / "short.mp4")


# ── 사진 · 입체감 도구 ─────────────────────────────────────────────
import json as _json
from functools import lru_cache as _lru
from PIL import ImageEnhance as _IE

PHOTOS = HERE.parent / "youtube" / "assets" / "photos"


@_lru(maxsize=32)
def photo(name, w, h, focus=(0.5, 0.5), dark=0.0, blur=0, sat=1.0, radius=0):
    """위키미디어 사진을 w×h로 채워 자르기 (+어둡게 · 흐리게 · 둥근 모서리)"""
    meta = _json.loads((PHOTOS / f"{name}.json").read_text())
    im = Image.open(PHOTOS / meta["file"]).convert("RGB")
    sc = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = int((im.width - w) * focus[0]), int((im.height - h) * focus[1])
    im = im.crop((x0, y0, x0 + w, y0 + h))
    if sat != 1.0:
        im = _IE.Color(im).enhance(sat)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark:
        im = _IE.Brightness(im).enhance(1 - dark)
    im = im.convert("RGBA")
    if radius:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
        im.putalpha(m)
    return im


def credit_of(*names):
    out = []
    for n in names:
        m = _json.loads((PHOTOS / f"{n}.json").read_text())
        out.append(f"{m['artist'][:28]}, {m['license']}")
    return "사진: " + " · ".join(out) + " (Wikimedia Commons)"


def credit(f, text):
    G.blit(f, T(text, 20, (170, 178, 200), "SemiBold", max_w=900), (60, 1262), 0.85, "lb")


def band(f, name, y0=380, h=880, focus=(0.5, 0.5), dark=0.6, sat=0.8, blur=0):
    """콘텐츠 영역(제목 아래~자막 위)에 사진 띠를 깔고 위아래를 배경색으로 녹임"""
    im = photo(name, W, h, focus, dark, blur, sat)
    a = np.ones((h, W), np.float32)
    ramp = np.linspace(0, 1, 160)
    a[:160] *= ramp[:, None]
    a[-160:] *= ramp[::-1][:, None]
    im = im.copy()
    im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    f.alpha_composite(im, (0, y0))


def shadow_of(im, blur=24, alpha=0.6, off=(10, 18)):
    sh = Image.new("RGBA", (im.width + blur * 4, im.height + blur * 4), (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * alpha))
    sh.paste((0, 0, 0, 255), (blur * 2, blur * 2), a)
    return sh.filter(ImageFilter.GaussianBlur(blur)), (off[0] - blur * 2, off[1] - blur * 2)


def drop(f, im, xy, anchor="mm", op=1.0, blur=24, alpha=0.6):
    x, y = xy
    ax = {"l": 0, "m": im.width / 2, "r": im.width}[anchor[0]]
    ay = {"t": 0, "m": im.height / 2, "b": im.height}[anchor[1]]
    sh, (dx, dy) = shadow_of(im, blur, alpha)
    G.blit(f, sh, (x - ax + dx, y - ay + dy), op)
    G.blit(f, im, (x - ax, y - ay), op)


@_lru(maxsize=8)
def globe(r, name="bluemarble_east", light=(-0.45, -0.5)):
    """실제 지구 사진을 원으로 잘라 빛 · 그림자 · 대기 테두리를 입힌 구"""
    d = 2 * r
    im = photo(name, d, d, (0.5, 0.5)).copy()
    yy, xx = np.mgrid[-1:1:d * 1j, -1:1:d * 1j]
    rr = np.sqrt(xx ** 2 + yy ** 2)
    shade = np.clip(1.05 - 0.75 * np.clip((xx - light[0]) ** 2 + (yy - light[1]) ** 2, 0, 2) / 2, 0.25, 1.1)
    a = np.array(im, np.float32)
    a[..., :3] *= shade[..., None]
    a[..., 3] = np.where(rr <= 1, 255, 0)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    pad = 40
    g = Image.new("RGBA", (d + pad * 2, d + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((pad - 6, pad - 6, pad + d + 6, pad + d + 6), fill=(110, 170, 255, 120))
    g = g.filter(ImageFilter.GaussianBlur(14))
    g.alpha_composite(out, (pad, pad))
    return g


def glow_line(f, p0, p1, color, width=6, glow=18):
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).line((p0, p1), fill=color + (200,), width=width + glow)
    f.alpha_composite(lay.filter(ImageFilter.GaussianBlur(glow / 2)))
    ImageDraw.Draw(f).line((p0, p1), fill=color + (255,), width=width)


# ── 깊이감(2.5D 패럴랙스) 사진 띠 ───────────────────────────────
_px = {}


def pband(f, name, t, dur, y0=380, h=880, move=None, focus=(0.5, 0.5), dark=0.35, fade=160):
    """사진을 깊이 지도로 입체화해 카메라가 천천히 움직이는 띠 (engine/depth.py)"""
    from engine import depth as DP
    key = (name, h, repr(move), tuple(focus))
    if key not in _px:
        _px[key] = DP.Parallax(name, W, h, move=move, focus=focus)
    im = _px[key].at(t / max(dur, 0.1))
    if dark:
        im = _IE.Brightness(im.convert("RGB")).enhance(1 - dark).convert("RGBA")
    a = np.ones((h, W), np.float32)
    if fade:
        ramp = np.linspace(0, 1, fade)
        a[:fade] *= ramp[:, None]
        a[-fade:] *= ramp[::-1][:, None]
    im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    f.alpha_composite(im, (0, y0))
