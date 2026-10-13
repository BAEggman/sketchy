"""구역 편집 키트 — 단원 통합판을 「바탕 한 장 + 구역별 편집 + 다시 붙이기」로 만드는 도구 (2026-10-13).

  python3 zone_kit.py crop    base.png  out_dir  --centers 530,660,810,955  [--cssw 1024]
      바탕 그림(CSS 1024 폭 기준 좌표)에서 구역 중심마다 9:16 세로 조각을 잘라 2배로 키워 저장한다.
      → out_dir/crop_<i>.png  +  out_dir/crops.json  (조각의 CSS 좌표 상자)

  python3 zone_kit.py compose config.json out.png
      config 예:
      {"base": "base2x.png", "cssw": 1024,
       "crops": "crops.json",
       "zones": [ {"crop": 0, "img": "Z0.png", "own": [440, 600]},     # own = 이 구역이 소유하는 CSS x 범위
                  {"crop": 1, "img": "Z1.png", "own": [600, 738]},
                  {"crop": 3, "img": "Z3.png", "own": [905, 1024]} ],
       "patches": [ {"zone": 2, "ellipse": [1467, 738, 60, 58], "shift": [18, 0]} ],   # 바탕 픽셀 좌표
       "feather": 14, "search": 12}
      - 각 구역 편집본을 바탕 위 제자리에 자동 정합(±search px, 하늘·담 띠로 오차 최소)한다.
      - 소유 범위(own) 바깥은 바탕 그대로, 경계는 feather px 로 섞는다.
      - 이웃 구역과 x 범위가 겹치는 소품은 patches 로 타원째 옮겨 붙인다(shift 로 살짝 비켜 놓을 수 있다).
"""
import sys, json, argparse
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion, gaussian_filter

def cmd_crop(a):
    base=Image.open(a.base).convert('RGB'); s=base.width/a.cssw
    H=round(base.height/s); cw=round(H*9/16)
    boxes=[]
    for i,c in enumerate(int(v) for v in a.centers.split(',')):
        x0=max(0,min(a.cssw-cw,c-cw//2)); box=(x0,0,x0+cw,H); boxes.append(box)
        px=tuple(round(v*s) for v in box)
        base.crop(px).resize((2*cw,2*H),Image.LANCZOS).save(f'{a.out_dir}/crop_{i}.png')
    json.dump(boxes,open(f'{a.out_dir}/crops.json','w')); print('crops',boxes,'(CSS 좌표, 업로드 크기',2*cw,'x',2*H,')')

def cmd_compose(a):
    cfg=json.load(open(a.config)); B=np.asarray(Image.open(cfg['base']).convert('RGB')).astype(float)
    H,W,_=B.shape; s=W/cfg.get('cssw',1024); crops=json.load(open(cfg['crops']))
    F=cfg.get('feather',14); R=cfg.get('search',12); C=B.copy(); x=np.arange(W); L=[]; COV=[]
    for zi,z in enumerate(cfg['zones']):
        x0,y0,x1,y1=[round(v*s) for v in crops[z['crop']]]; zw,zh=x1-x0,y1-y0
        Z=np.asarray(Image.open(z['img']).convert('RGB').resize((zw,zh),Image.LANCZOS)).astype(float)
        # 정합: 위쪽 띠(하늘·담) 7%~38% 높이, 좌우 4% 안쪽
        ya,yb=int(zh*.07),int(zh*.38); xa,xb=int(zw*.04),int(zw*.96); best=None
        for dy in range(-R,R+1):
            for dx in range(-R,R+1):
                b=B[ya+dy+y0:yb+dy+y0, x0+xa+dx:x0+xb+dx]
                if b.shape!=(yb-ya,xb-xa,3): continue
                e=np.mean((Z[ya:yb,xa:xb]-b)**2)
                if best is None or e<best[0]: best=(e,dx,dy)
        e,dx,dy=best; print(f"zone {zi} ({z['img']}): 정합 dx={dx} dy={dy} mse={e:.1f}" + ("  ⚠ mse 큼 — 편집이 구도를 바꿨는지 확인" if e>300 else ""))
        l=np.zeros_like(B); c=np.zeros((H,W))
        ys=np.arange(zh)+y0+dy; xs=np.arange(zw)+x0+dx; vy=(ys>=0)&(ys<H); vx=(xs>=0)&(xs<W)
        l[np.ix_(ys[vy],xs[vx])]=Z[np.ix_(np.where(vy)[0],np.where(vx)[0])]; c[np.ix_(ys[vy],xs[vx])]=1
        cov=binary_erosion(c>0,iterations=6).astype(float)
        cov[:8,:]=c[:8,:]; cov[-8:,:]=c[-8:,:]; cov[:,:8]=c[:,:8]; cov[:,-8:]=c[:,-8:]   # 그림 바깥 테두리 변은 깎지 않음
        L.append(l); COV.append(cov)
        oa,ob=[round(v*s) for v in z['own']]
        left=np.ones(W) if oa<=0 else np.clip((x-(oa-F))/(2*F),0,1)
        right=np.ones(W) if ob>=W else np.clip(((ob+F)-x)/(2*F),0,1)
        M=np.tile(left*right,(H,1))*cov
        C=C*(1-M[...,None])+l*M[...,None]
    yy,xx=np.mgrid[0:H,0:W]
    for p in cfg.get('patches',[]):
        cx,cy,rx,ry=p['ellipse']; sx,sy=p.get('shift',[0,0])
        m=((((xx-cx-sx)/rx)**2+((yy-cy-sy)/ry)**2)<=1).astype(float); m=gaussian_filter(m,4)
        src=np.roll(np.roll(L[p['zone']],sx,axis=1),sy,axis=0)
        C=C*(1-m[...,None])+src*m[...,None]
    Image.fromarray(np.clip(C,0,255).astype('uint8')).save(a.out); print('saved',a.out,(W,H))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('crop'); p.add_argument('base'); p.add_argument('out_dir'); p.add_argument('--centers',required=True); p.add_argument('--cssw',type=int,default=1024)
    p=sp.add_parser('compose'); p.add_argument('config'); p.add_argument('out')
    a=ap.parse_args(); {'crop':cmd_crop,'compose':cmd_compose}[a.cmd](a)
