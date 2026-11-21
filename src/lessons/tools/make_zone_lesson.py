# -*- coding: utf-8 -*-
"""구역 수정한 그림 + 정거장 명세 → 과 JSON · webp · 단서 그림 (P3 의학사 묶음 공용, make_jinyuan.py를 일반화)

실행: python3 src/lessons/tools/make_zone_lesson.py LID 완성.png 명세.json
- 명세.json: {"title","place","run","stations":[{n,kind,obj,fact,hook,say,tts,src,box}], "questions":[...], "trainer":[...], "notes":"…"}
  kind가 frame · review면 그대로, 그 밖(person · trap 등)은 role로 옮기고 kind를 비운다(재생기가 정거장으로 읽음).
  box는 [x,y,w,h] 2752×1536 좌표, 짧은 변 ≥240(frame · review는 null).
- 옛 과가 있으면 지우지 않고 보관함으로: src/lessons/_retired/<LID>_v1.json, images/_retired/<LID>_v1/(그림 · 단서 · 썸네일).
- 새 과(옛 JSON 없음)도 된다.
"""
import json, os, subprocess, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
W, H = 2752, 1536


def git_mv(src, dst):
    if not os.path.exists(src):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(['git', '-C', ROOT, 'mv', '-k', src, dst], check=True)


def retire(lid, run):
    old = os.path.join(ROOT, 'src/lessons/l', lid + '.json')
    if os.path.exists(old) and json.load(open(old, encoding='utf-8')).get('attrs', {}).get('run') == run:
        return  # 이미 새 과
    ret = os.path.join(ROOT, 'images/_retired', lid + '_v1')
    if os.path.exists(os.path.join(ROOT, 'src/lessons/_retired', lid + '_v1.json')):
        return  # 이미 보관함에 있음
    git_mv(old, os.path.join(ROOT, 'src/lessons/_retired', lid + '_v1.json'))
    git_mv(os.path.join(ROOT, 'images/lessons', lid + '.webp'), os.path.join(ret, 'lesson.webp'))
    git_mv(os.path.join(ROOT, 'images/cues', lid), os.path.join(ret, 'cues'))
    git_mv(os.path.join(ROOT, 'images/thumbs', lid + '.webp'), os.path.join(ret, 'thumb.webp'))


def main(lid, png, spec_path):
    S = json.load(open(spec_path, encoding='utf-8'))
    im = Image.open(png).convert('RGB')
    assert im.size == (W, H), im.size
    retire(lid, S['run'])
    im.save(os.path.join(ROOT, 'images/lessons', lid + '.webp'), 'WEBP', quality=90, method=6)
    cues = os.path.join(ROOT, 'images/cues', lid)
    os.makedirs(cues, exist_ok=True)
    st = []
    for s in S['stations']:
        d = {'n': s['n']}
        if s.get('kind') in ('frame', 'review'):
            d['kind'] = s['kind']
        for k in ('obj', 'fact', 'hook', 'say'):
            d[k] = s.get(k, '')
        b = s.get('box')
        if b:
            assert b[0] >= 0 and b[1] >= 0 and b[0] + b[2] <= W and b[1] + b[3] <= H and min(b[2], b[3]) >= 240, (s['n'], b)
            c = im.crop((b[0], b[1], b[0] + b[2], b[1] + b[3]))
            if max(c.size) > 800:
                r = 800.0 / max(c.size)
                c = c.resize((round(c.size[0] * r), round(c.size[1] * r)), Image.LANCZOS)
            c.save(os.path.join(cues, '%d.webp' % s['n']), 'WEBP', quality=90)
        d['box'] = b
        d['src'] = s.get('src', [])
        d['tts'] = s['tts']
        if s.get('kind') not in ('frame', 'review', None):
            d['role'] = s['kind']
        st.append(d)
    L = {'id': lid, 'title': S['title'], 'place': S['place'], 'image': 'images/lessons/%s.webp' % lid, 'w': W, 'h': H,
         'design': 'runs/%s/' % S['run'], 'stations': st,
         'attrs': {'run': S['run'], 'method': S.get('method', '구역 수정(zone_prep · Gemini · zone_paste)'),
                   'questions': S.get('questions', []), 'trainer': S.get('trainer', []), 'notes': S.get('notes', ''),
                   'narration': '옛 녹음은 쓰지 않는다 — 새 대본 확정 뒤 다시 녹음'}}
    json.dump(L, open(os.path.join(ROOT, 'src/lessons/l', lid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('written', lid, len(st), 'stations ·', os.path.getsize(os.path.join(ROOT, 'images/lessons', lid + '.webp')) // 1024, 'KB')


if __name__ == '__main__':
    main(*sys.argv[1:4])
