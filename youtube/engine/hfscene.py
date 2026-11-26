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
    "space": {"bg": "#05070F", "grid": "rgba(255,255,255,.035)", "ink": "#F2F4FA", "acc": "#FFC93C", "mark": "#3D6BFF", "sub": "#8E9AB8",
              "card": "#111933", "font": "Pretendard"},
    "navy": {"bg": "#0E1630", "grid": "rgba(255,255,255,.05)", "ink": "#F4F6FB", "acc": "#FFC93C", "mark": "#E8453C", "sub": "#9AA6C4",
             "card": "#17213F", "font": "Pretendard"},
}


def _esc(s):
    return html.escape(str(s))


def _hl(text, hl, mark_id):
    """강조어에 형광펜 띠(i#mark_id) 붙여 단어 span 으로 쪼갬"""
    out = []
    ws = str(text).split(" ")
    strip = lambda w: w.strip("'\"‘’“”,.?!·")
    pick = next((i for i, w in enumerate(ws) if hl and strip(w) == hl), next((i for i, w in enumerate(ws) if hl and hl in w), -1))
    for k, w in enumerate(ws):   # 형광펜은 한 단어만 (정확히 같은 단어 우선)
        if k == pick:
            a, b = w.split(hl, 1)
            out.append(f'<span>{_esc(a)}<b class="hlw">{_esc(hl)}<i id="{mark_id}"></i></b>{_esc(b)}</span>')
        else:
            out.append(f"<span>{_esc(w)}</span>")
    return "".join(out)


def _page(th, dur, body, css, js):
    faces = "".join(f'@font-face{{font-family:"{k}";src:url("assets/fonts/{v}");}}' for k, v in FONTS.items())
    return f"""<!doctype html><html><head><meta charset="utf-8">
<script src="assets/gsap.min.js"></script><script src="assets/three.min.js"></script>
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
#timer{{left:1610px;top:120px;width:220px;height:220px;opacity:0;}}
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


def t_equation(v, th, dur):
    """말 조립 도식 (11/26 사용자: 말만 하고 화면이 멈춰 지루) — 질문 → 큰 답 쾅 → 조각 분해(글자 강조) → 흔적(표지판)
    kicker, question, answer, parts:[{text, key}], signs:[...]; 시각 A0(질문) A1(답) A2(분해) A3(표지판)"""
    A0, A1, A2, A3 = v["A0"], v["A1"], v["A2"], v["A3"]
    def tile(i, p):
        t = _esc(p["text"]); k = p.get("key", "")
        if k and k in p["text"]:
            a, b = p["text"].split(k, 1)
            t = f'{_esc(a)}<em>{_esc(k)}</em>{_esc(b)}'
        return f'<div id="p{i}" class="tile">{t}</div>'
    parts = v["parts"]
    row = ""
    for i, p in enumerate(parts):
        if i:
            row += f'<div id="plus{i}" class="op">{_esc(v.get("op", "+"))}</div>'
        row += tile(i, p)
    row += '<div id="eq" class="op">=</div>' + f'<div id="res" class="tile res">{_esc(v["answer"])}</div>'
    signs = "".join(f'<div id="s{i}" class="sign">{_esc(x)}</div>' for i, x in enumerate(v.get("signs", [])))
    body = f"""<div id="kicker" class="abs">{_esc(v.get('kicker', ''))}</div>
<div id="qq" class="abs">{_hl(v.get('question', ''), v.get('q_hl'), 'mk')}</div>
<div id="big" class="abs">{_esc(v['answer'])}</div>
<div id="row" class="abs">{row}</div>
<div id="signs" class="abs">{signs}</div>"""
    css = f"""#kicker{{left:0;right:0;top:150px;text-align:center;font-family:"Pen";font-size:80px;color:{th['acc']};}}
#qq{{left:0;right:0;top:250px;text-align:center;font-size:110px;}}
#qq span{{display:inline-block;margin:0 .12em;}}
#big{{left:0;right:0;top:390px;text-align:center;font-size:300px;line-height:1;color:{th['acc']};}}
#row{{left:0;right:0;top:400px;display:flex;justify-content:center;align-items:center;gap:34px;}}
.tile{{background:{th['card']};border:6px solid {th['ink']};border-radius:28px;padding:22px 44px;font-size:110px;box-shadow:0 14px 30px rgba(0,0,0,.14);opacity:0;}}
.tile em{{font-style:normal;color:{th['acc']};}}
.res{{background:{th['acc']};color:#fff;border-color:{th['acc']};}}
.op{{font-size:110px;color:{th['sub']};opacity:0;}}
#signs{{left:0;right:0;top:640px;display:flex;justify-content:center;gap:50px;}}
.sign{{background:#1F5FB4;color:#fff;font-family:"Pretendard";font-size:72px;padding:16px 40px;border-radius:16px;border:6px solid #fff;box-shadow:0 0 0 4px #1F5FB4,0 14px 26px rgba(0,0,0,.2);opacity:0;}}"""
    n = len(parts)
    js = f"""tl.fromTo("#kicker",{{opacity:0,rotation:-5,scale:.8}},{{opacity:1,rotation:-2,scale:1,duration:.5,ease:"back.out(1.6)"}},{A0:.3f});
tl.fromTo("#qq span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.067}},{A0 + 0.1:.3f});
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{A0 + 0.6:.3f});
tl.fromTo("#big",{{opacity:0,scale:2.4,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.4,ease:"power4.out"}},{A1:.3f});
tl.to("#big",{{opacity:0,y:-60,scale:.7,filter:"blur(6px)",duration:.3,ease:"power3.in"}},{A2 - 0.15:.3f});
tl.to("#qq",{{y:-40,scale:.8,duration:.4,ease:"power2.inOut"}},{A2 - 0.15:.3f});"""
    for i in range(n):
        js += f'\ntl.fromTo("#p{i}",{{opacity:0,y:70,scale:.9}},{{opacity:1,y:0,scale:1,duration:.6,ease:"back.out(1.5)"}},{A2 + 0.35 * i:.3f});'
        if i:
            js += f'\ntl.fromTo("#plus{i}",{{opacity:0,scale:.5}},{{opacity:1,scale:1,duration:.3,ease:"expo.out"}},{A2 + 0.35 * i - 0.1:.3f});'
    js += f"""
tl.fromTo(".tile em",{{color:"{th['ink']}"}},{{color:"{th['acc']}",duration:.3,ease:"power2.out",stagger:.15}},{A2 + 0.35 * n + 0.1:.3f});
tl.fromTo("#eq",{{opacity:0,scale:.5}},{{opacity:1,scale:1,duration:.3,ease:"expo.out"}},{A2 + 0.35 * n + 0.3:.3f});
tl.fromTo("#res",{{opacity:0,scale:1.8,rotation:8}},{{opacity:1,scale:1,rotation:0,duration:.45,ease:"back.out(1.8)"}},{A2 + 0.35 * n + 0.5:.3f});
tl.fromTo(".sign",{{opacity:0,y:50}},{{opacity:1,y:0,duration:.55,ease:"expo.out",stagger:.12}},{A3:.3f});"""
    return body, css, js


def t_globe3d(v, th, dur):
    """실제 위성사진(NASA) 3D 지구본 — three.js · 자전 → 급정지(흔들림 · 번쩍) · 서울 표시 · 속도 태그 · 낮/밤 경계
    lon0(처음 정면 경도) · spin(초당 도) · stop_at(초, 없으면 계속) · tag(서울 옆 글자) · tag_on(초) · title · title_on · zoom(1~)"""
    tex = v.get("texture", "earth_day.jpg")
    title = _esc(v.get("title", ""))
    tag = _esc(v.get("tag", ""))
    body = f"""<canvas id="gl" width="1920" height="1080" class="abs" style="inset:0"></canvas>
<div id="flash" class="abs" style="inset:0;background:#fff;opacity:0"></div>
<div id="ttl" class="abs">{title}</div>
<div id="pin" class="abs"><div id="dot"></div><div id="tag">{tag}</div></div>"""
    css = """#grid{display:none;}
#root{background:#03050c !important;}
#ttl{left:0;right:0;top:70px;text-align:center;font-family:"Pretendard";font-size:84px;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,.6);opacity:0;}
#pin{left:0;top:0;width:0;height:0;}
#dot{position:absolute;left:-12px;top:-12px;width:24px;height:24px;border-radius:50%;background:#FFC93C;box-shadow:0 0 0 6px rgba(255,201,60,.35),0 0 30px #FFC93C;}
#tag{position:absolute;left:30px;top:-40px;white-space:nowrap;font-family:"Pretendard";font-size:56px;color:#111;background:#FFC93C;border-radius:16px;padding:6px 20px;opacity:0;}"""
    js = f"""
const W=1920,H=1080, cv=document.getElementById('gl');
const R=new THREE.WebGLRenderer({{canvas:cv,antialias:true,preserveDrawingBuffer:true}}); R.setSize(W,H,false);
const CY={float(v.get('cam_y', 0.0)):.2f}; const sc=new THREE.Scene(); const cam=new THREE.PerspectiveCamera(30,W/H,0.1,100); cam.position.set(0,{float(v.get('cam_y', -0.35)):.2f},{8.2 / float(v.get('zoom', 0.9)):.3f});
// 별(시드 고정)
let sd=7; const rnd=()=>{{sd=(sd*16807)%2147483647;return sd/2147483647;}};
const sg=new THREE.BufferGeometry(); const sp=[]; for(let i=0;i<2500;i++){{const a=rnd()*6.283,b=Math.acos(2*rnd()-1),r=40;sp.push(r*Math.sin(b)*Math.cos(a),r*Math.sin(b)*Math.sin(a),r*Math.cos(b));}}
sg.setAttribute('position',new THREE.Float32BufferAttribute(sp,3)); sc.add(new THREE.Points(sg,new THREE.PointsMaterial({{color:0xffffff,size:0.06,transparent:true,opacity:.8}})));
const tx=new THREE.TextureLoader().load('assets/{tex}'); tx.colorSpace=THREE.SRGBColorSpace; tx.anisotropy=8;
const earth=new THREE.Mesh(new THREE.SphereGeometry(2,128,128),new THREE.MeshStandardMaterial({{map:tx,roughness:.9,metalness:0}}));
const tilt=new THREE.Group(); tilt.rotation.z={float(v.get('tilt', 0.41)):.3f}; tilt.rotation.x={float(v.get('tilt_x', 0.5)):.3f}; tilt.add(earth); sc.add(tilt);
// 대기 빛
const atm=new THREE.Mesh(new THREE.SphereGeometry(2.12,64,64),new THREE.ShaderMaterial({{transparent:true,side:THREE.BackSide,blending:THREE.AdditiveBlending,
 vertexShader:'varying vec3 n;void main(){{n=normalize(normalMatrix*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}}',
 fragmentShader:'varying vec3 n;void main(){{float i=pow(0.72-dot(n,vec3(0,0,1.0)),3.0);gl_FragColor=vec4(0.35,0.6,1.0,1.0)*i*1.6;}}'}}));
sc.add(atm);
sc.add(new THREE.AmbientLight(0xffffff,{float(v.get('ambient', 0.55)):.2f}));
const sun=new THREE.DirectionalLight(0xffffff,{float(v.get('sun', 2.6)):.2f}); sun.position.set(-3,1.5,6); sc.add(sun);
const LAT={float(v.get('lat', 37.57)):.3f}*Math.PI/180, LON={float(v.get('lon', 126.98)):.3f}*Math.PI/180;
const S={{t:0}}, LON0={float(v.get('lon0', 110)):.2f}, SPIN={float(v.get('spin', 14)):.2f}, STOP={float(v['stop_at']) if v.get('stop_at') is not None else 1e9:.3f};
function rotAt(t){{const tt=Math.min(t,STOP);return (-(LON0+90)+SPIN*tt)*Math.PI/180;}}
function draw(){{
  const t=S.t; earth.rotation.y=rotAt(t);
  let shx=0,shy=0; if(t>=STOP&&t<STOP+0.6){{const k=1-(t-STOP)/0.6;shx=Math.sin(t*90)*0.06*k;shy=Math.cos(t*77)*0.05*k;}}
  cam.position.x=shx; cam.position.y=CY+shy; cam.lookAt(0,CY*0.0,0);
  R.render(sc,cam);
  const p=new THREE.Vector3(Math.cos(LAT)*Math.cos(LON)*2.02, Math.sin(LAT)*2.02, -Math.cos(LAT)*Math.sin(LON)*2.02);
  earth.localToWorld(p); const vis=p.clone().sub(cam.position).dot(p)<0; p.project(cam);
  const pin=document.getElementById('pin'); pin.style.transform='translate('+((p.x+1)/2*W)+'px,'+((1-p.y)/2*H)+'px)'; pin.style.opacity=vis?1:0;
}}
tl.to(S,{{t:{dur:.3f},duration:{dur:.3f},ease:"none",onUpdate:draw}},0);
tl.call(draw,null,0);
tl.fromTo("#ttl",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.22,ease:"power4.out"}},{float(v.get('title_on', 0.3)):.3f});
tl.fromTo("#tag",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.45,ease:"expo.out"}},{float(v.get('tag_on', 1.0)):.3f});
"""
    if v.get("stop_at") is not None:
        js += f'tl.fromTo("#flash",{{opacity:.85}},{{opacity:0,duration:.35,ease:"power3.out",immediateRender:false}},{float(v["stop_at"]):.3f});\n'
    return body, css, js


def t_bars(v, th, dur):
    """가로 막대 경주: 줄마다 막대가 자라며 숫자가 굴러 올라감 · 강조 줄(hl)은 마지막에 쾅 (주식 · 지식 공용)
    title, unit, vmax, rows:[{label, value, text, hl, T}]"""
    rows = v["rows"]
    vmax = float(v.get("vmax") or max(r["value"] for r in rows))
    n = len(rows)
    rh = min(150, 560 / max(1, n))
    y0 = 300 + (560 - rh * n) / 2
    body = f'<div id="ttl" class="abs">{_hl(v.get("title", ""), v.get("title_hl"), "mk")}</div>'
    for i, r in enumerate(rows):
        body += (f'<div id="r{i}" class="abs row" style="top:{y0 + i * rh:.0f}px;height:{rh - 26:.0f}px">'
                 f'<div class="lab">{_esc(r["label"])}</div><div class="track"><div id="b{i}" class="bar{" hl" if r.get("hl") else ""}"></div>'
                 f'<div id="v{i}" class="val">{_esc(r.get("text", ""))}</div></div></div>')
    css = f"""#ttl{{left:0;right:0;top:120px;text-align:center;font-size:84px;}}
#ttl span{{display:inline-block;margin:0 .12em;}}
.row{{left:150px;right:150px;display:flex;align-items:center;gap:30px;opacity:0;}}
.lab{{width:330px;text-align:right;font-size:{min(60, rh * 0.42):.0f}px;color:{th['ink']};}}
.track{{flex:1;position:relative;height:100%;}}
.bar{{position:absolute;left:0;top:12%;height:76%;width:100%;border-radius:18px;background:{th['sub']};transform-origin:left center;transform:scaleX(0);}}
.bar.hl{{background:{th['acc']};box-shadow:0 0 40px {th['acc']}88;}}
.val{{position:absolute;top:50%;transform:translateY(-50%);font-size:{min(64, rh * 0.45):.0f}px;color:{th['ink']};white-space:nowrap;}}"""
    js = f"""tl.fromTo("#ttl span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.067}},0.1);
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},0.6);"""
    W = 1920 - 300 - 360
    for i, r in enumerate(rows):
        k = max(0.02, r["value"] / vmax)
        t0 = r["T"]
        js += f"""
tl.fromTo("#r{i}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.35,ease:"expo.out"}},{t0:.3f});
tl.fromTo("#b{i}",{{scaleX:0}},{{scaleX:{k * 0.86:.4f},duration:{1.1 if r.get('hl') else .8},ease:"{'power2.in' if r.get('hl') else 'expo.out'}"}},{t0 + 0.1:.3f});
tl.fromTo("#v{i}",{{x:0,opacity:0}},{{x:{W * k * 0.86 + 24:.0f},opacity:1,duration:{1.1 if r.get('hl') else .8},ease:"{'power2.in' if r.get('hl') else 'expo.out'}"}},{t0 + 0.1:.3f});"""
        if r.get("hl"):
            js += f"""
tl.fromTo("#r{i}",{{scale:1}},{{scale:1.06,duration:.12,ease:"power2.out",yoyo:true,repeat:1}},{t0 + 1.2:.3f});
tl.to("#v{i}",{{color:"{th['acc']}",duration:.2}},{t0 + 1.2:.3f});"""
    return body, css, js


TEMPLATES = {"quiz": t_quiz, "stat": t_stat, "headline": t_headline, "equation": t_equation, "globe3d": t_globe3d, "bars": t_bars}


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
        shutil.copy(HF / "node_modules/three/build/three.min.js", work / "assets/three.min.js")
        tex = ROOT / "assets/photos/sn_earth_day.jpg"
        if tex.exists():
            shutil.copy(tex, work / "assets/earth_day.jpg")
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
        for k in list(sp):   # 공통: at_<이름>: [문장, 초] → <이름> = 초
            if k.startswith("at_") and isinstance(sp[k], list):
                v[k[3:]] = self.line_start(sp[k][0]) + sp[k][1]
        if isinstance(sp.get("rows"), list) and tpl not in ("bars",):
            v["rows"] = [dict(r, T=self.line_start(r.get("on", 1)) + r.get("offset", 0.05)) for r in sp["rows"]]
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
        elif tpl == "bars":
            v["rows"] = [dict(r, T=self.line_start(r.get("on", 1)) + r.get("offset", 0.05)) for r in sp["rows"]]
        elif tpl == "globe3d":
            for k in ("stop_at", "tag_on", "title_on"):
                if isinstance(sp.get(k), list):
                    v[k] = self.line_start(sp[k][0]) + sp[k][1]
        elif tpl == "equation":
            for k in ("A0", "A1", "A2", "A3"):
                on, off = sp.get(k.lower(), [1, 0.1])
                v[k] = self.line_start(on) + off
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
        if sp["template"] == "bars":
            return [(r["T"], "whoosh", 0.35) for r in self._vars()["rows"]] + [(r["T"] + 1.2, "boom", 0.5) for r in self._vars()["rows"] if r.get("hl")]
        if sp["template"] == "globe3d":
            v = self._vars()
            return [(v["stop_at"], "boom", 0.9)] if v.get("stop_at") is not None else []
        if sp["template"] == "equation":
            v = self._vars()
            return [(v["A1"], "boom", 0.5), (v["A2"], "pop", 0.4), (v["A3"], "whoosh", 0.4)]
        if sp["template"] in ("latitude", "impact", "inertia", "wave", "orbit", "bulge", "scale", "daylength"):
            v = self._vars()
            ev = [(v[k[3:]], "whoosh", 0.35) for k in sp if k.startswith("at_")]
            if sp["template"] == "impact":
                ev.append((v["stop"], "boom", 0.9))
            if sp["template"] == "wave":
                ev.append((v["hit"], "boom", 0.6))
            return ev
        if sp["template"] == "headline":
            return [(ln["T"], "whoosh", 0.4) for ln in self._vars()["lines"]]
        return []


TYPES.update({"hf": HFScene})
from . import hfscene2  # noqa: E402,F401  (그림 장면 2탄)
