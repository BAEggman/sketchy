"""r1a(말판 ①줄 先秦·漢) 아래 레인의 세로 그림자 띠 지우기 — 2026-10-25 허브 패널(s01u01)로 올리며 발견.
x≈1128~1190, y≈1005~끝에 구역 편집 페더가 남긴 회색 그러데이션(오른끝에서 밝기 ×0.73). 흰 바탕(y 1020~1300)의
열별 90 백분위로 열마다 밝기 이득(252/p90)을 재고, 그 띠에만 곱한다(위 끝 15줄은 이득을 서서히 켬).
usage: python3 r1a_seam_post.py   (r1a_master.webp → 고쳐 저장(q95) → r1a.webp(q84) 다시 씀)"""
from PIL import Image, ImageFilter; import numpy as np
a=np.asarray(Image.open('r1a_master.webp').convert('RGB')).astype(float); L=a.mean(2)
x0,x1,y0,y1=1124,1192,1005,a.shape[0]
g=np.array([252/max(np.percentile(L[1020:1300,x],90),120) for x in range(x0,x1)]).clip(1,1.45)
g=np.convolve(np.pad(g,2,mode='edge'),np.ones(5)/5,mode='valid')
ramp=np.clip((np.arange(y0,y1)-y0)/15,0,1)[:,None]
G=1+(g[None,:]-1)*ramp
a[y0:y1,x0:x1]*=G[...,None]
out=Image.fromarray(np.clip(a,0,255).astype('uint8'))
out.save('r1a_master.webp',quality=95,method=6)
out.filter(ImageFilter.UnsharpMask(radius=1.2,percent=40,threshold=2)).save('r1a.webp',quality=84,method=6)
print('gain max',g.max().round(3))
