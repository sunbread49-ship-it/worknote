"""롱폼에서 쇼츠(9:16) 잘라 만들기.

  python tools/make_shorts.py episodes/ep002_tqqq_reddit
episode.yaml 의 shorts: [{title, highlight, start: "1:44", end: "2:27"}] 를 읽는다.
먼저 롱폼(render.py)을 렌더해 둬야 한다(소리는 롱폼에서 잘라 씀).
구성: 위 = 후킹 제목 / 가운데 = 원본 화면 / 아래 = 큰 자막 / 맨 아래 = 채널 안내
"""
import multiprocessing as mp
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw  # noqa: E402

import render  # noqa: E402
from engine import draw as G  # noqa: E402
from engine import scenes as SC  # noqa: E402
from engine import style as S  # noqa: E402

VW, VH = 1080, 1920
FPS = 30


def ts(x):
    if isinstance(x, (int, float)):
        return float(x)
    m, s = x.split(":")
    return int(m) * 60 + float(s)


def vbg():
    im = Image.new("RGBA", (VW, VH), S.BG_BOT + (255,))
    d = ImageDraw.Draw(im)
    for y in range(VH):
        k = y / VH
        d.line((0, y, VW, y), fill=tuple(int(S.BG_TOP[i] * (1 - k) + S.BG_BOT[i] * k) for i in range(3)) + (255,))
    return im


def compose(c, sh, t, bg, head):
    f = bg.copy()
    f.alpha_composite(head, ((VW - head.width) // 2, 230))
    fr = render.frame_at(c, t, subs=False, chrome=False).resize((VW, 608), Image.LANCZOS)
    f.paste(fr, (0, 640))
    cue = next((x for x in c.cues if x[0] <= t < x[1] + 0.12), None)
    if cue:
        tx = G.text_img(cue[2], "Black", 62, (255, 255, 255), max_w=960, align="center", stroke=5, stroke_fill=(0, 0, 0))
        f.alpha_composite(tx, ((VW - tx.width) // 2, 1320))
    return f


def job(args):
    ep_dir, i, sh, out = args
    c = render.setup(ep_dir, log=lambda *a: None)
    bg = vbg()
    logo = SC._logo(c.channel.get("name", ""))
    bg.alpha_composite(logo, ((VW - logo.width) // 2, 70))
    foot = G.text_img(f"전체 영상은 채널에서  ·  {c.channel.get('handle', '')}", "Bold", 34, S.MUTED)
    bg.alpha_composite(foot, ((VW - foot.width) // 2, 1700))
    head = G.text_img(sh["title"], "Black", sh.get("size", 82), S.FG, max_w=980, align="center",
                      highlight=sh.get("highlight", ""), line_gap=1.18)
    t0, t1 = ts(sh["start"]), ts(sh["end"])
    silent = out.with_suffix(".silent.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                          "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    n = int((t1 - t0) * FPS)
    for k in range(n):
        p.stdin.write(compose(c, sh, t0 + k / FPS, bg, head).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    full = ROOT / "out" / ep_dir.name / "video.mp4"
    d = t1 - t0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-ss", f"{t0:.2f}", "-t", f"{d:.2f}", "-i", str(full),
                    "-map", "0:v", "-map", "1:a", "-af", f"afade=t=in:d=0.15,afade=t=out:st={d - 0.4:.2f}:d=0.4",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    silent.unlink()
    return out


def main(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    ep, _ = render.load(ep_dir)
    od = ROOT / "out" / ep_dir.name / "shorts"
    od.mkdir(parents=True, exist_ok=True)
    jobs = [(ep_dir, i, sh, od / f"short{i}.mp4") for i, sh in enumerate(ep["shorts"], 1)]
    with mp.get_context("fork").Pool(min(len(jobs), mp.cpu_count())) as pool:
        for o in pool.map(job, jobs):
            print("쇼츠 →", o)


if __name__ == "__main__":
    main(sys.argv[1])
