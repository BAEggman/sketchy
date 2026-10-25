# -*- coding: utf-8 -*-
"""panels/library.json + scenes.json + coverage/blind6_사전요약.md → recall.html   (회상 훈련·측정 페이지)

  허브(index.html)는 「보면서 외우기」, 이 페이지는 「보고 떠올려 스스로 채점하기」다.
  판 하나 → 그림만 보고 자유 회상(적기) → 행마다 ○△✗ 채점 → 저장(localStorage) → 다음 판.
  1단계(사전 없이) / 2단계(사전 읽고) 를 구분해 기록하고, 결과를 JSON 으로 내보낸다(사용자 회상 측정용).
  도해(D)는 답이 그림에 인쇄돼 있어 뺀다(CANON 74). 그림은 images/<id>.webp 외부 링크(허브와 같음).

  usage:  cd src && python3 build_recall.py   → ../recall.html
"""
import json, os, re, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = json.load(open(os.path.join(HERE, 'panels/library.json'), encoding='utf-8'))
SC  = json.load(open(os.path.join(HERE, 'panels/scenes.json'), encoding='utf-8'))
DICT = open(os.path.join(HERE, 'coverage/blind6_사전요약.md'), encoding='utf-8').read()

scene_of = {}
for s in SC['scenes']:
    for i in s['ids']:
        scene_of[i] = s['title']

panels = []
for p in LIB['panels']:
    if p.get('track') == 'D':
        continue
    panels.append({'id': p['id'], 'title': p['title'], 'tag': p.get('tag', ''), 'scene': scene_of.get(p['id'], ''),
                   'rows': [{'prop': r['prop'], 'fact': r['fact'], 'trap': bool(r.get('trap')), 'why': r.get('why', '')}
                            for r in p['rows']]})

def md_to_html(md):
    out = []
    for line in md.split('\n'):
        t = line.rstrip()
        if not t:
            continue
        t = (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        if t.startswith('# '):
            out.append('<h2>%s</h2>' % t[2:])
        elif t.startswith('## '):
            out.append('<h3>%s</h3>' % t[3:])
        elif t.startswith('&gt; '):
            out.append('<blockquote>%s</blockquote>' % t[5:])
        elif t.startswith('- '):
            head = t[2:].split(' = ', 1)[0]
            out.append('<div class="de" data-k="%s">%s</div>' % (head.replace('"', ''), t[2:]))
        else:
            out.append('<p>%s</p>' % t)
    return '\n'.join(out)

data_js = json.dumps(panels, ensure_ascii=False).replace('</', '<\\/')
dict_html = md_to_html(DICT)
today = datetime.date.today().isoformat()
n_rows = sum(len(p['rows']) for p in panels)

HTML = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sketchy 회상 훈련</title>
<style>
:root{--ink:#222;--line:#ddd;--acc:#2c7a4b;--trap:#c02020;--ok:#2c7a4b;--half:#c88a00;--no:#c02020}
*{box-sizing:border-box}
body{margin:0;font-family:'Apple SD Gothic Neo',-apple-system,BlinkMacSystemFont,'Pretendard','Malgun Gothic','맑은 고딕','Noto Sans KR','Noto Sans CJK KR',sans-serif;color:var(--ink);background:#faf8f4;letter-spacing:.02em;line-height:1.6;-webkit-font-smoothing:antialiased}
header{position:sticky;top:0;background:#fffdf8;border-bottom:1px solid var(--line);padding:10px 14px;z-index:9}
h1{font-size:18px;margin:0 0 8px}
h1 small{font-weight:normal;color:#777;font-size:12px;margin-left:8px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
select{font-size:14px;padding:6px 8px;border:1.5px solid var(--ink);border-radius:8px;background:#fff;max-width:100%}
.btn{display:inline-block;border:1.5px solid var(--ink);border-radius:18px;padding:5px 14px;font-size:14px;cursor:pointer;background:#fff;user-select:none}
.btn.on{background:var(--ink);color:#fff}
.btn.prim{background:var(--acc);border-color:var(--acc);color:#fff}
.btn.sm{padding:3px 10px;font-size:13px}
main{max-width:960px;margin:0 auto;padding:12px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0}
.card h2{font-size:15px;margin:0 0 8px;border-left:5px solid var(--acc);padding-left:8px}
.ttl{font-size:15px;font-weight:600;margin:4px 0 8px}
.ttl .tag{font-size:11px;background:#eef3ee;border-radius:10px;padding:2px 8px;margin-left:6px;font-weight:normal}
img.board{width:100%;height:auto;border:1px solid var(--line);border-radius:8px;cursor:zoom-in;background:#fff}
.timer{font-variant-numeric:tabular-nums;color:#555;font-size:14px}
textarea{width:100%;min-height:150px;font:inherit;font-size:15px;padding:10px;border:1.5px solid var(--line);border-radius:8px;resize:vertical}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{border-top:1px solid var(--line);padding:8px 6px;vertical-align:top;text-align:left}
th{font-size:12px;color:#777;font-weight:normal}
td.prop{width:44%}
td.fact{width:40%}
tr.trap td.prop:before{content:"⚠ ";color:var(--trap)}
td.mk{white-space:nowrap;width:16%}
.mk span{display:inline-block;width:30px;height:30px;line-height:28px;text-align:center;border:1.5px solid var(--line);border-radius:50%;margin-right:3px;cursor:pointer;font-size:14px}
.mk span.on.o{background:var(--ok);border-color:var(--ok);color:#fff}
.mk span.on.h{background:var(--half);border-color:var(--half);color:#fff}
.mk span.on.x{background:var(--no);border-color:var(--no);color:#fff}
tr.r0 td{opacity:.9}
tr.hid td.fact{color:transparent;text-shadow:0 0 9px rgba(0,0,0,.45);user-select:none}
.why{font-size:12px;color:#777;cursor:pointer;margin-left:4px}
tr.reason td{font-size:12px;color:#555;background:#fbfaf6;display:none}
tr.reason.open td{display:table-cell}
.score{font-size:16px;font-weight:600;margin:10px 0}
.score b{color:var(--acc)}
.hidden{display:none}
#dict{max-height:60vh;overflow:auto;font-size:13.5px}
#dict h2{font-size:15px}#dict h3{font-size:14px;margin:12px 0 4px}
#dict .de{padding:3px 0;border-top:1px dashed #eee}
#dict blockquote{margin:6px 0;padding:4px 10px;border-left:3px solid #ddd;color:#555}
#dq{width:100%;font:inherit;padding:6px 8px;border:1.5px solid var(--line);border-radius:8px;margin-bottom:8px}
.res td,.res th{font-size:13px}
.note{font-size:12.5px;color:#666}
footer{font-size:12px;color:#888;padding:20px 14px}
@media (max-width:600px){table.g,table.g tbody,table.g tr,table.g td{display:block;width:auto}table.g thead{display:none}table.g td.prop{border-top:1px solid var(--line);padding-bottom:2px;font-weight:600}table.g td.fact{border-top:0;padding-top:0;color:#333}table.g td.mk{border-top:0;padding-top:2px;padding-bottom:10px}table.g tr.reason td{border-top:0}table.g tr.reason:not(.open) td{display:none}}
</style></head><body>
<header>
 <h1>Sketchy 회상 훈련 <small>판 __NPAN__ · 행 __NROW__ · __TODAY__ 빌드</small></h1>
 <div class="row">
  <select id="sel"></select>
  <span class="btn on" id="st1" data-st="1">1단계 — 사전 없이</span>
  <span class="btn" id="st2" data-st="2">2단계 — 사전 읽고</span>
  <span class="btn" id="bDict">사전</span>
  <span class="btn" id="bRes">결과</span>
 </div>
</header>
<main>
 <div class="card hidden" id="dictCard"><h2>글자 사전 요약 — 2단계 전에 읽는 것</h2>
  <input id="dq" placeholder="찾기 — 글자·사물 (예: 久, 빗자루)">
  <div id="dict">__DICT__</div></div>

 <div class="card hidden" id="resCard"><h2>결과</h2>
  <div class="row" style="margin-bottom:8px"><span class="btn sm" id="bExport">JSON 내보내기</span><span class="btn sm" id="bCopy">클립보드 복사</span><span class="btn sm" id="bClear">전부 지우기</span><span class="note" id="resNote"></span></div>
  <table class="res"><thead><tr><th>날짜</th><th>판</th><th>단계</th><th>○</th><th>△</th><th>✗</th><th>점수</th><th>시간</th></tr></thead><tbody id="resBody"></tbody></table></div>

 <div class="card" id="boardCard">
  <div class="ttl" id="ttl"></div>
  <img class="board" id="img" alt="">
  <div class="row" style="margin-top:8px"><span class="timer" id="timer">0:00</span><span class="note">그림만 보고 떠오르는 사실을 아래에 적는다. 그림을 누르면 원본 크기.</span></div>
 </div>

 <div class="card" id="freeCard">
  <h2>① 떠올리기 — 한 줄에 하나씩</h2>
  <textarea id="free" placeholder="예) 肝은 눈으로 열린다 / 창밖 새순 = 봄 …"></textarea>
  <div class="row" style="margin-top:8px"><span class="btn prim" id="bGrade">② 답 보고 채점하기</span><span class="note">채점으로 넘어가면 시간이 멈춘다.</span></div>
 </div>

 <div class="card hidden" id="gradeCard">
  <h2>② 채점 — 행마다 ○ 떠올렸다 · △ 반쯤 · ✗ 못 떠올렸다</h2>
  <div class="note" style="margin-bottom:6px">첫 행은 틀(무대가 지는 단원 이름). ⚠ 는 함정 행. 「왜?」는 다리(채점 뒤 참고).</div>
  <table class="g"><thead><tr><th>소품</th><th>잠그는 사실</th><th>채점</th></tr></thead><tbody id="rows"></tbody></table>
  <div class="score" id="score"></div>
  <div class="row"><span class="btn prim" id="bSave">저장</span><span class="btn" id="bNext">다음 판 →</span><span class="btn" id="bRedo">이 판 다시</span><span class="note" id="saveNote"></span></div>
 </div>
</main>
<footer>자가 채점이라 느슨해지기 쉽다 — 「○」는 사실의 핵심어(장부·글자·수)까지 떠올랐을 때만. 결과 JSON 은 「결과 → 내보내기」로 받아 Claude 에게 보내면 판·행별로 분석한다. 저장은 이 브라우저(localStorage)에만 남는다.</footer>
<script>
const P=__DATA__;
const KEY='sketchy_recall_v1';
let cur=0, stage=1, t0=0, tick=null, secs=0, marks=[];
const $=id=>document.getElementById(id);
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){return []}}
function store(a){try{localStorage.setItem(KEY,JSON.stringify(a))}catch(e){}}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/\*\*(.+?)\*\*/g,'<b>$1</b>').replace(/\n/g,'<br>')}
function fmt(s){return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
// select
(function(){let last='';let html='';P.forEach((p,i)=>{if(p.scene!==last){if(last)html+='</optgroup>';html+='<optgroup label="'+esc(p.scene)+'">';last=p.scene}html+='<option value="'+i+'">'+esc(p.title.length>46?p.title.slice(0,46)+'…':p.title)+'</option>'});if(last)html+='</optgroup>';$('sel').innerHTML=html})();
function show(i){cur=i;const p=P[i];$('sel').value=i;location.hash=p.id;
 $('ttl').innerHTML=esc(p.title)+'<span class="tag">'+esc(p.tag)+'</span><span class="tag">#'+p.id+'</span>';
 $('img').src='images/'+p.id+'.webp';$('img').onclick=()=>window.open('images/'+p.id+'.webp');
 $('free').value='';$('gradeCard').classList.add('hidden');$('freeCard').classList.remove('hidden');$('saveNote').textContent='';
 marks=p.rows.map(()=>null);secs=0;$('timer').textContent='0:00';clearInterval(tick);t0=Date.now();tick=setInterval(()=>{secs=Math.round((Date.now()-t0)/1000);$('timer').textContent=fmt(secs)},500);
 window.scrollTo(0,0)}
$('sel').onchange=e=>show(+e.target.value);
document.querySelectorAll('[data-st]').forEach(b=>b.onclick=()=>{stage=+b.dataset.st;$('st1').classList.toggle('on',stage===1);$('st2').classList.toggle('on',stage===2);if(stage===2)$('dictCard').classList.remove('hidden')});
$('bDict').onclick=()=>$('dictCard').classList.toggle('hidden');
$('bRes').onclick=()=>{renderRes();$('resCard').classList.toggle('hidden')};
$('dq').oninput=e=>{const q=e.target.value.trim();document.querySelectorAll('#dict .de').forEach(d=>{d.style.display=(!q||d.textContent.includes(q))?'':'none'})};
function grade(){clearInterval(tick);secs=Math.round((Date.now()-t0)/1000);$('timer').textContent=fmt(secs);
 const p=P[cur];let h='';p.rows.forEach((r,i)=>{h+='<tr class="'+(r.trap?'trap ':'')+(i?'':'r0')+'" data-i="'+i+'"><td class="prop">'+esc(r.prop)+(r.why?' <span class="why">왜?</span>':'')+'</td><td class="fact">'+esc(r.fact)+'</td><td class="mk"><span class="o" data-m="o">○</span><span class="h" data-m="h">△</span><span class="x" data-m="x">✗</span></td></tr>';
  if(r.why)h+='<tr class="reason"><td colspan="3">다리 — '+esc(r.why)+'</td></tr>'});
 $('rows').innerHTML=h;$('gradeCard').classList.remove('hidden');$('freeCard').classList.add('hidden');calc();
 $('rows').querySelectorAll('.mk span').forEach(s=>s.onclick=()=>{const tr=s.closest('tr'),i=+tr.dataset.i;tr.querySelectorAll('.mk span').forEach(x=>x.classList.remove('on'));s.classList.add('on');marks[i]=s.dataset.m;calc()});
 $('rows').querySelectorAll('.why').forEach(w=>w.onclick=()=>{w.closest('tr').nextElementSibling.classList.toggle('open')});
 $('gradeCard').scrollIntoView({behavior:'smooth'})}
function calc(){const n=marks.length,o=marks.filter(m=>m==='o').length,h=marks.filter(m=>m==='h').length,x=marks.filter(m=>m==='x').length,u=n-o-h-x;const sc=((o+h*0.5)/n*100).toFixed(0);
 $('score').innerHTML='○ '+o+' · △ '+h+' · ✗ '+x+(u?' · 미채점 '+u:'')+' / '+n+'행 — <b>'+sc+'%</b> · '+fmt(secs);return {n,o,h,x,u,sc:+sc}}
$('bGrade').onclick=grade;
$('bSave').onclick=()=>{const s=calc();if(s.u){if(!confirm('미채점 '+s.u+'행은 ✗로 저장됩니다. 저장할까요?'))return;marks=marks.map(m=>m||'x');s.x+=s.u;s.u=0;calc()}
 const a=load();a.push({id:P[cur].id,title:P[cur].title,stage,date:new Date().toISOString().slice(0,16).replace('T',' '),secs,o:s.o,h:s.h,x:s.x,n:s.n,score:s.sc,marks:marks.slice(),free:$('free').value});store(a);$('saveNote').textContent='저장됨 ('+a.length+'건)';renderRes()};
$('bNext').onclick=()=>show((cur+1)%P.length);
$('bRedo').onclick=()=>show(cur);
function renderRes(){const a=load();$('resBody').innerHTML=a.slice().reverse().map(r=>'<tr><td>'+r.date+'</td><td>'+esc(r.title.slice(0,28))+' <span class="note">#'+r.id+'</span></td><td>'+r.stage+'</td><td>'+r.o+'</td><td>'+r.h+'</td><td>'+r.x+'</td><td><b>'+r.score+'%</b></td><td>'+fmt(r.secs)+'</td></tr>').join('')||'<tr><td colspan="8" class="note">아직 저장된 결과가 없다.</td></tr>';
 const s1=a.filter(r=>r.stage===1),s2=a.filter(r=>r.stage===2);const avg=l=>l.length?(l.reduce((t,r)=>t+r.score,0)/l.length).toFixed(0)+'%':'—';$('resNote').textContent='1단계 평균 '+avg(s1)+' ('+s1.length+'건) · 2단계 평균 '+avg(s2)+' ('+s2.length+'건)'}
function payload(){return JSON.stringify({exported:new Date().toISOString(),build:'__TODAY__',attempts:load()},null,1)}
$('bExport').onclick=()=>{const b=new Blob([payload()],{type:'application/json'});const u=URL.createObjectURL(b);const l=document.createElement('a');l.href=u;l.download='sketchy_recall_'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(l);l.click();l.remove();setTimeout(()=>URL.revokeObjectURL(u),2000)};
$('bCopy').onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText(payload()).then(()=>$('resNote').textContent='복사됨').catch(()=>$('resNote').textContent='복사 실패 — 내보내기를 쓰세요')};
$('bClear').onclick=()=>{if(confirm('저장된 결과를 모두 지울까요? (내보내기 먼저)')){store([]);renderRes()}};
(function(){const h=location.hash.slice(1);const i=P.findIndex(p=>p.id===h);show(i>=0?i:0)})();
</script></body></html>
'''
out = (HTML.replace('__DATA__', data_js).replace('__DICT__', dict_html)
          .replace('__NPAN__', str(len(panels))).replace('__NROW__', str(n_rows)).replace('__TODAY__', today))
dst = os.path.join(HERE, '..', 'recall.html')
open(dst, 'w', encoding='utf-8').write(out)
print('written recall.html %.2f MB — panels %d rows %d' % (os.path.getsize(dst) / 1e6, len(panels), n_rows))
