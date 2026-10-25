"""s20u01 藏象 오장 — 판독(blind63) 뒤 손질 (2026-10-25).
임금(心)의 배 위 손 손톱 끝 검은 점 다섯이 「칠한 손톱 = 爪」로 읽혀 肝의 華在爪가 心 칸으로 샜다(M5·N5·z25).
손톱 점마다 반지름 2 안의 가장 어두운 픽셀을 중심으로, 반지름 ~3.7 원판을 손끝 살색(반지름 7 안, 하이라이트·붉은 옷을 뺀 중앙값)으로 덮는다(1차 — 밝은 픽셀 평균으로 덮었더니 흰 반짝이로 읽힘(O5) → 중앙값 원판으로 고침).
usage: python3 s20u01_post.py in.png out.png   (2048×1144 합성본 픽셀 좌표)"""
from PIL import Image; import numpy as np, sys
src,dst=sys.argv[1],sys.argv[2]
a=np.asarray(Image.open(src).convert('RGB')).astype(float)
G=[(765,919),(767,940),(761,956),(741,969),(734,886)]   # 임금 손가락 넷 + 엄지 손톱
yy,xx=np.mgrid[-8:9,-8:9]
for gx,gy in G:
    s=a[gy-8:gy+9,gx-8:gx+9]; lum=s.mean(2)
    near=(xx**2+yy**2)<=4
    k=np.argmin(np.where(near,lum,999)); cy,cx=np.unravel_index(k,lum.shape)
    dist=(xx-(cx-8))**2+(yy-(cy-8))**2
    sat=s.max(2)-s.min(2)
    col=np.median(s[(dist<=49)&(lum>140)&(lum<225)&(sat<90)],axis=0)   # 손끝 살색(하이라이트·붉은 옷 빼고)
    w=np.clip(4.2-np.sqrt(dist),0,1)[...,None]                            # 반지름 ~3.7 원판, 가장자리 1px 페더
    s[:]=s*(1-w)+col*w; a[gy-8:gy+9,gx-8:gx+9]=s
Image.fromarray(np.clip(a,0,255).astype('uint8')).save(dst); print('saved',dst)
