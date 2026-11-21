import json, re, sys
from PIL import Image
d = json.load(open('/home/claude/work/runs/20261121-p3-b3/final.json', encoding='utf-8'))
sizes = {}
def size(path):
    p = path.split(' ')[0]
    if p not in sizes: sizes[p] = Image.open('/home/claude/work/' + p).size
    return sizes[p]
HAN = re.compile(r'[㐀-鿿豈-﫿]'); DIG = re.compile(r'[0-9０-９]')
bad = 0
nu_ids = {u['id'] for u in d['needs_user_ok']}
for lid, L in d['lessons'].items():
    for k in ['base_image','dict','keep','edits','stations','trainer','questions','needs_user_ok','counts']:
        if k not in L: print(lid, 'missing', k); bad += 1
    W, H = size(L['base_image'])
    tot = 0
    for e in L['edits']:
        x, y, w, h = e['crop']
        if x < 0 or y < 0 or x + w > W or y + h > H: print(lid, e['id'], 'crop out', e['crop'], (W, H)); bad += 1
        for r in e.get('region', []):
            rx, ry, rw, rh = r
            if rx < 0 or ry < 0 or rx + rw > w or ry + rh > h: print(lid, e['id'], 'region out', r); bad += 1
        n = len(e.get('new_objects', [])); tot += n
        if n > 3: print(lid, e['id'], 'new>3'); bad += 1
        for f in ['id','crop','region','order','prompt_en']:
            if f not in e: print(lid, e['id'], 'edit missing', f); bad += 1
        if re.search(r'\b\d', e['prompt_en']): pass
    if tot > 8: print(lid, 'new objects >8', tot); bad += 1
    if tot != L['counts']['new_objects']: print(lid, 'count mismatch', tot, L['counts']['new_objects']); bad += 1
    ss = L['stations']
    if ss[0]['kind'] != 'frame' or ss[-1]['kind'] != 'review': print(lid, 'frame/review order'); bad += 1
    if [s['n'] for s in ss] != list(range(len(ss))): print(lid, 'n seq'); bad += 1
    if len(ss) != L['counts']['stations']: print(lid, 'station count', len(ss)); bad += 1
    for s in ss:
        for f in ['n','kind','obj','fact','hook','say','tts','src','box']:
            if f not in s: print(lid, s.get('n'), 'missing', f); bad += 1
        if s['kind'] not in ('frame','person','trap','review'): print(lid, s['n'], 'kind', s['kind']); bad += 1
        if len(s['fact']) > 60: print(lid, s['n'], 'fact', len(s['fact']), s['fact']); bad += 1
        if HAN.search(s['tts']): print(lid, s['n'], 'tts hanja', HAN.findall(s['tts'])); bad += 1
        if DIG.search(s['tts']): print(lid, s['n'], 'tts digit', DIG.findall(s['tts'])); bad += 1
        if s['box'] is not None:
            bx, by, bw, bh = s['box']
            if bx < 0 or by < 0 or bx + bw > W or by + bh > H: print(lid, s['n'], 'box out'); bad += 1
    if len(L['questions']) != 5: print(lid, 'questions', len(L['questions'])); bad += 1
    for u in L['needs_user_ok']:
        if u not in nu_ids: print(lid, 'unknown needs id', u); bad += 1
    print(f'{lid}: edits {len(L["edits"])} new {tot} stations {len(ss)} size {W}x{H}')
print('BAD', bad)
