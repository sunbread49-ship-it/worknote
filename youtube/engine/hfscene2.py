"""HyperFrames 그림 장면 2탄 (2026-11-27 사용자: "워딩만으로는 승부가 안 난다 · 같은 틀 두 번 금지 · 더 고급스럽게")
말하는 내용을 '움직이는 도식'으로: 위도 고리 · 계기판 급정지 · 관성(버스→지구) · 해일 단면 · 공전(낮/밤) · 적도 볼록 → 바다 이동 · 체중계 · 하루 길이 시계
시각 값은 YAML 에서 at_<이름>: [문장, 초] 로 주면 초로 바뀌어 들어옴 (hfscene.HFScene._vars)
"""
from .hfscene import TEMPLATES, _esc, _hl


def _sp(th):
    return th["acc"], th["ink"], th["sub"], th["card"]


def _title(v, th):
    return (f'<div id="ttl" class="abs" style="left:0;right:0;top:90px;text-align:center;font-size:76px;">{_hl(v.get("title", ""), v.get("title_hl"), "mk")}</div>',
            '#ttl span{display:inline-block;margin:0 .12em;}',
            'tl.fromTo("#ttl span",{opacity:0,filter:"blur(8px)"},{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.067},0.1);\n'
            'tl.fromTo("#mk",{scaleX:0},{scaleX:1,duration:.45,ease:"expo.out"},0.6);\n')


# ── 1. 위도 고리: 북쪽으로 갈수록 원이 작아진다 ─────────────────────
def t_latitude(v, th, dur):
    acc, ink, sub, card = _sp(th)
    tb, tc, tj = _title(v, th)
    import math
    cx, cy, R = 640, 600, 330
    rows = v["rows"]   # [{label, lat, kmh, T}]
    rings, labels, js = "", "", tj
    for i, r in enumerate(rows):
        la = math.radians(r["lat"])
        y = cy - R * math.sin(la)
        hw = max(2, R * math.cos(la))
        col = acc if r.get("hl") else "#9FB4E8"
        rings += (f'<ellipse id="g{i}" cx="{cx}" cy="{y:.0f}" rx="{hw:.0f}" ry="{hw * 0.2:.0f}" fill="none" stroke="{col}" stroke-width="{7 if r.get("hl") else 5}" opacity="0"/>'
                  f'<circle id="d{i}" r="{14 if r.get("hl") else 11}" fill="{col}" opacity="0" style="filter:drop-shadow(0 0 10px {col})"/>')
        order = sorted(range(len(rows)), key=lambda j: -rows[j]["lat"])
        ly = 290 + order.index(i) * (560 / max(1, len(rows) - 1))
        rings += f'<line id="ld{i}" x1="{cx + hw:.0f}" y1="{y:.0f}" x2="1060" y2="{ly + 30:.0f}" stroke="{col}" stroke-width="3" opacity="0"/>'
        labels += (f'<div id="l{i}" class="abs lab" style="top:{ly - 20:.0f}px"><span class="ln" style="background:{col}"></span>'
                   f'<b>{_esc(r["label"])}</b><em id="n{i}" style="color:{col}">0</em><small>km/h</small></div>')
        T = r["T"]
        js += (f'tl.fromTo("#g{i}",{{opacity:0,attr:{{rx:0}}}},{{opacity:1,attr:{{rx:{hw:.0f}}},duration:.7,ease:"expo.out"}},{T:.3f});\n'
               f'tl.fromTo("#l{i}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:"expo.out"}},{T + 0.1:.3f});\n'
               f'tl.fromTo("#ld{i}",{{opacity:0}},{{opacity:.8,duration:.3}},{T + 0.2:.3f});\n'
               f'tl.set("#d{i}",{{opacity:1}},{T + 0.2:.3f});\n'
               f'(function(){{const o={{v:0}};tl.to(o,{{v:{r["kmh"]},duration:1.0,ease:"power3.out",onUpdate:()=>{{document.getElementById("n{i}").textContent=Math.round(o.v).toLocaleString("en-US");}}}},{T + 0.2:.3f});}})();\n')
    # 점이 고리를 따라 돎 (속도 ∝ 반지름 → 같은 시간에 한 바퀴)
    js += f"""const RW={[max(2, R * math.cos(math.radians(r["lat"]))) for r in rows]}, RY={[cy - R * math.sin(math.radians(r["lat"])) for r in rows]};
const S={{t:0}}; tl.to(S,{{t:{dur:.3f},duration:{dur:.3f},ease:"none",onUpdate:()=>{{for(let i=0;i<RW.length;i++){{const a=S.t*1.6;const d=document.getElementById('d'+i);d.setAttribute('cx',{cx}+RW[i]*Math.cos(a));d.setAttribute('cy',RY[i]+RW[i]*0.2*Math.sin(a));}}}}}},0);
tl.fromTo("#globe",{{opacity:0,scale:.9}},{{opacity:1,scale:1,duration:.7,ease:"expo.out",transformOrigin:"{cx}px {cy}px"}},0.2);
"""
    body = tb + f"""<svg class="abs" style="inset:0" viewBox="0 0 1920 1080"><defs><radialGradient id="eg" cx="40%" cy="35%"><stop offset="0" stop-color="#3C6FD8"/><stop offset="1" stop-color="#0C1C48"/></radialGradient></defs>
<g id="globe"><circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#eg)" stroke="#5B86FF" stroke-width="3"/>
<line x1="{cx}" y1="{cy - R - 40}" x2="{cx}" y2="{cy + R + 40}" stroke="{sub}" stroke-width="3" stroke-dasharray="10 10"/></g>{rings}</svg>{labels}"""
    css = tc + f""".lab{{left:1080px;display:flex;align-items:baseline;gap:22px;font-size:54px;opacity:0;}}
.lab .ln{{display:inline-block;width:46px;height:8px;border-radius:4px;transform:translateY(-14px);}}
.lab b{{font-weight:inherit;min-width:300px;}} .lab em{{font-style:normal;font-size:80px;}} .lab small{{font-size:36px;color:{sub};}}"""
    return body, css, js


# ── 2. 계기판 급정지 ─────────────────────────────────────
def t_impact(v, th, dur):
    acc, ink, sub, card = _sp(th)
    tb, tc, tj = _title(v, th)
    import math
    ST = v["stop"]
    cx, cy, R = 960, 700, 330
    ticks = ""
    for k in range(0, 15):
        a = math.radians(180 - k * 180 / 14)
        x1, y1 = cx + R * math.cos(a), cy - R * math.sin(a)
        x2, y2 = cx + (R - (40 if k % 2 == 0 else 22)) * math.cos(a), cy - (R - (40 if k % 2 == 0 else 22)) * math.sin(a)
        ticks += f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{ink}" stroke-width="{6 if k % 2 == 0 else 3}"/>'
        if k % 2 == 0:
            xl, yl = cx + (R - 85) * math.cos(a), cy - (R - 85) * math.sin(a)
            ticks += f'<text x="{xl:.0f}" y="{yl + 12:.0f}" fill="{sub}" font-size="34" text-anchor="middle" font-family="Pretendard">{k * 100}</text>'
    body = tb + f"""<div id="shake" class="abs" style="inset:0"><svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<path d="M {cx - R} {cy} A {R} {R} 0 0 1 {cx + R} {cy}" fill="none" stroke="#1B2547" stroke-width="44"/>
<path id="arc" d="M {cx - R} {cy} A {R} {R} 0 0 1 {cx + R} {cy}" fill="none" stroke="{acc}" stroke-width="44" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
{ticks}<g id="needle" style="transform-origin:{cx}px {cy}px"><line x1="{cx}" y1="{cy}" x2="{cx - R + 70}" y2="{cy}" stroke="#FF4D4D" stroke-width="12" stroke-linecap="round"/></g>
<circle cx="{cx}" cy="{cy}" r="30" fill="{ink}"/></svg>
<div id="read" class="abs"><span id="kmh">0</span><small> km/h</small></div>
<div id="cap" class="abs">{_esc(v.get('caption', '서울의 자전 속도'))}</div></div>
<div id="flash" class="abs" style="inset:0;background:#fff;opacity:0"></div>
<div id="fly" class="abs">{_esc(v.get('fly', '그 위의 모든 건 계속 1,330km/h →'))}</div>"""
    css = tc + f"""#read{{left:0;right:0;top:470px;text-align:center;font-size:120px;color:{ink};font-family:"Pretendard";}}
#read small{{font-size:48px;color:{sub};}}
#cap{{left:0;right:0;top:200px;text-align:center;font-size:44px;color:{sub};}}
#fly{{left:0;right:0;top:760px;text-align:center;font-size:62px;color:{acc};opacity:0;}}"""
    deg = 1330 / 1400 * 180
    js = tj + f"""const K={{v:0}};
tl.to(K,{{v:1330,duration:1.4,ease:"power2.out",onUpdate:()=>{{document.getElementById('kmh').textContent=Math.round(K.v).toLocaleString('en-US');}}}},0.4);
tl.fromTo("#needle",{{rotation:0}},{{rotation:{deg:.1f},duration:1.4,ease:"power2.out"}},0.4);
tl.fromTo("#arc",{{strokeDashoffset:1}},{{strokeDashoffset:{1 - 1330 / 1400:.3f},duration:1.4,ease:"power2.out"}},0.4);
for(let i=0;i<Math.floor(({ST}-1.9)/0.12);i++){{tl.to("#needle",{{rotation:{deg:.1f}+(i%2?1.2:-1.2),duration:.06,ease:"none"}},1.9+i*0.12);}}
tl.to("#needle",{{rotation:0,duration:.28,ease:"power4.out"}},{ST:.3f});
tl.to("#arc",{{strokeDashoffset:1,duration:.28,ease:"power4.out"}},{ST:.3f});
tl.to(K,{{v:0,duration:.28,ease:"power4.out",onUpdate:()=>{{document.getElementById('kmh').textContent=Math.round(K.v).toLocaleString('en-US');}}}},{ST:.3f});
tl.fromTo("#flash",{{opacity:.8}},{{opacity:0,duration:.4,ease:"power3.out",immediateRender:false}},{ST:.3f});
for(let i=0;i<8;i++){{tl.to("#shake",{{x:(i%2?1:-1)*(22-i*2.5),y:(i%3-1)*10,duration:.05,ease:"none"}},{ST}+i*0.05);}}
tl.to("#shake",{{x:0,y:0,duration:.1}},{ST + 0.42:.3f});
tl.fromTo("#fly",{{opacity:0,x:-160,filter:"blur(10px)"}},{{opacity:1,x:0,filter:"blur(0px)",duration:.45,ease:"expo.out"}},{v['fly_at']:.3f});
"""
    return body, css, js


# ── 3. 관성: 버스 급정거 → 지구 급정거 ─────────────────────
def _person(x, y, s, col, pid):
    return (f'<g transform="translate({x} {y})"><g id="{pid}"><g class="pp" style="transform-origin:0px 0px">'
            f'<circle cx="0" cy="{-s * 1.55:.0f}" r="{s * 0.28:.0f}" fill="{col}"/>'
            f'<rect x="{-s * 0.22:.0f}" y="{-s * 1.25:.0f}" width="{s * 0.44:.0f}" height="{s * 0.8:.0f}" rx="{s * 0.18:.0f}" fill="{col}"/>'
            f'<rect x="{-s * 0.2:.0f}" y="{-s * 0.5:.0f}" width="{s * 0.15:.0f}" height="{s * 0.5:.0f}" rx="6" fill="{col}"/>'
            f'<rect x="{s * 0.05:.0f}" y="{-s * 0.5:.0f}" width="{s * 0.15:.0f}" height="{s * 0.5:.0f}" rx="6" fill="{col}"/></g></g></g>')


def t_inertia(v, th, dur):
    acc, ink, sub, card = _sp(th)
    A, B, C = v["brake"], v["earth"], v["fly"]
    bus = (f'<g id="bus"><rect x="0" y="0" width="520" height="210" rx="34" fill="#E8F0FF"/><rect x="0" y="150" width="520" height="60" rx="20" fill="{acc}"/>'
           + "".join(f'<rect x="{40 + k * 115}" y="34" width="92" height="80" rx="14" fill="#2B3B66"/>' for k in range(4))
           + '<circle cx="110" cy="215" r="38" fill="#111"/><circle cx="410" cy="215" r="38" fill="#111"/></g>')
    objs = ""
    icons = [("p1", 0), ("car", 1), ("tree", 2), ("p2", 3), ("house", 4)]
    for k, (nm, i) in enumerate(icons):
        x = 300 + i * 290
        if nm.startswith("p"):
            objs += _person(x, 800, 120, ink, nm)
        elif nm == "car":
            objs += f'<g id="car"><rect x="{x - 90}" y="730" width="180" height="60" rx="18" fill="#FF6B5B"/><rect x="{x - 55}" y="695" width="110" height="50" rx="14" fill="#FF6B5B"/><circle cx="{x - 50}" cy="795" r="20" fill="#111"/><circle cx="{x + 50}" cy="795" r="20" fill="#111"/></g>'
        elif nm == "tree":
            objs += f'<g id="tree"><rect x="{x - 12}" y="700" width="24" height="100" fill="#8A5A34"/><circle cx="{x}" cy="680" r="70" fill="#3FAF5F"/></g>'
        else:
            objs += f'<g id="house"><rect x="{x - 80}" y="680" width="160" height="120" fill="#D9C7A6"/><polygon points="{x - 100},{684} {x},{600} {x + 100},{684}" fill="#B5543C"/></g>'
    body = f"""<div id="pa" class="abs" style="inset:0"><svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<rect x="0" y="830" width="1920" height="12" fill="{sub}"/>
<g id="road">{''.join(f'<rect x="{k * 240}" y="880" width="120" height="10" fill="{sub}" opacity=".6"/>' for k in range(10))}</g>
<g transform="translate(700 600)"><g id="busw">{bus}{_person(300, 140, 90, '#13203F', 'rider')}</g></g></svg>
<div id="la" class="abs tagc">버스 급정거 · 시속 50km</div></div>
<div id="pb" class="abs" style="inset:0;opacity:0"><svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<rect x="0" y="800" width="1920" height="280" fill="#1E3A2A"/><rect x="0" y="796" width="1920" height="10" fill="#3FAF5F"/>
<g id="objs">{objs}</g>
<g id="lines" opacity="0">{''.join(f'<rect x="{100 + (k * 137) % 1500}" y="{560 + (k * 53) % 260}" width="{180 + (k * 31) % 160}" height="6" rx="3" fill="{ink}" opacity=".5"/>' for k in range(14))}</g></svg>
<div id="lb" class="abs tagc">지구 급정거 · 시속 1,330km</div>
<div id="lc" class="abs tagc" style="top:330px;color:{acc};font-size:120px;opacity:0">동쪽으로 →</div></div>"""
    css = f""".tagc{{left:0;right:0;top:120px;text-align:center;font-size:72px;font-family:"Pretendard";}}"""
    js = f"""tl.fromTo("#busw",{{x:-1400}},{{x:0,duration:{max(0.8, A - 0.2):.2f},ease:"power2.out"}},0.1);
tl.to("#road",{{x:-480,duration:{A:.2f},ease:"power2.out"}},0);
tl.fromTo("#la",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2}},0.3);
tl.to("#rider .pp",{{rotation:28,x:24,duration:.25,ease:"power3.out"}},{A:.3f});
tl.to("#rider .pp",{{rotation:6,x:6,duration:.6,ease:"elastic.out(1,0.5)"}},{A + 0.3:.3f});
tl.to("#busw",{{x:30,duration:.15,ease:"power2.out",yoyo:true,repeat:1}},{A:.3f});
tl.to("#pa",{{opacity:0,filter:"blur(10px)",duration:.25,ease:"power3.in"}},{B - 0.25:.3f});
tl.fromTo("#pb",{{opacity:0,scale:1.06}},{{opacity:1,scale:1,duration:.5,ease:"expo.out"}},{B:.3f});
tl.fromTo("#lines",{{opacity:0}},{{opacity:1,duration:.2}},{C:.3f});
tl.fromTo("#lines",{{x:-300}},{{x:1600,duration:1.2,ease:"power1.in"}},{C:.3f});
tl.fromTo("#lc",{{opacity:0,x:-120}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},{C:.3f});
"""
    for k, (nm, i) in enumerate(icons):
        js += f'tl.to("#{nm}",{{x:{2400 - i * 290},y:{-120 - (k % 3) * 70},rotation:{(k % 2 * 2 - 1) * 35},duration:{1.1 + k * 0.12:.2f},ease:"power2.in"}},{C + 0.15 + k * 0.08:.3f});\n'
    return body, css, js


# ── 4. 해일 단면 ─────────────────────────────────────────
def t_wave(v, th, dur):
    acc, ink, sub, card = _sp(th)
    T0, T1 = v["slosh"], v["hit"]
    body = f"""<svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<defs><linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3C8DF0"/><stop offset="1" stop-color="#0B2B66"/></linearGradient></defs>
<path id="land" d="M 1380 1080 L 1380 640 L 1560 600 L 1700 560 L 1920 540 L 1920 1080 Z" fill="#6E5A3C"/>
{''.join(f'<rect x="{1480 + k * 90}" y="{520 - (k % 3) * 40}" width="60" height="{80 + (k % 3) * 40}" fill="#C9D2E6"/>' for k in range(5))}
<path id="sea" d="M 0 700 Q 480 690 960 700 T 1380 700 L 1380 1080 L 0 1080 Z" fill="url(#wg)"/>
</svg>
<div id="t1" class="abs tg">{_esc(v.get('label', '바닷물도 시속 1,330km로'))} <b>→</b></div>
<div id="t2" class="abs tg" style="top:200px;color:{acc};opacity:0">{_esc(v.get('label2', '대륙의 동쪽 해안을 덮치는 해일'))}</div>"""
    css = f""".tg{{left:0;right:0;top:110px;text-align:center;font-size:70px;font-family:"Pretendard";opacity:0;}} .tg b{{color:{acc};}}"""
    js = f"""tl.fromTo("#t1",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.22}},0.2);
tl.to("#sea",{{attr:{{d:"M 0 760 Q 480 740 960 700 T 1380 560 L 1380 1080 L 0 1080 Z"}},duration:1.2,ease:"power2.in"}},{T0:.3f});
tl.to("#sea",{{attr:{{d:"M 0 820 Q 600 800 1100 640 Q 1300 380 1560 330 Q 1700 420 1920 470 L 1920 1080 L 0 1080 Z"}},duration:.9,ease:"power3.out"}},{T1:.3f});
tl.to("#sea",{{attr:{{d:"M 0 830 Q 600 820 1100 760 Q 1400 600 1700 520 Q 1820 500 1920 500 L 1920 1080 L 0 1080 Z"}},duration:1.4,ease:"power2.inOut"}},{T1 + 0.9:.3f});
tl.fromTo("#t2",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{T1 + 0.4:.3f});
"""
    return body, css, js


# ── 5. 공전: 멈춘 지구 = 하루가 1년 ─────────────────────────
def t_orbit(v, th, dur):
    acc, ink, sub, card = _sp(th)
    O0, O1, HC = v["orbit"], v["orbit_end"], v["hotcold"]
    cx, cy, RX, RY = 960, 590, 620, 250
    body = f"""<svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<defs><radialGradient id="sun"><stop offset="0" stop-color="#FFF4B0"/><stop offset=".5" stop-color="#FFC93C"/><stop offset="1" stop-color="#FF8A00" stop-opacity="0"/></radialGradient></defs>
<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="none" stroke="{sub}" stroke-width="3" stroke-dasharray="6 12"/>
<circle cx="{cx}" cy="{cy}" r="150" fill="url(#sun)"/><circle cx="{cx}" cy="{cy}" r="70" fill="#FFD95A"/>
<g id="earth"><circle r="58" fill="#2F6FE0"/><path id="lit" d="" fill="#FFE08A" opacity=".55"/><circle id="mk" r="12" fill="#fff"/></g>
</svg>
<div id="big" class="abs">{_esc(v.get('title', '하루 = 1년'))}</div>
<div id="dn" class="abs">낮</div>
<div id="hc" class="abs"><span style="color:#FF8A4C">낮 쪽 · 타들어 감</span> &nbsp;|&nbsp; <span style="color:#7FC8FF">밤 쪽 · 얼어붙음</span></div>"""
    css = f"""#big{{left:0;right:0;top:80px;text-align:center;font-size:96px;color:{ink};}}
#dn{{left:0;top:0;font-family:"Pretendard";font-size:52px;padding:6px 22px;border-radius:14px;background:{acc};color:#111;opacity:0;}}
#hc{{left:0;right:0;top:770px;text-align:center;font-size:56px;font-family:"Pretendard";opacity:0;}}"""
    js = f"""tl.fromTo("#big",{{opacity:0,scale:1.3,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.35,ease:"power4.out"}},0.2);
const S={{a:0.0}};
function pos(){{const a=S.a, x={cx}+{RX}*Math.cos(a), y={cy}+{RY}*Math.sin(a);
 const e=document.getElementById('earth'); e.setAttribute('transform','translate('+x+' '+y+')');
 // 해를 향한 반쪽 밝게
 const ang=Math.atan2({cy}-y,{cx}-x); const c=Math.cos(ang), s=Math.sin(ang);
 const p=(dx,dy)=>(dx*c-dy*s).toFixed(1)+' '+(dx*s+dy*c).toFixed(1);
 document.getElementById('lit').setAttribute('d','M '+p(0,-58)+' A 58 58 0 0 1 '+p(0,58)+' Z');
 // 표식은 우주에 대해 방향 고정(자전 없음) → 해를 보면 낮
 document.getElementById('mk').setAttribute('cx',40); document.getElementById('mk').setAttribute('cy',-30);
 const day=Math.cos(ang)>0; const d=document.getElementById('dn'); d.textContent=day?'서울 · 낮':'서울 · 밤'; d.style.background=day?'{acc}':'#3D6BFF'; d.style.color=day?'#111':'#fff';
 d.style.transform='translate('+(x+70)+'px,'+(y-110)+'px)';}}
tl.call(pos,null,0);
tl.fromTo("#dn",{{opacity:0}},{{opacity:1,duration:.3}},{O0:.3f});
tl.to(S,{{a:Math.PI*2,duration:{max(1.0, O1 - O0):.2f},ease:"none",onUpdate:pos}},{O0:.3f});
tl.fromTo("#hc",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{HC:.3f});
"""
    return body, css, js


# ── 6. 적도 볼록 → 바다가 극지방으로 ───────────────────────
def t_bulge(v, th, dur):
    acc, ink, sub, card = _sp(th)
    B0, B1, B2 = v["bulge"], v["flow"], v["land"]
    cx, cy = 760, 590
    body = f"""<svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<ellipse id="wq" cx="{cx}" cy="{cy}" rx="380" ry="300" fill="#2F7BE8"/>
<ellipse id="core" cx="{cx}" cy="{cy}" rx="350" ry="300" fill="#7A5B3A"/>
<ellipse id="wn" cx="{cx}" cy="{cy - 300}" rx="230" ry="0" fill="#2F7BE8"/>
<ellipse id="ws" cx="{cx}" cy="{cy + 300}" rx="230" ry="0" fill="#2F7BE8"/>
<rect id="band" x="{cx - 352}" y="{cy - 60}" width="704" height="120" fill="#C79A5B" opacity="0"/>
<g id="arw" opacity="0"><path d="M {cx + 320} {cy - 40} Q {cx + 300} {cy - 260} {cx + 120} {cy - 330}" fill="none" stroke="{ink}" stroke-width="8" marker-end="url(#ah)"/>
<path d="M {cx + 320} {cy + 40} Q {cx + 300} {cy + 260} {cx + 120} {cy + 330}" fill="none" stroke="{ink}" stroke-width="8"/></g>
<line id="eqd" x1="{cx - 450}" y1="{cy}" x2="{cx + 450}" y2="{cy}" stroke="{acc}" stroke-width="4" stroke-dasharray="14 10"/>
</svg>
<div id="t1" class="abs tg" style="top:{cy - 40}px">적도 <b>21km</b> 볼록</div>
<div id="t2" class="abs tg" style="top:{cy - 300}px">바다 → 북극 · 남극</div>
<div id="t3" class="abs tg" style="top:{cy + 120}px;color:#E8C48A">적도엔 거대한 대륙 하나</div>"""
    css = f""".tg{{left:1250px;font-size:62px;font-family:"Pretendard";opacity:0;}} .tg b{{color:{acc};}}"""
    js = f"""tl.fromTo("#wq",{{attr:{{rx:300}}}},{{attr:{{rx:380}},duration:1.0,ease:"expo.out"}},{B0:.3f});
tl.fromTo("#t1",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.45,ease:"expo.out"}},{B0 + 0.3:.3f});
tl.to("#wq",{{attr:{{rx:350}},duration:1.4,ease:"power2.inOut"}},{B1:.3f});
tl.to(["#wn","#ws"],{{attr:{{ry:70}},duration:1.4,ease:"power2.inOut"}},{B1:.3f});
tl.to("#t1",{{opacity:.3,duration:.3}},{B1:.3f});
tl.fromTo("#t2",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.45,ease:"expo.out"}},{B1 + 0.4:.3f});
tl.fromTo("#band",{{opacity:0,scaleX:.2,transformOrigin:"{cx}px {cy}px"}},{{opacity:1,scaleX:1,duration:.7,ease:"expo.out"}},{B2:.3f});
tl.fromTo("#t3",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.45,ease:"expo.out"}},{B2 + 0.2:.3f});
"""
    return body, css, js


# ── 7. 체중계 ──────────────────────────────────────────
def t_scale(v, th, dur):
    acc, ink, sub, card = _sp(th)
    T0, T1 = v["weigh"], v["why"]
    body = f"""<svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<rect x="560" y="660" width="800" height="170" rx="40" fill="#E9EEF8"/><rect x="600" y="690" width="720" height="110" rx="26" fill="#C9D3E6"/>
<rect x="760" y="700" width="400" height="90" rx="18" fill="#0E1630"/>
{_person(960, 650, 230, '#9FB4E8', 'man')}
<g id="cf" opacity="0"><line x1="1150" y1="420" x2="1400" y2="420" stroke="{acc}" stroke-width="12" stroke-linecap="round"/><polygon points="1400,400 1440,420 1400,440" fill="{acc}"/></g>
<line id="xx" x1="1120" y1="380" x2="1460" y2="460" stroke="#FF4D4D" stroke-width="14" stroke-linecap="round" opacity="0"/>
</svg>
<div id="rd" class="abs">60.00<small> kg</small></div>
<div id="cfl" class="abs">원심력</div>
<div id="dl" class="abs">+210g</div>
<div id="kk" class="abs">{_esc(v.get('kicker', '적도에 사는 60kg인 사람'))}</div>"""
    css = f"""#rd{{left:760px;width:400px;top:705px;text-align:center;font-family:"Pretendard";font-size:76px;color:#7CFFB2;}} #rd small{{font-size:34px;}}
#cfl{{left:1180px;top:340px;font-size:48px;color:{acc};opacity:0;}} #dl{{left:1220px;top:690px;font-family:"Pretendard";font-size:96px;color:{acc};opacity:0;}}
#kk{{left:0;right:0;top:110px;text-align:center;font-size:66px;}}"""
    js = f"""tl.fromTo("#kk",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2}},0.15);
tl.fromTo("#man",{{y:-300,opacity:0}},{{y:0,opacity:1,duration:.6,ease:"expo.out"}},0.3);
tl.fromTo(["#cf","#cfl"],{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},0.9);
tl.to("#xx",{{opacity:1,duration:.2}},{T0:.3f});
tl.to(["#cf","#cfl"],{{opacity:.25,duration:.3}},{T0 + 0.2:.3f});
const W={{v:60}}; tl.to(W,{{v:60.21,duration:1.2,ease:"power3.out",onUpdate:()=>{{document.getElementById('rd').firstChild.textContent=W.v.toFixed(2);}}}},{T0 + 0.3:.3f});
tl.to("#man .pp",{{scaleY:.96,duration:.15,ease:"power2.out",yoyo:true,repeat:1,transformOrigin:"0px 0px"}},{T0 + 0.3:.3f});
tl.fromTo("#dl",{{opacity:0,scale:2,rotation:10}},{{opacity:1,scale:1,rotation:-6,duration:.4,ease:"power4.out"}},{T0 + 1.5:.3f});
"""
    return body, css, js


# ── 8. 하루 길이 시계 + 시간 축 ─────────────────────────────
def t_daylength(v, th, dur):
    acc, ink, sub, card = _sp(th)
    T0, T1, T2 = v["then"], v["now"], v["future"]
    import math
    C = 2 * math.pi * 210
    body = f"""<svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<circle cx="520" cy="560" r="210" fill="none" stroke="#1B2547" stroke-width="40"/>
<circle id="ring" cx="520" cy="560" r="210" fill="none" stroke="{acc}" stroke-width="40" stroke-linecap="round" stroke-dasharray="{C:.1f}" stroke-dashoffset="{C:.1f}" transform="rotate(-90 520 560)"/>
<line x1="900" y1="760" x2="1780" y2="760" stroke="{sub}" stroke-width="6"/>
<g id="m0" opacity="0"><circle cx="980" cy="760" r="16" fill="#9FB4E8"/><text x="980" y="830" fill="{ink}" font-size="40" text-anchor="middle" font-family="Pretendard">7천만 년 전</text><text x="980" y="700" fill="#9FB4E8" font-size="44" text-anchor="middle" font-family="Pretendard">23시간 30분</text></g>
<g id="m1" opacity="0"><circle cx="1420" cy="760" r="20" fill="{acc}"/><text x="1420" y="830" fill="{ink}" font-size="40" text-anchor="middle" font-family="Pretendard">지금</text><text x="1420" y="700" fill="{acc}" font-size="52" text-anchor="middle" font-family="Pretendard">24시간</text></g>
<g id="m2" opacity="0"><path d="M 1560 760 L 1760 760" stroke="#FF8A4C" stroke-width="10" marker-end=""/><polygon points="1760,740 1800,760 1760,780" fill="#FF8A4C"/><text x="1680" y="700" fill="#FF8A4C" font-size="40" text-anchor="middle" font-family="Pretendard">100년에 +1.7ms</text></g>
</svg>
<div id="clk" class="abs"><span id="hh">00:00</span><small>하루 길이</small></div>
<div id="ttl2" class="abs">{_hl(v.get('title', '지구는 진짜로 느려지는 중'), v.get('title_hl'), 'mk')}</div>"""
    css = f"""#clk{{left:320px;width:400px;top:480px;text-align:center;font-family:"Pretendard";font-size:92px;color:{ink};}}
#clk small{{display:block;font-size:34px;color:{sub};}}
#ttl2{{left:0;right:0;top:110px;text-align:center;font-size:76px;}} #ttl2 span{{display:inline-block;margin:0 .12em;}}"""
    js = f"""tl.fromTo("#ttl2 span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.067}},0.1);
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},0.6);
const H={{m:0}}; const fmt=()=>{{const m=Math.round(H.m);document.getElementById('hh').textContent=String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');}};
tl.to(H,{{m:1410,duration:1.2,ease:"power3.out",onUpdate:fmt}},{T0:.3f});
tl.to("#ring",{{strokeDashoffset:{C * (1 - 1410 / 1440):.1f},duration:1.2,ease:"power3.out"}},{T0:.3f});
tl.fromTo("#m0",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{T0 + 0.2:.3f});
tl.to(H,{{m:1440,duration:1.0,ease:"power2.inOut",onUpdate:fmt}},{T1:.3f});
tl.to("#ring",{{strokeDashoffset:0,duration:1.0,ease:"power2.inOut"}},{T1:.3f});
tl.fromTo("#m1",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{T1 + 0.2:.3f});
tl.fromTo("#m2",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:"expo.out"}},{T2:.3f});
"""
    return body, css, js


TEMPLATES.update({"latitude": t_latitude, "impact": t_impact, "inertia": t_inertia, "wave": t_wave, "orbit": t_orbit,
                  "bulge": t_bulge, "scale": t_scale, "daylength": t_daylength})
