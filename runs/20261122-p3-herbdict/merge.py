import json,os,collections,sys
R=os.path.dirname(os.path.abspath(__file__))
base=json.load(open(f'{R}/base.json'))
cho={x['hanja']:x for x in json.load(open(f'{R}/../20261121-p2-cho/final.json'))['dictionary']}
items={};nu=[];cr=[];ck=[]
for b in ['B1','B2','B3','B4','B5','B6']:
    p=f'{R}/{b}/final.json'
    if not os.path.exists(p): print('missing',b); continue
    f=json.load(open(p))
    for it in f['items']: it['batch']=b; items[it['id']]=it
    nu+= [dict(x,batch=b) for x in f.get('needs_user_ok',[])]; cr+=f.get('conflict_risk',[]); ck+=f.get('check_needed',[])
out=[]
for r in base:
    if r['fixed']:
        c=cho.get(r['hanzi'])
        it={'id':r['id'],'hanja':r['hanzi'],'reading':r['name'],'cue':c['cue'] if c else r['fixed'][1],'decode':c['decode'] if c else '','carriers':c['carriers'] if c else [r['fixed'][1].split(' — ')[0]],'type':c['type'] if c else '','status':'fixed','from':r['fixed'][0]}
    else:
        it=items.get(r['id'])
        if not it: print('no item',r['id'],r['hanzi']); continue
        it=dict(it); it['status']='candidate'
    it['category']=r['tb_cat'][:1]; it['tb_lines']=r['tb_lines'][:8]
    out.append(it)
cnt=collections.Counter()
own=collections.defaultdict(list)
for it in out:
    for c in it.get('carriers') or []:
        c=c.split('(')[0].strip(); cnt[c]+=1; own[c].append(it['hanja'])
over={c:own[c] for c,n in cnt.items() if n>2}
dup={c:own[c] for c,n in cnt.items() if n==2}
json.dump({'items':out,'needs_user_ok':nu,'conflict_risk':cr,'check_needed':ck,'carrier_over2':over,'carrier_twice':dup},open(f'{R}/merged.json','w'),ensure_ascii=False,indent=1)
print(len(out),'over2:',over);print('twice:',len(dup));print('needs_user_ok',len(nu))
