"""최단강하선 물리 계산 (마찰 없음, 미끄러짐 기준). 단위: m, s. A=(0,0) → B=(πR, -2R)"""
import numpy as np

G = 9.81


def cycloid(R=1.0, th0=0.0, th1=np.pi, n=4000):
    th = np.linspace(th0, th1, n)
    return R * (th - np.sin(th)), -R * (1 - np.cos(th))


def line(R=1.0, n=4000):
    s = np.linspace(0, 1, n)
    return np.pi * R * s, -2 * R * s


def arc(R=1.0, n=4000):
    """A에서 수직으로 떨어지기 시작해 B를 지나는 원호 (중심이 A와 같은 높이)"""
    cx = (np.pi ** 2 + 4) / (2 * np.pi) * R
    r = cx
    a1 = np.arctan2(-2 * R, np.pi * R - cx)          # B의 각도
    a = np.linspace(np.pi, 2 * np.pi + a1 if a1 < 0 else a1, n)
    return cx + r * np.cos(a), r * np.sin(a)


def times(x, y, y0=None):
    """곡선을 따라 정지 상태에서 출발 → 각 점까지 걸린 시간 배열"""
    y0 = y[0] if y0 is None else y0
    ds = np.hypot(np.diff(x), np.diff(y))
    h = np.maximum(y0 - (y[:-1] + y[1:]) / 2, 1e-12)
    v = np.sqrt(2 * G * h)
    # 첫 구간은 v≈0 특이점 → 등가속(접선 가속도) 공식으로 보정
    dt = ds / v
    a0 = G * max(1e-9, (y[0] - y[1]) / ds[0])
    dt[0] = np.sqrt(2 * ds[0] / a0)
    return np.concatenate([[0], np.cumsum(dt)])


if __name__ == "__main__":
    for name, (x, y) in {"직선": line(), "원호": arc(), "사이클로이드": cycloid()}.items():
        print(name, round(times(x, y)[-1], 4), "도착점", round(x[-1], 3), round(y[-1], 3))
    print("이론 사이클로이드 π√(R/g) =", round(np.pi * np.sqrt(1 / G), 4), " 직선 √(π²+4)·√(R/g) =", round(np.sqrt(np.pi**2 + 4) / np.sqrt(G), 4))
    for th0 in (0.0, 0.8, 1.6, 2.4):  # 등시성: 사이클로이드 어디서 놓아도 바닥(θ=π)까지 같은 시간
        x, y = cycloid(th0=th0)
        print("출발 θ", th0, "→ 바닥", round(times(x, y)[-1], 4))
