# new-zj-24 v4 -> v5: 다섯째 의자(초승달 · 齒) 손님 얼굴의 짙은 붉은 줄(피처럼 보임)을, 같은 자리의 부드럽게 번지는 붉은 빛으로 바꿈
import numpy as np
from PIL import Image, ImageFilter
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-24/'
D='/home/claude/s7/work/src/lessons/design/new-zj-24/'
a=np.asarray(Image.open(SP+'v4.png').convert('RGB')).astype(float).copy()
skin=np.median(a[340:356,1828:1846].reshape(-1,3),axis=0)          # 반대쪽 볼의 살색
x0,x1,y0,y1=1762,1830,288,392
sub=a[y0:y1,x0:x1].copy()
red=np.clip((sub[:,:,0]-sub[:,:,1])-(skin[0]-skin[1])-10,0,None)   # 살색보다 붉은 정도
keep=~((sub.max(axis=2)-sub.min(axis=2)<45)&(sub.sum(axis=2)<330))   # 무채색 어두운 윤곽선 · 머리카락만 그대로(짙은 붉은 점은 고침)
t=np.clip(red/70,0,1)*keep
lum=np.maximum(sub.mean(axis=2,keepdims=True),skin.mean()*0.8); flat=np.clip(skin*(lum/skin.mean()),0,255)   # 짙은 붉은 점은 살색 밝기로 끌어올림
basei=sub*(1-t[...,None])+flat*t[...,None]                           # 붉은 기를 뺀 바탕
glow=Image.fromarray((np.clip(t,0,1)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(9))
g=np.asarray(glow).astype(float)/255*1.0
g*=keep
tint=np.array([235,90,80.])
out=basei*(1-g[...,None]*0.8)+tint*(g[...,None]*0.8)
yy,xx=np.mgrid[0:y1-y0,0:x1-x0]; edge=np.minimum.reduce([xx,yy,(x1-x0-1)-xx,(y1-y0-1)-yy]).astype(float)
w=np.clip(edge/5,0,1)[...,None]
a[y0:y1,x0:x1]=sub*(1-w)+out*w
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v5.webp',quality=80); im.save(SP+'v5.png')
im.crop((1740,270,1920,450)).resize((540,540)).save(SP+'y_c5_v5.png')
