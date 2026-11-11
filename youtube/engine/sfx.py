"""코드로 합성한 효과음 (저작권 걱정 없음). 장면 YAML에서 이름으로 호출.

  pop      스티커 등장 '뽁'           whoosh   화면 전환 '슉'
  ding     수익/정답 '띵'              cash     돈 들어오는 '차-칭'
  boom     폭락/충격 '쿵'              fail     실패 '빠밤빠~' (트롬본 하강)
  riser    긴장감 상승 '슈우웅'        tick     카운트 '틱'
  scratch  반전 '끼익' (레코드 긁기)   bubble   말풍선 '뿅'
  drum     두둥                         laugh    가벼운 '뾰로롱' (웃긴 포인트)
"""
import wave

import numpy as np

SR = 48000


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    return e * np.exp(-t / max(r, 1e-4))


def _noise(n, seed=0):
    return np.random.default_rng(seed).normal(0, 1, n)


def _lp(x, k):
    k = max(1, int(k))
    return np.convolve(x, np.ones(k) / k, mode="same")


def pop():
    t = _t(0.16)
    f = 900 * np.exp(-t * 18) + 280
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.045) * 0.8


def bubble():
    t = _t(0.18)
    f = 500 + 1400 * t / 0.18
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.004, 0.07) * 0.5


def whoosh():
    t = _t(0.55)
    n = _noise(len(t), 1)
    sweep = np.sin(np.pi * t / 0.55) ** 2
    x = _lp(n, 6) - _lp(n, 40)
    return x * sweep * 0.55


def ding():
    t = _t(1.2)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in
            [(1568, 0.6, 3.5), (2349, 0.3, 4.5), (3136, 0.18, 6), (4186, 0.08, 8)])
    return x * _env(len(t), 0.002, 10) * 0.6


def cash():
    a = ding() * 0.7
    t = _t(0.25)
    clink = _noise(len(t), 3) * np.exp(-t * 30) * 0.25
    out = np.zeros(int(0.9 * SR) + len(a))
    out[:len(t)] += clink
    out[int(0.09 * SR):int(0.09 * SR) + len(a)] += a
    return out


def boom():
    t = _t(1.4)
    f = 70 * np.exp(-t * 2) + 35
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    hit = _lp(_noise(len(t), 5), 12) * np.exp(-t * 14) * 0.6
    return np.tanh((body + hit) * 1.8) * 0.9


def fail():
    out = []
    for i, (f, d) in enumerate([(392, 0.28), (370, 0.28), (349, 0.28), (330, 1.0)]):
        t = _t(d)
        vib = 1 + 0.012 * np.sin(2 * np.pi * 6 * t) * (t > 0.2)
        ph = 2 * np.pi * np.cumsum(f * vib * (1 - (0.06 * t if i == 3 else 0))) / SR
        x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
        out.append(x * _env(len(t), 0.02, d * 0.9) * 0.28)
    return np.concatenate(out)


def riser():
    t = _t(1.6)
    f = 200 * (8 ** (t / 1.6))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    n = (_lp(_noise(len(t), 7), 3) - _lp(_noise(len(t), 7), 30)) * 0.35
    return (tone + n) * (t / 1.6) ** 2


def tick():
    t = _t(0.05)
    return np.sin(2 * np.pi * 2200 * t) * _env(len(t), 0.001, 0.01) * 0.5


def scratch():
    t = _t(0.45)
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * t))
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return _lp(saw + _noise(len(t), 9) * 0.4, 4) * _env(len(t), 0.005, 0.25) * 0.45


def drum():
    out = np.zeros(int(0.9 * SR))
    for st in (0.0, 0.32):
        t = _t(0.5)
        f = 120 * np.exp(-t * 12) + 55
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
        s = int(st * SR)
        out[s:s + len(x)] += x * 0.9
    return np.tanh(out * 1.5) * 0.8


def laugh():
    out = []
    for f in (880, 1175, 1397, 1760):
        t = _t(0.09)
        out.append(np.sin(2 * np.pi * f * t) * _env(len(t), 0.003, 0.05) * 0.35)
    return np.concatenate(out)


# ── 강조용 무난한 효과음 (2026-11-11: 전환 '쓱' 대신 중요 대사 · 숫자에) ──────────────
def accent():
    """'톡' — 부드러운 나무 클릭 + 아주 짧은 저음 (긍정 · 일반 강조)"""
    t = _t(0.22)
    click = np.sin(2 * np.pi * 1800 * t) * _env(len(t), 0.001, 0.012)
    body = np.sin(2 * np.pi * (220 * np.exp(-t * 6) + 140) * t) * _env(len(t), 0.002, 0.06)
    return (click * 0.35 + body * 0.7) * 0.8


def accent_low():
    """'퉁' — 묵직하지만 휴대폰 스피커에서도 들리게 중음을 섞은 짧은 울림 (손실 · 경고 · 빨간 강조)"""
    t = _t(0.42)
    f = 160 * np.exp(-t * 5) + 90
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.003, 0.14)
    mid = np.sin(2 * np.pi * np.cumsum(f * 2.7) / SR) * _env(len(t), 0.002, 0.06) * 0.5
    snap = _lp(_noise(len(t), 3), 6) * _env(len(t), 0.001, 0.012) * 0.6
    return (body + mid + snap) * 0.95


def reveal():
    """'샤랑' — 부드러운 종소리 두 겹 (정답 · 결과 공개)"""
    t = _t(0.9)
    x = sum(np.sin(2 * np.pi * fr * t) * a for fr, a in ((880, 0.5), (1320, 0.3), (1760, 0.15)))
    return x * _env(len(t), 0.004, 0.35) * 0.55


def flyby():
    """'슈우웅~' 비행기가 지나가는 소리 (경로가 그려질 때) — 노이즈 대역이 올라갔다 내려감"""
    t = _t(1.3)
    x = _noise(len(t), 11)
    out = np.zeros_like(t)
    f = 400 + 1400 * np.sin(np.pi * t / 1.3) ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = _lp(x, 3) * (0.55 + 0.45 * np.sin(ph)) * np.sin(np.pi * t / 1.3) ** 2
    hum = np.sin(2 * np.pi * np.cumsum(180 + 60 * np.sin(np.pi * t / 1.3)) / SR) * np.sin(np.pi * t / 1.3) ** 2 * 0.25
    return (out * 0.35 + hum) * 0.9


def zip_():
    """'쓰윽' 짧은 선 긋기 (점선 직선이 그려질 때)"""
    t = _t(0.45)
    return _lp(_noise(len(t), 13), 2) * np.sin(np.pi * t / 0.45) ** 2 * 0.3


def wow():
    """'뾰-옹↑' 놀라움 상승음 (반전 · 큰 숫자 직전)"""
    t = _t(0.5)
    f = 300 * 2 ** (t / 0.5 * 1.6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.3) * 0.5


BANK = {k: v for k, v in globals().items() if k in
        "pop bubble whoosh ding cash boom fail riser tick scratch drum laugh accent accent_low reveal flyby wow".split()}
BANK["zip"] = zip_
_cache = {}


def get(name):
    if name not in _cache:
        _cache[name] = BANK[name]().astype(np.float64)
    return _cache[name]


def build_track(events, duration, path, gain=0.55):
    """events: [(time_sec, name, volume)] → 스테레오 wav"""
    n = int(duration * SR) + SR
    out = np.zeros(n)
    for t, name, vol in events:
        if name not in BANK or t < 0:
            continue
        x = get(name) * vol
        s = int(t * SR)
        e = min(n, s + len(x))
        if s < n:
            out[s:e] += x[:e - s]
    out = np.tanh(out * gain * 1.2) / 1.2
    pcm = (np.stack([out, out], 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm[: int(duration * SR)].tobytes())
    return path
