"""에피소드 렌더러.

  python render.py episodes/ep001_buffett_fear --script   # 녹음용 대본(script.md) 생성
  python render.py episodes/ep001_buffett_fear --stills   # 장면별 스틸 이미지만 (빠른 검수)
  python render.py episodes/ep001_buffett_fear            # 영상 전체 (녹음 없으면 가이드 모드)
  python render.py episodes/ep001_buffett_fear --scenes 5-7   # 일부 장면만 미리보기

결과물: out/<에피소드>/ video.mp4, captions.srt, thumbnail.png, youtube.json, stills/
"""
import argparse
import json
import multiprocessing as mp
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engine import bgm, charts, timeline  # noqa: E402
from engine import draw as G  # noqa: E402
from engine import scenes as SC  # noqa: E402
from engine import style as S  # noqa: E402


class _Loader(yaml.SafeLoader):
    """YAML 1.1은 on/off/yes/no 를 불리언으로 읽는다 → `on: 3` 키가 True가 되는 문제 방지."""


_Loader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:bool"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_Loader.add_implicit_resolver("tag:yaml.org,2002:bool", __import__("re").compile(r"^(?:true|True|false|False)$"),
                              list("tTfF"))


def read_yaml(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_Loader)


def load(ep_dir):
    ep = read_yaml(ep_dir / "episode.yaml")
    channel = read_yaml(ROOT / "channel.yaml")
    return ep, channel


def build_scenes(ep, channel):
    return [SC.make(s, i + 1, channel) for i, s in enumerate(ep["scenes"])]


# ── 대본 ────────────────────────────────────────────────────────
def write_script(ep, ep_dir):
    L = [f"# {ep['title']}", "", "## 녹음 방법", "",
         "- **통녹음 권장**: 처음부터 끝까지 한 파일로 녹음 → `audio/full.wav` (m4a/mp3도 가능)",
         "- 문장(번호) 사이는 자연스럽게 0.3~0.5초 쉬기 → 자막이 문장 단위로 맞춰집니다",
         "- **장면 사이(─── 표시)는 2초 쉬기** → 장면이 자동으로 나뉩니다",
         "- 틀리면 그 장면을 처음부터 다시 읽고, 나중에 틀린 부분만 잘라내면 됩니다",
         "- 또는 장면별로 `audio/01.wav`, `audio/02.wav` … 따로 녹음해도 됩니다", "",
         f"예상 길이: 약 {sum(timeline.est_line(x) for s in ep['scenes'] for x in s.get('narration', [])) / 60 + 0.4:.1f}분", ""]
    for i, s in enumerate(ep["scenes"], 1):
        L.append(f"### 장면 {i:02d} · {s.get('chapter') or s['type']}")
        L.append("")
        for j, line in enumerate(s.get("narration", []), 1):
            L.append(f"{j}. {line.replace(' | ', ' ').replace('|', '')}")
        L.append("")
        L.append("─── (2초 쉼) ───" if i < len(ep["scenes"]) else "(끝)")
        L.append("")
    (ep_dir / "script.md").write_text("\n".join(L), encoding="utf-8")
    print("대본 →", ep_dir / "script.md")


# ── 프레임 ──────────────────────────────────────────────────────
class Ctx:
    pass


def setup(ep_dir, only=None, log=print):
    ep, channel = load(ep_dir)
    scenes = build_scenes(ep, channel)
    for sc in scenes:
        sc.prepare()
    narr, mode = timeline.plan(scenes, ep_dir / "audio", log=log)
    c = Ctx()
    c.ep, c.channel, c.scenes, c.narr, c.mode = ep, channel, scenes, narr, mode
    c.total = scenes[-1].start + scenes[-1].dur
    c.cues = timeline.cues(scenes)
    if only:
        a, b = only
        sel = [s for s in scenes if a <= s.idx <= b]
        c.t0, c.t1 = sel[0].start, sel[-1].start + sel[-1].dur
    else:
        c.t0, c.t1 = 0.0, c.total
    return c


def frame_at(c, t):
    bg = G.background()
    sc = next((s for s in c.scenes if s.start <= t < s.start + s.dur), c.scenes[-1])
    lt = t - sc.start
    f = bg.copy()
    sc.draw(f, lt)
    fade_in, fade_out = 0.3, 0.25
    if lt < fade_in and sc.idx > 1:
        f = Image.blend(bg, f, G.ease_out(lt / fade_in))
    elif sc.dur - lt < fade_out and sc.idx < len(c.scenes):
        f = Image.blend(bg, f, max(0.0, (sc.dur - lt) / fade_out))
    SC.chrome(f, sc, t, c.total, c.channel)
    cue = next((x for x in c.cues if x[0] <= t < x[1] + 0.12), None)
    SC.subtitle(f, cue[2] if cue else "")
    return f.convert("RGB")


_C = None


def _worker(args):
    ep_dir, only, i0, i1, path = args
    global _C
    if _C is None:
        _C = setup(ep_dir, only, log=lambda *a: None)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{S.W}x{S.H}",
           "-r", str(S.FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-tune", "animation", str(path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(_C, _C.t0 + i / S.FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render_video(c, ep_dir, out, only, workers):
    n = int(round((c.t1 - c.t0) * S.FPS))
    tmp = out / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    k = max(1, workers)
    step = (n + k - 1) // k
    jobs = [(ep_dir, only, i, min(n, i + step), tmp / f"part{j:02d}.mp4") for j, i in enumerate(range(0, n, step))]
    t = time.time()
    print(f"프레임 {n}개 렌더링 (작업자 {len(jobs)}개)…")
    with mp.get_context("fork").Pool(len(jobs)) as pool:
        parts = pool.map(_worker, jobs)
    lst = tmp / "parts.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    silent = tmp / "silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(silent)], check=True)
    print(f"  영상 {time.time() - t:.0f}초")

    # 오디오: 내레이션 정리 + BGM 생성 + 더킹 믹스
    dur = c.t1 - c.t0
    music = bgm.generate(dur + 0.5, tmp / "bgm.wav")
    voice = None
    if c.narr:
        voice = tmp / "voice.wav"
        if isinstance(c.narr, list):  # 장면별 파일 → 장면 길이만큼 이어붙이기
            inputs, fl = [], []
            for i, (sc, p) in enumerate(zip(c.scenes, c.narr)):
                inputs += ["-i", str(p)]
                fl.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,apad=whole_dur={sc.dur:.3f}[a{i}]")
            fl.append("".join(f"[a{i}]" for i in range(len(c.narr))) + f"concat=n={len(c.narr)}:v=0:a=1[out]")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fl),
                            "-map", "[out]", str(tmp / "voice_raw.wav")], check=True)
            src = tmp / "voice_raw.wav"
        else:
            src = c.narr
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{c.t0:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
                        "-af", "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                               "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000",
                        "-ac", "1", str(voice)], check=True)
    final = out / ("video.mp4" if not only else f"preview_{only[0]:02d}-{only[1]:02d}.mp4")
    if voice:
        fc = ("[1:a]aresample=48000,volume=0.20,aformat=channel_layouts=stereo[m];"
              "[2:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];"
              "[m][v1]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=600[md];"
              "[md][v2]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(music), "-i", str(voice),
               "-filter_complex", fc]
    else:
        fc = "[1:a]aresample=48000,volume=0.30[a]"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(music), "-filter_complex", fc]
    cmd += ["-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", str(final)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp)
    return final


# ── 썸네일 ──────────────────────────────────────────────────────
def thumbnail(c, out):
    th = c.ep.get("thumbnail")
    if not th:
        return
    f = G.background().copy()
    if th.get("chart"):
        ch = charts.LineChart(dict(th["chart"], draw={"on": 1, "dur": 0.01}), rect=(980, 300, 840, 560))
        G.blit(f, ch.line, (0, 0))
        for m in th["chart"].get("marks", []):
            (mx, my), _ = ch.point_at(m["date"])
            G.blit(f, charts._dot(30, SC.col(m.get("color"), S.UP), ring=True), (mx, my), 1, "mm")
            G.blit(f, G.pill(m["label"], "Black", 44, (16, 20, 32), SC.col(m.get("color"), S.UP), pad=(24, 10)),
                   (mx + m.get("dx", 0), my + m.get("dy", -60)), 1, "mb")
    y = 170
    for i, line in enumerate(th["lines"]):
        im = G.text_img(line, "Black", th.get("size", 150), S.FG, highlight=th.get("highlight", ""))
        G.blit(f, im, (100, y))
        y += im.height - 6
    if th.get("sub"):
        G.blit(f, G.pill(th["sub"], "ExtraBold", 48, (16, 20, 32), S.GOLD, pad=(30, 14)), (100, y + 40))
    G.blit(f, G.text_img(c.channel.get("name", ""), "ExtraBold", 36, S.GOLD), (100, 70))
    f.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out / "thumbnail.png")
    print("썸네일 →", out / "thumbnail.png")


def stats_report(c, out):
    rows = []
    for sc in c.scenes:
        if sc.spec["type"] == "bars":
            for g in sc.chart.spec["groups"]:
                for b in g["bars"]:
                    rows.append(f"장면 {sc.idx:02d} | {g['label']} | {b['label']}: {b['value']}")
    for chk in c.ep.get("checks", []):
        from engine import data as D
        kw = dict(chk)
        name, kind = kw.pop("name"), kw.pop("kind")
        rows.append(f"검증 | {name}: {D.stat(kind, **kw):.1f}")
    (out / "numbers.txt").write_text("\n".join(rows), encoding="utf-8")
    print("대본 숫자 대조용 (실제 데이터 계산값):")
    for r in rows:
        print("  ", r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--script", action="store_true")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--scenes", help="예: 5-7")
    ap.add_argument("--workers", type=int, default=mp.cpu_count())
    a = ap.parse_args()
    ep_dir = Path(a.episode).resolve()
    out = ROOT / "out" / ep_dir.name
    out.mkdir(parents=True, exist_ok=True)

    if a.script:
        write_script(load(ep_dir)[0], ep_dir)
        return
    only = tuple(int(x) for x in a.scenes.split("-")) if a.scenes else None
    if only and len(only) == 1:
        only = (only[0], only[0])
    c = setup(ep_dir, only)
    print(f"모드: {c.mode} · 총 길이 {c.total / 60:.1f}분 · 장면 {len(c.scenes)}개")
    stats_report(c, out)
    timeline.write_srt(c.cues, out / "captions.srt")
    yt = c.ep.get("youtube", {})
    (out / "youtube.json").write_text(json.dumps(yt, ensure_ascii=False, indent=2), encoding="utf-8")
    thumbnail(c, out)
    if a.stills:
        st = out / "stills"
        st.mkdir(exist_ok=True)
        for sc in c.scenes:
            if only and not (only[0] <= sc.idx <= only[1]):
                continue
            t = sc.start + max(0.0, sc.dur - 0.6)
            frame_at(c, t).save(st / f"{sc.idx:02d}.png")
        print("스틸 →", st)
        return
    final = render_video(c, ep_dir, out, only, a.workers)
    print("완료 →", final)


if __name__ == "__main__":
    main()
