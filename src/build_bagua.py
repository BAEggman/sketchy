"""Build an offline direction mnemonic and recall page, without changing old panels."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'src/panels/bagua-memory.json').read_text())
template=(ROOT/'src/bagua-template.html').read_text()
script=(ROOT/'src/bagua.js').read_text()
page=template.replace('__BAGUA_DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')).replace('__BAGUA_SCRIPT__',script)
(ROOT/'bagua.html').write_text(page)
print('written bagua.html — 2 direction maps, 8 mnemonic objects, blank-board practice')
