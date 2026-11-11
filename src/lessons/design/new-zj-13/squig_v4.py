# new-zj-13 v3 -> v4: 쓰러진 임금 곁 튀는 하트 아래의 떨림 선(글자 'ㄴ'·'ℓ'처럼 보임)을 행마다 잔디 바탕 보간으로 지움
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-13/'
D='/home/claude/s7/work/src/lessons/design/new-zj-13/'
a=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(int).copy()
x0,x1,y0,y1=80,134,852,950
for y in range(y0,y1):
    L=np.median(a[y,x0-6:x0],axis=0); R=np.median(a[y,x1:x1+5],axis=0)
    for x in range(x0,x1):
        t=(x-x0)/(x1-x0); a[y,x]=(1-t)*L+t*R
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((30,740,200,980)).resize((340,480)).save(SP+'y_heart4.png')
