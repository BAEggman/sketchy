#!/usr/bin/env python3
"""Rebuild the plain-style review package from a pinned, unchanged baseline.

Does not replace the lesson player, alter source_station, or generate audio.
Run from any directory: python src/lessons/tools/build_plain_narrations.py
"""
import collections
import copy
import csv
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from narration_plain import convert

ROOT = Path(__file__).resolve().parents[3]
REL = 'docs/narration-review-20261120'
OUT = ROOT / REL
BASE = '2fe65baa180138fcd98226bb41c4b68c70c3b918'

def old_file(path):
    return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT).decode()

def dump(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

main=json.loads(old_file(REL+'/narrations.json'))
panel=json.loads(old_file(REL+'/panel-narrations.json'))
baseline=copy.deepcopy(main['records']+panel['records']+panel['bagua'])
records=main['records']+panel['records']+panel['bagua']
by_id={r['card_id']:r for r in records}
style=[]
for r in records:
    before=r['narration'];after,edits=convert(before)
    r['narration']=after
    if edits: style.append(dict(card_id=r['card_id'],before_sha256=sha(before),after_sha256=sha(after),before_chars=len(before),after_chars=len(after),edits=edits))
manual=json.loads((OUT/'narration-content-edits.json').read_text())
for e in manual['edits']:
    r=by_id[e['card_id']]
    assert r['narration']==e['before'],e['card_id']
    r['narration']=e['after']

# Only generic narration scaffolding is shortened. Content/anchors remain.
filler_rules=[
    ('먼저 그림의 단서를 살펴보자. ',''),
    ('이 장면에 연결할 내용이다. ','연결할 내용이다. '),
    ('장면과 연결을 빠짐없이 다시 짚어 보자.','다시 짚어 보자.'),
    ('이 말에 두 혈의 이름을 붙여 기억하자.','두 혈을 함께 기억하자.'),
]
filler=[]
for r in records:
    for old,new in filler_rules:
        count=r['narration'].count(old)
        if count:
            filler.append(dict(card_id=r['card_id'],before=old,after=new,count=count))
            r['narration']=r['narration'].replace(old,new)

# Targeted follow-up review: keep noun names audible after shortening endings.
post_review=json.loads((OUT/'post-conversion-review-edits.json').read_text())
for e in post_review['edits']:
    r=by_id[e['card_id']]
    assert r['narration']==e['before'],e['card_id']
    r['narration']=e['after']

visual=json.loads((OUT/'visual-audit.json').read_text())
vmap={v['lesson_id']:v for v in visual['observations']}
manual_ids={e['card_id'] for e in manual['edits']}
new_holds=[]
for r in main['records']:
    v=vmap[r['lesson_id']]
    r['visual_review']='scene_cues_viewed_details_not_certified'
    r['visual_audit_status']=v['status']
    r['visual_audit_note']=v['note']
    affected=v.get('cards',[])
    if v['status'] in {'mismatch','partial'}:
        # Intro/review can repeat affected material; keep them in the review queue.
        if r['card_id'] in affected or r['kind'] in {'frame','review'} or not affected:
            reason='이번 그림 대조: '+v['note']
            r['hold_reasons'].append(reason)
            if r['production_status']!='hold':new_holds.append(r['card_id'])
            r['production_status']='hold'
    r['text_changed']=r['narration']!=r['original_tts']
    r['edit_status']='rewritten' if r['text_changed'] else 'preserved'
    r['edit_reason'] += ' 이번 판은 반말 서술체로 정리했으며 실제 그림의 주요 단서 검토 결과는 visual_audit_note에 기록했다. 원전·정밀 해부·발음의 완전 검증과 구별한다.'
    if r['card_id'] in manual_ids:r['edit_reason']+=' 누락 용어·연결 또는 그림 위치 설명을 수동 보완했다.'
for r in records:
    r['spoken_text_sha256']=sha(r['narration'])
    r['style']='해라체 중심의 짧은 반말 서술체'
    r['ready_to_generate']=False

held=sum(r['production_status']=='hold' for r in main['records'])
changed=sum(a['narration']!=b['narration'] for a,b in zip(baseline,records))
summary=main['summary']
summary.update(changed_texts=sum(r['text_changed'] for r in main['records']),unchanged_texts=sum(not r['text_changed'] for r in main['records']),draft_candidates=2067-held,held_stations=held,ready_to_generate=0,lessons_with_holds=len({r['lesson_id'] for r in main['records'] if r['production_status']=='hold'}))
summary['scope']='본편 227과의 주요 그림 단서를 실제 열람했다. 전 의학적 사실·정밀 해부·발음·부록 그림 전체의 무결성 보장은 아니다.'
summary['review_baseline_revision']=BASE
summary['plain_style_changed_from_review']=sum(a['narration']!=b['narration'] for a,b in zip(baseline[:2067],main['records']))

dump('narrations.json',main);dump('panel-narrations.json',panel)
dump('plain-style-changes.json',{'baseline':BASE,'ending_changes':style,'scaffolding_shortening':filler})
with (OUT/'narrations.csv').open('w',encoding='utf-8-sig',newline='') as f:
    cols=['card_id','lesson_title','kind','production_status','text_changed','narration','original_tts','hold_reasons','edit_reason','spoken_text_sha256','visual_audit_status','visual_audit_note']
    w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n');w.writeheader()
    for r in main['records']:
        row=dict(r);row['hold_reasons']=' | '.join(row['hold_reasons']);w.writerow(row)
for name,rs in [('narrations.txt',main['records']),('panel-narrations.txt',panel['records']+panel['bagua'])]:
    lines=['반말 낭독 검토본 · 2026-11-20','보류 표시는 검토용이며 낭독하지 않는다. 생성 승인본이 아니다.','']
    for r in rs:
        if not r['narration']:continue
        state='녹음 보류' if r['production_status']=='hold' else '검토 초안'
        lines.extend([f"[{r['card_id']}] {state}",r['narration'],''])
    (OUT/name).write_text('\n'.join(lines),encoding='utf-8')

# Preserve and verify every source field; manual changes have a separate ledger.
old_by_id={r['card_id']:r for r in baseline}
assert len(by_id)==2809
assert [r['card_id'] for r in baseline]==[r['card_id'] for r in records]
for r in records:
    old=old_by_id[r['card_id']]
    for key in ['original_tts','source_station','source_row','source_system','source_cues','retained_terms']:
        assert r.get(key)==old.get(key),(r['card_id'],key)
    assert set(old.get('hold_reasons',[]))<=set(r.get('hold_reasons',[]))
    assert re.findall('“[^”]+”',old['narration'])==re.findall('“[^”]+”',r['narration']),r['card_id']
    assert r['spoken_text_sha256']==sha(r['narration'])
    assert not re.search(r'(?:습니다|입니다|[봅합됩]니다|세요|지요)(?=[.!?\s”]|$)',r['narration']),r['card_id']
for cid in ['new-gr-32#1','new-gr-32#7']:
    assert '45세' in by_id[cid]['narration'] or '사십오세' in by_id[cid]['narration'] or '마흔다섯' in by_id[cid]['narration']
for r in records:
    # Numeric literals cannot disappear in an ending/preamble edit.
    assert collections.Counter(re.findall(r'\d+',old_by_id[r['card_id']]['narration'])) <= collections.Counter(re.findall(r'\d+',r['narration'])),r['card_id']
image_blobs={r['lesson_image']:r['lesson_image_git_blob_sha1'] for r in main['records']}
for path,expected in image_blobs.items():
    data=(ROOT/path).read_bytes()
    assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==expected,path

validation={
    'passed':True,'baseline':BASE,'lessons':227,'main_scripts':2067,
    'appendix_spoken_rows':737,'appendix_excluded_rows':3,'bagua_scripts':2,
    'total_spoken_scripts':2806,'total_changed_from_previous_review':changed,
    'ending_changed_scripts':len(style),'manual_content_changed_scripts':len(manual_ids),
    'post_conversion_review_edits':len(post_review['edits']),
    'ending_only_chars_saved':sum(e['before_chars']-e['after_chars'] for e in style),
    'scaffolding_chars_saved':sum((len(e['before'])-len(e['after']))*e['count'] for e in filler),
    'before_chars':sum(len(r['narration']) for r in baseline),
    'after_chars':sum(len(r['narration']) for r in records),
    'main_held':held,'new_main_holds':len(new_holds),'new_main_hold_ids':new_holds,
    'ready_to_generate':0,'source_fields_preserved':True,'quoted_mnemonics_preserved':True,
    'old_holds_preserved':True,'remaining_polite_endings':0,'text_hashes_match':True,
    'image_scenes_viewed':len(vmap),'image_blobs_match_pinned_source':True,'numeric_literals_retained':True,'visual_status_counts':dict(collections.Counter(v['status'] for v in vmap.values())),
    'scope':'구조·원본·인용 니모닉·변경 기록·문체·해시 검사. 의미 동일성이나 임상 정확성의 자동 증명이 아니다.',
    'limitations':['현재 본편 이미지의 주요 단서 대조이며 모든 미세 묘사의 정확성을 보증하지 않는다.','부록 79판은 문체 변환과 원본 보존 검사이며 실물 그림 전수 검토는 미수행. why 필드의 개념·제작 이력 분리와 추가 윤문은 미완료.','원전 전수 검증·음성 발음 및 청취 검수는 수행하지 않았다.','실제 녹음 시간은 생성 전이므로 측정하지 않았다.']
}
dump('plain-style-validation.json',validation)
dump('validation.json',{'coverage_pass':True,'summary':summary,'plain_style_validation':'plain-style-validation.json','visual_audit':'visual-audit.json','limitations':validation['limitations']})
dump('package-integrity.json',{'passed':True,'lesson_ids':227,'station_ids':2067,'panel_rows':740,'excluded_metadata_rows':3,'bagua_scripts':2,'html_cards':2809,'original_tts_preserved':True,'spoken_text_hashes_match':True,'user_45_year_mnemonic_restored':True,'quoted_mnemonics_preserved':True,'ready_to_generate':0,'scope':validation['scope']})

# Keep the same URLs; load current image once per lesson for practical review.
original_html=old_file('narration-review.html')
css=re.search(r'<style>(.*?)</style>',original_html,re.S).group(1)
js=re.search(r'<script>(.*?)</script>',original_html,re.S).group(1)
sample=re.search(r'<audio\b.*?</audio>',original_html,re.S).group()
esc=lambda s:html.escape(str(s),quote=True)
labels={'visible_cues_match':'주요 단서 확인','partial':'세부 미확정','mismatch':'불일치 발견','resolved_text':'설명 보완'}
parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>한의학 반말 낭독 대본 검토본</title><style>'+css+'img.scene{display:block;max-width:100%;height:auto;border-radius:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>',
f'<header><p>2026-11-20 · 한의학 Sketchy</p><h1>반말 낭독 대본과 그림 대조</h1><p class="counts">본편 227과 · 2,067구간 · 녹음 보류 {held:,}</p>',
'<p>전체 낭독문 2,806개를 반말 서술체로 정리했다. 원대본·정답·니모닉과 보류 이력은 각 카드에 보존했다. 본편 그림의 주요 단서를 실제 대조했고, 세부 미확정과 불일치를 구별해 표시했다. 의학적 무결성이나 녹음 승인 완료를 뜻하지 않는다.</p>',
f'<p><a href="{REL}/audit-report.md">검토 결과</a> · <a href="{REL}/narrations.txt" download>본편 TXT</a> · <a href="{REL}/narrations.csv" download>본편 CSV</a> · <a href="{REL}/panel-narrations.txt" download>부록 TXT</a> · <a href="{REL}/narrations.json">본편 JSON</a></p>',
f'<p><a href="{REL}/post-conversion-review.md">반말 변환 후 재검토</a> · 인명·독음의 모호한 축약 2곳과 기존 문장부호 1곳을 보완했다.</p>',
'<details><summary>이전 대본의 Gemini 샘플 · 이번 반말판과 다름</summary><p>기존 46.2초 샘플이다. 이번 수정 대본의 음성은 아직 생성하지 않았다.</p>'+sample+'</details></header>',
'<main><div class="toolbar"><input id="search" placeholder="과 이름·한자·혈명·단서 검색" aria-label="대본 검색"><select id="state" aria-label="상태"><option value="all">전체</option><option value="candidate">보류 없는 초안</option><option value="hold">녹음 보류</option></select></div><p id="visible"></p><details><summary>227과 목차</summary><ol>']
groups=collections.OrderedDict()
for r in main['records']:groups.setdefault(r['lesson_id'],[]).append(r)
for lid,rs in groups.items():parts.append(f'<li><a href="#{lid}">{esc(lid)} · {esc(rs[0]["lesson_title"])}</a></li>')
parts.append('</ol></details>')
def card(r):
    held=r['production_status']=='hold';state='hold' if held else 'candidate'
    cid=r['card_id'];original=r.get('original_tts','');notes=r.get('hold_reasons',[])
    block=[f'<article class="card{" held" if held else ""}" id="{esc(cid)}" data-state="{state}"><h3>{esc(cid)} <span class="badge">{"녹음 보류" if held else "제작 메모 제외" if not r["narration"] else "검토 초안"}</span></h3><p class="script">{esc(r["narration"])}</p>']
    if notes:block.append('<ul class="reasons">'+''.join('<li>'+esc(n)+'</li>' for n in notes)+'</ul>')
    if original:block.append('<details><summary>수정 전 원대본과 편집 이유</summary><p>'+esc(original)+'</p><p class="note">'+esc(r.get('edit_reason',''))+'</p></details>')
    old=old_by_id[cid]['narration']
    if old!=r['narration']:block.append('<details><summary>이번 반말 변환 전 검토 대본</summary><p>'+esc(old)+'</p></details>')
    source=r.get('source_station',r.get('source_row',r.get('source_cues',{})))
    block.append('<details><summary>원문·정답·연결 단서 확인</summary><pre>'+esc(json.dumps(source,ensure_ascii=False,indent=2))+'</pre></details></article>')
    return ''.join(block)
for lid,rs in groups.items():
    v=vmap[lid]
    parts.append(f'<section id="{lid}"><h2>{esc(lid)} · {esc(rs[0]["lesson_title"])}</h2><p class="badge">{labels[v["status"]]}</p><p class="note">{esc(v["note"])}</p><a href="{esc(rs[0]["lesson_image"])}" target="_blank" rel="noopener"><img class="scene" src="{esc(rs[0]["lesson_image"])}" alt="{esc(lid)} 현재 그림" loading="lazy" width="1024"></a>')
    parts.extend(card(r) for r in rs);parts.append('</section>')
parts.append('<section id="appendix"><h2>부록 79판 · 737행과 제외 3행</h2><p>반말 변환을 적용했다. 부록의 그림 전수 대조와 why에 섞인 제작 이력·추가 개념의 완전 분리는 미완료다.</p>')
parts.extend(card(r) for r in panel['records']);parts.append('</section><section id="bagua"><h2>괘도 대본 2종</h2>')
parts.extend(card(r) for r in panel['bagua']);parts.append('</section></main><script>'+js+'</script></html>')
(ROOT/'narration-review.html').write_text('\n'.join(parts),encoding='utf-8')

percent=100*(validation['before_chars']-validation['after_chars'])/validation['before_chars']
report=['# 반말 낭독 대본 검토 결과 — 2026-11-20','',
f'본편 227과 2,067구간, 부록 737행, 괘도 2종의 총 2,806개 낭독문을 정리했다. 이번 판에서 실제 문장이 달라진 원고는 {changed:,}개다. 제작 메모 3행은 기존대로 낭독에서 제외했다.','',
f'원본과 대조해 누락 용어·연결 및 위치 표현을 {len(manual_ids)}개 원고에서 수동 보완했다. 복원과 위치 설명의 정확한 전후 문장은 `narration-content-edits.json`에 남겼다. 성미·승강부침·온보비위·설상·장상·관수본초 등의 누락을 보완했다. 원자료의 임상 사실 자체를 새로 검증했다는 뜻은 아니다.','',
'‘45세부터 위가 약해진다’ 이야기와 사암침법 이름 잇기 등 기존 큰따옴표 니모닉을 그대로 보존했다. 원대본, 원문 필드, 카드 순서, 기존 보류 이유도 모두 보존 검사했다.','',
f'어미 변경으로 {validation["ending_only_chars_saved"]:,}자, 반복 안내말 정리로 {validation["scaffolding_chars_saved"]:,}자를 줄였다. 필요한 내용을 복원한 뒤 최종 전체 분량은 {validation["before_chars"]:,}자에서 {validation["after_chars"]:,}자로 {percent:.2f}% 줄었다. 실제 녹음 시간은 아직 측정하지 않았다.','',
'## 그림 검토의 범위','',
'현재 본편 227개 그림을 열람해 주요 소품·위치·수량을 원자료 obj/hook 및 대본과 대조했다. 의심되는 숫자 일부는 확대했다. 주요 장면 일치와 미세 해부학·본초 식별·의학 원전의 정확성은 구별한다. 각 과의 확인 내용은 `visual-audit.json`에 있다.','',
'| 상태 | 과 수 |','|---|---:|']
for k,n in validation['visual_status_counts'].items():report.append(f'| {labels[k]} | {n} |')
report+=['',f'기존 본편 보류 339개에 이번 대조에서 {len(new_holds)}개를 추가해 총 {held}개를 보류했다. 보류 없는 {2067-held}개도 녹음 승인본이 아니다. 이번 수정본의 음성 생성은 0개다.','',
'## 남은 불일치와 미확정 사항','','| 과 | 상태 | 확인 내용 |','|---|---|---|']
for v in visual['observations']:
    if v['status'] in {'mismatch','partial'}:report.append(f'| {v["lesson_id"]} | {labels[v["status"]]} | {v["note"].replace("|","/")} |')
report+=['','## 범위 밖 검증','']+[f'- {x}' for x in validation['limitations']]+['','검토 페이지와 녹음용 원고 자료를 갱신했다. 기존 학습 플레이어의 say/tts와 과거 원문은 교체하지 않았다.','']
report+=['## 반말 변환 후 재검토','','인명 마시와 한자 독음 이가 어미와 붙어 모호해지는 2곳을 보완했다. 기존 물음표 뒤 쉼표 중복 1곳도 정리했다. [재검토 결과](post-conversion-review.md)와 [정확한 수정 전후](post-conversion-review-edits.json)를 참조한다.','']
(OUT/'audit-report.md').write_text('\n'.join(report),encoding='utf-8')
(OUT/'README.md').write_text(f'''# 그림 낭독 대본 검토본 — 반말판

[검토 페이지](https://baeggman.github.io/sketchy/narration-review.html) · [이번 검토 결과](audit-report.md)

본편 227과 2,067구간, 부록 737행, 괘도 2종의 2,806개 낭독문을 반말 서술체로 정리했다. ‘45세부터 위가 약해진다’를 포함한 사용자 니모닉, 원대본과 원문 필드, 기존 보류 이력을 보존했다.

본편 주요 그림 단서 227과를 대조했고 누락 용어·연결과 위치 설명을 {len(manual_ids)}개 원고에서 보완했다. 본편 녹음 보류는 {held}개다. 보류 없는 {2067-held}개도 초안이며 무결성이나 음성 생성 승인을 뜻하지 않는다. 부록의 실제 그림 전수 검토와 why 필드의 추가 의미 검토는 미완료다.

- [본편 TXT](narrations.txt) · [CSV](narrations.csv) · [JSON](narrations.json)
- [부록 TXT](panel-narrations.txt) · [JSON](panel-narrations.json)
- [그림 대조](visual-audit.json) · [수동 내용 보완 전후](narration-content-edits.json)
- [어미와 안내말 변경 기록](plain-style-changes.json) · [보존 검사](plain-style-validation.json)
- [반말 변환 후 재검토](post-conversion-review.md) · [추가 수정 전후](post-conversion-review-edits.json)
- [이전 의미 검토 기록](semantic-qc.json) · [Gemini 실행계획](opus-gemini-execution-plan.md)

이전 검토본 기준은 `{BASE}`, 최초 원자료 기준은 `{summary['source_revision']}`다. `python src/lessons/tools/build_plain_narrations.py`로 이 반말판을 재생성한다. 기존 학습 플레이어 say/tts를 덮어쓰거나 음성을 생성하지 않는다.
''',encoding='utf-8')
print(json.dumps({k:validation[k] for k in ['total_spoken_scripts','total_changed_from_previous_review','manual_content_changed_scripts','main_held','new_main_holds','before_chars','after_chars','visual_status_counts']},ensure_ascii=False,indent=2))
