"""화면 · 음성 싱크 자동 점검 (2026-11-13 사용자 피드백: "둘째 얘기할 때 셋째가 먼저 뜬다 · 화면이 한 줄씩 빠르다")

각 장면에서 'on: N'(N번째 문장에서 등장)이 붙은 요소의 글자와 내레이션 문장을 비교해,
그 내용을 실제로 말하는 문장 번호와 on이 다르면 알려 준다. --fix 면 에피소드 yaml의 on 값을 고친다.

  python tools/sync_check.py episodes/ep014_pension_kjh          → 점검만
  python tools/sync_check.py episodes/ep014_pension_kjh --fix    → yaml 수정
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

LISTS = ("items", "rows", "kpis", "bullets", "layers", "steps", "bands", "chips")
SINGLES = ("left", "right", "bar", "target", "total", "ghost")
FIELDS = ("text", "label", "title", "value", "sub", "highlight", "big")


def _norm(t):
    t = re.sub(r"\*\*|!!|\[낮게\]|\s//?\s|\|", " ", str(t))
    return re.sub(r"[^가-힣0-9%.]", "", t)


def _grams(t):
    t = _norm(t)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def _elements(sc):
    out = []
    for k in LISTS:
        for it in sc.get(k, []) or []:
            if isinstance(it, dict) and "on" in it:
                out.append((k, it))
    for k in SINGLES:
        it = sc.get(k)
        if isinstance(it, dict) and "on" in it:
            out.append((k, it))
    for it in (sc.get("chart", {}) or {}).get("marks", []) or []:
        if "on" in it:
            out.append(("marks", it))
    return out


def check(ep):
    found = []
    for si, sc in enumerate(ep["scenes"], 1):
        nar = sc.get("narration", [])
        if len(nar) < 2 or sc.get("type") in ("kinetic", "outro", "title"):
            continue
        lines = [_grams(x) for x in nar]
        # 첫째 · 둘째 · 셋째가 있으면 목록 k번째 = k번째 서수가 나오는 문장 (가장 확실한 기준)
        ords = {}
        for i, x in enumerate(nar, 1):
            for k, w in enumerate(("첫째", "둘째", "셋째", "넷째"), 1):
                if w in x and k not in ords:
                    ords[k] = i
        for k_ in LISTS:
            lst = [it for it in sc.get(k_, []) or [] if isinstance(it, dict) and "on" in it]
            if len(lst) >= 2 and len(ords) >= len(lst):
                for k, it in enumerate(lst, 1):
                    if int(it["on"]) != ords[k]:
                        txt = " ".join(str(it[f]) for f in FIELDS if it.get(f))
                        found.append((si, k_, txt[:40], int(it["on"]), ords[k], 1.0))
                sc = dict(sc, **{k_: []})   # 아래 일반 비교에서는 제외
        for kind, it in _elements(sc):
            txt = " ".join(str(it[f]) for f in FIELDS if it.get(f))
            g = _grams(txt)
            if len(g) < 3:
                continue
            sc_ = [len(g & L) / len(g) for L in lines]
            best = max(range(len(sc_)), key=lambda i: sc_[i]) + 1
            on = int(it["on"])
            # 앞 문장에서 이미 같은 말을 했으면(소개 문장 등) 더 뒤를 고르지 않음
            if sc_[best - 1] < 0.35 or abs(sc_[best - 1] - sc_[on - 1 if on <= len(sc_) else 0]) < 0.12:
                continue
            if best != on:
                found.append((si, kind, txt[:40], on, best, sc_[best - 1]))
    return found


def fix(ep_dir, found):
    p = Path(ep_dir) / "episode.yaml"
    s = p.read_text(encoding="utf-8")
    blocks = s.split("\n- type: ")
    n = 0
    for si, kind, txt, on, best, _ in found:
        b = blocks[si]
        key = re.sub(r"\s.*", "", txt)[:8]
        lines = b.split("\n")
        for i, ln in enumerate(lines):
            if key in ln and re.search(r"'?on'?: %d\b" % on, ln):
                lines[i] = re.sub(r"('?on'?): %d\b" % on, r"\g<1>: %d" % best, ln, count=1)
                n += 1
                break
        blocks[si] = "\n".join(lines)
    p.write_text("\n- type: ".join(blocks), encoding="utf-8")
    return n


def main(ep_dir, do_fix=False, quiet=False):
    import render as R
    ep, _ = R.load(Path(ep_dir).resolve())
    found = check(ep)
    rows = [f"[장면 {si:02d}] {kind} '{txt}' — on: {on} 인데 {best}번째 문장에서 말함 ({'화면이 빠름' if on < best else '화면이 늦음'})"
            for si, kind, txt, on, best, _ in found]
    if do_fix and found:
        print(f"싱크 고침 {fix(ep_dir, found)}곳")
    if not quiet:
        print("\n".join(rows) or "싱크 문제 없음")
    return rows


if __name__ == "__main__":
    main(sys.argv[1], "--fix" in sys.argv)
