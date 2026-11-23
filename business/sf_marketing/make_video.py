"""쇼츠 팩토리 마케팅 영상 mp4 — ① 릴스 홍보(1080x1920) ③ 사용설명서(1920x1080)
장면 이미지(make_mk.py, MK_VIDEO=1 → out_video/) + Gemini 내레이션(Shorts-Factory server/voice.py)
장면 길이 = 그 장면 내레이션 길이 + 여백. 2026-11-23 사용자: 릴스 태오(Fenrir) · 사용설명서 수아(Despina) · 둘 다 1.15배
실행: MK_VIDEO=1 python3 make_mk.py && python3 make_video.py   (Gemini 음성 하루 한도를 채널 렌더와 같이 씀 → 먼저 확인)
"""
import os
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
SF = next((p for p in (Path("/home/user/Shorts-Factory"), Path("/home/user/shorts-factory")) if p.exists()), None)
sys.path.insert(0, str(SF / "server"))
import voice  # noqa: E402

IMG = D / "out_video"
TMP = D / "out_video" / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
SPEED = 1.15
PAD = {"sf_reel": (0.08, 0.2), "sf_guide": (0.3, 0.45)}   # 장면 앞뒤 여백(초) · 릴스는 빠르게

# (화면 글, 읽는 법) — 읽는 법이 비면 글 그대로
REEL = [
    ("아직도 쇼츠, 직접 자르세요? 롱폼 한 편에 몇 시간씩.", ""),
    ("이제 풀영상 링크나 파일 하나만 넣으면 끝.", ""),
    ("AI가 재밌는 구간만 골라서 30~60초로 잘라 줘요.", "에이아이가 재밌는 구간만 골라서 삼십 초에서 육십 초로 잘라 줘요."),
    ("자막이랑 헤드 문구까지 자동으로.", ""),
    ("템플릿 5종, 목소리 10종. 내 스타일로 고정까지.", "템플릿 다섯 종, 목소리 열 종. 내 스타일로 고정까지."),
    ("고칠 건 손가락으로 쓱.", ""),
    ("롱폼 한 편으로 쇼츠 최대 다섯 개. 한 달 쇼츠 25편이 9,900원. 쇼츠 팩토리, 프로필 링크에서.",
     "롱폼 한 편으로 쇼츠 최대 다섯 개. 한 달 쇼츠 이십오 편이 구천구백 원. 쇼츠 팩토리, 프로필 링크에서."),
]
GUIDE = [
    ("쇼츠 팩토리 사용법을 알려 드릴게요. 풀영상 링크나 파일 하나로 쇼츠를 만들어 봐요.", ""),
    ("먼저 풀영상 링크를 붙여넣고 생성을 누르거나, 아래 칸에 영상 파일을 끌어다 놓고 생성을 눌러요. 30분 이하 영상까지 가능해요.",
     "먼저 풀영상 링크를 붙여넣고 생성을 누르거나, 아래 칸에 영상 파일을 끌어다 놓고 생성을 눌러요. 삼십 분 이하 영상까지 가능해요."),
    ("만들 쇼츠 개수를 1개부터 5개까지 고르고, 템플릿을 골라요. 고른 개수만큼 크레딧이 빠져요.",
     "만들 쇼츠 개수를 한 개부터 다섯 개까지 고르고, 템플릿을 골라요. 고른 개수만큼 크레딧이 빠져요."),
    ("생성 전에 체크 세 개를 해 주세요. 권리가 있는 영상만 올리고, 올릴 때 원본 출처를 꼭 표시해요.", ""),
    ("이제 공장이 돌아가요. AI가 받아쓰고, 재밌는 구간을 골라 쇼츠를 만들어요.",
     "이제 공장이 돌아가요. 에이아이가 받아쓰고, 재밌는 구간을 골라 쇼츠를 만들어요."),
    ("쇼츠가 나오면 카드마다 제목과 설명이 추천돼요. 다운로드를 누르면 바로 받을 수 있어요.", ""),
    ("고치고 싶으면 편집을 눌러요. 헤드 문구, 자르기, 자막 박스 위치까지 바꿀 수 있어요.", ""),
    ("AI 목소리를 넣고 싶으면 목소리와 배속을 고르세요. 마음에 들면 내 스타일로 고정해 두세요.",
     "에이아이 목소리를 넣고 싶으면 목소리와 배속을 고르세요. 마음에 들면 내 스타일로 고정해 두세요."),
    ("크레딧은 쇼츠 한 개에 하나. 못 만든 건 돌려드려요. 그럼 첫 쇼츠 만들어 볼까요?", ""),
]


def run(*a):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def build(name, lines, imgs, vid, size, zoom):
    w, h = size
    HEAD, TAIL = PAD[name]
    clips = []
    for i, ((text, reading), img) in enumerate(zip(lines, imgs), 1):
        wav, sc = voice.line(text, reading, voice=vid)
        a = TMP / f"{name}_{i:02d}.wav"
        # 1.15배 · 앞 여백 · 뒤 여백 (48k 스테레오)
        run("-i", str(wav), "-af", f"atempo={SPEED},adelay={int(HEAD * 1000)}:all=1,apad=pad_dur={TAIL},aresample=48000",
            "-ac", "2", str(a))
        t = dur(a)
        fr = int(round(t * 30))
        if zoom:   # 아주 천천히 다가가기
            vf = (f"scale={w * 2}:{h * 2},zoompan=z='min(1+0.0009*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={fr}:s={w}x{h}:fps=30,format=yuv420p")
        else:
            vf = f"scale={w}:{h},fps=30,format=yuv420p"
        c = TMP / f"{name}_{i:02d}.mp4"
        run("-loop", "1", "-i", str(img), "-i", str(a), "-vf", vf, "-frames:v", str(fr),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest", str(c))
        clips.append(c)
        print(name, i, f"{t:.2f}s", "일치율", sc)
    lst = TMP / f"{name}.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    out = D / f"{name}.mp4"
    run("-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out))
    print(out, f"{dur(out):.1f}초")


if __name__ == "__main__":
    which = sys.argv[1:] or ["reel", "guide"]
    if "reel" in which:
        build("sf_reel", REEL, [IMG / f"reel_{i:02d}.jpg" for i in range(1, 8)], "Fenrir", (1080, 1920), True)
    if "guide" in which:
        build("sf_guide", GUIDE, [IMG / f"guide_{i:02d}.jpg" for i in range(1, 10)], "Despina", (1920, 1080), False)
