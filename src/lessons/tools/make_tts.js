// 과 JSON의 내레이션(say)을 한글 독음 대본(tts)으로 바꿔 넣는다 — 브라우저 음성이 한자를 중국어로 읽어 버리기 때문.
// 독음은 qoaq 인출훈련 앱의 HanjaSong.toReading(두음법칙·다음자 처리)을 그대로 쓴다.
// 사용: node make_tts.js <qoaq 한의학_인출훈련_학습과학.html> <l/과.json> [...]   (jsdom 필요: npm i jsdom)
//   표시용 say는 그대로 두고 tts 칸만 새로 쓴다. 한자가 남거나 독음을 모르는 글자가 있으면 알린다.
const fs = require('fs');
const { JSDOM, VirtualConsole } = require('jsdom');
const [, , qoaq, ...files] = process.argv;
if (!qoaq || !files.length) { console.error('사용: node make_tts.js <qoaq html> <l/과.json> ...'); process.exit(2); }
const dom = new JSDOM(fs.readFileSync(qoaq, 'utf8'), {
  runScripts: 'dangerously', virtualConsole: new VirtualConsole(), url: 'https://baeggman.github.io/qoaq/x.html',
  beforeParse(w) { w.navigator.clipboard = { writeText: () => Promise.resolve() }; w.Element.prototype.scrollIntoView = function () {}; w.scrollTo = function () {}; }
});
const HAN = /[㐀-鿿豈-﫿]/;
function hasBatchim(s) { const c = s.charCodeAt(s.length - 1); return c >= 0xac00 && c <= 0xd7a3 && (c - 0xac00) % 28 !== 0; }
function rieul(s) { const c = s.charCodeAt(s.length - 1); return c >= 0xac00 && c <= 0xd7a3 && (c - 0xac00) % 28 === 8; }
// 앞말에 맞춰 붙인 조사를 새 앞말(독음)에 맞게 바꾼다
function fixParticle(r, p) {
  const b = hasBatchim(r);
  const pairs = [['으로', '로'], ['을', '를'], ['은', '는'], ['과', '와'], ['이다', '다'], ['이', '가'], ['아', '야']];
  for (const [withB, noB] of pairs) {
    for (const cand of [withB, noB]) {
      if (p.startsWith(cand)) {
        let use = b ? withB : noB;
        if (withB === '으로' && rieul(r)) use = '로';
        return use + p.slice(cand.length);
      }
    }
  }
  return p;
}
setTimeout(() => {
  const H = dom.window.HanjaSong;
  const rd = t => H.toReading(t);
  let bad = 0;
  for (const f of files) {
    const L = JSON.parse(fs.readFileSync(f, 'utf8'));
    for (const st of L.stations) {
      let s = st.say || st.fact || '';
      // ① 「한글 낱말(漢字)조사」 꼴의 뜻 풀이 → 「낱말 음조사」 (같은 소리면 겹치지 않게 지움)
      s = s.replace(/([가-힣]+)\(([㐀-鿿豈-﫿]+)\)([가-힣]*)/g, (m, w, h, p) => {
        const r = rd(h).text;
        if (w.endsWith(r)) return w + p;
        return w + ' ' + r + fixParticle(r, p);
      });
      // ② 나머지 한자 → 독음
      const out = rd(s);
      if (out.unknown && out.unknown.length) { bad++; console.log(`${L.id} #${st.n}: 독음 모름 ${out.unknown.join('')}`); }
      let t = out.text;
      // ③ 같은 소리 겹침(「당(당)」) 지움 · 괄호 바로 뒤에 조사가 붙으면 괄호만 풀어 이어 읽기(「왕빙(계현자)이다」 → 「왕빙 계현자이다」)
      t = t.replace(/([가-힣]+)\(\1\)/g, '$1').replace(/\(([^()]*)\)(?=[가-힣])/g, ' $1');
      // ④ 읽기용 다듬기 — 기호를 쉼표·공백으로
      t = t.replace(/[『』「」★]/g, '')
           .replace(/\s*[—→]\s*/g, ', ')
           .replace(/\s*·\s*/g, ', ')
           .replace(/\(\s*/g, ', ').replace(/\s*\)/g, ', ')
           .replace(/\s*~\s*/g, '에서 ')
           .replace(/,\s*([,.!?])/g, '$1').replace(/(,\s*){2,}/g, ', ')
           .replace(/\s+([,.!?])/g, '$1').replace(/\s{2,}/g, ' ').trim();
      if (HAN.test(t)) { bad++; console.log(`${L.id} #${st.n}: 한자가 남음 — ${t}`); }
      st.tts = t;
    }
    fs.writeFileSync(f, JSON.stringify(L, null, 1) + '\n');
    console.log(`${L.id}: tts ${L.stations.length}개`);
  }
  process.exit(bad ? 1 : 0);
}, 1500);
