# new-gr-11 v3 -> v4: 가운데 왼쪽 칸 모니터 테두리 아래의 "PM" 같은 버튼 무늬를 테두리 회색으로 지움
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-11/'
D='/home/claude/s7/work/src/lessons/design/new-gr-11/'
a=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(int).copy()
x0,y0,x1,y1=612,504,639,517
src=np.median(a[y0-2:y1+4,602:609],axis=1)   # 버튼 왼쪽 깨끗한 테두리 세로줄(밑선 포함)의 행별 중앙값
for x in range(x0,x1): a[y0-2:y1+4,x]=src
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((560,460,680,540)).resize((480,320)).save(SP+'../g11_pm2.png')
