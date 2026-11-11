from lk import *
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
im0=Image.open(SP+'mer-05/v4g.png').convert('RGB'); im=np.asarray(im0).astype(float)
H,W,_=im.shape; K=W/1421
P=[(0,0),(985,0),(1035,135),(1240,135),(1338,232),(1300,262),(1215,300),(1000,352),(800,372),(840,425),(810,468),(700,472),(600,468),(560,440),(240,432),(232,462),(215,488),(160,492),(110,500),(60,525),(20,548),(0,556)]
mk=Image.new('L',(W,H),0); ImageDraw.Draw(mk).polygon([(x*K,y*K) for x,y in P],fill=255)
r,g,b=im[...,0],im[...,1],im[...,2]
river=(b>190)&(g>140)&(r<140); sky=(b>215)&(g>215)&(r>170)
m=np.asarray(mk)/255.0*(~river&~sky)
m=np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2.5*K)))/255.0
shade=np.array([30,45,110.]); a=0.36
out=im*(1-a*m[...,None])+shade*(a*m[...,None])
o=Image.fromarray(out.clip(0,255).astype('uint8')); o.save(SP+'mer-05/v5.png'); o.resize((1421,793)).save(SP+'mer-05/view5.png')
