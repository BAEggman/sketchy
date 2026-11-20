#!/usr/bin/env python3
"""Independently replay the edit ledger and check every exported narration.

Does not import or call the style converter. It verifies an allowlisted change
history, not medical truth or the quality of audio that has not been generated.
"""
import collections
import csv
import hashlib
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/narration-review-20261120'
REL = OUT.relative_to(ROOT)

def read(name):
    return json.loads((OUT / name).read_text())

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def records(main, panels):
    return main['records'] + panels['records'] + panels['bagua']

ledger = read('plain-style-changes.json')
base = ledger['baseline']
def old(name):
    return json.loads(subprocess.check_output(
        ['git', 'show', f'{base}:{REL}/{name}'], cwd=ROOT))

baseline = records(old('narrations.json'), old('panel-narrations.json'))
main, panels = read('narrations.json'), read('panel-narrations.json')
current = records(main, panels)
assert len(current) == 2809
assert [r['card_id'] for r in baseline] == [r['card_id'] for r in current]
before = {r['card_id']: r for r in baseline}
replay = {r['card_id']: r['narration'] for r in baseline}
negative = re.compile(r'않|못|없|아니|아닙|금지|제외|예외|반대|지 마세요|지 말자')
def negatives(text):
    return collections.Counter(
        '아니' if s == '아닙' else '금지명령' if s in {'지 마세요', '지 말자'} else s
        for s in negative.findall(text))

forms = collections.Counter()
for record in ledger['ending_changes']:
    cid = record['card_id']
    text = replay[cid]
    assert sha(text) == record['before_sha256'], cid
    previous_end = -1
    for edit in record['edits']:
        start = edit['offset']
        assert start >= previous_end, cid
        assert text[start:start + len(edit['before'])] == edit['before'], cid
        previous_end = start + len(edit['before'])
        forms[(edit['before'], edit['after'])] += 1
    for edit in reversed(record['edits']):
        start = edit['offset']
        text = text[:start] + edit['after'] + text[start + len(edit['before']):]
    assert sha(text) == record['after_sha256'], cid
    assert negatives(text) == negatives(replay[cid]), cid
    assert re.findall(r'[.!?。…]', text) == re.findall(r'[.!?。…]', replay[cid]), cid
    replay[cid] = text

manual = read('narration-content-edits.json')['edits']
for edit in manual:
    cid = edit['card_id']
    assert replay[cid] == edit['before'], cid
    replay[cid] = edit['after']

for edit in ledger['scaffolding_shortening']:
    cid = edit['card_id']
    assert replay[cid].count(edit['before']) == edit['count'], cid
    replay[cid] = replay[cid].replace(edit['before'], edit['after'])

post = read('post-conversion-review-edits.json')['edits']
for edit in post:
    cid = edit['card_id']
    assert replay[cid] == edit['before'], cid
    replay[cid] = edit['after']

protected = ['original_tts', 'source_station', 'source_row', 'source_system',
             'source_cues', 'retained_terms']
for record in current:
    cid, text = record['card_id'], record['narration']
    prior = before[cid]
    assert replay[cid] == text, cid
    assert sha(text) == record['spoken_text_sha256'], cid
    for key in protected:
        assert prior.get(key) == record.get(key), (cid, key)
    for pattern in [r'\d+', r'[\u3400-\u9fff]']:
        assert not (collections.Counter(re.findall(pattern, prior['narration']))
                    - collections.Counter(re.findall(pattern, text))), cid
    assert re.findall('“[^”]+”', prior['narration']) == re.findall('“[^”]+”', text), cid
    assert set(prior.get('hold_reasons', [])) <= set(record.get('hold_reasons', [])), cid
    assert not record['ready_to_generate'], cid
    assert not re.search(r'(?:습니다|입니다|[봅합됩]니다|세요|지요)(?=[.!?\s”]|$)', text), cid

class ExportParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cid = None
        self.in_script = False
        self.scripts = {}
        self.images = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'article' and 'card' in a.get('class', '').split():
            self.cid = a['id']
            assert self.cid not in self.scripts
            self.scripts[self.cid] = ''
        if tag == 'p' and a.get('class') == 'script':
            self.in_script = True
        if tag == 'img' and a.get('class') == 'scene':
            self.images.append(a['src'])

    def handle_endtag(self, tag):
        if tag == 'p':
            self.in_script = False
        if tag == 'article':
            self.cid = None

    def handle_data(self, data):
        if self.in_script:
            self.scripts[self.cid] += data

parser = ExportParser()
parser.feed((ROOT / 'narration-review.html').read_text())
assert list(parser.scripts) == [r['card_id'] for r in current]
assert parser.scripts == replay
assert len(parser.images) == len(set(parser.images)) == 227
assert all((ROOT / image).is_file() for image in parser.images)
with (OUT / 'narrations.csv').open(encoding='utf-8-sig', newline='') as stream:
    rows = list(csv.DictReader(stream))
assert [(r['card_id'], r['narration']) for r in rows] == [
    (r['card_id'], r['narration']) for r in main['records']]
for name, rs in [('narrations.txt', main['records']),
                 ('panel-narrations.txt', panels['records'] + panels['bagua'])]:
    expected = ['반말 낭독 검토본 · 2026-11-20',
                '보류 표시는 검토용이며 낭독하지 않는다. 생성 승인본이 아니다.', '']
    for r in rs:
        if r['narration']:
            status = '녹음 보류' if r['production_status'] == 'hold' else '검토 초안'
            expected.extend([f"[{r['card_id']}] {status}", r['narration'], ''])
    assert (OUT / name).read_text() == '\n'.join(expected), name

result = {
    'passed': True, 'baseline': base,
    'all_records': len(current), 'spoken_scripts': sum(bool(r['narration']) for r in current),
    'changed_scripts': sum(r['narration'] != before[r['card_id']]['narration'] for r in current),
    'ending_substitutions': sum(forms.values()), 'unique_ending_pairs': len(forms),
    'followup_ambiguities_fixed': sum(e['kind'] == 'conversion_ambiguity' for e in post),
    'inherited_punctuation_fixed': sum(e['kind'] == 'inherited_punctuation' for e in post),
    'independent_edit_ledger_replay': True,
    'no_changes_outside_logged_edits': True,
    'negation_markers_preserved_during_ending_conversion': True,
    'punctuation_preserved_during_ending_conversion': True,
    'numeric_literals_and_hanja_retained': True,
    'quoted_mnemonics_preserved': True, 'source_fields_preserved': True,
    'html_csv_txt_match_json': True, 'main_images_linked': len(parser.images),
    'main_holds': sum(r['production_status'] == 'hold' for r in main['records']),
    'scope': '변환 전후 전문과 변경 기록·출력 대조. 의학적 정확성, 전 그림의 정밀 검증, 음성 청취를 증명하지 않는다.',
}
(OUT / 'post-conversion-review.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
