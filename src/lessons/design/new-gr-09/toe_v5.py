# new-gr-09 v4 -> v5: 둘째 칸 돌 발 — 요리사 발치에서 발가락 사이 바깥 틈(그림의 왼쪽 첫째 · 둘째 발가락 사이)으로 드는 발자국(검은 타원)을 그려 넣음(中指外間)
#  + 발가락 아래 초록 점 지움 + 다섯째 칸 콧방울 곁까지 간 발자국 끝 셋을 지움(三焦는 광대뼈까지, 挾鼻孔은 大腸)
#  + 아홉째 칸 흰 구슬을 코끝으로 옮김(bead_v2.py와 같은 처리, 입력만 v4)
import numpy as np, math
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-09/'
D='/home/claude/s7/work/src/lessons/design/new-gr-09/'
im=Image.open(SP+'v4.png').convert('RGBA')
P=[(1262,316),(1242,300),(1215,290),(1186,288),(1164,296),(1159,314)]
def foot(img,x,y,ang,side):
    L=Image.new('RGBA',(40,40),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.ellipse((20-5,20-2,20+5,20+2),fill=(25,25,25,255))
    L=L.rotate(-math.degrees(ang),resample=Image.BICUBIC)
    nx,ny=-math.sin(ang),math.cos(ang); ox,oy=nx*3*side,ny*3*side
    img.alpha_composite(L,(int(x+ox-20),int(y+oy-20)))
pts=[]
for (x0,y0),(x1,y1) in zip(P[:-1],P[1:]):
    for t in (0.25,0.75): pts.append((x0+(x1-x0)*t,y0+(y1-y0)*t,math.atan2(y1-y0,x1-x0)))
for i,(x,y,a) in enumerate(pts): foot(im,x,y,a,1 if i%2 else -1)
im=im.convert('RGB'); a=np.asarray(im).astype(int).copy()
def wipe(a,x0,y0,x1,y1,thr=450):
    reg=a[y0:y1,x0:x1]; bg=reg.reshape(-1,3); bg=bg[bg.sum(1)>=thr]
    a[y0:y1,x0:x1]=np.median(bg,axis=0)
for r in [(1203,632,1233,652),(1236,630,1266,649),(1257,646,1269,658)]: wipe(a,*r)
# 초록 점: 행마다 좌우 이웃 중앙값으로
for yy in range(356,376):
    nb=np.concatenate([a[yy,1198:1208],a[yy,1228:1238]]); a[yy,1208:1228]=np.median(nb,axis=0)
im=Image.fromarray(a.clip(0,255).astype('uint8')); im.save(SP+'v5a.png')
im.crop((1100,560,1340,720)).resize((480,320)).save(SP+'../g9_p5fix.png')
im.crop((1104,174,1368,380)).resize((528,412)).save(SP+'../g9_foot2.png')
