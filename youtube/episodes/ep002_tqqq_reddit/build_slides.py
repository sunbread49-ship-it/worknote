# EP002 슬라이드 구성 생성 스크립트 (episode.yaml을 다시 만들 때 사용). 직접 수정은 episode.yaml에 해도 됨.
import yaml, re
import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'episode.yaml')
src=open(P).read()
head=src[:src.index('scenes:\n')]

def K(lines, text, hl="", hc=None, sub=None, size=120, bg=None, bgc=None, ch=None, stamp=None, extra=None):
    """임팩트 문장 슬라이드 (1개 항목)"""
    it={'text':text,'on':1,'size':size}
    if hl: it['highlight']=hl
    if hc: it['hl_color']=hc
    if sub: it['sub']=sub
    d={'type':'kinetic','items':[it],'narration':lines}
    if bg: d['bg_word']=bg
    if bgc: d['bg_color']=bgc
    if ch: d['chapter']=ch
    if stamp: d['stamp']=stamp
    if extra: d.update(extra)
    return d

def VS(lines, heading, L, R, hl="", ch=None, extra=None):
    d={'type':'versus','heading':heading,'left':L,'right':R,'narration':lines}
    if hl: d['highlight']=hl
    if ch: d['chapter']=ch
    if extra: d.update(extra)
    return d

SRC="자료: Yahoo Finance 수정주가"
S=[]
# ── 1. 훅
S.append({'type':'reddit','chapter':'레딧 썰','posts':[
  {'flair':'Gain','title':'TQQQ 몰빵 2년, 계좌 30배 찍었습니다','en':'"30x in 2 years. TQQQ and chill."','up':'24.1k','comments':'3,812','on':2}],
  'stickers':[{'e':'rocket','pos':[1500,330],'size':200,'on':2,'offset':0.5,'rot':-15}],
  'narration':["자, 미국 최대 주식 커뮤니티죠. 레딧의 월스트리트베츠.","여기 들어가 보면요, 이런 글이 진짜 자주 올라옵니다. | TQQQ에 몰빵했더니 2년 만에 30배가 됐다."]})
S.append({'type':'reddit','chapter':'레딧 썰','posts':[
  {'flair':'Discussion','title':'레버리지 ETF 장기 보유하면 녹는다는 거, 다 미신 아님?','en':'"Leverage decay is a myth. Change my mind."','up':'8.7k','comments':'2,940','on':1},
  {'flair':'Loss','title':'SQQQ로 하락장 대비하다가… 계좌가 녹았습니다','en':'"SQQQ is a casino and I\'m the house\'s favorite customer."','up':'15.3k','comments':'1,207','on':2}],
  'mascot':{'on':2,'pos':[1700,820],'size':150,'say':'이거… 진짜야?','side':'left','offset':1.5},
  'narration':["레버리지 ETF 오래 들고 있으면 녹는다? | 그거 다 미신이다.","근데 반대편엔요, 인버스 SQQQ로 하락장 대비하다가 | 계좌가 녹았다는 글도 있습니다."]})
S.append(K(["과연 이 썰들, 진짜일까요?"],"이 썰들, 진짜일까?",hl="진짜일까?",size=130))
S.append({'type':'kinetic','stack':True,'bg_word':'30x','items':[{'text':'2년 만에 30배?','on':1,'size':130,'highlight':'30배?'},{'text':'1,000만 원 → 3억','on':2,'size':130,'highlight':'3억'}],
  'narration':["솔직히요. 이런 글 보면 손가락 근질근질하죠.","2년에 30배면, 천만 원이 3억이에요. | 아 진짜, 이거 인생역전 아닙니까?"]})
# ── 2. 타이틀
S.append({'type':'title','skyline':True,'y':250,'kicker':'레딧 썰 팩트체크 ①','title':'TQQQ 2년 만에 30배?\n그리고 SQQQ의 진실','highlight':'30배?',
  'subtitle':'2010년 상장 이후 실제 데이터로 끝까지 확인해봤습니다',
  'narration':["그래서 준비했습니다. 레딧 썰, 팩트체크.","오늘은 2010년 상장 이후 16년 치 실제 데이터로, | TQQQ랑 SQQQ를 끝까지 한번 파헤쳐 보겠습니다."]})
S.append(K(["아, 참고로요. 특정 상품 사라는 영상, 절대 아닙니다. | 오히려 그 반대에 가까워요."],"매수 추천 영상 아닙니다",hl="아닙니다",hc='down',sub="오히려 그 반대에 가깝습니다",size=110))
# ── 3. 기초
S.append(VS(["자, 먼저 간단히 짚고 갈게요.","TQQQ는요, 나스닥100이 하루에 1% 오르면, 3% 오르도록 만든 ETF예요."],"TQQQ = 나스닥100 하루 움직임 × 3",
  {'title':'나스닥100','value':'+1%','sub':'하루 상승','color':'neutral','on':2},{'title':'TQQQ','value':'+3%','sub':'같은 날','color':'up','on':2,'offset':0},hl="× 3",ch="기초"))
S.append(VS(["SQQQ는 정반대입니다. 지수가 하루 1% 떨어지면, 3% 오르는 인버스 상품이고요."],"SQQQ = 반대로 × 3",
  {'title':'나스닥100','value':'-1%','sub':'하루 하락','color':'neutral','on':1},{'title':'SQQQ','value':'+3%','sub':'같은 날','color':'down','on':1},hl="반대로",ch="기초"))
S.append({'type':'card','chapter':'기초','heading':'나스닥100 = 미국 대형 기술주 100개','highlight':'100개','width':1500,
  'bullets':[{'text':'애플 · 마이크로소프트 · 엔비디아 …','on':1},{'text':'이걸 하루 단위로 3배로 타는 상품','on':1,'highlight':'3배','hl_color':'up'}],
  'narration':["애플, 마이크로소프트, 엔비디아. | 이런 미국 대형 기술주 100개를 3배로 타는 셈이죠."]})
S.append(K(["근데 여기서 딱 하나만 기억해 주세요. | '하루'. 이게 오늘 얘기의 핵심입니다."],"핵심 단어: '하루'",hl="'하루'",size=140,bg="1 DAY"))
# ── 4. 302배
chart302={'lines':[{'series':'tqqq','color':'up','label':'TQQQ'},{'series':'qqq','color':'neutral','label':'QQQ','fill':False}],
  'start':'2010-02-11','end':'2026-10-30','base':1000,'unit':'won','log':True,'end_labels':True,'rect':[210,200,1420,620],
  'title':'2010년 2월에 1,000만 원 넣었다면 (로그 스케일)','draw':{'on':1,'dur':2.6},'source':'자료: Yahoo Finance 수정주가(배당 재투자) · 2010.2.11~2026.10.30'}
S.append({'type':'chart','chapter':'썰 ① 대박','chart':chart302,
  'narration':["자, 그럼 첫 번째 썰부터 볼게요.","2010년 2월, TQQQ가 처음 상장한 날. | 여기에 1,000만 원을 넣었다고 쳐 봅시다."]})
S.append(VS(["회색 선은 레버리지 없는 나스닥100, QQQ예요. | 이것도 16년 동안 약 18배. 1억 8천만 원이 됐습니다.","근데요, 빨간 선. TQQQ는요."],"1,000만 원의 16년 뒤",
  {'title':'QQQ (1배)','value':'1.8억','sub':'약 18배','color':'neutral','on':1},{'title':'TQQQ (3배)','value':'?','sub':'과연…','color':'up','on':2},ch="썰 ① 대박"))
S.append({'type':'bignum','chapter':'썰 ① 대박','label':'TQQQ 16년 수익','from':1,'to':302,'fmt':'{:,.0f}배','on':1,'dur':1.2,'color':'up','log_count':True,
  'sub':'1,000만 원 → 30억 원','sub_on':2,'sfx':[{'name':'cash','on':2,'offset':0.2}],'narration':["무려, 302배.","1,000만 원이, 30억이 됐습니다.","네, 잘못 보신 거 아니에요. 30억입니다. 아 진짜…"]})
# ── 5. 단톡방
S.append({'type':'phone','mode':'chat','bg':'dark','room':'주식하는 친구들 (4)','side_text':'그때 넣을걸…','side_on':3,
  'messages':[{'who':'other','name':'민수','avatar':'cool','text':'야 TQQQ 16년 동안 300배래','on':1},
              {'who':'me','text':'1,000만 원 넣었으면 30억?? ㄷㄷ','on':2},
              {'who':'other','name':'지훈','avatar':'cry','text':'아 2010년의 나 뭐 했냐','on':3},
              {'who':'other','name':'민수','avatar':'cool','text':'지금이라도 몰빵 ㄱㄱ?','on':4}],
  'narration':["이런 숫자 돌면, 단톡방은 바로 이렇게 되죠.","천만 원 넣었으면 30억이라고?","아… 2010년의 나는 대체 뭘 한 거냐.","지금이라도 몰빵 가?"]})
S.append(K(["잠깐만요. | 데이터는요, 아직 할 말이 많이 남았습니다."],"잠깐만요.",sub="데이터는 아직 할 말이 많이 남았습니다",size=150))
# ── 6. 10배
S.append(K(["그럼 '2년 만에 30배'는요? 이건 진짜일까요?","16년 동안 아무 날에나 샀다고 치고, | 2년 안에 찍을 수 있었던 최고 기록을 전부 계산해 봤어요."],"2년 안에 낼 수 있었던 최고 기록은?",hl="최고 기록",size=100,ch="썰 ① 팩트체크"))
S.append({'type':'bignum','chapter':'썰 ① 팩트체크','label':'TQQQ, 2년 안에 낸 최고 배수','from':1,'to':9.98,'fmt':'{:.1f}배','final':'약 10배','on':1,'dur':1.0,'color':'up',
  'sub':'2020.3.20 코로나 바닥 → 2021.11.19 고점 (20개월)','sub_on':2,
  'narration':["결과는, 약 10배.","2020년 3월 코로나 바닥에서 사서, | 2021년 11월 고점에 판 경우예요. 솔직히 이것도 엄청나죠."]})
S.append(K(["근데 30배는, 없었습니다. | 썰 판정. 과장입니다."],"\"2년 만에 30배\"",size=120,ch="썰 ① 팩트체크",
  stamp={'text':'판정: 과장','color':'gold','on':1,'offset':1.2,'pos':[960,720],'rot':-6,'size':90}))
# ── 7. -82%
S.append({'type':'chart','chapter':'썰 ① 반전','chart':{'series':'tqqq','start':'2019-06-01','end':'2021-12-31','color':[240,84,84],'ymin':-6,
  'title':'TQQQ 주가 · 2019.6 ~ 2021.12 (달러)','draw':{'on':1,'dur':2.2},
  'marks':[{'date':'2020-03-20','label':'코로나 바닥','on':1,'offset':0,'dy':40,'dx':60,'color':'gold'},{'date':'2021-11-19','label':'고점 (+898%)','on':2,'dy':-60,'color':'up'}],'source':SRC},
  'narration':["자, 근데 이 그래프. 조금만 더 보시죠.","10배 오른 바로 그 고점에서,"]})
S.append({'type':'chart','chapter':'썰 ① 반전','chart':{'series':'tqqq','start':'2021-11-19','end':'2022-12-31','color':[74,144,255],'ymin':0,
  'title':'TQQQ · 2021.11.19 고점 이후 13개월','draw':{'on':1,'dur':2.0},
  'marks':[{'date':'2022-12-28','label':'-82%','on':1,'offset':2.0,'dy':-80,'dx':-120,'color':'down','size':48}],'source':SRC},
  'shake':[{'on':1,'offset':2.0,'dur':0.5,'amp':16,'sfx':'boom'}],
  'narration':["다음 13개월 동안, TQQQ는 82%가 빠집니다.","10억이 1억 8천이 되는 속도예요. | 2년 동안 번 걸, 1년 만에 거의 다 토해낸 거죠."]})
S.append({'type':'chart','chapter':'썰 ① 반전','chart':{'series':'tqqq','start':'2021-11-01','end':'2024-12-31','color':[240,84,84],'ymin':0,
  'title':'TQQQ · 고점 회복까지','draw':{'on':1,'dur':2.0},
  'marks':[{'date':'2021-11-19','label':'고점','on':1,'dy':-50,'dx':60,'color':'up'},{'date':'2024-12-04','label':'본전 회복','sub':'3년 뒤','on':1,'offset':2.0,'dy':-60,'dx':-80,'color':'gold'}],'source':SRC},
  'narration':["그리고 그 고점, 다시 회복하는 데 3년 걸렸습니다."]})
# ── 8. 계좌
S.append({'type':'phone','mode':'account','bg':'dark','app':'내 주식 계좌','from':1000000000,'to':183400000,'drop_on':2,'drop_dur':3.0,
  'holdings':[{'name':'TQQQ','pct':-81.7}],'notes':[{'text':'TQQQ 오늘 -16.5% (2022.9.13)','on':3}],
  'side_text':'10억 → 1.8억','side_on':3,'side_highlight':'1.8억','side_hl_color':'down',
  'narration':["만약 그 고점에 계좌에 10억이 있었다? 어떻게 됐을까요.","숫자 녹는 거, 실시간으로 보시죠.","13개월 뒤. 1억 8천만 원."]})
S.append({'type':'bignum','label':'13개월 동안 하루에 -5% 넘게 빠진 날','from':0,'to':58,'fmt':'{:.0f}번','on':1,'dur':1.0,'color':'down',
  'sub':'일주일에 한 번꼴','narration':["그 사이에 하루 5% 넘게 빠진 날만 58번이에요. | 이런 알림을 거의 일주일에 한 번씩 받은 겁니다."]})
# ── 9. 2022
S.append(VS(["2022년 한 해만 딱 떼서 보면, 더 극명해요.","나스닥100은 33% 빠졌습니다. 아프죠. 근데 버틸 만은 해요.","TQQQ는요? 79% 하락. 1억이 2,100만 원이 됐습니다."],"2022년 한 해, 같은 지수 다른 결과",
  {'title':'QQQ (나스닥100)','value':'-33%','sub':'아프지만 버틸 만한 하락','color':'neutral','on':2},{'title':'TQQQ (3배)','value':'-79%','sub':'1억 → 2,100만 원','color':'down','on':3},ch="썰 ① 반전"))
S.append(K(["근데 눈치 빠른 분들, 뭔가 이상하지 않으세요? | 33에 3배면 99%인데, 왜 79%일까요."],"-33% × 3 = -99%?",hl="-99%?",hc='down',sub="그런데 왜 -79%일까",size=130,
  extra={'mascot':{'on':1,'offset':1.0,'pos':[1700,820],'size':150,'say':'3배면 -99% 아냐?','side':'left'}}))
S.append(K(["네. 아까 그 단어, '하루' 때문입니다."],"답은 '하루'",hl="'하루'",size=150,bg="1 DAY"))
# ── 10. 원리
S.append({'type':'kinetic','chapter':'핵심 원리','stack':True,'items':[{'text':'지수 +3%면, 나는 +9%?','on':1,'size':115,'highlight':'+9%?','hl_color':'up'},{'text':'현실: 오르락내리락만 해도 녹는다','on':2,'size':96,'highlight':'녹는다','hl_color':'down'}],
  'narration':["레버리지 처음 사는 사람 머릿속은 보통 이래요. | 지수가 3% 오르면, 나는 9%.","근데 현실은 달라요. | 시장이 오르락내리락만 해도, 계좌가 녹습니다. 왜 그럴까요?"]})
S.append({'type':'card','chapter':'핵심 원리','heading':'매일 3배를 다시 맞춘다','highlight':'매일','width':1500,'size':50,'icon':'dash','gap':40,
  'bullets':[{'text':'지수: 100 → +10% → 110 → -10% → 99','sub':'한 번 오르고 한 번 내렸을 뿐인데 -1%','on':2}],
  'narration':["레버리지 ETF는요, 매일매일 3배를 다시 맞춥니다. | 그래서 이런 일이 생겨요.","지수가 100에서 10% 올라서 110. 다음 날 10% 빠지면 99. 1% 손해죠."]})
S.append({'type':'card','chapter':'핵심 원리','heading':'3배짜리는?','highlight':'3배','width':1500,'size':50,'icon':'dash','gap':40,
  'bullets':[{'text':'3배: 100 → +30% → 130 → -30% → 91','sub':'똑같이 오르내렸는데 -9%','on':1,'highlight':'91','hl_color':'down'}],
  'narration':["3배짜리는요? 100에서 30% 올라 130. 다음 날 30% 빠지면, 91. | 9% 손해입니다."]})
S.append(VS(["똑같이 한 번 오르고 한 번 내렸을 뿐인데, 손실은 9배. 이게 진짜 무서운 거예요."],"같은 등락, 다른 손실",
  {'title':'지수 (1배)','value':'-1%','color':'neutral','on':1},{'title':'3배 레버리지','value':'-9%','color':'down','on':1},ch="핵심 원리"))
S.append(K(["이걸 변동성 끌림, 영어로는 볼러틸리티 디케이라고 합니다."],"변동성 끌림",sub="Volatility Decay",size=150,bg="DECAY",ch="핵심 원리"))
S.append({'type':'card','chapter':'핵심 원리','heading':'언제 커지나','highlight':'커지나','width':1500,'size':52,
  'bullets':[{'text':'시장이 크게 흔들릴수록','on':1,'hl_color':'down'},{'text':'오래 들고 있을수록','on':1,'offset':1.2,'highlight':'오래','hl_color':'down'}],
  'stickers':[{'e':'rollercoaster','pos':[1580,560],'size':220,'on':1,'offset':0.4}],
  'narration':["시장이 크게 흔들릴수록, 그리고 오래 들고 있을수록 커져요. | 레딧에서 말하는 '녹는다', 바로 이겁니다."]})
# ── 11. 지수 올랐는데 손실
S.append({'type':'chart','chapter':'핵심 원리','chart':{'lines':[{'series':'tqqq','color':'up','label':'TQQQ'},{'series':'qqq','color':'neutral','label':'QQQ','fill':False}],
  'start':'2022-05-05','end':'2023-05-05','base':1000,'unit':'won','end_labels':True,'rect':[210,200,1420,620],
  'title':'2022.5.5 ~ 2023.5.5 · 1,000만 원 넣었다면','draw':{'on':2,'dur':2.6},'source':SRC},
  'narration':["실제 데이터에서도 이게 그대로 보입니다.","2022년 5월부터 딱 1년. | 나스닥100이 크게 오르락내리락했던 구간인데요.","1년 뒤, 나스닥100은 오히려 4% 올랐습니다."]})
S.append(VS(["근데 TQQQ는요? | 3배인 12% 수익이 아니라, 20% 손실입니다.","지수는 올랐는데, 3배짜리는 돈을 잃은 거예요. | 솔직히 이게 레버리지의 진짜 얼굴입니다."],"지수는 올랐는데…",
  {'title':'QQQ (1년)','value':'+4%','sub':'2022.5.5 → 2023.5.5','color':'up','on':1},{'title':'TQQQ (1년)','value':'-20%','sub':'3배인데 손실','color':'down','on':1,'offset':1.2},
  extra={'sfx':[{'name':'scratch','on':1,'offset':1.2}]}))
# ── 12. 닷컴
chartsim={'lines':[{'series':'sim3x_ndx','color':'up','label':'가상 TQQQ','label_dy':34},{'series':'ndx','color':'neutral','label':'나스닥100','fill':False,'label_dy':-34}],
  'start':'1997-01-02','end':'2026-10-30','base':1000,'unit':'won','log':True,'end_labels':True,'rect':[210,200,1420,620],'ymin':15,
  'title':'TQQQ가 1997년에도 있었다면? (1,000만 원, 로그 스케일)','draw':{'on':2,'dur':2.6},
  'source':'가상 TQQQ = 나스닥100 일간수익률 x3 - 연 0.95% 보수 (차입비용 미반영 → 실제보다 유리하게 계산)'}
S.append(K(["그래서 이런 상상을 한번 해 봤어요."],"만약 1997년에도\nTQQQ가 있었다면?",hl="1997년",size=110,ch="만약에"))
c1=dict(chartsim); c1['end']='2000-03-31'; c1['end_labels']=False; c1['title']='가상 TQQQ · 1997 ~ 2000.3 (1,000만 원, 로그 스케일)'
S.append({'type':'chart','chapter':'만약에','chart':c1,'narration':["TQQQ가 1997년에도 있었다면? | 나스닥100 일간 데이터로, 가상의 TQQQ를 만들어 봤습니다.","닷컴 버블 때까지는, 지수보다 훨씬 빠르게 올라갑니다. | 레딧에 인증글 올리기 딱 좋은 그래프죠."]})
c2=dict(chartsim); c2['end']='2002-12-31'; c2['end_labels']=False; c2['draw']={'on':1,'dur':1.8}; c2['title']='2000년 3월, 버블이 터지고'
c2['marks']=[{'date':'2000-03-27','label':'닷컴 고점','on':1,'dy':0,'dx':190,'color':'gold'},{'date':'2002-10-07','label':'-99.94%','sub':'1억 → 6만 원','on':1,'offset':1.8,'dy':40,'dx':-200,'color':'down','size':40}]
S.append({'type':'chart','chapter':'만약에','chart':c2,'shake':[{'on':1,'offset':1.8,'dur':0.5,'amp':16,'sfx':'boom'}],
  'narration':["근데 2000년 3월, 버블이 터지고 2년 반 뒤. | 가상 TQQQ는 고점 대비 99.94% 하락. 1억이, 6만 원이 됩니다."]})
S.append(VS(["나스닥100도 83% 빠졌어요. 그래도 2015년에, 결국 고점을 회복했습니다.","가상 TQQQ는요? 26년이 지난 지금도, 2000년 고점보다 48% 아래에 있습니다."],"2000년 고점, 다시 찾았나?",
  {'title':'나스닥100','value':'회복','sub':'2015년 고점 회복','color':'up','on':1},{'title':'가상 TQQQ','value':'-48%','sub':'26년째 미회복','color':'down','on':2},ch="만약에"))
S.append({'type':'chart','chapter':'만약에','chart':dict(chartsim,draw={'on':1,'dur':2.4},title='1997 → 2026 · 29년 전체'),
  'narration':["근데 진짜 놀라운 건, 끝 숫자예요.","1997년부터 29년을 버텼다면, | 3배짜리가 34.4배. 그냥 지수가 34.8배."]})
S.append(VS(["3배 레버리지를 29년 동안 버텼는데, | 결과는 그냥 지수보다 오히려 조금 못했습니다. 아 진짜 허무하죠."],"29년 버틴 결과",
  {'title':'가상 TQQQ (3배)','value':'34.4배','color':'up','on':1},{'title':'나스닥100 (1배)','value':'34.8배','color':'neutral','on':1,'offset':0.8},ch="만약에"))
S.append({'type':'news','tag':'만약에 속보','headline':'가상 TQQQ, 닷컴 붕괴로 -99.94%','sub':'1억 원 → 6만 원… 2026년 현재까지 2000년 고점 회복 못 해',
  'ticker':['나스닥100 -83%','가상 TQQQ -99.94%','나스닥100 2015년 고점 회복','가상 TQQQ 26년째 미회복','※ 나스닥100 x3 가상 계산'],
  'narration':["그 시절에 TQQQ가 있었다면, 아마 뉴스는 이랬을 거예요.","1억이 6만 원. 그리고 26년이 지난 지금도, 본전은 아직입니다."]})
# ── 13. 인버스
S.append({'type':'reddit','chapter':'썰 ② 인버스','posts':[
  {'flair':'YOLO','title':'곧 폭락 온다. SQQQ 풀매수하고 기다리는 중','en':'"Crash is coming. All in SQQQ."','up':'6.2k','comments':'1,644','on':2},
  {'flair':'Loss','title':'SQQQ 2년 들고 있었는데 -90%… 하락장은 언제 오냐','en':'"Held SQQQ for 2 years. Down 90%. Where is the crash?"','up':'19.8k','comments':'4,107','on':3}],
  'stickers':[{'e':'bear','pos':[1500,420],'size':190,'on':2,'offset':0.5}],
  'narration':["자, 이번엔 반대편. 인버스 썰입니다.","곧 폭락 온다면서, SQQQ에 풀매수하는 글.","그리고 몇 달 뒤… 아니, 몇 년 뒤에 올라오는 후기."]})
S.append(K(["하락장 대비하는 거니까, 인버스는 오히려 안전한 거 아니냐고요?"],"인버스는 안전하다?",hl="안전하다?",size=140,ch="썰 ② 인버스"))
S.append({'type':'chart','chapter':'썰 ② 인버스','chart':{'series':'sqqq','start':'2010-02-11','end':'2026-10-30','color':[74,144,255],'base':10000,'unit':'won','log':True,'live_value':True,
  'rect':[260,200,1500,620],'title':'2010년 2월 SQQQ에 1억 원 넣었다면 (로그 스케일)','draw':{'on':2,'dur':3.0},'source':'자료: Yahoo Finance 수정주가 (액면병합 반영)'},
  'narration':["결론부터 보시죠.","SQQQ가 상장한 2010년 2월에, 1억을 넣었다면,","숫자가 계속 줄어요. 천만 원, 백만 원, 만 원…"]})
S.append({'type':'bignum','chapter':'썰 ② 인버스','label':'SQQQ 1억 원, 16년 뒤','from':100000000,'to':452,'fmt':'{:,.0f}원','final':'약 450원','on':1,'dur':1.4,'color':'down','log_count':True,
  'sub':'-99.9995% · 주가가 너무 낮아져 액면병합까지','sub_on':2,'sfx_end':'fail','narration':["2026년 10월 지금, 약 450원입니다.","오타 아니에요. 1억이, 450원. | 99.9995% 손실입니다.","주가가 너무 낮아져서, 주식을 합치는 액면병합까지 여러 번 했을 정도예요."]})
S.append(K(["한 번 더 말씀드릴게요. 1억이, 450원입니다.","편의점 삼각김밥 하나도 못 사요."],"1억 → 450원",hl="450원",hc='down',sub="SQQQ · 2010.2 → 2026.10",size=150,bg="450",bgc='down'))
S.append(K(["물론요. 인버스로 큰돈 버는 순간도 있습니다."],"인버스가 대박 날 때도 있다",hl="대박",hc='up',size=110,ch="썰 ② 인버스"))
S.append(VS(["2020년 코로나 폭락 때, SQQQ는 한 달도 안 돼서 92% 올랐어요.","근데 바로 그 고점부터 연말까지 9개월 동안은? 90%가 빠졌습니다."],"2020년 SQQQ",
  {'title':'코로나 폭락 한 달','value':'+92%','sub':'2020.2.19 → 3.16','color':'up','on':1},{'title':'그 뒤 9개월','value':'-90%','sub':'2020.3.16 → 12.31','color':'down','on':2},ch="썰 ② 인버스"))
S.append(VS(["2022년 하락장 때도 82% 올랐죠. | 근데 그 뒤로는 다시 96% 하락했습니다."],"2022년 SQQQ",
  {'title':'2022년 하락장','value':'+82%','sub':'2022년 한 해','color':'up','on':1},{'title':'그 뒤','value':'-96%','sub':'2022.12.28 → 2026.10','color':'down','on':1,'offset':1.5},ch="썰 ② 인버스"))
S.append(K(["그러니까 인버스로 돈 벌려면, | 하락의 시작이랑 끝, 둘 다 맞혀야 한다는 얘기예요."],"시작과 끝,\n둘 다 맞혀야 한다",hl="둘 다",size=120))
# ── 14. 3가지 이유
S.append(K(["인버스가 길게 들수록 불리한 이유, 세 가지만 짚을게요."],"인버스가 길게 들수록\n지는 이유 3가지",hl="3가지",size=110,ch="핵심 원리"))
for n,(t,sub_,line) in enumerate([("시장은 길게 보면 대체로 올랐다","인버스는 큰 흐름과 반대로 베팅","첫째. 미국 시장은 길게 보면 대체로 올랐어요. | 인버스는 그 큰 흐름에 정반대로 베팅하는 거고요."),
                                  ("변동성 끌림은 인버스에도 똑같이","흔들릴수록 녹는다","둘째. 아까 본 변동성 끌림, 인버스에도 똑같이 적용됩니다."),
                                  ("하락장은 짧고, 상승장은 길었다","기다리는 시간 자체가 비용","셋째. 하락장은 짧고, 상승장은 길었어요. | 폭락 기다리는 시간 자체가 손실이 됩니다.")],1):
    S.append({'type':'card','chapter':'핵심 원리','heading':f'이유 {n}','highlight':f'{n}','width':1500,'size':58,'numbered':False,
      'bullets':[{'text':t,'sub':sub_,'on':1}],'narration':[line]})
# ── 15. 2025
S.append({'type':'chart','chapter':'최근 사례','chart':{'series':'tqqq','start':'2024-10-01','end':'2025-10-31','color':[240,84,84],'ymin':8,'title':'TQQQ · 2024.10 ~ 2025.10 (달러)','draw':{'on':1,'dur':2.2},
  'marks':[{'date':'2024-12-16','label':'고점','on':2,'dy':-50,'color':'up'},{'date':'2025-04-08','label':'-58%','on':2,'dy':30,'dx':-130,'color':'down','size':36}],'source':SRC},
  'narration':["최근에도 이런 장면, 있었죠.","2025년 봄. 관세 충격으로 TQQQ가 고점 대비 58%까지 빠졌는데요."]})
S.append({'type':'bignum','chapter':'최근 사례','label':'2025.4.9 관세 유예 발표, TQQQ 하루','from':0,'to':35.2,'fmt':'+{:.1f}%','final':'+35%','on':1,'dur':1.0,'color':'up',
  'sub':'투자일까, 롤러코스터일까','sub_on':2,'narration':["그러다 4월 9일, 관세 유예 발표가 나오자 | 딱 하루 만에 35%가 올랐습니다.","하루에 35%요. 솔직히 이건 투자라기보다, 롤러코스터죠."]})
S.append(K(["물론 이 하루를 맛보려면, | 그 전에 58% 하락부터 버텨야 했습니다."],"그 하루 전에, -58%",hl="-58%",hc='down',sub="먼저 버텨야 했던 하락",size=130))
# ── 16. 생존자
S.append(VS(["그리고 하나 더요. 레딧에 올라오는 건, 대부분 대박 인증이에요.","반대로 -80% 맞고 조용히 떠난 사람들은, 글을 잘 안 씁니다. | 우리가 보는 건 살아남은 사람 얘기일 뿐이죠."],"레딧에서 보이는 것과 안 보이는 것",
  {'title':'보이는 글','value':'30배 인증','sub':'살아남은 소수의 후기','color':'up','on':1},{'title':'안 보이는 글','value':'조용히 퇴장','sub':'-80% 맞고 떠난 다수','color':'down','on':2}))
# ── 17. 정리
S.append(K(["자, 오늘 팩트체크 정리해 볼게요."],"오늘의 팩트체크",size=140,ch="정리",bg="CHECK"))
for txt,st,c,line in [("TQQQ 16년 302배","사실","up","TQQQ 16년 302배. 사실입니다. 다만, 결과만 봤을 때 얘기죠."),
                      ("2년 만에 30배","과장 (최고 약 10배)","gold","2년 만에 30배. 이건 과장이에요. 최고 기록은 약 10배였고, | 그 직후 82%가 빠졌습니다."),
                      ("레버리지는 오래 들면 녹는다","사실","up","레버리지는 오래 들면 녹는다. 사실입니다. | 지수가 올라도 손실이 날 수 있어요."),
                      ("인버스로 하락장 대비","길게 들면 위험","down","그리고 인버스로 하락장 대비한다? | 길게 들고 있으면, 1억이 450원이 될 수도 있습니다.")]:
    S.append(K([line],txt,size=110,ch="정리",stamp={'text':st,'color':c,'on':1,'offset':0.6,'pos':[960,700],'rot':-5,'size':80}))
S.append(K(["레딧의 대박 후기는, 살아남은 사람 얘기라는 거. 이거 하나만 꼭 기억해 주세요."],"대박 후기 = 살아남은 사람의 이야기",hl="살아남은 사람",size=96,ch="정리"))
S.append({'type':'outro','heading':'3배의 수익엔\n3배 이상의 대가가 있다','highlight':'3배 이상의 대가','sub':'다음 레딧 썰 팩트체크도 기대해 주세요',
  'disclaimer':'본 영상은 투자 교육 목적이며, 특정 종목·ETF의 매수·매도 추천이 아닙니다.\n레버리지·인버스 ETF는 원금 대부분을 잃을 수 있는 고위험 상품입니다. 투자 판단과 책임은 본인에게 있습니다.',
  'subscribe_on':4,'mascot':{'on':4,'pos':[1680,300],'size':150,'say':'구독 눌러주면 존버 가능','side':'left'},
  'narration':["3배의 수익 뒤에는요, 3배 이상의 대가가 숨어 있습니다.","다음 영상에서도 레딧에서 핫한 썰 하나 골라서, | 데이터로 끝까지 까 보겠습니다.",
               "여러분은 레버리지, 어떻게 생각하세요? | 궁금한 썰 있으면 댓글로 남겨 주세요.","구독이랑 좋아요는요, 제 계좌 대신 채널이라도 우상향하게 도와주시는 겁니다."]})

body=yaml.safe_dump({'scenes':S}, allow_unicode=True, sort_keys=False, width=200, default_flow_style=None)
body=body.replace("'on':","on:")
open(P,'w').write(head+"# 슬라이드 구성: 1~3문장마다 화면이 바뀌도록 쪼갬. 'kinetic' = 가운데 큰 글씨로 빠르게 넘기는 슬라이드\n"+body)
print(len(S), 'slides; kinetic', sum(1 for x in S if x['type']=='kinetic'))
