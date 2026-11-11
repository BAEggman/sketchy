# new-zj-26 v2 -> v3: 장승 머리 부분의 빛나는 혹 넷 중 코끝의 하나를 지워, 머리 · 몸 · 다리에 셋씩(三部九候 아홉)이 되게 함
import numpy as np, cv2
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-26/'
D='/home/claude/s7/work/src/lessons/design/new-zj-26/'
a=np.asarray(Image.open(SP+'v2.png').convert('RGB')).copy()
sub=a[290:340,150:205].astype(int)
glow=((sub[:,:,0]>200)&(sub[:,:,1]>170)&(sub[:,:,2]<140))            # 노란 빛 픽셀
ys,xs=np.nonzero(glow); cy,cx=290+int(ys.mean()),150+int(xs.mean())
mask=np.zeros(a.shape[:2],np.uint8); cv2.circle(mask,(cx,cy),17,255,-1)                  # 혹과 둘레 노란 번짐까지 둥글게
print('center',cx,cy)
out=cv2.inpaint(a,mask,6,cv2.INPAINT_TELEA)
im=Image.fromarray(out); im.save(D+'base_v3.webp',quality=80); im.save(SP+'v3.png')
im.crop((60,140,240,500)).resize((360,720)).save(SP+'y_pole3.png'); print(int(glow.sum()))
