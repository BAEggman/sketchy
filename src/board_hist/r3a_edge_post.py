"""r3a(말판 ③줄 宋) 오른쪽 위 검은 세로 띠 메우기 — 2026-10-25 허브 패널(s03u01)로 올리며 발견.
오른쪽 끝 18열 × 위 ~512줄이 검정(타일 캡처 때 오버레이 밖이 찍힘). 검은 화소만 골라, 그 줄의 왼쪽 첫 정상 열 색을
작은 잡음과 함께 채운다(강·하늘·비둘기장 테두리 모두 세로로 이어지는 배경이라 가로 복제로 충분).
usage: python3 r3a_edge_post.py   (r3a_master.webp → 고쳐 저장(q95) → r3a.webp(q84) 다시 씀)"""
from PIL import Image, ImageFilter; import numpy as np
a=np.asarray(Image.open('r3a_master.webp').convert('RGB')).astype(float)
H,W,_=a.shape; L=a.mean(2); rng=np.random.default_rng(3)
blk=np.zeros((H,W),bool); blk[:,W-24:]=L[:,W-24:]<60
blk[505:548,W-18:]=True   # 검은 띠 끝의 어두운 그러데이션(지붕 위)
n=0
for y in np.where(blk.any(1))[0]:
    xs=np.where(blk[y])[0]; x0=xs.min()-1
    ref=a[y,max(0,x0-3):x0+1].mean(0)
    a[y,xs]=ref+rng.normal(0,1.5,(len(xs),3)); n+=len(xs)
out=Image.fromarray(np.clip(a,0,255).astype('uint8'))
out.save('r3a_master.webp',quality=95,method=6)
out.filter(ImageFilter.UnsharpMask(radius=1.2,percent=40,threshold=2)).save('r3a.webp',quality=84,method=6)
print('filled',n,'px')
