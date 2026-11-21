# -*- coding: utf-8 -*-
"""20261121-p3-b5 final.json 형식 점검.
python3 -I runs/20261121-p3-b5/check_final.py runs/20261121-p3-b5/final.json
- JSON 유효 · 과마다 필수 키
- tts: 한자 · 숫자 · 라틴 글자 없음
- fact ≤ 60자
- 편집당 new_objects ≤ 3 · 그림당 새 물건 ≤ 8(선택 편집 포함)
- crop이 바탕(2752×1536) 안 · region이 crop 안
- stations: 0 = frame, 마지막 = review, 가운데 person/trap, n 연속 · box null
- questions 5
- prompt_en: 'No text' 끝맺음, 모든 편집 'in the same flat cartoon style'
"""
import json, re, sys
from PIL import Image

BASES = {k: f'/home/claude/zt/b5/base_{k}.png' for k in ('hist-11', 'hist-12', 'hist-13', 'hist-14')}
KEYS = ['base_image', 'dict', 'keep', 'edits', 'stations', 'trainer', 'questions', 'needs_user_ok', 'counts']
HANJA = re.compile(r'[㐀-鿿豈-﫿]')
BAD = re.compile(r'[0-9A-Za-z①-⑳]')

def main(fp, root='.'):
    d = json.load(open(fp, encoding='utf-8'))
    err = []
    assert d['run'] == '20261121-p3-b5'
    assert isinstance(d.get('needs_user_ok'), list) and d['needs_user_ok']
    for lid, L in d['lessons'].items():
        for k in KEYS:
            if k not in L: err.append(f'{lid}: 키 없음 {k}')
        bp = BASES[lid]
        W, H = Image.open(bp if bp.startswith('/') else f'{root}/{bp}').size
        if (W, H) != (2752, 1536): err.append(f'{lid}: 바탕 크기 {W}x{H}')
        eds = L['edits'] + L.get('optional_edits', [])
        tot = 0
        for e in eds:
            x, y, w, h = e['crop']
            if x < 0 or y < 0 or x + w > W or y + h > H: err.append(f'{lid} {e["id"]}: crop 밖 {e["crop"]}')
            for r in e.get('region', []):
                rx, ry, rw, rh = r
                if rx < 0 or ry < 0 or rx + rw > w or ry + rh > h: err.append(f'{lid} {e["id"]}: region 밖 {r}')
            n = len(e['new_objects']); tot += n
            if n > 3: err.append(f'{lid} {e["id"]}: 새 물건 {n} > 3')
            p = e['prompt_en']
            if not p.rstrip().endswith('Output the same aspect ratio as this picture.') or 'No text, no letters, no numbers anywhere.' not in p:
                err.append(f'{lid} {e["id"]}: 끝맺음 문장')
            if 'in the same flat cartoon style' not in p:
                err.append(f'{lid} {e["id"]}: 화풍 문장 없음')
            if HANJA.search(p): err.append(f'{lid} {e["id"]}: prompt에 한자')
        if tot > 8: err.append(f'{lid}: 새 물건 합 {tot} > 8')
        st = L['stations']
        if st[0]['kind'] != 'frame' or st[-1]['kind'] != 'review': err.append(f'{lid}: frame/review 자리')
        for i, s in enumerate(st):
            if s['n'] != i: err.append(f'{lid}: n 순서 {s["n"]}')
            if 0 < i < len(st) - 1 and s['kind'] not in ('person', 'trap'): err.append(f'{lid}#{i}: kind {s["kind"]}')
            for k in ('n', 'kind', 'obj', 'fact', 'hook', 'say', 'tts', 'src', 'box'):
                if k not in s: err.append(f'{lid}#{i}: 키 없음 {k}')
            if s.get('box') is not None: err.append(f'{lid}#{i}: box는 null')
            if len(s['fact']) > 60: err.append(f'{lid}#{i}: fact {len(s["fact"])}자')
            if HANJA.search(s['tts']): err.append(f'{lid}#{i}: tts 한자 {HANJA.findall(s["tts"])[:5]}')
            if BAD.search(s['tts']): err.append(f'{lid}#{i}: tts 숫자/라틴 {BAD.findall(s["tts"])[:5]}')
        if len(L['questions']) != 5: err.append(f'{lid}: questions {len(L["questions"])}')
        print(f'{lid}: 편집 {len(L["edits"])}(+선택 {len(L.get("optional_edits", []))}) · 새 물건 {tot} · 정거장 {len(st)} · fact 최장 {max(len(s["fact"]) for s in st)}자')
    print('needs_user_ok', len(d['needs_user_ok']))
    print('OK' if not err else '\n'.join(['오류:'] + err))
    return not err

if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '.') else 1)
