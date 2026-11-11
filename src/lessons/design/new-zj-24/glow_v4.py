# new-zj-24 v3 -> v4: 셋째 의자(작은 해 · 頭側痛) 손님 이마 가운데의 붉은 빛을 살색으로 되돌려, 붉은 빛이 양 관자놀이에만 남게 함(둘째 의자 이마 아픔과 헷갈림 방지)
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-24/'
D='/home/claude/s7/work/src/lessons/design/new-zj-24/'
a=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(float).copy()
skin=np.median(a[365:378,1020:1042].reshape(-1,3),axis=0)          # 아래 얼굴(코 · 볼)의 살색
base=skin[0]-skin[1]
x0,x1,y0,y1=998,1066,296,352                                         # 이마 가운데(두 손 사이)
sub=a[y0:y1,x0:x1]
lum=sub.mean(axis=2,keepdims=True); sl=skin.mean()
t=np.clip(((sub[:,:,0]-sub[:,:,1])-base-8)/55,0,1)[...,None]
t*= (sub.sum(axis=2,keepdims=True)>300)                              # 눈썹 · 윤곽선은 그대로
# 가장자리를 부드럽게
yy,xx=np.mgrid[0:y1-y0,0:x1-x0]; edge=np.minimum.reduce([xx,yy,(x1-x0-1)-xx,(y1-y0-1)-yy]).astype(float)
t*=np.clip(edge/6,0,1)[...,None]
new=np.clip(skin*(lum/sl),0,255)
a[y0:y1,x0:x1]=sub*(1-t)+new*t
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((960,270,1110,400)).resize((450,390)).save(SP+'y_c3_v4.png')
print(skin)
