import json
from PIL import Image, ImageDraw, ImageFont
R='/home/claude/work/runs/20261121-p3-b1/built/'
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',60)
except: f=None
C=[(230,25,75),(60,180,75),(0,130,200),(245,130,48),(145,30,180),(240,50,230),(0,0,0),(128,0,0),(0,128,128)]
import sys
for lid in (sys.argv[1:] or ['hist-04','hist-05a','hist-05b']):
    S=json.load(open(R+lid+'.spec.json',encoding='utf-8'))
    im=Image.open('/home/claude/zt/job/%s/cur.png'%lid).convert('RGB'); d=ImageDraw.Draw(im)
    for s in S['stations']:
        b=s['box']
        if not b: continue
        c=C[s['n']%len(C)]
        d.rectangle([b[0],b[1],b[0]+b[2],b[1]+b[3]],outline=c,width=10)
        d.rectangle([b[0]+10,b[1]+10,b[0]+90,b[1]+85],fill=c); d.text((b[0]+25,b[1]+15),str(s['n']),fill=(255,255,255),font=f)
    im.resize((1376,768),Image.LANCZOS).save(R+lid+'_boxes.jpg',quality=85)
