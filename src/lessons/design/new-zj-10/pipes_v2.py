# new-zj-10 v1 -> v2: 바깥 물통 둘을 잇는 관, 오른쪽 통과 건물을 잇는 관을 지움(막힌 통 癃 ↔ 새는 통 遺尿가 따로 읽히게)
#  열마다 관 위 · 아래 모래색을 세로로 보간
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-10/'
D='/home/claude/s7/work/src/lessons/design/new-zj-10/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(float).copy()
for (x0,x1,y0,y1) in [(277,336,916,934),(447,507,935,954)]:
    for x in range(x0,x1):
        T=a[y0-3,x]; Bt=a[y1+2,x]
        for y in range(y0,y1):
            t=(y-y0)/(y1-y0); a[y,x]=(1-t)*T+t*Bt
im=Image.fromarray(a.clip(0,255).astype('uint8')); im.save(D+'base_v2.webp',quality=80); im.save(SP+'v2.png')
im.crop((260,880,520,980)).resize((520,200)).save(SP+'../g_pipes2.png')
