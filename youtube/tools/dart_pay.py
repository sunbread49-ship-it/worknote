"""DART 사업보고서 '임원의 보수 등' · '직원 현황' 텍스트 추출
  python3 tools/dart_pay.py 하이브 [--year 2025]  → episodes/.../dart/<회사>_pay.txt
"""
import re, sys, html, urllib.request, urllib.parse
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0"}


def get(url, data=None):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None, headers=UA)
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")


def reports(name, start="20250101", end="20261231", kind="A001"):
    h = get("https://dart.fss.or.kr/dsab007/detailSearch.ax", {"textCrpNm": name, "startDate": start, "endDate": end, "publicType": kind, "maxResults": 20})
    return re.findall(r"openReportViewer\('(\d+)'.*?title=\"([^\"]*)\"", h)


def section(rcp, keys=("임원의 보수 등", "임원 및 직원 등의 현황")):
    m = get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp}")
    out = {}
    for blk in re.split(r"node[12] = \{\};", m):
        t = re.search(r"\['text'\] = \"([^\"]*)\"", blk)
        if not t or not any(k in t.group(1) for k in keys):
            continue
        p = dict(re.findall(r"\['(rcpNo|dcmNo|eleId|offset|length|dtd)'\] = \"([^\"]*)\"", blk))
        v = get("https://dart.fss.or.kr/report/viewer.do?" + urllib.parse.urlencode(p))
        v = re.sub(r"<(script|style).*?</\1>", "", v, flags=re.S)
        v = re.sub(r"</t[dh]>", " | ", v); v = re.sub(r"</tr>|<br\s*/?>|</p>", "\n", v)
        txt = html.unescape(re.sub(r"<[^>]+>", "", v))
        out[t.group(1)] = re.sub(r"[ \t\xa0]+", " ", re.sub(r"\n\s*\n+", "\n", txt))
    return out


if __name__ == "__main__":
    name = sys.argv[1]
    rs = reports(name)
    print(rs[:4])
    rcp = rs[0][0]
    secs = section(rcp)
    d = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}_{rcp}.txt").write_text("\n\n=====\n".join(f"## {k}\n{v}" for k, v in secs.items()), encoding="utf-8")
    print(name, rcp, {k: len(v) for k, v in secs.items()})
