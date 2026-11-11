# new-gr-18 v3 -> v4: 셋째 칸 왼쪽 부푸는 풍선 둘레의 흰 연기 뭉치 셋(터지는 연기와 같은 꼴)을 둘레 바탕색으로 덮음
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-18/'
D='/home/claude/s7/work/src/lessons/design/new-gr-18/'
a=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(int).copy()
for (x0,y0,x1,y1) in [(1565,245,1608,285),(1615,260,1652,297),(1483,340,1518,372)]:
    ring=np.concatenate([a[y0-6:y0,x0:x1].reshape(-1,3),a[y1:y1+6,x0:x1].reshape(-1,3),a[y0:y1,x0-6:x0].reshape(-1,3),a[y0:y1,x1:x1+6].reshape(-1,3)])
    s=ring.sum(1); ring=ring[(s>250)&(s<720)]
    a[y0:y1,x0:x1]=np.median(ring,axis=0)
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((1460,220,1700,460)).save(SP+'../g18_p3b.png')
