# -*- coding: utf-8 -*-
"""P2 시범 醋炙(Run 2) — 심사 명세 runs/20261121-p2-cho/final.json + 실제 그림 → pilot-cho 과 JSON · webp

- 그림 원본: ~/Downloads/sketchy_opus/gemini_raw/p2-cho_v2-edit3-tumble.jpeg (Gemini, 2752×1536). 확대하지 않고 WebP q90로만 바꾼다.
- 정거장 box는 원본을 좌표 격자 위에서 직접 읽었다(2026-11-21).
- 화면에 보이는 fact는 60자 이내로 줄이고, 심사본 fact 전문은 attrs.fact_full에 그대로 둔다(줄 번호 출처 보존).
- tts는 final.json 것을 그대로 쓴다(한자가 남아 있으면 멈춘다).
실행: python3 src/lessons/tools/make_pilot_cho.py <p2-cho_v2-edit3-tumble.jpeg>
"""
import json, os, re, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
RUN = 'runs/20261121-p2-cho'
FINAL = json.load(open(os.path.join(ROOT, RUN, 'final.json'), encoding='utf-8'))
RAW = 'p2-cho_v2-edit3-tumble.jpeg'

BOX = {1: [40, 280, 520, 830], 2: [530, 130, 370, 1050], 3: [830, 180, 270, 1000], 4: [1220, 50, 380, 370],
       5: [900, 440, 650, 640], 6: [1530, 300, 560, 860], 7: [2000, 340, 440, 730], 8: [2200, 540, 552, 760],
       9: [2280, 980, 472, 520]}

# 화면용 짧은 fact(60자 이내) — 내용은 심사본 fact에서 줄이기만 했다(새 사실 없음)
SHORT = {
    1: '乳香 — 醋炙 ① 疏肝·活血止痛 · ③ 矯臭矯味(3543행) · 妊娠愼用(3503행)',
    2: '沒藥 — 醋炙 ① · ③ 矯臭矯味(3543행) · 妊娠愼用(3503행)',
    3: '三稜 — 醋炙 ①(3543행) · 妊娠禁用(3501행) · 牙硝畏三稜(3500행)',
    4: '莪朮 — 醋炙 ①(3543행) · 妊娠禁用(三稜과 짝, 3501행)',
    5: '柴胡 — 醋炙 ①(3543행) · 炒 = 不斷히 저어 볶음(3530행)',
    8: '玄胡索 — 醋炙 ①(3543행) · 호박 아님(琥珀 = 重鎭安神藥 3597행)',
    9: '醋炙 ① 疏肝·活血止痛 = 여덟 약(3543행) · 上行·活血通絡은 酒炙(3542행)',
}
TITLE = '醋炙法 ① 疏肝·活血止痛 — 유몰삼아시향청현(시범 · 새 문법)'
PLACE = '약한 파란 불 위 긴 팬에 식초가 흐르는 부엌 작업대'


def check_tts(s, tag):
    left = re.findall(r'[一-鿿]+', s)
    if left:
        raise SystemExit(f'{tag}: tts에 한자가 남았다 — ' + ' '.join(sorted(set(left))))
    return s


def main(src):
    im = Image.open(src).convert('RGB')
    assert im.size == (2752, 1536), im.size
    lid = 'pilot-cho'
    out = os.path.join(ROOT, 'images/lessons', lid + '.webp')
    im.save(out, 'WEBP', quality=90, method=6)
    st, full = [], {}
    for s in FINAL['stations']:
        n = s['n']
        kind = 'frame' if n == 0 else ('review' if n == 10 else None)
        fact = SHORT.get(n, s['fact'])
        if fact != s['fact']:
            full[str(n)] = s['fact']
        if kind is None:
            assert len(fact) <= 60, (n, len(fact))
            b = BOX[n]
            assert b[0] >= 0 and b[1] >= 0 and b[0] + b[2] <= 2752 and b[1] + b[3] <= 1536, (n, b)
        else:
            b = None
        d = {'n': n}
        if kind:
            d['kind'] = kind
        d.update({'obj': s['obj'], 'fact': fact, 'hook': s['hook'], 'say': s['say'], 'box': b,
                  'src': [RUN + '/final.json'], 'tts': check_tts(s['tts'], f'#{n}')})
        st.append(d)
    L = {'id': lid, 'title': TITLE, 'place': PLACE, 'image': 'images/lessons/%s.webp' % lid, 'w': 2752, 'h': 1536,
         'stations': st,
         'attrs': {'pilot': 'P2', 'run': '20261121-p2-cho', 'lyric': FINAL['lyric'],
                   'raw': '~/Downloads/sketchy_opus/gemini_raw/' + RAW,
                   'fact_full': full, 'questions': FINAL['questions']}}
    json.dump(L, open(os.path.join(ROOT, 'src/lessons/l', lid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('written', lid, len(st), 'stations ·', os.path.getsize(out) // 1024, 'KB · fact 줄임', len(full))


if __name__ == '__main__':
    main(sys.argv[1])
