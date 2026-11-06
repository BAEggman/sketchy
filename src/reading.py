"""검토 가능한 용어별 독음. 런타임 외부 라이브러리/네트워크 의존성 없음."""
import html
import json
import re
from pathlib import Path

CJK = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]+')
READINGS = json.loads((Path(__file__).parent / 'panels/readings.json').read_text(encoding='utf-8'))


def reading_text(text):
    return CJK.sub(lambda match: READINGS[match.group()], text)


def fact_html(text):
    """원문을 보존하고 한자 구절 바로 뒤에 한국 한자음을 병기한다."""
    parts = []
    pos = 0
    for match in CJK.finditer(text or ''):
        parts.append(html.escape(text[pos:match.start()]))
        term = match.group()
        parts.append(html.escape(term))
        reading = '(' + READINGS[term] + ')'
        # 이미 원문에 있는 독음은 그대로 두고 중복 병기를 피한다.
        if not text[match.end():].startswith(reading):
            parts.append('<span class="reading">' + html.escape(reading) + '</span>')
        pos = match.end()
    parts.append(html.escape((text or '')[pos:]))
    return ''.join(parts).replace('\n', '<br>')


def memory_html(memory):
    if not memory:
        return ''
    parts = []
    for key, label in [('image', '그림으로 회상'), ('extra', '별도 암기')]:
        if memory.get(key):
            parts.append('<div class="memory-note"><strong>' + label + '</strong> ' + fact_html(memory[key]) + '</div>')
    return '<div class="memory-scope">' + ''.join(parts) + '</div>'
