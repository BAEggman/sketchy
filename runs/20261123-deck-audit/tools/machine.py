# -*- coding: utf-8 -*-
"""덱 감사 걸음 1 — 기계 점검 (전수). 저장소 파일은 읽기만 한다.

내는 것(runs/20261123-deck-audit/):
  machine.json   과 · 정거장 꼴, 무리, 장, 녹음, 카드, 옛 감사 흡수
  readings.json  낭독 대본(say ↔ tts)을 맞대어 뽑은 한자 → 한글 독음표(표결)
  terms.json     정거장마다 사실 칸의 한자 낱말 · 독음 · 물건/고리 칸에 소리가 드러나나
  carriers.json  물건 낱말 → 뜻 장부와 충돌(같은 낱말 다른 뜻 · 같은 뜻 다른 물건 · 사전과 다른 꼴)
실행: python3 runs/20261123-deck-audit/tools/machine.py
"""
import json, glob, os, re, difflib, subprocess
from collections import Counter, defaultdict

R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(R, 'runs', '20261123-deck-audit')
HAN = re.compile(r'[㐀-䶿一-鿿豈-﫿]')
HANW = re.compile(r'[㐀-䶿一-鿿豈-﫿]{2,}')
HANGUL = re.compile(r'[가-힣]')

def load(p):
    return json.load(open(os.path.join(R, p), encoding='utf-8'))

# ── 과 · 목차 ─────────────────────────────────────────────
cur = load('src/lessons/curriculum.json')
chap = {}; order = []
for c in cur['chapters']:
    for s in c['sections']:
        for it in s['items']:
            chap[it['lesson']] = c['id']; order.append(it['lesson'])
for it in cur.get('shelf', []):
    chap[it['lesson']] = 'shelf'
L = {}
for p in sorted(glob.glob(os.path.join(R, 'src/lessons/l/*.json'))):
    d = json.load(open(p, encoding='utf-8')); L[d['id']] = d

# 11-27 커밋에서 그림이 바뀌거나 새로 생긴 과
def git(*a):
    return subprocess.run(['git', '-C', R] + list(a), capture_output=True, text=True).stdout
changed_1127 = set()
for ln in git('diff', '--name-status', '68c88dd', '8c2dd18', '--', 'images/lessons/').splitlines():
    st, *ps = ln.split('\t')
    if st in ('M', 'A'):
        changed_1127.add(os.path.basename(ps[-1]).rsplit('.', 1)[0])

def group(lid):
    if re.match(r'^(hist-|suchi-|fan18|wei19|qiqing-|pilot-)', lid):
        return 'A'
    m = re.match(r'^new-gr-(\d+)$', lid)
    if m and 19 <= int(m.group(1)) <= 47:
        return 'B'
    if lid in changed_1127:
        return 'A2'          # 11-27에 다시 만든 옛 과
    return 'C'

# ── 녹음 ─────────────────────────────────────────────────
man = load('audio/narration/manifest.json')
recs = man['records'] if isinstance(man['records'], list) else list(man['records'].values())
rec = set()
for r in recs:
    m = re.search(r'([A-Za-z0-9\-]+)__s(\d+)__', r.get('src', ''))
    if m:
        rec.add((m.group(1), int(m.group(2))))

# ── 카드 지도(11-17 판) ───────────────────────────────────
lmap = load('src/lessons/lesson_map.json')['lessons']
map_cards = defaultdict(set)
for les in lmap:
    for st in les.get('stations', []):
        for c in st.get('cards', []):
            map_cards[c].add(les['id'])

# ── 독음표: say(한자 섞임) ↔ tts(한글) 맞대기 ────────────
votes = defaultdict(Counter)
def norm(t):
    return re.sub(r'[^㐀-䶿一-鿿豈-﫿가-힣0-9A-Za-z]', '', t)
for d in L.values():
    for s in d['stations']:
        a, b = norm(s.get('say', '')), norm(s.get('tts', ''))
        if not a or not b or not HAN.search(a):
            continue
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'replace' and (i2 - i1) == (j2 - j1):
                seg, rd = a[i1:i2], b[j1:j2]
                if all(HAN.match(ch) for ch in seg) and all(HANGUL.match(ch) for ch in rd):
                    for ch, r_ in zip(seg, rd):
                        votes[ch][r_] += 1
herbs = load('src/dict/herbs.json')
herb_items = herbs if isinstance(herbs, list) else (herbs.get('herbs') or herbs.get('items') or list(herbs.values()))
for h in herb_items:
    hz, rd = h.get('hanja', ''), h.get('reading', '')
    if len(hz) == len(rd):
        for ch, r_ in zip(hz, rd):
            votes[ch][r_] += 3
readings = {ch: c.most_common(2) for ch, c in votes.items()}
json.dump({ch: [[r, n] for r, n in v] for ch, v in readings.items()},
          open(os.path.join(OUT, 'readings.json'), 'w', encoding='utf-8'), ensure_ascii=False)

def read(word):
    out = []
    for ch in word:
        v = readings.get(ch)
        if not v:
            return None
        out.append(v[0][0])
    return ''.join(out)

def dueum(r):  # 두음 법칙 변형도 맞는 것으로 본다(녀→여, 력→역 …)
    alts = {r}
    first = {'녀': '여', '뇨': '요', '뉴': '유', '니': '이', '랴': '야', '려': '여', '례': '예', '료': '요',
             '류': '유', '리': '이', '라': '나', '래': '내', '로': '노', '뢰': '뇌', '루': '누', '르': '느',
             '력': '역', '련': '연', '렬': '열', '렴': '염', '령': '영', '록': '녹', '론': '논', '룡': '용',
             '륙': '육', '륜': '윤', '률': '율', '륭': '융', '릉': '능', '림': '임', '립': '입', '략': '약', '량': '양', '녕': '영'}
    if r and r[0] in first:
        alts.add(first[r[0]] + r[1:])
    return alts

# ── 정거장 훑기 ───────────────────────────────────────────
stations = []; terms = []; carriers = defaultdict(lambda: defaultdict(set)); term_carriers = defaultdict(lambda: defaultdict(set))
lesson_rows = []
all_src_cards = set()
for lid, d in L.items():
    g, ch = group(lid), chap.get(lid, '?')
    st_list = d['stations']
    n_content = 0
    img = os.path.join(R, d['image']) if not d['image'].startswith('http') else None
    for s in st_list:
        kind = s.get('kind') or s.get('role') or ''
        content = kind not in ('frame', 'review')
        fact = s.get('fact', ''); obj = s.get('obj', ''); hook = s.get('hook', '')
        src = s.get('src') or []
        if isinstance(src, str):
            src = [src]
        cards = [x for x in src if re.match(r'^[A-Z][A-Z0-9\-]+$', str(x))]
        all_src_cards.update(cards)
        tb = [x for x in src if '교재' in str(x)]
        box = s.get('box') or []
        boxes = box if (box and isinstance(box[0], list)) else ([box] if len(box) == 4 else [])
        area = sum(b[2] * b[3] for b in boxes if len(b) == 4)
        segs = len([x for x in re.split(r'[·/|;]', fact) if x.strip()])
        words = sorted(set(HANW.findall(fact)))
        carrier_text = obj + ' ' + re.sub(HAN, '', hook)
        found = []; missing = []; unknown = []
        for w in words:
            rd = read(w)
            if rd is None:
                unknown.append(w); continue
            if any(a in carrier_text for a in dueum(rd)):
                found.append(w)
            else:
                missing.append(w)
        row = {'lesson': lid, 'n': s.get('n'), 'group': g, 'chapter': ch, 'kind': kind or 'content',
               'content': content, 'fact_len': len(fact), 'fact_segments': segs,
               'multi_fact': content and (segs >= 4 or '/' in fact), 'src_cards': len(cards), 'src_textbook': len(tb),
               'src_none': content and not src, 'box': box,
               'boxes': len(boxes),
               'box_small': bool(boxes) and area < 0.004 * d['w'] * d['h'],
               'box_full': bool(boxes) and area > 0.9 * d['w'] * d['h'],
               'recorded': (lid, s.get('n')) in rec}
        if content:
            n_content += 1
            row['terms'] = len(words); row['sound_shown'] = found; row['sound_missing'] = missing; row['reading_unknown'] = unknown
            row['any_sound_shown'] = bool(found)
            terms.append({'lesson': lid, 'n': s.get('n'), 'group': g, 'chapter': ch,
                          'terms': [{'w': w, 'r': read(w), 'shown': w in found} for w in words]})
        # 물건 낱말 → 뜻 (hook의 「X = Y」 · 「X → Y」)
        for part in re.split(r'\s·\s|;', hook):
            m = re.match(r'\s*(.+?)\s*(?:=|→)\s*(.+)$', part)
            if not m:
                continue
            left, right = m.group(1).strip(), m.group(2).strip()
            left = re.sub(r'[「」『』()（）]', '', left)[:30]
            mean = HANW.findall(right) or HAN.findall(right)[:1]
            if not left or not mean:
                continue
            for mw in mean[:2]:
                carriers[left][mw].add(f'{lid}#{s.get("n")}')
                term_carriers[mw][left].add(f'{lid}#{s.get("n")}')
        stations.append(row)
    lesson_rows.append({'lesson': lid, 'title': d['title'], 'group': g, 'chapter': ch, 'stations': len(st_list),
                        'content_stations': n_content, 'image': d['image'], 'w': d['w'], 'h': d['h'],
                        'lowres': d['w'] < 1600, 'few_stations': len(st_list) < 6,
                        'recorded_stations': sum(1 for s in st_list if (lid, s.get('n')) in rec)})

# 카드 끊김: 11-17 지도에 있으나 지금 어느 근거 칸에도 없는 카드
broken = sorted(c for c in map_cards if c not in all_src_cards)
broken_rows = [{'card': c, 'was_in': sorted(map_cards[c])} for c in broken]

# 사전과 다른 꼴: 사실 칸에 약 이름이 있는데 그 정거장 물건/고리에 사전 운반 낱말이 하나도 없음
herb_by_hz = {}
for h in herb_items:
    car = h.get('carriers')
    if isinstance(car, str):
        try:
            car = json.loads(car.replace("'", '"'))
        except Exception:
            car = [car]
    herb_by_hz[h['hanja']] = {'hid': h.get('hid'), 'reading': h.get('reading'), 'carriers': car or [], 'status': h.get('status'), 'cue': h.get('cue')}
herb_hits = []
for d in L.values():
    for s in d['stations']:
        if (s.get('kind') or s.get('role')) in ('frame', 'review'):
            continue
        txt = s.get('obj', '') + ' ' + s.get('hook', '')
        for hz, h in herb_by_hz.items():
            if hz in s.get('fact', ''):
                keys = [c for c in h['carriers'] if c]
                ok = any(k.split()[0] in txt for k in keys) if keys else None
                herb_hits.append({'lesson': d['id'], 'n': s.get('n'), 'group': group(d['id']), 'herb': hz,
                                  'dict_cue': h['cue'], 'uses_dict_carrier': ok, 'obj': s.get('obj', '')[:80]})

# 옛 감사(GPT 11-20) 흡수
va = load('docs/narration-review-20261120/visual-audit.json')
obs = va.get('observations', [])
old = []
for o in (obs if isinstance(obs, list) else []):
    st = str(o.get('status', o.get('result', '')))
    if re.search(r'불일치|mismatch|미확정|unverified|uncertain', st, re.I):
        lid = o.get('lesson') or o.get('lesson_id') or o.get('id')
        old.append({'lesson': lid, 'status': st, 'note': str(o.get('note') or o.get('detail') or '')[:160],
                    'now': ('과 없음' if lid not in L else ('그림 바뀜(11-20 뒤 새 문법 · 11-27)' if group(lid) in ('A', 'A2') else '그림 그대로 — 남음 후보'))})

def summ(rows, key):
    out = defaultdict(Counter)
    for r in rows:
        k = r[key]; c = out[k]
        c['stations'] += 1
        if r['content']:
            c['content'] += 1
            c['multi_fact'] += r['multi_fact']; c['sound_shown'] += r.get('any_sound_shown', False)
            c['src_none'] += r['src_none']; c['src_cards'] += bool(r['src_cards']); c['src_textbook'] += bool(r['src_textbook'])
        c['multi_box'] += r['content'] and r['boxes'] > 1
        c['fact_over60'] += r['fact_len'] > 60; c['box_small'] += r['box_small']; c['box_full'] += r['box_full']; c['recorded'] += r['recorded']
    return {k: dict(v) for k, v in out.items()}

conflict_same_word = {w: {m: sorted(v) for m, v in ms.items()} for w, ms in carriers.items() if len(ms) > 1}
conflict_same_term = {m: {w: sorted(v) for w, v in ws.items()} for m, ws in term_carriers.items()
                      if len({re.sub(r'\s+', '', w)[:6] for w in ws}) > 2}
overuse = {w: sum(len(v) for v in ms.values()) for w, ms in carriers.items() if sum(len(v) for v in ms.values()) >= 3}

machine = {
    'base_commit': git('rev-parse', '--short', 'HEAD').strip(), 'lessons': len(L),
    'toc': len(order), 'shelf': len(cur.get('shelf', [])), 'stations': len(stations),
    'recordings': len(recs), 'reading_chars': len(readings),
    'by_group': summ(stations, 'group'), 'by_chapter': summ(stations, 'chapter'),
    'lessons_detail': lesson_rows,
    'flags': {'few_stations': [r['lesson'] for r in lesson_rows if r['few_stations']],
              'lowres': [r['lesson'] for r in lesson_rows if r['lowres']],
              'box_full': [f"{r['lesson']}#{r['n']}" for r in stations if r['box_full']]},
    'broken_cards': {'count': len(broken), 'of_map_cards': len(map_cards), 'rows': broken_rows},
    'herb_dict_vs_lessons': {'hits': len(herb_hits), 'not_using_dict_carrier': sum(1 for h in herb_hits if h['uses_dict_carrier'] is False), 'rows': herb_hits},
    'old_visual_audit': old,
    'changed_1127': sorted(changed_1127),
}
json.dump(machine, open(os.path.join(OUT, 'machine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(terms, open(os.path.join(OUT, 'terms.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({'same_word_many_meanings': conflict_same_word, 'same_term_many_objects': conflict_same_term,
           'word_used_3plus': dict(sorted(overuse.items(), key=lambda x: -x[1]))},
          open(os.path.join(OUT, 'carriers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(OUT, 'stations_machine.jsonl'), 'w', encoding='utf-8') as f:
    for r in stations:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('과', len(L), '· 목차', len(order), '· 보관함', len(cur.get('shelf', [])), '· 정거장', len(stations), '· 녹음', len(recs), '· 독음 글자', len(readings))
for g, v in sorted(machine['by_group'].items()):
    print(' 무리', g, v)
print(' 카드 끊김', len(broken), '/', len(map_cards), '· 사전 약 언급', len(herb_hits), '· 사전 꼴 안 씀', machine['herb_dict_vs_lessons']['not_using_dict_carrier'])
print(' 같은 물건 낱말 다른 뜻', len(conflict_same_word), '· 같은 뜻 물건 셋 이상', len(conflict_same_term), '· 옛 감사 남은 후보', sum(1 for o in old if '남음' in o['now']), '/', len(old))
