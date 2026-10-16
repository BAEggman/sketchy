"""fxdiff.py Fdir base.png -> prints bboxes (2x base coords) of changed areas, saves diff.png"""
import sys,json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
d,base=sys.argv[1],sys.argv[2]
crops=json.load(open(f'{d}/crops.json')); x0,_,x1,_=crops[0]; X0,X1=x0*2,x1*2; W=X1-X0
B=np.asarray(Image.open(base).convert('RGB')).astype(float)[:,X0:X1]
Z=np.asarray(Image.open(f'{d}/out.png').convert('RGB').resize((W,1530),Image.LANCZOS)).astype(float)
D=np.abs(Z-B).mean(2)
D=ndimage.uniform_filter(D,15)
m=D>28
m=ndimage.binary_opening(m,iterations=3)
lab,n=ndimage.label(m)
out=[]
for i,s in enumerate(ndimage.find_objects(lab)):
    area=(lab[s]==i+1).sum()
    if area<1500: continue
    out.append((area,s[1].start+X0,s[0].start,s[1].stop+X0,s[0].stop))
for o in sorted(out,reverse=True)[:12]: print(o)
Image.fromarray((np.clip(D*3,0,255)).astype('uint8')).save(f'{d}/diff.png')
