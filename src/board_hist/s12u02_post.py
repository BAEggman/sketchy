# s12u02 惡色 살갗 색 맞춤 (2026-10-17) — 쌍둥이 善·惡의 노랑을 같은 밝기로(惡이 더 어두워 陽黃/陰黃으로 읽히던 것)
# 사용: python3 s12u02_post.py comp_v3.png out.png   (comp_v3 = zone_kit compose 결과)
import sys, numpy as np
from PIL import Image
from scipy import ndimage
im=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)/255
H,W,_=im.shape
mx=im.max(2); mn=im.min(2); d=mx-mn+1e-6; r,g,b=im[...,0],im[...,1],im[...,2]
h=np.where(mx==r,(g-b)/d%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60; s=d/(mx+1e-6); v=mx
ys,xs=np.mgrid[0:H,0:W]; skin=(h>20)&(h<62)&(s>0.25)&(v>0.30)
gface=skin&(xs>1620)&(xs<1785)&(ys>280)&(ys<480); bface=skin&(xs>1795)&(xs<1965)&(ys>280)&(ys<480)
bad=skin&(xs>1795)&(xs<1965)&(ys>280)
gm=im[gface].mean(0); bm=im[bface].mean(0)
m=ndimage.binary_closing(bad,iterations=2)&skin; w=ndimage.gaussian_filter(m.astype(float),1.0)[...,None]
new=np.clip(im*(gm/bm)*0.74+np.array([0.72,0.70,0.66])*0.26,0,1)
out=im*(1-w)+new*w; out[:,-1]=out[:,-3]; out[:,-2]=out[:,-3]
Image.fromarray((out*255).astype('uint8')).save(sys.argv[2]); print('saved',sys.argv[2])
