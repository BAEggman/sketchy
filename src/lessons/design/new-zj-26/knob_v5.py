# new-zj-26 v4 -> v5: 편집으로 장승 머리 혹이 둘이 됨 → 위 혹 하나를 둥근 마스크로 오려 미간(콧등 위)에 붙여 머리도 셋(三部九候 아홉)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-26/'
D='/home/claude/s7/work/src/lessons/design/new-zj-26/'
im=Image.open(SP+'v4.png').convert('RGB'); a=np.asarray(im).astype(int)
sub=a[170:250,150:200]; m=(sub[:,:,0]>200)&(sub[:,:,1]>170)&(sub[:,:,2]<140)
ys,xs=np.nonzero(m); print('knob px',m.sum(),ys.min()+170,ys.max()+170,xs.min()+150,xs.max()+150)
# 위 혹 중심 찾기(위쪽 덩이)
top=ys<ys.min()+20; cy=int(ys[top].mean())+170; cx=int(xs[top].mean())+150
r=14
patch=im.crop((cx-r,cy-r,cx+r,cy+r))
mask=Image.new('L',(2*r,2*r),0); ImageDraw.Draw(mask).ellipse((1,1,2*r-2,2*r-2),fill=255); mask=mask.filter(ImageFilter.GaussianBlur(1.2))
ty=cy+2*35                                                            # 혹 간격(약 35px)으로 두 칸 아래 = 미간
im.paste(patch,(cx-r,ty-r),mask)
im.save(D+'base_v5.webp',quality=80); im.save(SP+'v5.png')
im.crop((60,140,240,440)).resize((360,600)).save(SP+'y_pole5.png'); print('top',cx,cy,'->',ty)
