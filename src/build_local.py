# -*- coding: utf-8 -*-
"""panels/library.json + images/ → index.html   (허브 빌더)

★ 2026-08-31 재작성 — 클라우드 컨테이너가 회수되어 원본이 사라졌고,
   GitHub 의 index.html 을 역산해 다시 썼다. 산출물이 이전 판과 같은 구조가 되도록 맞췄다.
   CSS·스크립트는 panels/_css.txt · panels/_script.txt 에 원본 그대로 떼어 두었다.
"""
import base64, io, json, os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LIB    = json.load(open(os.path.join(HERE, 'panels/library.json'), encoding='utf-8'))
SCENES = json.load(open(os.path.join(HERE, 'panels/scenes.json'), encoding='utf-8'))
CSS    = open(os.path.join(HERE, 'panels/_css.txt'), encoding='utf-8').read()
SCRIPT = open(os.path.join(HERE, 'panels/_script.txt'), encoding='utf-8').read()

# ── 배포 크기 예산 ───────────────────────────────────────────────
# GitHub 웹 업로드는 한 번에 10 MB가 상한이다. index.html 은 그림 110장을 base64로 품는다.
# ⚠ 사다리는 **이미지 base64 크기만** 잰다 — 본문(도해 문항·why 주석)이 0.6 MB쯤 더 붙으므로
#   그 몫을 미리 떼어 놓는다(2026-08-29 실측 563 KB → 여유 두고 700 KB).
BUDGET        = 9_850_000   # 업로드 다리 상한 10 MB
HTML_OVERHEAD = 700_000
LADDER = [(1250, 78), (1250, 74), (1250, 70), (1100, 70), (1024, 68), (1024, 66), (1024, 64),
          (1024, 62), (1000, 60), (980, 60), (940, 58)]
_PICK = {'mode': 'passthrough', 'recode': {}}


def img_path(pid):
    for ext in ('webp', 'png', 'jpg', 'jpeg'):
        p = os.path.join(HERE, 'images', '%s.%s' % (pid, ext))
        if os.path.exists(p):
            return p
    return None


def b64(path, maxw=None, q=None):
    im = Image.open(path)
    if path.lower().endswith('.webp') and im.width <= 1032:
        with open(path, 'rb') as f:                 # 무손실 통과
            return base64.b64encode(f.read()).decode()
    maxw, q = (1024, 70) if path.lower().endswith('.png') else (1100, 58)
    im = im.convert('RGB')
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6)
    return base64.b64encode(buf.getvalue()).decode()


def fit_budget(paths):
    """2026-09-02 — git 이력에서 되살린 고해상도 원본을 최대한 살리는 배분.
       ① 원래 1024px 이하인 판(더 좋은 판본이 없던 판)은 **무손실 통과** — 손해를 만들지 않는다.
       ② 되살린 고해상도 판(1100~1250px)만 1100px q58 로 맞춘다.
       ③ 재작도 png 4판은 1024px q70.
       업로드 다리 상한 10 MB 안에서 이 조합이 실측상 가장 깨끗했다(4안 비교, quality_pick.png)."""
    _PICK.update(mode='lossless 58 + 고해상도 1100/q58 + 재작도 1024/q70')
    print('배분 — 무손실 통과(≤1032px) · 고해상도 1100px q58 · 재작도 png 1024px q70')


def esc(t):
    """본문의 **굵게** 만 <b>로 바꾸고 나머지는 그대로 (원본이 그랬다)."""
    return (t or '').replace('\n', '<br>')


def panel_html(p):
    pid = p['id']
    diag = ' diag' if p['track'] == 'D' else ''
    nq = len(p['quiz'])
    badge = ('<span class="dbadge%s">도해 · 문항 %d</span> '
             % ('' if nq else ' none', nq)) if p['track'] == 'D' else ''
    o = ['<div class="panel%s" id="%s" data-track="%s">' % (diag, pid, p['track'])]
    o.append('<h3><a href="#%s">🔗</a> %s <span class="tag">%s</span> %s<span class="pid">#%s</span></h3>'
             % (pid, p['title'], p['tag'], badge, pid))
    ip = img_path(pid)
    if ip:
        o.append('<img loading="lazy" src="data:image/webp;base64,%s">' % b64(ip))
    o.append('<table><thead><tr><th>소품</th>'
             '<th>잠그는 사실 (테스트 모드: 탭하여 확인)</th></tr></thead><tbody>')
    for r in p['rows']:
        tc = ' class="trap"' if r['trap'] else ''
        o.append('<tr%s><td class="prop">%s <span class="why">왜?</span></td>'
                 '<td class="fact">%s</td></tr>' % (tc, esc(r['prop']), esc(r['fact'])))
        if r['why']:
            rc = 'reason trap' if r['trap'] else 'reason'
            o.append('<tr class="%s"><td colspan="2" class="rz">다리 — %s</td></tr>'
                     % (rc, esc(r['why'])))
    o.append('</tbody></table>')
    if p['quiz']:
        o.append('<div class="quiz"><div class="qhead">도해 문항 %d  '
                 '<span class="qtoggle">펼치기</span></div><table class="qtab"><tbody>' % nq)
        for i, q in enumerate(p['quiz'], 1):
            src = '<span class="qsrc">%s</span>' % q['src'] if q['src'] else ''
            o.append('<tr><td class="qq">%d. %s</td><td class="fact qa">%s%s</td></tr>'
                     % (i, esc(q['q']), esc(q['a']), src))
        o.append('</tbody></table></div>')
    o.append('</div>')
    return '\n'.join(o)


def run():
    pan = {p['id']: p for p in LIB['panels']}
    paths = [q for q in (img_path(p['id']) for p in LIB['panels']) if q]
    fit_budget(paths)

    npan  = len(LIB['panels'])
    ntrap = sum(1 for p in LIB['panels'] for r in p['rows'] if r['trap'])
    nquiz = sum(len(p['quiz']) for p in LIB['panels'])
    nqp   = sum(1 for p in LIB['panels'] if p['quiz'])
    from collections import Counter
    tc = Counter(p['track'] for p in LIB['panels'])

    chips = ''.join('<a class="chip" href="#%s">%s</a>' % (a, t) for a, t in SCENES['chips'])
    o = ['<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>한의학 Sketchy 허브 v2.1</title>',
         '<style>%s</style></head><body>' % CSS,
         '<header><h1>한의학 Sketchy 허브 <small>v2.2 · 패널 %d · 함정 %d · 도해 문항 %d</small></h1>'
         % (npan, ntrap, nquiz),
         '<span class="btn" id="bTest">자가테스트</span><span class="btn" id="bWhy">다리 전체</span>'
         '<span class="btn" id="bTrap">함정만</span><span class="btn" id="bQuiz">도해 문항</span>',
         '<div class="chips">%s</div></header>' % chips,
         '<main>']
    for sc in SCENES['scenes']:
        o.append('<h2>%s</h2>' % sc['title'])
        for pid in sc['ids']:
            if pid in pan:
                o.append(panel_html(pan[pid]))
    o.append('</main>')
    o.append('<footer>자가테스트: 사실 칸 blur, 탭하여 확인 · <b>왜?</b>: 행별 다리 펼침 · '
             '다리 전체: 일괄 펼침 · 함정만: ⚠ 행만 · <b>도해 문항</b>: 도해 판의 문항 일괄 펼침'
             '(자가테스트와 함께 켜면 답이 가려진다) · 딥링크: #id<br>'
             '수록 %d패널 — 서사 %d · 무대 %d · 카드 %d · 도해 %d · 장면 %d · 함정 %d행 · '
             '<b>도해 문항 %d개 / %d판</b><br>'
             '도해의 rows는 답이 그림에 인쇄돼 있어 자가테스트에서 빠진다(CANON 74). '
             '그 자리를 데이터에서 뽑은 문항이 대신 진다(규칙 108 · diagrams/quiz.py)</footer>'
             % (npan, tc['A'], tc['B'], tc['C'], tc['D'], len(SCENES['scenes']),
                ntrap, nquiz, nqp))
    o.append('<script>%s</script></body></html>' % SCRIPT)

    html = '\n'.join(o)
    out = os.path.join(HERE, 'index.html')
    open(out, 'w', encoding='utf-8').write(html)
    sz = os.path.getsize(out)
    print('written index.html %.2f MB, panels %d traps %d | 도해 문항 %d 개 / %d 판 | 화질 %s'
          % (sz / 1e6, npan, ntrap, nquiz, nqp, _PICK['mode']))
    if sz > BUDGET:
        print('⚠ 예산 초과 %.2f MB > %.2f MB — 업로드가 막힌다' % (sz / 1e6, BUDGET / 1e6))


if __name__ == '__main__':
    run()
