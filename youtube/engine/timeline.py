"""내레이션 타이밍: 녹음 파일(무음 구간 감지) 또는 글자 수 추정으로 장면·문장 시간을 잡는다.

녹음 방법(둘 중 하나, episodes/<ep>/audio/ 에 넣기):
  A) 한 번에 통녹음: full.wav (또는 .m4a/.mp3)
     - 문장 사이: 자연스럽게 0.3초 이상 쉬기
     - 장면 사이: 2초 정도 쉬기  ← 이걸로 장면을 자동으로 나눔
  B) 장면별 파일: 01.wav, 02.wav, ... (장면 번호와 같게)
녹음이 없으면 '가이드 모드'로 글자 수 기준 길이를 추정해 무음 영상을 만든다.
"""
import re
import subprocess
from pathlib import Path

SYL_PER_SEC = 5.3      # 가이드 모드 말하기 속도(초당 음절)
LINE_GAP = 0.45        # 가이드 모드 문장 사이 쉼
SCENE_PAD = (0.5, 0.8) # 가이드 모드 장면 앞/뒤 여유
AUDIO_EXT = (".wav", ".m4a", ".mp3", ".flac", ".aac", ".ogg")


def syllables(text):
    return len(re.findall(r"[가-힣A-Za-z0-9]", text))


def est_line(text):
    return syllables(text) / SYL_PER_SEC + 0.25


def ffprobe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def silences(path, noise_db=-38, min_d=0.22):
    """[(start, end)] 무음 구간"""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_d}", "-f", "null", "-"],
                       capture_output=True, text=True)
    out, cur = [], None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            cur = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and cur is not None:
            out.append((cur, float(m.group(1))))
            cur = None
    if cur is not None:
        out.append((cur, ffprobe_dur(path)))
    return out


def _split_lines(seg_start, seg_end, sil, n_lines, texts):
    """구간 안에서 가장 긴 무음 n-1개로 문장 경계를 잡는다. 반환: 장면 기준 [(s,e)]"""
    inner = [s for s in sil if s[0] > seg_start + 0.05 and s[1] < seg_end - 0.05]
    # 앞뒤 무음(말 시작 전/끝난 뒤)
    lead = next((s[1] for s in sil if s[0] <= seg_start + 0.05 < s[1]), seg_start)
    tail = next((s[0] for s in sil if s[0] < seg_end - 0.05 <= s[1] + 0.05), seg_end)
    lead, tail = max(lead, seg_start), min(max(tail, lead + 0.5), seg_end)
    if n_lines <= 1:
        return [(lead - seg_start, tail - seg_start)]
    if len(inner) >= n_lines - 1:
        cuts = sorted(sorted(inner, key=lambda s: s[1] - s[0], reverse=True)[:n_lines - 1])
        out, s0 = [], lead
        for a, b in cuts:
            out.append((s0 - seg_start, a - seg_start))
            s0 = b
        out.append((s0 - seg_start, tail - seg_start))
        return out
    # 무음이 부족하면 글자 수 비례
    w = [max(1, syllables(x)) for x in texts]
    tot, acc, out = sum(w), lead, []
    for wi in w:
        d = (tail - lead) * wi / tot
        out.append((acc - seg_start, acc + d - seg_start))
        acc += d
    return out


def plan(scenes, audio_dir: Path, log=print):
    """각 scene에 dur/lines를 채우고 (narration_path or None, mode) 반환"""
    audio_dir = Path(audio_dir)
    full = next((audio_dir / f"full{e}" for e in AUDIO_EXT if (audio_dir / f"full{e}").exists()), None)
    per = {}
    for sc in scenes:
        for e in AUDIO_EXT:
            p = audio_dir / f"{sc.idx:02d}{e}"
            if p.exists():
                per[sc.idx] = p

    if full:
        total = ffprobe_dur(full)
        sil = silences(full)
        n = len(scenes)
        long_sil = sorted([s for s in sil if s[1] - s[0] >= 1.0 and 0.5 < s[0] and s[1] < total - 0.5],
                          key=lambda s: s[1] - s[0], reverse=True)
        if len(long_sil) < n - 1:
            raise SystemExit(f"[녹음] 장면 사이 1초 이상 쉼이 {len(long_sil)}곳뿐인데 장면은 {n}개입니다. "
                             f"장면 사이를 2초 정도 쉬어 다시 녹음하거나, 장면별 파일(01.wav…)로 넣어주세요.")
        cuts = sorted(long_sil[:n - 1])
        bounds = [0.0] + [(a + b) / 2 for a, b in cuts] + [total]
        for sc, s0, s1 in zip(scenes, bounds, bounds[1:]):
            sc.start, sc.dur = s0, s1 - s0
            sc.lines = _split_lines(s0, s1, sil, len(sc.narration), sc.narration)
        _check(scenes, log)
        return full, "통녹음(full)"

    if per:
        missing = [sc.idx for sc in scenes if sc.idx not in per]
        if missing:
            raise SystemExit(f"[녹음] 장면별 파일이 빠졌습니다: {missing}")
        t = 0.0
        for sc in scenes:
            p = per[sc.idx]
            d = ffprobe_dur(p) + 0.35
            sc.start, sc.dur = t, d
            sc.lines = _split_lines(0, d - 0.35, silences(p), len(sc.narration), sc.narration)
            t += d
        _check(scenes, log)
        return [per[sc.idx] for sc in scenes], "장면별 파일"

    # 가이드 모드
    t = 0.0
    for sc in scenes:
        cur, lines = SCENE_PAD[0], []
        for x in sc.narration:
            d = est_line(x)
            lines.append((cur, cur + d))
            cur += d + LINE_GAP
        sc.start, sc.lines = t, lines
        sc.dur = max(cur - LINE_GAP + SCENE_PAD[1], sc.spec.get("min_dur", 3.0))
        t += sc.dur
    return None, "가이드(녹음 없음, 길이 추정)"


def _check(scenes, log):
    for sc in scenes:
        est = sum(est_line(x) for x in sc.narration) + LINE_GAP * max(0, len(sc.narration) - 1)
        r = sc.dur / max(est, 0.1)
        flag = "  ← 확인 필요" if r < 0.6 or r > 1.8 else ""
        log(f"  장면 {sc.idx:02d}: {sc.dur:5.1f}s (예상 {est:4.1f}s){flag}")


# ── 자막 ─────────────────────────────────────────────────────────
def chunks(text, max_chars=32):
    """긴 문장을 자막 조각으로 나눈다. 가운데에 가까운 쉼표·마침표 뒤를 우선.
    대본에 ' | '를 넣으면 그 위치에서 직접 끊는다(녹음 대본에서는 지워짐)."""
    if "|" in text:
        return [p.strip() for p in text.split("|") if p.strip()]
    if len(text) <= max_chars:
        return [text]
    words = text.split(" ")
    total = len(text)
    best, best_score, acc = 1, 1e9, 0
    for i in range(1, len(words)):
        acc += len(words[i - 1]) + 1
        score = abs(acc - total / 2)
        prev, nxt = words[i - 1], words[i]
        if prev[-1:] in ",.?!":
            score -= total * 0.15  # 문장부호 뒤에서 끊는 걸 선호
        if prev[-1:] in "%" or prev[-1:].isdigit() or nxt[:1].isdigit():
            score += total * 0.2   # '20% | 이상', '2026년 | 9월' 같은 숫자 덩어리는 붙여두기
        if min(acc, total - acc) < 9:
            score += total          # 너무 짧은 조각 방지
        if score < best_score:
            best, best_score = i, score
    return chunks(" ".join(words[:best]), max_chars) + chunks(" ".join(words[best:]), max_chars)


def cues(scenes):
    """[(global_start, global_end, text)]"""
    out = []
    for sc in scenes:
        for (s, e), text in zip(sc.lines, sc.narration):
            parts = chunks(text)
            w = [max(1, syllables(p)) for p in parts]
            tot, acc = sum(w), s
            for p, wi in zip(parts, w):
                d = (e - s) * wi / tot
                out.append((sc.start + acc, sc.start + acc + d, p))
                acc += d
    return out


def write_srt(cs, path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(path, "w", encoding="utf-8") as fp:
        for i, (a, b, t) in enumerate(cs, 1):
            fp.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
