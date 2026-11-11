# new-uk-14 v2: 둘째 옷걸이 나무 어깨에 그려진 초승달(標 기호)이 고리 = 本을 헷갈리게 해 나무색으로 지움
import numpy as np, cv2
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-14/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-uk-14/v1.png').convert('RGB')).copy()
x0,y0,x1,y1=470,214,512,254
s=a[y0:y1,x0:x1].astype(int)
yel=(s[:,:,0]>170)&(s[:,:,1]>150)&(s[:,:,2]<140)
dark=s.sum(2)<330
m=np.zeros(a.shape[:2],np.uint8); m[y0:y1,x0:x1][yel|dark]=255
m=cv2.dilate(m,np.ones((3,3),np.uint8),iterations=2)
out=cv2.inpaint(a,m,4,cv2.INPAINT_TELEA)
Image.fromarray(out).save(D+'base_v2.webp',quality=80); Image.fromarray(out).save(SP+'new-uk-14/v2.png')
Image.fromarray(out[180:280,440:560]).resize((480,400),Image.NEAREST).save(SP+'uk14_h2_v2.png')
