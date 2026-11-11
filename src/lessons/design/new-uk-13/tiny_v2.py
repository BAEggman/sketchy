# new-uk-13 v2: 불 거인 곁 「아주 작고 우는 붉은 사람」이 不及(쪼그라든 아이)으로 읽혀 지움 — 하늘 · 구름으로 메우고 구름 둥근 테두리를 이어 그림
import numpy as np, cv2
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-uk-13/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-uk-13/v1.png').convert('RGB')).astype(float)
h,w=a.shape[:2]
pts=np.array([(563,1014),(575,1006),(587,1001),(599,999),(653,994),(707,1002),(719,1006),(731,1012),(743,1024)],float)
arc=lambda x: np.interp(x,pts[:,0],pts[:,1])   # 실제 테두리 점을 꺾은선으로 이음
m=np.zeros((h,w),bool); m[835:1113,594:716]=True; m[1056:1113,558:750]=True
out=a.copy()
xl,xr=588,722
white=np.median(a[1040:1060,560:585].reshape(-1,3),0)
for y in range(835,1113):
    for x in range(558,750):
        if not m[y,x]: continue
        if y < arc(x)-3:
            t=(x-xl)/(xr-xl); t=min(max(t,0),1)
            out[y,x]=a[y,xl]*(1-t)+a[y,xr]*t
        else:
            out[y,x]=white
# 테두리 선 잇기
o=np.ascontiguousarray(out.clip(0,255).astype(np.uint8))
xs=np.arange(585,725); ys=arc(xs)
P=np.stack([xs,ys],1).round().astype(np.int32).reshape(-1,1,2)
cv2.polylines(o,[P],False,(28,28,30),4,cv2.LINE_AA)
o=o.astype(float)
# 경계 부드럽게
mm=cv2.GaussianBlur(m.astype(float),(0,0),2)[...,None]
fin=a*(1-mm)+o*mm
fin[m]=o[m]
fin=np.ascontiguousarray(fin.clip(0,255).astype(np.uint8)); cv2.polylines(fin,[P],False,(28,28,30),4,cv2.LINE_AA)   # 선은 맨 위에 다시
img=Image.fromarray(fin.clip(0,255).astype(np.uint8)); img.save(D+'base_v2.webp',quality=80); img.save(SP+'new-uk-13/v2.png')
img.crop((420,760,900,1144)).save(SP+'uk13_v2_crop.png')
