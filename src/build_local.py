# -*- coding: utf-8 -*-
"""panels/library.json + images/ → index.html   (허브 빌더)

★ 2026-08-31 재작성 — 클라우드 컨테이너가 회수되어 원본이 사라졌고,
   GitHub 의 index.html 을 역산해 다시 썼다. 산출물이 이전 판과 같은 구조가 되도록 맞췄다.
   CSS·스크립트는 panels/_css.txt · panels/_script.txt 에 원본 그대로 떼어 두었다.
"""
import base64, io, json, os, re, sys, html as html_module
from PIL import Image
from reading import fact_html, memory_html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIB    = json.load(open(os.path.join(HERE, 'panels/library.json'), encoding='utf-8'))
VERSION = LIB.get('release', {}).get('version', '2.3')
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
    panel = next(p for p in LIB['panels'] if p['id'] == pid)
    if panel.get('image'):
        return os.path.join(ROOT, panel['image'])
    for ext in ('webp', 'png', 'jpg', 'jpeg'):
        p = os.path.join(ROOT, 'images', '%s.%s' % (pid, ext))
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


EXTERNAL = os.environ.get('EXTERNAL') == '1'   # 1이면 그림을 images/ 파일로 링크(base64 미포함)


def panel_html(p):
    pid = p['id']
    diag = ' diag' if p['track'] == 'D' else ''
    nq = len(p['quiz'])
    badge = ('<span class="dbadge%s">도해 · 문항 %d</span> '
             % ('' if nq else ' none', nq)) if p['track'] == 'D' else ''
    o = ['<div class="panel%s" id="%s" data-track="%s">' % (diag, pid, p['track'])]
    o.append('<h3><a href="#%s">🔗</a> %s <span class="tag">%s</span> %s<span class="pid">#%s</span></h3>'
             % (pid, p['title'], p['tag'], badge, pid))
    if pid == 's10p01':
        o.append('<p class="study-note"><a href="bagua.html"><b>팔괘 방위 기억방 →</b></a> 남건북곤·동리서감 / 동남 손님·서남 곤잠·서북 건배·동북 간식 — 말장난으로 연결하고 빈 방위판을 채워 보세요.</p>')
    v7_links = {
        's02u01': ('hist-02a', 'Carbon v7 개편 판본 보기: hist-02a (陶弘景 梁=양 · 弘景=안경 홍학 · 365+365=730 · 集注=집 주전자) · hist-02b →', 'images/lessons/hist-02a.webp'),
        's03u02': ('hist-06b', 'Carbon v7 개편 판본 보기: hist-06a (金元四大家) · hist-06b (成無己 ★金 · 杜本 元 36종) →', 'images/lessons/hist-06b.webp'),
        's03u03': ('hist-06b', 'Carbon v7 개편 판본 보기: hist-06b (杜本 두더지+뿌리 · 오이씨=敖氏 · 삼지창+너트=36종) →', 'images/lessons/hist-06b.webp'),
        's18d01': ('hist-07a', 'Carbon v7 개편 판본 보기: hist-07a 혈 수 계보 (349→354→359→359→361 숫자 물건 부호) →', 'images/lessons/hist-07a.webp'),
        's18d06': ('new-gr-19', 'Carbon v7 개편 판본 보기: new-gr-19~30 (舍岩鍼法 12경 전담 과 · 肺經 4격) →', 'images/lessons/new-gr-19.webp'),
        's18d07': ('new-gr-19', 'Carbon v7 교정 반영: 大腸 寒格 補火 · 熱格 瀉火 = 양곡 · 양계(陽谿) / new-gr-19~30 열기 →', None),
        's18u01': ('new-gr-19', 'Carbon v7 신설 과 보기: new-gr-19(舍岩 肺) · new-gr-31(경혈 수) · new-gr-33(16극혈) →', 'images/lessons/new-gr-31.webp'),
    }
    if pid in v7_links:
        lid, ltxt, limg = v7_links[pid]
        img_tag = ('<br><a href="lessons.html?l=%s"><img loading="lazy" src="%s" alt="%s" style="margin-top:6px"></a>' % (lid, limg, lid)) if limg else ''
        o.append('<p class="study-note" style="border:1.5px solid var(--acc)"><b><a href="lessons.html?l=%s">★ %s</a></b>%s</p>' % (lid, ltxt, img_tag))
    ip = img_path(pid)
    if ip:
        is_extension = bool(p.get('extension'))
        if is_extension:
            o.append('<div class="extension-tools"><button type="button" class="figure-toggle" aria-expanded="true" aria-controls="figure-%s">도해 가리고 회상</button> <a href="%s" target="_blank" rel="noopener">도해 크게 보기 ↗</a> <a class="practice-link" href="#quiz-%s">회상 문제로 ↓</a></div>' % (pid, p['image'], pid))
            o.append('<div class="extension-figure" id="figure-%s" tabindex="0" role="region" aria-label="%s 도해">' % (pid, html_module.escape(p['title'], quote=True)))
        if EXTERNAL:
            o.append('<img loading="lazy" decoding="async" src="%s" alt="%s">' % (p.get('image', 'images/%s.webp' % pid), html_module.escape(p['title'], quote=True) if is_extension else ''))
        elif ip.endswith('.svg'):
            o.append('<img loading="lazy" src="data:image/svg+xml;base64,%s" alt="%s">' % (base64.b64encode(open(ip,'rb').read()).decode(), html_module.escape(p['title'],quote=True)))
        else:
            o.append('<img loading="lazy" src="data:image/webp;base64,%s">' % b64(ip))
        if is_extension:
            o.append('</div><p class="figure-hint">작은 화면에서는 도해를 좌우로 밀어 보세요.</p>')
            if p.get('study_note'):
                o.append('<p class="study-note">%s</p>' % html_module.escape(p['study_note']))
    o.append('<table><thead><tr><th>%s</th>'
             '<th>잠그는 사실 (테스트 모드: 탭하여 확인)</th></tr></thead><tbody>')
    o[-1] = o[-1] % ('도해의 연결' if p.get('extension') else '소품')
    for r in p['rows']:
        tc = ' class="trap"' if r['trap'] else ''
        o.append('<tr%s><td class="prop">%s <span class="why">왜?</span></td>'
                 '<td class="fact">%s%s</td></tr>' % (tc, esc(r['prop']), fact_html(r['fact']), memory_html(r.get('memory'))))
        if r['why']:
            rc = 'reason trap' if r['trap'] else 'reason'
            o.append('<tr class="%s"><td colspan="2" class="rz">다리 — %s</td></tr>'
                     % (rc, esc(r['why'])))
    o.append('</tbody></table>')
    if p['quiz']:
        o.append('<div class="quiz" id="quiz-%s"><div class="qhead">도해 문항 %d  '
                 '<span class="qtoggle">펼치기</span></div><table class="qtab"><tbody>' % (pid,nq))
        for i, q in enumerate(p['quiz'], 1):
            src = '<span class="qsrc">%s</span>' % q['src'] if q['src'] else ''
            o.append('<tr><td class="qq">%d. %s</td><td class="fact qa">%s%s</td></tr>'
                     % (i, esc(q['q']), fact_html(q['a']), src))
        o.append('</tbody></table></div>')
    if p.get('extension'):
        o.append('<details class="source-details"><summary>정리 자료와 원문 출처</summary><ul>')
        for note in p.get('source_notes',[]):
            o.append('<li>%s</li>' % html_module.escape(note))
        for source in p.get('sources',[]):
            o.append('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (html_module.escape(source['url'],quote=True), html_module.escape(source['title'])))
        o.append('</ul></details>')
    o.append('</div>')
    return '\n'.join(o)


def run():
    pan = {p['id']: p for p in LIB['panels']}
    paths = [q for q in (img_path(p['id']) for p in LIB['panels']) if q]
    if EXTERNAL:
        _PICK.update(mode='외부 파일 링크(images/*.webp) — 재압축 없음')
        print('외부 파일 모드 — 그림은 images/ 에서 불러온다(원본 화질 그대로)')
    else:
        fit_budget(paths)

    npan  = len(LIB['panels'])
    ntrap = sum(1 for p in LIB['panels'] for r in p['rows'] if r['trap'])
    nquiz = sum(len(p['quiz']) for p in LIB['panels'])
    nqp   = sum(1 for p in LIB['panels'] if p['quiz'])
    from collections import Counter
    tc = Counter(p['track'] for p in LIB['panels'])

    chips = '<a class="chip" href="#carbon-v7" style="border-color:var(--acc);color:var(--acc);font-weight:700">★ Carbon v7 개선판</a>' + ''.join('<a class="chip" href="#%s">%s</a>' % (a, t) for a, t in SCENES['chips'])
    carbon_sec = [
        '<h2 id="carbon-v7">★ Carbon v7 개선판 — 227과 완비(신규·개편 43과 실사 화질) · 신규 도해 4장</h2>',
        '<div class="panel" style="border:2px solid var(--acc);background:#f7fbf8">',
        '<h3><a href="lessons.html" style="color:var(--acc)">▶ 한의학 Sketchy 과 재생기 열기 (227과 · 정거장 2,059개 · 그림 227/227 완비) →</a> <span class="tag">Carbon v7</span></h3>',
        '<p class="study-note" style="margin:6px 0 12px">의학사 14과 전면 개편(왕조 터·字號·서명·기여·의의·수 부호), 혈 수 계보(349→354→359→359→361) 숫자 물건 부호화, 舍岩鍼法 12경 전담 과(19~30), 경맥 수·郄穴·子午流注·骨度·八脈·中風·診斷·引經·同音(31~41) 및 조건부 流注 원문 6과(42~47)까지 신규·개편 43과 전원 실사 삽화와 9절 2회차 블라인드 판독 관문 검증, 신규 코드 도해 4장(s18d10~s18d13)이 반영되었습니다. 전체 투어·복습·회상 시험은 <a href="lessons.html"><b>과 재생기(lessons.html)</b></a>에서 실행합니다.</p>',
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px">',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=hist-02a">hist-02a · 南北朝 本草와 製藥 (재생기 열기 →)</a></b><br><small>陶弘景(梁=흰 양, 弘景=안경 홍학, 365+365=730, 集注=집 주전자) · 雷斅 · 徐之才</small><a href="lessons.html?l=hist-02a"><img loading="lazy" src="images/lessons/hist-02a.webp" alt="hist-02a" style="margin-top:6px"></a></div>',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=hist-06b">hist-06b · 成無己(★金) · 杜本(元) (재생기 열기 →)</a></b><br><small>성문+무기(成無己, 최초 전면 주해) · 두더지+뿌리(杜本) · 오이씨(敖氏) · 삼지창+너트(36종)</small><a href="lessons.html?l=hist-06b"><img loading="lazy" src="images/lessons/hist-06b.webp" alt="hist-06b" style="margin-top:6px"></a></div>',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=hist-07a">hist-07a · 혈 수 계보 349→354→359→359→361 (재생기 열기 →)</a></b><br><small>어귀 삼지창(300) · 사과+구미호(349) · 오징어+사과(354) · 오징어+구미호 둘(359·359) · 너트+일렉기타(361)</small><a href="lessons.html?l=hist-07a"><img loading="lazy" src="images/lessons/hist-07a.webp" alt="hist-07a" style="margin-top:6px"></a></div>',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=new-gr-19">new-gr-19 · 舍岩 ① 手太陰肺經 4격 (재생기 열기 →)</a></b><br><small>正格(太白·太淵 補, 少府·魚際 瀉) · 勝格(少府·魚際 補, 尺澤·陰谷 瀉) · 寒格 · 熱格</small><a href="lessons.html?l=new-gr-19"><img loading="lazy" src="images/lessons/new-gr-19.webp" alt="new-gr-19" style="margin-top:6px"></a></div>',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=new-gr-29">new-gr-29 · 舍岩 ⑪ 足少陽膽經 4격 (재생기 열기 →)</a></b><br><small>초록 판관(膽) · 正格(俠谿·足通谷 補, 足竅陰·商陽 瀉) · 勝格 · 寒格 · 熱格</small><a href="lessons.html?l=new-gr-29"><img loading="lazy" src="images/lessons/new-gr-29.webp" alt="new-gr-29" style="margin-top:6px"></a></div>',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=new-gr-31">new-gr-31 · 경맥별 經穴 수 ① 手六經 (재생기 열기 →)</a></b><br><small>肺 11(기타+기타) · 大腸 20(버스+공룡) · 心 9(구미호) · 小腸 19(기타+구미호) · 心包 9 · 三焦 23(버스+삼지창)</small><a href="lessons.html?l=new-gr-31"><img loading="lazy" src="images/lessons/new-gr-31.webp" alt="new-gr-31" style="margin-top:6px"></a></div>',
        '<div style="border:1px solid var(--line);border-radius:8px;padding:8px;background:#fff"><b><a href="lessons.html?l=new-gr-33">new-gr-33 · 十六郄穴 ① 手六經 (재생기 열기 →)</a></b><br><small>肺 孔最 · 大腸 溫溜 · 心 陰郄 · 小腸 養老 · 心包 郄門 · 三焦 會宗</small><a href="lessons.html?l=new-gr-33"><img loading="lazy" src="images/lessons/new-gr-33.webp" alt="new-gr-33" style="margin-top:6px"></a></div>',
        '</div>',
        '<details style="margin-top:12px"><summary style="cursor:pointer;font-weight:700;color:var(--acc)">▼ Carbon v7 신규 코드 도해 4장 펼치기 (s18d10 骨度 · s18d11 子午流注 · s18d12 經穴 수 361 · s18d13 標本根結)</summary>',
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:12px;margin-top:10px">',
        '<div><b>#s18d10 · 骨度分寸法 전신 치수 대조표</b><img loading="lazy" src="images/s18d10.webp" alt="s18d10"></div>',
        '<div><b>#s18d11 · 子午流注 12시진 시계 · 氣血多少 · 脈長</b><img loading="lazy" src="images/s18d11.webp" alt="s18d11"></div>',
        '<div><b>#s18d12 · 十四經 경맥별 經穴 수 대조표 (361혈)</b><img loading="lazy" src="images/s18d12.webp" alt="s18d12"></div>',
        '<div><b>#s18d13 · 十二經 標本 · 六經 根結 대조표</b><img loading="lazy" src="images/s18d13.webp" alt="s18d13"></div>',
        '</div></details></div>',
    ]
    o = ['<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>한의학 Sketchy 허브 v%s</title>' % VERSION,
         '<style>%s</style></head><body>' % CSS,
         '<header><h1>한의학 Sketchy 허브 <small>v%s · 패널 %d · 과 재생기 227과(Carbon v7)</small></h1>'
         % (VERSION, npan),
         '<a class="btn" href="lessons.html" style="text-decoration:none;border-color:var(--acc);color:var(--acc);font-weight:700">과 재생기 (227과 · Carbon v7) →</a><a class="btn" href="lessons.html" style="text-decoration:none">교재 목차로 보기 →</a>'
         '<span class="btn" id="bTest">자가테스트</span><span class="btn" id="bWhy">다리 전체</span>'
         '<span class="btn" id="bTrap">함정만</span><span class="btn" id="bQuiz">도해 문항</span>'
         '<button type="button" class="btn" id="bReading" aria-pressed="true">한글 독음 켜짐</button>'
         '<a class="btn" href="recall.html" style="text-decoration:none">회상 훈련 →</a>',
         '<a class="btn" href="bagua.html" style="text-decoration:none">팔괘 방위 암기 →</a>',
         '<div class="chips">%s</div></header>' % chips,
         '<main>'] + carbon_sec
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
    out = os.path.join(ROOT, 'index.html')
    open(out, 'w', encoding='utf-8').write(html)
    sz = os.path.getsize(out)
    print('written index.html %.2f MB, panels %d traps %d | 도해 문항 %d 개 / %d 판 | 화질 %s'
          % (sz / 1e6, npan, ntrap, nquiz, nqp, _PICK['mode']))
    if sz > BUDGET and not EXTERNAL:
        print('⚠ 예산 초과 %.2f MB > %.2f MB — 업로드가 막힌다' % (sz / 1e6, BUDGET / 1e6))


if __name__ == '__main__':
    run()
