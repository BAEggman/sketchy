"""P2 시범 검수 화면 → pilot_review.html

그림만 보고 답하는 문항(Run 1 의학사 넷 × 5 = 20 + 督脈 5 + 醋炙 5)을 그림 옆에 두고,
「답 보기」 뒤 스스로 맞음/틀림을 매긴다. 넘어가는 기준(계획서 7절): 의학사 20문항 중 16 이상 + 「넓혀도 된다」.
기록은 localStorage 'sketchy_pilot_review_v1'(막히면 메모리). 내보내기(JSON)로 Opus에게 건넨다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / 'src/lessons/l'
GV_Q = [
    {'q': '붉은 실선이 겉으로 처음 나오는 혈(꼬리 끝 물결)과 끝나는 혈(입 안)은?', 'a': '長强(GV1) → 齦交(GV28)'},
    {'q': '목 아래 큰 점(대추 두 알)은 무슨 혈이고, 거기서 무엇이 모이나?', 'a': '大椎 — 陽經의 經氣가 모두 大椎에서 交會(그래서 督脈 = 陽脈之海)'},
    {'q': '정수리 왕관 자리 혈과, 그곳에서 督脈과 만나는 경맥은?', 'a': '百會 — 足厥陰肝經(上額與足厥陰交于巔)'},
    {'q': '꼬리 끝 長强은 시작 혈 말고 무슨 혈이기도 한가?', 'a': '督脈之絡(15絡脈 — 靈樞 經脈篇 학설)'},
    {'q': '督脈의 혈 수 · 별칭 · 병증은? (속 갈래 점선 셋은 어디로 가나?)', 'a': '28혈 · 陽脈之海(諸陽之海) · 脊强而折厥 / 腦에 屬 · 腎에 絡 · 心을 貫'},
]


def lesson(lid):
    return json.loads((L / f'{lid}.json').read_text(encoding='utf-8'))


def main():
    blocks = []
    for lid in ['pilot-tao', 'pilot-wangbing', 'pilot-duben', 'pilot-xue']:
        x = lesson(lid)
        blocks.append({'id': lid, 'title': x['title'], 'image': x['image'], 'group': 'hist', 'qs': x['attrs']['questions']})
    g = lesson('pilot-gv')
    blocks.append({'id': 'pilot-gv', 'title': g['title'], 'image': g['attrs']['blank_image'], 'image2': g['image'], 'group': 'gv', 'qs': GV_Q})
    cho = ROOT / 'src/lessons/l/pilot-cho.json'
    if cho.exists():
        c = json.loads(cho.read_text(encoding='utf-8'))
        blocks.append({'id': 'pilot-cho', 'title': c['title'], 'image': c['image'], 'group': 'cho', 'qs': c['attrs'].get('questions', [])})
    data = json.dumps(blocks, ensure_ascii=False).replace('<', '\\u003c')
    html = TEMPLATE.replace('__DATA__', data)
    (ROOT / 'pilot_review.html').write_text(html, encoding='utf-8')
    print('written pilot_review.html — %d 그림 · %d 문항' % (len(blocks), sum(len(b['qs']) for b in blocks)))


TEMPLATE = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>P2 시범 검수 — 그림만 보고 답하기</title>
<style>
:root{--paper:#faf8f2;--ink:#233d35;--muted:#61766c;--line:#d8e0d7;--green:#2d7159;--bad:#b23b3b}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:'Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR',sans-serif;line-height:1.6}
header,main{max-width:1180px;margin:auto;padding:14px 18px}h1{font-size:clamp(22px,4vw,32px);margin:6px 0}
.score{position:sticky;top:0;background:#fffdf8;border:1px solid var(--line);border-radius:12px;padding:8px 12px;z-index:2;display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:14px 0}
.card h2{font-size:18px;margin:0 0 8px}.card img{width:100%;height:auto;border-radius:10px;border:1px solid var(--line);cursor:zoom-in}
.q{border-top:1px dashed var(--line);padding:8px 0}.q p{margin:0 0 4px}.a{background:#eef7f0;border-radius:8px;padding:6px 10px;margin:4px 0}
button{font:inherit;cursor:pointer;border:1px solid var(--line);background:#fffdf8;border-radius:9px;padding:5px 11px}
button[aria-pressed=true].ok{background:var(--green);color:#fff;border-color:var(--green)}button[aria-pressed=true].no{background:var(--bad);color:#fff;border-color:var(--bad)}
.muted{color:var(--muted);font-size:13px}.row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
textarea{width:100%;font:inherit;border:1px solid var(--line);border-radius:8px;padding:6px;min-height:2.4em}
.pass{color:var(--green);font-weight:700}.fail{color:var(--bad);font-weight:700}
</style></head><body>
<header><div class="muted"><a href="index.html">← 허브</a> · <a href="lessons.html">교재 목차 그림</a></div>
<h1>P2 시범 검수 — 그림만 보고 답하기</h1>
<p class="muted">각 그림을 먼저 보고 문항에 소리 내어 답한 뒤 「답 보기」 → 맞음/틀림을 고른다. 틀리면 까닭을 고른다(소리 · 관계 · 크기 · 사실). 통과 기준: 의학사 20문항 중 16 이상 + 「넓혀도 된다」.</p></header>
<main>
<div class="score" id="score"></div>
<div id="list"></div>
<div class="card"><h2>마지막 판단</h2><div class="row"><button id="go" data-v="wide">넓혀도 된다</button><button id="fix" data-v="fix">고치고 다시</button><button id="exp">결과 내보내기(JSON)</button></div>
<textarea id="memo" placeholder="전체 메모(선택)"></textarea></div>
</main>
<script>
(function(){
var B=__DATA__, KEY='sketchy_pilot_review_v1', mem=false, R;
try{R=JSON.parse(localStorage.getItem(KEY)||'null')||{marks:{},why:{},memo:'',verdict:null};}catch(e){mem=true;R={marks:{},why:{},memo:'',verdict:null};}
function save(){if(mem)return;try{localStorage.setItem(KEY,JSON.stringify(R));}catch(e){mem=true;}}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
var list=document.getElementById('list'),h='';
B.forEach(function(b){
  h+='<section class="card"><h2>'+esc(b.title)+'</h2><img loading="lazy" src="'+esc(b.image)+'" alt="'+esc(b.title)+'">'+
     (b.image2?'<div class="muted">빈 판입니다. 답을 맞춘 뒤 <a href="'+esc(b.image2)+'" target="_blank">이름 있는 판</a>을 보세요.</div>':'');
  b.qs.forEach(function(q,i){var k=b.id+'#'+i,m=R.marks[k];
    h+='<div class="q"><p><b>'+(i+1)+'.</b> '+esc(q.q)+'</p><div class="row"><button class="show" data-k="'+k+'">답 보기</button>'+
       '<button class="ok" data-k="'+k+'" data-m="1" aria-pressed="'+(m===1)+'">맞음</button><button class="no" data-k="'+k+'" data-m="0" aria-pressed="'+(m===0)+'">틀림</button>'+
       '<select data-why="'+k+'"><option value="">틀린 까닭</option>'+['소리가 안 나옴','관계가 안 보임','소품이 작음','사실이 헷갈림'].map(function(w){return '<option'+(R.why[k]===w?' selected':'')+'>'+w+'</option>';}).join('')+'</select></div>'+
       '<div class="a" hidden>'+esc(q.a)+'</div></div>';});
  h+='</section>';});
list.innerHTML=h;
function score(){var hs=0,hn=0,all=0,n=0;B.forEach(function(b){b.qs.forEach(function(q,i){var m=R.marks[b.id+'#'+i];if(m!=null){n++;all+=m;if(b.group==='hist'){hn++;hs+=m;}}});});
  var tot=B.filter(function(b){return b.group==='hist';}).reduce(function(s,b){return s+b.qs.length;},0);
  document.getElementById('score').innerHTML='<span>의학사 <b>'+hs+'</b> / '+tot+(hn<tot?' (매긴 '+hn+')':'')+' — '+(hn===tot?(hs>=16?'<span class="pass">기준 16 넘음</span>':'<span class="fail">기준 16 미달</span>'):'채점 중')+'</span><span>전체 '+all+' / '+n+' 매김</span><span class="muted">'+(mem?'저장 막힘 — 이 창에서만 기억':'자동 저장')+'</span>'+(R.verdict?'<span>판단: <b>'+(R.verdict==='wide'?'넓혀도 된다':'고치고 다시')+'</b></span>':'');}
list.addEventListener('click',function(e){var t=e.target;if(t.classList.contains('show')){t.parentNode.nextElementSibling.hidden=false;return;}
  if(t.dataset.m!=null){var k=t.dataset.k;R.marks[k]=+t.dataset.m;save();Array.prototype.forEach.call(list.querySelectorAll('button[data-k="'+k+'"][data-m]'),function(x){x.setAttribute('aria-pressed',x===t);});score();}});
list.addEventListener('change',function(e){var k=e.target.dataset.why;if(k){R.why[k]=e.target.value;save();}});
list.addEventListener('click',function(e){if(e.target.tagName==='IMG')window.open(e.target.src,'_blank');});
var memo=document.getElementById('memo');memo.value=R.memo||'';memo.oninput=function(){R.memo=memo.value;save();};
['go','fix'].forEach(function(id){document.getElementById(id).onclick=function(){R.verdict=this.dataset.v;save();score();};});
document.getElementById('exp').onclick=function(){var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({blocks:B.map(function(b){return {id:b.id,qs:b.qs.length};}),result:R},null,1)],{type:'application/json'}));a.download='pilot_review_'+new Date().toISOString().slice(0,10)+'.json';a.click();};
score();
})();
</script></body></html>
'''

if __name__ == '__main__':
    main()
