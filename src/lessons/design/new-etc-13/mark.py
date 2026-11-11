# v_in → v_out (기본 v1 → v2, Gemini v3 → v4에도 그대로 씀): 아래 미끄럼틀 옆면의 글자처럼 보이는 작은 낙서(약 891-915, 985-999)를 옆면 색으로 메움.
# 옆면 안쪽 패널 선(y≈987-0.45(x-883))과 바깥 모서리(y≈1015-0.44(x-877)) 사이 띠에서만, 어두운 화소만 바꾼다.
from PIL import Image, ImageFilter; import numpy as np
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-13/'
import sys; vin,vout=(sys.argv[1:3]+['1','2'])[:2] if len(sys.argv)>2 else ('1','2')
im=Image.open(SP+f'v{vin}.png').convert('RGB'); a=np.asarray(im).astype(int).copy()
H,W=a.shape[:2]; yy,xx=np.mgrid[0:H,0:W]
inner=987-0.45*(xx-883); outer=1015-0.44*(xx-877)
band=(xx>=884)&(xx<=922)&(yy>inner+4)&(yy<outer-4)
lum=a.mean(2)
face=np.median(a[band&(lum>150)],axis=0); print('face',face)
dark=band&(lum<face.mean()-18)
# 낙서 둘레 1px까지 넓혀 번짐 자국도 덮기
from scipy.ndimage import binary_dilation
m=binary_dilation(dark,iterations=2)&band
a[m]=face; print('px',m.sum())
Image.fromarray(a.astype(np.uint8)).save(SP+f'v{vout}.png')
