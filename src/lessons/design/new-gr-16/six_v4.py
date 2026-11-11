# new-gr-16 v3 -> v4: 大椎 칸(가운데 줄 셋째)에 해 배지 사람을 하나 더 넣어 왼쪽 셋 · 오른쪽 셋 = 六陽經
#  칸 안을 금발 여자 오른쪽 끝에서 갈라, 금발 여자를 복제해(옷 → 파랑, 머리 → 짙은 갈색) 끼워 넣고, 전체를 칸 너비로 가로 압축
import numpy as np, colorsys
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-16/'
D='/home/claude/s7/work/src/lessons/design/new-gr-16/'
im=Image.open(SP+'v3.png').convert('RGB')
OX,OY=1024,377            # 칸 자른 원점(2048 좌표)
X0,X1,Y0,Y1=1033,1535,382,765   # 칸 안쪽(테두리 제외)
panel=im.crop((X0,Y0,X1,Y1)); W=X1-X0
cut=1024+122-X0           # 금발 여자 오른쪽 끝(칸 안 좌표)
p0,p1=1024+50-X0,cut      # 금발 여자 띠
L=panel.crop((0,0,cut,panel.height)); R=panel.crop((cut,0,W,panel.height))
P=np.asarray(panel.crop((p0,0,p1,panel.height))).astype(float)/255
# 복제 인물 색 바꾸기: 붉은 갈색 옷 → 파랑, 금발(윗부분) → 짙은 갈색
H=P.shape[0]; out=P.copy()
for y in range(H):
    for x in range(P.shape[1]):
        r,g,b=P[y,x]; h,s,v=colorsys.rgb_to_hsv(r,g,b)
        if y>215 and s>0.25 and (h<0.06 or h>0.93) and v<0.85:   # 옷
            out[y,x]=colorsys.hsv_to_rgb(0.60,s,v)
        elif 165<y<225 and s>0.35 and 0.11<h<0.17 and v>0.6:     # 머리
            out[y,x]=colorsys.hsv_to_rgb(0.07,0.6,v*0.45)
P2=Image.fromarray((out*255).clip(0,255).astype('uint8'))
strip=Image.new('RGB',(L.width+P2.width+R.width,panel.height))
strip.paste(L,(0,0)); strip.paste(P2,(L.width,0)); strip.paste(R,(L.width+P2.width,0))
strip=strip.resize((W,panel.height),Image.LANCZOS)
TOP=150   # 이 행 위(벽 · 등뼈 조각)는 원래 그림 그대로 — 조각이 겹쳐 보이지 않게
im.paste(strip.crop((0,TOP,W,panel.height)),(X0,Y0+TOP))
# 위 원래 영역(TOP 위)에 남은 지팡이 윗동은 inpaint로 지우고(갈색 = 채도 높은 픽셀 + 그 테두리), 옮겨진 지팡이 끝에 둥근 손잡이를 그림
import cv2
from scipy.ndimage import binary_dilation
a=np.asarray(im).astype(np.uint8).copy()
r0,r1,c0,c1=110,TOP,170,222
seg=a[Y0+r0:Y0+r1,X0+c0:X0+c1].astype(int)
sat=np.array([[colorsys.rgb_to_hsv(*(seg[y,x]/255))[1] for x in range(seg.shape[1])] for y in range(seg.shape[0])])
staff=binary_dilation(sat>0.22,iterations=3)
mask=np.zeros(a.shape[:2],np.uint8); mask[Y0+r0:Y0+r1,X0+c0:X0+c1][staff]=255
a=cv2.cvtColor(cv2.inpaint(cv2.cvtColor(a,cv2.COLOR_RGB2BGR),mask,5,cv2.INPAINT_TELEA),cv2.COLOR_BGR2RGB).astype(int)
# 옮겨진 지팡이의 TOP 행 위치를 찾아 손잡이
row=a[Y0+TOP+2,X0+200:X0+270]; hs=[colorsys.rgb_to_hsv(*(p/255)) for p in row]
xs=[i for i,(h,sv,v) in enumerate(hs) if sv>0.25 and 0.03<h<0.15]
if xs:
    cx=X0+200+int(np.median(xs)); cy=Y0+TOP-4
    from PIL import ImageDraw
    tmp=Image.fromarray(a.astype('uint8')); d=ImageDraw.Draw(tmp)
    d.ellipse((cx-9,cy-9,cx+9,cy+9),fill=(176,130,86),outline=(30,20,15),width=3)
    a=np.asarray(tmp).astype(int)
im=Image.fromarray(a.astype('uint8'))
im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((1024,377,1542,769)).save(SP+'../g16_c2.png'); print('ok', L.width, P2.width, R.width)
