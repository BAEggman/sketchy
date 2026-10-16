"""r4b 후처리 — 鍼灸經驗方 빈 간판에 침통 그림, 李中梓 허리춤 자두 (2026-10-16)"""
import sys
from PIL import Image, ImageDraw
im=Image.open(sys.argv[1]).convert('RGB')
S=4; x0,y0,x1,y1=1700,1140,1880,1205
reg=im.crop((x0,y0,x1,y1)).resize(((x1-x0)*S,(y1-y0)*S),Image.LANCZOS); d=ImageDraw.Draw(reg)
cx,cy=(1782-x0)*S,(1172-y0)*S
d.rounded_rectangle([cx-48*S,cy-11*S,cx+28*S,cy+11*S],radius=8*S,fill=(150,105,60),outline=(60,40,22),width=2*S)
d.ellipse([cx+20*S,cy-11*S,cx+36*S,cy+11*S],fill=(122,86,50),outline=(60,40,22),width=2*S)
d.line([cx-40*S,cy-4*S,cx+16*S,cy-4*S],fill=(120,82,45),width=S)
for dy,ey in [(-6,-16),(0,-2),(6,12)]:
    d.line([cx+34*S,cy+dy*S,cx+62*S,cy+ey*S],fill=(70,70,70),width=2*S)
    d.ellipse([cx+60*S,cy+(ey-2)*S,cx+64*S,cy+(ey+2)*S],fill=(70,70,70))
im.paste(reg.resize((x1-x0,y1-y0),Image.LANCZOS),(x0,y0))
S=6; x0,y0,x1,y1=1260,950,1320,1010
reg=im.crop((x0,y0,x1,y1)).resize(((x1-x0)*S,(y1-y0)*S),Image.LANCZOS); d=ImageDraw.Draw(reg)
cx,cy=(1288-x0)*S,(980-y0)*S; r=11*S
d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(150,60,110),outline=(70,30,50),width=2*S)
d.ellipse([cx-r*0.55,cy-r*0.6,cx-r*0.15,cy-r*0.2],fill=(205,140,175))
d.line([cx,cy-r,cx+2*S,cy-r-5*S],fill=(80,60,30),width=2*S)
d.polygon([(cx+2*S,cy-r-4*S),(cx+12*S,cy-r-9*S),(cx+7*S,cy-r-1*S)],fill=(90,150,70),outline=(40,80,30))
im.paste(reg.resize((x1-x0,y1-y0),Image.LANCZOS),(x0,y0))
im.save(sys.argv[2]); print('saved',sys.argv[2])
