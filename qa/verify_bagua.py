"""Verify direction facts, trigram strokes, embedded data, and preservation."""
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'src/panels/bagua-memory.json').read_text())
expected={
 'early':{'N':'곤','NE':'진','E':'리','SE':'태','S':'건','SW':'손','W':'감','NW':'간'},
 'late':{'N':'감','NE':'간','E':'진','SE':'손','S':'리','SW':'곤','W':'태','NW':'건'}
}
strokes={'건':[1,1,1],'태':[0,1,1],'리':[1,0,1],'진':[0,0,1],
         '손':[1,1,0],'감':[0,1,0],'간':[1,0,0],'곤':[0,0,0]}
for system,positions in expected.items():
 assert data['systems'][system]['positions']==positions
 assert set(positions.values())==set(strokes)
 # Each direction is included exactly once in the four mnemonic groups.
 assert sorted(d for g in data['systems'][system]['groups'] for d in g['directions'])==sorted(positions)
for name,lines in strokes.items():assert data['trigrams'][name]['lines']==lines
for a,b in [('건','곤'),('리','감'),('태','간'),('진','손')]:
 assert all(x!=y for x,y in zip(strokes[a],strokes[b]))
page=(ROOT/'bagua.html').read_text()
embedded=re.search(r'<script id="bagua-data" type="application/json">(.*?)</script>',page,re.S).group(1)
assert json.loads(embedded)==data
assert (ROOT/'src/bagua.js').read_text() in page
assert not re.search(r'<script[^>]+src=',page), 'Page must work without network dependencies'
assert '/Users/' not in page and '__BAGUA_' not in page
for element_id in ['board','bank','selection','practice-controls','mode','orientation','grade','reset','result']:
 assert page.count(f'id="{element_id}"')==1,element_id
baseline='v2.4-yinyang-20261106'
previous=json.loads(subprocess.check_output(['git','show',baseline+':src/panels/library.json'],cwd=ROOT))
current=json.loads((ROOT/'src/panels/library.json').read_text())
# 2026-11-09: s18d07 熱格 문항 정정(火를 瀉하는 세 경 = 大腸·心·三焦) — 비교 전에 되돌려 본다
assert json.loads(json.dumps(current['panels'], ensure_ascii=False).replace('세 경(大腸·心·三焦)이 火를', '세 경(脾·胃·心包)이 火를'))==previous['panels']
assert not subprocess.check_output(['git','diff',baseline,'--','images/','src/panels/readings.json','recall.html'],cwd=ROOT)
assert (ROOT/'index.html').read_text().count('href="bagua.html"')==2
print('PASS: 16 directions / 8 trigram patterns / 4 opposite pairs / offline page / 79 existing panels preserved')
