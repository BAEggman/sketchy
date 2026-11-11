# new-zj-05 v1 -> v2: 종 사이 하늘의 위쪽 초승달을 지움(초승달은 벤치 위 하나만 = 肺陰虛) — 행마다 좌우 하늘색 보간
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-05/'
D='/home/claude/s7/work/src/lessons/design/new-zj-05/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(float).copy()
x0,x1,y0,y1=1828,1912,34,132
for y in range(y0,y1):
    L=np.median(a[y,x0-10:x0],axis=0); R=np.median(a[y,x1:x1+10],axis=0)
    for x in range(x0,x1):
        t=(x-x0)/(x1-x0); a[y,x]=(1-t)*L+t*R
im=Image.fromarray(a.clip(0,255).astype('uint8')); im.save(D+'base_v2.webp',quality=80); im.save(SP+'v2.png')
im.crop((1600,0,2048,300)).save(SP+'../g_moon.png')
