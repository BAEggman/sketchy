"""겹치는 타일 캡처를 정합(registration)해 붙인다 — 2026-10-13.
   tile_stitch.py 는 타일 경계가 맞닿기만 해서, 캡처 배율의 1~2px 오차가 2배 확대 뒤 이음매로 보였다.
   여기서는 타일을 겹치게 찍고(겹침 ≥ 64px), 겹친 띠에서 ±6px 탐색으로 어긋남을 찾아 맞춘 뒤 페더로 섞는다.
   usage: tile_stitch2.py out.png W H  file:tx:ty:tw:th  file:tx:ty:tw:th ..."""
import sys, numpy as np
from PIL import Image
from tile_stitch import crop_tile, _defringe

def place(files, W, H, out):
    cv=np.zeros((H,W,3)); wt=np.zeros((H,W))
    for spec in files:
        f,tx,ty,tw,th=spec.split(':'); tx,ty,tw,th=map(int,(tx,ty,tw,th))
        t=np.asarray(_defringe(crop_tile(f).resize((tw,th),Image.LANCZOS))).astype(float)
        # 이미 놓인 부분과 겹치는 곳에서 어긋남 찾기
        best=(None,0,0)
        if wt[ty:ty+th, tx:tx+tw].sum()>0:
            for dy in range(-6,7):
                for dx in range(-6,7):
                    y0,x0=ty+dy,tx+dx
                    ys=slice(max(y0,0),min(y0+th,H)); xs=slice(max(x0,0),min(x0+tw,W))
                    m=wt[ys,xs]>0.99
                    if m.sum()<2000: continue
                    a=cv[ys,xs][m]; b=t[ys.start-y0:ys.stop-y0, xs.start-x0:xs.stop-x0][m]
                    e=np.mean((a-b)**2)
                    if best[0] is None or e<best[0]: best=(e,dx,dy)
        e,dx,dy=best; y0,x0=ty+dy,tx+dx
        print(f[-14:], 'offset', dx, dy, 'mse', None if e is None else round(e,1))
        # 페더 가중: 타일 가장자리 24px 에서 0→1
        yy=np.arange(th)[:,None]; xx=np.arange(tw)[None,:]
        F=24.0
        w=np.minimum(np.minimum((yy+1)/F,(th-yy)/F),np.minimum((xx+1)/F,(tw-xx)/F)).clip(0,1)
        # 그림 바깥 가장자리(0 또는 W/H에 닿는 변)는 페더하지 않음
        ys=slice(max(y0,0),min(y0+th,H)); xs=slice(max(x0,0),min(x0+tw,W))
        tt=t[ys.start-y0:ys.stop-y0, xs.start-x0:xs.stop-x0]; ww=w[ys.start-y0:ys.stop-y0, xs.start-x0:xs.stop-x0]
        cv[ys,xs]+=tt*ww[...,None]; wt[ys,xs]+=ww
    # 가장자리에서 가중이 0인 곳 보정
    cv=cv/np.maximum(wt,1e-6)[...,None]
    Image.fromarray(np.clip(cv,0,255).astype('uint8')).save(out)

if __name__=='__main__':
    out=sys.argv[1]; W=int(sys.argv[2]); H=int(sys.argv[3])
    place(sys.argv[4:], W, H, out)
