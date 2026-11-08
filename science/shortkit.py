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
VOICE, RATE = "ko-KR-Chirp3-HD-Sadaltager", 1.12
BG1, BG2 = (14, 18, 34), (6, 8, 16)
CREAM = (244, 236, 220)
DIM = (150, 160, 190)
CORAL = (255, 112, 88)
VIOLET = (186, 140, 255)
BLUE = (96, 168, 255)
MINT = (120, 230, 190)
GOLD = (255, 200, 80)
CTA = "더 재밌고 신기한 지식은, 채널 구독하고 우리 함께 봐요!"


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


def plan(scenes, out, say):
    cache = out / "tts_cache"
    t, clips, cues = 0.0, [], []
    for sc in scenes:
        sc["start"], cur, sc["L"] = t, 0.25, []
        for line in sc["narr"]:
            a = pcm(TTS.synth(TTS.speakable(line, say), VOICE, RATE, 0.0, cache))
            sc["L"].append(cur)
            clips.append((t + cur, a))
            d = len(a) / 48000
            cues.append((t + cur, t + cur + d, line.replace(" | ", " ").replace("|", "")))
            cur += d + 0.25
        sc["dur"] = max(sc.get("min", 2.0), cur + 0.3)
        t += sc["dur"]
    buf = np.zeros(int(t * 48000) + 48000, np.float32)
    for st, a in clips:
        s = int(st * 48000)
        buf[s:s + len(a)] += a
    return t, buf, cues


def sub_frames(cues):
    out = []
    for s, e, txt in cues:
        parts = [p.strip() for p in txt.replace("? ", "?|").replace(". ", ".|").replace(", ", ",|").split("|") if p.strip()]
        chunks, cur = [], ""
        for p in parts:
            if len(cur) + len(p) > 24 and cur:
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
        tx = T(text, 56, (14, 16, 24), "Bold", max_w=830, align="center", line_gap=1.25)
        px, py = 34, 16
        box = Image.new("RGBA", (tx.width + px * 2, tx.height + py * 2), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), radius=18, fill=(255, 255, 255, 232))
        box.alpha_composite(tx, (px, py))
        _subc[text] = box
    G.blit(f, _subc[text], (W / 2 - 30, 1295), 1, "mt")


def run(scenes, head, out, say=None, sfx=None, cover=None, argv=None):
    """scenes: [{draw(f, t, sc), narr:[..], min}], head: {kicker, title, highlight}, cover: draw(f) 커버 그림"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    a = ap.parse_args(argv)
    out.mkdir(parents=True, exist_ok=True)
    total, voice, cues = plan(scenes, out, say or {})
    subs = sub_frames(cues)
    print(f"길이 {total:.1f}초 · 장면 {len(scenes)}개")

    def frame(t):
        f = BG.copy()
        header(f, head)
        sc = next((s for s in scenes if s["start"] <= t < s["start"] + s["dur"]), scenes[-1])
        lt = t - sc["start"]
        sc["draw"](f, lt, sc)
        if lt < 0.18 and sc is not scenes[0]:
            f.alpha_composite(Image.new("RGBA", (W, H), BG2 + (int(200 * (1 - lt / 0.18)),)))
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
    ev = [(sc["start"], "whoosh", 0.18) for sc in scenes]
    for sc in scenes:
        for at, nm, vol in sc.get("sfx", []):
            ev.append((sc["start"] + sc["L"][0] + at, nm, vol))
    ev += (sfx or [])
    tail = 0.3 if cover else 0.0
    SFX.build_track(ev, total + tail, out / "sfx.wav")
    from engine import bgm
    bgm.generate(total + tail, out / "bgm.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(out / "voice.wav"), "-i", str(out / "sfx.wav"), "-i", str(out / "bgm.wav"),
           "-filter_complex", "[3:a]volume=0.10[b];[1:a][2:a][b]amix=inputs=3:normalize=0,apad,loudnorm=I=-14:TP=-1.5[a]",
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
