import json,sys
M=json.load(open('/home/claude/s7/work/src/lessons/lesson_map.json'))
L={l['id']:l for l in M['lessons']}
D={c['id']:c for c in json.load(open('/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/deck_local.json'))}
lib=json.load(open('/home/claude/s7/work/src/panels/library.json'))
rows={f"{p['id']}#{i}":r for p in lib['panels'] for i,r in enumerate(p['rows'])}
def rt(r):
    x=rows.get(r); return (x.get('fact') if isinstance(x,dict) else x) if x else None
for lid in sys.argv[1:]:
    l=L[lid]; print('==',lid,l['title'],'|',l['place'],'| n',l['n_stations'])
    seen=set()
    for i,s in enumerate(l['stations'],1):
        print(f"[{i}] split={s.get('split')} | {rt(s['row']) if s.get('row') else s.get('fact')} | {s.get('note','')[:120]}")
        for c in s['cards']:
            if c in seen: print('   (dup)',c); continue
            seen.add(c); d=D[c]; print(f"   {c} | {d['q'][:70]} → {d['a'][:150]}")
    print('notes',l.get('notes'))
