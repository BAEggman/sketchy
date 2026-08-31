# -*- coding: utf-8 -*-
"""index.html → panels/library.json + images/  복구기 (2026-08-31)

2026-08-29 이후 클라우드 컨테이너가 회수되어 작업 트리가 사라졌다.
GitHub에 올려 둔 index.html 이 유일한 현재본이라, 거기서 되짚어 되살린다.
★ 이 파일 자체도 저장소에 넣어 둔다 — 같은 일이 또 나면 이것부터 돌린다.
"""
import re, json, html, base64, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/s6/work'

s = open(SRC, encoding='utf-8').read()
os.makedirs(os.path.join(OUT, 'images'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'panels'), exist_ok=True)

def txt(x):
    """<br>은 줄바꿈으로, 나머지 태그는 벗기고, 엔티티는 되돌린다."""
    if not x:
        return ''
    x = re.sub(r'<br\s*/?>', '\n', x)
    x = re.sub(r'<span class="why">.*?</span>', '', x, flags=re.S)
    x = re.sub(r'<[^>]+>', '', x)
    return html.unescape(x).strip()

# 판 하나하나로 자른다 — class 가 "panel" 과 "panel diag" 둘이다
starts = [m.start() for m in re.finditer(r'<div class="panel(?: diag)?" id="', s)]
starts.append(len(s))

panels = []
nimg = 0
for a, b in zip(starts, starts[1:]):
    blk = s[a:b]
    m = re.match(r'<div class="panel(?: diag)?" id="([^"]+)" data-track="([^"]+)"', blk)
    if not m:
        continue
    pid, track = m.group(1), m.group(2)

    hm = re.search(r'<h3>.*?</a>\s*(.*?)\s*<span class="tag">(.*?)</span>', blk, re.S)
    title = txt(hm.group(1)) if hm else ''
    tag = txt(hm.group(2)) if hm else ''

    im = re.search(r'<img[^>]*src="data:image/(webp|png|jpeg);base64,([A-Za-z0-9+/=]+)"', blk)
    if im:
        open(os.path.join(OUT, 'images', '%s.%s' % (pid, im.group(1))), 'wb') \
            .write(base64.b64decode(im.group(2)))
        nimg += 1

    # ── rows ── prop/fact 줄과 (있으면) 바로 뒤의 reason 줄을 짝짓는다
    body = blk.split('<div class="quiz">')[0]
    rows = []
    pat = re.compile(
        r'<tr(?: class="(trap)")?>\s*<td class="prop">(.*?)</td>\s*<td class="fact">(.*?)</td>\s*</tr>'
        r'(?:\s*<tr class="reason(?: trap)?">\s*<td colspan="2" class="rz">(.*?)</td>\s*</tr>)?',
        re.S)
    for r in pat.finditer(body):
        why = txt(r.group(4))
        why = re.sub(r'^다리\s*—\s*', '', why)
        rows.append({'prop': txt(r.group(2)), 'fact': txt(r.group(3)),
                     'trap': bool(r.group(1)), 'why': why})

    # ── quiz ──
    quiz = []
    qm = re.search(r'<div class="quiz">(.*?)</table>', blk, re.S)
    if qm:
        for q in re.finditer(
                r'<td class="qq">\s*\d+\.\s*(.*?)</td>\s*<td class="fact qa">(.*?)'
                r'(?:<span class="qsrc">(.*?)</span>)?</td>', qm.group(1), re.S):
            quiz.append({'q': txt(q.group(1)), 'a': txt(q.group(2)), 'src': txt(q.group(3))})

    panels.append({'id': pid, 'title': title, 'tag': tag, 'track': track,
                   'rows': rows, 'quiz': quiz})

json.dump({'panels': panels}, open(os.path.join(OUT, 'panels', 'library.json'), 'w',
                                   encoding='utf-8'), ensure_ascii=False, indent=1)

nr = sum(len(p['rows']) for p in panels)
nq = sum(len(p['quiz']) for p in panels)
nt = sum(1 for p in panels for r in p['rows'] if r['trap'])
from collections import Counter
c = Counter(p['track'] for p in panels)
print('복구 완료')
print('  패널 %d   (%s)' % (len(panels), ' · '.join('%s %d' % kv for kv in sorted(c.items()))))
print('  rows %d · 함정 %d · 도해 문항 %d · 그림 %d장' % (nr, nt, nq, nimg))
print('  기대치 — 패널 110 · 함정 165 · 문항 335')
