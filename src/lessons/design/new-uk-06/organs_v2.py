# new-uk-06 v2: 뒷모습인데 장기가 앞모습 배치(간이 환자 왼쪽)로 그려져, 척추 실(x≈1690)을 축으로 장기 묶음을 좌우로 뒤집음
import numpy as np
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-06/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-uk-06/v1.png').convert('RGB')).astype(float)
ax=1690; hw=85; y0,y1=410,700
x0,x1=ax-hw,ax+hw
reg=a[y0:y1,x0:x1]; mir=reg[:,::-1]
h,w=reg.shape[:2]; f=14
def ramp(n):
    r=np.ones(n); t=np.linspace(0,1,f); r[:f]=t; r[-f:]=t[::-1]; return r
al=np.outer(ramp(h),ramp(w))[...,None]
a[y0:y1,x0:x1]=reg*(1-al)+mir*al
out=Image.fromarray(a.clip(0,255).astype(np.uint8))
out.save(D+'base_v2.webp',quality=80); out.save(SP+'new-uk-06/v2.png')
out.crop((1560,380,1840,760)).save(SP+'uk06_org_v2.png')
