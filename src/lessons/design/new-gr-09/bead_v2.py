# new-gr-09 v1 -> v2: 아홉째 칸 흰 구슬을 콧방울 옆에서 코끝(素髎 = 鼻準)으로 옮김
#  원래 구슬 자리는 둘레 밝은 회색 중앙값으로 메우고 가장자리를 흐림, 끊긴 코 오른쪽 선을 콧방울까지 이어 그림, 코끝에 새 구슬
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-09/'
D='/home/claude/s7/work/src/lessons/design/new-gr-09/'
import sys
SRC,V=(sys.argv[1],sys.argv[2]) if len(sys.argv)>2 else ('v1.png','2')  # v5: python3 bead_v2.py v5a.png 5
im=Image.open(SP+SRC).convert('RGB'); a=np.asarray(im).astype(int)
cx0,cy0,r0=1763,1028,19
yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; dist=np.hypot(xx-cx0,yy-cy0)
ring=a[(dist>r0+2)&(dist<r0+10)]; ring=ring[ring.sum(1)>450]
med=np.median(ring,axis=0); print('fill',med)
b=a.copy(); b[dist<=r0]=med
out=Image.fromarray(b.astype('uint8'))
m=Image.new('L',out.size,0); ImageDraw.Draw(m).ellipse((cx0-r0-3,cy0-r0-3,cx0+r0+3,cy0+r0+3),fill=255)
out=Image.composite(out.filter(ImageFilter.GaussianBlur(2)),out,m.filter(ImageFilter.GaussianBlur(2)))
d=ImageDraw.Draw(out)
P=[(1752,994),(1754,1008),(1756,1021)]
def cat(P,n=12):
    Q=[P[0]]+P+[P[-1]]; o=[]
    for i in range(1,len(Q)-2):
        p0,p1,p2,p3=[np.array(q,float) for q in Q[i-1:i+3]]
        for t in np.linspace(0,1,n,endpoint=False):
            o.append(tuple(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)))
    return o+[P[-1]]
d.line(cat(P),fill=(35,35,35),width=3,joint='curve')
cx,cy,r=1716,1044,17
d.ellipse((cx-r-3,cy-r-3,cx+r+3,cy+r+3),fill=(20,20,20))
d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(246,248,250))
d.ellipse((cx-r+5,cy-r+4,cx-r+13,cy-r+11),fill=(255,255,255))
d.arc((cx-r+3,cy-r+3,cx+r-3,cy+r-3),20,120,fill=(190,196,205),width=3)
out.save(D+f'base_v{V}.webp',quality=80); out.save(SP+f'v{V}.png')
out.crop((1600,950,1850,1120)).resize((500,340)).save(SP+'../g9_bead.png')
