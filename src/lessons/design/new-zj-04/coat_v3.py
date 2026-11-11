# new-zj-04 v2 -> v3: 지친 농부가 내민 분홍 혀 위에 두꺼운 흰 설태(苔膩)를 덧칠 — 혀 가장자리의 분홍은 남김
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-04/'
D='/home/claude/s7/work/src/lessons/design/new-zj-04/'
im=Image.open(SP+'v2.png').convert('RGB')
m=Image.new('L',im.size,0); ImageDraw.Draw(m).ellipse((1443,686,1458,701),fill=255)
a=np.asarray(im).astype(int); mk=np.asarray(m)>0
pink=(a[:,:,0]>170)&(a[:,:,1]<160)&(a[:,:,0]-a[:,:,2]>25)
sel=mk&pink
coat=np.array([238,236,226])
b=a.copy(); b[sel]=coat
rng=np.random.default_rng(1)
ys,xs=np.where(sel)
for i in rng.choice(len(ys),size=min(14,len(ys)),replace=False): b[ys[i],xs[i]]=[205,200,190]
out=Image.fromarray(b.astype('uint8'))
mm=Image.fromarray((sel*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))
out=Image.composite(out,im,mm)
out.save(D+'base_v3.webp',quality=80); out.save(SP+'v3.png'); print(sel.sum())
out.crop((1400,660,1480,740)).resize((320,320)).save(SP+'../g_tongue2.png')
