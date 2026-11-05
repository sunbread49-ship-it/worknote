"""롱폼에서 쇼츠(9:16) 잘라 만들기.

  python tools/make_shorts.py episodes/ep002_tqqq_reddit
episode.yaml 의 shorts: [{title, highlight, start: "1:44", end: "2:27"}] 를 읽는다.
먼저 롱폼(render.py)을 렌더해 둬야 한다(소리는 롱폼에서 잘라 씀).
구성: 가운데 = 원본 화면(로고 포함) / 그 위 = 자막 / 아래 가운데 = 채널 프로필 + "전체 영상은 ... 채널에서 확인하세요."
  python tools/make_shorts.py episodes/ep002_tqqq_reddit 3   # 3번 쇼츠만
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


VID_Y = (VH - 608) // 2 - 40   # 가운데 영상 위치


def compose(c, sh, t, bg):
    f = bg.copy()
    fr = render.frame_at(c, t, subs=False, chrome=False).convert("RGBA")  # 롱폼 진행바는 빼고
    fr.alpha_composite(SC._logo(c.channel.get("name", "")), (34, 26))      # 로고만 넣기
    fr = fr.resize((VW, 608), Image.LANCZOS)
    f.paste(fr, (0, VID_Y))
    cue = next((x for x in c.cues if x[0] <= t < x[1] + 0.12), None)
    if cue:  # 자막: 영상 바로 위
        tx = G.text_img(cue[2], "Black", 64, (255, 255, 255), max_w=980, align="center", stroke=5, stroke_fill=(0, 0, 0))
        f.alpha_composite(tx, ((VW - tx.width) // 2, VID_Y - 90 - tx.height))
    return f


def cta(channel):
    """하단 가운데: 채널 프로필 + '전체 영상은 ... 채널에서 확인하세요.'"""
    from engine.character import logo_badge
    b = logo_badge(120)
    name = channel.get("name", "")
    t1 = G.text_img("전체 영상은", "Bold", 44, S.FG)
    t2 = G.text_img(f"'{name}' 채널에서 확인하세요.", "Bold", 44, S.FG, highlight=f"'{name}'")
    tw = max(t1.width, t2.width)
    w = b.width + 28 + tw
    h = max(b.height, t1.height + t2.height + 8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(b, (0, (h - b.height) // 2))
    y = (h - (t1.height + t2.height + 8)) // 2
    im.alpha_composite(t1, (b.width + 28, y))
    im.alpha_composite(t2, (b.width + 28, y + t1.height + 8))
    return im


def cover(c, sh, path):
    """쇼츠 썸네일(1080x1920): 위 질문 / 가운데 큰 숫자 대비 / 아래 채널"""
    from engine import charts
    cv = sh["cover"]
    f = vbg()
    glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-300, 500, 900, 1500), fill=SC.col(cv.get("glow"), S.UP) + (90,))
    from PIL import ImageFilter
    f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    if cv.get("chart"):
        ch = cv["chart"]
        spec = {"lines": [{"series": ch["series"], "color": ch.get("color"), "fill": False}],
                **{k: v for k, v in ch.items() if k not in ("series", "color")}, "draw": {"on": 1, "dur": 0.01}}
        lc = charts.LineChart(spec, rect=(60, 200, 960, 420))
        part = G.with_opacity(lc.line, 0.7).crop((0, 150, VW, 680))
        f.alpha_composite(part, (0, 1180))
    logo = SC._logo(c.channel.get("name", ""))
    f.alpha_composite(logo, ((VW - logo.width) // 2, 110))
    top = G.text_img(cv["top"], "Black", 92, S.FG, max_w=980, align="center", stroke=6, stroke_fill=(0, 0, 0),
                     highlight=cv.get("top_highlight", ""), line_gap=1.15)
    f.alpha_composite(top, ((VW - top.width) // 2, 330))
    y = 330 + top.height + 80
    for ln in cv["big"]:
        size = ln.get("size", 200)
        im = G.text_img(ln["text"], "Black", size, SC.col(ln.get("color"), S.FG), stroke=10, stroke_fill=(0, 0, 0))
        while im.width > 1000 and size > 80:
            size -= 10
            im = G.text_img(ln["text"], "Black", size, SC.col(ln.get("color"), S.FG), stroke=10, stroke_fill=(0, 0, 0))
        f.alpha_composite(im, ((VW - im.width) // 2, y))
        y += im.height + 10
    if cv.get("bottom"):
        b = G.text_img(cv["bottom"], "ExtraBold", 54, (255, 255, 255), stroke=5, stroke_fill=(0, 0, 0))
        f.alpha_composite(b, ((VW - b.width) // 2, y + 30))
    f.convert("RGB").save(path)
    return f


def job(args):
    ep_dir, i, sh, out = args
    c = render.setup(ep_dir, log=lambda *a: None)
    bg = vbg()
    cb = cta(c.channel)
    bg.alpha_composite(cb, ((VW - cb.width) // 2, VID_Y + 608 + 90))
    t0, t1 = ts(sh["start"]), ts(sh["end"])
    silent = out.with_suffix(".silent.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                          "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    n = int((t1 - t0) * FPS)
    for k in range(n):
        p.stdin.write(compose(c, sh, t0 + k / FPS, bg).convert("RGB").tobytes())
    if sh.get("cover"):  # 영상 끝 0.3초에 커버 화면 → 앱에서 '썸네일 선택'으로 고를 수 있게
        cv = cover(c, sh, out.with_name(out.stem + "_thumbnail.png")).convert("RGB").tobytes()
        for _ in range(9):
            p.stdin.write(cv)
    p.stdin.close()
    p.wait()
    full = ROOT / "out" / ep_dir.name / "video.mp4"
    d = t1 - t0
    pad = 0.3 if sh.get("cover") else 0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-ss", f"{t0:.2f}", "-t", f"{d:.2f}", "-i", str(full),
                    "-map", "0:v", "-map", "1:a",
                    "-af", f"afade=t=in:d=0.15,afade=t=out:st={d - 0.4:.2f}:d=0.4,apad=pad_dur={pad}",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    silent.unlink()
    return out


def main(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    ep, _ = render.load(ep_dir)
    od = ROOT / "out" / ep_dir.name / "shorts"
    od.mkdir(parents=True, exist_ok=True)
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    jobs = [(ep_dir, i, sh, od / f"short{i}.mp4") for i, sh in enumerate(ep["shorts"], 1) if not only or i in only]
    with mp.get_context("fork").Pool(min(len(jobs), mp.cpu_count())) as pool:
        for o in pool.map(job, jobs):
            print("쇼츠 →", o)
    lines = []
    for i, sh in enumerate(ep["shorts"], 1):
        lines.append(f"[쇼츠 {i}] {sh.get('yt_title', sh['title'].replace(chr(10), ' '))}\n{sh.get('yt_desc', '')}\n")
    (od / "쇼츠_제목_설명.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
