# -*- coding: utf-8 -*-
"""final.json 형식 점검: JSON 유효 · tts 한자/숫자 없음 · fact ≤60 · 편집당 새 물건 ≤3 · 그림당 ≤8 · crop/region이 바탕 안 · 문항 5 · 필수 키."""
import json, re, sys
from PIL import Image
F = sys.argv[1] if len(sys.argv) > 1 else 'runs/20261121-p3-b2/final.json'
d = json.load(open(F, encoding='utf-8'))
BASE = {'hist-01a': 'images/lessons/hist-01a.webp', 'hist-01b': 'images/lessons/hist-01b.webp',
        'hist-02a': '/home/claude/zt/b2/base_hist-02a.png', 'hist-02b': 'images/lessons/hist-02b.webp'}
KEYS = ['base_image', 'dict', 'keep', 'edits', 'stations', 'trainer', 'questions', 'needs_user_ok', 'counts']
HAN = re.compile(r'[㐀-鿿豈-﫿]'); DIG = re.compile(r'[0-9０-９]')
err = []
for lid, l in d['lessons'].items():
    for k in KEYS:
        if k not in l: err.append(f'{lid}: 키 없음 {k}')
    W, H = Image.open(BASE[lid]).size
    tot = 0
    for e in l['edits']:
        x, y, w, h = e['crop']
        if x < 0 or y < 0 or x + w > W or y + h > H: err.append(f'{lid} {e["id"]}: crop 바탕 밖 {e["crop"]} ({W}×{H})')
        for r in e['region']:
            rx, ry, rw, rh = r
            if rx < 0 or ry < 0 or rx + rw > w or ry + rh > h: err.append(f'{lid} {e["id"]}: region crop 밖 {r}')
        n = len(e.get('new_objects', [])); tot += n
        if n > 3: err.append(f'{lid} {e["id"]}: 새 물건 {n} > 3')
        for k in ('id', 'crop', 'region', 'order', 'prompt_en'):
            if k not in e: err.append(f'{lid} {e.get("id")}: edit 키 없음 {k}')
        p = e['prompt_en']
        if not p.startswith('This is a cropped piece') or not p.endswith('Output the same aspect ratio as this picture.'):
            err.append(f'{lid} {e["id"]}: 편집문 머리/꼬리')
    if tot > 8: err.append(f'{lid}: 그림 새 물건 {tot} > 8')
    if l['counts'].get('new_objects') != tot: err.append(f'{lid}: counts.new_objects {l["counts"].get("new_objects")} ≠ {tot}')
    S = l['stations']
    if S[0]['kind'] != 'frame' or S[0]['n'] != 0: err.append(f'{lid}: 첫 정거장 frame 아님')
    if S[-1]['kind'] != 'review': err.append(f'{lid}: 끝 정거장 review 아님')
    if l['counts'].get('stations') != len(S): err.append(f'{lid}: counts.stations 불일치')
    for s in S:
        for k in ('n', 'kind', 'obj', 'fact', 'hook', 'say', 'tts', 'src', 'box'):
            if k not in s: err.append(f'{lid} s{s.get("n")}: 키 없음 {k}')
        if s['kind'] not in ('frame', 'person', 'trap', 'review'): err.append(f'{lid} s{s["n"]}: kind {s["kind"]}')
        if len(s['fact']) > 60: err.append(f'{lid} s{s["n"]}: fact {len(s["fact"])}자')
        if HAN.search(s['tts']): err.append(f'{lid} s{s["n"]}: tts 한자 {HAN.findall(s["tts"])[:5]}')
        if DIG.search(s['tts']): err.append(f'{lid} s{s["n"]}: tts 숫자 {DIG.findall(s["tts"])[:5]}')
        if s['box'] is not None: err.append(f'{lid} s{s["n"]}: box는 null')
    if len(l['questions']) != 5: err.append(f'{lid}: 문항 {len(l["questions"])}')
print('JSON 유효 · 과', len(d['lessons']), '· 편집', sum(len(l['edits']) for l in d['lessons'].values()),
      '· 정거장', sum(len(l['stations']) for l in d['lessons'].values()))
print('\n'.join(err) if err else '점검 통과: 오류 0')
sys.exit(1 if err else 0)
