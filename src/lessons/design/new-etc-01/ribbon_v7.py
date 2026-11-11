# new-etc-01 v7: 연 꼬리가 네 색(초록 · 빨강 · 노랑 · 검정)뿐이라, 검정 꼬리 가운데 선을 따라 오른쪽에 흰 꼬리 하나를 더 그림(五行 다섯 색)
import numpy as np, cv2
from PIL import Image
D='/home/claude/s7/work/src/lessons/design/new-etc-01/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
a=np.asarray(Image.open(SP+'new-etc-01/v6.png').convert('RGB')).copy()
pts=[]
for y in range(286,400,3):
    row=a[y,1380:1440].astype(int).sum(1)<200
    runs=[];start=None
    for i,v in enumerate(list(row)+[False]):
        if v and start is None: start=i
        if not v and start is not None: runs.append((i-start,start)); start=None
    if not runs: continue
    w,s=max(runs)
    if w>=5: pts.append((1380+s+w/2,y))
pts=np.array(pts,float)
# 매끈하게
cf=np.polyfit(pts[:,1],pts[:,0],3)               # x(y)를 3차식으로 매끈하게
ys=np.arange(283,int(pts[-1,1])+1,2); xs=np.polyval(cf,ys)+18
xs[ys<300]=np.interp(ys[ys<300],[283,300],[np.polyval(cf,300)+8,np.polyval(cf,300)+18])   # 뿌리는 연 모서리 쪽으로 모음
P=np.stack([xs,ys],1)
P=P.round().astype(np.int32).reshape(-1,1,2)
blk=a.copy(); cv2.polylines(blk,[P],False,(25,25,28),13,cv2.LINE_AA)
wht=blk.copy(); cv2.polylines(wht,[P],False,(246,246,242),8,cv2.LINE_AA)
# 검정 꼬리는 앞에 그대로 두기
orig_black=(a.astype(int).sum(2)<200)
reg=np.zeros(orig_black.shape,bool); reg[270:405,1380:1445]=True
keep=orig_black&reg
out=wht.copy(); out[keep]=a[keep]
Image.fromarray(out).save(D+'base_v7.webp',quality=80); Image.fromarray(out).save(SP+'new-etc-01/v7.png')
Image.fromarray(out[174:421,1292:1481]).resize((378,494)).save(SP+'e01_kite_v7.png')
print(len(pts))
