"""배포 산출물의 사실 보존·독음·그림 연결 회귀 검사. 저장소 루트에서 실행."""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from reading import CJK, READINGS, fact_html

BASE = '893de62e9600985db33d0b35633e9a62258443c5'
lib = json.loads((ROOT / 'src/panels/library.json').read_text())
old = json.loads(subprocess.check_output(['git', 'show', BASE + ':src/panels/library.json'], cwd=ROOT))
original_ids = {p['id'] for p in old['panels']}
original_panels = [p for p in lib['panels'] if p['id'] in original_ids]
assert [p['id'] for p in original_panels] == [p['id'] for p in old['panels']]
assert len(original_panels) == 58
assert sum(len(p['rows']) for p in original_panels) == 613
assert sum(len(p.get('quiz', [])) for p in original_panels) == 335
changed_facts = []
terms = set()
for p, before in zip(original_panels, old['panels']):
    # 2026-11-09: s18d07 熱格 문항 정정(火를 瀉하는 세 경 = 大腸·心·三焦 — 행·카드 HUBGR-0222/0234/0254와 맞춤)
    fix = lambda qs: [dict(q, a=q['a'].replace('세 경(大腸·心·三焦)이 火를', '세 경(脾·胃·心包)이 火를')) for q in qs]
    assert fix(p.get('quiz', [])) == before.get('quiz', [])
    assert len(p['rows']) == len(before['rows'])
    for i, (row, previous) in enumerate(zip(p['rows'], before['rows'])):
        if row['fact'] != previous['fact']:
            changed_facts.append((p['id'], i))
    texts = [r['fact'] for r in p['rows']] + [q['a'] for q in p.get('quiz', [])]
    texts += [v for r in p['rows'] for v in r.get('memory', {}).values()]
    for text in texts:
        terms.update(CJK.findall(text))
        rendered = fact_html(text)
        restored = re.sub(r'<span class="reading">.*?</span>', '', rendered)
        assert html.unescape(restored.replace('<br>', '\n')) == text
    image = ROOT / p.get('image', 'images/' + p['id'] + '.webp')
    assert image.is_file() and image.stat().st_size > 1000, image
assert len(changed_facts) == 1 and changed_facts[0][0] == 's20p08', changed_facts
assert terms <= READINGS.keys(), terms - READINGS.keys()
assert all(re.fullmatch('[가-힣]+', READINGS[t]) for t in terms)
for term, expected in {'復溜': '부류', '數脈': '삭맥', '少氣懶言': '소기나언',
                       '罷極之本': '피극지본', '參附湯': '삼부탕', '悲則氣消': '비즉기소',
                       '口眼喎斜': '구안와사', '背兪穴': '배수혈'}.items():
    assert READINGS[term] == expected, term
assert fact_html('炮製(포제)') == '炮製(포제)'
assert fact_html('<>&\n') == '&lt;&gt;&amp;<br>'

index = (ROOT / 'index.html').read_text()
recall = (ROOT / 'recall.html').read_text()
assert len(re.findall(r'<td class="fact(?: qa)?">', index)) == sum(len(p['rows']) + len(p.get('quiz', [])) for p in lib['panels'])
assert len(re.findall(r'id="bReading"', index)) == 1
assert len(re.findall(r'id="bReading"', recall)) == 1
assert '<title>한의학 Sketchy 허브 v' + lib['release']['version'] + '</title>' in index
for pid in ['s02u02', 's14u01', 's15u02']:
    for page in [index, recall]:
        assert 'images/' + pid + '-v2.3.png' in page
for image in re.findall(r'<img[^>]+src="([^"]+)"', index):
    assert (ROOT / image).is_file(), image
# 두 페이지의 실제 배포 스크립트를 구문 검사한다.
with tempfile.TemporaryDirectory() as tmp:
    for name, page in [('index', index), ('recall', recall)]:
        path = Path(tmp) / (name + '.js')
        path.write_text('\n'.join(re.findall(r'<script>(.*?)</script>', page, re.S)))
        if shutil.which('node'):
            subprocess.run(['node', '--check', str(path)], check=True)
# 기존 원본 이미지의 내용은 이전 버전과 같아야 한다.
assert not subprocess.check_output(['git', 'diff', BASE, '--', 'images/*.webp'], cwd=ROOT)
print(f'PASS: 58 panels / 613 facts / 335 quiz answers / {len(terms)} readings; original text and images preserved')
print('JS syntax: passed' if shutil.which('node') else 'JS syntax: node not on PATH; verify separately or in browser')
