# v2 → v3: 오후 햇살 편집에서 농부(脾) 패가 초승달로 바뀌어, v1의 보름달 패(원판)를 같은 자리에 되붙인다.
# 원판 중심 (1178,695) 반지름 21(테 포함), 가장자리 1.5px만 섞어 붙임.
from PIL import Image; import numpy as np
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-31/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(float)
b=np.asarray(Image.open(SP+'v2.png').convert('RGB')).astype(float).copy()
H,W=b.shape[:2]; yy,xx=np.mgrid[0:H,0:W]
cx,cy,R=1178,695,21.5
d=np.sqrt((xx-cx)**2+(yy-cy)**2)
al=np.clip((R-d)/1.5,0,1)[...,None]
b=b*(1-al)+a*al
Image.fromarray(b.astype(np.uint8)).save(SP+'v3.png'); print('ok')
