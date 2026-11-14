"""AI 음성(TTS) 생성. 문장마다 따로 만들어 캐시하고, 장면·문장 타이밍을 정확히 맞춘다.

  provider: google
  인증: 클라우드 환경의 Network secrets 에 texttospeech.googleapis.com / 헤더 X-Goog-Api-Key 로 키 등록
        (요청에 키가 자동으로 붙음). 로컬 PC에서는 환경 변수 GOOGLE_TTS_API_KEY 로도 가능.
  voice 예: ko-KR-Chirp3-HD-Charon (남), ko-KR-Chirp3-HD-Kore (여), ko-KR-Neural2-C (남), ko-KR-Neural2-A (여)
  목소리 목록·샘플: python tools/tts_voices.py
"""
import base64
import re
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
    "VIX": "빅스", "9·11": "구일일", "AI": "에이아이", "SOXL": "속슬",
    "무려, 302배": "무려, 삼백, 이 배", "302배": "삼백 이 배",
    "%p": "퍼센트포인트",
    "연예인급": "연예인끕", "역대급": "역대끕", "국가대표급": "국가대표끕", "재벌급": "재벌끕",  # 된소리 (EP014)
    "OECD": "오이씨디", "IRP": "아이알피", "KB": "케이비", "GDP": "지디피", "CEO": "씨이오", "CFO": "씨에프오",  # 2026-11-11: 퍼센트피 → 퍼센트포인트
}


_DIG = "영일이삼사오육칠팔구"


def hangul_num(n):
    """정수 → 한자어 수 읽기 (1억 8천 → 일억 팔천에 쓰임). 1 앞의 '일'은 십·백·천에서 생략."""
    if n == 0:
        return "영"
    out = ""
    for big, name in ((10 ** 8, "억"), (10 ** 4, "만"), (1, "")):
        part, n = divmod(n, big)
        if not part:
            continue
        s = ""
        for unit, un in ((1000, "천"), (100, "백"), (10, "십"), (1, "")):
            d, part = divmod(part, unit)
            if d:
                s += ("" if (d == 1 and un) else _DIG[d]) + un
        out += s + name
    return out


def _money_words(t):
    """'1억 8천만 원', '1,000만 원', '30억' 같은 금액을 붙여 읽는 한글로 ('일억팔천만 원')"""
    import re
    unit = r"(억|천만|백만|만|천)"

    def one(m):
        n = int(m.group(1).replace(",", ""))
        return hangul_num(n) + m.group(2)
    # '4천8백만', '3천1백7십만' 처럼 숫자+천/백/십이 섞인 금액 → 한 덩어리 한글 (삼천백칠십만 · EP007 피드백)
    def mixed(m):
        v = 0
        for d, u in re.findall(r"(\d+)([천백십])", m.group(1)):
            v += int(d) * {"천": 1000, "백": 100, "십": 10}[u]
        tail = re.sub(r"^(?:\d+[천백십])+", "", m.group(1))
        v += int(tail) if tail else 0
        return hangul_num(v) + (m.group(2) or "")
    t = re.sub(r"(?<![\d.])((?:\d+[천백십])+\d*)(만|억)(?=[\s원이을은가도의에,.?!]|$)", mixed, t)
    t = re.sub(r"(?<![\d.])(\d[\d,]*)" + unit + r"(?=[\s원이을은가도의에만,.?!]|$)", one, t)
    t = re.sub(r"억\s+(?=[일이삼사오육칠팔구십백천]+(천만|천|만))", "억", t)  # 일억 팔천 → 일억팔천
    return t


_N1 = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
_N10 = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]


def native_count(n, ordinal=False):
    """횟수 읽기: 19번 → 열아홉 번, 20번 → 스무 번, 1번째 → 첫 번째"""
    if ordinal and n == 1:
        return "첫"
    if n == 20:
        return "스무"
    t, o = divmod(n, 10)
    return _N10[t] + _N1[o]


def _numbers_ko(t):
    """피드백으로 정한 숫자 읽기 규칙 (SCRIPT_STYLE.md 참고)"""
    import re
    # 횟수: N번째 / N번 → 고유어 (99 이하)
    t = re.sub(r"(?<![\d.])(\d{1,2})번째", lambda m: native_count(int(m.group(1)), True) + " 번째", t)
    t = re.sub(r"(?<![\d.])(\d{1,2})번(?!째)", lambda m: native_count(int(m.group(1))) + " 번", t)
    # 연도·기간: N년 → 한자어로 붙여 읽기 (1990년엔 → 천구백구십년엔, 76년 → 칠십육년)
    t = re.sub(r"(?<![\d.,])(\d{1,4})년", lambda m: hangul_num(int(m.group(1))) + "년", t)
    # 날짜: 3월 16일엔 → 삼월 십육일엔 (숫자와 '일엔/일에' 사이가 끊겨 읽히는 문제 · EP005 피드백)
    _mon = {6: "유월", 10: "시월"}
    t = re.sub(r"(?<![\d.,])(\d{1,2})월", lambda m: _mon.get(int(m.group(1)), hangul_num(int(m.group(1))) + "월"), t)
    t = re.sub(r"(?<![\d.,])(\d{1,2})일(?=[가-힣\s,.!?]|$)", lambda m: hangul_num(int(m.group(1))) + "일", t)
    # 'N조 달러' → 붙여 읽기 (오조달러 · EP009 피드백)
    t = re.sub(r"(?<![\d.,])(\d+)조\s*달러", lambda m: hangul_num(int(m.group(1))) + "조달러", t)
    t = re.sub(r"(?<![\d.,])(\d+)조(?=[\s,.]|$)", lambda m: hangul_num(int(m.group(1))) + "조", t)
    # 쉼표 숫자: 7,568 → 칠천오백육십팔
    t = re.sub(r"(?<![\d.])(\d{1,3}(?:,\d{3})+)(?![\d.])", lambda m: hangul_num(int(m.group(1).replace(",", ""))), t)
    # "-30%에 사도" → 에와 사를 붙여 자연스럽게
    t = re.sub(r"%에 (사|팔)", r"%에\1", t)
    # 2026-11-12 (EP014): 남은 숫자를 TTS에 맡기지 않고 직접 읽기로 바꿈
    t = re.sub(r"(?<![\d.,])(\d+)\s?%", lambda m: hangul_num(int(m.group(1))) + " 퍼센트", t)          # 13% → 십삼 퍼센트
    t = re.sub(r"(?<![\d.,])(\d+)층", lambda m: hangul_num(int(m.group(1))) + "층", t)                    # 1층 → 일층
    t = re.sub(r"(?<![\d.,])(\d{1,2})배", lambda m: (native_count(int(m.group(1))) if int(m.group(1)) <= 10 else hangul_num(int(m.group(1)))) + " 배", t)  # 4배 → 네 배 · 15배 → 십오 배
    t = re.sub(r"(?<![\d.,])(\d{1,2})\s?(명|가지|개|살|마리|군데|시간|가구)", lambda m: (native_count(int(m.group(1))) if int(m.group(1)) < 100 else hangul_num(int(m.group(1)))) + " " + m.group(2), t)  # 3가지 → 세 가지
    t = re.sub(r"([가-힣])(\d+)(?![\d.,])", lambda m: m.group(1) + " " + hangul_num(int(m.group(2))), t)   # 코스피200 → 코스피 이백
    t = re.sub(r"(?<![\d.,])(\d+)(?![\d.,])", lambda m: hangul_num(int(m.group(1))), t)                    # 그 밖의 숫자는 한자어로
    # 띄어 읽기 → 붙여 읽기
    for a, b in (("년 치", "년치"), ("다음 해", "다음해"), ("전 해", "전해"), ("1등", "일뜽")):
        t = t.replace(a, b)
    return t


def speakable(text, extra=None):
    """TTS가 어색하게 읽는 표현을 소리 내기 좋은 형태로 바꾼다."""
    import re
    t = text.replace("[낮게]", "").replace(" | ", " ").replace("|", "").replace("**", "").replace("!!", "")  # 자막 강조 표시 제거
    # 소수 끝자리 0은 읽지 않음: 2.60억 → 2.6억, 3.70억 → 3.7억, 1.0억 → 1억 (EP011 피드백)
    t = re.sub(r"(\d+\.\d*?[1-9])0+(?=\s?억)", r"\1", t)
    t = re.sub(r"(\d+)\.0+(?=\s?억)", r"\1", t)
    for k, v in sorted({**SAY, **(extra or {})}.items(), key=lambda kv: -len(kv[0])):
        t = t.replace(k, v)
    t = re.sub(r"(?<![\w.])-(\d)", r"마이너스 \1", t)      # -80% → 마이너스 80%
    t = re.sub(r"(?<![\w.])\+(\d)", r"플러스 \1", t)      # +4% → 플러스 4%
    t = t.replace("…", ",").replace("...", ",")
    t = re.sub(r"[\'\"‘’“”]", "", t)                      # 따옴표는 소리로 쉼을 만들어 어색 → 제거
    # 소수: 46.1% → 사십육점일 퍼센트 · 9.5% → 구점오 퍼센트 · 8.3배 → 팔점삼 배 ('점' 앞뒤가 끊겨 들림 · EP014 피드백)
    # 2026-11-13: 소수점은 말하듯 '쩜' (구쩜오 퍼센트 · 오쩜일배 · 사용자 피드백 "점이 아니라 쩜")
    t = re.sub(r"(?<![\d.,])(\d+)\.(\d+)(?![\d.])", lambda m: hangul_num(int(m.group(1))) + "쩜" + "".join(_DIG[int(c)] for c in m.group(2)) + " ", t)
    t = re.sub(r" +(%|퍼센트)", " 퍼센트", t)
    t = re.sub(r"쩜([영일이삼사오육칠팔구]+) (?=[억만배조년])", r"쩜\1", t)
    t = _money_words(t)
    t = re.sub(r"억(?=[이일][백천십만])", "억 ", t)   # 이억이백만 → 이억 이백만 ('이이백'으로 끌림 · EP014)
    t = _numbers_ko(t)
    t = re.sub(r"(\S)\?\s", r"\1? ", t)
    # 조사 바로 뒤 극적인 쉼표("1억이, 450원")는 소리로는 어색 → 제거
    t = re.sub(r"([가-힣])(이|가|은|는|을|를),\s(?=[\d가-힣])", r"\1\2 ", t)
    t = re.sub(r",\s*,", ",", t).strip(" ,")
    return t


def _pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def _pieces(text, voice, rate, cfg, cache):
    parts = re.split(r"\s(//?)\s", text)
    pcm = []
    for i, seg in enumerate(parts):
        if i % 2:
            pcm.append(np.zeros(int(SR * (0.3 if seg == "//" else 0.12)), dtype=np.float32))
            continue
        a = _pcm(synth(speakable(seg, cfg.get("say")), voice, rate, cfg.get("pitch", 0.0), cache))
        nz = np.where(np.abs(a) > 0.01)[0]
        pcm.append(a[max(0, nz[0] - 240): nz[-1] + 1200] if len(nz) else a)
    key = [speakable(p_, cfg.get("say")) if i % 2 == 0 else p_ for i, p_ in enumerate(parts)]   # 읽기 규칙이 바뀌면 다시 만듦
    out = cache / (hashlib.sha1(json.dumps([key, voice, rate], ensure_ascii=False).encode()).hexdigest()[:16] + ".pcs.wav")
    if not out.exists():
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(np.concatenate(pcm), -1, 1) * 32767).astype("<i2").tobytes())
    return out


def plan(scenes, cfg, work_dir: Path, log=print):
    """각 장면에 start/dur/lines를 채우고 내레이션 wav 경로 반환"""
    # 2026-11-11 두 채널 통일: 남자 15번(Umbriel) 1.15배 — 롱폼 · 쇼츠 모두 (에피소드 tts에 따로 적으면 그게 우선)
    voice = cfg.get("voice", "ko-KR-Chirp3-HD-Umbriel")
    rate = cfg.get("rate", 1.15)
    gap = cfg.get("line_gap", 0.28)          # 문장 사이 쉼
    lead, tail = cfg.get("scene_pad", [0.2, 0.45])
    cache = work_dir / "tts_cache"
    clips, t = [], 0.0
    for sc in scenes:
        sc.start = t
        cur, lines = lead, []
        for text in sc.narration:
            # 첫째 · 둘째 · 셋째는 따로 떼어 차분하게 (쉼표 억양 · [pause] 모두 어색 · EP013 · EP014 피드백)
            text = re.sub(r"(첫째|둘째|셋째|넷째),\s", r"\1 / ", text)
            if re.search(r"\s//?\s", text):   # ' / ' 짧은 쉼(0.12초) · ' // ' 긴 쉼(0.3초): 조각마다 따로 만들어 이어 붙임
                mp3 = _pieces(text, voice, rate, cfg, cache)
            else:
                mp3 = synth(speakable(text, cfg.get("say")), voice, rate, cfg.get("pitch", 0.0), cache)
            if text.lstrip().startswith("[낮게]"):
                # soft(기본): 음 높이는 그대로, 5% 느리게 · 살짝 작게 → 기계음 없음 (EP013 피드백)
                # pitch: 음 높이 -1.2음 + 6% 느리게 (EP012에서 사용, rubberband 특유의 기계음이 남)
                mode = cfg.get("low", "soft")
                low = mp3.with_suffix(".low.wav" if mode == "pitch" else ".soft.wav")
                af = "rubberband=pitch=0.93:formant=preserved,atempo=0.94" if mode == "pitch" else "atempo=0.95,volume=0.9"
                if not low.exists():
                    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-af", af, str(low)], check=True)
                mp3 = low
            pcm = _pcm(mp3)
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


# ══ Gemini TTS (2026-11-14 사용자 결정: 블라인드 테스트에서 '압도적으로' 자연스러움 → 두 채널 모두 사용) ══════════
# 키: 환경 Network secrets — generativelanguage.googleapis.com / 헤더 x-goog-api-key (요청에 자동으로 붙음)
GEMINI_MODEL = "gemini-2.5-flash-preview-tts"   # pro 모델은 긴 글에서 502가 잦음
GEMINI_STYLE = ("다음 한국어 대본을 그대로 읽어 줘. 경제 유튜브 진행자 말투로, 친구에게 이야기하듯 자연스럽고 생생하게. "
                "{speed} 숫자는 또렷하게, 질문은 진짜 궁금한 듯이, 반전 앞에서는 한 박자 쉬어 줘.")
GEMINI_SPEED = {"보통": "차분하지만 지루하지 않은 보통 속도로.", "빠르게": "템포 빠르고 경쾌하게, 쇼츠처럼 몰입감 있게."}


def gemini_text(text, extra=None):
    """Gemini용 가벼운 다듬기: 자막 표시 · 쉼 표시 제거 + 발음 사전 + 소수 '쩜' (나머지 숫자는 Gemini가 자연스럽게 읽음)"""
    t = re.sub(r"\s//?\s", " ", text).replace("[낮게]", "").replace(" | ", " ").replace("|", "").replace("**", "").replace("!!", "")
    for k, v in sorted({**SAY, **(extra or {})}.items(), key=lambda kv: -len(kv[0])):
        t = t.replace(k, v)
    t = re.sub(r"(?<![\d.,])(\d+)\.(\d+)(?![\d.])", lambda m: hangul_num(int(m.group(1))) + "쩜" + "".join(_DIG[int(c)] for c in m.group(2)), t)
    return t.strip()


def gemini_synth(text, voice="Umbriel", speed="보통", cache_dir=Path("."), style=None, take=0):
    """문장/문단 → wav(24kHz) 경로. 같은 입력이면 캐시. take를 바꾸면 다시 만든다(어색할 때 재시도)."""
    import time
    cache_dir.mkdir(parents=True, exist_ok=True)
    prompt = (style or GEMINI_STYLE).format(speed=GEMINI_SPEED.get(speed, speed))
    h = hashlib.sha1(json.dumps([text, voice, prompt, GEMINI_MODEL, take], ensure_ascii=False).encode()).hexdigest()[:16]
    out = cache_dir / f"g_{h}.wav"
    if out.exists():
        return out
    body = {"contents": [{"parts": [{"text": prompt + "\n\n대본:\n" + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    last = None
    for k in range(6):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                res = json.loads(r.read())
            pcm = base64.b64decode(res["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            with wave.open(str(out), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(24000)
                w.writeframes(pcm)
            return out
        except Exception as e:  # 429(잠깐 많음) · 502(서버) → 잠시 뒤 재시도
            last = e
            time.sleep(10 + 10 * k)
    raise RuntimeError(f"Gemini TTS 실패: {last}")
