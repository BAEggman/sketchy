"""src/saam/table.json + saam-template.html + saam.js → saam.html (舍岩 표 트레이너, 오프라인 한 파일)

먼저 python3 src/saam/make_table.py 로 정본을 만들고(규칙 · 노래 · 사용자 문장 세 갈래 검산), 그다음 이 파일을 돌린다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'src/saam/table.json').read_text(encoding='utf-8'))
assert len(data['cells']) == 24, 'table.json 칸 수가 24가 아니다'
template = (ROOT / 'src/saam/saam-template.html').read_text(encoding='utf-8')
script = (ROOT / 'src/saam/saam.js').read_text(encoding='utf-8')
page = (template
        .replace('__SAAM_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'))
        .replace('__SAAM_SCRIPT__', script))
(ROOT / 'saam.html').write_text(page, encoding='utf-8')
print('written saam.html — 正格 · 勝格 24칸 · 오수혈 60 · 本穴 10 · 自經 補瀉 12 (%d bytes)' % len(page.encode('utf-8')))
