"""시험 카드 검색: python3 src/lessons/tools/cards.py '<정규식>' [장 이름 일부 ...]
먼저 src/lessons/tools/fetch_deck.sh 로 .cache/deck.json 을 만든다."""
import json, re, sys
from pathlib import Path
D = json.load(open(Path(__file__).resolve().parents[1] / '.cache/deck.json'))
pat = re.compile(sys.argv[1]); chs = sys.argv[2:]; n = 0
for c in D:
    if chs and not any(x in c['ch'] for x in chs): continue
    if pat.search(c['q'] + ' ' + c['a']):
        n += 1; print(f"{c['id']} | {c['ch']} | {c['src']} | {c['q']} → {c['a'][:160]}")
print(f'-- {n}장')
