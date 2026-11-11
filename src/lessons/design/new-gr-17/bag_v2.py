# new-gr-17 v1 -> v2: 왼쪽 아래 쇼핑객의 비닐봉지에 찍힌 "153" · "E" 같은 글자를 봉지 하늘색으로 덮음
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-17/'
D='/home/claude/s7/work/src/lessons/design/new-gr-17/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).astype(int).copy()
reg=a[985:1050,40:110]; lb=(reg[:,:,2]>190)&(reg[:,:,1]>190)&(reg[:,:,0]<215)&(reg[:,:,0]>140)
blue=np.median(reg[lb],axis=0); print('blue',blue)
for y in range(988,1046):
    row=a[y,40:110]; m=(row[:,2]>190)&(row[:,1]>190)&(row[:,0]<215)&(row[:,0]>140)
    xs=np.where(m)[0]
    if len(xs)<3: continue
    x0,x1=40+xs.min()+3,40+xs.max()-2
    for x in range(x0,x1):
        if np.abs(a[y,x]-blue).sum()>30: a[y,x]=blue
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v2.webp',quality=80); im.save(SP+'v2.png')
im.crop((20,960,140,1110)).resize((240,300)).save(SP+'../g17_bag2.png')
