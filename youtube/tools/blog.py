"""영상 에피소드 → 네이버 블로그 글 (2026-11-28 사용자) · 규칙: BLOG.md

  python3 tools/blog.py episodes/ep027_cisco_dotcom            # 캡처 + 글쓰기
  python3 tools/blog.py episodes/ep027_cisco_dotcom --capture  # 캡처만 (Gemini 호출 없음)
  python3 tools/blog.py episodes/ep027_cisco_dotcom --write    # 이미 뽑은 캡처로 글만 다시

→ out/<ep>/blog/  frames/(후보 전체) · images/01.jpg… · post.html · post.md · naver.txt · tags.txt · post.json
화면은 자막만 빼고(로고 · 챕터 표시 유지) 문장마다 그 문장이 끝나갈 무렵을 캡처. 녹음이 없으면 가이드 타이밍.
글: Gemini 텍스트 모델(키는 환경 Network secrets — generativelanguage.googleapis.com)
"""
import argparse
import html
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODELS = ["gemini-pro-latest", "gemini-3.1-pro-preview", "gemini-2.5-pro", "gemini-flash-latest"]
IMG_W, IMG_H = 1280, 720


def clean(t):
    return t.replace("!!", "").replace("**", "").replace(" | ", " ").replace("|", "").strip()


# ── 1) 캡처 ──────────────────────────────────────────────────────
def capture(ep_dir, bd):
    import render as R
    if not any((ep_dir / "audio").glob("*.*")):
        R.TTS_OVERRIDE = {"enabled": False}   # 음성 비용 0 · 가이드 타이밍
    c = R.setup(ep_dir, log=lambda *a: None)
    fr = bd / "frames"
    shutil.rmtree(fr, ignore_errors=True)
    fr.mkdir(parents=True)
    cands = []
    for sc in c.scenes:
        lines = sc.lines or [(0.0, sc.dur)]
        for k, (a0, a1) in enumerate(lines):
            t = sc.start + min(sc.dur - 0.05, a0 + max(0.8, (a1 - a0) * 0.85))   # 그 문장 요소가 다 나온 뒤
            im = R.frame_at(c, t, subs=False).resize((IMG_W, IMG_H), Image.LANCZOS)
            fid = f"{sc.idx:02d}_{k + 1}"
            im.save(fr / f"{fid}.jpg", quality=88)
            txt = clean(sc.narration[k]) if k < len(sc.narration) else ""
            cands.append({"id": fid, "scene": sc.idx, "type": sc.spec.get("type"), "chapter": sc.spec.get("chapter", ""), "line": txt})
    (bd / "frames.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"캡처 {len(cands)}장 →", fr)
    return cands


# ── 2) 글쓰기 ────────────────────────────────────────────────────
def gemini(prompt):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8}}
    last = None
    for m in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
        for k in range(3):
            try:
                req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=300) as r:
                    res = json.loads(r.read())
                txt = "".join(p.get("text", "") for p in res["candidates"][0]["content"]["parts"])
                print("  글 모델:", m)
                return json.loads(txt)
            except urllib.error.HTTPError as e:
                last = f"{m} HTTP {e.code} {e.read()[:200]!r}"
                if e.code in (400, 403, 404):
                    break
                time.sleep(10 + 10 * k)
            except Exception as e:   # JSON 깨짐 · 시간 초과 → 한 번 더
                last = f"{m} {e}"
                time.sleep(5)
    raise RuntimeError("Gemini 글쓰기 실패: " + str(last))


def youtube_url(ep_name):
    try:
        up = json.loads((ROOT / "uploads.json").read_text())
        v = up.get(ep_name, {}).get("long", {})
        vid = v.get("id") or v.get("video_id")
        return f"https://youtu.be/{vid}" if vid else ""
    except Exception:
        return ""


def write(ep_dir, bd, n_img):
    import yaml
    ep = yaml.safe_load((ep_dir / "episode.yaml").read_text())
    notes = "\n".join(l[1:].strip() for l in (ep_dir / "episode.yaml").read_text().splitlines() if l.startswith("#"))
    cands = json.loads((bd / "frames.json").read_text())
    rules = (ROOT / "BLOG.md").read_text().split("## 글 스타일")[1].split("## 사람이 하는 일")[0]
    yt = ep.get("youtube", {})
    script = "\n".join(f"[{c['id']} · {c['chapter']} · {c['type']}] {c['line']}" for c in cands)
    prompt = f"""너는 주식 블로그 '주식 악어새'를 운영하는 블로거야. 아래 유튜브 영상과 같은 주제로 네이버 블로그 글을 써.
영상 대본을 옮기지 말고, 같은 사실과 숫자로 블로그 독자를 위해 새로 써. 숫자는 아래 대본 · 숫자 메모에 있는 것만 써.

# 글 스타일
{rules}

# 영상 제목
{yt.get('title') or ep.get('title')}

# 숫자 메모 (근거)
{notes}

# 영상 설명란
{yt.get('description', '')}

# 화면 캡처 후보 (id · 챕터 · 장면 종류 · 그 화면에서 나오는 말)
{script}

# 할 일
- 위 캡처 후보 중 글 흐름에 맞는 {n_img}장 안팎을 골라 본문 사이사이에 넣어(같은 장면에서 2장 이상 고르지 말 것, 퀴즈는 정답이 보이는 마지막 화면).
- 사진마다 짧은 캡션(20자 안팎)을 달아.
- 출력은 JSON 하나:
{{"title": "...", "tags": ["태그 10개, # 없이"], "intro": ["문단", ...],
  "sections": [{{"heading": "이모지 1개 + 소제목", "blocks": [{{"p": "문단"}} 또는 {{"img": "캡처 id", "caption": "..."}} 또는 {{"summary": "📌 한 줄 정리 내용"}}]}}],
  "outro": ["결론 3줄을 담은 문단", ...], "question": "댓글 질문 한 문장",
  "source": "자료 출처 · 계산 조건 한 줄", "disclaimer": "투자 권유 아님 · 과거 수익률 문구"}}
문단 안에서 강조할 숫자는 **굵게** 표시해."""
    post = gemini(prompt)
    ids = {c["id"] for c in cands}
    img_dir = bd / "images"
    shutil.rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir()
    n = 0
    for s in post["sections"]:
        for b in s["blocks"]:
            if "img" in b:
                if b["img"] not in ids:
                    b.clear()
                    continue
                n += 1
                b["file"] = f"images/{n:02d}.jpg"
                b["no"] = n
                shutil.copy(bd / "frames" / f"{b['img']}.jpg", bd / b["file"])
    post["youtube"] = youtube_url(ep_dir.name)
    (bd / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=1), encoding="utf-8")
    export(post, bd)
    print(f"글 · 사진 {n}장 →", bd / "post.html")


# ── 3) 내보내기 ──────────────────────────────────────────────────
def _b(t, mode):
    if mode == "html":
        t = html.escape(t)
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t if mode == "md" else re.sub(r"\*\*(.+?)\*\*", r"\1", t)


def export(post, bd):
    H, M, T = [], [f"# {post['title']}", ""], [post["title"], ""]
    for p in post.get("intro", []):
        H.append(f"<p>{_b(p, 'html')}</p>"); M += [p, ""]; T += [_b(p, 'txt'), ""]
    for s in post["sections"]:
        H.append(f"<h2>{html.escape(s['heading'])}</h2>"); M += [f"## {s['heading']}", ""]; T += ["", f"■ {s['heading']}", ""]
        for b in s["blocks"]:
            if "p" in b:
                H.append(f"<p>{_b(b['p'], 'html')}</p>"); M += [b["p"], ""]; T += [_b(b["p"], "txt"), ""]
            elif "file" in b:
                cap = html.escape(b.get("caption", ""))
                H.append(f'<figure><img src="{b["file"]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>')
                M += [f"![{b.get('caption', '')}]({b['file']})", f"*{b.get('caption', '')}*", ""]
                T += [f"[사진 {b['no']:02d}] {b.get('caption', '')}", ""]
            elif "summary" in b:
                H.append(f'<div class="sum">{_b(b["summary"], "html")}</div>'); M += [f"> {b['summary']}", ""]; T += [_b(b["summary"], "txt"), ""]
    H.append("<h2>마무리</h2>"); M += ["## 마무리", ""]; T += ["", "■ 마무리", ""]
    for p in post.get("outro", []):
        H.append(f"<p>{_b(p, 'html')}</p>"); M += [p, ""]; T += [_b(p, 'txt'), ""]
    if post.get("youtube"):
        H.append(f'<p class="yt">▶ 영상으로 보기: <a href="{post["youtube"]}">{post["youtube"]}</a></p>')
        M += [f"▶ 영상으로 보기: {post['youtube']}", ""]; T += [f"▶ 영상으로 보기: {post['youtube']}", ""]
    H.append(f"<p class=\"q\">{html.escape(post.get('question', ''))}</p>")
    H.append(f"<p class=\"src\">{html.escape(post.get('source', ''))}<br>{html.escape(post.get('disclaimer', ''))}</p>")
    M += [post.get("question", ""), "", f"<small>{post.get('source', '')} · {post.get('disclaimer', '')}</small>"]
    T += [post.get("question", ""), "", post.get("source", ""), post.get("disclaimer", "")]
    tags = " ".join("#" + t.replace(" ", "") for t in post.get("tags", []))
    H.append(f'<p class="tags">{html.escape(tags)}</p>'); T += ["", tags]
    page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(post['title'])}</title><style>
body{{margin:0;background:#f5f6f8;font-family:-apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#222}}
article{{max-width:720px;margin:0 auto;background:#fff;padding:40px 24px 60px;line-height:1.85;font-size:17px}}
h1{{font-size:26px;line-height:1.4;margin:0 0 28px}} h2{{font-size:20px;margin:44px 0 14px;padding-left:10px;border-left:4px solid #03c75a}}
figure{{margin:26px 0;text-align:center}} img{{max-width:100%;border-radius:6px}} figcaption{{font-size:14px;color:#888;margin-top:6px}}
.sum{{background:#f1faf4;border:1px solid #cdebd8;border-radius:8px;padding:14px 16px;margin:20px 0;font-weight:600}}
.q{{font-weight:700;margin-top:30px}} .src{{font-size:13px;color:#999}} .tags{{color:#03c75a;font-size:14px}} b{{color:#d33}}
</style></head><body><article><h1>{html.escape(post['title'])}</h1>
{chr(10).join(H)}
</article></body></html>"""
    (bd / "post.html").write_text(page, encoding="utf-8")
    (bd / "post.md").write_text("\n".join(M), encoding="utf-8")
    (bd / "naver.txt").write_text("\n".join(T), encoding="utf-8")
    (bd / "tags.txt").write_text(tags, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--capture", action="store_true", help="캡처만")
    ap.add_argument("--write", action="store_true", help="글만 (캡처 재사용)")
    ap.add_argument("--images", type=int, default=8)
    a = ap.parse_args()
    ep_dir = Path(a.episode).resolve()
    bd = ROOT / "out" / ep_dir.name / "blog"
    bd.mkdir(parents=True, exist_ok=True)
    if not a.write:
        capture(ep_dir, bd)
    if not a.capture:
        write(ep_dir, bd, a.images)


if __name__ == "__main__":
    main()
