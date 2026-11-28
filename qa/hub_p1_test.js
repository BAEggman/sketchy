// P1 허브 시험 — 교재 목차 · 썸네일 · 별표 · 다음 그림 자동 · 반복 · 저장 · 폭 380px
//   node qa/hub_p1_test.js [port]   (저장소 뿌리에서 python3 -m http.server <port> 를 먼저 띄운다)
// 시계는 Playwright clock으로 빨리 돌린다. 소리는 끄고(체류 시간) 시험하고, 녹음 · 읽어 주기 실패는 가짜로 만든다.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const PORT = +(process.argv[2] || 8765);
const BASE = `http://127.0.0.1:${PORT}/lessons.html`;
const ROOT = path.resolve(__dirname, '..');
const CUR = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/lessons/curriculum.json'), 'utf8'));
const BOOK = [], SHELF = CUR.shelf.map(x => x.lesson);
CUR.chapters.forEach(c => c.sections.forEach(s => s.items.forEach(it => BOOK.push(it.lesson))));
const OUT = process.env.SHOT_DIR || path.join(ROOT, 'docs/overhaul/p1_shots');
fs.mkdirSync(OUT, { recursive: true });

const results = [];
function ok(name, cond, extra) { results.push({ name, pass: !!cond, extra: extra || '' }); }

async function fresh(browser, opts = {}) {
  const ctx = await browser.newContext({ viewport: opts.viewport || { width: 1280, height: 900 }, deviceScaleFactor: opts.dsf || 1 });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  if (opts.init) await page.addInitScript(opts.init);
  if (opts.clock) await page.clock.install();
  return { ctx, page, errs };
}
const lid = page => new URL(page.url()).searchParams.get('l');
async function tick(page, ms) { await page.clock.runFor(ms); }
// 정거장 자동을 켠다(이미 켜져 있으면 그대로). 11-24부터 다음 그림 자동이 켜져 있으면 과를 열 때 저절로 켜진다.
async function autoOn(page) { if ((await page.getAttribute('[data-act="auto"]', 'aria-pressed')) !== 'true') await page.click('[data-act="auto"]'); }

(async () => {
  const browser = await chromium.launch();
  const quiet = `localStorage.setItem('sketchy_lessons_prefs_v1', JSON.stringify({rate:1.4, voice:false}));`;

  // 1. 목차 · 썸네일 · 한 번씩
  {
    const { ctx, page, errs } = await fresh(browser);
    await page.goto(BASE);
    const rows = await page.$$eval('#toc .ch:not(.shelf) .lrow', els => els.map(e => e.dataset.id));
    ok('목차 줄 수 = 교재에 놓인 과', rows.length === BOOK.length, `${rows.length}/${BOOK.length}`);
    ok('목차 순서 = curriculum.json', JSON.stringify(rows) === JSON.stringify(BOOK));
    const shelf = await page.$$eval('#toc .ch.shelf .lrow', els => els.map(e => e.dataset.id));
    ok('보관함 줄 = 12', shelf.length === SHELF.length, String(shelf.length));
    const all = rows.concat(shelf), uniq = new Set(all);
    const NL = fs.readdirSync(path.join(ROOT, 'src/lessons/l')).filter(f => f.endsWith('.json')).length;
    ok(`${NL}과(src/lessons/l 전부)가 꼭 한 번씩`, all.length === NL && uniq.size === NL, `${all.length}/${uniq.size}`);
    const thumbs = await page.$$eval('#toc .lrow .thumb img', els => els.map(e => e.getAttribute('src')));
    let missing = 0;
    for (const t of thumbs) if (!fs.existsSync(path.join(ROOT, t))) missing++;
    ok(`썸네일 ${NL}/${NL} 파일 있음`, thumbs.length === NL && missing === 0, `${thumbs.length} · 없음 ${missing}`);
    const empties = await page.$$eval('#toc .empty', els => els.length);
    ok('빈 절이 「그림 없음 — 감사 대상」으로 보임', empties >= 10, String(empties));
    ok('페이지 오류 없음', errs.length === 0, errs.join(' | '));
    await page.screenshot({ path: path.join(OUT, '01_toc_1280.png'), fullPage: false });
    await ctx.close();
  }

  // 2. 별표 · 보기 · 추천 순서 · 저장 유지 · 내보내기
  {
    const { ctx, page } = await fresh(browser);
    await page.goto(BASE);
    await page.click('.lrow[data-id="hist-02a"] .stars button[data-star="2"]');
    let st = await page.evaluate(() => JSON.parse(localStorage.getItem('sketchy_hub_v1')).stars);
    ok('별 둘 누르면 2', st['hist-02a'] === 2);
    await page.click('.lrow[data-id="hist-02a"] .stars button[data-star="2"]');
    st = await page.evaluate(() => JSON.parse(localStorage.getItem('sketchy_hub_v1')).stars);
    ok('같은 별 다시 누르면 0', !st['hist-02a']);
    await page.focus('.lrow[data-id="hist-03b"] .stars button[data-star="3"]');
    await page.keyboard.press('Enter');
    await page.click('.lrow[data-id="new-gr-14"] .stars button[data-star="1"]');
    st = await page.evaluate(() => JSON.parse(localStorage.getItem('sketchy_hub_v1')).stars);
    ok('키보드(Enter)로도 별표', st['hist-03b'] === 3);
    await page.reload();
    const kept = await page.$$eval('.lrow[data-id="hist-03b"] .stars button.on', e => e.length);
    ok('새로 열어도 별표 유지', kept === 3);
    await page.click('[data-view="stars"]');
    const sv = await page.$$eval('#toc .lrow', els => els.map(e => e.dataset.id));
    ok('별표만 보기', JSON.stringify(sv) === JSON.stringify(['hist-03b', 'new-gr-14']), sv.join(','));
    await page.click('[data-view="path"]');
    const pv = await page.$$eval('#toc .ch', els => els.map(ch => [...ch.querySelectorAll('.lrow')].map(r => r.dataset.id)));
    let viol = 0;
    const where = {}; pv.forEach((ids, ci) => ids.forEach((id, k) => where[id] = [ci, k]));
    CUR.chapters.forEach(c => c.sections.forEach(s => s.items.forEach(it => (it.prereq || []).forEach(p => {
      if (where[p] && where[p][0] === where[it.lesson][0] && where[p][1] > where[it.lesson][1]) viol++;
    }))));
    ok('추천 학습 순서가 같은 장의 선행을 지킴', viol === 0, `위반 ${viol}`);
    await page.click('[data-view="book"]');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('[data-act="hubexport"]')]);
    const file = await dl.path();
    const exp = JSON.parse(fs.readFileSync(file, 'utf8'));
    ok('별표 · 설정 내보내기', exp.stars['hist-03b'] === 3 && exp.format === 'sketchy_hub_v1');
    await page.evaluate(() => localStorage.removeItem('sketchy_hub_v1'));
    await page.reload();
    await page.setInputFiles('#hubImport', file);
    await page.waitForTimeout(200);
    const imp = await page.evaluate(() => JSON.parse(localStorage.getItem('sketchy_hub_v1') || '{}').stars || {});
    ok('별표 · 설정 가져오기', imp['hist-03b'] === 3 && imp['new-gr-14'] === 1);
    await ctx.close();
  }

  // 3. 기존 주소 · 시험 기록 그대로
  {
    const rec = `localStorage.setItem('sketchy_lessons_v1', JSON.stringify({'hist-02a':[{date:'2026-11-18T00:00:00Z',score:5,total:8,wrong:[2,3,6]}]}));`;
    const { ctx, page, errs } = await fresh(browser, { init: rec });
    await page.goto(BASE + '?l=hist-02a');
    ok('?l=hist-02a 열림', (await page.textContent('#lTitle')).includes('南北朝'));
    await page.goto(BASE + '?l=hist-02a&m=test');
    ok('&m=test 시험 모드', await page.isVisible('#testCard'));
    await page.goto(BASE);
    const t = await page.textContent('.lrow[data-id="hist-02a"] .lmeta');
    ok('목차에 지난 시험 기록', t.includes('5/8'), t);
    ok('오류 없음(주소)', errs.length === 0, errs.join(' | '));
    await ctx.close();
  }

  // 4. 다음 그림 자동 + 반복
  async function autoRun(name, setup, expect) {
    const { ctx, page, errs } = await fresh(browser, { init: quiet, clock: true });
    await page.goto(BASE);
    await setup(page);
    let seen = [lid(page)];
    for (let k = 0; k < 40 && seen.length < expect.length; k++) {
      await tick(page, 15000);
      const cur = lid(page);
      if (cur !== seen[seen.length - 1]) seen.push(cur);
    }
    ok(name, JSON.stringify(seen.slice(0, expect.length)) === JSON.stringify(expect), seen.join(' → '));
    if (errs.length) ok(name + ' 오류 없음', false, errs.join(' | '));
    return { ctx, page };
  }
  const bi = id => BOOK.indexOf(id);
  {   // 끔: 교재 순서 다음 과로, 끝에서 멈춤
    const i = bi('hist-14');
    const r = await autoRun('자동: 반복 끔 → 교재 다음 과', async p => {
      await p.click('[data-act="autonext"]');
      await p.click('.lrow[data-id="hist-14"] a.lt');
      await autoOn(p);
    }, ['hist-14', BOOK[i + 1]]);
    await r.ctx.close();
  }
  {   // 끝에서 멈춤
    const last = BOOK[BOOK.length - 1];
    const { ctx, page } = await fresh(browser, { init: quiet, clock: true });
    await page.goto(BASE);
    await page.click('[data-act="autonext"]');
    await page.click(`.lrow[data-id="${last}"] a.lt`);
    await autoOn(page);
    for (let k = 0; k < 20; k++) await tick(page, 15000);
    ok('자동: 반복 끔 · 재생 목록 끝에서 멈춤', lid(page) === last && (await page.textContent('#autoNote')).includes('끝'), lid(page));
    await ctx.close();
  }
  {   // 이 그림
    const { ctx, page } = await fresh(browser, { init: quiet, clock: true });
    await page.goto(BASE);
    await page.click('[data-act="autonext"]');
    await page.selectOption('#listView select[data-role="repeat"]', 'one');
    await page.click('.lrow[data-id="hist-11"] a.lt');
    await autoOn(page);
    let back = false;
    for (let k = 0; k < 30 && !back; k++) {
      await tick(page, 5000);
      const c = await page.textContent('#tCount');
      if (k > 3 && c.startsWith('1 /')) back = true;
    }
    ok('자동: 이 그림 반복 → 같은 과 처음으로', back && lid(page) === 'hist-11', lid(page));
    await ctx.close();
  }
  {   // 구간 A–B: 끝 → 처음
    const r = await autoRun('자동: 구간 반복 hist-13 → hist-14 → hist-13', async p => {
      await p.click('[data-act="autonext"]');
      await p.selectOption('#listView select[data-role="repeat"]', 'section');
      await p.click('.lrow[data-id="hist-13"] [data-ab="a"]');
      await p.click('.lrow[data-id="hist-14"] [data-ab="b"]');
      await p.click('.lrow[data-id="hist-13"] a.lt');
      await autoOn(p);
    }, ['hist-13', 'hist-14', 'hist-13']);
    await r.ctx.close();
  }
  {   // 전체 + 별표만 재생 목록(시작 순간 고정)
    const r = await autoRun('자동: 별표만 목록 · 전체 반복 → 처음으로 감김', async p => {
      await p.click('.lrow[data-id="yyox-11"] .stars button[data-star="1"]');
      await p.click('.lrow[data-id="yyox-13"] .stars button[data-star="1"]');
      await p.click('[data-act="autonext"]');
      await p.selectOption('#listView select[data-role="repeat"]', 'all');
      await p.click('[data-view="stars"]');
      await p.click('.lrow[data-id="yyox-11"] a.lt');
      await autoOn(p);
    }, ['yyox-11', 'yyox-13', 'yyox-11']);
    const pos = await r.page.textContent('#plPos');
    ok('재생 목록 표시', pos.includes('/ 2') && pos.includes('별표만'), pos);
    await r.ctx.close();
  }
  {   // 자동 넘김 끔 + 반복 전체: 저절로 안 감, 「다음 그림」은 감김
    const { ctx, page } = await fresh(browser, { init: quiet, clock: true });
    await page.goto(BASE);
    await page.selectOption('#listView select[data-role="repeat"]', 'all');
    const last = BOOK[BOOK.length - 1];
    await page.click(`.lrow[data-id="${last}"] a.lt`);
    await autoOn(page);
    for (let k = 0; k < 15; k++) await tick(page, 15000);
    ok('자동 넘김 끔이면 반복이 켜져도 저절로 안 넘어감', lid(page) === last);
    await page.click('[data-act="nextlesson"]');
    ok('「다음 그림」은 반복대로 처음으로 감김', lid(page) === BOOK[0], lid(page));
    await ctx.close();
  }
  {   // 시험 모드에서는 안 넘어감 · 수동 이동은 예약을 지움 · 탭 숨김
    const { ctx, page } = await fresh(browser, { init: quiet, clock: true });
    await page.goto(BASE);
    await page.click('[data-act="autonext"]');
    await page.click('.lrow[data-id="hist-12"] a.lt');
    const n = await page.$$eval('#tDots .dot', e => e.length);
    await page.click(`#tDots .dot[data-i="${n - 1}"]`);   // 마지막 정거장으로
    let armed = false;
    for (let k = 0; k < 200 && !armed; k++) {               // 체류가 끝나 다음 그림 예약(1.5초)이 걸릴 때까지
      await tick(page, 250);
      armed = (await page.textContent('#autoNote')).includes('넘어간다');
    }
    await page.click('[data-act="prev"]');                 // 예약이 걸린 사이 수동 이동
    await tick(page, 5000);
    ok('수동 이동은 걸린 다음 그림 예약을 지움', armed && lid(page) === 'hist-12', `armed=${armed} · ${lid(page)}`);
    await page.goto(BASE + '?l=hist-12&m=test');
    await tick(page, 120000);
    ok('시험 모드에서는 자동으로 안 넘어감', lid(page) === 'hist-12');
    await page.goto(BASE + '?l=hist-12');
    await autoOn(page);
    await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange')); });
    const i0 = await page.textContent('#tCount');
    await tick(page, 120000);
    const i1 = await page.textContent('#tCount');
    ok('탭 숨김은 걸린 타이머를 지움', i0 === i1 && lid(page) === 'hist-12', `${i0} → ${i1}`);
    await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => false }); document.dispatchEvent(new Event('visibilitychange')); });
    ok('돌아오면 「이어서」를 보임', await page.isVisible('[data-act="resume"]'));
    await ctx.close();
  }
  {   // 새로 열면 설정은 되살리되 소리 · 넘김 없음
    const init = quiet + `localStorage.setItem('sketchy_hub_v1', JSON.stringify({autoNext:true, repeat:{mode:'all'}, stars:{}}));`;
    const { ctx, page } = await fresh(browser, { init, clock: true });
    await page.goto(BASE + '?l=hist-01a');
    await tick(page, 300000);
    const pressed = await page.getAttribute('#tourOpts [data-act="autonext"]', 'aria-pressed');
    ok('새로 열면 설정 되살림(다음 그림 자동 켜짐 표시)', pressed === 'true');
    ok('새로 열면 저절로 넘어가지 않음', lid(page) === 'hist-01a' && (await page.textContent('#tCount')).startsWith('1 /'));
    await ctx.close();
  }
  {   // 녹음 실패 → 멈추고 「다시 · 건너뛰기」, 완료로 치지 않음
    const fakeAudio = `window.Audio = function(){ var a = { playbackRate:1, onended:null, onerror:null, pause(){}, load(){}, removeAttribute(){},
      play(){ var self=this; setTimeout(function(){ self.onerror && self.onerror(new Event('error')); }, 10); return Promise.resolve(); } }; return a; };
      localStorage.setItem('sketchy_lessons_prefs_v1', JSON.stringify({rate:1, voice:true}));`;
    const { ctx, page } = await fresh(browser, { init: fakeAudio, clock: true });
    await page.goto(BASE);
    await page.click('[data-act="autonext"]');
    const recId = (JSON.parse(fs.readFileSync(path.join(ROOT, 'audio/narration/manifest.json'), 'utf8')).records);
    const key = Object.keys(recId).find(k => k.endsWith('#1') || k.endsWith('#0'));
    const [rid, rn] = key.split('#');
    await page.click(`.lrow[data-id="${rid}"] a.lt`);
    const idx = await page.evaluate(n => [...document.querySelectorAll('#tDots .dot')].findIndex(d => d.textContent === n || (n === '0' && d.textContent === '틀')), rn);
    await page.click(`#tDots .dot[data-i="${Math.max(0, idx)}"]`);
    await autoOn(page);
    await tick(page, 3000);
    const c0 = await page.textContent('#tCount');
    await tick(page, 60000);
    ok('녹음 실패 → 「다시 · 건너뛰기」', await page.isVisible('#playErr') && await page.isVisible('#playErr [data-act="skip"]'), key);
    ok('녹음 실패를 완료로 치지 않음', (await page.textContent('#tCount')) === c0 && lid(page) === rid);
    await ctx.close();
  }
  {   // 읽어 주기 끝 신호 없음 → 실패
    const mute = `try{ speechSynthesis.speak = function(){}; speechSynthesis.cancel = function(){}; }catch(e){}
      localStorage.setItem('sketchy_lessons_prefs_v1', JSON.stringify({rate:1, voice:true}));`;
    const { ctx, page } = await fresh(browser, { init: mute, clock: true });
    await page.goto(BASE);
    await page.click('[data-act="autonext"]');
    // 녹음이 하나도 없는 과로 시험한다(읽어 주기 길). 2026-11-23: hist-01a에 녹음이 생겨 고정 id를 버림.
    const recLids = new Set(Object.keys(JSON.parse(fs.readFileSync(path.join(ROOT, 'audio/narration/manifest.json'), 'utf8')).records).map(k => k.split('#')[0]));
    const ttsId = BOOK.find(id => !recLids.has(id));
    if (!ttsId) {
      ok('읽어 주기 끝 신호가 없으면 실패로 멈춤', true, '녹음 없는 과가 없어 건너뜀');
    } else {
      await page.click(`.lrow[data-id="${ttsId}"] a.lt`);
      await autoOn(page);
      await tick(page, 200000);
      ok('읽어 주기 끝 신호가 없으면 실패로 멈춤', await page.isVisible('#playErr') && lid(page) === ttsId, `${ttsId} · ` + await page.textContent('#playErrMsg'));
    }
    await ctx.close();
  }

  // 5. 저장 막힘 · 폭 380px
  {
    const block = `Object.defineProperty(window, 'localStorage', { get(){ throw new Error('blocked'); } }); Object.defineProperty(window, 'sessionStorage', { get(){ throw new Error('blocked'); } });`;
    const { ctx, page, errs } = await fresh(browser, { init: block });
    await page.goto(BASE);
    await page.click('.lrow[data-id="hist-02a"] .stars button[data-star="1"]');
    const on = await page.$$eval('.lrow[data-id="hist-02a"] .stars button.on', e => e.length);
    ok('저장이 막혀도 돌아감(메모리)', on === 1 && errs.length === 0, errs.join(' | '));
    ok('저장 막힘을 알림', (await page.textContent('#storeNote')).includes('이 탭에만'));
    await ctx.close();
  }
  {
    const { ctx, page } = await fresh(browser, { viewport: { width: 380, height: 800 }, dsf: 2 });
    await page.goto(BASE);
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    ok('폭 380px 목록 가로 넘침 없음', sw <= 380, String(sw));
    await page.screenshot({ path: path.join(OUT, '02_toc_380.png') });
    await page.click('.lrow[data-id="hist-03b"] a.lt');
    const sw2 = await page.evaluate(() => document.documentElement.scrollWidth);
    ok('폭 380px 과 화면 가로 넘침 없음', sw2 <= 380, String(sw2));
    await page.screenshot({ path: path.join(OUT, '03_lesson_380.png') });
    await ctx.close();
  }
  {
    const { ctx, page } = await fresh(browser, { viewport: { width: 1280, height: 900 }, dsf: 2 });
    await page.goto(BASE);
    await page.click('.lrow[data-id="hist-03b"] .stars button[data-star="3"]');
    await page.selectOption('#listView select[data-role="repeat"]', 'section');
    await page.click('.lrow[data-id="hist-02a"] [data-ab="a"]');
    await page.click('.lrow[data-id="hist-03b"] [data-ab="b"]');
    await page.evaluate(() => document.querySelector('.lrow[data-id="hist-02a"]').scrollIntoView({ block: 'start' }));
    await page.screenshot({ path: path.join(OUT, '04_toc_section_stars.png') });
    await page.click('.lrow[data-id="hist-03b"] a.lt');
    await page.screenshot({ path: path.join(OUT, '05_lesson_1280.png') });
    await page.goto(BASE);
    await page.click('[data-view="path"]');
    await page.evaluate(() => document.querySelector('.ch[data-ch="ch05"]').scrollIntoView({ block: 'start' }));
    await page.screenshot({ path: path.join(OUT, '06_path_ch05.png') });
    await ctx.close();
  }

  {   // 11-24: 다음 그림 자동을 켜면 정거장 자동도 켜지고, 다음 그림에서도 정거장 자동이 이어진다
    const okAudio = `window.Audio = function(src){ var a = { src:src, playbackRate:1, onended:null, onerror:null, pause(){}, load(){}, removeAttribute(){},
      play(){ var self=this; setTimeout(function(){ self.onended && self.onended(new Event('ended')); }, 50); return Promise.resolve(); } }; return a; };
      localStorage.setItem('sketchy_lessons_prefs_v1', JSON.stringify({rate:1, voice:true}));`;
    const { ctx, page } = await fresh(browser, { init: okAudio, clock: true });
    await page.goto(BASE);
    // 녹음이 모두 있는 과가 셋 잇달아 있어야 한다(가짜 Audio로만 넘어감). 11-28 가 선 ①에서 new-gr-14 일부 녹음이 재검토 대기로 빠져 new-jq-06으로 바꿈
    await page.click('.lrow[data-id="new-jq-06"] a.lt');
    await tick(page, 300);
    await page.click('[data-act="autonext"]:visible');
    const on1 = await page.getAttribute('[data-act="auto"]', 'aria-pressed');
    let moved = 0, l0 = lid(page);
    for (let k = 0; k < 60 && moved < 2; k++) { await tick(page, 2000); const l = lid(page); if (l !== l0) { moved++; l0 = l; } }
    ok('다음 그림 자동 → 정거장 자동도 켜지고 그림이 바뀌어도 이어짐', on1 === 'true' && moved >= 2 && (await page.getAttribute('[data-act="auto"]', 'aria-pressed')) === 'true', `넘어간 그림 ${moved}`);
    await ctx.close();
  }
  await browser.close();
  const pass = results.filter(r => r.pass).length;
  results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.name + (r.extra ? '  — ' + r.extra : '')));
  console.log(`\n${pass}/${results.length} pass`);
  fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(results, null, 1));
  process.exit(pass === results.length ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
