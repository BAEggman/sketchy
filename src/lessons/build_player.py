#!/usr/bin/env python3
"""과 재생기 빌드 — src/lessons/l/*.json → 저장소 루트 lessons.html (단일 파일, 외부 라이브러리·폰트·CDN 없음).

    python3 src/lessons/build_player.py

과 JSON은 페이지에 인라인으로 들어가고, 그림은 외부 파일(images/lessons/<id>.webp)을 링크한다.
그림 파일이 없으면 has_image=false로 표시해 회색 자리표시를 그린다(요청 자체를 하지 않음).
꼴이 틀리면(필수 칸·상자 꼴·중복 id) 멈추고, 권고 위반(정거장 6~14·사실 60자·상자 범위)은 경고만 한다.
"""
import json
import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LDIR = HERE / 'l'
OUT = ROOT / 'lessons.html'


def is_box(b):
    return isinstance(b, list) and len(b) == 4 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in b)


def boxes(st):
    b = st.get('box')
    if b is None:
        return []
    if is_box(b):
        return [b]
    if isinstance(b, list) and b and all(is_box(x) for x in b):
        return b
    raise ValueError(f"정거장 {st.get('n')}: box는 [x,y,w,h] 하나 또는 그 목록이어야 한다 — {b!r}")


def check(L, path, errors, warns):
    tag = path.name
    for k in ('id', 'title', 'w', 'h', 'stations'):
        if k not in L:
            errors.append(f'{tag}: 「{k}」 칸이 없다')
    if errors:
        return
    if L['id'] != path.stem:
        warns.append(f"{tag}: id {L['id']!r}가 파일 이름과 다르다")
    L.setdefault('image', f"images/lessons/{L['id']}.webp")
    L.setdefault('place', '')
    W, H = L['w'], L['h']
    sts = L['stations']
    if not isinstance(sts, list) or not sts:
        errors.append(f'{tag}: stations가 비었다')
        return
    if not 6 <= len(sts) <= 14:
        warns.append(f'{tag}: 정거장 {len(sts)}개(권고 6~14)')
    seen = set()
    for st in sts:
        n = st.get('n')
        if not isinstance(n, int) or n in seen:
            errors.append(f'{tag}: 정거장 번호 {n!r}가 정수가 아니거나 겹친다')
        seen.add(n)
        kind = st.get('kind')
        if kind not in (None, 'frame', 'review'):
            errors.append(f'{tag} #{n}: kind {kind!r}는 frame·review·(없음) 가운데 하나여야 한다')
        for k in ('fact',):
            if not st.get(k):
                warns.append(f'{tag} #{n}: 「{k}」가 비었다')
        tts_txt = st.get('tts')
        if not tts_txt:
            warns.append(f'{tag} #{n}: 읽기 대본 tts가 없다(브라우저가 한자를 중국어로 읽는다 — tools/make_tts.js)')
        elif re.search('[\u3400-\u9fff\uf900-\ufaff]', tts_txt):
            warns.append(f'{tag} #{n}: tts에 한자가 남았다')
        try:
            bs = boxes(st)
        except ValueError as e:
            errors.append(f'{tag}: {e}')
            continue
        if kind == 'frame' and bs:
            warns.append(f'{tag} #{n}: 틀에 box가 있다(투어에서는 무시하고 전체 그림을 보인다)')
        if kind is None and not bs:
            warns.append(f'{tag} #{n}: 내용 정거장에 box가 없다(시험·복습에서 빠진다)')
        if kind is None and len(st.get('fact') or '') > 60:
            warns.append(f"{tag} #{n}: 사실 {len(st['fact'])}자(권고 60자 이내)")
        for x, y, w, h in bs:
            if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
                warns.append(f'{tag} #{n}: 상자 {[x, y, w, h]}가 그림({W}×{H}) 밖으로 나간다')
        attrs = st.get('attrs')
        if attrs is not None:
            if not isinstance(attrs, list):
                errors.append(f'{tag} #{n}: attrs는 목록이어야 한다')
            else:
                num_codes = ('공룡', '일렉기타', '이층 버스', '삼지창', '사과', '오징어', '육각 너트', '칠면조', '팔레트', '구미호', '사계절 바퀴', '둘', '두 ', '셋', '세 ', '하나', '3단', '2구', '2具')
                for a in attrs:
                    slot = a.get('slot', '?')
                    vessel = a.get('vessel')
                    if not vessel or not isinstance(vessel, list) or vessel == ['그림']:
                        warns.append(f'{tag} #{n} [{slot}]: attrs 칸에 그릇(vessel)이 없거나 「그림」만 있다(문항 필요)')
                    if slot == '수':
                        a_obj = a.get('obj') or ''
                        if not any(nc in a_obj for nc in num_codes):
                            warns.append(f'{tag} #{n} [수]: 숫자 물건 표기 {a_obj!r}가 공용 부호표와 다르다')
                    ab = a.get('box')
                    if ab is not None and not is_box(ab):
                        errors.append(f'{tag} #{n} [{slot}]: attr box는 [x,y,w,h]여야 한다 — {ab!r}')


def main():
    errors, warns, lessons = [], [], []
    audio_path = ROOT / 'audio/narration/manifest.json'
    recordings = json.loads(audio_path.read_text())['records'] if audio_path.exists() else {}
    applied = set()
    for p in sorted(LDIR.glob('*.json')):
        try:
            L = json.loads(p.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'{p.name}: JSON 오류 — {e}')
            continue
        check(L, p, errors, warns)
        for st in L['stations']:
            key = f"{L['id']}#{st['n']}"
            if key not in recordings:
                continue
            a = recordings[key]
            digest = lambda data: hashlib.sha256(data).hexdigest()
            if digest(json.dumps(st, ensure_ascii=False, sort_keys=True).encode()) != a['station_sha256']:
                errors.append(f'{key}: 녹음 승인 후 정거장 변경 — 재검토 필요')
            if digest(a['text'].encode()) != a['text_sha256'] or digest((ROOT / a['src']).read_bytes()) != a['audio_sha256']:
                errors.append(f'{key}: 대본/음성 해시 불일치')
            if digest((ROOT / L['image']).read_bytes()) != a['image_sha256']:
                errors.append(f'{key}: 녹음 승인 후 그림 변경 — 재검토 필요')
            st['recording'] = {'src': a['src'], 'text': a['text']}
            applied.add(key)
        L['has_image'] = (ROOT / L.get('image', '')).is_file() if L.get('image') else False
        lessons.append(L)
    ids = [L.get('id') for L in lessons]
    if applied != set(recordings):
        errors.append('녹음 연결표에 존재하지 않는 정거장이 있다')
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f'과 id {i!r}가 겹친다')
    for w in warns:
        print('경고:', w, file=sys.stderr)
    if errors:
        for e in errors:
            print('오류:', e, file=sys.stderr)
        sys.exit(1)
    lessons.sort(key=lambda L: (L['id'].startswith('_'), L['id']))   # 데모(_)는 맨 뒤
    data = json.dumps(lessons, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    template = (HERE / 'player-template.html').read_text(encoding='utf-8')
    script = (HERE / 'player.js').read_text(encoding='utf-8')
    if '</script' in script.lower():
        sys.exit('오류: player.js 안에 </script가 있다')
    page = template.replace('__PLAYER_SCRIPT__', script).replace('__LESSONS_DATA__', data)   # 데이터는 마지막에(내용이 자리표를 건드리지 않게)
    OUT.write_text(page, encoding='utf-8')
    n_st = sum(len(L['stations']) for L in lessons)
    n_img = sum(1 for L in lessons if L['has_image'])
    print(f'written {OUT.relative_to(ROOT)} — {len(lessons)}과 · 정거장 {n_st} · 그림 {n_img}/{len(lessons)} · 경고 {len(warns)}')


if __name__ == '__main__':
    main()
