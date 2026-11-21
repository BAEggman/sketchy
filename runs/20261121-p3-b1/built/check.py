import json,re,sys
ok=True
for lid in (sys.argv[1:] or ['hist-04','hist-05a','hist-05b']):
    S=json.load(open('/home/claude/work/runs/20261121-p3-b1/built/%s.spec.json'%lid,encoding='utf-8'))
    assert len(S['questions'])==5, lid
    for s in S['stations']:
        bad=re.sub(r'[가-힣\s.,?!·]','',s['tts'])
        if bad: ok=False; print(lid,s['n'],'tts bad:',repr(bad))
        if len(s['fact'])>60: ok=False; print(lid,s['n'],'fact',len(s['fact']),s['fact'])
        b=s['box']
        if s['kind'] in ('frame','review'):
            if b is not None: ok=False; print(lid,s['n'],'box should be null')
        else:
            if not(b and b[0]>=0 and b[1]>=0 and b[0]+b[2]<=2752 and b[1]+b[3]<=1536 and min(b[2],b[3])>=240):
                ok=False; print(lid,s['n'],'box bad',b)
        if not s['src']: ok=False; print(lid,s['n'],'no src')
print('OK' if ok else 'FAIL')
