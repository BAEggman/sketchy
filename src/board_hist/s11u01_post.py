# s11u01 宣明五氣 — 바탕(4 Argon) 위 PIL 덧그림 (2026-10-17, Gemini reCAPTCHA로 구역 편집 불가 → 대체)
# 사용: python3 s11u01_post.py wip/s11u01_base_v1.png out.png  → 이어서 zone_kit finish out.png s11u01.webp --wm 783,853,819,893 --wm 1190,878,1224,918 --wm 1580,860,1620,904
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from draw_kit import *
from PIL import Image
import numpy as np
im=Image.open(sys.argv[1]).convert('RGB')
# 1) 화로 불꽃(心惡熱 — 숯만 있으면 瘀로 읽힘, blind25)
pt=Patch(im,(735,660,830,770))
for bx,h,w,l in [(758,44,20,-0.12),(772,62,24,0.05),(787,54,22,0.12),(801,38,18,0.18)]: flame(pt,(bx,756),h,w,l)
pt.commit()
# 2) 장군 눈물(肝爲淚)
pt=Patch(im,(205,370,275,425))
taper(pt,[(224,385),(222.6,392),(223.4,399),(222.2,407)],0.6,1.25,bead=1.6)
taper(pt,[(253,385),(254.4,392),(253.8,399),(255.2,406)],0.6,1.25,bead=1.6)
pt.ellipse((221.5,415),1.1,1.4,(70,105,130,200)); pt.ellipse((221.5,415),0.7,1.0,(190,222,238,215))
pt.commit()
# 3) 농부 침(脾爲涎 — 입꼬리에서 턱 아래로 늘어진 실 + 구슬)
pt=Patch(im,(1000,590,1040,640))
taper(pt,[(1016.5,601),(1015.6,608),(1016.2,615),(1015.4,623)],0.55,0.8,bead=1.9)
pt.commit()
# 4) 문틈 솜뭉치 + 들이치는 눈송이(肺惡寒 — 문틈 성에 = 裏寒 위험 회피)
pt=Patch(im,(1515,440,1620,660))
blobs=[(1583,548,7),(1578,556,7),(1586,560,7),(1581,567,6.5),(1576,548,5.5),(1588,552,5)]
for x,y,r in blobs: pt.ellipse((x,y),r+1.1,r+1.1,(105,105,100,255))
for x,y,r in blobs: pt.ellipse((x,y),r,r,(250,250,246,255))
for x,y,r in [(1580,562,3),(1586,566,2.5)]: pt.ellipse((x,y),r,r*0.7,(222,222,216,255))
for c,r in [((1567,503),7),((1550,530),6.5),((1562,592),7),((1537,575),6),((1572,468),5.5),((1544,480),5.5),((1528,548),5)]: snowflake(pt,c,r)
pt.commit()
# 5) 캡처 마젠타 잔흔(오른쪽 2열) 덮기
a=np.asarray(im).copy(); a[:,-1]=a[:,-3]; a[:,-2]=a[:,-3]
Image.fromarray(a).save(sys.argv[2]); print('saved',sys.argv[2])
