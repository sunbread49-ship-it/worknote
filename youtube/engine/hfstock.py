"""HyperFrames 주식채널 장면 세트 (2026-11-28 사용자: "롱폼마다 분위기가 비슷 · 글 중심 말고 영상화 · 영상별로 템플릿 다변화
· 퀴즈는 지식채널과 다르게 주식 톤으로 · CI를 건물 배경과 함께")
첫 사용 ep027(시스코 닷컴). 색: 빨강 = 손해 · 경고 / 초록 = 회복 · 정답 / 금색 = 핵심 (theme 08 규칙)

tickerdrop  증권 앱 시세창: 로고 패 + 가격이 굴러 떨어짐 + 미니 차트 + 아래 흐르는 시세 띠 + 한 줄 질문
brandvs     실사 본사 건물(켄번스) 위에 CI 패 · 연도 · 한 줄 → 가운데 '=' 도장
quizorder   호가창 퀴즈: 보기 = 주문 줄 · 카운트다운 = '체결까지 3' LED · 정답 줄 초록 번쩍 + '체결' 도장
journey     1,000만 원의 여정: 실제 주가로 선이 그려지고 점이 달림 · 연도 · 금액 계기판이 같이 돈다 · 깃발
gap         매출 막대는 자라는데 주가 막대는 제자리 → 사이 틈에 '비싸게 산 값' 태그
road        인터넷 길: 시스코가 길(케이블 · 라우터)을 깔고 → 주문 뚝 · 재고 상자 → 아마존 상자가 그 길 위를 달림
race        원금 회복 경주: 회사 패들이 2000년 출발선에서 달려 원금선에 닿는 해에 멈춤 · 위 연도 시계
mirror      두 회사 거울: 로고 두 개 · 줄마다 같으면 '=' 선(빨강), 다르면 '≠'(초록)
"""
import json
from pathlib import Path

from .hfscene import TEMPLATES, _esc, _hl

ROOT = Path(__file__).resolve().parents[1]
RED, GREEN, GOLD, BLUE = "#FF5A4E", "#3DDC97", "#FFC93C", "#5B8CFF"


def _ttl(v, top=80, size=76):
    return (f'<div id="ttl" class="abs" style="left:0;right:0;top:{top}px;text-align:center;font-size:{size}px;font-family:Pretendard">'
            f'{_hl(v.get("title", ""), v.get("title_hl"), "mk")}</div>',
            '#ttl span{display:inline-block;margin:0 .12em;}',
            'tl.fromTo("#ttl span",{opacity:0,y:30},{opacity:1,y:0,duration:.35,ease:"expo.out",stagger:.06},0.1);\n'
            'tl.fromTo("#mk",{scaleX:0},{scaleX:1,duration:.45,ease:"expo.out"},0.6);\n')


def _plq(logo, w, h, pad=22, extra=""):
    return (f'<div class="plq" style="width:{w}px;height:{h}px;{extra}"><img src="assets/{logo}" '
            f'style="max-width:{w - 2 * pad}px;max-height:{h - 2 * pad}px"></div>')


PLQ_CSS = (".plq{background:#fff;border-radius:22px;display:flex;align-items:center;justify-content:center;"
           "box-shadow:0 18px 40px rgba(0,0,0,.45);} .plq img{display:block;}")


def _fmt_js(dec=0):
    return f'const fmt=(x)=>{{const s=Math.abs(x).toFixed({dec}).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,",");return (x<0?"-":"")+s;}};\n'


# ── 1. tickerdrop ─────────────────────────────────────────────
def t_tickerdrop(v, th, dur):
    if "points" not in v:   # series · start · end 로 실제 종가
        _, w = _series_pts(v["series"], v["start"], v["end"], 1, every=v.get("every", "D"))
        v["points"] = list(w.values)
    pts = v["points"]
    W, H, X0, Y0 = 1000, 330, 820, 380
    lo, hi = min(pts), max(pts)
    xy = [(X0 + i * W / (len(pts) - 1), Y0 + H - (p - lo) / (hi - lo + 1e-9) * H) for i, p in enumerate(pts)]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    area = path + f" L{xy[-1][0]:.1f},{Y0 + H} L{X0},{Y0 + H} Z"
    tape = "".join(f'<span class="tk"><b>{_esc(a)}</b> <em style="color:{RED if "-" in b else GREEN}">{_esc(b)}</em></span>' for a, b in v.get("tape", []))
    A, B = v.get("a", 0.4), v.get("b", 3.0)
    body = f"""<div class="abs" style="inset:0;background:radial-gradient(ellipse 60% 70% at 70% 45%,rgba(255,90,78,.14),rgba(0,0,0,0) 70%)"></div>
<div id="card" class="abs">{_plq(v['logo'], 380, 150)}<div id="tkr">{_esc(v.get('ticker', ''))}</div><div id="nm">{_esc(v.get('name', ''))}</div></div>
<div id="px" class="abs"><span id="cur">$</span><span id="pv">0</span></div>
<div id="chg" class="abs">▼ <span id="pc">0.0</span>%</div>
<div id="hilo" class="abs">{_esc(v.get('hilo', ''))}</div>
<svg class="abs" style="inset:0" viewBox="0 0 1920 1080"><defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{RED}" stop-opacity=".45"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient></defs>
<path id="ar" d="{area}" fill="url(#ga)" opacity="0"/><path id="ln" d="{path}" fill="none" stroke="{RED}" stroke-width="7" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
<circle id="dt" cx="{xy[-1][0]:.1f}" cy="{xy[-1][1]:.1f}" r="13" fill="{RED}" opacity="0"/></svg>
<div id="q" class="abs">{_hl(v.get('question', ''), v.get('question_hl'), 'mq')}</div>
<div id="tape" class="abs"><div id="tr">{tape}{tape}</div></div>"""
    css = f"""{PLQ_CSS}
#card{{left:130px;top:250px;}} #tkr{{margin-top:26px;font-family:Pretendard;font-size:64px;color:#fff;letter-spacing:4px}} #nm{{font-size:40px;color:{th['sub']};font-family:Pretendard}}
#px{{left:130px;top:560px;font-family:Pretendard;font-size:190px;line-height:1;color:#fff;letter-spacing:-4px}} #cur{{font-size:.5em;color:{th['sub']};margin-right:10px}}
#chg{{left:140px;top:770px;font-family:Pretendard;font-size:84px;color:{RED};background:rgba(255,90,78,.14);border-radius:16px;padding:4px 24px}}
#hilo{{left:830px;top:300px;font-size:36px;color:{th['sub']};font-family:Pretendard}}
#q{{left:0;right:0;top:110px;text-align:center;font-family:Pretendard;font-size:92px;color:#fff;opacity:0}} #q span{{display:inline-block;margin:0 .12em}} #q .hlw{{color:{RED}}}
#tape{{left:0;right:0;bottom:0;height:72px;background:#0A1024;border-top:2px solid rgba(255,255,255,.08);overflow:hidden}}
#tr{{position:absolute;left:0;top:12px;white-space:nowrap;font-family:Pretendard;font-size:38px;color:#DDE3F2}} .tk{{margin-right:70px}} .tk em{{font-style:normal}}"""
    p0, p1, c1 = float(v["from"]), float(v["to"]), float(v["pct"])
    js = _fmt_js(2) + f"""tl.fromTo("#card",{{opacity:0,x:-60}},{{opacity:1,x:0,duration:.6,ease:"expo.out"}},0.05);
tl.fromTo("#tr",{{x:0}},{{x:-{max(1200, 900 * len(v.get('tape', [])))},duration:{dur:.2f},ease:"none"}},0);
const P={{v:{p0}}},Q={{v:0}}; tl.set("#pv",{{textContent:fmt({p0})}},0);
tl.fromTo("#px",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{A:.3f});
tl.to(P,{{v:{p1},duration:2.2,ease:"power2.in",onUpdate:()=>{{document.getElementById('pv').textContent=fmt(P.v);}}}},{A + 0.2:.3f});
tl.to(Q,{{v:{c1},duration:2.2,ease:"power2.in",onUpdate:()=>{{document.getElementById('pc').textContent=Q.v.toFixed(1);}}}},{A + 0.2:.3f});
tl.fromTo("#chg",{{opacity:0}},{{opacity:1,duration:.3}},{A + 0.2:.3f});
tl.to("#pv",{{color:"{RED}",duration:.3}},{A + 1.6:.3f});
tl.fromTo("#chg",{{scale:1.25}},{{scale:1,duration:.4,ease:"back.out(2)",immediateRender:false}},{A + 2.4:.3f});
tl.fromTo("#hilo",{{opacity:0}},{{opacity:1,duration:.3}},{A:.3f});
tl.to("#ln",{{strokeDashoffset:0,duration:2.4,ease:"power1.inOut"}},{A:.3f});
tl.to("#ar",{{opacity:1,duration:.6}},{A + 1.8:.3f});
tl.fromTo("#dt",{{opacity:0,scale:0,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:.3,ease:"back.out(3)"}},{A + 2.4:.3f});
tl.to(["#card","#px","#chg","#hilo"],{{y:60,duration:.5,ease:"power3.inOut"}},{B - 0.1:.3f});
tl.to("svg",{{y:60,duration:.5,ease:"power3.inOut"}},{B - 0.1:.3f});
tl.set("#q",{{opacity:1}},{B:.3f});
tl.fromTo("#q span",{{opacity:0,filter:"blur(10px)",scale:1.3}},{{opacity:1,filter:"blur(0px)",scale:1,duration:.3,ease:"power4.out",stagger:.09}},{B:.3f});
tl.fromTo("#mq",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{B + 0.5:.3f});
"""
    return body, css, js


# ── 2. brandvs ─────────────────────────────────────────────────
def t_brandvs(v, th, dur):
    L, R = v["left"], v["right"]
    A, B, C = v.get("a", 0.3), v.get("b", 1.2), v.get("c", 3.0)
    def side(s, k, x):
        return (f'<div id="ph{k}" class="abs ph" style="left:{x}px;"><img src="assets/{s["photo"]}" style="object-position:{s.get("pos", "50% 50%")}"></div>'
                f'<div id="sd{k}" class="abs sd" style="left:{x}px;">'
                f'<div class="yr">{_esc(s["year"])}</div>{_plq(s["logo"], 420, 150)}'
                f'<div class="tg">{_esc(s.get("tag", ""))}</div><div class="sb">{_esc(s.get("sub", ""))}</div></div>')
    body = f"""{side(L, 0, 0)}{side(R, 1, 960)}
<div id="seam" class="abs"></div>
<div id="eq" class="abs">=</div>
<div id="kk" class="abs">{_esc(v.get('kicker', ''))}</div>
<div id="bt" class="abs">{_hl(v.get('bottom', ''), v.get('bottom_hl'), 'mb')}</div>"""
    css = f"""{PLQ_CSS} #grid{{display:none}}
.ph{{top:0;width:960px;height:1080px;overflow:hidden}} .ph img{{width:100%;height:100%;object-fit:cover;filter:grayscale(.35) brightness(.42) contrast(1.1)}}
#ph0 img{{filter:grayscale(1) sepia(.35) brightness(.38) contrast(1.15)}}
.sd{{top:250px;width:960px;display:flex;flex-direction:column;align-items:center}}
.yr{{font-family:Pretendard;font-size:150px;color:#fff;line-height:1;margin-bottom:30px;letter-spacing:-3px}}
.tg{{margin-top:34px;font-family:Pretendard;font-size:72px;color:{GOLD}}} .sb{{margin-top:8px;font-size:40px;color:#C9D2E8;font-family:Pretendard}}
#seam{{left:957px;top:0;width:6px;height:1080px;background:{GOLD};box-shadow:0 0 30px {GOLD}}}
#eq{{left:885px;top:430px;width:150px;height:150px;border-radius:50%;background:{RED};color:#fff;font-family:Pretendard;font-size:120px;line-height:140px;text-align:center;box-shadow:0 0 0 10px rgba(255,90,78,.25),0 20px 40px rgba(0,0,0,.5)}}
#kk{{left:0;right:0;top:70px;text-align:center;font-family:Pretendard;font-size:46px;color:{GOLD};letter-spacing:6px}}
#bt{{left:160px;right:160px;bottom:190px;text-align:center;font-family:Pretendard;font-size:66px;color:#fff;background:rgba(8,12,26,.82);border-radius:22px;padding:22px 30px;opacity:0}}
#bt span{{display:inline-block;margin:0 .1em}} #bt .hlw{{color:{GOLD}}}"""
    js = f"""tl.fromTo("#ph0 img",{{scale:1.18}},{{scale:1.02,duration:{dur:.2f},ease:"none"}},0);
tl.fromTo("#ph1 img",{{scale:1.02,x:-30}},{{scale:1.16,x:0,duration:{dur:.2f},ease:"none"}},0);
tl.fromTo("#ph0",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.7,ease:"expo.out"}},0.05);
tl.fromTo("#ph1",{{clipPath:"inset(0 0 0 100%)"}},{{clipPath:"inset(0 0 0 0%)",duration:.7,ease:"expo.out"}},{B:.3f});
tl.fromTo("#seam",{{scaleY:0}},{{scaleY:1,duration:.5,ease:"expo.out"}},{B:.3f});
tl.fromTo("#kk",{{opacity:0,letterSpacing:"30px"}},{{opacity:1,letterSpacing:"6px",duration:.6,ease:"expo.out"}},0.1);
tl.fromTo("#sd0 > *",{{opacity:0,y:50}},{{opacity:1,y:0,duration:.5,ease:"expo.out",stagger:.12}},{A:.3f});
tl.fromTo("#sd1 > *",{{opacity:0,y:50}},{{opacity:1,y:0,duration:.5,ease:"expo.out",stagger:.12}},{B + 0.25:.3f});
tl.fromTo("#eq",{{opacity:0,scale:3,rotation:-90}},{{opacity:1,scale:1,rotation:0,duration:.45,ease:"power4.out"}},{B + 0.9:.3f});
tl.set("#bt",{{opacity:1}},{C:.3f});
tl.fromTo("#bt",{{y:40}},{{y:0,duration:.4,ease:"expo.out"}},{C:.3f});
tl.fromTo("#bt span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power4.out",stagger:.06}},{C:.3f});
tl.fromTo("#mb",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{C + 0.6:.3f});
"""
    return body, css, js


# ── 3. quizorder ───────────────────────────────────────────────
def t_quizorder(v, th, dur):
    ch, ans = v["choices"], v["answer"]
    C0, RV = v["C0"], v["RV"]
    rows = ""
    for i, c in enumerate(ch):
        rows += (f'<div id="o{i}" class="abs od" style="top:{400 + i * 150}px"><div class="no">{i + 1}</div><div class="tx">{_esc(c)}</div>'
                 f'<div class="bt">선택</div><div id="fl{i}" class="fl"></div></div>')
    body = f"""<div id="hd" class="abs"><span class="dot"></span>{_esc(v.get('kicker', '퀴즈 · 3초 안에 맞혀 보세요'))}</div>
<div id="q" class="abs">{_hl(v['question'], v.get('highlight'), 'mk')}</div>
{rows}
<div id="led" class="abs"><div class="lb">정답 공개까지</div><div id="dg">3</div><div id="pb"><i id="pf"></i></div></div>
<div id="hint" class="abs">{_esc(v.get('hint', ''))}</div>
<div id="st" class="abs">정답</div>"""
    css = f"""#hd{{left:120px;top:150px;font-family:Pretendard;font-size:44px;color:{GOLD};letter-spacing:3px}}
.dot{{display:inline-block;width:20px;height:20px;border-radius:50%;background:{RED};margin-right:18px;box-shadow:0 0 14px {RED}}}
#q{{left:120px;right:520px;top:215px;font-family:Pretendard;font-size:84px;color:#fff;line-height:1.2}} #q span{{display:inline-block;margin-right:.24em}}
.od{{left:120px;width:1180px;height:122px;background:#141E3C;border:2px solid rgba(255,255,255,.08);border-radius:18px;display:flex;align-items:center;overflow:hidden}}
.no{{width:122px;height:122px;display:flex;align-items:center;justify-content:center;font-family:Pretendard;font-size:60px;color:{th['sub']};border-right:2px solid rgba(255,255,255,.08)}}
.tx{{flex:1;padding-left:44px;font-family:Pretendard;font-size:70px;color:#fff}}
.bt{{margin-right:26px;font-family:Pretendard;font-size:38px;color:#fff;background:{BLUE};border-radius:12px;padding:12px 30px}}
.fl{{position:absolute;inset:0;background:{GREEN};opacity:0;mix-blend-mode:screen}}
#led{{left:1400px;top:400px;width:400px;height:420px;background:#070B18;border:2px solid rgba(255,255,255,.1);border-radius:24px;opacity:0}}
.lb{{text-align:center;margin-top:34px;font-family:Pretendard;font-size:42px;color:{th['sub']}}}
#dg{{text-align:center;font-family:Pretendard;font-size:220px;line-height:1.05;color:{RED};text-shadow:0 0 30px rgba(255,90,78,.7)}}
#pb{{position:absolute;left:40px;right:40px;bottom:40px;height:16px;background:#1B2546;border-radius:8px;overflow:hidden}} #pf{{position:absolute;left:0;top:0;bottom:0;width:100%;background:{RED};transform-origin:left}}
#hint{{left:120px;top:880px;font-family:Pretendard;font-size:46px;color:{th['sub']}}}
#st{{left:{1300 - 260}px;top:{400 + ans * 150 - 18}px;font-family:Pretendard;font-size:62px;color:{GREEN};border:7px solid {GREEN};border-radius:16px;padding:2px 22px;background:#0E1630;opacity:0}}"""
    wrong = json.dumps([f"#o{i}" for i in range(len(ch)) if i != ans])
    js = f"""tl.fromTo("#hd",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},0.05);
tl.fromTo(".dot",{{opacity:1}},{{opacity:.2,duration:.4,yoyo:true,repeat:{int(dur / 0.8)},ease:"none"}},0.1);
tl.fromTo("#q span",{{opacity:0,y:24}},{{opacity:1,y:0,duration:.3,ease:"expo.out",stagger:.05}},0.15);
tl.fromTo("#mk",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},0.8);
tl.fromTo(".od",{{opacity:0,x:120}},{{opacity:1,x:0,duration:.5,ease:"expo.out",stagger:.1}},0.6);
tl.fromTo("#hint",{{opacity:0}},{{opacity:1,duration:.3}},1.4);
tl.fromTo("#led",{{opacity:0,x:60}},{{opacity:1,x:0,duration:.45,ease:"expo.out"}},{C0 - 0.45:.3f});
const BT={json.dumps([round(x, 3) for x in v.get("BT", [C0, C0 + 1, C0 + 2])])};
for (let i=0;i<3;i++){{const t=BT[i];
 tl.set("#dg",{{textContent:String(3-i)}},t);
 tl.fromTo("#dg",{{scale:1.5,opacity:.3}},{{scale:1,opacity:1,duration:.35,ease:"expo.out"}},t);
 tl.fromTo("#pf",{{scaleX:1-i/3}},{{scaleX:1-(i+1)/3,duration:.98,ease:"none"}},t);}}
tl.set("#dg",{{textContent:"0"}},{RV - 0.05:.3f});
tl.to("#led",{{opacity:0,duration:.2,ease:"power3.in"}},{RV:.3f});
tl.to({wrong},{{opacity:.3,duration:.3}},{RV:.3f});
tl.fromTo("#fl{ans}",{{opacity:.9}},{{opacity:.18,duration:.6,ease:"power2.out",immediateRender:false}},{RV:.3f});
tl.to("#o{ans}",{{borderColor:"{GREEN}",scale:1.04,duration:.4,ease:"back.out(2)"}},{RV:.3f});
tl.to("#o{ans} .bt",{{backgroundColor:"{GREEN}",duration:.2}},{RV:.3f});
tl.fromTo("#st",{{opacity:0,scale:2.4,rotation:14}},{{opacity:1,scale:1,rotation:-8,duration:.35,ease:"power4.out"}},{RV + 0.35:.3f});
"""
    return body, css, js


# ── 4. journey ─────────────────────────────────────────────────
def _series_pts(name, start, end, base, every="W"):
    import sys
    sys.path.insert(0, str(ROOT))
    from engine import data as D
    s = D.series(name, start, end)
    s = s / s.iloc[0] * base
    step = 1 if every == "D" else max(1, len(s) // 400)   # 실제 거래일 그대로 솎아 냄 (점 400개 안팎)
    w = s.iloc[::step]
    if w.index[-1] != s.index[-1]:
        w = s.loc[list(w.index) + [s.index[-1]]]
    for d in (s.idxmin(),):   # 바닥은 반드시 포함
        if d not in w.index:
            w = s.loc[sorted(list(w.index) + [d])]
    return s, w


def t_journey(v, th, dur):
    import pandas as pd
    s, w = _series_pts(v["series"], v["start"], v["end"], v.get("base", 1000))
    X0, X1, Y0, Y1 = 200, 1760, 250, 900
    vmax = float(v.get("vmax", max(w)))
    n = len(w)
    xs = [X0 + i * (X1 - X0) / (n - 1) for i in range(n)]
    ys = [Y1 - min(val, vmax) / vmax * (Y1 - Y0) for val in w.values]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    yrs = [d.year + (d.dayofyear - 1) / 365.25 for d in w.index]
    keys = []   # (인덱스, 시각) — 선이 그 인덱스까지 그 시각에 도착
    for k in v["keys"]:
        idx = int(w.index.get_indexer([pd.Timestamp(k["date"])], method="nearest")[0])
        keys.append((idx, v[k["at"]]))
    base_y = Y1 - v.get("base", 1000) / vmax * (Y1 - Y0)
    flags, fjs = "", ""
    for j, f in enumerate(v.get("flags", [])):
        idx = int(w.index.get_indexer([pd.Timestamp(f["date"])], method="nearest")[0])
        x, y = xs[idx], ys[idx]
        col = {"red": RED, "green": GREEN, "gold": GOLD}.get(f.get("color", "gold"), GOLD)
        dy = f.get("dy", -90)
        flags += (f'<div id="f{j}" class="abs flg" style="left:{x + f.get("dx", 0):.0f}px;top:{y + dy:.0f}px;border-color:{col}">'
                  f'<b style="color:{col}">{_esc(f["label"])}</b><small>{_esc(f.get("sub", ""))}</small></div>'
                  f'<div id="fp{j}" class="abs fpt" style="left:{x - 12:.0f}px;top:{y - 12:.0f}px;background:{col};box-shadow:0 0 18px {col}"></div>')
        T = v[f["at"]] + f.get("offset", 0)
        fjs += (f'tl.fromTo("#fp{j}",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:.3,ease:"back.out(3)"}},{T:.3f});\n'
                f'tl.fromTo("#f{j}",{{opacity:0,y:20,scale:.8}},{{opacity:1,y:0,scale:1,duration:.4,ease:"back.out(1.8)"}},{T + 0.05:.3f});\n')
    ticks = "".join(f'<div class="abs yt" style="left:{X0 + (y - yrs[0]) / (yrs[-1] - yrs[0]) * (X1 - X0) - 40:.0f}px;top:{Y1 + 18}px">{y}</div>'
                    for y in range(2005, int(yrs[-1]) + 1, 5))
    body = f"""<div id="kk" class="abs">{_esc(v.get('kicker', ''))}</div>
<div id="hud" class="abs"><div class="hl">연도</div><div id="yr">{int(yrs[0])}</div><div class="hl">내 1,000만 원</div><div id="mv">1,000</div><small>만 원</small></div>
<svg class="abs" style="inset:0" viewBox="0 0 1920 1080">
<line x1="{X0}" y1="{base_y:.1f}" x2="{X1}" y2="{base_y:.1f}" stroke="{GREEN}" stroke-width="3" stroke-dasharray="14 12" opacity=".7"/>
<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="rgba(255,255,255,.2)" stroke-width="2"/>
<path id="jl" d="{path}" fill="none" stroke="{v.get('color', RED)}" stroke-width="6" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
<circle id="jd" r="14" fill="#fff" cx="{xs[0]:.1f}" cy="{ys[0]:.1f}" style="filter:drop-shadow(0 0 12px #fff)"/></svg>
<div class="abs bl" style="left:{X0 + 10}px;top:{base_y - 50:.0f}px;color:{GREEN}">원금 1,000만 원</div>
{ticks}{flags}"""
    css = f"""#kk{{left:200px;top:150px;font-family:Pretendard;font-size:50px;color:#fff}}
#hud{{left:560px;top:250px;width:380px;background:rgba(7,11,24,.85);border:2px solid rgba(255,255,255,.1);border-radius:22px;padding:18px 28px;font-family:Pretendard}}
.hl{{font-size:30px;color:{th['sub']}}} #yr{{font-size:72px;color:#fff;line-height:1.1}} #mv{{display:inline-block;font-size:90px;color:{GOLD};line-height:1.05}}
#hud small{{font-size:34px;color:{th['sub']};margin-left:8px}}
.yt{{width:80px;text-align:center;font-family:Pretendard;font-size:30px;color:{th['sub']}}} .bl{{font-family:Pretendard;font-size:32px}}
.flg{{transform:translateX(-50%);background:rgba(7,11,24,.92);border:3px solid;border-radius:16px;padding:8px 20px;text-align:center;font-family:Pretendard;white-space:nowrap;opacity:0}}
.flg b{{display:block;font-size:46px}} .flg small{{font-size:30px;color:#C9D2E8}} .fpt{{width:24px;height:24px;border-radius:50%;opacity:0}}"""
    W_ = json.dumps([round(x, 1) for x in w.values])
    XS, YS, YR = json.dumps([round(x, 1) for x in xs]), json.dumps([round(y, 1) for y in ys]), json.dumps([round(y, 3) for y in yrs])
    js = _fmt_js(0) + f"""const WV={W_},XS={XS},YS={YS},YR={YR},N={n};
const S={{p:0}};
function upd(){{const i=Math.min(N-1,Math.max(0,Math.round(S.p)));document.getElementById('yr').textContent=Math.floor(YR[i]);
 document.getElementById('mv').textContent=fmt(WV[i]);document.getElementById('mv').style.color=WV[i]<1000?"{RED}":"{GREEN}";
 const d=document.getElementById('jd');d.setAttribute('cx',XS[i]);d.setAttribute('cy',YS[i]);
 document.getElementById('jl').style.strokeDashoffset=String(1-(i/(N-1)));}}
tl.fromTo("#kk",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},0.05);
tl.fromTo("#hud",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},0.15);
tl.call(upd,null,0);
"""
    prev_i, prev_t = 0, v.get("t0", 0.4)
    for idx, T in keys:
        d = max(0.4, T - prev_t)
        js += f'tl.to(S,{{p:{idx},duration:{d:.2f},ease:"power1.inOut",onUpdate:upd}},{prev_t:.3f});\n'
        prev_i, prev_t = idx, T
    js += fjs
    return body, css, js


# ── 5. gap ─────────────────────────────────────────────────────
def t_gap(v, th, dur):
    a, b = v["a_pair"], v["b_pair"]   # {label, v0, v1, t0, t1, mult}
    A, B, C = v.get("a", 0.3), v.get("b", 2.0), v.get("c", 4.0)
    def col(k, p, x, color):
        mx = max(p["v1"], p["v0"])
        h0, h1 = p["v0"] / mx * 360, p["v1"] / mx * 360
        cell = lambda bid, h, t, c, yy: (f'<div class="bx"><div class="bt" style="color:{c}">{_esc(t)}</div>'
                                         f'<div id="{bid}" class="bar" style="height:{h:.0f}px;background:{c if c != "#C9D2E8" else "#55607E"}"></div><div class="yy">{yy}</div></div>')
        return (f'<div id="g{k}" class="abs grp" style="left:{x}px"><div class="gl">{_esc(p["label"])}</div>'
                f'<div class="pair">{cell(f"b{k}0", h0, p["t0"], "#C9D2E8", "2000")}{cell(f"b{k}1", h1, p["t1"], color, "2026")}</div>'
                f'<div id="m{k}" class="mul" style="color:{color}">{_esc(p["mult"])}</div></div>')
    body = (_ttl(v, 150, 74)[0] + col(0, a, 120, GREEN) + col(1, b, 1200, RED) +
            f'<div id="tag" class="abs"><span>{_esc(v.get("tag", ""))}</span></div>')
    css = _ttl(v)[1] + f"""
.grp{{top:270px;width:600px}} .gl{{text-align:center;font-family:Pretendard;font-size:50px;color:#fff;margin-bottom:40px}}
.pair{{display:flex;justify-content:center;gap:60px;height:480px;align-items:flex-end}}
.bx{{width:200px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}}
.bar{{width:180px;border-radius:14px 14px 0 0;transform-origin:bottom}} .bt{{font-family:Pretendard;font-size:42px;margin-bottom:10px;white-space:nowrap}}
.yy{{font-family:Pretendard;font-size:34px;color:{th['sub']};margin-top:10px}}
.mul{{text-align:center;font-family:Pretendard;font-size:96px;line-height:1.1}}
#tag{{left:740px;width:440px;top:470px;text-align:center}} #tag span{{display:inline-block;font-family:Pretendard;font-size:50px;line-height:1.3;color:#111;background:{GOLD};border-radius:16px;padding:14px 26px;opacity:0;white-space:pre-line;transform:rotate(-4deg)}}"""
    js = _ttl(v)[2]
    for k, T in ((0, A), (1, B)):
        js += (f'tl.fromTo("#g{k} .gl",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.35,ease:"expo.out"}},{T:.3f});\n'
               f'tl.fromTo("#b{k}0",{{scaleY:0}},{{scaleY:1,duration:.6,ease:"expo.out"}},{T + 0.1:.3f});\n'
               f'tl.fromTo("#b{k}1",{{scaleY:0}},{{scaleY:1,duration:1.2,ease:"power2.inOut"}},{T + 0.6:.3f});\n'
               f'tl.fromTo("#g{k} .bt",{{opacity:0}},{{opacity:1,duration:.3,stagger:.7}},{T + 0.4:.3f});\n'
               f'tl.fromTo("#g{k} .yy",{{opacity:0}},{{opacity:1,duration:.3}},{T + 0.1:.3f});\n'
               f'tl.fromTo("#m{k}",{{opacity:0,scale:2}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}},{T + 1.8:.3f});\n')
    js += f'tl.fromTo("#tag span",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}},{C:.3f});\n'
    return body, css, js


# ── 6. road ────────────────────────────────────────────────────
def t_road(v, th, dur):
    A, B, C = v.get("a", 0.4), v.get("b", 4.0), v.get("c", 8.0)
    RY = 640
    routers = "".join(f'<div class="abs rt" style="left:{300 + i * 300}px;top:{RY - 70}px"><i></i><i></i><i></i></div>' for i in range(5))
    shops = "".join(f'<div class="abs shp" style="left:{360 + i * 300}px;top:{RY - 250}px"><div class="rf"></div></div>' for i in range(5))
    boxes = "".join(f'<div class="abs pk" style="left:-120px;top:{RY + 24}px"></div>' for i in range(6))
    inv = "".join(f'<div class="abs iv" style="left:{150 + (i % 4) * 66}px;top:{900 - (i // 4) * 62}px"></div>' for i in range(10))
    body = f"""{_ttl(v, 70, 72)[0]}
<div id="road" class="abs"><div id="cab"></div><div id="lane"></div></div>
{routers}{shops}{boxes}
<div id="cs" class="abs">{_plq(v['logo_a'], 300, 110)}<div class="cap">{_esc(v.get('cap_a', '길을 까는 회사'))}</div></div>
<div id="az" class="abs">{_plq(v['logo_b'], 300, 110)}<div class="cap">{_esc(v.get('cap_b', '길 위에서 장사하는 회사'))}</div></div>
<div id="ord" class="abs"><div class="ol">{_esc(v.get('order_label', '장비 주문'))}</div><div id="ob"><i id="of"></i></div><div id="ot">{_esc(v.get('order_text', '주문 뚝'))}</div></div>
{inv}<div id="ivt" class="abs">{_esc(v.get('inv_text', ''))}</div>
<div id="cp" class="abs">{_hl(v.get('caption', ''), v.get('caption_hl'), 'mc')}</div>"""
    css = _ttl(v)[1] + f"""{PLQ_CSS}
#road{{left:0;right:0;top:{RY}px;height:110px;background:#1A2342;border-top:4px solid #2C3966;border-bottom:4px solid #2C3966}}
#cab{{position:absolute;left:0;top:10px;height:10px;width:100%;background:{BLUE};box-shadow:0 0 18px {BLUE};transform-origin:left}}
#lane{{position:absolute;left:0;right:0;top:52px;height:6px;background:repeating-linear-gradient(90deg,{GOLD} 0 60px,transparent 60px 120px);transform-origin:left}}
.rt{{width:120px;height:62px;background:#2B3A6B;border:3px solid {BLUE};border-radius:10px;display:flex;gap:12px;align-items:center;justify-content:center}}
.rt i{{width:12px;height:12px;border-radius:50%;background:{GREEN};box-shadow:0 0 8px {GREEN}}}
.shp{{width:180px;height:150px;background:#24305A;border:3px solid #3A4A80;border-radius:8px}} .shp .rf{{position:absolute;left:-14px;right:-14px;top:-30px;height:34px;background:{GOLD};border-radius:10px 10px 0 0}}
.pk{{width:70px;height:56px;background:#C8955A;border:3px solid #8A5E30;border-radius:6px}}
#cs{{left:120px;top:250px;text-align:center}} #az{{left:1500px;top:250px;text-align:center;opacity:0}} .cap{{margin-top:14px;font-family:Pretendard;font-size:36px;color:#C9D2E8}}
#ord{{left:520px;top:250px;width:460px;font-family:Pretendard;opacity:0}} .ol{{font-size:36px;color:{th['sub']}}}
#ob{{height:34px;background:#1B2546;border-radius:10px;margin:10px 0;overflow:hidden}} #of{{display:block;height:100%;width:100%;background:{GREEN};transform-origin:left}}
#ot{{font-size:56px;color:{RED};opacity:0}}
.iv{{width:58px;height:54px;background:#7A5A3A;border:3px solid #4A3420;border-radius:5px;opacity:0}} #ivt{{left:120px;top:780px;font-family:Pretendard;font-size:40px;color:{RED};opacity:0}}
#cp{{left:0;right:0;top:960px;text-align:center;font-family:Pretendard;font-size:62px;color:#fff;opacity:0}} #cp span{{display:inline-block;margin:0 .1em}} #cp .hlw{{color:{GOLD}}}"""
    js = _ttl(v)[2] + f"""tl.fromTo("#cs",{{opacity:0,y:-40}},{{opacity:1,y:0,duration:.5,ease:"expo.out"}},{A:.3f});
tl.fromTo("#cab",{{scaleX:0}},{{scaleX:1,duration:1.8,ease:"power2.inOut"}},{A + 0.3:.3f});
tl.fromTo(".rt",{{opacity:0,y:-80}},{{opacity:1,y:0,duration:.4,ease:"bounce.out",stagger:.3}},{A + 0.4:.3f});
tl.fromTo("#ord",{{opacity:0}},{{opacity:1,duration:.3}},{A + 0.4:.3f});
tl.fromTo("#of",{{scaleX:.15}},{{scaleX:1,duration:1.6,ease:"power2.out"}},{A + 0.4:.3f});
tl.to("#of",{{scaleX:.04,backgroundColor:"{RED}",duration:.5,ease:"power4.in"}},{B:.3f});
tl.fromTo("#ot",{{opacity:0,scale:2}},{{opacity:1,scale:1,duration:.35,ease:"power4.out"}},{B + 0.45:.3f});
tl.to(".rt i",{{backgroundColor:"#555",boxShadow:"none",duration:.3}},{B + 0.3:.3f});
tl.fromTo(".iv",{{opacity:0,y:-200}},{{opacity:1,y:0,duration:.45,ease:"bounce.out",stagger:.08}},{B + 0.8:.3f});
tl.fromTo("#ivt",{{opacity:0}},{{opacity:1,duration:.3}},{B + 1.6:.3f});
tl.fromTo("#lane",{{scaleX:0}},{{scaleX:1,duration:.8,ease:"expo.out"}},{C:.3f});
tl.fromTo("#az",{{opacity:0,y:-40}},{{opacity:1,y:0,duration:.5,ease:"expo.out"}},{C:.3f});
tl.fromTo(".shp",{{opacity:0,scaleY:0,transformOrigin:"50% 100%"}},{{opacity:1,scaleY:1,duration:.4,ease:"back.out(1.8)",stagger:.15}},{C + 0.3:.3f});
tl.to(["#cs","#ord","#ot",".iv","#ivt"],{{opacity:.25,duration:.4}},{C + 0.2:.3f});
const PK=document.querySelectorAll('.pk');PK.forEach((p,i)=>{{tl.fromTo(p,{{x:0}},{{x:2100,duration:3.2,ease:"none"}},{C + 0.6:.3f}+i*0.45);}});
"""
    if v.get("d"):
        js += (f'tl.set("#cp",{{opacity:1}},{v["d"]:.3f});\n'
               f'tl.fromTo("#cp span",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.2,ease:"power4.out",stagger:.07}},{v["d"]:.3f});\n'
               f'tl.fromTo("#mc",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{v["d"] + 0.6:.3f});\n')
    return body, css, js


# ── 7. race ────────────────────────────────────────────────────
def t_race(v, th, dur):
    lanes = v["lanes"]   # [{name, logo?, years, text, hl}]
    y0, y1 = float(v.get("year0", 2000.24)), float(v.get("year1", 2026.9))
    T0, T1 = v.get("go", 0.6), v.get("end", dur - 0.6)
    X0, X1 = 430, 1740
    n = len(lanes)
    lh = min(120, 620 / n)
    body = _ttl(v, 70, 72)[0] + f'<div id="clk" class="abs"><span id="cy">{int(y0)}</span>년</div>'
    body += f'<div class="abs" style="left:{X1}px;top:250px;width:6px;height:{n * lh + 20:.0f}px;background:{GREEN};box-shadow:0 0 18px {GREEN}"></div>'
    body += f'<div class="abs" style="left:{X1 - 40}px;top:{270 + n * lh:.0f}px;font-family:Pretendard;font-size:36px;color:{GREEN}">원금</div>'
    js = _ttl(v)[2] + f'const C={{y:{y0}}};tl.to(C,{{y:{y1},duration:{T1 - T0:.2f},ease:"none",onUpdate:()=>{{document.getElementById("cy").textContent=Math.floor(C.y);}}}},{T0:.3f});\n'
    for i, L in enumerate(lanes):
        top = 260 + i * lh
        logo = (f'<img src="assets/{L["logo"]}" style="max-height:{lh * 0.5:.0f}px;max-width:150px">' if L.get("logo")
                else f'<b>{_esc(L.get("tag", L["name"][:6]))}</b>')
        col = RED if L.get("hl") else (GREEN if L.get("win") else "#9FB0D8")
        body += (f'<div class="abs lab" style="top:{top:.0f}px;height:{lh - 18:.0f}px">{_esc(L["name"])}</div>'
                 f'<div class="abs trk" style="left:{X0}px;width:{X1 - X0}px;top:{top + lh / 2 - 22:.0f}px"></div>'
                 f'<div id="rn{i}" class="abs rn" style="left:{X0 - 90}px;top:{top + 2:.0f}px;height:{lh - 22:.0f}px;border-color:{col}">{logo}</div>'
                 f'<div id="rt{i}" class="abs rtx" style="top:{top + 8:.0f}px;color:{col}">{_esc(L["text"])}</div>')
        dist = min(1.0, L["years"] / (y1 - y0))
        t_arrive = T0 + dist * (T1 - T0)
        xe = X0 - 90 + dist * (X1 - X0)
        tx = xe + 200 if xe + 200 + 300 < 1900 else xe - 290
        js += (f'tl.fromTo("#rn{i}",{{x:0}},{{x:{xe - (X0 - 90):.0f},duration:{t_arrive - T0:.2f},ease:"none"}},{T0:.3f});\n'
               f'tl.fromTo("#rt{i}",{{opacity:0,x:{tx:.0f}}},{{opacity:1,x:{tx:.0f},duration:.3}},{t_arrive:.3f});\n'
               f'tl.fromTo("#rn{i}",{{scale:1.25}},{{scale:1,duration:.35,ease:"back.out(3)",immediateRender:false}},{t_arrive:.3f});\n')
    css = _ttl(v)[1] + f"""
#clk{{right:300px;top:160px;font-family:Pretendard;font-size:66px;color:{GOLD}}}
.lab{{left:60px;width:250px;display:flex;align-items:center;justify-content:flex-end;font-family:Pretendard;font-size:40px;color:#fff}}
.trk{{height:44px;border-radius:22px;background:#141E3C}}
.rn{{width:180px;background:#fff;border:5px solid;border-radius:16px;display:flex;align-items:center;justify-content:center;font-family:Pretendard;font-size:34px;color:#111}}
.rtx{{left:0;font-family:Pretendard;font-size:44px;white-space:nowrap;opacity:0}}"""
    return body, css, js


# ── 8. mirror ──────────────────────────────────────────────────
def t_mirror(v, th, dur):
    rows = v["rows"]   # [{a, b, same: bool, T}]
    body = (f'<div id="la" class="abs lg">{_plq(v["logo_a"], 360, 130)}<div class="ly">{_esc(v.get("year_a", ""))}</div></div>'
            f'<div id="lb" class="abs lg" style="left:1340px">{_plq(v["logo_b"], 360, 130)}<div class="ly">{_esc(v.get("year_b", ""))}</div></div>')
    js = ('tl.fromTo("#la",{opacity:0,x:-60},{opacity:1,x:0,duration:.5,ease:"expo.out"},0.1);\n'
          'tl.fromTo("#lb",{opacity:0,x:60},{opacity:1,x:0,duration:.5,ease:"expo.out"},0.25);\n')
    for i, r in enumerate(rows):
        top = 380 + i * 128
        col = RED if r.get("same") else GREEN
        body += (f'<div id="ra{i}" class="abs ca" style="top:{top}px">{_esc(r["a"])}</div>'
                 f'<div id="rb{i}" class="abs cb" style="top:{top}px">{_esc(r["b"])}</div>'
                 f'<div id="rl{i}" class="abs lk" style="top:{top + 44}px;background:{col}"></div>'
                 f'<div id="rs{i}" class="abs sg" style="top:{top + 4}px;background:{col}">{"=" if r.get("same") else "≠"}</div>')
        T = r["T"]
        js += (f'tl.fromTo("#ra{i}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},{T:.3f});\n'
               f'tl.fromTo("#rb{i}",{{opacity:0,x:40}},{{opacity:1,x:0,duration:.4,ease:"expo.out"}},{T + 0.15:.3f});\n'
               f'tl.fromTo("#rl{i}",{{scaleX:0}},{{scaleX:1,duration:.4,ease:"expo.out"}},{T + 0.35:.3f});\n'
               f'tl.fromTo("#rs{i}",{{opacity:0,scale:2.5}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2)"}},{T + 0.6:.3f});\n')
    css = f"""{PLQ_CSS}
.lg{{left:220px;top:110px;text-align:center}} .ly{{margin-top:12px;font-family:Pretendard;font-size:44px;color:{GOLD}}}
.ca,.cb{{width:600px;height:96px;background:#141E3C;border-radius:16px;display:flex;align-items:center;justify-content:center;font-family:Pretendard;font-size:46px;color:#fff;padding:0 20px;box-sizing:border-box}}
.ca{{left:110px}} .cb{{left:1210px}}
.lk{{left:710px;width:500px;height:8px;transform-origin:center;opacity:.8}}
.sg{{left:908px;width:104px;height:88px;border-radius:44px;color:#fff;font-family:Pretendard;font-size:64px;line-height:86px;text-align:center}}"""
    return body, css, js


TEMPLATES.update({"tickerdrop": t_tickerdrop, "brandvs": t_brandvs, "quizorder": t_quizorder, "journey": t_journey,
                  "gap": t_gap, "road": t_road, "race": t_race, "mirror": t_mirror})

# 효과음: (변수 이름, 소리, 크기) — HFScene.extra_sfx 에서 사용
SFX = {
    "tickerdrop": [("a", "whoosh", 0.5), ("b", "boom", 0.6)],
    "brandvs": [("a", "whoosh", 0.4), ("b", "whoosh", 0.4), ("c", "pop", 0.4)],
    "journey": [],
    "gap": [("a", "whoosh", 0.4), ("b", "whoosh", 0.4), ("c", "pop", 0.5)],
    "road": [("a", "whoosh", 0.4), ("b", "boom", 0.6), ("c", "whoosh", 0.5)],
    "race": [("go", "riser", 0.4)],
    "mirror": [],
}
