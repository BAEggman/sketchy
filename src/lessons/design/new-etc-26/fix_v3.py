# v2 → v3: (1) 편집이 번져 시계추 금빛 원판에 생긴 인삼 그림을 v1 원판으로 되돌림 — 원 안에서 유리병(푸르스름 · 밝은 화소)은 지킴.
#          (2) ④ 손님 무릎의 피처럼 보이는 붉은 얼룩을 바지 색으로 덮음.
from PIL import Image; import numpy as np
from scipy.ndimage import binary_dilation
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-26/'
v1=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int)
v2=np.asarray(Image.open(SP+'v2.png').convert('RGB')).astype(int).copy()
H,W=v2.shape[:2]; yy,xx=np.mgrid[0:H,0:W]
cx,cy,R=1326,498,30
disk=(xx-cx)**2+(yy-cy)**2<=R*R
r,g,b=v2[...,0],v2[...,1],v2[...,2]
glass=((b-r)>8)|((r+g+b)/3>215)
glass=binary_dilation(glass&disk,iterations=1)
m=disk&~glass
v2[m]=v1[m]; print('disk px',int(m.sum()))
y0,y1,x0,x1=568,628,1028,1070          # 무릎 둘레만
reg=v2[y0:y1,x0:x1]; rr,gg,bb=reg[...,0],reg[...,1],reg[...,2]
red=(rr-gg>45)&(gg<125)                # 진한 붉은 얼룩(살색은 g≥160, 손 윤곽 검정은 r-g 작음)
red=binary_dilation(red,iterations=1)&(gg<140)&((rr-gg)>15)
pants=np.array([115,128,126])          # 얼룩 바로 아래 같은 다리 바지색(v2 1043-1049, 615)
reg[red]=pants; v2[y0:y1,x0:x1]=reg; print('red px',int(red.sum()))
Image.fromarray(v2.astype(np.uint8)).save(SP+'v3.png')
