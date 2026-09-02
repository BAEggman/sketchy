# -*- coding: utf-8 -*-
"""git 전 이력의 index.html 에서 판마다 '가장 화질 좋은' webp 를 골라 모은다.
품질 기준: ① 픽셀 폭이 큰 것 ② 같은 폭이면 바이트가 큰 것(=재인코딩 세대가 적음).
"""
import os, re, base64, subprocess, io, json, shutil
from PIL import Image

REPO = '/home/claude/s6repo'
OUT  = '/home/claude/s6/work/images_best'
os.makedirs(OUT, exist_ok=True)

shas = subprocess.run(['git','log','--all','--format=%H','--','index.html'],
                      cwd=REPO, capture_output=True, text=True).stdout.split()
print(len(shas), '개 리비전')

PAT = re.compile(rb'<div class="panel(?: diag)?" id="([a-z0-9]+)"[^>]*>.*?data:image/webp;base64,([A-Za-z0-9+/=]+)', re.S)

best = {}   # pid -> (width, nbytes, sha)
for sha in shas:
    blob = subprocess.run(['git','cat-file','-p', sha+':index.html'],
                          cwd=REPO, capture_output=True).stdout
    n = 0
    for m in PAT.finditer(blob):
        pid = m.group(1).decode()
        raw = base64.b64decode(m.group(2))
        try:
            w = Image.open(io.BytesIO(raw)).width
        except Exception:
            continue
        key = (w, len(raw))
        n += 1
        if pid not in best or key > best[pid][:2]:
            best[pid] = (w, len(raw), sha[:7])
            open(os.path.join(OUT, pid + '.webp'), 'wb').write(raw)
    print(f'  {sha[:7]}  {n:3d}판')

json.dump({k: {'w': v[0], 'bytes': v[1], 'from': v[2]} for k, v in best.items()},
          open('coverage/best_images.json','w'), ensure_ascii=False, indent=1)
print('\n판 수:', len(best))
print('총 바이트:', sum(v[1] for v in best.values()))
