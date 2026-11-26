"""HyperFrames 장면 (2026-11-26 사용자: "퀄이 훨씬 좋다 · 주식/지식 둘 다 핵심 포인트 장면에 적극 활용")
HTML + GSAP 로 만든 장면을 HyperFrames(공식 heygen-com/hyperframes · youtube/hf 에 설치)로 미리 렌더 →
우리 엔진은 그 프레임을 깔고 그 위에 로고 · 자막 · 출처를 얹는다. 시간은 전부 TTS 문장 시각에서 계산.

type: hf
  template: quiz | stat | headline
  theme: paper(지식 · 기본) | navy(주식)
  quiz:     kicker, question, highlight, choices[3], answer(0~), hint, countdown_on(줄), beat_line(=countdown_on), reveal_on(줄)
  stat:     kicker, value(숫자), prefix, suffix, decimals, from, sub, sub_hl, on(줄) · stamp(선택)
  headline: lines: [{text, hl, on}]  — 줄마다 다른 등장(단어 흐림 · 슬롯 굴림 · 글자별)
모션 규칙은 TEMPLATES.md 'HyperFrames' 절 (도착 느리게 · 퇴장 짧게 · 숨쉬기 반복 금지 · 착지 후 정지)
"""
import fcntl
import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image

from . import style as S
from .editorial import Editorial, TYPES

ROOT = Path(__file__).resolve().parents[1]
HF = ROOT / "hf"
FONTS = {"Myeongjo": "NanumMyeongjo-ExtraBold.ttf", "Pen": "NanumPenScript-Regular.ttf", "Pretendard": "Pretendard-Black.otf"}

THEMES = {
    "paper": {"bg": "#F7F1E4", "grid": "rgba(0,0,0,.05)", "ink": "#262834", "acc": "#E25C40", "mark": "#FFD678", "sub": "#786E5E",
              "card": "#FFFDF6", "font": "Myeongjo"},
    "navy": {"bg": "#0E1630", "grid": "rgba(255,255,255,.05)", "ink": "#F4F6FB", "acc": "#FFC93C", "mark": "#E8453C", "sub": "#9AA6C4",
             "card": "#17213F", "font": "Pretendard"},
}


def _esc(s):
    return html.escape(str(s))


def _hl(text, hl, mark_id):
    """강조어에 형광펜 띠(i#mark_id) 붙여 단어 span 으로 쪼갬"""
    out = []
    for w in str(text).split(" "):
        if hl and hl in w:
            a, b = w.split(hl, 1)
            out.append(f'<span>{_esc(a)}<b class="hlw">{_esc(hl)}<i id="{mark_id}"></i></b>{_esc(b)}</span>')
        else:
            out.append(f"<span>{_esc(w)}</span>")
    return "".join(out)


def _page(th, dur, body, css, js):
    faces = "".join(f'@font-face{{font-family:"{k}";src:url("assets/fonts/{v}");}}' for k, v in FONTS.items())
    return f"""<!doctype html><html><head><meta charset="utf-8">
<script src="assets/gsap.min.js"></script>
<style>{faces}
html,body{{margin:0;background:{th['bg']};}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{th['bg']};font-family:"{th['font']}";color:{th['ink']};}}
.abs{{position:absolute;}}
#grid{{inset:0;background-image:linear-gradient({th['grid']} 1px,transparent 1px),linear-gradient(90deg,{th['grid']} 1px,transparent 1px);background-size:60px 60px;}}
.hlw{{font-weight:inherit;position:relative;color:inherit;}}
.hlw i{{position:absolute;left:-6px;right:-6px;bottom:.08em;height:.32em;background:{th['mark']};z-index:-1;transform-origin:left center;}}
{css}
</style></head><body>
<div id="root" data-composition-id="root" data-start="0" data-duration="{dur:.3f}" data-width="1920" data-height="1080">
<div id="grid" class="abs"></div>
{body}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{js}
tl.set({{}}, {{}}, {max(0.0, dur - 0.01):.3f});
window.__timelines = window.__timelines || {{}};
window.__timelines["root"] = tl;
</script></body></html>"""


# ── 템플릿 ─────────────────────────────────────────────
def t_quiz(v, th, dur):
    ch = v["choices"]
    n = len(ch)
    cw = 500 if n <= 3 else 400
    gap = 50
    x0 = (1920 - (n * cw + (n - 1) * gap)) / 2
    cards = ""
    for i, c in enumerate(ch):
        num = "①②③④"[i]
        cards += (f'<div id="c{i}" class="abs card" style="left:{x0 + i * (cw + gap):.0f}px;width:{cw}px"><div class="inner" id="in{i}">'
                  f'<div class="face front"><span class="num">{num}</span>{_esc(c)}</div>'
                  f'<div class="face back"><span class="num">{num}</span>{_esc(c)}</div></div></div>')
    body = f"""<div id="kicker" class="abs">{_esc(v.get('kicker', '퀴즈'))}</div>
<div id="q" class="abs">{_hl(v['question'], v.get('highlight'), 'mk')}</div>
{cards}
<div id="hint" class="abs">{_esc(v.get('hint', ''))}</div>
<div id="timer" class="abs"><svg viewBox="0 0 220 220"><circle cx="110" cy="110" r="100" fill="{th['card']}" stroke="{th['ink']}" stroke-width="7"/>
<circle id="ring" cx="110" cy="110" r="86" fill="none" stroke="{th['acc']}" stroke-width="16" stroke-linecap="round" stroke-dasharray="540.35" stroke-dashoffset="0" transform="rotate(-90 110 110)"/></svg><div id="digit">3</div></div>
<div id="stamp" class="abs">정답!</div>"""
    css = f"""#kicker{{left:0;right:0;top:70px;text-align:center;font-family:"Pen";font-size:96px;color:{th['acc']};}}
#q{{left:0;right:0;top:180px;text-align:center;font-size:116px;}}
#q span{{display:inline-block;margin:0 .12em;}}
.card{{top:440px;height:330px;perspective:1400px;}}
.inner{{position:absolute;inset:0;transform-style:preserve-3d;}}
.face{{position:absolute;inset:0;border-radius:30px;display:flex;align-items:center;justify-content:center;font-size:{min(84 if cw >= 500 else 70, int((cw - 70) / max(len(c) for c in ch)))}px;backface-visibility:hidden;box-shadow:0 14px 30px rgba(0,0,0,.16);}}
.front{{background:{th['card']};border:6px solid {th['ink']};}}
.back{{background:{th['acc']};color:#fff;transform:rotateY(180deg);}}
.num{{position:absolute;left:28px;top:16px;font-size:56px;color:{th['sub']};}}
.back .num{{color:rgba(255,255,255,.75);}}
#hint{{left:0;right:0;top:820px;text-align:center;font-family:"Pen";font-size:74px;color:{th['sub']};}}
#timer{{left:1630px;top:60px;width:220px;height:220px;opacity:0;}}
#timer svg{{position:absolute;inset:0;}}
#digit{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:140px;color:{th['acc']};font-family:"Myeongjo";}}
#stamp{{left:{x0 + v['answer'] * (cw + gap) + cw - 140:.0f}px;top:370px;font-family:"Pretendard";font-size:58px;color:{th['acc']};border:7px solid {th['acc']};border-radius:18px;padding:4px 22px;background:{th['card']};opacity:0;}}"""
    C0, RV = v["C0"], v["RV"]
    wrong = json.dumps([f"#c{i}" for i in range(n) if i != v["answer"]])
    js = f"""tl.fromTo("#kicker",{{opacity:0,rotation:-6,scale:.8}},{{opacity:1,rotation:-2,scale:1,duration:.5,ease:"back.out(1.6)"}},0.05);
tl.fromTo("#q span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.067}},0.15);
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},0.75);
tl.fromTo(".card",{{opacity:0,y:90,scale:.92}},{{opacity:1,y:0,scale:1,duration:.7,ease:"back.out(1.4)",stagger:.08}},0.55);
tl.fromTo("#hint",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:.25,ease:"power3.out"}},1.6);
tl.fromTo("#timer",{{opacity:0,scale:.4,rotation:-30}},{{opacity:1,scale:1,rotation:0,duration:.5,ease:"back.out(1.7)"}},{C0 - 0.45:.3f});
for (let i=0;i<3;i++){{const t={C0:.3f}+i;
 tl.set("#digit",{{textContent:String(3-i)}},t);
 tl.fromTo("#digit",{{scale:1.7,opacity:.2}},{{scale:1,opacity:1,duration:.35,ease:"expo.out"}},t);
 tl.fromTo("#ring",{{strokeDashoffset:0}},{{strokeDashoffset:540.35,duration:.98,ease:"none"}},t);
 tl.fromTo(".card",{{y:0}},{{y:-10,duration:.12,ease:"power2.out",yoyo:true,repeat:1}},t);}}
tl.to("#timer",{{opacity:0,scale:.6,duration:.2,ease:"power3.in"}},{RV - 0.05:.3f});
tl.to({wrong},{{opacity:.35,filter:"blur(3px)",scale:.95,duration:.35,ease:"power2.out"}},{RV:.3f});
tl.to("#in{v['answer']}",{{rotationY:180,duration:.6,ease:"back.out(1.3)"}},{RV:.3f});
tl.to("#c{v['answer']}",{{scale:1.08,y:-16,duration:.6,ease:"back.out(1.6)"}},{RV:.3f});
tl.fromTo("#stamp",{{opacity:0,scale:2.2,rotation:18}},{{opacity:1,scale:1,rotation:-8,duration:.35,ease:"power4.out"}},{RV + 0.4:.3f});"""
    return body, css, js


def t_stat(v, th, dur):
    """큰 숫자 한 방: 숫자가 굴러 올라가다(슬롯) 쾅 착지 → 아래 한 줄 → 도장"""
    T0 = v["T0"]
    body = f"""<div id="kicker" class="abs">{_esc(v.get('kicker', ''))}</div>
<div id="num" class="abs"><span id="pre">{_esc(v.get('prefix', ''))}</span><span id="val">0</span><span id="suf">{_esc(v.get('suffix', ''))}</span></div>
<div id="bar" class="abs"></div>
<div id="sub" class="abs">{_hl(v.get('sub', ''), v.get('sub_hl'), 'mk')}</div>
<div id="stamp" class="abs">{_esc(v.get('stamp', ''))}</div>"""
    css = f"""#kicker{{left:0;right:0;top:180px;text-align:center;font-size:72px;color:{th['sub']};}}
#num{{left:0;right:0;top:290px;text-align:center;font-family:"Pretendard";font-size:360px;line-height:1;color:{th['acc']};letter-spacing:-6px;}}
#pre,#suf{{font-size:.6em;}}
#bar{{left:510px;width:900px;top:700px;height:10px;background:{th['acc']};transform-origin:left center;border-radius:5px;}}
#sub{{left:0;right:0;top:740px;text-align:center;font-size:88px;}}
#sub span{{display:inline-block;margin:0 .12em;}}
#stamp{{right:200px;top:250px;font-family:"Pretendard";font-size:62px;color:{th['mark']};border:8px solid {th['mark']};border-radius:20px;padding:6px 26px;opacity:0;{'display:none;' if not v.get('stamp') else ''}}}"""
    frm, to, dec = float(v.get("from", 0)), float(v["value"]), int(v.get("decimals", 0))
    js = f"""tl.fromTo("#kicker",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2,ease:"power4.out"}},0.1);
const o={{v:{frm}}}; const fmt=(x)=>{{const s=Math.abs(x).toFixed({dec}).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,",");return (x<0?"-":"")+s;}};
tl.set("#val",{{textContent:fmt({frm})}},0);
tl.fromTo("#num",{{opacity:0,scale:.7,y:40}},{{opacity:1,scale:1,y:0,duration:.5,ease:"expo.out"}},{T0:.3f});
tl.to(o,{{v:{to},duration:1.1,ease:"power3.out",onUpdate:()=>{{document.querySelector("#val").textContent=fmt(o.v);}}}},{T0:.3f});
tl.fromTo("#num",{{scale:1.12}},{{scale:1,duration:.4,ease:"back.out(2)"}},{T0 + 1.1:.3f});
tl.fromTo("#bar",{{scaleX:0}},{{scaleX:1,duration:.6,ease:"expo.out"}},{T0 + 1.1:.3f});
tl.fromTo("#sub span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.08}},{v.get('S0', T0 + 1.4):.3f});
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{v.get('S0', T0 + 1.4) + 0.4:.3f});
tl.fromTo("#stamp",{{opacity:0,scale:2.2,rotation:16}},{{opacity:1,scale:1,rotation:-7,duration:.35,ease:"power4.out"}},{v.get('ST', T0 + 2.0):.3f});"""
    return body, css, js


def t_headline(v, th, dur):
    """줄마다 다른 등장: 0=단어별 흐림, 1=강조어 슬롯 굴림, 2=글자별, 3=통째 흐림 — 이전 줄은 위로 밀리며 흐려짐"""
    lines = v["lines"]
    body = ""
    for i, ln in enumerate(lines):
        words = _hl(ln["text"], ln.get("hl"), f"mk{i}")
        body += f'<div id="L{i}" class="abs line">{words}</div>'
    css = f""".line{{left:0;right:0;top:470px;text-align:center;font-size:{v.get('size', 140)}px;line-height:1.15;opacity:0;}}
.line span{{display:inline-block;margin:0 .12em;}}
.hlw{{color:{th['acc']};}}"""
    js = ""
    for i, ln in enumerate(lines):
        t = ln["T"]
        style = ln.get("style", i % 4)
        js += f'tl.set("#L{i}",{{opacity:1}},{t:.3f});\n'
        if style == 1:
            js += f'tl.fromTo("#L{i} span",{{opacity:0,y:60}},{{opacity:1,y:0,duration:.45,ease:"expo.out",stagger:.09}},{t:.3f});\n'
        elif style == 2:
            js += f'tl.fromTo("#L{i} span",{{opacity:.15,filter:"blur(4px)",scale:1.3}},{{opacity:1,filter:"blur(0px)",scale:1,duration:.3,ease:"power4.out",stagger:.1}},{t:.3f});\n'
        elif style == 3:
            js += f'tl.fromTo("#L{i}",{{filter:"blur(10px)",scale:1.06}},{{filter:"blur(0px)",scale:1,duration:.22,ease:"power4.out"}},{t:.3f});\n'
        else:
            js += f'tl.fromTo("#L{i} span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.067}},{t:.3f});\n'
        js += f'tl.fromTo("#mk{i}",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{t + 0.45:.3f});\n'
        if i + 1 < len(lines):   # 다음 줄이 오면 위로 밀리며 흐려짐(퇴장은 짧게)
            nt = lines[i + 1]["T"]
            js += f'tl.to("#L{i}",{{y:-230,scale:.62,opacity:.35,filter:"blur(2px)",duration:.35,ease:"power3.inOut"}},{nt - 0.05:.3f});\n'
            if i >= 1:
                js += f'tl.to("#L{i - 1}",{{opacity:0,y:-330,duration:.25,ease:"power3.in"}},{nt - 0.05:.3f});\n'
    return body, css, js


TEMPLATES = {"quiz": t_quiz, "stat": t_stat, "headline": t_headline}


def build(template, v, theme, dur):
    th = THEMES.get(theme, THEMES["paper"])
    body, css, js = TEMPLATES[template](v, th, dur)
    return _page(th, dur, body, css, js)


def render_frames(page, work, dur):
    """같은 내용이면 다시 렌더하지 않음(해시). 결과: work/frames/000001.jpg …"""
    work.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(page.encode()).hexdigest()[:12]
    done = work / f"done_{key}"
    lock = open(work / ".lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        if done.exists():
            return work / "frames"
        for p in work.glob("done_*"):
            p.unlink()
        shutil.rmtree(work / "frames", ignore_errors=True)
        (work / "assets/fonts").mkdir(parents=True, exist_ok=True)
        for f in FONTS.values():
            dst = work / "assets/fonts" / f
            if not dst.exists():
                shutil.copy(ROOT / "assets/fonts" / f, dst)
        shutil.copy(HF / "node_modules/gsap/dist/gsap.min.js", work / "assets/gsap.min.js")
        (work / "index.html").write_text(page, encoding="utf-8")
        mp4 = work / "hf.mp4"
        r = subprocess.run(["npx", "hyperframes", "render", str(work), "-q", "delivery", "-w", "3", "--fps", str(S.FPS), "-o", str(mp4), "--quiet"],
                           cwd=HF, capture_output=True, text=True)
        if r.returncode != 0 or not mp4.exists():
            raise RuntimeError("HyperFrames 렌더 실패: " + (r.stderr or r.stdout)[-800:])
        (work / "frames").mkdir()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-q:v", "2", str(work / "frames/%06d.jpg")], check=True)
        done.write_text(str(dur))
        return work / "frames"
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


class HFScene(Editorial):
    def _vars(self):
        sp = dict(self.spec)
        v = {k: sp[k] for k in sp if k not in ("narration", "type", "chapter")}
        tpl = sp["template"]
        if tpl == "quiz":
            bt = sp.get("_beats") or []
            cl = sp.get("countdown_on", 2)
            k = sp.get("countdown_beat", 1)
            v["C0"] = self.line_start(cl) + (bt[k] if bt and sp.get("beat_line") == cl and k < len(bt) else 0.3)
            v["RV"] = self.line_start(sp.get("reveal_on", 3)) + sp.get("reveal_offset", 0)
        elif tpl == "stat":
            v["T0"] = self.line_start(sp.get("on", 1)) + sp.get("offset", 0.2)
            if sp.get("sub_on"):
                v["S0"] = self.line_start(sp["sub_on"]) + 0.1
            if sp.get("stamp_on"):
                v["ST"] = self.line_start(sp["stamp_on"]) + 0.2
        elif tpl == "headline":
            v["lines"] = [dict(ln, T=self.line_start(ln.get("on", i + 1)) + ln.get("offset", 0.05)) for i, ln in enumerate(sp["lines"])]
        return v

    def _frames(self):
        if getattr(self, "_fdir", None) is None:
            out = Path(getattr(self, "out_dir", ROOT / "out" / "_hf"))
            work = out / "hf" / f"{getattr(self, 'idx', 0):02d}_{self.spec['template']}"
            page = build(self.spec["template"], self._vars(), self.spec.get("theme", "paper"), self.dur)
            self._fdir = render_frames(page, work, self.dur)
            self._n = len(list(self._fdir.glob("*.jpg")))
        return self._fdir

    def draw(self, f, t):
        fd = self._frames()
        i = min(self._n, max(1, int(round(t * S.FPS)) + 1))
        im = Image.open(fd / f"{i:06d}.jpg").convert("RGBA")
        if im.size != f.size:
            im = im.resize(f.size, Image.LANCZOS)
        f.paste(im, (0, 0))
        self.paper = self.spec.get("theme", "paper") == "paper"
        self.finish(f, t)

    def extra_sfx(self):
        sp = self.spec
        if sp["template"] == "quiz":
            v = self._vars()
            return [(v["C0"] + i, "tick", 0.7) for i in range(3)] + [(v["RV"], "ding", 0.8), (v["RV"] + 0.4, "pop", 0.5)]
        if sp["template"] == "stat":
            v = self._vars()
            return [(v["T0"], "count_roll", 0.6), (v["T0"] + 1.1, "boom", 0.6)] + ([(v["ST"], "pop", 0.6)] if "ST" in v else [])
        if sp["template"] == "headline":
            return [(ln["T"], "whoosh", 0.4) for ln in self._vars()["lines"]]
        return []


TYPES.update({"hf": HFScene})
