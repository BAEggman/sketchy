# 과 하나를 마무리하는 공용 도구 — 캡처 저장 · 상자 · 과 JSON · 카드 대조 · 검사 목록 · 덧그림 · 음성 대본
import json, os, glob, subprocess, sys
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/'
R='/home/claude/s7/work/src/lessons/'
IMG='/home/claude/s7/work/images/lessons/'
F=1.4413
def bx(a,b,c,d):
    x,y,w,h=round(a*F),round(b*F),round((c-a)*F),round((d-b)*F)
    x=max(0,x);y=max(0,y);w=min(w,2048-x);h=min(h,1144-y);return [x,y,w,h]
def latest():
    fs=sorted(glob.glob('/tmp/claude-chrome-screenshots-*/screenshot-*.png'),key=os.path.getmtime);return fs[-1]
def shot(lid,v,src=None,final=True,crops=None):
    """캡처(1456×828)를 잘라 2048×1144로 — design/<id>/base_v<v>.webp, 스크래치 PNG, (final이면) images/lessons"""
    src=src or latest(); os.makedirs(R+'design/'+lid,exist_ok=True); os.makedirs(SP+lid,exist_ok=True)
    c=Image.open(src).crop((0,0,1421,793)).resize((2048,1144),Image.LANCZOS)
    c.save(R+f'design/{lid}/base_v{v}.webp',quality=80); c.save(SP+f'{lid}/v{v}.png')
    if final: c.save(IMG+lid+'.webp',quality=82); c.save(SP+f'{lid}/final.png')
    for name,(x0,y0,x1,y1),z in (crops or []):
        c.crop((x0,y0,x1,y1)).resize((int((x1-x0)*z),int((y1-y0)*z))).save(SP+f'{lid}/{name}.png')
    print('saved',lid,'v',v,os.path.basename(src))
def use(lid,v):
    c=Image.open(SP+f'{lid}/v{v}.png'); c.save(IMG+lid+'.webp',quality=82); c.save(SP+f'{lid}/final.png'); print('final =',v)
def finish(lid,title,place,S,show=True,tts=True):
    for s in S: assert len(s['fact'])<=60,(s['n'],len(s['fact']),s['fact'])
    assert [s['n'] for s in S]==list(range(len(S))), 'n 순서'
    out=dict(id=lid,title=title,place=place,image=f'images/lessons/{lid}.webp',w=2048,h=1144,stations=S)
    json.dump(out,open(R+f'l/{lid}.json','w'),ensure_ascii=False,indent=1)
    M=json.load(open(R+'lesson_map.json'));L={l['id']:l for l in M['lessons']}
    need=set(c for st in L[lid]['stations'] for c in st['cards']); have=[c for s in S for c in s['src']]
    print(lid,'정거장',len(S),'| 지도',L[lid]['n_stations'],'| 카드',len(need),'| missing',sorted(need-set(have)),'extra',sorted(set(have)-need),'dups',sorted(set(c for c in have if have.count(c)>1)))
    d=R+'design/'+lid
    json.dump({str(s['n']):s['box'] for s in S if s['box']},open(d+'/boxes.json','w'),ensure_ascii=False,indent=1)
    with open(d+'/check_list.md','w') as fo:
        fo.write(f'# {lid} 일치 검사 묘사 목록 (그림: images/lessons/{lid}.webp, 2048×1144)\n\n')
        for s in S:
            if s['box']: fo.write(f"{s['n']}. {s['obj']} — 자리(2048×1144 기준 상자): {s['box']}\n")
    if os.path.exists(SP+f'{lid}/final.png'):
        im=Image.open(SP+f'{lid}/final.png').convert('RGB');dr=ImageDraw.Draw(im)
        cols=['red','blue','magenta','orange','cyan','lime','purple','black','white','brown','pink','navy','yellow','green']
        for i,s in enumerate(S):
            b=s['box']
            if not b: continue
            for x,y,w,h in (b if isinstance(b[0],list) else [b]):
                dr.rectangle([x,y,x+w,y+h],outline=cols[i%len(cols)],width=5);dr.text((x+8,y+8),str(s['n']),fill=cols[i%len(cols)])
        im.resize((1280,715)).save(SP+f'{lid}/overlay.png')
    if tts:
        r=subprocess.run(['node','make_tts.js','/home/claude/ext/qoaq/한의학_인출훈련_학습과학.html',R+f'l/{lid}.json'],cwd='/home/claude/s7/jsd',capture_output=True,text=True)
        print(r.stdout.strip(), r.stderr.strip()[:300])
        if show:
            for s in json.load(open(R+f'l/{lid}.json'))['stations']: print(s['n'],s['tts'])
def reserve(rows):
    p=R+'reserved.md'; s=open(p).read(); k='\n## 피할 것'; assert s.count(k)==1
    open(p,'w').write(s.replace(k, rows.strip('\n')+'\n'+k,1))
def commit(msg):
    w='/home/claude/s7/work'
    subprocess.run(['cp',R+'tools/make_tts.js','/home/claude/s7/jsd/make_tts.js'])
    r=subprocess.run(['python3','src/lessons/build_player.py'],cwd=w,capture_output=True,text=True); print(r.stdout.strip().splitlines()[-3:])
    subprocess.run(['git','add','-A','src/lessons','images/lessons','lessons.html'],cwd=w)
    full=msg.rstrip()+'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01H8LcZK4WVLkMjSUBUXBg6J\n'
    r=subprocess.run(['git','commit','-q','-m',full],cwd=w,capture_output=True,text=True); print(r.stdout[-200:],r.stderr[-200:])
    print(subprocess.run(['git','log','--oneline','-1'],cwd=w,capture_output=True,text=True).stdout.strip())

# ── 덧그림: 괘 획(세 줄)과 점 타일을 코드로 정확히 그려 넣는다 (Gemini는 획·개수를 못 맞춘다)
GUA={'乾':(1,1,1),'兌':(1,1,0),'離':(1,0,1),'震':(1,0,0),'巽':(0,1,1),'坎':(0,1,0),'艮':(0,0,1),'坤':(0,0,0)}  # 아래→위, 1=이어짐
DOTS={1:[(0,0)],2:[(-1,-1),(1,1)],3:[(-1,-1),(0,0),(1,1)],4:[(-1,-1),(1,-1),(-1,1),(1,1)],5:[(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],
 6:[(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)],7:[(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1),(0,0)],8:[(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1),(0,-1),(0,1)]}
def overlay(lid,vin,vout,grams=(),tiles=(),gw=60,bar=11,gap=6.5,ts=92,final=True):
    """grams: [(cx,cy,'乾')] · tiles: [(cx,cy,n)] — 좌표는 2048×1144. 2배로 그려 줄여 붙인다."""
    base=Image.open(SP+f'{lid}/v{vin}.png').convert('RGBA'); K=2
    lay=Image.new('RGBA',(base.width*K,base.height*K),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for cx,cy,g in grams:
        h=3*bar+2*gap
        for i,solid in enumerate(GUA[g]):            # i=0 맨 아래
            y1=cy+h/2-i*(bar+gap); y0=y1-bar
            if solid: d.rectangle([(cx-gw/2)*K,y0*K,(cx+gw/2)*K,y1*K],fill=(22,18,14,255))
            else:
                s=gw*0.4
                d.rectangle([(cx-gw/2)*K,y0*K,(cx-gw/2+s)*K,y1*K],fill=(22,18,14,255))
                d.rectangle([(cx+gw/2-s)*K,y0*K,(cx+gw/2)*K,y1*K],fill=(22,18,14,255))
    for cx,cy,n in tiles:
        r=ts/2
        d.rounded_rectangle([(cx-r)*K,(cy-r)*K,(cx+r)*K,(cy+r)*K],radius=14*K,fill=(253,252,246,255),outline=(22,18,14,255),width=5*K)
        for dx,dy in DOTS[n]:
            x=cx+dx*ts*0.27; y=cy+dy*ts*0.27; q=ts*0.095
            d.ellipse([(x-q)*K,(y-q)*K,(x+q)*K,(y+q)*K],fill=(22,18,14,255))
    lay=lay.resize(base.size,Image.LANCZOS); c=Image.alpha_composite(base,lay).convert('RGB')
    c.save(R+f'design/{lid}/base_v{vout}.webp',quality=80); c.save(SP+f'{lid}/v{vout}.png')
    if final: c.save(IMG+lid+'.webp',quality=82); c.save(SP+f'{lid}/final.png')
    print('overlay',lid,'v',vin,'->',vout)
