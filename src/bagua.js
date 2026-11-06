'use strict';
const baguaData=JSON.parse(document.getElementById('bagua-data').textContent);
const directionNames={N:'북',NE:'동북',E:'동',SE:'동남',S:'남',SW:'서남',W:'서',NW:'서북'};
const southUp=['SE','S','SW','E',null,'W','NE','N','NW'];
const northUp=['NW','N','NE','W',null,'E','SW','S','SE'];
const bankOrder=['건','곤','진','손','감','리','간','태'];
let activeSystem='early',northOnTop=false,practicing=false,selected=null,answers={},graded=false;
const byId=id=>document.getElementById(id);
const escapeText=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function trigram(name){
 const lines=baguaData.trigrams[name].lines;
 return '<svg class="trigram" viewBox="0 0 42 28" aria-hidden="true">'+lines.map((solid,i)=>solid?`<path d="M2 ${4+i*10}H40" stroke="currentColor" stroke-width="5"/>`:`<path d="M2 ${4+i*10}H17 M25 ${4+i*10}H40" stroke="currentColor" stroke-width="5"/>`).join('')+'</svg>';
}
function displayName(name){return `${baguaData.trigrams[name].han}(${name})`;}
function renderBoard(){
 const system=baguaData.systems[activeSystem];
 byId('map-title').textContent=system.name+' 방위판';
 byId('orientation-note').textContent=northOnTop?'북 ↑ · 동 →':'남 ↑ · 동 ←';
 byId('orientation').textContent=northOnTop?'전통 방위로 바꾸기':'북쪽 위로 바꾸기';
 byId('map-note').textContent=practicing?'방위 이름을 보고 채워 봐. 화면의 좌우만 외우지 않기.':northOnTop?'익숙한 지도 방향. 전통도 전체를 180° 돌렸어.':'전통 방위도: 위 남 · 아래 북 · 왼쪽 동 · 오른쪽 서.';
 byId('learning').classList.toggle('practice',practicing);
 byId('board').innerHTML=(northOnTop?northUp:southUp).map(dir=>{
  if(!dir)return `<div class="center"><strong>${system.name}</strong><span>${northOnTop?'북쪽이 위':'남쪽이 위'}</span><span>${practicing?'빈칸 복원':'십자 + 모서리'}</span></div>`;
  const name=practicing?answers[dir]:system.positions[dir];
  const correct=name===system.positions[dir],mark=practicing&&graded&&name?(correct?'✓ 맞음':'↺ 다시'):'';
  const content=`<span class="direction">${directionNames[dir]}</span>`+(name?trigram(name)+`<span class="name">${displayName(name)}</span>`:'<span class="empty">?</span>')+(practicing?`<span class="mark">${mark}</span>`:`<span class="cue"><span class="emoji" aria-hidden="true">${baguaData.trigrams[name].icon}</span>${baguaData.trigrams[name].cue}</span>`);
  const classes='place'+(dir.length===2?' corner':'')+(practicing&&graded&&name?(correct?' correct':' incorrect'):'');
  return practicing?`<button class="${classes}" data-dir="${dir}" aria-label="${directionNames[dir]}: ${name?displayName(name):'빈칸'}${mark?', '+mark:''}">${content}</button>`:`<div class="${classes}" data-dir="${dir}">${content}</div>`;
 }).join('');
}
function renderBank(){
 byId('bank').innerHTML=bankOrder.map(name=>{
  const used=Object.keys(answers).find(dir=>answers[dir]===name);
  return `<button data-name="${name}" aria-pressed="${selected===name}" class="${used?'used':''}">${trigram(name)}${displayName(name)}<small>${used?directionNames[used]+'에 놓음':'아직 안 놓음'}</small></button>`;
 }).join('');
 byId('selection').textContent=selected?displayName(selected)+' 선택 · 놓을 방위를 눌러줘.':'괘 하나를 골라줘.';
}
function render(){
 const system=baguaData.systems[activeSystem];
 document.querySelectorAll('[data-system]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.system===activeSystem)));
 ['subtitle','chant','subchant','intro','check'].forEach(key=>byId(key).textContent=system[key]);
 byId('corner-story').textContent=system.cornerStory;
 byId('groups').innerHTML=system.groups.map(group=>`<div class="group"><small>${escapeText(group.label)}</small><strong>${escapeText(group.title)}</strong><p>${escapeText(group.text)}</p></div>`).join('');
 byId('study').hidden=practicing;byId('practice').hidden=!practicing;byId('practice-controls').hidden=!practicing;
 byId('bridges-details').hidden=practicing;
 byId('mode').textContent=practicing?'정답·암기 장면 보기':'빈 방위판 채우기';
 renderBoard();renderBank();
}
function clearAnswers(){answers={};selected=null;graded=false;byId('result').textContent='';}
document.querySelectorAll('[data-system]').forEach(button=>button.addEventListener('click',()=>{
 if(activeSystem===button.dataset.system)return;
 activeSystem=button.dataset.system;clearAnswers();render();
}));
byId('orientation').addEventListener('click',()=>{northOnTop=!northOnTop;renderBoard();});
byId('mode').addEventListener('click',()=>{practicing=!practicing;clearAnswers();render();document.querySelector('main').scrollIntoView({block:'start'});});
byId('reset').addEventListener('click',()=>{clearAnswers();renderBoard();renderBank();});
byId('bank').addEventListener('click',event=>{
 const button=event.target.closest('[data-name]');if(!button)return;
 selected=button.dataset.name;renderBank();byId('bank').querySelector('[aria-pressed="true"]').focus({preventScroll:true});
});
byId('board').addEventListener('click',event=>{
 if(!practicing)return;
 const button=event.target.closest('[data-dir]');if(!button)return;
 if(!selected){byId('result').textContent='먼저 괘 하나를 골라줘.';return;}
 for(const dir of Object.keys(answers))if(answers[dir]===selected)delete answers[dir];
 const destination=button.dataset.dir;
 answers[destination]=selected;selected=null;graded=false;byId('result').textContent='';renderBoard();renderBank();
 byId('board').querySelector('[data-dir="'+destination+'"]').focus({preventScroll:true});
});
byId('grade').addEventListener('click',()=>{
 const target=baguaData.systems[activeSystem].positions;
 const filled=Object.keys(answers).length,correct=Object.keys(target).filter(dir=>answers[dir]===target[dir]).length;
 graded=true;renderBoard();
 byId('result').textContent=correct===8?'8 / 8 · 모두 맞았어! 빈칸으로 다시 누르고, 지도를 뒤집어 한 번 더 해 봐.':`${correct} / 8 맞음 · ${8-filled}칸 비어 있음. `+(filled?'표시된 칸을 다시 떠올려 봐.':'먼저 괘를 놓아 봐.');
});
byId('bridges').innerHTML=bankOrder.map(name=>`<p><strong>${baguaData.trigrams[name].icon} ${baguaData.trigrams[name].cue} → ${displayName(name)}</strong><br>${escapeText(baguaData.trigrams[name].bridge)}</p>`).join('');
byId('sources').innerHTML=baguaData.sources.map(source=>`<li><a href="${escapeText(source.url)}" ${source.url.startsWith('https:')?'target="_blank" rel="noopener"':''}>${escapeText(source.title)}</a></li>`).join('');
render();
