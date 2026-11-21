import json, math, re, sys, collections
sys.path.insert(0, '/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/p1')
from seed import SECTIONS, DRAFT, SHELF
REPO = '/home/claude/s7/work'
TB = '/mnt/user-data/uploads/Downloads/sketchy_carbon/refs/교재/_txt/한의학개론_p001-250_최종.txt'
lines = open(TB, encoding='utf-8').read().split('\n')
CJK = re.compile(r'[㐀-鿿豈-﫿]{2,}')
secs = [s for s in SECTIONS if s[4]]
sec_text = {s[1]: '\n'.join(lines[s[4]-1:s[5]]) for s in secs}
def grams(t):
    out = set()
    for run in CJK.findall(t):
        for n in (2, 3, 4):
            for i in range(len(run) - n + 1):
                out.add(run[i:i+n])
    return out
df = collections.Counter()
for k, t in sec_text.items():
    for g in grams(t):
        df[g] += 1
N = len(sec_text)
def lesson_text(L):
    parts = [L.get('title', '')]
    for st in L['stations']:
        if st.get('kind') in ('frame', 'review'):
            continue
        parts.append(st.get('fact', ''))
    return '\n'.join(parts)
draft_of = {i: s for s, ids in DRAFT.items() for i in ids}
res = {}
for lid in sorted(set(draft_of) | set(SHELF)):
    L = json.load(open(f'{REPO}/src/lessons/l/{lid}.json'))
    gs = [g for g in grams(lesson_text(L)) if 0 < df[g] <= max(2, N // 6)]
    sc = {}
    for k, t in sec_text.items():
        sc[k] = sum(math.log(N / df[g]) for g in gs if g in t)
    top = sorted(sc.items(), key=lambda x: -x[1])[:3]
    # 앵커 줄: 상위 절 안에서 gram이 걸린 줄들의 중앙값
    s_from = dict((s[1], s[4]) for s in secs)
    best = top[0][0]
    hits = []
    for j, ln in enumerate(lines[s_from[best]-1: [s for s in secs if s[1]==best][0][5]]):
        w = sum(1 for g in gs if g in ln)
        hits += [s_from[best] + j] * w
    anchor = sorted(hits)[len(hits)//2] if hits else None
    res[lid] = {'draft': draft_of.get(lid, 'SHELF'), 'top': top, 'anchor': anchor, 'title': L['title']}
json.dump(res, open('/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/p1/vote.json', 'w'), ensure_ascii=False, indent=1)
mism = [(k, v) for k, v in res.items() if v['draft'] != v['top'][0][0] and v['draft'] not in ('SHELF', 'ch05-x1')]
print('lessons', len(res), 'mismatch', len(mism))
for k, v in mism:
    t = ' '.join(f"{s}:{x:.0f}" for s, x in v['top'])
    print(f"{k:11s} draft={v['draft']:8s} | {t} | {v['title'][:34]}")
