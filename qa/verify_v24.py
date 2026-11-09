"""v2.4: preserve the user's old panels, verify new coverage and countable diagrams."""
import collections
import html
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from reading import CJK, READINGS, fact_html

BASE = 'bd0e22619d976e1b1d529aed60a8da31ba29a816'
def previous(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
def read(path):
    return json.loads((ROOT / path).read_text())

before = json.loads(previous('src/panels/library.json'))
lib = read('src/panels/library.json')
added = read('src/panels/yinyang-v2.4.json')
panels = {p['id']: p for p in lib['panels']}
assert len(panels) == len(lib['panels']) == 79
# 2026-11-09: s18d07 熱格 문항 정정(火를 瀉하는 세 경 = 大腸·心·三焦) — 비교 전에 되돌려 본다
assert json.loads(json.dumps(lib['panels'][:58], ensure_ascii=False).replace('세 경(大腸·心·三焦)이 火를', '세 경(脾·胃·心包)이 火를')) == before['panels'], 'Original panel changed'
for key in before.keys() - {'panels', 'release'}:
    assert lib[key] == before[key], key
assert lib['panels'][58:] == added
assert len(added) == 21
assert sum(len(p['rows']) for p in added) == 127
assert sum(len(p['quiz']) for p in added) == 132
assert {a for p in added for a in p['audit_ids']} == {f'A{i:02}' for i in range(1, 16)} | {'B04', 'B05'}
old_readings = json.loads(previous('src/panels/readings.json'))
assert all(READINGS[k] == v for k, v in old_readings.items()), 'Existing reading changed'
assert (ROOT / 'recall.html').read_bytes() == previous('recall.html')
assert not subprocess.check_output(['git', 'diff', BASE, '--', 'images/*.webp', 'images/*.png'], cwd=ROOT)

scene_ids = [pid for scene in read('src/panels/scenes.json')['scenes'] for pid in scene['ids']]
assert collections.Counter(scene_ids) == collections.Counter(panels.keys())
for p in added:
    assert all(r['fact'] in [q['a'] for q in p['quiz']] for r in p['rows']), p['id']
    assert p['source_notes'] and p['diagram']['labels']
    ET.parse(ROOT / p['image'])
    for text in [r['fact'] for r in p['rows']] + [q['a'] for q in p['quiz']]:
        assert set(CJK.findall(text)) <= READINGS.keys()
        restored = re.sub(r'<span class="reading">.*?</span>', '', fact_html(text))
        assert html.unescape(restored.replace('<br>', '\n')) == text
    for row in p.get('diagram', {}).get('matrix', []):
        assert len(row) == 6

# Each season is independently derived from the five-phase generation/control cycles.
elements = ['목', '화', '토', '금', '수']
for i, row in enumerate(panels['s09x09']['diagram']['matrix'][1:]):
    assert row[1:] == [elements[j % 5] for j in (i, i+1, i-1, i-2, i+2)], row

# Count the actual SVG marks, rather than relying on printed numbers.
he = ET.parse(ROOT / panels['s10x01']['image'])
for attr, last in [('data-hetu', 10), ('data-luoshu', 9)]:
    count = collections.Counter(int(e.attrib[attr]) for e in he.iter() if attr in e.attrib)
    assert count == {n: n for n in range(1, last+1)}, count
    for e in he.iter():
        if attr in e.attrib:
            assert (e.attrib['fill'] == '#fff') == (int(e.attrib[attr]) % 2 == 1)
count = collections.Counter(int(e.attrib['data-number']) for e in ET.parse(ROOT / panels['s09x08']['image']).iter() if 'data-number' in e.attrib)
assert count == {n: n for n in range(1, 11)}
grid = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
assert all(sum(line) == 15 for line in grid + list(zip(*grid)) + [[grid[i][i] for i in range(3)], [grid[i][2-i] for i in range(3)]])
assert '무역초시소극248' in panels['s09x03']['study_note']
assert '신수 → 심화' in panels['s09x10']['rows'][2]['fact']
assert '폐금 → 심화' in panels['s09x10']['rows'][3]['fact']
for han, kor in {'說言乎兌': '열언호태', '勞乎坎': '노호감', '徵': '치'}.items():
    assert READINGS[han] == kor

index = (ROOT / 'index.html').read_text()
assert index.count('class="figure-toggle"') == 21
assert index.count('class="practice-link"') == 21
assert '/Users/mac/' not in index and 'CloudStorage' not in index
for p in added:
    assert f'id="{p["id"]}"' in index
    assert f'id="quiz-{p["id"]}"' in index
    assert f'src="{p["image"]}"' in index
print('PASS: 58 original panels and all original images/readings preserved')
print('PASS: 17 audit topics / 21 new diagrams / 127 facts / 132 questions')
print('PASS: scene links, Korean readings, season relationships, dot counts, direction anchors')
