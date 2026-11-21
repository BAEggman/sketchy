#!/usr/bin/env python3
"""포제 장면 명세 도구.
  python3 spec_tools.py boxes Pxx   → runs/20261122-p3-suchi/built/Pxx_boxes.jpg (상자 번호 그림)
  python3 spec_tools.py check Pxx…  → 명세 검사(OK/FAIL)
명세: runs/20261122-p3-suchi/built/Pxx.spec.json"""
import json,re,sys
from PIL import Image, ImageDraw, ImageFont
R='/home/claude/work/runs/20261122-p3-suchi/'
W,H=2752,1536
C=[(230,25,75),(60,180,75),(0,130,200),(245,130,48),(145,30,180),(240,50,230),(0,0,0),(128,0,0),(0,128,128)]
def load(p): return json.load(open(R+'built/%s.spec.json'%p,encoding='utf-8'))
def boxes(p):
    S=load(p); im=Image.open(R+'scenes/%s.jpeg'%p).convert('RGB'); d=ImageDraw.Draw(im)
    try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',60)
    except Exception: f=None
    for s in S['stations']:
        b=s.get('box')
        if not b: continue
        c=C[s['n']%len(C)]
        d.rectangle([b[0],b[1],b[0]+b[2],b[1]+b[3]],outline=c,width=10)
        d.rectangle([b[0]+10,b[1]+10,b[0]+90,b[1]+85],fill=c); d.text((b[0]+25,b[1]+15),str(s['n']),fill=(255,255,255),font=f)
    im.resize((1376,768)).save(R+'built/%s_boxes.jpg'%p,quality=85); print('saved',R+'built/%s_boxes.jpg'%p)
def check(ps):
    ok=True
    for p in ps:
        S=load(p)
        for k in ('title','place','run','stations','questions','trainer'):
            if k not in S: ok=False; print(p,'missing',k)
        if len(S.get('questions',[]))!=5: ok=False; print(p,'questions != 5')
        ns=[s['n'] for s in S['stations']]
        if ns!=list(range(len(ns))): ok=False; print(p,'n not 0..',ns)
        if S['stations'][0].get('kind')!='frame' or S['stations'][-1].get('kind')!='review': ok=False; print(p,'first frame / last review needed')
        for s in S['stations']:
            for k in ('obj','fact','hook','say','tts','src'):
                if not s.get(k): ok=False; print(p,s['n'],'empty',k)
            bad=re.sub(r'[가-힣\s.,?!·]','',s.get('tts',''))
            if bad: ok=False; print(p,s['n'],'tts 한글 아닌 글자:',repr(bad))
            if len(s.get('fact',''))>90: ok=False; print(p,s['n'],'fact 길이',len(s['fact']))
            b=s.get('box')
            if s.get('kind') in ('frame','review'):
                if b is not None: ok=False; print(p,s['n'],'frame/review box는 null')
            elif not(b and b[0]>=0 and b[1]>=0 and b[0]+b[2]<=W and b[1]+b[3]<=H and min(b[2],b[3])>=240):
                ok=False; print(p,s['n'],'box 잘못',b)
    print('OK' if ok else 'FAIL')
if __name__=='__main__':
    if sys.argv[1]=='boxes': boxes(sys.argv[2])
    else: check(sys.argv[2:])
