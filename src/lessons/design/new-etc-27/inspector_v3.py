# v2 → v3: 맞불 · 노란 집 편집에서 사라진 왼쪽 위 집 안의 「의자 위 화재경보기 점검 소방관」을 v1에서 같은 자리로 되붙인다.
# 두 판은 자리가 맞으므로, 집 안 상자(x190-285, y118-335) 안에서 v1과 v2가 다른 화소(차이 60 넘음, 3px 넓힘)만 v1로 바꾼다.
from PIL import Image; import numpy as np
from scipy.ndimage import binary_dilation
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-27/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int)
b=np.asarray(Image.open(SP+'v2.png').convert('RGB')).astype(int).copy()
y0,y1,x0,x1=118,336,188,288
d=np.abs(a[y0:y1,x0:x1]-b[y0:y1,x0:x1]).sum(2)>60
m=binary_dilation(d,iterations=3)
b[y0:y1,x0:x1][m]=a[y0:y1,x0:x1][m]; print('px',int(m.sum()))
Image.fromarray(b.astype(np.uint8)).save(SP+'v3.png')
