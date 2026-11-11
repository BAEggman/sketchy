# new-uk-08 v5: v4에서 농부가 셋째 · 넷째 식탁 사이로 가 버려, v3 바탕으로 그 자리를 되살리고 v4 농부(가장 큰 덩이)를 오려 0.78배로 줄여 넷째 식탁 가운데 앞으로 옮김
import numpy as np, cv2
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-08/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
v3=np.asarray(Image.open(SP+'new-uk-08/v3.png').convert('RGB')).astype(float)
v4=np.asarray(Image.open(SP+'new-uk-08/v4.png').convert('RGB')).astype(float)
f=2048/1441
x0,y0,x1,y1=[int(v*f) for v in (745,500,920,804)]
y1=min(y1,v4.shape[0])
d=np.abs(v4-v3).sum(2)
m=np.zeros(d.shape,np.uint8); m[y0:y1,x0:x1]=(d[y0:y1,x0:x1]>45).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
# 구멍 메우기
ff=m.copy(); h,w=m.shape; mask=np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff,mask,(0,0),255); m=m|cv2.bitwise_not(ff)
n,lab,st,_=cv2.connectedComponentsWithStats(m); keep=np.zeros_like(m)
big=1+int(np.argmax(st[1:,cv2.CC_STAT_AREA])); keep[lab==big]=255   # 가장 큰 덩이(농부)만
m=cv2.dilate(keep,np.ones((5,5),np.uint8))
dd=cv2.GaussianBlur(d,(0,0),1.2); sm=np.clip((dd-18)/30,0,1)            # 배경이 같은 곳(옮기면 남의 식탁 조각이 되는 곳)은 빼기
ys,xs=np.where(m>0); top,bot=ys.min(),ys.max(); belt=int(top+0.55*(bot-top))
blue=(v4[...,2]>v4[...,0]+25)&(v4[...,2]>v4[...,1]); blue[belt:,:]=False      # 윗몸(셔츠 · 얼굴 · 모자)에 낀 파란 조각 = 셋째 식탁 고드름 · 파도 케이크 조각
blue=cv2.dilate(blue.astype(np.uint8),np.ones((5,5),np.uint8))>0
sm=sm*(~blue)
al=cv2.GaussianBlur((m.astype(float)/255)*sm,(0,0),1.0)[...,None]
# 1) 농부 지우기: 그 자리 v3로
out=v4.copy()
fe=np.zeros(d.shape); fe[y0:y1,x0:x1]=1; fe=cv2.GaussianBlur(fe,(0,0),4)[...,None]
out=out*(1-fe)+v3*fe
# 2) 오린 농부를 오른쪽으로 옮겨 붙이기
ys,xs=np.where(m>0); fx=(xs.min()+xs.max())/2; fy=ys.max()     # 발밑 가운데를 기준점으로
sc=0.78; tx=985*f; ty=min(fy,h-6)                                # 넷째 식탁 가운데 앞, 0.78배로 줄여 모자가 케이크 아래로
M=np.float32([[sc,0,tx-sc*fx],[0,sc,ty-sc*fy]]); dx=round(tx-fx)
fs=cv2.warpAffine(v4,M,(w,h)); als=cv2.warpAffine(al[...,0],M,(w,h))[...,None]
out=out*(1-als)+fs*als
print('mask px',int((m>0).sum()),'dx',dx)
o=Image.fromarray(out.clip(0,255).astype(np.uint8)); o.save(D+'base_v5.webp',quality=80); o.save(SP+'new-uk-08/v5.png')
o.crop((int(600*f),int(300*f),int(1441*f),int(804*f))).resize((840,504)).save(SP+'uk08_v5_crop.png')
