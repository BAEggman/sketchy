#!/usr/bin/env python3
"""과 지도 검사 (Carbon v7 경로 대응):
   python3 src/lessons/tools/carbon/check_map.py
- 740행이 정거장·틀·dropped·held에 정확히 한 번씩 나오는가
- 과마다 정거장 수가 6~14이고 계산값과 일치하는가
- 모든 카드 id가 유효하고 빠진 카드가 없는가
- 장소(place 앞부분)가 중복되지 않는가
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
L = HERE.parents[1]                     # sketchy/src/lessons
ROOT = L.parents[1]                     # sketchy/
WORK = ROOT.parent                      # sketchy_carbon/

lib = json.loads((L.parent / 'panels/library.json').read_text(encoding='utf-8'))
M = json.loads((L / 'lesson_map.json').read_text(encoding='utf-8'))
want = {f"{p['id']}#{i}" for p in lib['panels'] for i in range(len(p['rows']))}
seen = collections.Counter()
err = []

for x in M['lessons']:
    n = 2
    for r in x.get('frame_rows', []):
        seen[r] += 1
    for s in x['stations']:
        if s.get('row'):
            seen[s['row']] += 1
        elif not s.get('cards'):
            err.append(f"{x['id']}: 행도 카드도 없는 정거장")
        n += s.get('split', 1) or 1
    if n != x['n_stations'] or not 6 <= n <= 14:
        err.append(f"{x['id']}: 정거장 {x['n_stations']} (계산 {n})")

for d in M['dropped'] + M.get('held', []):
    seen[d['row']] += 1

miss = want - set(seen)
extra = set(seen) - want
dup = [k for k, v in seen.items() if v > 1]
if miss:
    err.append(f'빠진 행 {sorted(miss)[:10]}')
if extra:
    err.append(f'없는 행 {sorted(extra)[:10]}')
if dup:
    err.append(f'두 번 나온 행 {dup[:10]}')

deck = WORK / 'refs/cards/deck.json'
if not deck.exists():
    deck = L / '.cache/deck.json'
if deck.exists():
    deck_data = json.loads(deck.read_text(encoding='utf-8'))
    allc = {c['id'] for c in deck_data}
    bad = {c for x in M['lessons'] for s in x['stations'] for c in s.get('cards', []) if c not in allc}
    if bad:
        err.append(f'덱에 없는 카드 {sorted(bad)[:10]}')
    linked = {c for x in M['lessons'] for s in x['stations'] for c in s.get('cards', [])}
    sk = {x['card'] for x in M.get('skipped_cards', [])}
    un = allc - linked - sk
    if un:
        err.append(f'어디에도 없는 카드 {len(un)}: {sorted(un)[:10]}')
    if linked & sk:
        err.append(f'정거장과 skip에 함께 있는 카드 {sorted(linked & sk)[:10]}')

pl = collections.Counter(x['place'].split(' — ')[0].strip() for x in M['lessons'])
dup_pl = [k for k, v in pl.items() if v > 1]
if dup_pl:
    err.append(f'장소 중복 {dup_pl}')

print(f"과 {len(M['lessons'])} · 정거장 {sum(x['n_stations'] for x in M['lessons'])} · 정거장 행 {sum(len(x['stations']) for x in M['lessons'])} · dropped {len(M['dropped'])} · held {len(M.get('held', []))} · 행 {len(want)}")
print('\n'.join(err) if err else 'PASS')
sys.exit(1 if err else 0)
