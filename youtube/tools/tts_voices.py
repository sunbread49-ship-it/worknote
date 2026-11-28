"""구글 TTS 한국어 목소리 목록 + 같은 문장으로 샘플 mp3 만들기.

  python tools/tts_voices.py              # 목록만
  python tools/tts_voices.py --samples    # out/tts_samples/ 에 목소리별 샘플 mp3
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import tts  # noqa: E402

SAMPLE = "그런데 TQQQ는요? 3배인 12% 수익이 아니라, 20% 손실입니다. 지수는 올랐는데, 3배 상품은 돈을 잃은 거죠."

voices = sorted(tts.list_voices(), key=lambda v: v["name"])
for v in voices:
    print(f'{v["name"]:32s} {v.get("ssmlGender", "")}')
if "--samples" in sys.argv:
    out = ROOT / "out" / "tts_samples"
    for v in voices:
        if any(k in v["name"] for k in ("Chirp3-HD", "Neural2", "Wavenet")):
            p = tts.synth(SAMPLE, v["name"], 1.0, 0.0, out / "_cache")
            dst = out / f'{v["name"]}.mp3'
            dst.write_bytes(p.read_bytes())
    print("샘플 →", out)
