"""Install the additive v2.4 chapter without changing any original panel."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent/'panels'
lib=json.loads((P/'library.json').read_text()); scenes=json.loads((P/'scenes.json').read_text())
added=json.loads((P/'yinyang-v2.4.json').read_text()); ids={p['id'] for p in added}
lib['panels']=[p for p in lib['panels'] if p['id'] not in ids]+added
lib['release']={'version':'2.4','date':'2026-11-06','baseline':'bd0e22619d976e1b1d529aed60a8da31ba29a816','scope':'음양오행 17개 보완 주제 · 기존 말장난·그림·행 보존'}
for s in scenes['scenes']:
 s['ids']=[i for i in s['ids'] if i not in ids]
 if s['ids'] and s['ids'][0]=='s09u01':s['ids'] += [p['id']for p in added if p['id'].startswith('s09')]
 if s['ids'] and s['ids'][0]=='s10d02':s['ids'] += [p['id']for p in added if p['id'].startswith('s10')]
if not any(i=='s09x01'for i,label in scenes['chips']):scenes['chips'].insert(6,['s09x01','음양오행 보완'])
for name,obj in [('library.json',lib),('scenes.json',scenes)]:
 (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=1)+'\n')
print('Installed additive yin/yang chapter:',len(added),'panels')
