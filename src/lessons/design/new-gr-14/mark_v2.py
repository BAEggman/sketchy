# new-gr-14 v1 -> v2: 오른쪽 아래 구석 풀밭의 서명 같은 'L' 표시를 풀색 중앙값으로 덮음
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-14/'
D='/home/claude/s7/work/src/lessons/design/new-gr-14/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int).copy()
x0,y0,x1,y1=2010,1063,2030,1089
ring=np.concatenate([a[y0:y1,x1:x1+10].reshape(-1,3),a[y0-8:y0,x0:x1].reshape(-1,3),a[y1:y1+8,x0:x1].reshape(-1,3)])
a[y0:y1,x0:x1]=np.median(ring,axis=0)
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v2.webp',quality=80); im.save(SP+'v2.png'); print(np.median(ring,axis=0))
