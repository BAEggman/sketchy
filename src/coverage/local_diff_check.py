# -*- coding: utf-8 -*-
"""옛 판본 ↔ 현재본의 '국소 최대 차이'를 잰다. 소품 하나만 바뀌어도 커진다."""
import os, re, io, json, base64, subprocess, sys
from PIL import Image
import numpy as np

REPO='/home/claude/s6repo'
PAT = re.compile(rb'<div class="panel(?: diag)?" id="([a-z0-9]+)"[^>]*>.*?data:image/webp;base64,([A-Za-z0-9+/=]+)', re.S)
N=256; B=16          # 256px, 16x16 블록 → 블록 256개

def prep(im):
    return np.asarray(im.convert('L').resize((N,N), Image.LANCZOS), dtype=np.float32)

def local_max_diff(a, b):
    # 전체 밝기/대비 차를 먼저 맞춘 뒤 블록별 평균차의 최대값
    b2 = (b - b.mean())/(b.std()+1e-6) * (a.std()+1e-6) + a.mean()
    d = np.abs(a - b2)
    blocks = d.reshape(N//B, B, N//B, B).mean(axis=(1,3))
    return float(blocks.max())

cur={}
for f in os.listdir('images'):
    cur[f.rsplit('.',1)[0]] = prep(Image.open('images/'+f))

shas = subprocess.run(['git','log','--all','--format=%H','--','index.html'],
                      cwd=REPO, capture_output=True, text=True).stdout.split()
res={}
for sha in shas:
    blob = subprocess.run(['git','cat-file','-p', sha+':index.html'], cwd=REPO, capture_output=True).stdout
    for m in PAT.finditer(blob):
        pid=m.group(1).decode()
        if pid not in cur: continue
        raw=base64.b64decode(m.group(2))
        try: im=Image.open(io.BytesIO(raw)); im.load()
        except Exception: continue
        d = local_max_diff(cur[pid], prep(im))
        res.setdefault(pid, []).append({'sha':sha[:7],'w':im.width,'bytes':len(raw),'d':round(d,1)})
json.dump(res, open('coverage/local_diff.json','w'), ensure_ascii=False)

# 검증: 재작도가 확실한 판들의 옛 판본 d 값
b4=set(json.load(open('coverage/blind4_map.json')).values())
print("=== 재작도 확정 판의 '옛 판본' 최소 d (이 값보다 낮으면 통과시키면 안 됨)")
mins=[]
for pid in sorted(b4):
    old=[x for x in res.get(pid,[]) if x['sha'] not in ('89c00e0',)]
    if not old: continue
    m=min(x['d'] for x in old); mins.append((m,pid))
    print(f"  {pid}  최소 d={m:5.1f}")
print("\n재작도판 옛본 d 의 최솟값 =", round(min(m for m,_ in mins),1))
