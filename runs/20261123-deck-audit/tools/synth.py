# -*- coding: utf-8 -*-
"""덱 감사 묶음 5 — 합치기: 과별 판정 · 고칠 순위 · 교재 누락표 · 일관성. 읽기만 하고 감사 폴더에 쓴다."""
import json, glob, os, re
from collections import Counter, defaultdict
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
A = os.path.join(R, 'runs', '20261123-deck-audit')
J = lambda p: json.load(open(os.path.join(A, p), encoding='utf-8'))
def jl(p):
    out = []
    for ln in open(p, encoding='utf-8'):
        ln = ln.strip()
        if ln:
            try: out.append(json.loads(ln))
            except Exception: pass
    return out

machine = J('machine.json')
det = {r['lesson']: r for r in machine['lessons_detail']}
st = jl(os.path.join(A, 'stations.jsonl'))
by_les = defaultdict(list)
for r in st: by_les[r['lesson']].append(r)

# ── 교재 대조: 1차 + 2차, 엇갈림은 본체 판정 ─────────────────
ADJ = {  # 본체 판정(2026-11-27) — (과, 정거장): 최종
    ('yyox-03', 7): '갈림', ('yyox-08', 4): '다름', ('new-uk-15', 8): '다름', ('new-jq-06', 2): '맞음',
    ('new-jq-05', 6): '갈림', ('new-gr-18', 2): '다름', ('new-zj-01', 2): '갈림', ('new-zj-12', 1): '갈림',
    ('new-zj-04', 10): '다름', ('new-zj-09', 5): '다름', ('hp-12', 1): '갈림', ('hp-10', 7): '다름', ('new-zj-18', 3): '다름'}
fact = {}; fnote = {}
items_final = []
for L in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']:
    a = J(f'ledger/{L}_a.json'); b = J(f'ledger/{L}_b.json')
    sb = {(s['lesson'], s['n']): s for s in b.get('stations', [])}
    for s in a.get('stations', []):
        k = (s['lesson'], s['n']); c = s.get('check'); y = sb.get(k)
        if k in ADJ: c = ADJ[k]
        elif y and y.get('check') != c:
            # 엇갈렸고 본체 판정 목록에 없으면: 「다름」이 아닌 쪽끼리 — 더 약한 쪽(맞음 < 갈림 < 교재에없음)을 고르지 않고 둘 다 적는다
            c = c if c == '다름' else (y.get('check') if y.get('check') in ('교재에없음', '갈림') else c)
        fact[k] = c; fnote[k] = (s.get('note') or '')[:140]
    ib = {}
    for i in b.get('items', []): ib.setdefault(i.get('line'), i)
    for i in a.get('items', []):
        v = i.get('verdict'); y = ib.get(i.get('line'))
        if y is not None and v == '없음' and y.get('verdict') != '없음':
            v = y.get('verdict') + '(2차)'
        items_final.append({'bundle': L, **i, 'final': v, 'checked_b': y is not None})

# ── 그림 독자 ───────────────────────────────────────────────
n_why = defaultdict(Counter); d_text_only = Counter(); d_atoms = Counter(); d_mismatch = defaultdict(list)
for f in glob.glob(os.path.join(A, 'eyes', 'E*_n.jsonl')):
    for r in jl(f):
        try: n = int(float(str(r.get('n')).split('.')[0]))
        except Exception: continue
        n_why[(r.get('lesson'), n)][str(r.get('why') or '')[:8]] += 1
for f in glob.glob(os.path.join(A, 'eyes', 'E*_d.jsonl')):
    for r in jl(f):
        try: n = int(r.get('n'))
        except Exception: continue
        k = (r.get('lesson'), n); d_atoms[k] += 1
        if not r.get('xywh') or str(r.get('carrier', '')).strip() in ('', '없음', '글로만') or '글로만' in str(r.get('carrier', '')):
            d_text_only[k] += 1
        om = str(r.get('obj_missing') or '').strip()
        if om and om not in ('없음', '-'):
            d_mismatch[k].append(om[:80])

eyes_lessons = set(l for v in J('eyes_chunks.json').values() for l in v)

# ── 과별 판정 ────────────────────────────────────────────────
SAAM = {f'new-gr-{i}' for i in range(19, 31)}
YUJU_PH = {'new-gr-35'} | {f'new-gr-{i}' for i in range(37, 48)}
lessons = []
for lid, info in det.items():
    rows = by_les.get(lid, [])
    g = Counter(r.get('grade') for r in rows)
    fixes = Counter(r.get('fix') for r in rows if r.get('grade') in ('높음', '중간'))
    codes = Counter(c for r in rows for c in r.get('codes', []))
    cards = sum(r.get('src_cards') or 0 for r in rows)
    f_diff = [r['n'] for r in rows if fact.get((lid, r['n'])) == '다름']
    f_none = [r['n'] for r in rows if fact.get((lid, r['n'])) == '교재에없음']
    f_split = [r['n'] for r in rows if fact.get((lid, r['n'])) == '갈림']
    atoms = sum(d_atoms[(lid, r['n'])] for r in rows); tonly = sum(d_text_only[(lid, r['n'])] for r in rows)
    whyc = Counter()
    for r in rows: whyc.update(n_why.get((lid, r['n']), {}))
    named = whyc.get('소리', 0) + whyc.get('글자 뜻', 0); guess = whyc.get('하는 일 · ', 0) + whyc.get('하는 일·자', 0) + whyc.get('모름', 0)
    mism = sum(len(d_mismatch[(lid, r['n'])]) for r in rows)
    ch = info['chapter']; grp = info['group']
    hi = g.get('높음', 0); mid = g.get('중간', 0); n = max(1, len(rows))
    if lid in SAAM:
        verdict = '그릇바꿈(舍岩 표 연습 — 이미 saam.html)'
    elif lid in YUJU_PH:
        verdict = '그릇바꿈(유주도) — 물건 칸이 틀 문구 그대로'
    elif ch == 'ch05':
        top = fixes.most_common(1)[0][0] if fixes else '없음'
        verdict = {'그릇바꿈': '그릇바꿈(표 · 트레이너)', '다시그림': '그릇바꿈 검토(5장 — 그림 대신)'}.get(top, '글만 고침' if (hi + mid) else '그대로')
    else:
        tr = (tonly / atoms) if atoms else None
        if hi == 0 and mid <= 1 and not f_diff:
            verdict = '그대로'
        elif fixes.get('그릇바꿈', 0) >= max(3, n // 3):
            verdict = '그릇바꿈(표 · 트레이너)'
        elif (hi >= 4 and grp in ('C', 'A2')) or (tr is not None and tr >= 0.45 and hi >= 2):
            verdict = '다시 그림'
        elif hi >= 1 or fixes.get('구역', 0) >= 2:
            verdict = '구역 고침'
        else:
            verdict = '글만 고침'
        if f_diff and verdict == '그대로':
            verdict = '글만 고침'
    rec = info.get('recorded_stations', 0)
    score = hi * 3 + mid + len(f_diff) * 4
    weight = cards
    lessons.append({'lesson': lid, 'title': info['title'], 'chapter': ch, 'group': grp, 'stations': info['content_stations'],
                    'high': hi, 'mid': mid, 'codes': dict(codes.most_common(6)), 'cards': cards, 'recorded': rec,
                    'fact_diff': f_diff, 'fact_not_in_textbook': f_none, 'fact_split': f_split,
                    'picture_atoms': atoms, 'picture_text_only': tonly, 'name_reader_named': named, 'name_reader_guess': guess,
                    'obj_vs_picture_mismatch': mism, 'eyes_checked': lid in eyes_lessons,
                    'verdict': verdict, 'score': score, 'weight': weight,
                    'high_stations': [r['n'] for r in rows if r.get('grade') == '높음'][:20],
                    'notes': [f"#{r['n']} {r.get('note','')[:90]}" for r in rows if r.get('grade') == '높음' and r.get('note')][:4]})
json.dump(lessons, open(os.path.join(A, 'lessons.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ── 고칠 순위와 선 셋 ────────────────────────────────────────
COST = {'그대로': 0, '글만 고침': 0.25, '구역 고침': 1.0, '다시 그림': 2.5}
def cost(l):
    v = l['verdict']
    c = next((c for k, c in COST.items() if v.startswith(k)), 1.5)
    rr = 0.15 if l['recorded'] else 0
    return c + rr
order = sorted([l for l in lessons if l['verdict'] != '그대로'], key=lambda l: (-(l['score'] > 0 and bool(l['fact_diff'])), -l['high'], -l['weight'], -l['mid']))
lineA = [l for l in order if l['fact_diff'] or (l['high'] >= 2 and l['weight'] >= 10)]
lineB = [l for l in order if l['high'] >= 1 or l['mid'] >= 3 or l['fact_diff']]
lineC = order
def line_sum(ls):
    v = Counter(re.sub(r'\(.*', '', l['verdict']).strip() for l in ls)
    return {'과': len(ls), '정거장': sum(l['stations'] for l in ls), '판정별': dict(v),
            '다시 녹음 과': sum(1 for l in ls if l['recorded'] and l['verdict'] != '그대로'),
            '어림 시간': round(sum(cost(l) for l in ls), 1)}
lines = {'가': line_sum(lineA), '나': line_sum(lineB), '다': line_sum(lineC)}
json.dump({'lines': lines, 'A': [l['lesson'] for l in lineA], 'B': [l['lesson'] for l in lineB], 'C': [l['lesson'] for l in lineC]},
          open(os.path.join(A, 'lines.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(A, '고침순위.md'), 'w', encoding='utf-8') as f:
    f.write('# 고칠 순위 (2026-11-27 · 기준 판 8c2dd18)\n\n순위 = 교재와 다른 사실 → 「높음」 수 → 걸린 시험 카드 수 → 「중간」 수. 어림 시간은 과당 글만 0.25시간 · 구역 1시간 · 다시 그림 2.5시간(6+1 포함) · 그 밖 1.5시간 + 녹음 있는 과 0.15시간으로 센 것이다 — 실측이 아니다.\n\n')
    for k, v in lines.items():
        f.write(f'- **선 {k}**: {json.dumps(v, ensure_ascii=False)}\n')
    f.write('\n| 순 | 과 | 장 | 판정 | 높음 | 중간 | 교재와 다름(정거장) | 카드 | 녹음 | 그림: 글로만/원자 | 주된 흠 |\n|---|---|---|---|---|---|---|---|---|---|---|\n')
    for i, l in enumerate(order, 1):
        f.write(f"| {i} | {l['lesson']} | {l['chapter']} | {l['verdict']} | {l['high']} | {l['mid']} | {','.join(map(str,l['fact_diff'])) or '-'} | {l['cards']} | {l['recorded']} | {l['picture_text_only']}/{l['picture_atoms']} | {' · '.join(l['notes'][:1])[:100]} |\n")

# ── 교재 누락표 ─────────────────────────────────────────────
with open(os.path.join(A, 'gaps.md'), 'w', encoding='utf-8') as f:
    c = Counter(i['final'] for i in items_final)
    f.write('# 교재에서 빠진 것 (2026-11-27)\n\n1차가 「없음」이라 했으나 2차가 덱에서 찾은 것은 2차 판정을 따랐다. 2차가 보지 않은 1차 「없음」은 그대로 둔다(넉넉하게 잡혔을 수 있다).\n\n')
    f.write('판정 수: ' + json.dumps(dict(c), ensure_ascii=False) + '\n\n')
    for L in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']:
        none = [i for i in items_final if i['bundle'] == L and i['final'] == '없음']
        f.write(f'## {L} — 없음 {len(none)}\n\n| 교재 줄 | 용어 | 2차 확인 | 그릇 제안 |\n|---|---|---|---|\n')
        for i in none:
            f.write(f"| {i.get('line')}{('-'+str(i['end'])) if i.get('end') and i.get('end')!=i.get('line') else ''} | {str(i.get('term',''))[:20]} | {'둘 다 없음' if i['checked_b'] else '1차만'} | {str(i.get('proposal',''))[:60]} |\n")
        f.write('\n')

# ── 사실 장부 ───────────────────────────────────────────────
with open(os.path.join(A, 'facts.md'), 'w', encoding='utf-8') as f:
    f.write('# 사실 대조 (교재 줄 기준)\n\n')
    f.write('판정 수: ' + json.dumps(dict(Counter(fact.values())), ensure_ascii=False) + '\n\n## 교재와 다름\n\n')
    for k, v in sorted(fact.items()):
        if v == '다름': f.write(f'- {k[0]}#{k[1]} — {fnote[k]}\n')
    f.write('\n## 갈림(교재와 문제집 · 원전이 다르고 둘 다 성립 — 한쪽을 택하지 않음)\n\n')
    for k, v in sorted(fact.items()):
        if v == '갈림': f.write(f'- {k[0]}#{k[1]} — {fnote[k]}\n')

print('판정', Counter(re.sub(r'\(.*', '', l['verdict']).strip() for l in lessons))
print('선', json.dumps(lines, ensure_ascii=False))
print('사실', Counter(fact.values()))
print('항목', Counter(i['final'] for i in items_final))
