# new-uk-09 v3: 돌림판 색 차례를 시계방향 초록→빨강→노랑→흰→파랑(木火土金水 相生)으로 — 파랑 칸과 흰 칸 색을 맞바꿈
import numpy as np
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-09/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-uk-09/v2.png').convert('RGB')).astype(float)
h,w=a.shape[:2]; yy,xx=np.mgrid[0:h,0:w]
cx,cy,rx,ry=351,636,108,152
ell=((xx-cx)/rx)**2+((yy-cy)/ry)**2<1
ell&=yy>505                                     # 위쪽 파란 바늘은 빼기
B=np.array([42,119,211.]); W=np.array([255,255,255.])
db=np.linalg.norm(a-B,axis=2); dw=np.linalg.norm(a-W,axis=2)
tb=np.clip(1-db/90,0,1)*ell; tw=np.clip(1-dw/60,0,1)*ell
out=a+tb[...,None]*(W-B)+tw[...,None]*(B-W)
o=Image.fromarray(out.clip(0,255).astype(np.uint8)); o.save(D+'base_v3.webp',quality=80); o.save(SP+'new-uk-09/v3.png')
o.crop((220,440,480,820)).save(SP+'uk09_wheel_v3.png')
