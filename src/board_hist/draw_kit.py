# PIL 덧그리기 도구 — 국소 패치를 SS배로 키워 그린 뒤 줄여 붙인다(앤티앨리어싱)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math
SS=4
def catmull(pts, n=16):
    P=[pts[0]]+list(pts)+[pts[-1]]; out=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for t in [k/n for k in range(n)]:
            t2,t3=t*t,t*t*t
            out.append(tuple(0.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3) for j in range(2)))
    out.append(pts[-1]); return out
class Patch:
    def __init__(self, im, box):
        self.im=im; self.box=box; x0,y0,x1,y1=box
        self.big=im.crop(box).resize(((x1-x0)*SS,(y1-y0)*SS),Image.LANCZOS).convert('RGBA')
        self.layer=Image.new('RGBA',self.big.size,(0,0,0,0)); self.d=ImageDraw.Draw(self.layer)
    def P(self,p): return ((p[0]-self.box[0])*SS,(p[1]-self.box[1])*SS)
    def line(self,pts,w,col,smooth=True):
        q=[self.P(p) for p in (catmull(pts) if smooth and len(pts)>2 else pts)]
        self.d.line(q,fill=col,width=max(1,int(w*SS)),joint='curve')
        r=w*SS/2
        for e in (q[0],q[-1]): self.d.ellipse([e[0]-r,e[1]-r,e[0]+r,e[1]+r],fill=col)
    def ellipse(self,c,rx,ry,fill,outline=None,ow=1):
        cx,cy=self.P(c); self.d.ellipse([cx-rx*SS,cy-ry*SS,cx+rx*SS,cy+ry*SS],fill=fill,outline=outline,width=int(ow*SS))
    def polygon(self,pts,fill,outline=None,ow=1,smooth=True):
        q=[self.P(p) for p in (catmull(pts+[pts[0]]) if smooth else pts)]
        self.d.polygon(q,fill=fill)
        if outline: self.d.line(q+[q[0]],fill=outline,width=int(ow*SS),joint='curve')
    def commit(self, blur=0):
        lay=self.layer
        if blur: lay=lay.filter(ImageFilter.GaussianBlur(blur*SS))
        out=Image.alpha_composite(self.big,lay).convert('RGB')
        x0,y0,x1,y1=self.box
        small=out.resize((x1-x0,y1-y0),Image.LANCZOS)
        self.im.paste(small,(x0,y0))
        self.layer=Image.new('RGBA',self.big.size,(0,0,0,0)); self.d=ImageDraw.Draw(self.layer)
        self.big=out.convert('RGBA')
def liquid(pt, pts, w=2.2, bead=None):
    # 맑은 액체 줄기: 바깥 회청 윤곽 → 안쪽 옅은 하늘빛 → 흰 반짝임
    pt.line(pts, w+1.4, (95,120,140,230))
    pt.line(pts, w, (205,228,240,255))
    hl=[(x-0.5,y) for x,y in pts]
    pt.line(hl, max(0.7,w*0.35), (255,255,255,255))
    if bead:
        c=pts[-1]; r=bead
        pt.ellipse((c[0],c[1]+r*0.6), r+0.7, r*1.15+0.7, (95,120,140,230))
        pt.ellipse((c[0],c[1]+r*0.6), r, r*1.15, (205,228,240,255))
        pt.ellipse((c[0]-r*0.35,c[1]+r*0.25), r*0.3, r*0.3, (255,255,255,255))
def flame(pt, base, h, w, lean=0.0):
    bx,by=base
    def tongue(scale,col):
        hh=h*scale; ww=w*scale
        pts=[(bx-ww/2,by),(bx-ww*0.45,by-hh*0.35),(bx-ww*0.2+lean*hh*0.3,by-hh*0.7),(bx+lean*hh,by-hh),(bx+ww*0.25+lean*hh*0.3,by-hh*0.62),(bx+ww*0.45,by-hh*0.3),(bx+ww/2,by)]
        return pts
    pt.polygon(tongue(1.0,None),(214,72,38,255),outline=(110,40,20,255),ow=1.1)
    pt.polygon(tongue(0.7,None),(240,140,50,255))
    pt.polygon(tongue(0.42,None),(250,215,110,255))
def snowflake(pt, c, r):
    cx,cy=c
    for k in range(3):
        a=math.pi/3*k+0.3
        p1=(cx+r*math.cos(a),cy+r*math.sin(a)); p2=(cx-r*math.cos(a),cy-r*math.sin(a))
        pt.line([p1,p2],1.9,(120,135,150,255),smooth=False)
    for k in range(3):
        a=math.pi/3*k+0.3
        p1=(cx+r*math.cos(a),cy+r*math.sin(a)); p2=(cx-r*math.cos(a),cy-r*math.sin(a))
        pt.line([p1,p2],1.0,(255,255,255,255),smooth=False)
def taper(pt, pts, r0, r1, bead=0, edge=(70,105,130,200), fill=(190,222,238,215), hl=(255,255,255,235)):
    path=catmull(pts, 24); n=len(path)
    rs=[r0+(r1-r0)*(i/(n-1)) for i in range(n)]
    for (x,y),r in zip(path,rs): pt.ellipse((x,y), r+0.55, r+0.55, edge)
    if bead:
        c=path[-1]; pt.ellipse((c[0],c[1]+bead*0.5), bead+0.55, bead*1.2+0.55, edge)
    for (x,y),r in zip(path,rs): pt.ellipse((x,y), r, r, fill)
    if bead:
        c=path[-1]; pt.ellipse((c[0],c[1]+bead*0.5), bead, bead*1.2, fill)
        pt.ellipse((c[0]-bead*0.35,c[1]+bead*0.2), bead*0.32, bead*0.32, hl)
    for (x,y),r in list(zip(path,rs))[2:-3:2]: pt.ellipse((x-r*0.4,y), r*0.28, r*0.28, hl)
