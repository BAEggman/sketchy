# v2 → v3: 기름 편집에서 사라진 정강이의 파란 멍을 v1에서 되살리고(두 판은 자리가 맞음), v2 무릎의 낙서 같은 갈색 자국은 살색으로 덮는다.
# (가장자리는 가우스 2px로 흐려 붙임) 덮는 곳은 v1에서 「살 또는 멍」이었던 화소 안으로만 한정(바닥 · 손 · 테두리는 건드리지 않음). 멍 위엔 주황 기름빛 25%.
from PIL import Image; import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-20/'
v1=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int)
v2=np.asarray(Image.open(SP+'v2.png').convert('RGB')).astype(int).copy()
y0,y1,x0,x1=755,815,1750,1830
a1=v1[y0:y1,x0:x1]; a2=v2[y0:y1,x0:x1]
r1,g1,b1=a1[...,0],a1[...,1],a1[...,2]
blue=(b1-r1)>25
skin1=(r1>200)&(g1>140)&(b1<170)&((r1-b1)>60)
leg=binary_erosion(skin1|blue,iterations=1)|blue      # v1에서 살 · 멍이던 곳(테두리 한 줄 안쪽)
lum2=a2.mean(2)
skin=np.median(a2[leg&~blue&(lum2>170)],axis=0); print('skin',skin)
scrib=leg&~blue&(lum2<skin.mean()-15)
a2[scrib]=skin
glow=np.array([255,170,60])
from scipy.ndimage import gaussian_filter
alpha=np.clip(gaussian_filter(blue.astype(float),2.0)*1.3,0,1)[...,None]   # 가장자리를 2~3px 흐리게
bruise=a1*0.75+glow*0.25
a2[:]=(a2*(1-alpha)+bruise*alpha).astype(int)
v2[y0:y1,x0:x1]=a2; print('blue',int(blue.sum()),'scrib',int(scrib.sum()))
Image.fromarray(v2.astype(np.uint8)).save(SP+'v3.png')
