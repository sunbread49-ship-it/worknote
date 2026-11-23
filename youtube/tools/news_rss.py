"""구글 뉴스 RSS 헤드라인 (허용 호스트 news.google.com) — 대본 사실 확인용
  python3 tools/news_rss.py "Alphabet stock" [en|ko] [개수]
제목 · 날짜 · 매체만 출력 (본문은 받지 않음)
"""
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

q = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else "en"
n = int(sys.argv[3]) if len(sys.argv) > 3 else 15
hl = {"en": "hl=en-US&gl=US&ceid=US:en", "ko": "hl=ko&gl=KR&ceid=KR:ko"}[lang]
u = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&" + hl
x = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
for it in ET.fromstring(x).iter("item")[:n] if False else list(ET.fromstring(x).iter("item"))[:n]:
    src = it.find("source")
    print(it.findtext("pubDate", "")[:16], "|", (src.text if src is not None else ""), "|", it.findtext("title", ""))
