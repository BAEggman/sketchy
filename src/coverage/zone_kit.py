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
        patches.zone = zones 배열 순번(0부터) · ellipse = 편집본 속 소품의 원래 중심·반지름(바탕 픽셀) · shift 만큼 옮겨 붙인다.
      - band(선택, 기본 [0.07,0.38]) = 정합에 쓰는 조각 높이 비율 띠. 소품이 없는 하늘·담 높이로.

  python3 zone_kit.py plan W H [--scale 2]     캡처 타일 계획(__show2 호출 + tile_stitch2 인자)을 찍는다
  python3 zone_kit.py finish comp.png out.webp [--wm x0,y0,x1,y1 ...]   워터마크 메우기 + 언샤프 + webp
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
        band=cfg.get('band',[0.07,0.38]); ya,yb=int(zh*band[0]),int(zh*band[1]); xa,xb=int(zw*.04),int(zw*.96); best=None
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

def cmd_plan(a):
    """캡처 타일 계획 — W×H(__setup() 이 돌려준 값) 그림을 576×≤560 타일로 겹쳐 덮는 __show2 호출과 tile_stitch2 인자를 찍는다."""
    W,H,k=a.W,a.H,a.scale; TW,TH,OV=576,560,96
    def starts(L,T):
        if L<=T: return [0],L
        n=1; 
        while (L-T)/n>T-OV: n+=1
        return [round(i*(L-T)/n) for i in range(n+1)],T
    xs,tw=starts(W,TW); ys,th=starts(H,TH)
    print(f'# {W}x{H} → 타일 {len(xs)*len(ys)}장 ({tw}x{th}), zoom 영역 [0,0,820,800] (스크린샷으로 좌표계 1456x816 고정 뒤)')
    specs=[]
    for ty in ys:
        for tx in xs:
            print(f'window.__show2({tx},{ty},{tw},{th})   → zoom → 저장 경로를 아래 SHOT_{len(specs)} 자리에')
            specs.append(f'SHOT_{len(specs)}:{k*tx}:{k*ty}:{k*tw}:{k*th}')
    print('window.__show2(-1)')
    print(f'python3 tile_stitch2.py OUT.png {k*W} {k*H} '+' '.join(specs))

def cmd_finish(a):
    """마무리 — (선택) 워터마크 ✦ 메우기 → 약한 언샤프 → webp.  --wm x0,y0,x1,y1 는 ✦ 를 둘러싼 상자(합성본 픽셀)."""
    from PIL import ImageFilter
    from scipy.ndimage import median_filter, binary_dilation, label
    im=np.asarray(Image.open(a.inp).convert('RGB')).astype(float)
    for box in a.wm or []:
        # --wm 상자는 눈으로 ✦ 를 확인하고 그것만 감싸게 잡는다(자동 탐지는 하지 않는다 — 불빛·눈송이를 지운다).
        # 상자에 내접한 타원 안에서, 주변 중앙값보다 밝은(+6) 덩어리 중 가운데에 가장 가까운 것을 메운다.
        x0,y0,x1,y1=map(int,box.split(',')); sub=im[y0:y1,x0:x1].copy(); lum=sub.mean(2)
        h,w=lum.shape; yy,xx=np.mgrid[0:h,0:w]
        ell=(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)<=1
        m=((lum-median_filter(lum,size=31))>6)&ell; lab,n=label(m)
        cand=[i for i in range(1,n+1) if (lab==i).sum()>=30]
        if not cand: print('wm',box,'밝은 덩어리 없음 — 건너뜀'); continue
        def dist(i):
            ys,xs=np.where(lab==i); return (ys.mean()-h/2)**2+(xs.mean()-w/2)**2
        best=min(cand,key=dist); mm=binary_dilation(lab==best,iterations=2)
        Image.fromarray(np.clip(np.concatenate([sub,np.where(mm[...,None],[255,0,255],sub)],1),0,255).astype('uint8')).resize((4*w,2*h)).save(a.out+f'.wm_{x0}_{y0}.png')
        o1=sub.copy(); o2=sub.copy()
        for y in range(mm.shape[0]):
            if mm[y].any():
                k=np.where(~mm[y])[0]
                for c in range(3): o1[y,:,c]=np.interp(np.arange(mm.shape[1]),k,sub[y,k,c])
        for x in range(mm.shape[1]):
            if mm[:,x].any():
                k=np.where(~mm[:,x])[0]
                for c in range(3): o2[:,x,c]=np.interp(np.arange(mm.shape[0]),k,sub[k,x,c])
        f=(o1+o2)/2+np.random.default_rng(1).normal(0,1.2,sub.shape); sub[mm]=f[mm]; im[y0:y1,x0:x1]=sub
        print('wm',box,'메움',int(mm.sum()),'px')
    out=Image.fromarray(np.clip(im,0,255).astype('uint8')).filter(ImageFilter.UnsharpMask(radius=1.2,percent=60,threshold=2))
    out.save(a.out,quality=84,method=6); print('saved',a.out,out.size)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('crop'); p.add_argument('base'); p.add_argument('out_dir'); p.add_argument('--centers',required=True); p.add_argument('--cssw',type=int,default=1024)
    p=sp.add_parser('compose'); p.add_argument('config'); p.add_argument('out')
    p=sp.add_parser('plan'); p.add_argument('W',type=int); p.add_argument('H',type=int); p.add_argument('--scale',type=int,default=1)
    p=sp.add_parser('finish'); p.add_argument('inp'); p.add_argument('out'); p.add_argument('--wm',action='append')
    a=ap.parse_args(); {'crop':cmd_crop,'compose':cmd_compose,'plan':cmd_plan,'finish':cmd_finish}[a.cmd](a)
