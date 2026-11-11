# new-zj-01 v2 -> v3: 지붕 대나무 깃대를 정확히 여섯 마디(六節)로 다시 그림 — 원래 깃대를 하늘색으로 지우고 같은 자리에 마디 여섯 대나무를 그림
import numpy as np
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-01/'
D='/home/claude/s7/work/src/lessons/design/new-zj-01/'
im=Image.open(SP+'v2.png').convert('RGB'); a=np.asarray(im).astype(int).copy()
x0,x1,y0,y1=1160,1194,14,236
sky=np.median(a[y0:y1,1130:1150].reshape(-1,3),axis=0)
body=a[60:200,1170:1184].reshape(-1,3); green=np.median(body[(body[:,1]>body[:,0])&(body.sum(1)>300)],axis=0)
print('sky',sky,'green',green)
for y in range(y0,y1):
    a[y,x0:x1]=np.median(np.concatenate([a[y,1140:1158],a[y,1196:1214]]),axis=0)
im=Image.fromarray(a.astype('uint8')); d=ImageDraw.Draw(im)
bx0,bx1,top,bot=1168,1186,20,236
dark=(30,40,20); light=tuple(int(min(255,c+35)) for c in green)
d.rectangle((bx0,top,bx1,bot),fill=tuple(int(c) for c in green),outline=dark,width=3)
d.line((bx0+5,top+6,bx0+5,bot-2),fill=light,width=3)
seg=(bot-top)/6
for k in range(1,6):
    y=int(top+seg*k)
    d.line((bx0-3,y,bx1+3,y),fill=dark,width=3)
im.save(D+'base_v3.webp',quality=80); im.save(SP+'v3.png')
im.crop((1120,0,1240,260)).resize((240,520)).save(SP+'../g_bamboo2.png')
