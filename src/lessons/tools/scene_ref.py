#!/usr/bin/env python3
"""장면 참조판: python3 scene_ref.py P07 [run(기본 20261122-p3-suchi)] → /home/claude/zt/scene/P07_ref.jpg, P07_prompt.txt
스티커(images/herbs/Hxxx.webp)를 장면 순서(왼→오)대로 한 줄로 붙인 참조 그림 + 보낼 프롬프트.
스티커가 없으면 MISSING을 찍고 끝낸다."""
import json,sys,os
from PIL import Image
ROOT='/home/claude/work'; OUT='/home/claude/zt/scene'
pid=sys.argv[1]
RUN=sys.argv[2] if len(sys.argv)>2 else '20261122-p3-suchi'
job={x['id']:x for x in json.load(open(f'{ROOT}/runs/{RUN}/scene_jobs.json'))}[pid]
sh={x['id']:x for x in json.load(open(f'{ROOT}/runs/{RUN}/merged.json'))['sheets']}[pid]
seen=[];[seen.append(h) for h in job['stickers'] if h not in seen]
miss=[h for h in seen if not os.path.exists(f'{ROOT}/images/herbs/{h}.webp')]
if miss: print('MISSING',' '.join(miss)); sys.exit(1)
S=400; ref=Image.new('RGB',(S*len(seen)+20*(len(seen)+1),S+40),'white')
for i,h in enumerate(seen):
    im=Image.open(f'{ROOT}/images/herbs/{h}.webp').convert('RGB'); im.thumbnail((S,S))
    ref.paste(im,(20+i*(S+20)+(S-im.width)//2,20+(S-im.height)//2))
os.makedirs(OUT,exist_ok=True); ref.save(f'{OUT}/{pid}_ref.jpg',quality=90)
pre=("Use the attached reference image only as a character design sheet: it shows "+str(len(seen))+
 " cartoon characters from left to right. Every one of these characters must appear in the new picture with exactly the same "
 "shape, colors, outfit and props as in the reference (do not redesign them, do not change their colors). "
 "Do not copy the reference layout or its white background. Draw this new scene:\n\n")
open(f'{OUT}/{pid}_prompt.txt','w').write(pre+sh['prompt_en'])
print('OK',pid,len(seen),'stickers',f'{OUT}/{pid}_ref.jpg')
