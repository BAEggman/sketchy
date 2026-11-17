#!/usr/bin/env python3
"""단계 B (4-2-1, 4-2-2): 의학사 속성 장부(hist_attrs.json)와 경락 교재 항목 장부(meridian_items.json) 생성."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # sketchy/
WORK = ROOT.parent                                   # sketchy_carbon/
TXT_DIR = WORK / 'refs/교재/_txt'
DECK = json.loads((WORK / 'refs/cards/deck.json').read_text(encoding='utf-8'))
CARDS_BY_ID = {c['id']: c for c in DECK}

GAERON_LINES = (TXT_DIR / '한의학개론_p001-250_최종.txt').read_text(encoding='utf-8').splitlines()
WB_LINES = (TXT_DIR / '한의학개론_문제집_정답_최종수정본_전체.txt').read_text(encoding='utf-8').splitlines()

HIST_CSV = list(csv.DictReader((WORK / 'refs/교재/학습자료/답지/의학사_정답한줄해설_검증형.csv').read_text(encoding='utf-8-sig').splitlines()))
MER_CSV = list(csv.DictReader((WORK / 'refs/교재/학습자료/답지/gyeongrak_answers_verified.csv').read_text(encoding='utf-8-sig').splitlines()))


def find_gaeron_ref(keywords, start_line=1, end_line=len(GAERON_LINES)):
    cur_p = 'p.1'
    for idx in range(start_line - 1, min(end_line, len(GAERON_LINES))):
        line = GAERON_LINES[idx]
        if line.startswith('원문 p.'):
            cur_p = line.replace('원문 ', '').split()[0]
        for kw in keywords:
            if kw and kw in line:
                return f"한의학개론_p001-250_최종.docx {cur_p} (L{idx + 1})"
    # Fallback full search
    cur_p = 'p.1'
    for idx, line in enumerate(GAERON_LINES):
        if line.startswith('원문 p.'):
            cur_p = line.replace('원문 ', '').split()[0]
        for kw in keywords:
            if kw and kw in line:
                return f"한의학개론_p001-250_최종.docx {cur_p} (L{idx + 1})"
    return "한의학_의학사_종합.docx / 문제집 해설"


def find_hist_wb_q(keywords):
    qs = []
    for r in HIST_CSV:
        txt = (r.get('question') or '') + ' ' + (r.get('one_line_explain') or '')
        if any(k and k in txt for k in keywords):
            qs.append(f"의학사-{r['q_no']}")
    for idx, line in enumerate(WB_LINES):
        if any(k and k in line for k in keywords):
            m = re.match(r'^(\d+)\.\s', line)
            if m and f"문제집-{m.group(1)}" not in qs and len(qs) < 6:
                qs.append(f"문제집-{m.group(1)}")
    return qs[:6]


def find_cards(keywords, base_ids=None):
    out = list(base_ids or [])
    for c in DECK:
        txt = c['q'] + ' ' + c['a']
        if any(k and k in txt for k in keywords):
            if c['id'] not in out:
                out.append(c['id'])
        if len(out) >= 8:
            break
    return out


# 최종안 3-5에 따른 의학사 과 분할 매핑 (14과 -> 21과)
HIST_SPLIT_MAP = {
    ('hist-01', 1): 'hist-01a', ('hist-01', 2): 'hist-01a', ('hist-01', 3): 'hist-01a',
    ('hist-01', 4): 'hist-01a', ('hist-01', 5): 'hist-01a',
    ('hist-01', 6): 'hist-01b', ('hist-01', 7): 'hist-01b', ('hist-01', 8): 'hist-01b',
    ('hist-01', 9): 'hist-01b', ('hist-01', 10): 'hist-01b', ('hist-01', 11): 'hist-01b',
    ('hist-02', 1): 'hist-02a', ('hist-02', 2): 'hist-02a', ('hist-02', 3): 'hist-02a', ('hist-02', 4): 'hist-02a',
    ('hist-02', 5): 'hist-02b', ('hist-02', 6): 'hist-02b', ('hist-02', 7): 'hist-02b', ('hist-02', 8): 'hist-02b',
    ('hist-02', 9): 'hist-12',  # 결정 9: 百濟新集方·新羅法師方을 hist-12로 이동
    ('hist-03', 1): 'hist-03a', ('hist-03', 2): 'hist-03a', ('hist-03', 3): 'hist-03a',
    ('hist-03', 4): 'hist-03a', ('hist-03', 5): 'hist-03a', ('hist-03', 6): 'hist-03a',
    ('hist-03', 7): 'hist-03b', ('hist-03', 8): 'hist-03b', ('hist-03', 9): 'hist-03b',
    ('hist-05', 1): 'hist-05a', ('hist-05', 2): 'hist-05a', ('hist-05', 3): 'hist-05a',
    ('hist-05', 4): 'hist-05a', ('hist-05', 5): 'hist-05a',
    ('hist-05', 6): 'hist-05b', ('hist-05', 7): 'hist-05b', ('hist-05', 8): 'hist-05b',
    ('hist-05', 9): 'hist-05b', ('hist-05', 10): 'hist-05b', ('hist-05', 11): 'hist-05b',
    ('hist-06', 2): 'hist-06a', ('hist-06', 3): 'hist-06a', ('hist-06', 4): 'hist-06a',
    ('hist-06', 5): 'hist-06a', ('hist-06', 6): 'hist-06a', ('hist-06', 7): 'hist-06a',
    ('hist-06', 9): 'hist-06a', ('hist-06', 10): 'hist-06a',
    ('hist-06', 1): 'hist-06b', ('hist-06', 8): 'hist-06b',
    ('hist-07', 1): 'hist-07a', ('hist-07', 2): 'hist-07a', ('hist-07', 3): 'hist-07a',
    ('hist-07', 4): 'hist-07a', ('hist-07', 5): 'hist-07a', ('hist-07', 6): 'hist-07a',
    ('hist-07', 10): 'hist-07a', ('hist-07', 11): 'hist-07a', ('hist-07', 12): 'hist-07a',
    ('hist-07', 7): 'hist-07b', ('hist-07', 8): 'hist-07b', ('hist-07', 9): 'hist-07b',
    ('hist-08', 1): 'hist-08a', ('hist-08', 2): 'hist-08a', ('hist-08', 3): 'hist-08a', ('hist-08', 4): 'hist-08a',
    ('hist-08', 5): 'hist-08b', ('hist-08', 6): 'hist-08b', ('hist-08', 7): 'hist-08b', ('hist-08', 8): 'hist-08b',
}

# 교재 괄호 또는 문제집 보기에 등장하여 그림 칸으로 올리는 字·號 목록 (최종안 2절)
HIGH_VALUE_JAHO = {
    '秦越人': '扁鵲(秦越人)',
    '仲景': '張機(仲景)',
    '啓玄子': '王冰(啓玄子)',
    '無擇': '陳言(無擇)',
    '潔古': '張元素(潔古)',
    '守眞': '劉完素(守眞·河間)',
    '子和': '張從正(子和·戴人)',
    '東垣': '李杲(東垣)',
    '丹溪': '朱震亨(丹溪)',
    '漢卿': '竇默(漢卿)',
    '伯仁': '滑壽(伯仁)',
    '濟時': '楊繼洲(濟時)',
    '景岳': '張介賓(景岳)',
    '士材': '李中梓(士材)',
    '靈胎': '徐大椿(靈胎)',
    '安道': '王履(安道)',
    '又可': '吳有性(又可)',
    '天士': '葉桂(天士)',
    '生白': '薛雪(生白)',
    '鞠通': '吳瑭(鞠通)',
    '孟英': '王士雄(孟英)',
    '茶山': '丁若鏞(茶山)',
    '東武': '李濟馬(東武)',
}


def parse_hist_station_slots(lid, st):
    """정거장 fact/hook/say에서 7개 속성 칸(이름·왕조·字號·서명·기여·의의·수)을 추출하고 현재 그림 담지 여부를 판정한다."""
    fact = st.get('fact', '')
    hook = st.get('hook', '')
    obj = st.get('obj', '')
    say = st.get('say', '')
    base_cards = st.get('src', [])
    target_lid = HIST_SPLIT_MAP.get((lid, st['n']), lid)

    slots = []

    # 1. 서명 (`『...』`)
    books = re.findall(r'『([^』]+)』', fact + ' ' + say)
    unique_books = []
    for b in books:
        if b not in unique_books:
            unique_books.append(b)

    # 2. 인명 추출
    person_patterns = [
        '扁鵲', '神農', '張仲景', '華佗', '王叔和', '葛洪',
        '陶弘景', '雷斅', '徐之才', '劉涓子', '全元起', '巢元方', '楊上善',
        '孫思邈', '甄權', '蘇敬', '孟詵', '陳藏器', '王燾', '王冰', '李珣',
        '錢乙', '許叔微', '陳無擇', '唐愼微', '寇宗奭', '張元素', '王好古', '李時珍', '趙學敏', '姚瀾',
        '成無己', '劉完素', '張從正', '李杲', '杜本', '朱震亨',
        '皇甫謐', '王惟一', '王執中', '竇默', '滑壽', '徐鳳', '楊繼洲', '吳謙', '李學川',
        '薛己', '張介賓', '張景岳', '趙獻可', '孫一奎', '李中梓', '徐大椿',
        '王履', '吳有性', '葉桂', '薛雪', '吳瑭', '王士雄',
        '馬蒔', '汪昂', '沈金鰲', '王淸任',
        '金永碩', '崔宗峻', '鄭道傳', '許浚', '鄭禮男', '許任', '아담 샬', '丁若鏞', '黃度淵', '李濟馬', '崔圭憲', '알렌'
    ]
    persons = [p for p in person_patterns if p in (fact + ' ' + say)]

    # 3. 왕조 추출
    dynasty_patterns = [
        '西漢', '東漢', '漢', '東晉', '晉', '梁', '北齊', '隋', '唐末·五代', '唐',
        '北宋', '南宋', '宋', '金', '元末明初', '元', '明末', '明', '淸',
        '百濟', '新羅', '高麗', '고려 말', '고려', '朝鮮 세종', '朝鮮', '개항'
    ]
    dynasty = None
    for d in dynasty_patterns:
        if d in fact or d in say:
            dynasty = d
            break

    # 4. 字·號 추출
    jaho_found = []
    for jh, label in HIGH_VALUE_JAHO.items():
        if jh in (fact + ' ' + say) or label.split('(')[0] in persons:
            if jh in (fact + ' ' + say) or jh in ('子和', '丹溪', '東垣', '漢卿', '伯仁', '濟時', '又可', '潔古', '景岳', '天士', '生白', '鞠通', '孟英', '安道', '守眞', '茶山', '東武', '秦越人', '仲景', '啓玄子', '無擇'):
                if label.split('(')[0] in (fact + ' ' + say):
                    jaho_found.append((jh, label))

    # 5. 의의 (최초 / 현존 최고 / 시조 / 方書之祖)
    sig = None
    m_sig = re.search(r'(현존\s*最古[^·—,\)]*|현존\s*최초[^·—,\)]*|세계\s*최초[^·—,\)]*|중국\s*최초[^·—,\)]*|최초의?\s*[^·—,\)]+|처음으로?\s*[^·—,\)]+|方書之祖|易水學派\s*시조|溫病學派\s*창시자)', fact + ' ' + say)
    if m_sig:
        sig = m_sig.group(1).strip()

    # 6. 수 (혈 수, 종수, 권수, 문답 수, 맥 수, 조문 수 등)
    nums = re.findall(r'(\d+(?:종|권|개|難|脈|혈|穴|具|類|편|篇|년제)|\b(?:349|354|359|360|361|365|730|716|24|28|33|36|81)\b)', fact)
    unique_nums = []
    for x in nums:
        if x not in unique_nums:
            unique_nums.append(x)

    kw_base = persons + unique_books[:2]
    if not kw_base:
        kw_base = [fact.split('—')[0].strip()[:8]]
    tb_ref = find_gaeron_ref(kw_base)
    wb_qs = find_hist_wb_q(kw_base)
    c_ids = find_cards(kw_base, base_cards)

    # 이름 칸
    if persons:
        p_str = '·'.join(persons)
        # 지금 그림이 이름 전체를 지는가? (성씨만 지거나 없으면 아니오/예 판정)
        carried = '예' if any(p[0] in hook or p in hook for p in persons) and not ('杜本' in p_str) else '아니오'
        if '陶弘景' in p_str or '吳謙' in p_str or '王冰' in p_str:
            # 陶만 지고 弘景 없음, 謙만 지고 吳 없음 등
            carried = '아니오(성·이름 일부만)'
        slots.append({
            'slot': '이름',
            'value': p_str,
            'textbook_ref': tb_ref,
            'workbook_q': wb_qs,
            'card_ids': c_ids,
            'carried_by_current_image': carried,
            'new_vessel': ['그림', '이야기', '문항'],
        })

    # 왕조 칸
    if dynasty:
        # 기존 그림에서 왕조가 직접 표지로 그려진 곳: hist-01(한옥=漢), hist-03(사탕=唐), hist-04(소나무=宋), hist-06(금광=金, 원두막=元), hist-08(등불=明, 유리=淸), hist-09(유리=淸)
        d_carried = '아니오'
        if lid == 'hist-01' and '漢' in dynasty:
            d_carried = '예(장소 한옥)'
        elif lid == 'hist-03' and dynasty == '唐':
            d_carried = '예(장소 사탕)'
        elif lid == 'hist-04' and '宋' in dynasty:
            d_carried = '예(장소 소나무)'
        elif lid == 'hist-06' and dynasty in ('金', '元'):
            d_carried = '예(금광·원두막)'
        elif lid == 'hist-08' and dynasty in ('明', '淸'):
            d_carried = '예(방 안 등불·문밖)'
        elif lid == 'hist-09' and dynasty == '淸':
            d_carried = '예(유리 온실)'
        vessel = ['그림', '이야기', '문항'] if dynasty != '北齊' else ['이야기', '문항']
        slots.append({
            'slot': '왕조',
            'value': dynasty,
            'textbook_ref': tb_ref,
            'workbook_q': wb_qs,
            'card_ids': c_ids,
            'carried_by_current_image': d_carried,
            'new_vessel': vessel,
        })

    # 字·號 칸
    if jaho_found:
        jh_str = ' · '.join(x[1] for x in jaho_found)
        jh_carried = '예' if any(x[0] in hook for x in jaho_found) else '아니오'
        slots.append({
            'slot': '字號',
            'value': jh_str,
            'textbook_ref': tb_ref,
            'workbook_q': wb_qs,
            'card_ids': c_ids,
            'carried_by_current_image': jh_carried,
            'new_vessel': ['그림', '이야기', '문항'],
        })

    # 서명 칸
    if unique_books:
        b_str = ' · '.join(f'『{b}』' for b in unique_books)
        b_carried = '예' if any(any(ch in hook for ch in b) for b in unique_books) else '아니오'
        slots.append({
            'slot': '서명',
            'value': b_str,
            'textbook_ref': tb_ref,
            'workbook_q': wb_qs,
            'card_ids': c_ids,
            'carried_by_current_image': b_carried,
            'new_vessel': ['그림', '이야기', '문항'],
        })

    # 기여 칸
    slots.append({
        'slot': '기여',
        'value': fact,
        'textbook_ref': tb_ref,
        'workbook_q': wb_qs,
        'card_ids': c_ids,
        'carried_by_current_image': '예' if hook else '아니오',
        'new_vessel': ['그림', '이야기', '문항'],
    })

    # 의의 칸
    if sig:
        s_carried = '예' if ('금메달' in obj or '금메달' in hook or '처방 쪽지' in obj) else '아니오'
        note = ''
        if '滑壽' in fact:
            note = '결정 8: 최초 天然色 經絡圖譜 = 滑壽(滑伯仁, 문제집 경락 239번·카드 기준). 이설: 의학사 108번 해설 陳會 『神應經』'
        slots.append({
            'slot': '의의',
            'value': sig,
            'textbook_ref': tb_ref,
            'workbook_q': wb_qs,
            'card_ids': c_ids,
            'carried_by_current_image': s_carried,
            'new_vessel': ['그림', '이야기', '문항'],
            **({'note': note} if note else {}),
        })

    # 수 칸
    if unique_nums:
        n_str = ' · '.join(unique_nums)
        # 기존 그림에서 3 이하(9권x2는 세어야 함, 6단 사다리, 3칸 금궤, 3단 선반 등)를 빼면 수는 대부분 못 짐
        n_carried = '예(3 이하 개수)' if any(x in ('3단', '2권', '2인') for x in unique_nums) else '아니오'
        note = ''
        if lid == 'hist-07' and st['n'] in (11, 12):
            note = '결정 1: 吳謙 『醫宗金鑑』 = 361혈로 확정(교재·문제집 의학사 41번·경락 144번). 李學川 정거장 퇴역, 針灸逢源은 이야기 한 줄로 유지'
        slots.append({
            'slot': '수',
            'value': n_str,
            'textbook_ref': tb_ref,
            'workbook_q': wb_qs,
            'card_ids': c_ids,
            'carried_by_current_image': n_carried,
            'new_vessel': ['그림', '이야기', '문항'],
            **({'note': note} if note else {}),
        })

    return {
        'lesson_id': lid,
        'target_lesson_v7': target_lid,
        'station_n': st['n'],
        'fact': fact,
        'current_obj': obj,
        'current_hook': hook,
        'slots': slots,
    }


def build_hist_ledger():
    ldir = ROOT / 'src/lessons/l'
    stations_out = []
    slot_totals = {'total': 0, 'carried_before': 0, 'carried_after_image': 0}

    for p in sorted(ldir.glob('hist-*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        lid = d['id']
        for st in d['stations']:
            if st.get('kind') in ('frame', 'review'):
                continue
            item = parse_hist_station_slots(lid, st)
            for sl in item['slots']:
                slot_totals['total'] += 1
                if sl['carried_by_current_image'].startswith('예'):
                    slot_totals['carried_before'] += 1
                if '그림' in sl['new_vessel']:
                    slot_totals['carried_after_image'] += 1
            stations_out.append(item)

    # 교재에 있으나 기존 hist-07에 빠졌던 高武 『鍼灸聚英』 · 汪機 『鍼灸問對』 · 河若愚 『流注指微賦』 추가
    extra_hist07b = [
        {
            'lesson_id': 'hist-07(신규보강)',
            'target_lesson_v7': 'hist-07b',
            'station_n': 901,
            'fact': '河若愚(金) 『流注指微賦』(『子午流注鍼經』) — 子午流注 침법의 시초',
            'current_obj': '(기존 과에 없음)',
            'current_hook': '(기존 과에 없음)',
            'slots': [
                {'slot': '이름', 'value': '河若愚', 'textbook_ref': '한의학개론_p001-250_최종.docx p.13 (L311)', 'workbook_q': ['의학사-92'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
                {'slot': '왕조', 'value': '金', 'textbook_ref': '한의학개론_p001-250_최종.docx p.13 (L311)', 'workbook_q': ['의학사-92'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
                {'slot': '서명', 'value': '『流注指微賦』(『子午流注鍼經』)', 'textbook_ref': '한의학개론_p001-250_최종.docx p.13 (L311)', 'workbook_q': ['의학사-92'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
                {'slot': '기여', 'value': '子午流注鍼法 출현', 'textbook_ref': '한의학개론_p001-250_최종.docx p.13 (L311)', 'workbook_q': ['의학사-92'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
            ]
        },
        {
            'lesson_id': 'hist-07(신규보강)',
            'target_lesson_v7': 'hist-07b',
            'station_n': 902,
            'fact': '高武(明) 『鍼灸聚英』(『鍼灸節要』) · 汪機(明) 『鍼灸問對』(『外科理例』)',
            'current_obj': '(기존 과에 없음)',
            'current_hook': '(기존 과에 없음)',
            'slots': [
                {'slot': '이름', 'value': '高武 · 汪機', 'textbook_ref': '한의학개론_p001-250_최종.docx p.16 (L411-412)', 'workbook_q': ['의학사-41'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
                {'slot': '왕조', 'value': '明', 'textbook_ref': '한의학개론_p001-250_최종.docx p.16 (L411-412)', 'workbook_q': ['의학사-41'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
                {'slot': '서명', 'value': '『鍼灸聚英』 · 『鍼灸問對』', 'textbook_ref': '한의학개론_p001-250_최종.docx p.16 (L411-412)', 'workbook_q': ['의학사-41'], 'card_ids': [], 'carried_by_current_image': '아니오', 'new_vessel': ['그림', '이야기', '문항']},
            ]
        }
    ]
    for item in extra_hist07b:
        for sl in item['slots']:
            slot_totals['total'] += 1
            slot_totals['carried_after_image'] += 1
        stations_out.append(item)

    out = {
        'version': 'carbon-v7-20261117',
        'summary': {
            'original_lessons': 14,
            'v7_lessons': 21,
            'total_stations_analyzed': len(stations_out),
            'total_attribute_slots': slot_totals['total'],
            'carried_by_image_before': slot_totals['carried_before'],
            'carried_by_image_after': slot_totals['carried_after_image'],
            'disputed_facts_logged': [
                '결정 1: 吳謙 『醫宗金鑑』 경혈 수 = 361혈(교재·문제집 의학사 41번·경락 144번 기준). 역사 기록(金鑑 360·李學川 針灸逢源 361)은 카드_교정목록.md에 메모로 기록.',
                '결정 8: 최초 天然色 經絡圖譜 = 滑壽(滑伯仁) 『十四經發揮』(문제집 경락 239번·카드 기준). 이설: 문제집 의학사 108번 해설 陳會 『神應經』.',
                '결정 9: 『百濟新集方』·『新羅法師方』(일본 『醫心方』 인용)을 hist-02에서 빼서 한국 의서 과 hist-12로 이동.'
            ]
        },
        'stations': stations_out,
    }
    dst = ROOT / 'carbon/ledger/hist_attrs.json'
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Saved {dst.relative_to(ROOT)}: {len(stations_out)} stations, {slot_totals['total']} slots (before={slot_totals['carried_before']}, after={slot_totals['carried_after_image']})")


# 舍岩 48방 정본 데이터 (library.json s18d06·s18d07, mer-11·mer-12, 카드 HUBGR-0203~0262, 사용자 문장 대조 완료)
SAAM_12 = [
    {
        'meridian': '手太陰肺經', 'short': '肺', 'element': '金', 'lesson_id': 'new-gr-19',
        'jeong': {'bo': ['太白', '太淵'], 'sa': ['少府', '魚際'], 'rule': '補母(土)·瀉官(火)', 'user_sentence': '태백산의 태연이가 어제 소부산으로 갔다.'},
        'seung': {'bo': ['少府', '魚際'], 'sa': ['尺澤', '陰谷'], 'rule': '補官(火)·瀉子(水)', 'user_sentence': '어제 소부친 걸 보니 음곡에서 척택을 사라지게 해야겠다.'},
        'han':   {'bo': ['少府', '魚際'], 'sa': ['尺澤', '陰谷'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['尺澤', '陰谷'], 'sa': ['太白', '太淵'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '太淵', 'sil_sa': '尺澤'},
        'jugaek': {'ju_won': '太淵', 'gaek_rak': '偏歷'},
        'cards': ['HUBGR-0203', 'HUBGR-0215', 'HUBGR-0216', 'HUBGR-0217', 'HUBGR-0218']
    },
    {
        'meridian': '手陽明大腸經', 'short': '大腸', 'element': '金', 'lesson_id': 'new-gr-20',
        'jeong': {'bo': ['足三里', '曲池'], 'sa': ['陽谷', '陽谿'], 'rule': '補母(土)·瀉官(火)', 'user_sentence': '삼리나 걸어 꼭지가 돌았는데 양계장의 양곡도 바닥났다.'},
        'seung': {'bo': ['陽谷', '陽谿'], 'sa': ['二間', '足通谷'], 'rule': '補官(火)·瀉子(水)', 'user_sentence': '양계장과 양곡창고를 잘 보살피고 통곡하고 이간질하는 놈들은 사퇴해.'},
        'han':   {'bo': ['陽谷', '陽谿'], 'sa': ['二間', '足通谷'], 'rule': '補火·瀉水 (※기존 s18d07·mer-12·HUBGR-0222의 解谿 오기를 陽谿로 교정)'},
        'yeol':  {'bo': ['二間', '足通谷'], 'sa': ['陽谷', '陽谿'], 'rule': '補水·瀉火(大腸·心·三焦 3경만 瀉火)'},
        'jagyeong': {'heo_bo': '曲池', 'sil_sa': '二間'},
        'jugaek': {'ju_won': '合谷', 'gaek_rak': '列缺'},
        'cards': ['HUBGR-0204', 'HUBGR-0219', 'HUBGR-0220', 'HUBGR-0221', 'HUBGR-0222']
    },
    {
        'meridian': '足陽明胃經', 'short': '胃', 'element': '土', 'lesson_id': 'new-gr-21',
        'jeong': {'bo': ['解谿', '陽谷'], 'sa': ['陷谷', '足臨泣'], 'rule': '補母(火)·瀉官(木)', 'user_sentence': '양곡가의 해계모니를 비판했더니 함곡령이 떨어져 임읍막음을 당했다.'},
        'seung': {'bo': ['陷谷', '足臨泣'], 'sa': ['厲兌', '商陽'], 'rule': '補官(木)·瀉子(金) (※카드 HUBGR-0205는 商丘 표기, s18d06·mer-11·사용자 문장 대조 기록)', 'user_sentence': '임읍막음 함곡령이 풀리나 보네, 여태 안 떠벌린 상구(상양)씨는 사퇴시키지 마.'},
        'han':   {'bo': ['解谿', '陽谷'], 'sa': ['內庭', '足通谷'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['內庭', '足通谷'], 'sa': ['足三里', '委中'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '解谿', 'sil_sa': '厲兌'},
        'jugaek': {'ju_won': '衝陽', 'gaek_rak': '公孫'},
        'cards': ['HUBGR-0205', 'HUBGR-0223', 'HUBGR-0224', 'HUBGR-0225', 'HUBGR-0226']
    },
    {
        'meridian': '足太陰脾經', 'short': '脾', 'element': '土', 'lesson_id': 'new-gr-22',
        'jeong': {'bo': ['大都', '少府'], 'sa': ['隱白', '大敦'], 'rule': '補母(火)·瀉官(木)', 'user_sentence': '소부에서 대도로 가서 대돈을 주고 은백색 말을 샀다.'},
        'seung': {'bo': ['隱白', '大敦'], 'sa': ['商丘', '經渠'], 'rule': '補官(木)·瀉子(金)', 'user_sentence': '대돈 주고 산 은백색 말을 잘 보관해, 경거망동하는 상구씨는 사퇴시키고.'},
        'han':   {'bo': ['大都', '少府'], 'sa': ['陰陵泉', '陰谷'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['陰陵泉', '陰谷'], 'sa': ['太白', '太谿'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '大都', 'sil_sa': '商丘'},
        'jugaek': {'ju_won': '太白', 'gaek_rak': '豊隆'},
        'cards': ['HUBGR-0206', 'HUBGR-0227', 'HUBGR-0228', 'HUBGR-0229', 'HUBGR-0230']
    },
    {
        'meridian': '手少陰心經', 'short': '心', 'element': '君火', 'lesson_id': 'new-gr-23',
        'jeong': {'bo': ['少衝', '大敦'], 'sa': ['少海', '陰谷'], 'rule': '補母(木)·瀉官(水)', 'user_sentence': '피엑스에서 대돈 주고 소충을 샀더니 음곡에서 소해되었다.'},
        'seung': {'bo': ['少海', '陰谷'], 'sa': ['神門', '太白'], 'rule': '補官(水)·瀉子(土)', 'user_sentence': '음곡에서 소해되고 나서 태백산에서 신문 돌린다.'},
        'han':   {'bo': ['少府', '然谷'], 'sa': ['少海', '陰谷'], 'rule': '補火·瀉水 (寒格에서만 心 = 腎 동일 처방)'},
        'yeol':  {'bo': ['少海', '陰谷'], 'sa': ['少府', '然谷'], 'rule': '補水·瀉火(大腸·心·三焦 3경만 瀉火)'},
        'jagyeong': {'heo_bo': '少衝', 'sil_sa': '神門'},
        'jugaek': {'ju_won': '神門', 'gaek_rak': '支正'},
        'cards': ['HUBGR-0207', 'HUBGR-0231', 'HUBGR-0232', 'HUBGR-0233', 'HUBGR-0234']
    },
    {
        'meridian': '手太陽小腸經', 'short': '小腸', 'element': '火', 'lesson_id': 'new-gr-24',
        'jeong': {'bo': ['後谿', '足臨泣'], 'sa': ['前谷', '足通谷'], 'rule': '補母(木)·瀉官(水)', 'user_sentence': '후계자에 대한 정보 임읍막음 했더니 전곡 사람들이 통곡했다.'},
        'seung': {'bo': ['前谷', '足通谷'], 'sa': ['小海', '足三里'], 'rule': '補官(水)·瀉子(土)', 'user_sentence': '통곡하는 전곡 사람들을 잘 보듬고, 삼리 걷던 소해는 사뿐히 무시해.'},
        'han':   {'bo': ['陽谷', '崑崙'], 'sa': ['前谷', '足通谷'], 'rule': '補火·瀉水 (寒格에서만 小腸 = 膀胱 동일 처방)'},
        'yeol':  {'bo': ['前谷', '足通谷'], 'sa': ['小海', '足三里'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '後谿', 'sil_sa': '小海'},
        'jugaek': {'ju_won': '腕骨', 'gaek_rak': '通里'},
        'cards': ['HUBGR-0208', 'HUBGR-0235', 'HUBGR-0236', 'HUBGR-0237', 'HUBGR-0238']
    },
    {
        'meridian': '足太陽膀胱經', 'short': '膀胱', 'element': '水', 'lesson_id': 'new-gr-25',
        'jeong': {'bo': ['至陰', '商陽'], 'sa': ['委中', '足三里'], 'rule': '補母(金)·瀉官(土)', 'user_sentence': '지음 상양히 위중한 삼리를 걷고 있다.'},
        'seung': {'bo': ['委中', '足三里'], 'sa': ['束骨', '足臨泣'], 'rule': '補官(土)·瀉子(木)', 'user_sentence': '삼리 걷는 위중한 길을 잘 보호하고 임읍에서 속골 썩이는 놈은 사라져라.'},
        'han':   {'bo': ['陽谷', '崑崙'], 'sa': ['前谷', '足通谷'], 'rule': '補火·瀉水 (寒格에서만 小腸 = 膀胱 동일 처방)'},
        'yeol':  {'bo': ['前谷', '足通谷'], 'sa': ['足三里', '委中'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '至陰', 'sil_sa': '束骨'},
        'jugaek': {'ju_won': '京骨', 'gaek_rak': '大鍾'},
        'cards': ['HUBGR-0209', 'HUBGR-0239', 'HUBGR-0240', 'HUBGR-0241', 'HUBGR-0242']
    },
    {
        'meridian': '足少陰腎經', 'short': '腎', 'element': '水', 'lesson_id': 'new-gr-26',
        'jeong': {'bo': ['復溜', '經渠'], 'sa': ['太谿', '太白'], 'rule': '補母(金)·瀉官(土)', 'user_sentence': '신발 신고 경거망동하게 복류이크댄스를 췄더니 태백산의 태계이황 선생님한테 꾸중들었다.'},
        'seung': {'bo': ['太谿', '太白'], 'sa': ['湧泉', '大敦'], 'rule': '補官(土)·瀉子(木)', 'user_sentence': '태백산 태계이황 선생님을 잘 보필하는 과정에서 대돈 주고 산 용천수를 드렸다.'},
        'han':   {'bo': ['少府', '然谷'], 'sa': ['陰谷', '少海'], 'rule': '補火·瀉水 (寒格에서만 心 = 腎 동일 처방)'},
        'yeol':  {'bo': ['陰谷', '少海'], 'sa': ['太白', '太谿'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '復溜', 'sil_sa': '湧泉'},
        'jugaek': {'ju_won': '太谿', 'gaek_rak': '飛揚'},
        'cards': ['HUBGR-0210', 'HUBGR-0243', 'HUBGR-0244', 'HUBGR-0245', 'HUBGR-0246']
    },
    {
        'meridian': '手厥陰心包經', 'short': '心包', 'element': '相火', 'lesson_id': 'new-gr-27',
        'jeong': {'bo': ['中衝', '大敦'], 'sa': ['曲澤', '陰谷'], 'rule': '補母(木)·瀉官(水)', 'user_sentence': '심뽀부려 대돈 주고 중고 충전기 샀더니 음곡에서 곡택 소리 나게 맞았다.'},
        'seung': {'bo': ['曲澤', '陰谷'], 'sa': ['大陵', '太白'], 'rule': '補官(水)·瀉子(土)', 'user_sentence': '음곡에서 곡택 마련의 꿈을 꾸었지만 현실은 태백산에서 대릉만족해야 된다.'},
        'han':   {'bo': ['少府', '勞宮'], 'sa': ['曲澤', '少海'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['曲澤', '少海'], 'sa': ['太白', '大陵'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '中衝', 'sil_sa': '大陵'},
        'jugaek': {'ju_won': '大陵', 'gaek_rak': '外關'},
        'cards': ['HUBGR-0211', 'HUBGR-0247', 'HUBGR-0248', 'HUBGR-0249', 'HUBGR-0250']
    },
    {
        'meridian': '手少陽三焦經', 'short': '三焦', 'element': '相火', 'lesson_id': 'new-gr-28',
        'jeong': {'bo': ['中渚', '足臨泣'], 'sa': ['液門', '足通谷'], 'rule': '補母(木)·瀉官(水)', 'user_sentence': '삼초 만에 임읍막음당한 다음 중저가 폰 뺏기고 액문 앞에서 통곡했다.'},
        'seung': {'bo': ['液門', '足通谷'], 'sa': ['天井', '足三里'], 'rule': '補官(水)·瀉子(土)', 'user_sentence': '통곡하는 액문을 잘 보호하고 천정에서 삼리를 걸으면 사라진다.'},
        'han':   {'bo': ['支溝', '崑崙'], 'sa': ['液門', '足通谷'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['液門', '足通谷'], 'sa': ['支溝', '崑崙'], 'rule': '補水·瀉火(大腸·心·三焦 3경만 瀉火)'},
        'jagyeong': {'heo_bo': '中渚', 'sil_sa': '天井'},
        'jugaek': {'ju_won': '陽池', 'gaek_rak': '內關'},
        'cards': ['HUBGR-0212', 'HUBGR-0251', 'HUBGR-0252', 'HUBGR-0253', 'HUBGR-0254']
    },
    {
        'meridian': '足少陽膽經', 'short': '膽', 'element': '木', 'lesson_id': 'new-gr-29',
        'jeong': {'bo': ['俠谿', '足通谷'], 'sa': ['足竅陰', '商陽'], 'rule': '補母(水)·瀉官(金)', 'user_sentence': '담이 작아 통곡하는 협계를 비웃다가 상양한 척 규음음척 했다.'},
        'seung': {'bo': ['足竅陰', '商陽'], 'sa': ['陽輔', '陽谷'], 'rule': '補官(金)·瀉子(火)', 'user_sentence': '상양한 척 규음은 척 보살피고 양곡 양보 안 하는 형님은 사라져.'},
        'han':   {'bo': ['陽輔', '陽谷'], 'sa': ['俠谿', '足通谷'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['俠谿', '足通谷'], 'sa': ['委中', '陽陵泉'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '俠谿', 'sil_sa': '陽輔'},
        'jugaek': {'ju_won': '丘墟', 'gaek_rak': '蠡溝'},
        'cards': ['HUBGR-0213', 'HUBGR-0255', 'HUBGR-0256', 'HUBGR-0257', 'HUBGR-0258']
    },
    {
        'meridian': '足厥陰肝經', 'short': '肝', 'element': '木', 'lesson_id': 'new-gr-30',
        'jeong': {'bo': ['曲泉', '陰谷'], 'sa': ['中封', '經渠'], 'rule': '補母(水)·瀉官(金)', 'user_sentence': '음곡에서 곡천 번다고 하는 소리를 중봉 군은 경거해야 해.'},
        'seung': {'bo': ['中封', '經渠'], 'sa': ['行間', '少府'], 'rule': '補官(金)·瀉子(火)', 'user_sentence': '경거망동하지 말고 중봉 군을 잘 보살피고 소부에서 행간 띄우는 놈은 사라져.'},
        'han':   {'bo': ['行間', '少府'], 'sa': ['陰谷', '曲泉'], 'rule': '補火·瀉水'},
        'yeol':  {'bo': ['陰谷', '曲泉'], 'sa': ['太衝', '太白'], 'rule': '補水·瀉土'},
        'jagyeong': {'heo_bo': '曲泉', 'sil_sa': '行間'},
        'jugaek': {'ju_won': '太衝', 'gaek_rak': '光明'},
        'cards': ['HUBGR-0214', 'HUBGR-0259', 'HUBGR-0260', 'HUBGR-0261', 'HUBGR-0262']
    },
]


def build_meridian_ledger():
    """교재 제5장 경락(개론 L1614~2114, 총강 L1287~1820, 5장 요약 발췌)을 항목 단위로 쪼개어 전후 상태를 기록한다."""
    ldir = ROOT / 'src/lessons/l'
    existing_mer_text = ''
    for p in sorted(list(ldir.glob('mer-*.json')) + list(ldir.glob('new-gr-*.json'))):
        existing_mer_text += p.read_text(encoding='utf-8') + '\n'

    items = []
    cur_p = 'p.66'
    cur_sec = '제1절 經絡의 槪念'

    for idx in range(1613, 2114):
        line = GAERON_LINES[idx].strip()
        if not line:
            continue
        if line.startswith('원문 p.'):
            cur_p = line.replace('원문 ', '').split()[0]
            continue
        if re.match(r'^제\d+절', line):
            cur_sec = line
            continue

        # 항목 분류 및 현행 그릇 판정
        before_status = '있음'
        before_vessels = []
        after_vessels = []

        if '349' in line or '354' in line or '359' in line or '361' in line or '醫宗金鑒' in line or '鍼灸甲乙經' in line:
            before_status = '글로만'
            before_vessels = ['hist-07(글로만, 그림에 수 부호 없음)', 's18d01(도해)']
            after_vessels = ['hist-07a(그림 수 부호+문항)', 's18d01(도해)']
        elif '兩肘' in line or '兩腋' in line or '兩髀' in line or '兩膕' in line or '切尺膚' in line or '切兪募' in line or '前頭痛' in line or '診絡' in line:
            before_status = '약함'
            before_vessels = ['new-uk-01(일부)', 'new-zj-24(두통 일부)']
            after_vessels = ['new-gr-39(경락 진단 전담 과)', '문항']
        elif '標本' in line or '根結' in line:
            before_status = '약함'
            before_vessels = ['new-gr-15(개념만, 혈 짝 없음)']
            after_vessels = ['new-gr-15', 's18d13(標本根結 혈 짝 코드 도해)', 'carbon/cards_draft.tsv']
        elif '流走' in line or any(k in line for k in ['肺手太陰之脈', '大腸手陽明之脈', '胃足陽明之脈', '脾足太陰之脈', '心手少陰之脈', '小腸手太陽之脈', '膀胱足太陽之脈', '腎足少陰之脈', '心主手厥陰', '三焦手少陽之脈', '膽足少陽之脈', '肝足厥陰之脈']):
            before_status = '약함'
            before_vessels = ['new-gr-09(표지 9개만)']
            after_vessels = ['new-gr-09', 'new-gr-42~47(조건부 流注 원문 6과)', 'carbon/cards_draft.tsv']
        elif re.match(r'^［經穴圖］|^(LU|LI|ST|SP|HT|SI|BL|KI|PC|TE|GB|LR|GV|CV)\d+', line) or '經穴 분포' in line:
            before_status = '없음'
            before_vessels = []
            after_vessels = ['new-gr-31(경맥 혈 수 手)', 'new-gr-32(경맥 혈 수 足)', 's18d12(경맥 혈 수 코드 도해)', 'carbon/cards_draft.tsv']
        elif '同音이면서 漢文이 틀린 穴名' in line:
            before_status = '없음'
            before_vessels = []
            after_vessels = ['new-gr-41(같은 이름 혈 전담 과)', '문항']
        elif '세 가지 學說' in line or ('靈樞 經脈篇' in line and '大絡' in line) or ('難經' in line and '陽絡' in line) or '醫門法律' in line:
            before_status = '없음'
            before_vessels = []
            after_vessels = ['mer-10(구역 편집 정거장 3개 추가)', '문항']
        elif '郄穴' in line or ('孔最' in line and '溫溜' in line) or ('梁丘' in line and '地機' in line):
            before_status = '없음'
            before_vessels = ['카드 일부만']
            after_vessels = ['new-gr-33(郄穴 手)', 'new-gr-34(郄穴 足+奇經)', 'carbon/songs/geuk_16.md(노래)', '문항']
        elif '八脈交會穴' in line or ('公孫' in line and '衝脈' in line) or ('內關' in line and '陰維' in line) or ('後谿' in line and '督脈' in line) or ('申脈' in line and '陽蹻' in line) or ('足臨泣' in line and '帶脈' in line) or ('外關' in line and '陽維' in line) or ('列缺' in line and '任脈' in line) or ('照海' in line and '陰蹻' in line):
            before_status = '글로만'
            before_vessels = ['카드만, 전담 그림 과 없음']
            after_vessels = ['new-gr-37(八脈交會 여덟 짝 전담 과)', '문항']
        elif 'AM3-5' in line or '5-7' in line or '7-9' in line or '9-11' in line or '11-13' in line or 'PM1-3' in line or '3尺5寸' in line:
            before_status = '없음'
            before_vessels = []
            after_vessels = ['new-gr-31·32(경맥 혈 수)', 'new-gr-35(子午流注)', 'new-gr-07(출발 시각 보강)', 's18d11(子午流注 시계 도해)', 's18d12(경맥 혈 수 표 도해)']
        elif '28혈' in line or '24혈' in line:
            before_status = '약함'
            before_vessels = ['new-gr-13(주사위 눈으로만 표기)']
            after_vessels = ['new-gr-13(숫자 물건 28·24·12로 보강)', '문항']
        else:
            before_status = '있음'
            before_vessels = ['기존 mer-02~13 / new-gr-01~18 정거장 및 카드']
            after_vessels = ['기존 mer-02~13 / new-gr-01~18 정거장 및 카드']

        items.append({
            'id': f'MER-L{idx + 1}',
            'source': f'한의학개론_p001-250_최종.docx {cur_p} (L{idx + 1})',
            'section': cur_sec,
            'text': line[:180],
            'before_status': before_status,
            'before_vessels': before_vessels,
            'after_status': '있음',
            'after_vessels': after_vessels,
        })

    # 사용자 요약본 · 총강 · 특수 주제 추가 항목 (骨度法, 中風七處穴, 東垣 引經藥, 舍岩 48방)
    extra_topics = [
        {
            'id': 'MER-EXTRA-GOLDO',
            'source': '5장경락_사용자요약_발췌.md 3절 骨度法 & 한의학총강',
            'section': '骨度分寸法 (전신 치수)',
            'text': '두부(전발제~후발제 12촌, 양 유양돌기 9촌, 미간~전발제 3촌, 후발제~대추 3촌) · 흉복부(천돌~흉골체하연 9촌, 양 유두 8촌, 흉골체하연~배꼽 8촌, 배꼽~치골상연 5촌) · 상지(액와~주횡문 9촌, 주횡문~완횡문 12촌) · 측흉요(액와~11늑골단 12촌, 11늑골단~대전자 9촌) · 하지(대전자~슬와 19촌, 치골상연~내측과상연 18촌, 슬와~외과첨 16촌, 슬개골하연~내과첨 15촌, 둔구~오금 14촌, 내측과하연~내과첨 13촌, 외과첨~족저 3촌)',
            'before_status': '없음',
            'before_vessels': [],
            'after_status': '있음',
            'after_vessels': ['new-gr-36(骨度 같은 수끼리 모은 과)', 's18d10(骨度 전체 치수 코드 도해)', '문항'],
        },
        {
            'id': 'MER-EXTRA-JUNGPOONG7',
            'source': '5장경락_사용자요약_발췌.md 6절 주요 상용혈',
            'section': '中風七處穴과 손끝 구급혈(兩商·兩間·十宣·十二井)',
            'text': '中風七處穴(百會·肩井·曲池·風市·足三里·絶骨[懸鍾]·曲鬢) 및 兩商(少商·商陽)·兩間(二間·三間)·十宣穴',
            'before_status': '없음',
            'before_vessels': [],
            'after_status': '있음',
            'after_vessels': ['new-gr-38(中風七處穴과 손끝 구급혈 과)', '문항'],
        },
        {
            'id': 'MER-EXTRA-INGYEONG',
            'source': '한의학개론 p.13/p.188 & 본초 引經報使',
            'section': '東垣 十二經 引經報使 약물',
            'text': '手太陰肺(升麻·白芷·蔥白·桔梗) · 手陽明大腸(白芷·升麻·石膏) · 足陽明胃(白芷·升麻·石膏·葛根) · 足太陰脾(升麻·蒼朮·葛根·白芍) · 手少陰心(黃連·細辛) · 手太陽小腸(本·黃柏) · 足太陽膀胱(羌活) · 足少陰腎(獨活·知母·桂皮·細辛) · 手厥陰心包(柴胡·牡丹皮) · 手少陽三焦(柴胡·連翹, 상초 黃芩·중초 靑皮·하초 附子) · 足少陽膽(柴胡·靑皮) · 足厥陰肝(柴胡·川芎·靑皮·吳茱萸)',
            'before_status': '약함',
            'before_vessels': ['hp-06 #6(일부 예만), new-etc-15(두통 인경만)'],
            'after_status': '있음',
            'after_vessels': ['new-gr-40(東垣 引經藥 전담 과)', '문항'],
        },
    ]
    items.extend(extra_topics)

    # 舍岩 48방(12경 × 4격) 항목 추가
    for s in SAAM_12:
        items.append({
            'id': f"MER-SAAM-{s['short']}",
            'source': f"library.json s18d06·s18d07, mer-11·mer-12, 5장경락_사용자요약_발췌.md 9절 ({s['meridian']})",
            'section': '舍岩鍼法 48방 (正格·勝格·寒格·熱格 + 自經·主客)',
            'text': f"{s['meridian']} — 正格(補{','.join(s['jeong']['bo'])}/瀉{','.join(s['jeong']['sa'])}) · 勝格(補{','.join(s['seung']['bo'])}/瀉{','.join(s['seung']['sa'])}) · 寒格(補{','.join(s['han']['bo'])}/瀉{','.join(s['han']['sa'])}) · 熱格(補{','.join(s['yeol']['bo'])}/瀉{','.join(s['yeol']['sa'])})",
            'before_status': '있음' if s['short'] == '肺' else ('약함' if s['short'] in ('脾', '膀胱') else '글로만'),
            'before_vessels': ['mer-11·mer-12 내레이션 줄글 및 s18d06·s18d07 도해, 카드 HUBGR'],
            'after_status': '있음',
            'after_vessels': [f"{s['lesson_id']}(舍岩 {s['short']} 전담 그림 과)", 's18d06·s18d07(도해)', f"카드 {','.join(s['cards'])}"],
        })

    counts_before = {'없음': 0, '글로만': 0, '약함': 0, '있음': 0}
    counts_after = {'없음': 0, '글로만': 0, '약함': 0, '있음': 0}
    for it in items:
        counts_before[it['before_status']] += 1
        counts_after[it['after_status']] += 1

    out = {
        'version': 'carbon-v7-20261117',
        'summary': {
            'total_items': len(items),
            'before_counts': counts_before,
            'after_counts': counts_after,
            'saam_48_audit_note': 's18d07·mer-12·HUBGR-0222의 大腸 寒格 補火/熱格 瀉火 「陽谷·解谿」를 「陽谷·陽谿」로 교정 완료(BLOCKERS.md 및 카드_교정목록.md 기록).',
        },
        'saam_48_table': SAAM_12,
        'items': items,
    }
    dst = ROOT / 'carbon/ledger/meridian_items.json'
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Saved {dst.relative_to(ROOT)}: {len(items)} items, before={counts_before}, after={counts_after}")


if __name__ == '__main__':
    build_hist_ledger()
    build_meridian_ledger()
