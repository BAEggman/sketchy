#!/usr/bin/env python3
"""Carbon v7 경락·사암 새 과 29개(new-gr-19..47) 및 기존 보강 3과(mer-10, new-gr-07, new-gr-13) 일괄 생성."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LESSONS = HERE.parents[1]
ROOT = LESSONS.parents[1]
CARBON = ROOT / 'carbon'
sys.path.insert(0, str(HERE))
import make_tts


def grid_boxes(n_content: int, W: int = 2752, H: int = 1536):
    cols = max(2, (n_content + 1) // 2) if n_content > 4 else max(1, n_content)
    rows = 2 if n_content > 4 else 1
    pad_x, pad_y = 60, 80
    cw = (W - pad_x * (cols + 1)) // cols
    ch = (H - pad_y * (rows + 1)) // rows
    out = []
    for i in range(n_content):
        r = i // cols
        c = i % cols
        x = pad_x + c * (cw + pad_x)
        y = pad_y + r * (ch + pad_y)
        out.append([int(x), int(y), max(260, int(cw)), max(260, int(ch))])
    return out


# 혈명/핵심어 → 구체적 시각 소품 매핑
PROP_MAP = {
    '太白': '눈 덮인 하얀 산봉우리(태백산)',
    '太淵': '깊은 돌우물(태연)',
    '少府': '작은 붉은 기와 관청(소부)',
    '魚際': '도마 위 붉은 물고기 배 가장자리(어제)',
    '尺澤': '대나무 자(尺)가 꽂힌 연못(척택)',
    '陰谷': '초승달 그늘이 진 어두운 골짜기(음곡)',
    '足三里': '삼지창(3) 이정표가 선 고갯길(족삼리)',
    '曲池': '구부러진 연못(곡지)',
    '陽谷': '해 비치는 밝은 골짜기(양곡)',
    '陽谿': '해 비치는 시냇물(양계)',
    '二間': '이층 버스(2) 사이 틈새(이간)',
    '足通谷': '시원하게 뚫린 골짜기(족통곡)',
    '解谿': '풀어진 신발 끈 옆 시내(해계)',
    '陷谷': '움푹 꺼진 함정 골짜기(함곡)',
    '足臨泣': '눈물 방울이 맺힌 언덕(족임읍)',
    '厲兌': '숫돌과 날카로운 칼끝(여태)',
    '商陽': '볕 아래 봇짐 상인(상양)',
    '商丘': '봇짐 상인이 오른 언덕(상구)',
    '大都': '큰 성문 도읍지 모형(대도)',
    '大敦': '두툼한 큰 돈주머니와 언덕(대돈)',
    '隱白': '숨겨진 흰 은백색 말(은백)',
    '經渠': '곧게 판 물길 도랑(경거)',
    '陰陵泉': '그늘 언덕 아래 솟는 샘(음릉천)',
    '太谿': '큰 시냇물과 퇴계 선생 패(태계)',
    '少衝': '작은 화살이 솟구치는 과녁(소충)',
    '少海': '작은 금관이 뜬 바닷물(심소해)',
    '神門': '등불 켜진 신령한 붉은 문(신문)',
    '然谷': '불타는 골짜기 바위(연곡)',
    '後谿': '뒤편으로 흐르는 시내(후계)',
    '前谷': '앞쪽에 열린 골짜기(전곡)',
    '小海': '붉은 체가 뜬 작은 바다(소장소해)',
    '崑崙': '높고 험한 곤륜산 봉우리(곤륜)',
    '至陰': '가장 깊은 그늘 끝자리(지음)',
    '委中': '굽힌 오금 한가운데(위중)',
    '束骨': '끈으로 단단히 묶은 뼈(속골)',
    '復溜': '되돌아 흐르는 물줄기(복류)',
    '湧泉': '바닥에서 솟구치는 샘물(용천)',
    '中衝': '가운데로 솟구치는 창끝(중충)',
    '曲澤': '굽이진 얕은 못(곡택)',
    '大陵': '크고 높은 구릉 언덕(대릉)',
    '勞宮': '일꾼들이 땀 흘리는 궁전(노궁)',
    '中渚': '강 한가운데 작은 모래섬(중저)',
    '液門': '물방울이 흐르는 수문(액문)',
    '天井': '하늘이 비치는 우물(천정)',
    '支溝': '갈라진 좁은 도랑(지구)',
    '俠谿': '양쪽 바위가 좁은 시내(협계)',
    '足竅陰': '그늘진 작은 구멍(족규음)',
    '陽輔': '해가 돕는 수레 덧방나무(양보)',
    '陽陵泉': '볕 드는 언덕 아래 샘(양릉천)',
    '曲泉': '굽이쳐 솟는 샘물(곡천)',
    '中封': '가운데 봉인한 흙제단(중봉)',
    '行間': '나무 사이를 걸어가는 길(행간)',
    '太衝': '크게 솟구치는 길목(태충)',
    '孔最': '가장 꼭대기(最)에 뚫린 둥근 구멍(孔)',
    '溫溜': '김이 모락모락 나는 따뜻한 물줄기(溫溜)',
    '陰郄': '초승달 그늘이 진 어두운 바위 틈(陰郄)',
    '養老': '할머니에게 밥상을 올려 봉양하는 평상(養老)',
    '郄門': '바위 틈 사이에 세운 붉은 두 짝 대문(郄門)',
    '會宗': '큰 구리 범종 앞에 모인 여러 깃발(會宗)',
    '梁丘': '나무 들보 다리가 놓인 언덕(梁丘)',
    '地機': '땅 위에 놓인 베틀(地機)',
    '金門': '번쩍이는 황금 대문(金門)',
    '水泉': '맑은 물이 솟는 바위 샘(水泉)',
    '外丘': '바깥쪽으로 솟은 언덕(外丘)',
    '中都': '한가운데 세운 도읍 성루(中都)',
    '跗陽': '발등 위 해 문양 장대(跗陽)',
    '交信': '서로 편지를 주고받는 달 장대(交信)',
    '陽交': '해 배지 금빛 그물이 교차하는 매듭(陽交)',
    '築賓': '귀한 손님을 맞이하려 다진 돌축대(築賓)',
}

NUM_OBJ_MAP = {
    '11': '아래 붉은 일렉기타(1) 위에 맞닿아 세운 붉은 일렉기타(1)',
    '20': '아래 붉은 이층 버스(2) 지붕 위에 올라탄 초록 공룡(0)',
    '9': '저울판 위에 앉은 꼬리 여럿 달린 흰 구미호(9)',
    '19': '아래 붉은 일렉기타(1) 위에 올라앉은 흰 구미호(9)',
    '23': '아래 붉은 이층 버스(2) 지붕 위에 꽂힌 황금 삼지창(3)',
    '45': '아래 붉은 사과(4) 궤짝 위에 얹힌 주황 오징어(5)',
    '21': '아래 붉은 이층 버스(2) 지붕 위에 세운 붉은 일렉기타(1)',
    '67': '아래 은색 육각 너트(6) 받침 위에 올라선 부채 꼬리 칠면조(7)',
    '27': '아래 붉은 이층 버스(2) 지붕 위에 올라선 칠면조(7)',
    '44': '아래 붉은 사과(4) 위에 맞닿아 얹힌 붉은 사과(4)',
    '14': '아래 붉은 일렉기타(1) 위에 얹힌 붉은 사과(4)',
    '361': '큰 황금 삼지창(3) 옆 은색 육각 너트(6) 위에 세운 일렉기타(1)',
    '3寸': '세 갈래 황금 삼지창(3)',
    '8寸': '물감 짠 화가 팔레트(8)',
    '9寸': '흰 여우 구미호(9)',
    '12寸': '붉은 일렉기타(1) 위에 얹힌 이층 버스(2)',
}


def describe_obj_for_fact(lid: str, idx: int, fact: str, place: str) -> tuple[str, str, str, list]:
    """정거장 fact로부터 구체적 시각 물건(obj), 고리(hook), 내레이션(say), attrs 목록 생성."""
    attrs = []
    matched_props = [ f"{v}" for k, v in PROP_MAP.items() if k in fact ]

    # 1. 사암 과 (new-gr-19 .. 30)
    if 19 <= int(lid.split('-')[-1]) <= 30:
        char_hint = place.split('(')[1].split(' 방')[0] if '(' in place else '경락 인물'
        if '正格 補' in fact:
            obj = f"왼쪽 正格 찬장 위 칸(母) 물이 가득 찬 독 둘 — {' · '.join(matched_props[:2]) or '보하는 두 혈 모형'}"
            hook = f"왼쪽 위 칸 채운 독 = 正格 補母 · {' / '.join(matched_props[:2])}"
        elif '正格 瀉' in fact:
            obj = f"왼쪽 正格 찬장 가운데 칸(官) 엎어져 쏟아진 독 둘 — {' · '.join(matched_props[:2]) or '사하는 두 혈 모형'}"
            hook = f"왼쪽 가운데 칸 쏟은 독 = 正格 瀉官 · {' / '.join(matched_props[:2])}"
        elif '勝格 補' in fact:
            obj = f"오른쪽 勝格 찬장 가운데 칸(官) 물이 가득 찬 독 둘 — {' · '.join(matched_props[:2]) or '보하는 두 혈 모형'}"
            hook = "오른쪽 가운데 칸 채운 독 = 勝格 補官 (正格의 瀉와 같은 두 혈)"
        elif '勝格 瀉' in fact:
            obj = f"오른쪽 勝格 찬장 아래 칸(子) 엎어져 쏟아진 독 둘 — {' · '.join(matched_props[:2]) or '사하는 두 혈 모형'}"
            hook = f"오른쪽 아래 칸 쏟은 독 = 勝格 瀉子 · {' / '.join(matched_props[:2])}"
        elif '寒格' in fact:
            obj = f"눈 오는 창 아래 풀무로 불 키운 화로(補火)와 밖으로 물 퍼내는 물통(瀉水) — {' · '.join(matched_props[:4])}"
            hook = "화로 불 키움 = 補火 · 물통 물 퍼내기 = 瀉水"
        elif '熱格' in fact:
            obj = f"해 뜬 창 아래 주전자로 물 붓는 물통(補水)과 퍼내는 흙/숯불(瀉) — {' · '.join(matched_props[:4])}"
            hook = "물통 물 붓기 = 補水(寒格의 瀉와 같음) · 흙/불 퍼내기 = 瀉土(또는 瀉火)"
        else:
            obj = f"가운데 선 {char_hint}이(가) 쥔 제 경 오수혈 모형과 표리 짝 락혈 패"
            hook = "제 경 안에서만 보사 = 自經補瀉 · 본경 原穴 + 표리경 絡穴 = 主客原絡"
        say = f"{place.split(' — ')[0]}의 #{idx} 정거장이다. {obj}이(가) 보인다. {fact}."
        attrs.append({'slot': '기여', 'obj': obj, 'fact': fact, 'link': '공용 부호+뜻', 'vessel': ['그림', '문항']})
        return obj, hook, say, attrs

    # 2. 경맥 혈 수 (new-gr-31, 32)
    if lid in ('new-gr-31', 'new-gr-32'):
        m_num = re.search(r'=\s*(\d+)혈', fact)
        num_str = m_num.group(1) if m_num else '361'
        num_obj = NUM_OBJ_MAP.get(num_str, '삼지창(3)과 육각 너트(6) 위 일렉기타(1)')
        mer_name = fact.split('=')[0].strip()
        obj = f"{mer_name} 정본 인물과 저울판 위의 {num_obj}"
        hook = f"{num_obj} = {num_str}혈"
        say = f"{mer_name} 계량대다. 정본 인물이 {num_obj}과 맞닿아 서 있다. {fact}."
        attrs.append({'slot': '이름', 'obj': f"{mer_name} 정본 인물", 'fact': mer_name, 'link': '공용 부호', 'vessel': ['그림', '문항']})
        attrs.append({'slot': '수', 'obj': num_obj, 'fact': f"{num_str}혈", 'link': '공용 부호', 'vessel': ['그림', '문항']})
        return obj, hook, say, attrs

    # 3. 16극혈 (new-gr-33, 34)
    if lid in ('new-gr-33', 'new-gr-34'):
        if '정의' in fact:
            obj = '깊게 갈라진 바위 절벽의 여섯 틈새(郄)와 솟구치는 붉은 물줄기·번개 표지 · 일렉기타(1) 위 육각 너트(6)'
            hook = '바위 틈 = 郄(틈 극) · 일렉기타(1)+육각 너트(6) = 16郄穴 · 급성병과 음경 혈증 치료'
            attrs.append({'slot': '수', 'obj': '일렉기타(1) 위 육각 너트(6)', 'fact': '16개(12경맥 + 음양교·음양유)', 'link': '공용 부호', 'vessel': ['그림', '문항']})
            attrs.append({'slot': '기여', 'obj': '바위 틈과 붉은 물줄기·번개', 'fact': '내장 급성병 · 양경 급성 동통 · 음경 혈증 치료', 'link': '뜻', 'vessel': ['그림', '문항']})
        else:
            obj = ' · '.join(matched_props) if matched_props else f"바위 틈 앞 경락 인물과 {fact.split('=')[1].strip() if '=' in fact else fact}"
            hook = f"바위 틈(郄) + {' · '.join(matched_props)}"
            attrs.append({'slot': '기여', 'obj': obj, 'fact': fact, 'link': '뜻', 'vessel': ['그림', '문항']})
        say = f"암벽 틈새 #{idx} 정거장이다. {obj}이(가) 뚜렷이 그려져 있다. {fact}."
        return obj, hook, say, attrs

    # 4. 골도법 (new-gr-36)
    if lid == 'new-gr-36':
        num_key = next((k for k in ('3寸', '8寸', '9寸', '12寸') if k in fact), None)
        num_obj = NUM_OBJ_MAP.get(num_key, '일렉기타(1)·팔레트(8)·구미호(9)와 육각 너트(6)·오징어(5)·사과(4)·삼지창(3)')
        obj = f"{num_obj} 작업대 위에 나란히 놓인 신체 부위 모형들 ({fact.split('=')[1].strip() if '=' in fact else fact})"
        hook = f"{num_obj} = {fact.split('=')[0].strip()}"
        say = f"목수의 골도 치수 작업대 #{idx}다. {num_obj}과 맞닿은 부위들을 한 묶음으로 외운다. {fact}."
        attrs.append({'slot': '수', 'obj': num_obj, 'fact': fact.split('=')[0].strip(), 'link': '공용 부호', 'vessel': ['그림', '문항']})
        attrs.append({'slot': '기여', 'obj': obj, 'fact': fact, 'link': '뜻', 'vessel': ['그림', '문항']})
        return obj, hook, say, attrs

    # 5. 그 밖의 경락 과 (new-gr-35, 37..47)
    obj = f"구역 #{idx}의 경락 정본 인물과 상징 소품 ({' · '.join(matched_props) if matched_props else fact.split('—')[0].strip()})"
    hook = fact.split('—')[0].strip() if '—' in fact else fact[:28]
    say = f"{place.split(' — ')[0]}의 #{idx} 정거장이다. {fact}."
    attrs.append({'slot': '기여', 'obj': obj, 'fact': fact, 'link': '뜻+소리', 'vessel': ['그림', '문항']})
    return obj, hook, say, attrs


def build_mer_lessons():
    M = json.loads((LESSONS / 'lesson_map.json').read_text(encoding='utf-8'))
    map_by_id = {x['id']: x for x in M['lessons']}

    # 1. 새 과 29개 (new-gr-19 .. 47)
    for num in range(19, 48):
        lid = f'new-gr-{num:02d}'
        m = map_by_id[lid]
        W, H = 2752, 1536
        st_rows = m['stations']
        boxes = grid_boxes(len(st_rows), W, H)

        stations = [{
            'n': 0,
            'kind': 'frame',
            'obj': m['place'],
            'fact': m['title'][:60],
            'hook': m['place'].split(' — ')[0],
            'say': f"{m['title']} 과다. 장소는 {m['place']}. 정본 경락 인물과 공용 부호·뜻·소리 고리를 따라 차례로 읽는다.",
            'box': None,
            'src': [],
        }]
        q_list = []
        for idx, srow in enumerate(st_rows, start=1):
            bx = boxes[idx - 1]
            fact = srow.get('fact') or srow.get('note') or m['title']
            cards = srow.get('cards', [])
            obj, hook, say, attrs_raw = describe_obj_for_fact(lid, idx, fact, m['place'])
            attrs = []
            for a in attrs_raw:
                attrs.append({
                    'slot': a['slot'],
                    'obj': a['obj'],
                    'fact': a['fact'],
                    'link': a['link'],
                    'box': bx,
                    'vessel': a['vessel'],
                })
                q_list.append({
                    'station': idx,
                    'slot': a['slot'],
                    'q': f"[{m['title']} #{idx}] 「{a['obj']}」이(가) 나타내는 [{a['slot']}]은?",
                    'a': a['fact'],
                    'src': cards,
                })
            stations.append({
                'n': idx,
                'obj': obj,
                'fact': fact[:60],
                'hook': hook,
                'say': say,
                'box': bx,
                'src': cards,
                'attrs': attrs,
            })

        rev_n = len(st_rows) + 1
        rev_cards = []
        for s in st_rows:
            for c in s.get('cards', []):
                if c not in rev_cards:
                    rev_cards.append(c)
        stations.append({
            'n': rev_n,
            'kind': 'review',
            'obj': '전체 구역 한 바퀴 되짚기',
            'fact': f"되짚기 — {m['title']}"[:60],
            'hook': '구역 차례대로 핵심 혈명·수·짝 복습',
            'say': '처음부터 한 바퀴 되짚는다. ' + ' / '.join(s['fact'] for s in stations[1:rev_n]),
            'box': boxes[:min(4, len(boxes))],
            'src': rev_cards[:6],
        })
        assert len(stations) == m['n_stations'], f"{lid}: {len(stations)} != {m['n_stations']}"

        for st in stations:
            st['tts'] = make_tts.convert_text_to_tts(st['say'])[0]

        L = {
            'id': lid,
            'title': m['title'],
            'place': m['place'],
            'image': f'images/lessons/{lid}.webp',
            'w': W,
            'h': H,
            'design': f'src/lessons/design/{lid}/',
            'stations': stations,
        }
        (LESSONS / 'l' / f'{lid}.json').write_text(json.dumps(L, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        (CARBON / 'questions' / f'{lid}.json').write_text(json.dumps({'lesson_id': lid, 'questions': q_list}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        ddir = LESSONS / 'design' / lid
        ddir.mkdir(parents=True, exist_ok=True)
        if not (ddir / 'design.md').exists():
            lines = [f"# {lid} {m['title']} — Carbon v7 설계서\n", f"- **장소**: {m['place']}", f"- **정거장 수**: {len(stations)}\n", "## 정거장 매핑\n"]
            for s in stations[1:-1]:
                lines.append(f"### #{s['n']}. {s['fact']}\n- **물건**: {s['obj']}\n- **고리**: {s['hook']}")
            lines.append("\n## 금지 목록\n- 그림 안의 모든 글자·한자·아라비아 숫자·간판 금지\n- 12경락 인물 정본 생김새·옷차림·도구 흔들림 금지\n")
            (ddir / 'design.md').write_text('\n'.join(lines), encoding='utf-8')

        prompt_lines = [
            "A wide 16:9 landscape 2D cartoon illustration in the style of Sketchy Medical: bold black ink outlines, flat bright colors, simple clear shapes, plenty of empty space between objects. Every object is drawn LARGE.",
            f"Scene: {m['place']}.",
        ]
        for s in stations[1:-1]:
            prompt_lines.append(f"{s['n']}. (Zone {s['n']}): {s['obj']}.")
        prompt_lines.append("No text, no letters, no numbers, no signs, no labels, no writing anywhere in the image.")
        (ddir / 'prompt_base.txt').write_text('\n'.join(prompt_lines) + '\n', encoding='utf-8')

        kpath = CARBON / 'keys' / f'{lid}.md'
        if not kpath.exists():
            kpath.write_text(
                f"# 과 열쇠: {lid}\n- **주제**: 경락·사암 ({lid})\n- **장소**: {m['place'].split(' — ')[0]}\n\n"
                "## 공용 부호표\n"
                "- **수**: 0 공룡 · 1 일렉기타 · 2 이층 버스 · 3 삼지창 · 4 사과 · 5 오징어 · 6 육각 너트 · 7 칠면조 · 8 팔레트 · 9 구미호\n"
                "- **12경락 인물**: 肺 흰 수염 노인 · 大腸 솔 흰 작업복 · 胃 국자 요리사 · 脾 밀짚모자 농부 · 心 금관 임금 · 小腸 체 붉은 앞치마 · 膀胱 물지게꾼 · 腎 대머리 장사 · 心包 칼·방패 호위무사 · 三焦 삽 주황 일꾼 · 膽 저울 판관 · 肝 초록 갑옷 장군\n",
                encoding='utf-8'
            )

    # 2. 기존 보강 3과 (mer-10, new-gr-07, new-gr-13) 갱신
    for lid in ('mer-10', 'new-gr-07', 'new-gr-13'):
        jpath = LESSONS / 'l' / f'{lid}.json'
        L = json.loads(jpath.read_text(encoding='utf-8'))
        W, H = L.get('w', 2048), L.get('h', 1144)
        q_list = []

        for st in L['stations']:
            n = st.get('n')
            if st.get('kind') in ('frame', 'review'):
                if lid == 'new-gr-13' and st.get('kind') == 'review':
                    st['obj'] = st['obj'].replace('주사위', '숫자 물건(이층 버스+팔레트 28 · 이층 버스+사과 24 · 일렉기타+이층 버스 12)')
                st['tts'] = make_tts.to_reading(st.get('say', ''))
                continue

            bx = st.get('box')
            first_box = bx[0] if (isinstance(bx, list) and bx and isinstance(bx[0], list)) else (bx or [100, 100, 300, 300])
            if isinstance(bx, list) and len(bx) == 4 and isinstance(bx[0], (int, float)):
                x, y, bw, bh = int(bx[0]), int(bx[1]), int(bx[2]), int(bx[3])
                if bw < 240:
                    x = max(0, min(W - 240, x - (240 - bw) // 2))
                    bw = 240
                if bh < 240:
                    y = max(0, min(H - 240, y - (240 - bh) // 2))
                    bh = 240
                st['box'] = [x, y, bw, bh]
                first_box = st['box']

            if lid == 'mer-10' and n == 3:
                if '醫門法律' not in st['say']:
                    st['say'] += ' 十五絡脈의 세 학설도 함께 기억한다: ① 『靈樞·經脈』은 12별락 + 任脈(鳩尾)·督脈(長强)·脾之大絡(大包), ② 『難經』은 任·督 대신 陽蹻·陰蹻의 락을 넣은 15락, ③ 淸 喩昌의 『醫門法律』은 胃之大絡(虛里)을 더해 16락(또는 기경대락·비·위대락)을 말했다.'
            elif lid == 'new-gr-07' and n == 6:
                if '寅時' not in st['say']:
                    st['say'] += ' 하루의 유주는 새벽 寅時(3~5시) 手太陰肺經(中焦에서 시작)에서 출발하여 丑時(1~3시) 足厥陰肝經에서 끝난다.'
            elif lid == 'new-gr-13' and n in (4, 7, 9):
                if n == 4:
                    st['obj'] = '파란 줄기(長强 → 齦交) · 곁의 이층 버스(2) 위 화가 팔레트(8) = 28혈'
                    st['say'] = st['say'].replace('주사위 2와 8', '이층 버스(2) 위 팔레트(8)')
                    st['attrs'] = [{'slot': '수', 'obj': '이층 버스(2) 위 팔레트(8)', 'fact': '督脈 28穴(長强~齦交)', 'link': '공용 부호', 'box': first_box, 'vessel': ['그림', '문항']}]
                elif n == 7:
                    st['obj'] = '흰 줄기(會陰 → 承漿) · 곁의 이층 버스(2) 위 붉은 사과(4) = 24혈'
                    st['say'] = st['say'].replace('주사위 2와 4', '이층 버스(2) 위 사과(4)')
                    st['attrs'] = [{'slot': '수', 'obj': '이층 버스(2) 위 사과(4)', 'fact': '任脈 24穴(會陰~承漿)', 'link': '공용 부호', 'box': first_box, 'vessel': ['그림', '문항']}]
                elif n == 9:
                    st['obj'] = '붉은 띠(氣衝 ~ 幽門) · 곁의 일렉기타(1) 위 이층 버스(2) = 12혈'
                    st['say'] = st['say'].replace('주사위 1과 2', '일렉기타(1) 위 이층 버스(2)')
                    st['attrs'] = [{'slot': '수', 'obj': '일렉기타(1) 위 이층 버스(2)', 'fact': '衝脈 12穴(氣衝~幽門, 腎經 교회)', 'link': '공용 부호', 'box': first_box, 'vessel': ['그림', '문항']}]

            if not st.get('attrs'):
                st['attrs'] = [{'slot': '기여', 'obj': st.get('obj', ''), 'fact': st.get('fact', ''), 'link': '뜻', 'box': first_box, 'vessel': ['그림', '문항']}]
            for a in st['attrs']:
                q_list.append({
                    'station': n,
                    'slot': a['slot'],
                    'q': f"[{L['title']} #{n}] 「{a['obj']}」이(가) 가리키는 [{a['slot']}]은?",
                    'a': a['fact'],
                    'src': st.get('src', []),
                })
            st['tts'] = make_tts.to_reading(st.get('say', ''))

        jpath.write_text(json.dumps(L, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        (CARBON / 'questions' / f'{lid}.json').write_text(json.dumps({'lesson_id': lid, 'questions': q_list}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print('Generated all 29 new Meridian lessons and updated mer-10, new-gr-07, new-gr-13.')


if __name__ == '__main__':
    build_mer_lessons()
