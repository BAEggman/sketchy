import sys, numpy as np
from PIL import Image
def crop_tile(path, probe=10):
    """타일은 왼쪽 위 모서리에 닿아 있다 — 오른쪽·아래의 마젠타 테두리를 찾아 잘라낸다."""
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(int)
    mag=(a[:,:,0]>170)&(a[:,:,1]<100)&(a[:,:,2]>170)
    h,w=mag.shape
    col=mag[:, probe]; row=mag[probe, :]
    ys=np.where(col)[0]; xs=np.where(row)[0]
    y1=int(ys[0]) if len(ys) else h; x1=int(xs[0]) if len(xs) else w
    return im.crop((0,0,x1-4,y1-4))
def stitch(files, out, W=1024, H=1024, T=512):
    """files: 타일 순서 (0,0),(T,0),(0,T),(T,T)… 행 우선. 각 타일을 CSS 크기로 되돌려 붙인다."""
    cv=Image.new('RGB',(W,H)); k=0
    for ty in range(0,H,T):
        for tx in range(0,W,T):
            tw=min(T,W-tx); th=min(T,H-ty)
            c=crop_tile(files[k]); print(files[k][-12:], c.size, '->', (tw,th))
            cv.paste(c.resize((tw,th),Image.LANCZOS), (tx,ty)); k+=1
    cv.save(out); return cv
if __name__=='__main__':
    # usage: tile_stitch.py out.png W H tile1 tile2 ...
    out=sys.argv[1]; W=int(sys.argv[2]); H=int(sys.argv[3])
    stitch(sys.argv[4:], out, W, H)
