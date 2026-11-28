"""src/tables/tables.json + tables-template.html + tables.js → tables.html (표에서 연습, 오프라인 한 파일)

가 선 ②(2026-11-28): 한 정거장에 사실이 너무 많은 7과의 표 내용을 옮긴 곳. 과 정거장의 「table」 칸이 여기 #<표 id>로 잇는다.
    python3 src/tables/build_tables.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
data = json.loads((HERE / 'tables.json').read_text(encoding='utf-8'))
ids = [t['id'] for t in data['tables']]
assert len(ids) == len(set(ids)), '표 id가 겹친다'
lessons = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in (ROOT / 'src/lessons/l').glob('*.json')}
for t in data['tables']:
    assert t['lesson'] in lessons, f"{t['id']}: 없는 과 {t['lesson']}"
    ns = {s['n'] for s in lessons[t['lesson']]['stations']}
    for r in t['rows']:
        assert len(r['c']) == len(t['cols']), f"{t['id']}: 칸 수가 머리와 다르다 — {r['c']}"
        assert set(r['st']) <= ns, f"{t['id']}: 없는 정거장 {r['st']}"
# 과 쪽 「table」 칸이 가리키는 표가 있는지
for lid, L in lessons.items():
    for s in L['stations']:
        tb = s.get('table')
        if tb:
            assert tb['id'] in ids, f"{lid}#{s['n']}: 없는 표 {tb['id']}"
template = (HERE / 'tables-template.html').read_text(encoding='utf-8')
script = (HERE / 'tables.js').read_text(encoding='utf-8')
assert '</script' not in script.lower()
page = (template
        .replace('__TABLES_SCRIPT__', script)
        .replace('__TABLES_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))
(ROOT / 'tables.html').write_text(page, encoding='utf-8')
n_cells = sum(len(r['c']) - sum(1 for c in t['cols'] if c.get('key')) for t in data['tables'] for r in t['rows'])
print(f'written tables.html — 표 {len(ids)} · 과 {len({t["lesson"] for t in data["tables"]})} · 가릴 칸 {n_cells} ({len(page.encode())} bytes)')
