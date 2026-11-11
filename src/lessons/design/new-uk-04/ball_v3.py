# new-uk-04 v2 -> v3: 달 통 위 높이 떠 있는 큰 주황 공과 그 튀는 궤적 선(陽脈 공이 달 통으로 가는 것처럼 읽힘)을 벽 바탕으로 지움. 닻 · 브레이크 패드는 그대로
import numpy as np, cv2
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-uk-04/'
D='/home/claude/s7/work/src/lessons/design/new-uk-04/'
a=np.asarray(Image.open(SP+'v2.png').convert('RGB')).copy()
ox,oy=795,255                                       # 2048 좌표계에서 살핀 칸의 왼쪽 위
wall=np.median(a[oy+160:oy+200,ox+180:ox+220].reshape(-1,3).astype(int),axis=0)
sub=a[oy:oy+384,ox:ox+398].astype(int)
diff=np.abs(sub-wall).sum(axis=2)>45
m=np.zeros(diff.shape,bool); m[5:300,60:345]=True
m[215:,15:165]=False                                 # 닻
m[100:210,0:85]=False                                # 브레이크 패드
m[270:,250:]=False                                   # 컨베이어 끝 물보라
mask=np.zeros(a.shape[:2],np.uint8); mask[oy:oy+384,ox:ox+398][diff&m]=255
mask=cv2.dilate(mask,np.ones((5,5),np.uint8),iterations=1)
out=cv2.inpaint(a,mask,5,cv2.INPAINT_TELEA)
im=Image.fromarray(out); im.save(D+'base_v3.webp',quality=80); im.save(SP+'v3.png')
im.crop((ox,oy,ox+398,oy+384)).save(SP+'y_grid3.png'); print(wall, int((diff&m).sum()))
