# new-gr-08 v2 -> v3: 첫 칸 등뼈 지팡이 사내의 앞가슴 정중선 등뼈 무늬를 살색으로 지움(任脈 오해 방지)
import numpy as np
from PIL import Image, ImageFilter
D='/home/claude/s7/work/src/lessons/design/new-gr-08/'
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-08/'
im=Image.open(SP+'v2.png').convert('RGB'); a=np.asarray(im).astype(int)
x0,y0,x1,y1=[int(v) for v in __import__('sys').argv[1:5]] if len(__import__('sys').argv)>4 else (348,165,368,207)
reg=a[y0:y1,x0:x1]
# 살색 표본: 영역 양옆 띠
side=np.concatenate([a[y0:y1,x0-8:x0].reshape(-1,3),a[y0:y1,x1:x1+8].reshape(-1,3)])
lum=side.sum(1); skin=np.median(side[lum>np.percentile(lum,40)],axis=0)
for yy in range(y0,y1):
    row=a[yy,x0-8:x1+8]; rl=row.sum(1)
    s=np.median(row[rl>np.percentile(rl,50)],axis=0)
    a[yy,x0:x1]=s
out=Image.fromarray(a.clip(0,255).astype('uint8'))
m=Image.new('L',out.size,0); 
from PIL import ImageDraw; ImageDraw.Draw(m).rectangle((x0-2,y0-2,x1+2,y1+2),fill=255)
bl=out.filter(ImageFilter.GaussianBlur(2)); out=Image.composite(bl,out,m)
out.save(D+'base_v3.webp',quality=80); out.save(SP+'v3.png')
out.crop((288,43,461,331)).resize((346,576)).save('/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/g8_p1fix.png')
print(skin)
# 허리띠 위에 남은 맨 아래 등뼈 조각: 행마다 좌우 이웃(허리띠 붉은색 · 바지 청색) 중앙값으로 덮음
a=np.asarray(out).astype(int).copy()
for yy in range(207,226):
    nb=np.concatenate([a[yy,341:351],a[yy,363:372]]); a[yy,351:363]=np.median(nb,axis=0)
out=Image.fromarray(a.clip(0,255).astype('uint8'))
m2=Image.new('L',out.size,0); ImageDraw.Draw(m2).rectangle((349,205,365,228),fill=255)
out=Image.composite(out.filter(ImageFilter.GaussianBlur(1)),out,m2)
out.save(D+'base_v3.webp',quality=80); out.save(SP+'v3.png')
out.crop((330,185,390,235)).resize((480,400),Image.NEAREST).save('/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/g8_belt.png')
