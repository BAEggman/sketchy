# v4 → v5: 둘째 책상 편집이 첫 책상(여름) 손님 앞에 새로 그린 엎어진 아이스크림 접시를 v3 모습으로 되돌린다.
# 두 판은 자리가 맞으므로 상자(x278-372, y745-842) 안에서 v3와 다른 화소(차이 60 넘음, 3px 넓힘)만 v3로 바꾼다.
from PIL import Image; import numpy as np
from scipy.ndimage import binary_dilation
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-28/'
a=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(int)
b=np.asarray(Image.open(SP+'v4.png').convert('RGB')).astype(int).copy()
y0,y1,x0,x1=745,843,278,373
d=np.abs(a[y0:y1,x0:x1]-b[y0:y1,x0:x1]).sum(2)>60
m=binary_dilation(d,iterations=3)
b[y0:y1,x0:x1][m]=a[y0:y1,x0:x1][m]; print('px',int(m.sum()))
Image.fromarray(b.astype(np.uint8)).save(SP+'v5.png')
