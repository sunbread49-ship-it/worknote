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
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engine import bgm, charts, sfx, timeline  # noqa: E402
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
    if ep.get("series_tag"):
        channel["_series_tag"] = ep["series_tag"]
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


TTS_OVERRIDE = None  # --tts 옵션


def setup(ep_dir, only=None, log=print):
    ep, channel = load(ep_dir)
    scenes = build_scenes(ep, channel)
    for sc in scenes:
        sc.prepare()
    tts_cfg = ep.get("tts") if TTS_OVERRIDE is None else {**(ep.get("tts") or {}), **TTS_OVERRIDE}
    if tts_cfg and tts_cfg.get("enabled", True) and not any((ep_dir / "audio").glob("*.*")):
        from engine import tts
        work = ROOT / "out" / ep_dir.name
        work.mkdir(parents=True, exist_ok=True)
        narr, mode = tts.plan(scenes, tts_cfg, work, log=log)
    else:
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


TRANS_T = 0.3
TRANS_CYCLE = ["slide", "up", "wipe", "slide", "cut", "up"]
_last = {}


def scene_content(c, sc, lt):
    """장면 그림(로고·자막 제외). 화면 흔들림 반영."""
    bg = G.background()
    f = bg.copy()
    sc._now = lt  # 움직이는 배경(bgvideo)용 장면 시각
    sc.draw(f, lt)
    cx, cy, z = sc.camera_at(lt)
    if z > 1.001:
        w, h = S.W / z, S.H / z
        x0 = min(max(cx - w / 2, 0), S.W - w)
        y0 = min(max(cy - h / 2, 0), S.H - h)
        f = f.resize((S.W, S.H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))
    dx, dy = sc.shake_at(lt)
    if dx or dy:
        moved = bg.copy()
        moved.alpha_composite(f.crop((max(0, -dx), max(0, -dy), S.W - max(0, dx), S.H - max(0, dy))),
                              (max(0, dx), max(0, dy)))
        f = moved
    return f


def last_frame(c, sc):
    if sc.idx not in _last:
        _last[sc.idx] = scene_content(c, sc, max(0.0, sc.dur - 0.02))
    return _last[sc.idx]


def transition_kind(c, sc):
    return sc.spec.get("transition") or getattr(sc, "default_transition", None) or \
        TRANS_CYCLE[(sc.idx - 2) % len(TRANS_CYCLE)]


def transition(kind, a, b, p):
    """a: 이전 장면 마지막 화면, b: 새 장면, p: 0→1"""
    k = G.ease_in_out(p)
    if kind == "cut":
        return b
    if kind in ("slide", "up"):
        out = Image.new("RGBA", (S.W, S.H))
        if kind == "slide":
            o = int(S.W * k)
            out.paste(a, (-o, 0))
            out.paste(b, (S.W - o, 0))
        else:
            o = int(S.H * k)
            out.paste(a, (0, -o))
            out.paste(b, (0, S.H - o))
        return out
    if kind == "zoom":
        sa = 1 + 0.35 * k
        za = a.resize((int(S.W * sa), int(S.H * sa)), Image.BILINEAR)
        za = za.crop(((za.width - S.W) // 2, (za.height - S.H) // 2, (za.width - S.W) // 2 + S.W,
                      (za.height - S.H) // 2 + S.H))
        sb = 1.15 - 0.15 * k
        zb = b.resize((int(S.W * sb), int(S.H * sb)), Image.BILINEAR)
        zb = zb.crop(((zb.width - S.W) // 2, (zb.height - S.H) // 2, (zb.width - S.W) // 2 + S.W,
                      (zb.height - S.H) // 2 + S.H))
        return Image.blend(za, zb, k)
    if kind == "flash":
        white = Image.new("RGBA", (S.W, S.H), (255, 255, 255, 255))
        if p < 0.35:
            return Image.blend(a, white, p / 0.35)
        return Image.blend(white, b, min(1.0, (p - 0.35) / 0.65))
    if kind == "wipe":  # 대각선 금색 띠가 쓸고 지나감
        x = int((S.W + 700) * k) - 350
        mask = Image.new("L", (S.W, S.H), 0)
        ImageDraw.Draw(mask).polygon([(0, 0), (x + 300, 0), (x - 300, S.H), (0, S.H)], fill=255)
        out = Image.composite(b, a, mask)
        band = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
        ImageDraw.Draw(band).polygon([(x + 300, 0), (x + 380, 0), (x - 220, S.H), (x - 300, S.H)], fill=S.GOLD + (255,))
        out.alpha_composite(band)
        return out
    return Image.blend(a, b, k)


def frame_at(c, t, subs=True, chrome=True):
    sc = next((s for s in c.scenes if s.start <= t < s.start + s.dur), c.scenes[-1])
    lt = t - sc.start
    f = scene_content(c, sc, lt)
    if sc.idx > 1 and lt < TRANS_T:
        prev = c.scenes[sc.idx - 2]
        f = transition(transition_kind(c, sc), last_frame(c, prev), f, lt / TRANS_T)
    if chrome and not sc.spec.get("no_chrome"):
        SC.chrome(f, sc, t, c.total, c.channel)
    if subs:
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
        src = c.narr
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{c.t0:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
                        "-af", "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                               "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000",
                        "-ac", "1", str(voice)], check=True)
    final = out / ("video.mp4" if not only else f"preview_{only[0]:02d}-{only[1]:02d}.mp4")
    events = [(t - c.t0, n, v) for t, n, v in sfx_events(c) if c.t0 <= t < c.t1]
    fx = sfx.build_track(events, dur + 0.5, tmp / "sfx.wav")
    if voice:
        fc = ("[1:a]aresample=48000,volume=0.20,aformat=channel_layouts=stereo[m];"
              "[2:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];"
              "[m][v1]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=600[md];"
              "[3:a]aresample=48000,volume=0.55[fx];"
              "[md][v2][fx]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(music), "-i", str(voice),
               "-i", str(fx), "-filter_complex", fc]
    else:
        fc = ("[1:a]aresample=48000,volume=0.30[m];[2:a]aresample=48000,volume=0.6[fx];"
              "[m][fx]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(music), "-i", str(fx),
               "-filter_complex", fc]
    cmd += ["-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", str(final)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp)
    return final


def chapters(c):
    """장면의 chapter 값이 바뀌는 지점으로 유튜브 챕터(타임스탬프) 생성"""
    rows, last = [], None
    for sc in c.scenes:
        ch = sc.spec.get("chapter") or ("인트로" if sc.idx == 1 else None)
        if ch and ch != last:
            t = 0 if not rows else sc.start
            if rows and t - rows[-1][0] < 12:  # 너무 짧은 챕터는 합침
                rows[-1] = (rows[-1][0], ch)
            else:
                rows.append((t, ch))
            last = ch
    return "\n".join(f"{int(t // 60):02d}:{int(t % 60):02d} {n}" for t, n in rows) if len(rows) >= 3 else ""


def write_review(c, out):
    """검수표: 문장 번호 · 시작 시간 · 장면 → '12번 어색' 처럼 번호로 피드백"""
    rows, n = [], 0
    for sc in c.scenes:
        for (a, _), text in zip(sc.lines, sc.narration):
            n += 1
            t = sc.start + a
            rows.append(f"{n:3d}번  {int(t // 60)}:{int(t % 60):02d}  [장면 {sc.idx:02d}]  {text.replace(' | ', ' ')}")
    (out / "검수표.txt").write_text("문장 번호 · 영상 시간 · 장면 · 문장\n(어색한 곳은 '12번, 37번'처럼 번호나 시간으로 알려주세요)\n\n"
                                   + "\n".join(rows), encoding="utf-8")


def sfx_events(c):
    """전체 영상 기준 효과음 이벤트: 장면 전환 '슉' + 장면별 요소"""
    ev = []
    import re
    for sc in c.scenes:
        # 2026-11-11: 전환 '쓱'은 기본으로 빼고(필요하면 transition_sfx로 지정), 중요 대사에 강조음
        tr = sc.spec.get("transition_sfx", c.ep.get("transition_sfx", "none"))
        if sc.idx > 1 and tr and tr != "none":
            ev.append((sc.start - 0.18, tr, 0.25))
        ev += [(sc.start + t, n, v) for t, n, v in sc.sfx_events()]
        if c.ep.get("emphasis_sfx", True) and not sc.spec.get("no_emphasis"):
            for text, (a, b) in zip(getattr(sc, "narration", []), getattr(sc, "lines", [])):
                plain = text.replace("[낮게]", "")
                m = re.search(r"!!|\*\*", plain)
                if not m:
                    continue
                pos = len(re.sub(r"!!|\*\*", "", plain[:m.start()])) / max(1, len(re.sub(r"!!|\*\*", "", plain)))
                name = "accent_low" if m.group() == "!!" else "accent"
                ev.append((sc.start + a + (b - a) * pos, name, 0.55 if name == "accent_low" else 0.45))
    return ev


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
    ap.add_argument("--tts", help="AI 음성 사용. 예: --tts ko-KR-Chirp3-HD-Charon (녹음 파일이 있으면 녹음 우선)")
    ap.add_argument("--rate", type=float, help="AI 음성 속도 (기본 1.0)")
    a = ap.parse_args()
    global TTS_OVERRIDE
    if a.tts or a.rate:
        TTS_OVERRIDE = {k: v for k, v in (("voice", a.tts), ("rate", a.rate)) if v}
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
    write_review(c, out)
    try:  # 2026-11-12: 사용자 검수 전에 음성 자동 점검 (tools/voice_check.py · VOICE_RULES.md)
        sys.path.insert(0, str(ROOT / "tools"))
        import voice_check
        voice_check.main(ep_dir, quiet=True)
    except Exception as e:
        print("음성 자동 점검 생략:", e)
    yt = dict(c.ep.get("youtube", {}))
    chap = chapters(c)
    if chap and "description" in yt:
        yt["description"] = yt["description"].replace("00:00 레딧에서 도는 썰\n(챕터는 업로드 시 자동 생성 예정)\n", "")
        yt["description"] = __import__("re").sub(r"\n{3,}", "\n\n", yt["description"]).rstrip() + "\n\n[챕터]\n" + chap
    (out / "설명란.txt").write_text(yt.get("title", "") + "\n\n" + yt.get("description", "") + "\n\n"
                                  + " ".join("#" + x for x in yt.get("tags", [])[:3]), encoding="utf-8")
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
