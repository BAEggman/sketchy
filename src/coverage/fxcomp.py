"""fix compose: python3 fxcomp.py Fdir base.png out.png x0,y0,x1,y1 [...]  (rect 2x px, feather 12)"""
import sys,json,subprocess,os
from PIL import Image
import numpy as np
d,base,out=sys.argv[1],sys.argv[2],sys.argv[3]; rects=[list(map(int,r.split(','))) for r in sys.argv[4:]]
crops=json.load(open(f'{d}/crops.json')); x0,_,x1,_=crops[0]; X0,X1=x0*2,x1*2; W=X1-X0
B=np.asarray(Image.open(base).convert('RGB')).astype(float)
z=Image.open(f'{d}/out.png').convert('RGB'); Z=np.asarray(z.resize((W,1530),Image.LANCZOS)).astype(float); Bc=B[:,X0:X1]
o=np.asarray(z).astype(float).copy()
for ch in range(3):
    zc=Z[:,:,ch].ravel(); bc=Bc[:,:,ch].ravel(); m=np.abs(zc-bc)<30
    A=np.vstack([zc[m],np.ones(m.sum())]).T; g,of=np.linalg.lstsq(A,bc[m],rcond=None)[0]; o[:,:,ch]=o[:,:,ch]*g+of
Image.fromarray(np.clip(o,0,255).astype('uint8')).save(f'{d}/outt.png')
json.dump([crops[0]],open(f'{d}/crops1.json','w'))
cfg={"base":os.path.abspath(base),"cssw":1024,"crops":os.path.abspath(f'{d}/crops1.json'),"zones":[{"crop":0,"img":os.path.abspath(f'{d}/outt.png'),"own":[1100,1100]}],
     "patches":[{"zone":0,"rect":r,"feather":12} for r in rects],"feather":14,"search":12,"band":[0.07,0.38]}
json.dump(cfg,open(f'{d}/cfg.json','w'))
subprocess.run(['python3','/home/claude/s7/work/src/coverage/zone_kit.py','compose',f'{d}/cfg.json',out],check=True)
