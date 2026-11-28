"""HyperFrames 주식채널 세트 3 (ep029 배당주 5종 비교 · 2026-11-28) — 영상별 템플릿 다변화
lineup     직전 편 카드(작게) → 5개 로고 패가 위에서 떨어지며 줄 서고 · 각 패 아래 '1,000만 원' 칩
roster     선수 소개 카드 5장(로고 · 한 줄 정체 · 배당 주기 꼬리표) 차례로 뒤집혀 열림
crashgrid  하락장 방패 표: 열 = 하락장, 행 = 종목 · 칸마다 낙폭이 색 막대로 차오름 · 열 단위로 등장 · 강조 칸 테두리
envelopes  월급 봉투 5개: 1,000만 원 → 1년 배당 금액만큼 봉투가 부풀고 숫자가 굴러감 · 아래 '한 달에'
stairs     배당 계단: 해마다 한 칸씩 오르는 계단(2015→2025) 두 줄 비교 · 끝에 '내 원금 대비 배당률' 꼬리표
iceberg    빙산: 수면 위 = 주가 변화(음수면 수면 아래로 파임) · 수면 아래 = 받은 배당 · 오른쪽 합계 = 총수익
lifemap    인생 지도: 길 위 정거장 2030 · 4050 · 6070 · 정거장마다 '성장 / 배당성장 / 월배당 · 현금' 세 막대(크기 = 무게)
"""
import json

from .hfscene import TEMPLATES, _esc, _hl
from .hfstock import GOLD, GREEN, RED, BLUE, _ttl, _fmt_js, _plq, PLQ_CSS, SFX


def _logo_cell(logo, w, h, label=None):
    lab = f'<div class="lg-l">{_esc(label)}</div>' if label else ""
    return (f'<div class="lg" style="width:{w}px;height:{h}px"><img src="assets/{logo}" style="max-width:{w - 40}px;max-height:{h - (64 if label else 34)}px">{lab}</div>')


LOGO_CSS = (".lg{background:#fff;border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;"
            "box-shadow:0 16px 36px rgba(0,0,0,.45)} .lg-l{margin-top:8px;font-family:Pretendard;font-size:30px;color:#222}")


# ── lineup ────────────────────────────────────────────────
def t_lineup(v, th, dur):
    items = v["items"]   # [{logo, label}]
    A, B = v.get("a", 0.3), v.get("b", 3.0)
    n = len(items)
    pw, gap = 300, 34
    x0 = (1920 - (n * pw + (n - 1) * gap)) / 2
    cells = "".join(f'<div id="p{i}" class="abs" style="left:{x0 + i * (pw + gap):.0f}px;top:360px">{_logo_cell(it["logo"], pw, 210, it.get("label"))}'
                    f'<div class="chip">1,000만 원</div></div>' for i, it in enumerate(items))
    body = f"""<div id="prev" class="abs"><div class="pk">{_esc(v.get('prev_kicker', '지난 영상'))}</div><div class="pt">{_hl(v.get('prev', ''), v.get('prev_hl'), 'mp')}</div></div>
{cells}<div id="q" class="abs">{_hl(v.get('question', ''), v.get('question_hl'), 'mq')}</div>"""
    css = f"""{LOGO_CSS}
#prev{{left:560px;width:800px;top:330px;background:#141E3C;border:3px solid {RED};border-radius:24px;padding:26px 30px;text-align:center;font-family:Pretendard}}
.pk{{font-size:34px;color:{th['sub']}}} .pt{{font-size:64px;color:#fff;margin-top:6px}} .pt span{{display:inline-block;margin:0 .1em}} .pt .hlw{{color:{RED}}}
.chip{{margin:18px auto 0;width:220px;text-align:center;font-family:Pretendard;font-size:38px;color:#111;background:{GOLD};border-radius:14px;padding:6px 0}}
#q{{left:0;right:0;top:760px;text-align:center;font-family:Pretendard;font-size:80px;color:#fff;opacity:0}} #q span{{display:inline-block;margin:0 .12em}} #q .hlw{{color:{GOLD}}}"""
    js = f"""tl.fromTo("#prev",{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.5,ease:"back.out(1.6)"}},{A:.3f});
tl.fromTo("#mp",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{A + 0.6:.3f});
tl.to("#prev",{{scale:.42,x:-650,y:-250,opacity:.75,duration:.6,ease:"power3.inOut"}},{B - 0.4:.3f});
"""
    for i in range(n):
        js += f'tl.fromTo("#p{i}",{{opacity:0,y:-420,rotation:{(-1) ** i * 8}}},{{opacity:1,y:0,rotation:0,duration:.6,ease:"bounce.out"}},{B + i * 0.22:.3f});\n'
    js += (f'tl.set("#q",{{opacity:1}},{v.get("c", B + 2.0):.3f});\n'
           f'tl.fromTo("#q span",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.35,ease:"expo.out",stagger:.07}},{v.get("c", B + 2.0):.3f});\n'
           f'tl.fromTo("#mq",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"expo.out"}},{v.get("c", B + 2.0) + 0.6:.3f});\n')
    return body, css, js


# ── roster ────────────────────────────────────────────────
def t_roster(v, th, dur):
    rows = v["rows"]   # [{logo, name, line, tag, T}]
    n = len(rows)
    cw, gap = 330, 26
    x0 = (1920 - (n * cw + (n - 1) * gap)) / 2
    body = _ttl(v, 150, 70)[0]
    js = _ttl(v)[2]
    for i, r in enumerate(rows):
        body += (f'<div id="r{i}" class="abs rc" style="left:{x0 + i * (cw + gap):.0f}px">'
                 f'<div class="rl">{_logo_cell(r["logo"], cw - 40, 150)}</div><div class="rn">{_esc(r["name"])}</div>'
                 f'<div class="rd">{_esc(r["line"])}</div><div class="rt">{_esc(r.get("tag", ""))}</div></div>')
        js += f'tl.fromTo("#r{i}",{{opacity:0,rotationY:90}},{{opacity:1,rotationY:0,duration:.55,ease:"back.out(1.4)"}},{r["T"]:.3f});\n'
    css = _ttl(v)[1] + f"""{LOGO_CSS}
.rc{{top:290px;width:{cw}px;height:600px;background:#141E3C;border-radius:26px;padding:20px;box-sizing:border-box;transform-origin:50% 50%;text-align:center}}
.rl{{display:flex;justify-content:center}} .rn{{margin-top:22px;font-family:Pretendard;font-size:46px;color:#fff}}
.rd{{margin-top:14px;font-family:Pretendard;font-size:32px;line-height:1.35;color:#C9D2E8;min-height:180px}}
.rt{{margin:16px auto 0;width:fit-content;font-family:Pretendard;font-size:30px;color:#111;background:{GOLD};border-radius:12px;padding:6px 16px}}"""
    return body, css, js


# ── crashgrid ─────────────────────────────────────────────
def t_crashgrid(v, th, dur):
    cols, rows = v["cols"], v["rows"]   # cols: [{label, T}] · rows: [{name, vals:[숫자 or null], hl:[열 번호]}]
    X0, Y0, CW, RH = 430, 245, 360, 92
    body = _ttl(v, 150, 70)[0]
    js = _ttl(v)[2]
    for j, c in enumerate(cols):
        body += f'<div id="h{j}" class="abs ch" style="left:{X0 + j * CW}px;width:{CW - 20}px">{_esc(c["label"])}</div>'
        js += f'tl.fromTo("#h{j}",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.35,ease:"expo.out"}},{c["T"]:.3f});\n'
    vmax = float(v.get("vmax", 50))
    for i, r in enumerate(rows):
        y = Y0 + 80 + i * RH
        body += f'<div class="abs rn2" style="top:{y}px">{_esc(r["name"])}</div>'
        for j, val in enumerate(r["vals"]):
            x = X0 + j * CW
            if val is None:
                body += f'<div id="c{i}_{j}" class="abs cell na" style="left:{x}px;top:{y}px;width:{CW - 20}px">상장 전</div>'
            else:
                k = min(1, abs(val) / vmax)
                col = RED if abs(val) >= v.get("red_at", 25) else (GOLD if abs(val) >= v.get("gold_at", 12) else GREEN)
                hl = j in r.get("hl", [])
                body += (f'<div id="c{i}_{j}" class="abs cell" style="left:{x}px;top:{y}px;width:{CW - 20}px;{"outline:5px solid " + GOLD + ";" if hl else ""}">'
                         f'<i style="width:{k * 100:.0f}%;background:{col}"></i><b>{val:+.0f}%</b></div>')
            js += f'tl.fromTo("#c{i}_{j} i, #c{i}_{j} b",{{opacity:0,scaleX:0,transformOrigin:"left"}},{{opacity:1,scaleX:1,duration:.4,ease:"expo.out"}},{cols[j]["T"] + 0.1 + i * 0.07:.3f});\n' if val is not None else \
                  f'tl.fromTo("#c{i}_{j}",{{opacity:0}},{{opacity:1,duration:.3}},{cols[j]["T"] + 0.1 + i * 0.07:.3f});\n'
    css = _ttl(v)[1] + f"""
.ch{{top:{Y0}px;text-align:center;font-family:Pretendard;font-size:38px;color:{GOLD}}}
.rn2{{left:60px;width:340px;height:{RH - 18}px;display:flex;align-items:center;justify-content:flex-end;font-family:Pretendard;font-size:40px;color:#fff}}
.cell{{height:{RH - 18}px;background:#141E3C;border-radius:12px;overflow:hidden}} .cell i{{position:absolute;left:0;top:0;bottom:0;opacity:.55}}
.cell b{{position:absolute;right:18px;top:50%;transform:translateY(-50%);font-family:Pretendard;font-size:44px;color:#fff}}
.na{{display:flex;align-items:center;justify-content:center;font-family:Pretendard;font-size:30px;color:{th['sub']}}}"""
    return body, css, js


# ── envelopes ─────────────────────────────────────────────
def t_envelopes(v, th, dur):
    rows = v["rows"]   # [{label, value(만 원), month, T, hl}]
    mx = max(r["value"] for r in rows)
    n = len(rows)
    cw = 1640 / n
    body = _ttl(v, 150, 70)[0]
    js = _ttl(v)[2] + _fmt_js(0)
    for i, r in enumerate(rows):
        s = 0.45 + 0.55 * (r["value"] / mx) ** 0.5
        w, h = 240 * s, 170 * s
        cx = 140 + cw * i + cw / 2
        body += (f'<div id="e{i}" class="abs env" style="left:{cx - w / 2:.0f}px;top:{640 - h:.0f}px;width:{w:.0f}px;height:{h:.0f}px;{"box-shadow:0 0 50px " + GOLD + ";" if r.get("hl") else ""}"><div class="fl2"></div></div>'
                 f'<div id="v{i}" class="abs ev" style="left:{cx - 160:.0f}px"><span id="n{i}">0</span>만 원</div>'
                 f'<div class="abs el" style="left:{cx - 160:.0f}px">{_esc(r["label"])}</div>'
                 f'<div id="m{i}" class="abs em" style="left:{cx - 160:.0f}px">{_esc(r.get("month", ""))}</div>')
        T = r["T"]
        js += (f'tl.fromTo("#e{i}",{{opacity:0,scale:.3,transformOrigin:"50% 100%"}},{{opacity:1,scale:1,duration:.6,ease:"back.out(1.8)"}},{T:.3f});\n'
               f'const N{i}={{v:0}};tl.to(N{i},{{v:{r["value"]},duration:1.0,ease:"power3.out",onUpdate:()=>{{document.getElementById("n{i}").textContent=fmt(N{i}.v);}}}},{T:.3f});\n'
               f'tl.fromTo("#m{i}",{{opacity:0}},{{opacity:1,duration:.3}},{v.get("mm", T + 1.0):.3f});\n')
    css = _ttl(v)[1] + f"""
.env{{background:linear-gradient(#F3E2B8,#D9BF84);border-radius:10px;box-shadow:0 14px 30px rgba(0,0,0,.45)}}
.fl2{{position:absolute;left:0;right:0;top:0;height:55%;background:linear-gradient(#E8D29E,#CDB070);clip-path:polygon(0 0,100% 0,50% 100%)}}
.ev{{top:670px;width:320px;text-align:center;font-family:Pretendard;font-size:58px;color:{GOLD}}}
.el{{top:750px;width:320px;text-align:center;font-family:Pretendard;font-size:38px;color:#fff}}
.em{{top:805px;width:320px;text-align:center;font-family:Pretendard;font-size:32px;color:{th['sub']};opacity:0}}"""
    return body, css, js


# ── stairs ────────────────────────────────────────────────
def t_stairs(v, th, dur):
    lines = v["lines"]   # [{name, color, vals:[...], start_text, end_text, yoc, T}]
    years = v["years"]
    n = len(years)
    X0, X1, Y1, HH = 220, 1680, 860, 480
    mx = max(max(l["vals"]) / l["vals"][0] for l in lines)
    body = _ttl(v, 150, 70)[0]
    js = _ttl(v)[2]
    sw = (X1 - X0) / n
    for li, l in enumerate(lines):
        col = {"gold": GOLD, "green": GREEN, "red": RED, "blue": BLUE}.get(l.get("color", "gold"), GOLD)
        for k, val in enumerate(l["vals"]):
            h = (val / l["vals"][0]) / mx * HH
            x = X0 + k * sw + li * sw * 0.45
            body += f'<div id="s{li}_{k}" class="abs st" style="left:{x:.0f}px;top:{Y1 - h:.0f}px;width:{sw * 0.42:.0f}px;height:{h:.0f}px;background:{col}"></div>'
            js += f'tl.fromTo("#s{li}_{k}",{{scaleY:0}},{{scaleY:1,duration:.35,ease:"back.out(1.6)"}},{l["T"] + k * 0.12:.3f});\n'
        body += (f'<div id="lt{li}" class="abs ltag" style="left:{X1 + 10}px;top:{Y1 - (l["vals"][-1] / l["vals"][0]) / mx * HH - 30 + li * 0:.0f}px;color:{col}">{_esc(l["name"])} {_esc(l.get("end_text", ""))}</div>')
        js += f'tl.fromTo("#lt{li}",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.35,ease:"expo.out"}},{l["T"] + n * 0.12:.3f});\n'
        if l.get("yoc"):
            body += f'<div id="y{li}" class="abs yoc" style="top:{300 + li * 80}px;border-color:{col}">{_esc(l["yoc"])}</div>'
            js += f'tl.fromTo("#y{li}",{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2)"}},{v.get("y", l["T"] + 2.0) + li * 0.4:.3f});\n'
    body += "".join(f'<div class="abs yy" style="left:{X0 + k * sw:.0f}px;width:{sw:.0f}px;top:{Y1 + 12}px">{y}</div>' for k, y in enumerate(years) if k % 2 == 0)
    css = _ttl(v)[1] + f"""
.st{{border-radius:6px 6px 0 0;transform-origin:bottom}} .ltag{{font-family:Pretendard;font-size:40px;white-space:nowrap}}
.yy{{text-align:left;font-family:Pretendard;font-size:30px;color:{th['sub']}}}
.yoc{{left:220px;font-family:Pretendard;font-size:44px;color:#fff;border:4px solid;border-radius:16px;padding:8px 22px;background:#0E1630;opacity:0}}"""
    return body, css, js


# ── iceberg ───────────────────────────────────────────────
def t_iceberg(v, th, dur):
    rows = v["rows"]   # [{name, logo, price, divs, total, T, hl}]  (% 단위)
    n = len(rows)
    WL = 470   # 수면 y
    sc = float(v.get("scale", 3.2))   # 1% = px
    cw = 1640 / n
    body = _ttl(v, 150, 66)[0] + f'<div class="abs sea" style="top:{WL}px"></div><div class="abs wl" style="top:235px">{_esc(v.get("water", "▲ 주가 · ▼ 받은 배당"))}</div>'
    js = _ttl(v)[2]
    for i, r in enumerate(rows):
        cx = 140 + cw * i + cw / 2
        w = cw * 0.5
        ph = abs(r["price"]) * sc
        dh = r["divs"] * sc
        if r["price"] >= 0:
            body += f'<div id="pa{i}" class="abs ice" style="left:{cx - w / 2:.0f}px;top:{WL - ph:.0f}px;width:{w:.0f}px;height:{ph:.0f}px;background:#DDEBFF"></div>'
            dtop = WL
        else:   # 주가가 빠지면 수면 아래로 파인 빨간 칸
            body += f'<div id="pa{i}" class="abs ice" style="left:{cx - w / 2:.0f}px;top:{WL:.0f}px;width:{w:.0f}px;height:{ph:.0f}px;background:{RED};opacity:.85"></div>'
            dtop = WL + ph
        body += (f'<div id="dv{i}" class="abs ice" style="left:{cx - w / 2:.0f}px;top:{dtop:.0f}px;width:{w:.0f}px;height:{dh:.0f}px;background:{GOLD}"></div>'
                 f'<div class="abs nm" style="left:{cx - 140:.0f}px">{_esc(r["name"])}</div>'
                 f'<div id="pt{i}" class="abs pt2" style="left:{cx - 140:.0f}px;top:{(WL - ph - 56) if r["price"] >= 0 else WL - 56:.0f}px;color:{"#DDEBFF" if r["price"] >= 0 else RED}">주가 {r["price"]:+.0f}%</div>'
                 f'<div id="dt{i}" class="abs pt2" style="left:{cx - 140:.0f}px;top:{dtop + dh + 6:.0f}px;color:{GOLD}">배당 +{r["divs"]:.0f}%</div>'
                 f'<div id="tt{i}" class="abs tot" style="left:{cx - 140:.0f}px;{"color:" + GOLD + ";" if r.get("hl") else ""}">합계 {r["total"]:+.0f}%</div>')
        T = r["T"]
        js += (f'tl.fromTo("#pa{i}",{{scaleY:0,transformOrigin:"{"50% 100%" if r["price"] >= 0 else "50% 0%"}"}},{{scaleY:1,duration:.5,ease:"expo.out"}},{T:.3f});\n'
               f'tl.fromTo("#pt{i}",{{opacity:0}},{{opacity:1,duration:.3}},{T + 0.3:.3f});\n'
               f'tl.fromTo("#dv{i}",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,duration:.5,ease:"expo.out"}},{T + 0.6:.3f});\n'
               f'tl.fromTo("#dt{i}",{{opacity:0}},{{opacity:1,duration:.3}},{T + 0.9:.3f});\n'
               f'tl.fromTo("#tt{i}",{{opacity:0,scale:1.5}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2)"}},{v.get("tot", T + 1.2):.3f});\n')
    css = _ttl(v)[1] + f"""
.sea{{left:0;right:0;bottom:0;background:linear-gradient(rgba(40,90,180,.35),rgba(10,20,50,.6));border-top:4px solid #6FA8FF}}
.wl{{right:80px;font-family:Pretendard;font-size:30px;color:#9FC2FF}}
.ice{{border-radius:8px}} .nm{{top:{WL + 235}px;width:280px;text-align:center;font-family:Pretendard;font-size:40px;color:#fff}}
.pt2{{width:280px;text-align:center;font-family:Pretendard;font-size:34px;opacity:0}}
.tot{{top:{WL + 285}px;width:280px;text-align:center;font-family:Pretendard;font-size:50px;color:#fff;opacity:0}}"""
    return body, css, js


# ── lifemap ───────────────────────────────────────────────
def t_lifemap(v, th, dur):
    stops = v["stops"]   # [{age, title, bars:[[label, weight 1~3], ...], note, T}]
    n = len(stops)
    body = _ttl(v, 130, 66)[0] + '<svg class="abs" style="inset:0" viewBox="0 0 1920 1080"><path id="road" d="M120,900 C520,860 520,700 960,700 C1400,700 1400,560 1800,520" fill="none" stroke="#2C3966" stroke-width="70" stroke-linecap="round"/><path id="dash" d="M120,900 C520,860 520,700 960,700 C1400,700 1400,560 1800,520" fill="none" stroke="' + GOLD + '" stroke-width="6" stroke-dasharray="26 22" pathLength="1"/></svg>'
    js = _ttl(v)[2] + 'tl.fromTo("#road",{opacity:0},{opacity:1,duration:.5},0.2);tl.fromTo("#dash",{strokeDashoffset:1},{strokeDashoffset:0,duration:1.4,ease:"power2.inOut"},0.3);\n'
    xs = [330, 960, 1590]
    for i, s in enumerate(stops):
        x = xs[i]
        bars = "".join(f'<div class="bb"><span>{_esc(b[0])}</span><i style="width:{b[1] * 70}px;background:{[BLUE, GREEN, GOLD][k % 3]}"></i></div>' for k, b in enumerate(s["bars"]))
        body += (f'<div id="c{i}" class="abs card" style="left:{x - 270}px"><div class="ag">{_esc(s["age"])}</div><div class="at">{_esc(s["title"])}</div>{bars}'
                 f'<div class="an">{_esc(s.get("note", ""))}</div></div>')
        js += f'tl.fromTo("#c{i}",{{opacity:0,y:60}},{{opacity:1,y:0,duration:.5,ease:"back.out(1.6)"}},{s["T"]:.3f});\n'
        js += f'tl.fromTo("#c{i} .bb i",{{scaleX:0,transformOrigin:"left"}},{{scaleX:1,duration:.5,ease:"expo.out",stagger:.12}},{s["T"] + 0.3:.3f});\n'
    css = _ttl(v)[1] + f"""
.card{{top:240px;width:540px;background:#141E3C;border:3px solid #2C3966;border-radius:26px;padding:24px 28px;box-sizing:border-box;font-family:Pretendard}}
.ag{{font-size:64px;color:{GOLD}}} .at{{font-size:38px;color:#fff;margin-bottom:16px}}
.bb{{display:flex;align-items:center;gap:14px;margin:10px 0}} .bb span{{width:210px;font-size:30px;color:#C9D2E8}} .bb i{{display:block;height:28px;border-radius:8px}}
.an{{margin-top:14px;font-size:28px;color:{th['sub']};line-height:1.35}}"""
    return body, css, js


TEMPLATES.update({"lineup": t_lineup, "roster": t_roster, "crashgrid": t_crashgrid, "envelopes": t_envelopes,
                  "stairs": t_stairs, "iceberg": t_iceberg, "lifemap": t_lifemap})
SFX.update({"lineup": [("b", "whoosh", 0.5)], "roster": [], "crashgrid": [], "envelopes": [], "stairs": [], "iceberg": [], "lifemap": []})
