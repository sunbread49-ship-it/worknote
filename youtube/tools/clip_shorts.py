"""롱폼 → 구간 쇼츠 (2026-11-21 사용자 전략: 롱폼 1편 = 쇼츠 9개 · 새로 만들지 않고 구간만 잘라 9:16 + 상단 후킹 문구)
  python tools/clip_shorts.py <에피소드 폴더명>        → out/<ep>/clips/c1.mp4 … + cover · desc
에피소드 yaml 의 clips: [{start, end, hook, hl}] 사용 (초 단위 · 롱폼 video.mp4 기준)
화면(1080x1920): 흐린 배경 · 위 후킹 문구 · 가운데 롱폼 화면 전체(자막 포함 · 2026-11-21 사용자: 잘리면 어색) · 큰 자막(captions.srt) · '풀버전은 아래 영상 버튼'
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import draw as G  # noqa: E402

W, H = 1080, 1920
FONTS = ROOT / "assets/fonts"


def T(text, size, color, weight="Black", **kw):
    return G.text_img(text, weight, size, color, **kw)


def overlay(hook, hl, theme, out):
    acc = {"science": (110, 232, 140), "stock": (255, 204, 40)}[theme]
    band = {"science": (14, 40, 34), "stock": (1, 66, 43)}[theme]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 480), fill=band + (235,))
    d.rectangle((0, 472, W, 480), fill=acc + (255,))
    lines = hook.split("\n")
    y = 95 if len(lines) > 1 else 165
    for ln in lines:
        t = T(ln, 104, (255, 255, 255), highlight=hl if hl and hl in ln else "", hl_fill=acc, stroke=6, stroke_fill=(0, 0, 0))
        if t.width > W - 70:
            t = t.resize((W - 70, int(t.height * (W - 70) / t.width)), Image.LANCZOS)
        im.alpha_composite(t, ((W - t.width) // 2, y))
        y += t.height + 10
    pill = G.pill("▶ 풀버전은 아래 영상 버튼", "Black", 44, (20, 22, 30), acc, pad=(26, 12), radius=14)
    im.alpha_composite(pill, ((W - pill.width) // 2, 1365))
    im.save(out)


def srt_cues(path):
    txt = Path(path).read_text(encoding="utf-8")
    out = []
    for blk in re.split(r"\n\s*\n", txt.strip()):
        m = re.search(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)\s*\n(.+)", blk, re.S)
        if m:
            g = [int(x) for x in m.groups()[:8]]
            a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
            b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
            out.append((a, b, m.group(9).strip().replace("\n", " ")))
    return out


def ass_for(cues, s, e, path):
    def ts(x):
        x = max(0, x)
        return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
         "Style: S,Pretendard Black,66,&H00FFFFFF,&H00000000,&H80000000,1,7,2,2,50,50,590", "",
         "[Events]", "Format: Layer, Start, End, Style, Text"]
    for a, b, t in cues:
        if b <= s or a >= e:
            continue
        t = t.replace("!!", "").replace("**", "")
        if len(t) > 17:   # 두 줄로 (가운데 가까운 띄어쓰기)
            sp = [i for i, ch in enumerate(t) if ch == " "]
            if sp:
                k = min(sp, key=lambda i: abs(i - len(t) / 2))
                t = t[:k] + "\\N" + t[k + 1:]
        L.append(f"Dialogue: 0,{ts(a - s)},{ts(min(b, e) - s)},S,{t}")
    Path(path).write_text("\n".join(L), encoding="utf-8")


def make(ep, i, clip, theme, video, cues, od):
    s, e = float(clip["start"]), float(clip["end"])
    ov, ass = od / f"_ov{i}.png", od / f"_c{i}.ass"
    overlay(clip["hook"], clip.get("hl", ""), theme, ov)
    ass_for(cues, s, e, ass)
    fc = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2,eq=brightness=-0.28[bg];"
          "[b]scale=1080:608[fg];[bg][fg]overlay=0:540[v1];[v1][1:v]overlay=0:0[v2];"
          f"[v2]subtitles={ass}:fontsdir={FONTS}[v]")
    out = od / f"c{i}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s}", "-to", f"{e}", "-i", str(video), "-i", str(ov),
                    "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-r", "30", str(out)], check=True)
    # 표지(자막 없는 한 장): 후킹 문구 + 가운데 화면 한 장
    fr = od / f"_f{i}.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s + min(3.0, (e - s) / 2)}", "-i", str(video), "-frames:v", "1", str(fr)], check=True)
    src = Image.open(fr).convert("RGB")
    from PIL import ImageFilter, ImageEnhance
    bg = src.resize((int(1920 * 1920 / 1080), 1920)).crop((0, 0, 1080, 1920)).filter(ImageFilter.GaussianBlur(24))
    bg = ImageEnhance.Brightness(bg).enhance(0.72).convert("RGBA")
    bg.alpha_composite(src.resize((1080, 608)).convert("RGBA"), (0, 540))
    bg.alpha_composite(Image.open(ov))
    bg.convert("RGB").save(od / f"c{i}_cover.jpg", quality=90)
    fr.unlink(missing_ok=True)
    return out


if __name__ == "__main__":
    name = sys.argv[1]
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    ep = yaml.safe_load((ROOT / "episodes" / name / "episode.yaml").read_text())
    theme = ep.get("clip_theme", "stock")
    out = ROOT / "out" / name
    od = out / "clips"
    od.mkdir(exist_ok=True)
    cues = srt_cues(out / "captions.srt")
    for i, c in enumerate(ep["clips"], 1):
        if only and i not in only:
            continue
        p = make(name, i, c, theme, out / "video.mp4", cues, od)
        print(f"쇼츠 {i} → {p} ({float(c['end']) - float(c['start']):.0f}초) · {c['hook'].replace(chr(10), ' ')}")
