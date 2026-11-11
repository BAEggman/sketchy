# new-gr-16 v4 -> v5:
#  ① 睛明 칸 물장수(검은 두건 옷)에 어깨 물지게 막대 + 물통 끈을 그려 膀胱 물장수로 읽히게
#  ② 첫 창 우물 가로대에 감긴 밧줄("nll"처럼 보임)을 가로대 결로 덮음
#  ③ 大椎 칸 복제 여자 머리에 남은 금발 얼룩을 짙은 갈색으로
import numpy as np, colorsys
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-16/'
D='/home/claude/s7/work/src/lessons/design/new-gr-16/'
im=Image.open(SP+'v4.png').convert('RGB'); a=np.asarray(im).astype(int).copy()
# ② 우물 가로대
for y in range(137,160):
    a[y,405:436]=np.median(a[y,385:402],axis=0)
# ③ 머리 금발 얼룩
for y in range(536,610):
    for x in range(1128,1200):
        r,g,b=a[y,x]/255; h,s,v=colorsys.rgb_to_hsv(r,g,b)
        if 0.10<h<0.18 and s>0.3 and v>0.5:
            a[y,x]=np.array(colorsys.hsv_to_rgb(0.07,0.6,v*0.45))*255
im=Image.fromarray(a.astype('uint8')); d=ImageDraw.Draw(im)
# ① 물지게
y0=597; xl,xr=1563,1670
d.line((xl,y0,xr,y0),fill=(25,18,12),width=11); d.line((xl+2,y0,xr-2,y0),fill=(160,110,60),width=6)
for (x1,x2) in [(xl+5,1577),(xr-5,1659)]:
    d.line((x1,y0+4,x2,666),fill=(40,30,20),width=3)
im.save(D+'base_v5.webp',quality=80); im.save(SP+'v5.png')
im.crop((1540,520,1660,700)).resize((240,360)).save(SP+'../g16_nun2.png')
im.crop((348,116,436,188)).resize((352,288)).save(SP+'../g16_well2.png')
