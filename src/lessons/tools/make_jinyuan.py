# -*- coding: utf-8 -*-
"""P3 金元 Run 3 — 심사 명세 runs/20261121-p3-jinyuan/final.json + 구역 수정한 그림 → hist-06a 과 JSON · webp · 단서 그림

- 그림: 옛 hist-06a를 바탕으로 E1~E6 구역 수정(zone_prep → Gemini → zone_paste)한 2752×1536 PNG. 확대 없이 WebP q90.
- 옛 과는 지우지 않고 보관함으로 내린다: src/lessons/_retired/hist-06a_v1.json, images/_retired/hist-06a_v1/(그림 · 단서 그림 · 썸네일).
- 정거장 box는 완성 그림을 직접 보고 잡았다(2026-11-21). 내용 정거장은 kind를 비운다(player가 정거장으로 읽음). 함정 정거장도 해 · 달 물통에 상자를 준다.
- tts는 final.json의 tts를 그대로 쓴다(심사 때 손으로 적은 독음).
실행: python3 src/lessons/tools/make_jinyuan.py <완성.png>
"""
import json, os, shutil, subprocess, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
RUN = 'runs/20261121-p3-jinyuan'
FINAL = json.load(open(os.path.join(ROOT, RUN, 'final.json'), encoding='utf-8'))
LID = 'hist-06a'
W, H = 2752, 1536

BOX = {1: [120, 140, 600, 700], 2: [60, 250, 700, 980], 3: [840, 120, 600, 720], 4: [840, 120, 820, 1380],
       5: [1540, 120, 600, 800], 6: [1840, 40, 240, 780], 7: [2160, 40, 592, 980], 8: [2490, 760, 262, 280],
       9: [2100, 1040, 652, 496], 10: [2280, 770, 460, 240]}

TITLE = '金·元 ① 金元四大家 — 劉完素 · 張從正 · 李杲(金) · 朱震亨(元)'
PLACE = '금광(金) 갱도 셋과 고개 너머 붉은 시내 원두막(元)'


def git_mv(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(['git', '-C', ROOT, 'mv', src, dst], check=True)


def retire():
    old_json = os.path.join(ROOT, 'src/lessons/l', LID + '.json')
    if json.load(open(old_json, encoding='utf-8')).get('attrs', {}).get('run') == '20261121-p3-jinyuan':
        print('이미 새 과다 — 보관 단계 건너뜀')
        return
    ret = os.path.join(ROOT, 'images/_retired', LID + '_v1')
    git_mv(old_json, os.path.join(ROOT, 'src/lessons/_retired', LID + '_v1.json'))
    git_mv(os.path.join(ROOT, 'images/lessons', LID + '.webp'), os.path.join(ret, 'lesson.webp'))
    git_mv(os.path.join(ROOT, 'images/cues', LID), os.path.join(ret, 'cues'))
    if os.path.exists(os.path.join(ROOT, 'images/thumbs', LID + '.webp')):
        git_mv(os.path.join(ROOT, 'images/thumbs', LID + '.webp'), os.path.join(ret, 'thumb.webp'))


def main(png):
    im = Image.open(png).convert('RGB')
    assert im.size == (W, H), im.size
    retire()
    im.save(os.path.join(ROOT, 'images/lessons', LID + '.webp'), 'WEBP', quality=90, method=6)
    cues = os.path.join(ROOT, 'images/cues', LID)
    os.makedirs(cues, exist_ok=True)
    st = []
    for s in FINAL['stations']:
        n = s['n']
        d = {'n': n}
        if s['kind'] in ('frame', 'review'):
            d['kind'] = s['kind']
        for k in ('obj', 'fact', 'hook', 'say'):
            d[k] = s[k]
        b = BOX.get(n)
        if b:
            assert b[0] >= 0 and b[1] >= 0 and b[0] + b[2] <= W and b[1] + b[3] <= H and min(b[2], b[3]) >= 240, (n, b)
            c = im.crop((b[0], b[1], b[0] + b[2], b[1] + b[3]))
            if max(c.size) > 800:
                r = 800.0 / max(c.size)
                c = c.resize((round(c.size[0] * r), round(c.size[1] * r)), Image.LANCZOS)
            c.save(os.path.join(cues, '%d.webp' % n), 'WEBP', quality=90)
        d['box'] = b
        d['src'] = s.get('src', [])
        d['tts'] = s['tts']
        if s['kind'] not in ('frame', 'review'):
            d['role'] = s['kind']
        st.append(d)
    L = {'id': LID, 'title': TITLE, 'place': PLACE, 'image': 'images/lessons/%s.webp' % LID, 'w': W, 'h': H,
         'design': RUN + '/', 'stations': st,
         'attrs': {'run': '20261121-p3-jinyuan', 'method': '옛 hist-06a 구역 수정 E1~E6(zone_prep · zone_paste)',
                   'retired': 'src/lessons/_retired/%s_v1.json' % LID, 'questions': FINAL['questions'],
                   'trainer': FINAL['trainer'], 'narration': '옛 녹음은 쓰지 않는다 — 새 대본 확정 뒤 다시 녹음'}}
    json.dump(L, open(os.path.join(ROOT, 'src/lessons/l', LID + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('written', LID, len(st), 'stations ·', os.path.getsize(os.path.join(ROOT, 'images/lessons', LID + '.webp')) // 1024, 'KB')


if __name__ == '__main__':
    main(sys.argv[1])
