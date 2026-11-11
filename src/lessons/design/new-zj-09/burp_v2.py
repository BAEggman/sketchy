# new-zj-09 v1 -> v2: 트림하는 일꾼 곁의 영어 글자 "Burp"와 그 위 작은 기호를 바탕 베이지로 덮음(그림에 글자 금지)
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-09/'
D='/home/claude/s7/work/src/lessons/design/new-zj-09/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int).copy()
x0,x1,y0,y1=999,1049,666,714
for y in range(y0,y1):   # 행마다 좌우 바탕을 선형 보간(나무통 테두리 · 그늘 결을 잇기)
    L=np.median(a[y,x0-6:x0],axis=0); R=np.median(a[y,x1:x1+4],axis=0)
    for x in range(x0,x1):
        t=(x-x0)/(x1-x0); a[y,x]=(1-t)*L+t*R
# 'p' 꼬리 남은 획(상자 오른쪽 아래)
for y in range(712,726):
    L=np.median(a[y,1024:1030],axis=0); R=np.median(a[y,1054:1058],axis=0)
    for x in range(1030,1054):
        t=(x-1030)/24; a[y,x]=(1-t)*L+t*R
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v2.webp',quality=80); im.save(SP+'v2.png')
im.crop((960,640,1100,760)).resize((280,240)).save(SP+'../g_burp2.png')
