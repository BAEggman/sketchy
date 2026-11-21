"""Gemini 스티커 판(3×2)을 피규어 하나씩 잘라 images/herbs/<hid>.webp 로 저장.
usage: python3 crop_stickers.py SHEET_ID 판그림.jpeg [--grid]  (sheets.json 순서 = 위 줄 왼→오, 아래 줄 왼→오)
--grid: 덩어리 찾기 대신 화면을 3×2로 등분해 자른다."""
import sys,json,os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sheets={s['sheet']:s for s in json.load(open(f'{ROOT}/runs/20261122-p3-herbstickers/sheets.json'))}
sid,path=sys.argv[1],sys.argv[2]; grid='--grid' in sys.argv
s=dict(sheets[sid]); ids=s['ids']
for a_ in sys.argv:
    if a_.startswith('--ids='):
        ids=a_.split('=',1)[1].split(','); s['hanja']=[sheets[sid]['hanja'][sheets[sid]['ids'].index(i)] for i in ids]
n=len(ids)
im=Image.open(path).convert('RGB'); W,H=im.size; a=np.asarray(im).astype(int)
ink=(a.min(2)<235)
boxes=[]
if not grid:
    m=ndimage.binary_dilation(ink,iterations=max(6,W//150))
    lab,k=ndimage.label(m)
    objs=ndimage.find_objects(lab)
    sizes=ndimage.sum(ink,lab,range(1,k+1))
    order=np.argsort(-sizes)[:n]
    for i in order:
        sl=objs[i]; boxes.append((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop))
    if len(boxes)<n or min(sizes[order])<0.15*max(sizes[order]): grid=True; boxes=[]
if grid:
    for r in range(2):
        for c in range(3):
            x0,x1=c*W//3,(c+1)*W//3; y0,y1=r*H//2,(r+1)*H//2
            sub=ink[y0:y1,x0:x1]; ys,xs=np.nonzero(sub)
            if len(xs)==0: continue
            boxes.append((x0+xs.min(),y0+ys.min(),x0+xs.max(),y0+ys.max()))
    boxes=boxes[:n]
# sort: rows by center y (two rows), then x
cy=[(b[1]+b[3])/2 for b in boxes]; mid=H/2
boxes=sorted(boxes,key=lambda b:(0 if (b[1]+b[3])/2<mid else 1, (b[0]+b[2])/2))
os.makedirs(f'{ROOT}/images/herbs',exist_ok=True)
sheet=Image.new('RGB',(n*260,300),'white'); dr=ImageDraw.Draw(sheet)
for j,(b,hid) in enumerate(zip(boxes,ids)):
    pad=16; x0,y0,x1,y1=max(0,b[0]-pad),max(0,b[1]-pad),min(W,b[2]+pad),min(H,b[3]+pad)
    c=im.crop((x0,y0,x1,y1)); w,h=c.size; side=max(w,h)
    sq=Image.new('RGB',(side,side),'white'); sq.paste(c,((side-w)//2,(side-h)//2))
    if side>768: sq=sq.resize((768,768),Image.LANCZOS)
    sq.save(f'{ROOT}/images/herbs/{hid}.webp',quality=90)
    t=sq.resize((250,250)); sheet.paste(t,(j*260+5,5)); dr.text((j*260+8,262),f'{hid} {s["hanja"][j]}',fill='black')
os.makedirs(f'{ROOT}/runs/20261122-p3-herbstickers/check',exist_ok=True)
tag=sid+('_'+'_'.join(ids) if len(ids)!=len(sheets[sid]['ids']) else '')
sheet.save(f'{ROOT}/runs/20261122-p3-herbstickers/check/{tag}.jpg',quality=85)
print(sid,'grid' if grid else 'blobs',len(boxes),'->',' '.join(ids))
