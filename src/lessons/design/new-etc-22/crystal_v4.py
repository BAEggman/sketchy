# v3 → v4: 참외로 바꾸는 편집에서 사라진 파란 결정(膽礬)을 v2에서 같은 자리로 옮겨 붙인다.
# v2의 결정 영역(캡처 좌표 약 1326-1396, 696-778)에서 파랑 계열 + 그 검은 테두리만 가려 내어 v3 바닥 위에 얹는다.
from PIL import Image; import numpy as np
from scipy.ndimage import binary_dilation, binary_fill_holes, label
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-22/'
k=2048/1410
v2=np.asarray(Image.open(SP+'v2.png').convert('RGB')).astype(int)
v3=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(int).copy()
y0,y1,x0,x1=int(692*k),int(782*k),int(1322*k),int(1402*k)
a=v2[y0:y1,x0:x1]; r,g,b=a[...,0],a[...,1],a[...,2]
blue=(b-r)>40
blue=binary_fill_holes(binary_dilation(blue,iterations=3))     # 결정 몸통 + 테두리 선 + 안쪽 흰 반사
lab,n=label(blue); sizes=[(lab==i).sum() for i in range(1,n+1)]; keep=lab==(1+int(np.argmax(sizes)))
v3[y0:y1,x0:x1][keep]=a[keep]
print('px',int(keep.sum()))
Image.fromarray(v3.astype(np.uint8)).save(SP+'v4.png')
