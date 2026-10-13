import sys, numpy as np
from PIL import Image
def _magenta(a):
    return (a[:,:,0]>170)&(a[:,:,1]<100)&(a[:,:,2]>170)
def crop_tile(path, probe=10):
    """타일은 왼쪽 위 모서리에 닿아 있다 — 오른쪽·아래의 마젠타 테두리 바로 앞까지 자른다.
       (2026-10-13 개정) 예전엔 4px 안쪽을 잘라 늘렸는데, 그만큼 타일이 늘어나 이음매가 2~3px 어긋났다.
       이제는 경계에서 정확히 자르고, 경계에 번진 마젠타 한두 줄은 붙일 때 안쪽 줄로 덮는다."""
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(int)
    mag=_magenta(a); h,w=mag.shape
    ys=np.where(mag[:, probe])[0]; xs=np.where(mag[probe, :])[0]
    y1=int(ys[0]) if len(ys) else h; x1=int(xs[0]) if len(xs) else w
    return im.crop((0,0,x1,y1))
def _defringe(t, n=2):
    a=np.asarray(t).astype(int).copy()
    for _ in range(n):
        h,w,_=a.shape
        tint=lambda px: (px[...,0]-px[...,1]>60)&(px[...,2]-px[...,1]>60)
        if tint(a[:,-1]).mean()>0.02: a[:,-1]=a[:,-2]
        if tint(a[-1,:]).mean()>0.02: a[-1,:]=a[-2,:]
    # 경계 한 줄은 늘 안쪽과 같게 — 반올림으로 섞인 색 제거
    a[:,-1]=a[:,-2]; a[-1,:]=a[-2,:]
    return Image.fromarray(a.astype('uint8'))
def stitch(files, out, W=1024, H=1024, T=512):
    """files: 타일 순서 (0,0),(T,0),(0,T),(T,T)… 행 우선. 각 타일을 CSS 크기로 되돌려 붙인다."""
    cv=Image.new('RGB',(W,H)); k=0
    for ty in range(0,H,T):
        for tx in range(0,W,T):
            tw=min(T,W-tx); th=min(T,H-ty)
            c=crop_tile(files[k]); print(files[k][-12:], c.size, '->', (tw,th))
            cv.paste(_defringe(c.resize((tw,th),Image.LANCZOS)), (tx,ty)); k+=1
    cv.save(out); return cv
if __name__=='__main__':
    # usage: tile_stitch.py out.png W H tile1 tile2 ...
    out=sys.argv[1]; W=int(sys.argv[2]); H=int(sys.argv[3])
    stitch(sys.argv[4:], out, W, H)
