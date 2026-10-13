from PIL import Image
import numpy as np, json, sys
from scipy.ndimage import binary_erosion, gaussian_filter
B=np.asarray(Image.open('base2x.png').convert('RGB')).astype(float); H,W,_=B.shape
crops=json.load(open('crops.json'))
names={'fire':'Zf','wet':'Zw','dry':'Zd','cold':'Zc'}
reg={'fire':(-3,-2),'wet':(-3,-1),'dry':(-4,-1),'cold':(-5,-1)}
bounds={'fire':(440,600),'wet':(600,738),'dry':(738,905),'cold':(905,1024)}
patches=[('dry',(1368,676,1528,802))]   # (zone, x0,y0,x1,y1 in 2x canvas)
L={}; COV={}
for z in names:
    X0=2*crops[z][0]; dx,dy=reg[z]
    Z=np.asarray(Image.open(names[z]+'.png').convert('RGB').resize((488,868),Image.LANCZOS)).astype(float)
    l=np.zeros_like(B); c=np.zeros((H,W))
    ys=np.arange(868)+dy; xs=np.arange(488)+X0+dx; vy=(ys>=0)&(ys<H); vx=(xs>=0)&(xs<W)
    l[np.ix_(ys[vy],xs[vx])]=Z[np.ix_(np.where(vy)[0],np.where(vx)[0])]; c[np.ix_(ys[vy],xs[vx])]=1
    # 그림 바깥 테두리에 닿은 변은 깎지 않는다
    e=binary_erosion(c>0,iterations=6).astype(float)
    if z=='cold': e[:, -40:]=c[:, -40:]
    e[:8,:]=c[:8,:]; e[-8:,:]=c[-8:,:]
    L[z]=l; COV[z]=e
C=B.copy(); x=np.arange(W); F=14
for z in ['fire','wet','dry','cold']:
    a,b=2*bounds[z][0],2*bounds[z][1]
    left=np.clip((x-(a-F))/(2*F),0,1); right=np.ones(W) if z=='cold' else np.clip(((b+F)-x)/(2*F),0,1)
    M=np.tile(left*right,(H,1))*COV[z]
    C=C*(1-M[...,None])+L[z]*M[...,None]
# 물동이: 젖은 구역 화로와 겹쳐 띠 경계로는 못 살린다 → 타원 패치로 옮겨 붙인다(오른쪽 18px)
cx,cy,rx,ry,sh=1467,738,60,58,18
yy,xx=np.mgrid[0:H,0:W]
m=((((xx-cx-sh)/rx)**2+((yy-cy)/ry)**2)<=1).astype(float); m=gaussian_filter(m,4)
src=np.roll(L['dry'],sh,axis=1)
C=C*(1-m[...,None])+src*m[...,None]
out=Image.fromarray(np.clip(C,0,255).astype('uint8')); out.save(sys.argv[1] if len(sys.argv)>1 else 'comp_v3.png')
