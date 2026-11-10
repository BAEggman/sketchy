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
// 사전 독음과 다르게 읽는 고유명사·용어(성씨 葉=섭 등) — ②보다 먼저 바꿔 둔다
const PRE = [['葉天士', '섭천사'], ['葉桂', '섭계'], ['戾氣', '려기'], ['沈金鰲', '심금오'], ['沈氏', '심씨'], ['金永碩', '김영석'], ['醫方類聚', '의방유취'], ['鄭禮男', '정예남'], ['角徵宮商羽', '각치궁상우'], ['소리 徵', '소리 치'], ['所惡', '소오'], ['四問便', '사문변'], ['實在易', '실재이'], ['惡濕', '오습'], ['惡燥', '오조'], ['惡熱', '오열'], ['惡風', '오풍'], ['惡寒', '오한'], ['說言乎兌', '열언호태'], ['醋炒則斂', '초초즉렴'], ['人蔘惡萊菔子', '인삼오내복자'], ['生薑惡黃芩', '생강오황금'], ['相惡', '상오'], ['相殺', '상살'], ['丹參', '단삼'], ['玄參', '현삼'], ['沙參', '사삼'], ['苦參', '고삼'], ['人參', '인삼'], ['五參', '오삼'], ['다섯 參', '다섯 삼'], ['杜仲', '두충'], ['黨參', '당삼'], ['善行而數變', '선행이삭변'], ['數變', '삭변'], ['易襲陽位', '이습양위'], ['易襲陰位', '이습음위'], ['易傷陽氣', '이상양기'], ['著痺', '착비'], ['易耗傷津液', '이모상진액'], ['易傷津液', '이상진액'], ['易傷肺', '이상폐'], ['易動血', '이동혈'], ['熱極易生風', '열극이생풍'], ['參附湯', '삼부탕'], ['汗稀而涼', '한희이량'], ['少氣懶言', '소기나언']];
// 한 글자의 다른 음(다음자) — 뜻풀이 「미워할 오(惡)」처럼 사전 첫 음과 다르게 적은 것을 겹쳐 읽지 않게
const ALT = { '惡': ['오', '악'], '說': ['열', '설', '세'], '樂': ['락', '악', '요'], '復': ['복', '부'], '數': ['수', '삭'], '便': ['편', '변'], '易': ['역', '이'], '行': ['행', '항'], '降': ['강', '항'] };
// 두음법칙 때문에 낱말 끝 소리(「신 리」)와 독음(「이」)이 어긋나도 같은 소리로 본다
function sameSound(w, r) {
  if (w.endsWith(r)) return true;
  const c = r.charCodeAt(0) - 0xac00;
  if (c < 0 || c > 11171 || Math.floor(c / 588) !== 11) return false; // 첫소리 ㅇ일 때만
  const rest = c % 588;
  return [5, 2].some(ini => w.endsWith(String.fromCharCode(0xac00 + ini * 588 + rest) + r.slice(1))); // ㄹ·ㄴ
}
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
        if (sameSound(w, r)) return w + p;
        if (h.length === 1 && (ALT[h] || []).some(x => sameSound(w, x))) return w + p; // 다음자: 뜻풀이에 쓴 음을 믿는다(미워할 오(惡))
        return w + ' ' + r + fixParticle(r, p);
      });
      for (const [k, v] of PRE) s = s.split(k).join(v);
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
