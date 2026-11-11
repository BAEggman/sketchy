# new-uk-07 v5: 장군 입가 침 줄기가 청록(민트)이라 콧물 · 토사물처럼 보여, 맑은 흰빛으로 바꿈
import numpy as np
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-07/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-uk-07/v4.png').convert('RGB')).astype(int)
y0,y1,x0,x1=812,852,758,800
s=a[y0:y1,x0:x1]
m=(s[:,:,1]>s[:,:,0]+8)&(s.sum(2)>420)
v=s.mean(2)
new=np.stack([v+12,v+18,v+28],2)
s[m]=np.clip(new[m],0,255)
a[y0:y1,x0:x1]=s
print('pixels',m.sum())
out=Image.fromarray(a.astype(np.uint8)); out.save(D+'base_v5.webp',quality=80); out.save(SP+'new-uk-07/v5.png')
out.crop((740,800,820,890)).resize((320,360),Image.NEAREST).save(SP+'uk07_drool_v5.png')
