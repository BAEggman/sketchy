"""과 지도 검사: python3 src/lessons/tools/check_map.py — 740행이 정거장·틀·dropped에 정확히 한 번, 과마다 정거장 6~14"""
import json, collections, sys
from pathlib import Path
L = Path(__file__).resolve().parents[1]
lib = json.load(open(L.parent / 'panels/library.json'))
M = json.load(open(L / 'lesson_map.json'))
want = {f"{p['id']}#{i}" for p in lib['panels'] for i in range(len(p['rows']))}
seen = collections.Counter(); err = []
for x in M['lessons']:
    n = 2
    for r in x.get('frame_rows', []): seen[r] += 1
    for s in x['stations']:
        if s.get('row'): seen[s['row']] += 1
        elif not s.get('cards'): err.append(f"{x['id']}: 행도 카드도 없는 정거장")
        n += s.get('split', 1) or 1
    if n != x['n_stations'] or not 6 <= n <= 14: err.append(f"{x['id']}: 정거장 {x['n_stations']} (계산 {n})")
for d in M['dropped'] + M.get('held', []): seen[d['row']] += 1
miss = want - set(seen); extra = set(seen) - want; dup = [k for k, v in seen.items() if v > 1]
if miss: err.append(f'빠진 행 {sorted(miss)[:10]}')
if extra: err.append(f'없는 행 {sorted(extra)[:10]}')
if dup: err.append(f'두 번 나온 행 {dup[:10]}')
deck = L / '.cache/deck.json'
if deck.exists():
    ids = {c['id'] for c in json.load(open(deck))}
    bad = {c for x in M['lessons'] for c in x['cards'] if c not in ids}
    if bad: err.append(f'덱에 없는 카드 {sorted(bad)[:10]}')
print(f"과 {len(M['lessons'])} · 정거장 {sum(x['n_stations'] for x in M['lessons'])} · 정거장 행 {sum(len(x['stations']) for x in M['lessons'])} · dropped {len(M['dropped'])} · held {len(M.get('held', []))} · 행 {len(want)}")
print('\n'.join(err) if err else 'PASS'); sys.exit(1 if err else 0)
