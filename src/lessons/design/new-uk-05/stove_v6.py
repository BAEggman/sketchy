# new-uk-05 v6: 셋째 집 난로 창의 숫자처럼 읽히는 불꽃 무늬(「14:04」)를 매끈한 불빛으로 덮음
import numpy as np, cv2
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-05/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-uk-05/v5.png').convert('RGB')).astype(float)
x0,x1,y0,y1=1225,1281,651,693
h,w=y1-y0,x1-x0
yy,xx=np.mgrid[0:h,0:w]
t=yy/(h-1)                                   # 0 위 → 1 아래
top=np.array([226,96,28.]); bot=np.array([255,196,64.])
fill=top*(1-t[...,None])+bot*t[...,None]
# 둥근 불꽃 셋(노란 물방울꼴)을 흐리게 얹음
glow=np.zeros((h,w))
for cx,cy,rx,ry in [(12,30,8,14),(28,26,10,18),(44,30,8,14)]:
    m=np.zeros((h,w),np.uint8); cv2.ellipse(m,(cx,cy),(rx,ry),0,0,360,255,-1); glow=np.maximum(glow,m/255.)
glow=cv2.GaussianBlur(glow,(0,0),3)
yel=np.array([255,236,120.])
fill=fill*(1-0.85*glow[...,None])+yel*(0.85*glow[...,None])
# 가장자리 2px는 원래 그림과 섞어 이음매를 없앰
edge=np.ones((h,w)); edge[:2,:]=edge[-2:,:]=0.5; edge[:,:2]=edge[:,-2:]=0.5
reg=a[y0:y1,x0:x1]
a[y0:y1,x0:x1]=reg*(1-edge[...,None])+fill*edge[...,None]
out=Image.fromarray(a.clip(0,255).astype(np.uint8))
out.save(D+'base_v6.webp',quality=80); out.save(SP+'new-uk-05/v6.png')
out.crop((1150,600,1330,740)).resize((540,420),Image.LANCZOS).save(SP+'uk05_stove_v6.png')
