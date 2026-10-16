"""r5c 후처리 (2026-10-16) — 濟生醫院 우물: 가로대에서 내려온 밧줄이 건져지는 사람의 허리를 감게(濟 = 물에 드리운 밧줄)"""
import sys
from PIL import Image, ImageDraw
im=Image.open(sys.argv[1]).convert('RGB')
x0,y0,x1,y1=60,1220,300,1480; S=4
reg=im.crop((x0,y0,x1,y1)).resize(((x1-x0)*S,(y1-y0)*S),Image.LANCZOS); d=ImageDraw.Draw(reg)
P=lambda x,y:(x/2*S,y/2*S)   # well.png(2배 확대본) 좌표 → 영역 좌표
pts=[P(236,226),P(240,262),P(236,300),P(226,340),P(214,372)]
d.line(pts,fill=(70,50,30),width=int(4.6*S),joint='curve'); d.line(pts,fill=(196,160,105),width=int(3.0*S),joint='curve')
# 허리를 감은 고리
for dy in (0,7):
    a,b=P(150,372+dy),P(258,392+dy)
    d.arc([a[0],a[1],b[0],b[1]],10,170,fill=(70,50,30),width=int(4.4*S)); d.arc([a[0],a[1],b[0],b[1]],10,170,fill=(196,160,105),width=int(2.8*S))
im.paste(reg.resize((x1-x0,y1-y0),Image.LANCZOS),(x0,y0)); im.save(sys.argv[2])
im.crop((x0,y0,x1,y1)).resize((480,520)).save('well2.png')
