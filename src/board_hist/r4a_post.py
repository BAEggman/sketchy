"""r4a 후처리 (2026-10-16)
 1) RB2 궁궐 간판에 Flash-Lite가 써 넣은 한글 「침통」을 지우고 침통 그림으로 (구역 편집본 RB2.png 576×1024 좌표 — 합성 전에 적용 → RB2f.png)
 2) 합성본의 鍼灸擇日編 달력: 겹쳐 그려진 동그라미 둘·회색 덩이를 지우고, 한 칸에 검은 점 + 뜸봉(붉은 불씨)으로 다시 그림
 usage: r4a_post.py sign RB2.png RB2f.png  |  r4a_post.py cal comp.png out.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw
def sign(inp,out):
    im=Image.open(inp).convert('RGB'); a=np.asarray(im).astype(int)
    reg=a[836:864,54:94]; bg=tuple(int(v) for v in np.median(reg[(reg.sum(2)>600)],0))
    S=4; big=im.resize((576*S,1024*S),Image.LANCZOS); d=ImageDraw.Draw(big)
    d.rectangle([55*S,837*S,92*S,862*S],fill=bg); cx,cy=73*S,852*S
    d.rounded_rectangle([cx-12*S,cy-3*S,cx+8*S,cy+4*S],radius=3*S,fill=(150,105,60),outline=(70,45,25),width=S)
    d.ellipse([cx+6*S,cy-3*S,cx+10*S,cy+4*S],fill=(120,85,50),outline=(70,45,25),width=S)
    for dy in (-2,0,2): d.line([cx+10*S,cy+dy*S,cx+17*S,cy+(dy*2-3)*S],fill=(60,60,60),width=max(1,S//2))
    big.resize((576,1024),Image.LANCZOS).save(out)
def cal(inp,out):
    im=Image.open(inp).convert('RGB'); X0,Y0=1660,1240; line=(138,131,116); bg=(235,228,213)
    S=6; rx0,ry0,rx1,ry1=X0+100,Y0+64,X0+186,Y0+134
    reg=im.crop((rx0,ry0,rx1,ry1)).resize(((rx1-rx0)*S,(ry1-ry0)*S),Image.LANCZOS); d=ImageDraw.Draw(reg)
    P=lambda ox,oy: ((X0+ox-rx0)*S,(Y0+oy-ry0)*S)
    d.rectangle([*P(108.5,71.5),*P(176,127)],fill=bg)
    for gx in (131,154): d.line([P(gx,70),P(gx,128)],fill=line,width=int(2.0*S))
    for gy in (94,118): d.line([P(107,gy),P(177,gy)],fill=line,width=int(2.0*S))
    cx,cy=P(142.5,107); r=7.5*S; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(28,26,24))
    bw,bh=6*S,14*S; by=cy+2*S
    d.polygon([(cx-bw,by),(cx+bw,by),(cx,by-bh)],fill=(160,150,100),outline=(80,70,45))
    for t in (-3,0,3): d.line([cx+t*S,by-1*S,cx+t*S*0.4,by-bh*0.7],fill=(120,110,72),width=S)
    d.ellipse([cx-2.2*S,by-bh-2.2*S,cx+2.2*S,by-bh+2.2*S],fill=(225,75,40))
    im.paste(reg.resize((rx1-rx0,ry1-ry0),Image.LANCZOS),(rx0,ry0)); im.save(out)
if __name__=='__main__':
    {'sign':sign,'cal':cal}[sys.argv[1]](sys.argv[2],sys.argv[3])
