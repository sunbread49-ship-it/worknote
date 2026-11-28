"""구간 쇼츠 제목 · 설명 파일 만들기: out/<ep>/clips/cN.txt (첫 줄 제목)
  python3 tools/clip_desc.py <ep> <롱폼 영상 ID> "#태그1 #태그2"
"""
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
ep, lid, tags = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
d = yaml.safe_load((ROOT / "episodes" / ep / "episode.yaml").read_text())
lt = (d.get("youtube") or {}).get("title") or d["title"]
sci = d.get("clip_theme") == "science"
for i, c in enumerate(d["clips"], 1):
    h = c["hook"].replace("\n", " ")
    foot = ("세상의 지식, 악어새가 쏙쏙 골라 드릴게요. 더 신기한 지식은 @악어새지식창고" if sci
            else "※ 투자 교육 목적이며 매수 · 매도 추천이 아닙니다.")
    txt = f"""{h} {tags} #shorts
{h}

▶ 풀버전: {lt}
화면 아래 '관련 동영상' 버튼을 눌러 보세요.
https://youtu.be/{lid}

{foot}

{tags} #shorts"""
    (ROOT / "out" / ep / "clips" / f"c{i}.txt").write_text(txt, encoding="utf-8")
print("쇼츠 설명", len(d["clips"]), "개 →", ROOT / "out" / ep / "clips")
