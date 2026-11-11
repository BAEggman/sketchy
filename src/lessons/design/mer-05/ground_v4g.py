# v4의 위 둑 땅색 고르기 → v4g. 다각형 안에서 땅 계열 색에 가까운 화소를 G로. 색마다 쓰는 구역을 제한해 인물·물건을 건드리지 않는다.
from lk import *
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage as ndi
im=Image.open(SP+'mer-05/v4.png').convert('RGB'); a=np.asarray(im).astype(float); H,W,_=a.shape; K=W/1421
P=[(0,150),(985,150),(1035,135),(1240,135),(1338,232),(1300,262),(1215,300),(1000,352),(800,372),(840,425),(810,468),(700,472),(600,468),(560,440),(240,432),(232,462),(215,488),(160,492),(110,500),(60,525),(20,548),(0,556)]
mk=Image.new('L',(W,H),0); ImageDraw.Draw(mk).polygon([(x*K,y*K) for x,y in P],fill=255); poly=np.asarray(mk)>0
yy,xx=np.mgrid[0:H,0:W]/K   # 보기 좌표(1421 폭)
def near(cols,thr):
    T=np.array(cols,float); return np.min(np.linalg.norm(a[:,:,None,:]-T[None,None,:,:],axis=3),axis=2)<thr
m = near([(100,157,70),(110,170,100)],30)
m|= near([(32,105,153),(28,104,156),(24,96,144)],30) & (yy>150)&(yy<262)
m|= near([(60,125,115),(70,130,130)],26) & (yy>175)&(yy<262)
m|= near([(24,80,120),(30,90,130)],24) & (yy>222)&(yy<300)&(xx<700)
m|= near([(126,187,128),(120,180,120),(82,141,96),(72,132,96),(84,132,84)],30) & (xx>700)
m|= near([(173,208,79),(131,169,23)],34) & (xx<260)&(yy>330)
m&=poly
m=ndi.binary_opening(m,iterations=1); m=ndi.binary_closing(m,iterations=2)&poly
G=np.array([100,157,70.]); out=a.copy(); out[m]=G
Image.fromarray(out.clip(0,255).astype('uint8')).save(SP+'mer-05/v4g.png')
print('px',m.sum())
