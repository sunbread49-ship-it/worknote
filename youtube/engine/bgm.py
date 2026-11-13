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


# ══ 2026-11-13: 장(챕터) 분위기에 맞춰 바뀌는 배경음 (사용자: "잔잔하다 → 흥미진진 · 두근두근 · 쫄깃하게") ══
def _kit(rng):
    kt = np.arange(int(0.28 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-kt * 24) + 46) / SR) * np.exp(-kt * 12)
    ht = np.arange(int(0.05 * SR)) / SR
    hat = np.diff(rng.normal(0, 1, len(ht) + 1)) * np.exp(-ht * 100) * 0.16
    ct = np.arange(int(0.18 * SR)) / SR
    clap = rng.normal(0, 1, len(ct)) * (np.exp(-ct * 30) + 0.4 * np.exp(-np.maximum(0, ct - 0.012) * 40)) * 0.22
    return kick, hat, clap


def _tone(f, d, dec, harm=(1, 0.35, 0.12)):
    tt = np.arange(int(d * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * f * (i + 1) * tt) for i, a in enumerate(harm))
    return x * np.exp(-tt * dec) * np.minimum(1, tt / 0.004)


def _saw(f, d, dec=3.0, n=7):
    return _tone(f, d, dec, tuple(0.6 / (k + 1) for k in range(n)))


def mood(kind, duration, seed=5):
    """kind: tense(쫄깃 · 긴장) | drive(흥미진진 · 탐색) | dark(무겁게 · 심장박동) | hope(밝게 · 설렘)"""
    rng = np.random.default_rng(seed)
    n = int(duration * SR) + SR
    out = np.zeros(n)

    def add(at, sig, g=1.0):
        s = int(at * SR)
        if s >= n:
            return
        e = min(n, s + len(sig))
        out[s:e] += sig[:e - s] * g

    kick, hat, clap = _kit(rng)
    if kind == "hope":
        return None
    bpm = {"tense": 104, "drive": 112, "dark": 76}[kind]
    beat = 60 / bpm
    prog = {"tense": [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]],   # Am F Dm E
            "drive": [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],   # Am F C G
            "dark": [[57, 60, 64], [53, 57, 60], [57, 60, 64], [52, 56, 59]]}[kind]
    nb = int(duration / beat) + 4
    for b in range(nb):
        at, bar = b * beat, b // 4
        ch = prog[bar % 4]
        root = ch[0] - 24
        if kind == "tense":
            add(at, kick, 0.5 if b % 2 == 0 else 0.0)
            if b % 4 == 3:
                add(at + beat * 0.5, kick, 0.35)
            for q in range(2):   # 8분 펄스 베이스 (쫄깃)
                add(at + q * beat / 2, _saw(_hz(root + 12 * (q % 2 == 1 and b % 2 == 1)), beat / 2 * 0.9, 9), 0.11)
            for q in range(4):
                add(at + q * beat / 4, hat, 0.55 if q % 2 else 0.3)
            pat = [ch[0] + 24, ch[1] + 24, ch[2] + 24, ch[1] + 24]
            add(at, _tone(_hz(pat[b % 4]), 0.3, 10), 0.07)
            add(at + beat / 2, _tone(_hz(pat[(b + 2) % 4]), 0.3, 10), 0.05)
            if bar % 4 == 3 and b % 4 == 0:   # 4마디마다 긴장 상승(라이저)
                L = int(beat * 4 * SR)
                tt = np.arange(L) / SR
                add(at, np.sin(2 * np.pi * np.cumsum(np.linspace(300, 1200, L)) / SR) * np.linspace(0, 0.05, L))
        elif kind == "drive":
            add(at, kick, 0.55)
            if b % 2 == 1:
                add(at, clap, 0.6)
            add(at + beat / 2, hat, 0.7)
            add(at + beat / 2, _saw(_hz(root + 12), beat / 2 * 0.8, 7), 0.10)   # 오프비트 베이스
            for q in range(4):
                m = ch[[0, 2, 1, 2][q]] + 24
                add(at + q * beat / 4, _tone(_hz(m), 0.25, 12), 0.06 if q else 0.08)
        elif kind == "dark":
            add(at, kick, 0.55 if b % 2 == 0 else 0.0)        # 쿵-쿵 심장박동
            add(at + beat * 0.3, kick, 0.3 if b % 2 == 0 else 0.0)
            if b % 4 == 0:
                d = beat * 4
                for m in (root, root + 7, root + 12):
                    add(at, _tone(_hz(m), d, 0.4, (1, 0.3)), 0.07)
            if b % 2 == 1 and rng.random() < 0.6:
                add(at, _tone(_hz(ch[rng.integers(3)] + 12), 1.4, 2.5), 0.06)
    return out[:int(duration * SR)]


def scored(duration, path, cues, xfade=2.0):
    """cues: [(시작 초, kind)] → 분위기별 트랙을 겹쳐 만들고 구간마다 2초 크로스페이드"""
    import tempfile
    from pathlib import Path
    L = int(duration * SR)
    mix = np.zeros(L)
    kinds = sorted({k for _, k in cues})
    for k in kinds:
        if k == "hope":
            tmp = Path(tempfile.mkdtemp()) / "h.wav"
            bright(duration + 1, tmp)
            with wave.open(str(tmp)) as w:
                x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, 2)[:, 0].astype(np.float64) / 32767
        else:
            x = mood(k, duration + 1)
        x = x[:L] if len(x) >= L else np.pad(x, (0, L - len(x)))
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 0.12      # 분위기마다 크기 맞춤
        g = np.zeros(L)
        for i, (t0, kk) in enumerate(cues):
            if kk != k:
                continue
            t1 = cues[i + 1][0] if i + 1 < len(cues) else duration
            a, b = int(max(0, t0 - xfade / 2) * SR), int(min(duration, t1 + xfade / 2) * SR)
            env = np.ones(b - a)
            f = int(xfade * SR)
            if t0 > 0:
                env[:f] = np.linspace(0, 1, min(f, len(env)))[:len(env[:f])]
            if t1 < duration:
                env[-f:] = np.linspace(1, 0, min(f, len(env)))[-len(env[-f:]):]
            g[a:b] = np.maximum(g[a:b], env)
        mix += x * g
    fi, fo = int(0.5 * SR), int(3 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.6
    stereo = np.stack([mix, np.roll(mix, int(0.01 * SR))], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype("<i2").tobytes())
    return path
