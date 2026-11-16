"""EP017 커버드콜 — 9:16 전용 쇼츠 2개 (2026-11-17 12:00 · 21:00)
규칙: 첫 1초 가장 센 숫자 · 3초 질문 · 5초 약속 · 위쪽 제목 띠 · 중하단 큰 멘트(장면은 y 780~960 비움) · Gemini 1.12배
      · 내용 자체를 영상으로 (돈 세는 실사 · 3D 동전 탑 · 영수증) · 마무리 '친구한테 아는 척'
숫자: 롱폼 checks와 같음 (수정 주가를 실제 가격으로 복원 · 분배금 · 과세표준)

  python3 youtube/shorts9/ep017_cc.py 1 [--stills]   → youtube/out/ep017_covered_call/shorts9/s1/short.mp4
"""
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep015_ship import K, G, T, W, H, CREAM, GOLD, MINT, ROOT, vbg, big, pop, pill, bgp, disclaimer, RED, GREEN, BLUE, Image, ImageDraw, np  # noqa: E402

OUT = ROOT / "youtube" / "out" / "ep017_covered_call" / "shorts9"
MEDIA = ROOT / "youtube" / "assets" / "media"
SAY = {"__gemini__": {"voice": "Umbriel", "speed": "빠르게", "tempo": 1.12}, "JEPQ": "젭큐", "ISA": "아이에스에이",
       "코스피200": "코스피 이백", "KODEX 200": "코덱스 이백"}


@lru_cache(maxsize=2)
def _clip_frames(name, w=1080):
    # 동전 탑 + 위 합계 띠까지 (가로 15~85% · 세로 15.5~95%) — 띠가 잘리지 않게 (2026-11-16 사용자)
    h = int(w * (1080 * 0.795) / (1920 * 0.70)) // 2 * 2
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(MEDIA / name), "-vf",
                          f"fps=30,crop=iw*0.70:ih*0.795:iw*0.15:ih*0.155,scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def clip(f, name, t, y, speed=1.0):
    """가로 영상을 화면 폭에 맞춰 한 번 재생 (끝 장면 유지)"""
    fr = _clip_frames(name)
    i = min(int(t * 30 * speed), len(fr) - 1)
    f.alpha_composite(Image.fromarray(fr[i]).convert("RGBA"), (0, y))


def cta(f, t, sc, line="풀버전은 오늘 오후 4시"):
    vbg(f, "money_count_v", t, 0.66)
    big(f, "여러분 커버드콜은\n어느 계좌에?", 300, 120, hl="어느 계좌", hlc=GOLD)
    pill(f, line, 640, t, 0.2, bg=MINT, size=56)
    disclaimer(f)


# ── 쇼츠 1 (12:00): 월배당 받는 동안 원금 -5% ─────────────────────
def a1(f, t, sc):
    vbg(f, "money_count_v", t, 0.5)
    big(f, "월배당 받는 동안\n원금은", 180, 110)
    big(f, "-5%", 450, 260, col=BLUE, o=pop(t, 0.1, 0.25))
    K.credit(f, "영상: Hassas_Arts (Pixabay)")


def a2(f, t, sc):
    vbg(f, "market_crash_v", t, 0.62)
    big(f, "TIGER 나스닥100타겟데일리CC\n1,000만 원 · 2년 5개월", 150, 64)
    big(f, "들어온 분배금 +308만", 420, 92, col=GREEN, o=pop(t, 0.2))
    big(f, "계좌는 -47만", 590, 120, col=BLUE, o=pop(t, 0.9))
    K.credit(f, "영상: MrWashingt0n (Pixabay)")


def a3(f, t, sc):
    f.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 24, 255)))
    clip(f, "coins_ep017.mp4", t, 80, speed=1.6)
    if t > 2.6:
        big(f, "그래도 나스닥이 더 높다", 1010, 72, col=GOLD, o=pop(t, 2.6))


def a4(f, t, sc):
    vbg(f, "skyline_v", t, 0.62)
    big(f, "그런데 반전", 180, 100, col=GOLD)
    big(f, "분배금 72%가\n세금 0원인\n커버드콜도?", 360, 120, hl="세금 0원", hlc=GREEN, o=pop(t, 0.2))


def a5(f, t, sc):
    vbg(f, "datacenter_v", t, 0.62)
    big(f, "어떻게 사면 되는지", 260, 100)
    pill(f, "오늘 오후 4시 풀버전", 520, t, 0.3, bg=MINT, size=70)


S1 = [
    {"draw": a1, "nohead": True, "min": 2.2, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.1, "mx:2908", 0.8)],
     "narr": ["매달 분배금 받는 동안, 원금은 오히려 마이너스 5%."]},
    {"draw": a2, "nohead": True, "flash": True, "min": 2.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "ding", 0.5), (0.9, "fall_burn", 0.5)],
     "narr": ["국내 2위 나스닥 커버드콜에 1,000만 원. 분배금 308만 원 받는 사이, 계좌는 47만 원 줄었어요."]},
    {"draw": a3, "nohead": True, "flash": True, "min": 3.4, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.2, "tick", 0.4), (2.6, "reveal", 0.5)],
     "narr": ["분배금까지 다 쌓아도, 그냥 나스닥이 1,396만 원으로 더 높았죠."]},
    {"draw": a4, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "sparkle", 0.5)],
     "narr": ["그런데 반전. 분배금 72%에 세금이 안 붙는 커버드콜도 있어요."]},
    {"draw": a5, "nohead": True, "flash": True, "min": 2.0, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "pop", 0.5)],
     "narr": ["어떻게 사면 되는지, 오늘 오후 4시 풀버전에서 정리해 드릴게요."]},
    {"draw": cta, "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.05, "pop", 0.6)],
     "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]


# ── 쇼츠 2 (21:00): 같은 월배당인데 세금 107만 vs 22만 ─────────────
def receipt(f, t, x, title, rows, total, t0):
    w = 470
    m = sum(1 for i in range(len(rows) + 1) if t >= t0 + i * 0.45)
    h = 150 + m * 74 + 40
    p = Image.new("RGBA", (w, h), (250, 250, 246, 255))
    d = ImageDraw.Draw(p)
    p.alpha_composite(T(title, 34, (20, 22, 30), "Black", max_w=w - 40), (24, 30))
    d.line((24, 120, w - 24, 120), fill=(180, 180, 180, 255), width=2)
    for i, (lab, val, c) in enumerate((rows + [total])[:m]):
        y = 140 + i * 74
        tot = i == len(rows)
        if tot:
            d.line((24, y - 4, w - 24, y - 4), fill=(40, 40, 40, 255), width=3)
        p.alpha_composite(T(lab, 30 if tot else 28, (20, 22, 30), "Black" if tot else "Bold"), (24, y + 10))
        v = T(val, 40 if tot else 32, c, "Black")
        p.alpha_composite(v, (w - 24 - v.width, y + 6))
    K.drop(f, p, (x, 230), "mt", 1, blur=18)


def b1(f, t, sc):
    bgp(f, "krw_coins", t, 0.7)
    big(f, "같은 1,000만 원 · 분배금 영수증", 100, 56)
    receipt(f, t, W * 0.27, "KODEX 200타겟위클리", [("분배금", "509만", (20, 22, 30)), ("세금", "-22만", BLUE)], ("손에 쥔 돈", "487만", GREEN), 0.2)
    receipt(f, t, W * 0.73, "TIGER 배당CC", [("분배금", "694만", (20, 22, 30)), ("세금", "-107만", BLUE)], ("손에 쥔 돈", "587만", (20, 22, 30)), 0.9)
    K.credit(f, K.credit_of("krw_coins").replace("(Wikimedia Commons)", ""))


def b2(f, t, sc):
    vbg(f, "skyline_v", t, 0.62)
    big(f, "왜 22만 원뿐?", 160, 110, col=GOLD)
    big(f, "코스피200 옵션 이익은\n원래 비과세", 400, 96, hl="비과세", hlc=GREEN, o=pop(t, 0.3))


def b3(f, t, sc):
    bgp(f, "ai_two_jars", t, 0.35)
    big(f, "나스닥 · 미국형은?", 160, 100)
    big(f, "연금저축 · ISA\n안에서 사기", 380, 120, hl="연금저축 · ISA", hlc=GOLD, o=pop(t, 0.3))
    K.credit(f, "그림: AI 생성 (Gemini)")


def b4(f, t, sc):
    vbg(f, "datacenter_v", t, 0.62)
    big(f, "단, JEPQ는\n못 넣어요", 300, 140, hl="못 넣어요", hlc=RED)


def b5(f, t, sc):
    bgp(f, "john_bogle", t, 0.45, (0.5, 0.3))
    big(f, "불릴 돈이라면?", 160, 100)
    big(f, "건초 더미를\n통째로 사라", 380, 120, col=GOLD, o=pop(t, 0.3))
    big(f, "— 존 보글 (뱅가드 창업자)", 680, 50, o=pop(t, 0.6))
    K.credit(f, K.credit_of("john_bogle"))


S2 = [
    {"draw": b1, "nohead": True, "min": 3.0, "gap": 0.1, "tail": 0.2, "sfx_t": [(0.2, "tick", 0.4), (0.65, "tick", 0.4), (0.9, "tick", 0.4), (1.35, "tick", 0.4), (1.6, "mx:2182", 0.6)],
     "narr": ["같은 1,000만 원 커버드콜인데, 세금이 22만 원 대 107만 원."]},
    {"draw": b2, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "reveal", 0.5)],
     "narr": ["코스피200을 덮은 커버드콜은, 분배금 72%가 비과세거든요."]},
    {"draw": b3, "nohead": True, "flash": True, "min": 2.6, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.3, "sparkle", 0.5)],
     "narr": ["나스닥이나 미국형 커버드콜이라면, 연금저축이나 ISA 안에서 사면 세금을 미루거나 줄일 수 있어요."]},
    {"draw": b4, "nohead": True, "flash": True, "min": 1.8, "gap": 0.1, "tail": 0.1, "sfx_t": [(0.2, "fail", 0.35)],
     "narr": ["단, 미국에 상장된 젭큐는 이 계좌에 넣을 수 없어요."]},
    {"draw": b5, "nohead": True, "flash": True, "min": 2.4, "gap": 0.1, "tail": 0.15, "sfx_t": [(0.3, "accent", 0.5)],
     "narr": ["그리고 불려야 할 돈이라면, 커버드콜 말고 지수. 건초 더미를 통째로 사라는 말처럼요."]},
    {"draw": lambda f, t, sc: cta(f, t, sc, "풀버전은 채널에서"), "nohead": True, "flash": True, "min": 2.2, "gap": 0.1, "tail": 0.2,
     "sfx_t": [(0.05, "pop", 0.6)], "narr": ["좋아요 누르고, 친구한테 아는 척해 보세요!"]},
]

SETS = {1: (S1, ["월배당 받는 동안", "원금은 -5%?"], [(0, "tense"), (3, "hope")]),
        2: (S2, ["같은 월배당인데", "세금 107만 vs 22만"], [(0, "drive"), (2, "hope")])}

if __name__ == "__main__":
    n = int(sys.argv[1])
    sc, ban, cues = SETS[n]
    K.run(sc, {"kicker": "", "title": "", "banner": ban}, OUT / f"s{n}", say=dict(SAY), argv=sys.argv[2:], bgm_cues=cues)
