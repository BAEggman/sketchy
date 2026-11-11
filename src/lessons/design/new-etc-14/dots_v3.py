# v2 → v3: 지붕 모서리에서 비둘기 꼬리로 「올라가는」 점선 다섯 줄을 지운다(비둘기가 둥지에서 날아오르는 것처럼 읽힘).
# 하늘 띠(캡처 좌표 y 136-219) 전체 폭에서 줄마다 하늘색(중앙값)을 구하고, 하늘과 다른 덩어리 중 큰 것(비둘기 · 물건 · 구름 · 지붕)은
# 띠 전체 기준으로 지킨다. 칸마다 점선 범위 x 안의 나머지(점과 흐린 번짐)만 그 줄 하늘색으로 덮는다.
from PIL import Image; import numpy as np, cv2
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-14/'
a=np.asarray(Image.open(SP+'v2.png').convert('RGB')).astype(int).copy(); k=2048/1410
y0,y1=int(100*k),int(219*k)                       # 덩어리 판정은 비둘기 몸 전체가 들어오게 넓게
band=a[y0:y1]; med=np.median(band,axis=1)
non=(np.abs(band-med[:,None,:]).sum(2)>40).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(non,8)
keep=np.isin(lab,[i for i in range(1,n) if st[i,cv2.CC_STAT_AREA]>=400])
keep=cv2.dilate(keep.astype(np.uint8),np.ones((7,7),np.uint8)).astype(bool)
fy0=int(136*k)-y0
tot=0
for x0,x1 in [(132,268),(377,508),(607,738),(837,973),(1067,1208)]:
    X0,X1=int(x0*k),int(x1*k)
    f=np.zeros(keep.shape,bool); f[fy0:,X0:X1]=True; f&=~keep
    band[f]=np.broadcast_to(med[:,None,:],band.shape)[f]; tot+=int(f.sum())
a[y0:y1]=band; print('filled',tot)
Image.fromarray(a.astype(np.uint8)).save(SP+'v3.png')
