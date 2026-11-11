"""저작권 걱정 없는 배경음: 코드로 합성한 잔잔한 앰비언트 패드 + 피아노풍 아르페지오."""
import wave

import numpy as np

SR = 44100
# Am9 - Fmaj7 - C(add9) - G6  (반음 기준 MIDI 노트)
CHORDS = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 67], [48, 55, 60, 64, 62], [55, 59, 62, 64, 67]]
BASS = [45, 41, 36, 43]


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def generate(duration, path, seed=7, bar_sec=8.0):
    rng = np.random.default_rng(seed)
    n = int(duration * SR) + SR
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float64)
    nbars = int(np.ceil(n / (bar_sec * SR)))
    env_len = int(bar_sec * SR)
    xfade = int(1.5 * SR)
    for b in range(nbars):
        ci = b % len(CHORDS)
        s0 = b * env_len
        s1 = min(n, s0 + env_len + xfade)
        tt = t[s0:s1] - t[s0]
        L = s1 - s0
        env = np.minimum(1, tt / 1.5) * np.minimum(1, (L / SR - tt) / 1.5)
        seg = np.zeros(L)
        for m in CHORDS[ci]:
            f = _hz(m)
            for det in (-0.6, 0.6):  # 살짝 어긋난 두 음 → 따뜻한 코러스
                ff = f * (1 + det / 1200)
                seg += (np.sin(2 * np.pi * ff * tt) + 0.25 * np.sin(4 * np.pi * ff * tt)) * 0.05
        seg += np.sin(2 * np.pi * _hz(BASS[ci]) * tt) * 0.09
        # 아르페지오(0.5초 간격, 지수 감쇠)
        notes = CHORDS[ci] + [CHORDS[ci][1] + 12]
        step = int(0.5 * SR)
        for k in range(int(bar_sec / 0.5)):
            if rng.random() < 0.25:
                continue
            m = notes[[0, 2, 1, 3, 5, 3, 2, 4][k % 8]] + 12
            p0 = k * step
            if p0 >= L:
                break
            d = np.arange(min(int(2.0 * SR), L - p0)) / SR
            f = _hz(m)
            tone = (np.sin(2 * np.pi * f * d) + 0.3 * np.sin(4 * np.pi * f * d) + 0.1 * np.sin(6 * np.pi * f * d))
            seg[p0:p0 + len(d)] += tone * np.exp(-d * 3.2) * 0.045 * (0.7 + 0.3 * rng.random())
        out[s0:s1] += seg * env
    # 아주 약한 노이즈 질감 + 부드럽게
    out += rng.normal(0, 0.002, n)
    out = np.convolve(out, np.ones(6) / 6, mode="same")
    # 전체 페이드
    fi, fo = int(2 * SR), int(4 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    end = int(duration * SR)
    out = out[:end]
    out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.abs(out).max() + 1e-9) * 0.5
    stereo = np.stack([out, np.roll(out, int(0.012 * SR))], axis=1)
    pcm = (stereo * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def bright(duration, path, bpm=116, seed=3):
    """밝고 두근거리는 배경음 (2026-11-11: 지식창고 '신기하지?! 어?!' 느낌)
    C - G - Am - F 장조 진행 · 심장박동 같은 '쿵-쿵' 킥 · 16분 플럭 아르페지오 · 가벼운 하이햇"""
    rng = np.random.default_rng(seed)
    n = int(duration * SR) + SR
    out = np.zeros(n)
    beat = 60 / bpm
    prog = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
    bass = [36, 43, 45, 41]
    nb = int(duration / beat) + 4

    def add(at, sig):
        s = int(at * SR)
        if s >= n:
            return
        e = min(n, s + len(sig))
        out[s:e] += sig[:e - s]

    def tone(f, d, dec, harm=(1, 0.35, 0.12)):
        tt = np.arange(int(d * SR)) / SR
        x = sum(a * np.sin(2 * np.pi * f * (i + 1) * tt) for i, a in enumerate(harm))
        return x * np.exp(-tt * dec) * np.minimum(1, tt / 0.004)

    kick_t = np.arange(int(0.25 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(110 * np.exp(-kick_t * 22) + 48) / SR) * np.exp(-kick_t * 14)
    hat_t = np.arange(int(0.05 * SR)) / SR
    hat = np.diff(rng.normal(0, 1, len(hat_t) + 1)) * np.exp(-hat_t * 90) * 0.18
    for b in range(nb):
        at = b * beat
        bar = b // 4
        ch = prog[bar % 4]
        # 심장박동: 박마다 '쿵', 2·4박엔 짧은 뒤따름 '쿵'
        add(at, kick * 0.55)
        if b % 2 == 1:
            add(at + beat * 0.28, kick * 0.28)
        add(at + beat / 2, hat)
        if b % 4 == 0:
            add(at, tone(_hz(bass[bar % 4]), beat * 4, 1.2, (1, 0.2)) * 0.22)
        for q in range(4):  # 16분 플럭
            m = ch[[0, 2, 1, 3][q]] + 12
            add(at + q * beat / 4, tone(_hz(m), 0.35, 9) * (0.06 if q else 0.08) * (0.8 + 0.2 * rng.random()))
    fi, fo = int(0.3 * SR), int(1.5 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    end = int(duration * SR)
    out = out[:end]
    out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.abs(out).max() + 1e-9) * 0.55
    stereo = np.stack([out, np.roll(out, int(0.008 * SR))], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype("<i2").tobytes())
    return path
