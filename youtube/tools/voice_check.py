"""음성 자동 점검 (2026-11-12 사용자 요청: "검수를 일일이 보기 힘들다 → 처음부터 자연스럽게")

렌더 전에 Claude가 먼저 돌려서, 사용자가 듣기 전에 고친다.
  python tools/voice_check.py episodes/ep014_pension_kjh      → out/<ep>/음성점검.txt

점검 항목
  [글자] 읽기 변환 후에도 숫자 · 영어 · 기호가 남은 곳 (TTS가 제멋대로 읽을 위험)
  [글자] 말꼬리 조각("~처럼요." "~까지요.")처럼 음정이 튀기 쉬운 끝맺음, 사전에 '점' 띄어 쓴 소수, [pause] 남발
  [소리] 문장 중간의 긴 끊김(쉼표 · 쉼 표시가 없는데 0.3초 넘게 멈춤)
  [소리] 말 속도가 다른 문장보다 25% 넘게 빠르거나 느림
  [소리] 질문이 아닌데 끝 음정이 올라감 / 질문인데 끝이 뚝 떨어짐(참고)
기준 · 규칙은 VOICE_RULES.md
"""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import tts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SR = 16000


def _pcm(path):
    import subprocess
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def _f0(x):
    """40ms 창마다 자기상관으로 기본 주파수(Hz) · 무성음은 0"""
    w, hop = int(SR * 0.04), int(SR * 0.01)
    out = []
    for i in range(0, len(x) - w, hop):
        fr = x[i:i + w] - x[i:i + w].mean()
        e = (fr ** 2).sum()
        if e < 1e-3:
            out.append(0.0)
            continue
        ac = np.correlate(fr, fr, "full")[w - 1:]
        lo, hi = SR // 300, SR // 70
        k = lo + int(np.argmax(ac[lo:hi]))
        out.append(SR / k if ac[k] / ac[0] > 0.45 else 0.0)
    return np.array(out)


def _pauses(x, thr=0.012, min_s=0.3):
    env = np.convolve(np.abs(x), np.ones(160) / 160, "same")
    quiet = env < thr
    runs, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) / SR >= min_s:
                runs.append((start / SR, i / SR))
            start = None
    nz = np.where(~quiet)[0]
    if len(nz):
        runs = [r for r in runs if r[0] > nz[0] / SR + 0.05 and r[1] < nz[-1] / SR - 0.05]
    return runs


STT_URL = "https://speech.googleapis.com/v1/speech:recognize"


def stt(x, cache):
    """음성 → 글자 (Google Speech-to-Text · 키는 환경 Network secrets가 자동 첨부). 결과는 캐시."""
    import base64
    import hashlib
    import json
    import urllib.request
    h = hashlib.sha1(x.tobytes()).hexdigest()[:16]
    if h in cache:
        return cache[h]
    pad = np.zeros(SR // 2, np.float32)   # 앞뒤 무음 0.5초: 없으면 첫 · 끝 단어를 자주 놓침
    raw = (np.clip(np.concatenate([pad, x, pad]), -1, 1) * 32767).astype("<i2").tobytes()
    body = {"config": {"encoding": "LINEAR16", "sampleRateHertz": SR, "languageCode": "ko-KR", "model": "latest_long"},
            "audio": {"content": base64.b64encode(raw).decode()}}
    r = urllib.request.Request(STT_URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(r, timeout=90).read())
    txt = " ".join(a["alternatives"][0]["transcript"] for a in res.get("results", []))
    if not txt.strip():   # 가끔 빈 결과 → 한 번 더
        res = json.loads(urllib.request.urlopen(r, timeout=90).read())
        txt = " ".join(a["alternatives"][0]["transcript"] for a in res.get("results", []))
    cache[h] = txt
    return txt


def _norm(t):
    t = re.sub(r"[A-Za-z][A-Za-z&]*\d*", " ", t)   # 영어 약어(S&P500 · IMF)는 받아쓰기가 영어로 적으므로 비교에서 뺌
    t = tts.speakable(t)                       # 받아쓴 숫자(18.3)도 같은 규칙으로 한글로
    return re.sub(r"[^가-힣]", "", t)


def stt_diff(spoken, heard):
    """대본 읽기 vs 받아쓰기: 일치율과 다른 부분"""
    import difflib
    a, b = _norm(spoken), _norm(heard)
    sm = difflib.SequenceMatcher(None, a, b)
    diffs = [f"'{a[i1:i2]}'→'{b[j1:j2]}'" for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal" and (i2 - i1 > 1 or j2 - j1 > 1)]
    return sm.ratio(), diffs


TAIL = re.compile(r"(처럼|같이|보다|까지|부터|만큼|대로|이라도|라도)요[.?!]?$")


def text_lint(raw, spoken, say):
    w = []
    s = re.sub(r"\[[^\]]*\]", "", spoken)
    if re.search(r"\d", s):
        w.append("숫자가 그대로 남음 → 읽기 사전/규칙 필요: " + ", ".join(sorted(set(re.findall(r"\d[\d.,]*\S?", s))))[:80])
    eng = [t for t in re.findall(r"[A-Za-z][A-Za-z&]+", s)]
    if eng:
        w.append("영어가 남음 → 한글 읽기 지정: " + ", ".join(sorted(set(eng))))
    if re.search(r"[~()/·]", re.sub(r"\s//?\s", " ", s)):
        w.append("기호(~ ( ) / ·)가 남음 → 소리가 이상할 수 있음")
    last = re.split(r"\s//?\s|[|]", raw.strip())[-1].strip()
    if TAIL.search(last.replace("**", "").replace("!!", "")):
        w.append("말꼬리 조각으로 끝남(음정이 튀기 쉬움) → 완결된 문장으로 ('~처럼요.' → '~도 그랬어요.')")
    return w


def main(ep_dir, quiet=False, use_stt=True):
    import render as R
    ep_dir = Path(ep_dir).resolve()
    ep, _ = R.load(ep_dir)
    cfg = ep.get("tts", {})
    say = cfg.get("say", {}) or {}
    voice, rate = cfg.get("voice", "ko-KR-Chirp3-HD-Umbriel"), cfg.get("rate", 1.15)
    cache = ROOT / "out" / ep_dir.name / "tts_cache"
    rows, stats = [], []
    for k, v in say.items():
        if re.search(r"\d\s*점\s|\s점\s", str(v)):
            rows.append(f"[사전] '{k}: {v}' — 소수를 띄어 쓰면 '점' 앞뒤가 끊겨 들림. 사전에서 빼면 자동 규칙(사십육점일)이 처리")
        if "[pause]" in str(v):
            rows.append(f"[사전] '{k}: {v}' — [pause]는 길고 어색함. 쉼표(짧은 쉼)나 ' // '를 쓸 것")
    import json
    sc_path = ROOT / "out" / ep_dir.name / "stt_cache.json"
    stt_cache = json.loads(sc_path.read_text(encoding="utf-8")) if sc_path.exists() else {}
    n = 0
    for si, sc in enumerate(ep["scenes"], 1):
        for text in sc.get("narration", []):
            n += 1
            text = re.sub(r"(첫째|둘째|셋째|넷째),\s", r"\1 / ", text)
            spoken = " / ".join(tts.speakable(p, say) for p in re.split(r"\s//?\s", text))
            warn = text_lint(text, spoken, say)
            mp3 = None
            if cfg.get("provider") == "gemini":
                mp3 = tts.gemini_line(text, cfg, cache, log=lambda *a: None)
            elif re.search(r"\s//?\s", text):
                mp3 = tts._pieces(text, voice, rate, cfg, cache)
            else:
                mp3 = tts.synth(tts.speakable(text, say), voice, rate, cfg.get("pitch", 0.0), cache)
            x = _pcm(mp3)
            nz = np.where(np.abs(x) > 0.01)[0]
            x = x[nz[0]:nz[-1]] if len(nz) else x
            dur = len(x) / SR
            syl = len(re.findall(r"[가-힣]", spoken))
            sps = syl / max(dur, 0.1)
            commas = len(re.findall(r"[,.?!|]|\s//?\s", text))   # 원문 기준 (조사 뒤 쉼표는 읽기에서 지워도 자연스럽게 쉼)
            ps = _pauses(x)
            if len(ps) > commas:
                warn.append(f"쉼표 없는 곳에서 끊김 {len(ps) - commas}번 (" + ", ".join(f"{a:.1f}초" for a, _ in ps[:3]) + ")")
            f0 = _f0(x)
            v = f0[f0 > 0]
            if len(v) > 20:
                med = np.median(v)
                tailv = f0[-int(0.45 / 0.01):]
                tailv = tailv[tailv > 0]
                if len(tailv) > 5:
                    rise = np.median(tailv[-6:]) / med
                    q = spoken.rstrip().endswith("?")
                    if not q and rise > 1.18:
                        warn.append(f"질문이 아닌데 끝 음정이 올라감(+{(rise - 1) * 100:.0f}%) → 끝맺음 바꾸기('~요.' 대신 '~어요/~죠' 완결형)")
            if use_stt:
                try:
                    heard = stt(x, stt_cache)
                    ratio, diffs = stt_diff(re.sub(r"\s//?\s|[|]|\[낮게\]|\*\*|!!", " ", text), heard)
                    if ratio < 0.85 and diffs:
                        warn.append(f"받아쓰기와 다름(일치 {ratio * 100:.0f}%): " + ", ".join(diffs[:4]) + f"  · 들린 말: {heard[:60]}")
                except Exception as e:  # 키 · 네트워크 문제면 받아쓰기만 건너뜀
                    use_stt = False
                    rows.append(f"[받아쓰기] 생략: {str(e)[:80]}")
            stats.append((n, si, sps))
            rows.append((n, si, text, spoken, warn, sps))
    sc_path.write_text(json.dumps(stt_cache, ensure_ascii=False, indent=1), encoding="utf-8")
    med = np.median([s for _, _, s in stats])
    out, bad = [], 0
    for r in rows:
        if isinstance(r, str):
            out.append(r)
            bad += 1
            continue
        n, si, text, spoken, warn, sps = r
        if sps > med * 1.25 and len(re.findall(r"[가-힣]", spoken)) > 25:
            warn.append(f"다른 문장보다 빠름 ({sps:.1f} vs 보통 {med:.1f}음절/초) → 쉼표나 ' / '로 호흡")
        elif sps < med * 0.75:
            warn.append(f"다른 문장보다 느림 ({sps:.1f} vs {med:.1f}음절/초)")
        if warn:
            bad += 1
            out.append(f"{n:3d}번 [장면 {si:02d}] {text}\n      읽기: {spoken}\n      → " + "\n      → ".join(warn))
    rep = ROOT / "out" / ep_dir.name / "음성점검.txt"
    rep.write_text(f"음성 자동 점검 · 문장 {n}개 · 확인 필요 {bad}곳 · 보통 속도 {med:.1f}음절/초\n\n" + "\n\n".join(out), encoding="utf-8")
    if quiet:
        print(f"음성 자동 점검: 문장 {n}개 중 확인 필요 {bad}곳 → {rep}")
    else:
        print(rep.read_text(encoding="utf-8"))
    return bad


if __name__ == "__main__":
    main(sys.argv[1])
