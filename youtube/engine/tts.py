"""AI 음성(TTS) 생성. 문장마다 따로 만들어 캐시하고, 장면·문장 타이밍을 정확히 맞춘다.

  provider: google
  인증: 클라우드 환경의 Network secrets 에 texttospeech.googleapis.com / 헤더 X-Goog-Api-Key 로 키 등록
        (요청에 키가 자동으로 붙음). 로컬 PC에서는 환경 변수 GOOGLE_TTS_API_KEY 로도 가능.
  voice 예: ko-KR-Chirp3-HD-Charon (남), ko-KR-Chirp3-HD-Kore (여), ko-KR-Neural2-C (남), ko-KR-Neural2-A (여)
  목소리 목록·샘플: python tools/tts_voices.py
"""
import base64
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.request
import wave
from pathlib import Path

import numpy as np

SR = 48000
API = "https://texttospeech.googleapis.com/v1"


def _headers():
    h = {"Content-Type": "application/json"}
    k = os.environ.get("GOOGLE_TTS_API_KEY")
    if k:  # 로컬 실행용. 클라우드에서는 Network secrets 가 헤더를 자동으로 붙임
        h["X-Goog-Api-Key"] = k
    return h


def _call(url, body=None, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:300]
        if e.code in (401, 403):
            raise SystemExit(f"Google TTS 인증 실패({e.code}). Network secrets 설정(허용 웹사이트 "
                             f"texttospeech.googleapis.com, 헤더 X-Goog-Api-Key)과 API 사용 설정을 확인하세요.\n{msg}")
        raise RuntimeError(f"Google TTS 오류 {e.code}: {msg}")


def _post(path, body):
    return _call(f"{API}/{path}", body)


def list_voices(lang="ko-KR"):
    return _call(f"{API}/voices?languageCode={lang}", timeout=30).get("voices", [])


def synth(text, voice, rate=1.0, pitch=0.0, cache_dir=Path("."), lang="ko-KR"):
    """문장 하나 → mp3 파일 경로 (같은 문장·목소리면 캐시 재사용 → 다시 만들어도 무료 사용량 안 씀)"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(json.dumps([text, voice, rate, pitch, "markup-v1"]).encode()).hexdigest()[:16]
    out = cache_dir / f"{h}.mp3"
    if out.exists():
        return out
    cfg = {"audioEncoding": "MP3", "sampleRateHertz": 24000}
    if abs(rate - 1.0) > 1e-3:
        cfg["speakingRate"] = rate
    if pitch and "Chirp" not in voice:
        cfg["pitch"] = pitch
    if "Chirp3" in voice:  # Chirp3는 쉼표에서 거의 안 쉼 → 쉼 표시(markup)로 실제 쉼을 넣음
        import re
        mk = re.sub(r",\s+", ", [pause short] ", text)
        inp = {"markup": mk}
    else:
        inp = {"text": text}
    body = {"input": inp, "voice": {"languageCode": lang, "name": voice}, "audioConfig": cfg}
    try:
        res = _post("text:synthesize", body)
    except RuntimeError as e:
        if "speakingRate" in cfg and "rate" in str(e).lower():  # 속도 조절 미지원 목소리
            cfg.pop("speakingRate")
            res = _post("text:synthesize", body)
        else:
            raise
    out.write_bytes(base64.b64decode(res["audioContent"]))
    return out


# 음성용 발음 사전 (자막 글자는 그대로, 읽는 소리만 바뀜). 에피소드 tts.say 로 추가 가능
SAY = {
    "TQQQ": "티큐큐큐", "SQQQ": "에스큐큐큐", "QQQ": "큐큐큐", "ETF": "이티에프", "S&P500": "에스앤피 오백",
    "VIX": "빅스", "AI": "에이아이",
}


def speakable(text, extra=None):
    """TTS가 어색하게 읽는 표현을 소리 내기 좋은 형태로 바꾼다."""
    import re
    t = text.replace(" | ", " ").replace("|", "")
    for k, v in sorted({**SAY, **(extra or {})}.items(), key=lambda kv: -len(kv[0])):
        t = t.replace(k, v)
    t = re.sub(r"(?<![\w.])-(\d)", r"마이너스 \1", t)      # -80% → 마이너스 80%
    t = re.sub(r"(?<![\w.])\+(\d)", r"플러스 \1", t)      # +4% → 플러스 4%
    t = t.replace("…", ",").replace("...", ",")
    t = re.sub(r"(\S)\?\s", r"\1? ", t)
    # 조사 바로 뒤 극적인 쉼표("1억이, 450원")는 소리로는 어색 → 제거
    t = re.sub(r"([가-힣])(이|가|은|는|을|를|도),\s(?=[\d가-힣])", r"\1\2 ", t)
    t = re.sub(r",\s*,", ",", t).strip(" ,")
    return t


def _pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def plan(scenes, cfg, work_dir: Path, log=print):
    """각 장면에 start/dur/lines를 채우고 내레이션 wav 경로 반환"""
    voice = cfg.get("voice", "ko-KR-Chirp3-HD-Charon")
    rate = cfg.get("rate", 1.0)
    gap = cfg.get("line_gap", 0.28)          # 문장 사이 쉼
    lead, tail = cfg.get("scene_pad", [0.2, 0.45])
    cache = work_dir / "tts_cache"
    clips, t = [], 0.0
    for sc in scenes:
        sc.start = t
        cur, lines = lead, []
        for text in sc.narration:
            clean = speakable(text, cfg.get("say"))
            pcm = _pcm(synth(clean, voice, rate, cfg.get("pitch", 0.0), cache))
            # 앞뒤 무음 다듬기
            nz = np.where(np.abs(pcm) > 0.01)[0]
            if len(nz):
                pcm = pcm[max(0, nz[0] - 480): nz[-1] + 2400]
            d = len(pcm) / SR
            lines.append((cur, cur + d))
            clips.append((t + cur, pcm))
            cur += d + gap
        sc.lines = lines
        sc.dur = max(cur - gap + tail, sc.spec.get("min_dur", 2.0))
        t += sc.dur
    buf = np.zeros(int(t * SR) + SR, dtype=np.float32)
    for st, pcm in clips:
        s = int(st * SR)
        buf[s:s + len(pcm)] += pcm
    out = work_dir / "tts_narration.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(buf, -1, 1) * 32767).astype("<i2").tobytes())
    log(f"  AI 음성: {voice} · 속도 {rate} · 문장 {len(clips)}개 · {t / 60:.1f}분")
    return out, f"AI 음성({voice})"
