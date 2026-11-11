# new-zj-28 v2 -> v3: 뒷방 어항 물고기(魚翔) 몸통의 「$」처럼 보이는 S자 무늬를 지움 — 무늬 획만 마스크로 잡아 둘레 몸 색으로 inpaint(아가미 선은 그대로)
import numpy as np, cv2
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-28/'
D='/home/claude/s7/work/src/lessons/design/new-zj-28/'
a=np.asarray(Image.open(SP+'v2.png').convert('RGB')).copy()
x0,x1,y0,y1=1728,1746,297,326
sub=a[y0:y1,x0:x1].astype(int)
ref=np.median(a[300:320,1748:1760].reshape(-1,3).astype(int),axis=0)
dark=sub.sum(axis=2)<ref.sum()-30
mask=np.zeros(a.shape[:2],np.uint8); mask[y0:y1,x0:x1][dark]=255
mask=cv2.dilate(mask,np.ones((3,3),np.uint8),iterations=1)
out=cv2.inpaint(a,mask,4,cv2.INPAINT_TELEA)
im=Image.fromarray(out); im.save(D+'base_v3.webp',quality=80); im.save(SP+'v3.png')
im.crop((1660,240,1810,380)).resize((450,420)).save(SP+'y_fish3.png'); print(ref, int(dark.sum()))
