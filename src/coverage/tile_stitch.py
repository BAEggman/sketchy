import sys, numpy as np
from PIL import Image
def crop_tile(path):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(int)
    mag=(a[:,:,0]>170)&(a[:,:,1]<100)&(a[:,:,2]>170)
    h,w=mag.shape
    col=mag[:, 60]; row=mag[60, :]           # 왼쪽 위 모서리에 닿는 타일 → 위·왼쪽은 0
    ys=np.where(col)[0]; xs=np.where(row)[0]
    y1=int(ys[0]) if len(ys) else h; x1=int(xs[0]) if len(xs) else w
    return im.crop((0,0,x1-4,y1-4))
def stitch(files, out):
    tiles=[(0,0),(512,0),(0,512),(512,512)]
    cv=Image.new('RGB',(1024,1024))
    for f,t in zip(files,tiles):
        c=crop_tile(f); print(f[-12:], c.size)
        cv.paste(c.resize((512,512),Image.LANCZOS), t)
    cv.save(out); return cv
if __name__=='__main__':
    stitch(sys.argv[1:5], sys.argv[5])
