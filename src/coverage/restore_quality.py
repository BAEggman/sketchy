# -*- coding: utf-8 -*-
"""판마다 '내용이 같은(d<=8)' 리비전 중 최고 화질본을 골라 images_best/ 에 모은다."""
import os, re, io, json, base64, subprocess, shutil
from PIL import Image

REPO='/home/claude/s6repo'
PAT = re.compile(rb'<div class="panel(?: diag)?" id="([a-z0-9]+)"[^>]*>.*?data:image/webp;base64,([A-Za-z0-9+/=]+)', re.S)
diff = json.load(open('coverage/local_diff.json'))

pick = {}
for pid, cands in diff.items():
    ok = [c for c in cands if c['d'] <= 8]
    if not ok: continue
    ok.sort(key=lambda c: (c['w'], c['bytes']))
    pick[pid] = ok[-1]

need = {}
for pid, c in pick.items(): need.setdefault(c['sha'], []).append(pid)

shutil.rmtree('images_best', ignore_errors=True); os.makedirs('images_best')
cur = {f.rsplit('.',1)[0]: f for f in os.listdir('images')}
report = {}

for sha, pids in need.items():
    full = subprocess.run(['git','rev-parse', sha], cwd=REPO, capture_output=True, text=True).stdout.strip()
    blob = subprocess.run(['git','cat-file','-p', full+':index.html'], cwd=REPO, capture_output=True).stdout
    want = set(pids)
    for m in PAT.finditer(blob):
        pid = m.group(1).decode()
        if pid not in want: continue
        raw = base64.b64decode(m.group(2))
        curf = cur[pid]; curp = 'images/'+curf; cursz = os.path.getsize(curp)
        # 방금 재작도한 png 이거나 현재본이 더 크면 현재본 유지
        if curf.endswith('.png') or cursz >= len(raw):
            shutil.copy(curp, 'images_best/'+curf)
            report[pid] = {'src':'current','w':Image.open(curp).width,'bytes':cursz,'upgraded':False}
        else:
            open(f'images_best/{pid}.webp','wb').write(raw)
            report[pid] = {'src':sha,'w':pick[pid]['w'],'bytes':len(raw),'d':pick[pid]['d'],'upgraded':True}
        want.discard(pid)

for pid, f in cur.items():
    if pid not in report:
        shutil.copy('images/'+f, 'images_best/'+f)
        report[pid] = {'src':'current','w':Image.open('images/'+f).width,'bytes':os.path.getsize('images/'+f),'upgraded':False}

json.dump(report, open('coverage/quality_restore.json','w'), ensure_ascii=False, indent=1)
up = [p for p,v in report.items() if v['upgraded']]
tot = sum(v['bytes'] for v in report.values())
print(f"판 {len(report)} | 화질 상향 {len(up)} | 총 이미지 {tot:,} 바이트")
from collections import Counter
print("해상도:", dict(Counter(v['w'] for v in report.values())))
