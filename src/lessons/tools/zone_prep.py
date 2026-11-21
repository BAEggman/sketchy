# -*- coding: utf-8 -*-
"""구역 조각 준비: 심사 final.json의 crop을 Gemini가 받는 비율(1:1 · 3:4 · 4:3 · 9:16 · 16:9) 중 가까운 것으로 넓히고,
region 상자를 넓힌 조각 좌표로 옮긴다. python3 -I zone_prep.py CUR.png final.json EID OUTDIR → OUTDIR/EID.jpg, EID.json"""
import sys, json
from PIL import Image
R = {'1:1': 1.0, '3:4': 3/4, '4:3': 4/3, '9:16': 9/16, '16:9': 16/9}
cur, fj, eid, od = sys.argv[1:5]
B = Image.open(cur).convert('RGB'); W, H = B.size
e = [x for x in json.load(open(fj, encoding='utf-8'))['edits'] if x['id'] == eid][0]
x, y, w, h = e['crop']
name, r = min(R.items(), key=lambda kv: abs(__import__('math').log((w / h) / kv[1])))
if w / h < r: nw, nh = round(h * r), h
else: nw, nh = w, round(w / r)
nw, nh = min(nw, W), min(nh, H)
nx = min(max(0, x - (nw - w) // 2), W - nw); ny = min(max(0, y - (nh - h) // 2), H - nh)
B.crop((nx, ny, nx + nw, ny + nh)).save(f'{od}/{eid}.jpg', quality=93)
regs = [[rx + x - nx, ry + y - ny, rw, rh] for rx, ry, rw, rh in e.get('region') or []]
json.dump({'eid': eid, 'aspect': name, 'crop': [nx, ny, nw, nh], 'region': regs, 'prompt_en': e['prompt_en']},
          open(f'{od}/{eid}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(eid, name, [nx, ny, nw, nh], 'regions', len(regs))
