#!/usr/bin/env python3
"""manifest의 상대 경로 src(audio/narration/<파일>)를 음성 저장소 주소로 바꾼다 — 2026-11-23 음성 분리.

  python3 src/lessons/tools/audio_to_remote.py --verified runs/20261123-audio-split/verify.json

verify.json = 브라우저에서 주소마다 받아 본 결과 {"<파일>": {"status":200,"sha256":"…"}}.
주소가 200이고 sha가 manifest의 audio_sha256과 같은 기록만 바꾼다. 하나라도 어긋나면 아무것도 바꾸지 않는다.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BASE = 'https://baeggman.github.io/sketchy-audio/'
args = sys.argv[1:]
if args[:1] != ['--verified'] or len(args) != 2:
    sys.exit(__doc__)
ver = json.loads(Path(args[1]).read_text())
mp = ROOT / 'audio/narration/manifest.json'
m = json.loads(mp.read_text())
bad, n = [], 0
for k, r in m['records'].items():
    name = r['src'].rsplit('/', 1)[-1]
    v = ver.get(name)
    if not v or v.get('status') != 200 or v.get('sha256') != r['audio_sha256']:
        bad.append((k, name, v))
if bad:
    for b in bad[:20]:
        print('FAIL', *b)
    sys.exit(f'어긋남 {len(bad)}건 — 아무것도 바꾸지 않음')
for r in m['records'].values():
    if not r['src'].startswith('http'):
        r['src'] = BASE + r['src'].rsplit('/', 1)[-1]; n += 1
mp.write_text(json.dumps(m, ensure_ascii=False, indent=1))
print(f'바꿈 {n}개 · 전체 {len(m["records"])}개 확인 통과')
