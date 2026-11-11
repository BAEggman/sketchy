# new-zj-02 v1 -> v2: 물레방아 곁 회색 기계 옆면의 "IIII"·고리 무늬 판(글자 '皿'처럼 보임)을 옆면 회색으로 덮음
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-02/'
D='/home/claude/s7/work/src/lessons/design/new-zj-02/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int).copy()
x0,y0,x1,y1=584,966,626,1013
ref=np.concatenate([a[y0:y1,575:583].reshape(-1,3),a[y0:y1,628:634].reshape(-1,3),a[1015:1022,x0:x1].reshape(-1,3)])
ref=ref[ref.sum(1)>450]; g=np.median(ref,axis=0); print(g)
a[y0:y1,x0:x1]=g
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v2.webp',quality=80); im.save(SP+'v2.png')
im.crop((540,920,680,1060)).resize((280,280)).save(SP+'../g_label2.png')
