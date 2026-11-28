"""HyperFrames 주식채널 세트 2 (ep028 삼성 배당 · 2026-11-28) — 영상별 템플릿 다변화 규칙(TEMPLATES.md)
bankpush   폰 잠금화면에 '배당금 입금' 알림이 내려옴 → 옆에 질문 줄
divcal     1년 달력 띠: 배당 나오는 달에 동전이 떨어짐(크기 = 금액) · 보너스 달은 거대한 금화
divbars    연도별 1주당 배당 기둥 · 평소선(점선) · 보너스 해에 '보너스' 꼬리표 · 0원 해 표시
tower      돈다발 탑 두 개가 올라감(보너스 기준 vs 평소 기준) · 사이 'N배'
meltdown   원금 막대가 녹아 내림 + 오른쪽 작은 배당 동전 · '배당 N년치' 도장
teaser     다음 편 예고: 먹구름(하락장) 아래 방패 · 제목 · 날짜 꼬리표
"""
import json

from .hfscene import TEMPLATES, _esc, _hl
from .hfstock import GOLD, GREEN, RED, BLUE, _ttl, _fmt_js


# ── bankpush ──────────────────────────────────────────────
def t_bankpush(v, th, dur):
    A, B = v.get("a", 0.4), v.get("b", 3.0)
    lines = v.get("lines", [])
    qs = "".join(f'<div id="q{i}" class="qq">{_hl(l["text"], l.get("hl"), f"mq{i}")}</div>' for i, l in enumerate(lines))
    body = f"""<div id="ph" class="abs"><div class="nt">{_esc(v.get('time', '11월 27일 금요일'))}</div><div class="ck">{_esc(v.get('clock', '9:41'))}</div>
<div id="nf" class="nf"><div class="ic">₩</div><div class="nb"><div class="na">{_esc(v.get('app', '증권'))} <span>지금</span></div>
<div class="nt2">{_esc(v.get('title', '배당금 입금'))}</div><div class="nm">{_esc(v.get('msg', ''))}</div></div></div>
<div id="amt" class="amt">+<span id="av">0</span>원</div></div>
<div id="qs" class="abs">{qs}</div>"""
    css = f"""#ph{{left:230px;top:90px;width:520px;height:960px;border-radius:70px;background:linear-gradient(160deg,#2B3A6B,#0B1230);border:12px solid #1C2442;box-shadow:0 40px 80px rgba(0,0,0,.6);overflow:hidden}}
.nt{{margin-top:110px;text-align:center;font-family:Pretendard;font-size:30px;color:#C9D2E8}} .ck{{text-align:center;font-family:Pretendard;font-size:150px;color:#fff;line-height:1}}
.nf{{position:absolute;left:26px;right:26px;top:400px;background:rgba(255,255,255,.93);border-radius:30px;padding:22px;display:flex;gap:18px;opacity:0}}
.ic{{width:76px;height:76px;border-radius:18px;background:{BLUE};color:#fff;font-family:Pretendard;font-size:48px;display:flex;align-items:center;justify-content:center;flex:none}}
.nb{{font-family:Pretendard;color:#111}} .na{{font-size:26px;color:#555}} .na span{{float:right;margin-left:60px}} .nt2{{font-size:36px;margin-top:4px}} .nm{{font-size:30px;color:#333;margin-top:4px}}
.amt{{position:absolute;left:0;right:0;top:650px;text-align:center;font-family:Pretendard;font-size:84px;color:{GREEN};opacity:0}}
#qs{{left:880px;right:100px;top:300px}} .qq{{font-family:Pretendard;font-size:82px;color:#fff;line-height:1.25;margin-bottom:34px;opacity:0}} .qq span{{display:inline-block;margin-right:.22em}} .qq .hlw{{color:{GOLD}}}"""
    js = _fmt_js(0) + f"""tl.fromTo("#ph",{{opacity:0,y:80,rotation:-4}},{{opacity:1,y:0,rotation:-2,duration:.7,ease:"expo.out"}},0.05);
tl.fromTo("#nf",{{opacity:0,y:-120}},{{opacity:1,y:0,duration:.6,ease:"back.out(1.6)"}},{A:.3f});
const M={{v:0}}; tl.set("#amt",{{opacity:1}},{A + 0.5:.3f});
tl.to(M,{{v:{float(v.get('amount', 0))},duration:1.2,ease:"power3.out",onUpdate:()=>{{document.getElementById('av').textContent=fmt(M.v);}}}},{A + 0.5:.3f});
tl.fromTo("#amt",{{scale:1.2}},{{scale:1,duration:.4,ease:"back.out(2)",immediateRender:false}},{A + 1.7:.3f});
"""
    for i, l in enumerate(lines):
        T = v.get(f"l{i}", B + i * 1.2)
        js += (f'tl.set("#q{i}",{{opacity:1}},{T:.3f});\n'
               f'tl.fromTo("#q{i} span",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.35,ease:"expo.out",stagger:.07}},{T:.3f});\n'
               f'tl.fromTo("#mq{i}",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{T + 0.5:.3f});\n')
    return body, css, js


# ── divcal ────────────────────────────────────────────────
def t_divcal(v, th, dur):
    items = v["items"]   # [{month, amount, label, T, bonus}]
    mx = max(i["amount"] for i in items)
    cells = "".join(f'<div class="mo" style="left:{110 + k * 142}px">{k + 1}월</div>' for k in range(12))
    coins, js = "", _ttl(v)[2]
    for j, it in enumerate(items):
        m = it["month"] - 1
        d = 60 + 240 * (it["amount"] / mx) ** 0.5
        cx = 110 + m * 142 + 66
        col = GOLD if it.get("bonus") else "#C9D2E8"
        coins += (f'<div id="c{j}" class="abs coin" style="left:{cx - d / 2:.0f}px;top:{720 - d:.0f}px;width:{d:.0f}px;height:{d:.0f}px;'
                  f'background:radial-gradient(circle at 35% 30%,#fff8,{col} 45%,{"#B8860B" if it.get("bonus") else "#7A86A6"});'
                  f'font-size:{max(22, d * 0.2):.0f}px">{_esc(it.get("text", ""))}</div>'
                  f'<div id="cl{j}" class="abs cl" style="left:{cx - 120:.0f}px;top:{735}px;color:{col}">{_esc(it.get("label", ""))}</div>')
        T = it["T"]
        js += (f'tl.fromTo("#c{j}",{{opacity:0,y:-500}},{{opacity:1,y:0,duration:.7,ease:"bounce.out"}},{T:.3f});\n'
               f'tl.fromTo("#cl{j}",{{opacity:0}},{{opacity:1,duration:.3}},{T + 0.5:.3f});\n')
        if it.get("bonus"):
            js += f'tl.fromTo("#c{j}",{{boxShadow:"0 0 0 rgba(255,201,60,0)"}},{{boxShadow:"0 0 80px rgba(255,201,60,.9)",duration:.5,yoyo:true,repeat:1,immediateRender:false}},{T + 0.7:.3f});\n'
    body = _ttl(v, 150, 72)[0] + f'<div class="abs strip"></div>{cells}{coins}<div id="nt" class="abs">{_hl(v.get("note", ""), v.get("note_hl"), "mn")}</div>'
    css = _ttl(v)[1] + f"""
.strip{{left:100px;right:100px;top:800px;height:90px;background:#141E3C;border-radius:18px}}
.mo{{position:absolute;top:822px;width:132px;text-align:center;font-family:Pretendard;font-size:38px;color:{th['sub']}}}
.coin{{border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:Pretendard;color:#1a1a1a;box-shadow:0 10px 30px rgba(0,0,0,.5)}}
.cl{{width:240px;text-align:center;font-family:Pretendard;font-size:30px;opacity:0}}
#nt{{left:0;right:0;top:280px;text-align:center;font-family:Pretendard;font-size:54px;color:#fff;opacity:0}} #nt span{{display:inline-block;margin:0 .1em}} #nt .hlw{{color:{GOLD}}}"""
    if v.get("n"):
        js += (f'tl.set("#nt",{{opacity:1}},{v["n"]:.3f});\n'
               f'tl.fromTo("#nt span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2,stagger:.06}},{v["n"]:.3f});\n'
               f'tl.fromTo("#mn",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{v["n"] + 0.5:.3f});\n')
    return body, css, js


# ── divbars ───────────────────────────────────────────────
def t_divbars(v, th, dur):
    rows = v["rows"]   # [{year, value, text, bonus, zero_note, T}]
    mx = float(v.get("vmax", max(r["value"] for r in rows)))
    n = len(rows)
    X0, X1, Y1, HH = 170, 1750, 880, 560
    bw = (X1 - X0) / n
    base = v.get("baseline")
    body = _ttl(v, 150, 72)[0]
    js = _ttl(v)[2]
    for i, r in enumerate(rows):
        h = max(6, r["value"] / mx * HH)
        x = X0 + i * bw + bw * 0.18
        col = GOLD if r.get("bonus") else "#5E6B8E"
        body += (f'<div id="b{i}" class="abs bar" style="left:{x:.0f}px;top:{Y1 - h:.0f}px;width:{bw * 0.64:.0f}px;height:{h:.0f}px;background:{col}"></div>'
                 f'<div id="t{i}" class="abs bt" style="left:{x - 30:.0f}px;width:{bw * 0.64 + 60:.0f}px;top:{Y1 - h - 52:.0f}px;color:{GOLD if r.get("bonus") else "#DDE3F2"}">{_esc(r["text"])}</div>'
                 f'<div class="abs yr" style="left:{x - 20:.0f}px;width:{bw * 0.64 + 40:.0f}px;top:{Y1 + 14}px">{_esc(r["year"])}</div>')
        if r.get("tag"):
            body += f'<div id="g{i}" class="abs tg" style="left:{x - 40:.0f}px;top:{Y1 - h - 120:.0f}px;background:{RED if r.get("zero") else GOLD}">{_esc(r["tag"])}</div>'
        T = r["T"]
        js += (f'tl.fromTo("#b{i}",{{scaleY:0}},{{scaleY:1,duration:.6,ease:"expo.out"}},{T:.3f});\n'
               f'tl.fromTo("#t{i}",{{opacity:0}},{{opacity:1,duration:.3}},{T + 0.3:.3f});\n')
        if r.get("tag"):
            js += f'tl.fromTo("#g{i}",{{opacity:0,scale:2,rotation:10}},{{opacity:1,scale:1,rotation:-6,duration:.35,ease:"back.out(2)"}},{r.get("TG", T + 0.6):.3f});\n'
    if base:
        by = Y1 - base["value"] / mx * HH
        body += (f'<div id="bl" class="abs" style="left:{X0}px;width:{X1 - X0}px;top:{by:.0f}px;border-top:4px dashed {GREEN}"></div>'
                 f'<div id="blt" class="abs" style="left:{X0}px;top:250px;font-family:Pretendard;font-size:38px;color:{GREEN}">- - -  {_esc(base["label"])}</div>')
        js += (f'tl.fromTo("#bl",{{scaleX:0,transformOrigin:"left"}},{{scaleX:1,duration:.8,ease:"expo.out"}},{v.get("bl", 1.0):.3f});\n'
               f'tl.fromTo("#blt",{{opacity:0}},{{opacity:1,duration:.3}},{v.get("bl", 1.0) + 0.4:.3f});\n')
    css = _ttl(v)[1] + f"""
.bar{{border-radius:12px 12px 0 0;transform-origin:bottom}} .bt{{text-align:center;font-family:Pretendard;font-size:38px;opacity:0}}
.yr{{text-align:center;font-family:Pretendard;font-size:34px;color:{th['sub']}}}
.tg{{font-family:Pretendard;font-size:34px;color:#111;border-radius:12px;padding:4px 16px;white-space:nowrap;opacity:0}}"""
    return body, css, js


# ── tower ─────────────────────────────────────────────────
def t_tower(v, th, dur):
    L, R = v["left"], v["right"]   # {label, value, text, T}
    mx = max(L["value"], R["value"])
    def col(k, s, x, color):
        h = max(40, s["value"] / mx * 430)
        nb = max(1, int(h / 26))
        bills = "".join(f'<i style="bottom:{j * 26}px"></i>' for j in range(nb))
        return (f'<div id="w{k}" class="abs tw" style="left:{x}px;height:{h:.0f}px">{bills}</div>'
                f'<div id="tt{k}" class="abs ttx" style="left:{x - 100}px;top:{850 - h - 110:.0f}px;color:{color}">{_esc(s["text"])}</div>'
                f'<div class="abs tl2" style="left:{x - 150}px;top:{850 - h - 160:.0f}px">{_esc(s["label"])}</div>')
    body = _ttl(v, 150, 70)[0] + col(0, L, 560, GREEN) + col(1, R, 1160, RED) + f'<div id="mx" class="abs">{_esc(v.get("mult", ""))}</div>'
    css = _ttl(v)[1] + f"""
.tw{{top:auto;bottom:230px;width:260px}} .tw i{{position:absolute;left:0;width:260px;height:22px;border-radius:5px;background:linear-gradient(90deg,#3E8E5E,#6FCF97,#3E8E5E);box-shadow:0 2px 0 #1E4D33;opacity:0}}
.ttx{{width:460px;text-align:center;font-family:Pretendard;font-size:84px}} .tl2{{width:560px;text-align:center;font-family:Pretendard;font-size:40px;color:#C9D2E8}}
#mx{{left:800px;width:320px;top:420px;text-align:center;font-family:Pretendard;font-size:120px;color:{GOLD};opacity:0}}"""
    js = _ttl(v)[2]
    for k, s in ((0, L), (1, R)):
        js += (f'tl.fromTo("#w{k} i",{{opacity:0,y:-40}},{{opacity:1,y:0,duration:.18,ease:"power2.out",stagger:{min(0.06, 1.6 / max(1, int(max(40, s["value"] / mx * 430) / 26))):.3f}}},{s["T"]:.3f});\n'
               f'tl.fromTo("#tt{k}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}},{s["T"] + 1.0:.3f});\n')
    js += f'tl.fromTo("#mx",{{opacity:0,scale:2.5}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}},{v.get("m", R["T"] + 2.0):.3f});\n'
    return body, css, js


# ── meltdown ──────────────────────────────────────────────
def t_meltdown(v, th, dur):
    A, B, C = v.get("a", 0.4), v.get("b", 2.5), v.get("c", 5.0)
    p0, p1 = float(v["from"]), float(v["to"])
    k = p1 / p0
    body = _ttl(v, 150, 70)[0] + f"""<div class="abs lab1">{_esc(v.get('bar_label', ''))}</div>
<div id="bw" class="abs"><div id="bf"></div><div id="drip"></div></div><div id="bv" class="abs"><span id="vv">{p0:g}</span>억</div>
<div id="ls" class="abs">{_esc(v.get('loss_text', ''))}</div>
<div id="cn" class="abs"><div class="cc">₩</div><div class="ct">{_esc(v.get('coin_text', ''))}</div></div>
<div id="st" class="abs">{_esc(v.get('stamp', ''))}</div>"""
    css = _ttl(v)[1] + f"""
.lab1{{left:200px;top:330px;font-family:Pretendard;font-size:40px;color:#C9D2E8}}
#bw{{left:200px;top:400px;width:1000px;height:150px;background:#141E3C;border-radius:20px;overflow:hidden}}
#bf{{position:absolute;left:0;top:0;bottom:0;width:100%;background:linear-gradient(90deg,{GREEN},#2FAE78);transform-origin:left}}
#drip{{position:absolute;right:0;top:0;bottom:0;width:0;background:{RED}}}
#bv{{left:1230px;top:410px;font-family:Pretendard;font-size:110px;color:#fff}}
#ls{{left:200px;top:590px;font-family:Pretendard;font-size:76px;color:{RED};opacity:0}}
#cn{{left:200px;top:760px;display:flex;align-items:center;gap:24px;opacity:0}} .cc{{width:90px;height:90px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff8,{GOLD} 45%,#B8860B);display:flex;align-items:center;justify-content:center;font-family:Pretendard;font-size:44px;color:#111}}
.ct{{font-family:Pretendard;font-size:52px;color:{GOLD}}}
#st{{left:1180px;top:700px;font-family:Pretendard;font-size:96px;color:{RED};border:10px solid {RED};border-radius:24px;padding:4px 34px;opacity:0;background:#0E1630}}"""
    js = _ttl(v)[2] + f"""const V={{v:{p0}}};
tl.fromTo("#bw",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.5,ease:"expo.out"}},{A:.3f});
tl.to("#bf",{{scaleX:{k:.3f},duration:1.8,ease:"power2.in"}},{B:.3f});
tl.to(V,{{v:{p1},duration:1.8,ease:"power2.in",onUpdate:()=>{{document.getElementById('vv').textContent=V.v.toFixed(1);}}}},{B:.3f});
tl.to("#bv",{{color:"{RED}",duration:.3}},{B + 1.5:.3f});
tl.fromTo("#ls",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{B + 1.9:.3f});
tl.fromTo("#cn",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},{C:.3f});
tl.fromTo("#st",{{opacity:0,scale:2.4,rotation:14}},{{opacity:1,scale:1,rotation:-7,duration:.35,ease:"power4.out"}},{C + 0.9:.3f});
"""
    return body, css, js


# ── teaser ────────────────────────────────────────────────
def t_teaser(v, th, dur):
    A, B = v.get("a", 0.3), v.get("b", 2.0)
    clouds = "".join(f'<div class="abs cld" style="left:{x}px;top:{y}px;width:{w}px;height:{w * 0.45:.0f}px"></div>'
                     for x, y, w in ((-80, 60, 700), (420, 20, 820), (1100, 70, 900), (200, 150, 600), (900, 140, 700)))
    rain = "".join(f'<i style="left:{(i * 137) % 1920}px;animation:none"></i>' for i in range(40))
    body = f"""{clouds}<div id="rn" class="abs">{rain}</div>
<div id="kk" class="abs">{_esc(v.get('kicker', '다음 편 예고'))}</div>
<div id="sh" class="abs"><svg viewBox="0 0 200 240" width="300"><path d="M100 10 L185 45 L185 120 Q185 190 100 230 Q15 190 15 120 L15 45 Z" fill="#17213F" stroke="{GOLD}" stroke-width="10"/>
<circle cx="100" cy="118" r="46" fill="{GOLD}"/><text x="100" y="135" text-anchor="middle" font-family="Pretendard" font-size="48" fill="#111">₩</text></svg></div>
<div id="tt" class="abs">{_hl(v.get('title', ''), v.get('title_hl'), 'mk')}</div>
<div id="sb" class="abs">{_esc(v.get('sub', ''))}</div>"""
    css = f"""#grid{{display:none}} #root{{background:linear-gradient(#141A2E,#070A14) !important}}
.cld{{border-radius:50%;background:radial-gradient(ellipse at 50% 60%,#3A4258,#1B2033 70%,rgba(0,0,0,0) 72%);opacity:.9}}
#rn{{inset:0}} #rn i{{position:absolute;top:-60px;width:3px;height:60px;background:linear-gradient(transparent,#8FA3D6)}}
#kk{{left:0;right:0;top:300px;text-align:center;font-family:Pretendard;font-size:46px;color:{GOLD};letter-spacing:8px}}
#sh{{left:810px;top:370px}} #tt{{left:0;right:0;top:760px;text-align:center;font-family:Pretendard;font-size:92px;color:#fff}} #tt span{{display:inline-block;margin:0 .12em}} #tt .hlw{{color:{GOLD}}}
#sb{{left:0;right:0;top:880px;text-align:center;font-family:Pretendard;font-size:44px;color:#C9D2E8}}"""
    js = f"""document.querySelectorAll('#rn i').forEach((d,i)=>{{tl.fromTo(d,{{y:0}},{{y:1200,duration:.9,ease:"none",repeat:{int(dur / 0.9) + 1}}},(i%9)*0.1);}});
tl.fromTo(".cld",{{opacity:0,y:-60}},{{opacity:.9,y:0,duration:.8,ease:"expo.out",stagger:.08}},0);
tl.fromTo("#kk",{{opacity:0,letterSpacing:"30px"}},{{opacity:1,letterSpacing:"8px",duration:.6,ease:"expo.out"}},{A:.3f});
tl.fromTo("#sh",{{opacity:0,scale:.4,y:60}},{{opacity:1,scale:1,y:0,duration:.6,ease:"back.out(1.8)"}},{B:.3f});
tl.fromTo("#tt span",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.35,ease:"expo.out",stagger:.07}},{B + 0.4:.3f});
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{B + 1.0:.3f});
tl.fromTo("#sb",{{opacity:0}},{{opacity:1,duration:.4}},{B + 1.2:.3f});
"""
    return body, css, js


TEMPLATES.update({"bankpush": t_bankpush, "divcal": t_divcal, "divbars": t_divbars, "tower": t_tower, "meltdown": t_meltdown, "teaser": t_teaser})
from .hfstock import SFX  # noqa: E402
SFX.update({"bankpush": [("a", "pop", 0.6)], "divcal": [], "divbars": [], "tower": [("m", "boom", 0.5)],
            "meltdown": [("b", "whoosh", 0.5), ("c", "boom", 0.6)], "teaser": [("b", "riser", 0.5)]})
