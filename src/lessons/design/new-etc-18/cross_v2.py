# v1 → v2: 간호사 모자의 빨간 십자(적십자 표장 · 기호)를 모자 흰색으로 덮는다.
# 모자 위 테두리(y≈682-685)는 남기고, 그 아래 십자 상자 안에서 붉은 화소 · 십자 검은 테 · 분홍 번짐만 바꾼다.
from PIL import Image; import numpy as np
from scipy.ndimage import binary_dilation
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-18/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int).copy()
y0,y1,x0,x1=687,710,369,398
reg=a[y0:y1,x0:x1]; r,g,b=reg[...,0],reg[...,1],reg[...,2]; lum=reg.mean(2)
white=np.array([228,244,246])
m=((r-g)>12)|(lum<200)
m=binary_dilation(m,iterations=1)
reg[m]=white; a[y0:y1,x0:x1]=reg; print('px',int(m.sum()))
# 십자 위 끝의 검은 테 조각(모자 테두리 바로 아래 y 685-687)
sub=a[685:688,376:393]; sm=sub.mean(2)<200; sub[sm]=white; a[685:688,376:393]=sub; print('top px',int(sm.sum()))
Image.fromarray(a.astype(np.uint8)).save(SP+'v2.png')
