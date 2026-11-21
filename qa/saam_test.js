// 舍岩 표 트레이너 시험 — node qa/saam_test.js [port]
//   (저장소 뿌리에서 python3 -m http.server <port> --bind 127.0.0.1 을 먼저 띄운다)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const PORT = +(process.argv[2] || 8765);
const URL0 = `http://127.0.0.1:${PORT}/saam.html`;
const ROOT = path.resolve(__dirname, '..');
const T = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/saam/table.json'), 'utf8'));
const P = T.points;
const OUT = process.env.SHOT_DIR || path.join(ROOT, 'docs/overhaul/saam_shots');
fs.mkdirSync(OUT, { recursive: true });
const results = [];
const ok = (name, cond, extra) => results.push({ name, pass: !!cond, extra: extra || '' });
const ko = hz => P[hz].ko;

async function fresh(browser, opts = {}) {
  const ctx = await browser.newContext({ viewport: opts.viewport || { width: 1200, height: 900 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  if (opts.init) await page.addInitScript(opts.init);
  await page.goto(opts.url || URL0);
  return { ctx, page, errs };
}
const tab = (page, id) => page.click(`#tabs button[data-id="${id}"]`);

(async () => {
  const browser = await chromium.launch();
  let { ctx, page, errs } = await fresh(browser);

  // 1 기본
  ok('탭 12개', (await page.$$('#tabs button')).length === 12);
  ok('안내 화면에 8단계', (await page.$$('ol.stages li')).length === 8);
  await page.screenshot({ path: path.join(OUT, '01_guide.png'), fullPage: true });

  // 2 오행 줄
  await tab(page, 's1');
  await page.fill('#yin', '목화토금수'); await page.fill('#yang', '금수목화토');
  await page.click('#chk');
  ok('오행 줄 정답(한글)', /맞음/.test(await page.textContent('#fb')));
  await tab(page, 's1');
  await page.fill('#yin', '木火土金水'); await page.fill('#yang', '金水火木土');
  await page.click('#chk');
  ok('오행 줄 오답이면 정답 보임', /陽經 金水木火土/.test(await page.textContent('#fb')));

  // 3 오수혈 60 — 두 번 연속 다 채우면 통과, 한 칸 틀리면 연속이 0
  async function fillGrid(wrongOne) {
    await tab(page, 's2');
    const inputs = await page.$$('input[data-hz]');
    for (let i = 0; i < inputs.length; i++) {
      const hz = await inputs[i].getAttribute('data-hz');
      await inputs[i].fill(wrongOne && i === 7 ? '엉터리' : ko(hz));
    }
    await page.click('#chk');
    return page.textContent('#fb');
  }
  ok('격자 60칸', (await (async () => { await tab(page, 's2'); return (await page.$$('input[data-hz]')).length; })()) === 60);
  let fb = await fillGrid(false); ok('격자 첫 판 60/60', /60 \/ 60/.test(fb), fb);
  fb = await fillGrid(true); ok('한 칸 틀리면 연속 0', /59 \/ 60/.test(fb) && /연속 0회/.test(fb), fb);
  await fillGrid(false); fb = await fillGrid(false); ok('두 번 연속 → 통과', /통과/.test(fb), fb);
  await page.screenshot({ path: path.join(OUT, '02_grid.png'), fullPage: true });

  // 4 本穴 경 → 本穴 한 바퀴
  await tab(page, 's3');
  for (let i = 0; i < 10; i++) {
    const q = await page.textContent('.q');
    const m = T.meridians.find(x => q.includes('<b>' + x.hanja) || q.includes(' · ' + x.hanja + '('));
    await page.fill('#ans', ko(m.ben)); await page.click('#chk');
    await page.waitForTimeout(650);
  }
  ok('本穴 경→本穴 한 바퀴 통과', /이 방향 통과/.test(await page.textContent('#main')));
  // 本穴 → 경
  await page.click('#dR');
  for (let i = 0; i < 10; i++) {
    const q = await page.textContent('.q');
    const m = T.meridians.find(x => x.lends && q.includes(P[x.ben].hanja + ' ' + P[x.ben].ko));
    await page.click(`button[data-m="${m.id}"]`);
    await page.waitForTimeout(650);
  }
  ok('本穴 本穴→경 한 바퀴 통과', /이 방향 통과/.test(await page.textContent('#main')));

  // 5 한 칸 풀기 — 짝 안 순서 바꿔도 맞음 · 補瀉 바꾸면 틀림 · 힌트 3단 · 문장 표시
  async function askCell(m, g) {
    await tab(page, 's4');
    await page.selectOption('#sm', m); await page.selectOption('#sg', g); await page.click('#next');
    return T.cells.find(c => c.meridian === m && c.ge === g);
  }
  let c = await askCell('LU', '正格');
  await page.fill('#b1', ko(c.bu.own)); await page.fill('#b2', ko(c.bu.other));
  await page.fill('#x1', ko(c.xie.own)); await page.fill('#x2', ko(c.xie.other));
  await page.click('#chk');
  fb = await page.textContent('#fb');
  ok('肺 正格 짝 안 순서 바꿔도 맞음', /^맞음/.test(fb.trim()), fb.slice(0, 60));
  ok('검산 칸에 내 문장', fb.includes('태백산의 태연이가'));
  ok('문장 소리 조각 칠(mark 넷)', (await page.$$('#fb mark')).length === 4);
  ok('노래 가사 보임', fb.includes('폐 정격, 태백 태연 보, 소부 어제 사'));
  c = await askCell('LU', '勝格');
  await page.fill('#b1', ko(c.xie.other)); await page.fill('#b2', ko(c.xie.own));
  await page.fill('#x1', ko(c.bu.other)); await page.fill('#x2', ko(c.bu.own));
  await page.click('#chk');
  ok('補瀉를 바꾸면 틀림 + 알림', /補와 瀉가 바뀌었다/.test(await page.textContent('#fb')));
  c = await askCell('HT', '正格');
  await page.click('#hint'); await page.click('#hint'); await page.click('#hint');
  const hints = await page.$$eval('.hint', a => a.map(x => x.textContent));
  ok('힌트 3단', hints.length === 3 && /本穴/.test(hints[2]), hints.join(' / ').slice(0, 120));
  await page.fill('#b1', '대돈'); await page.fill('#b2', '少衝'); await page.fill('#x1', '음곡'); await page.fill('#x2', '소해');
  await page.click('#chk');
  ok('한자 입력 · 소해(心) 받음', /^맞음/.test((await page.textContent('#fb')).trim()));
  c = await askCell('SI', '勝格');
  await page.fill('#b1', '통곡'); await page.fill('#b2', '전곡'); await page.fill('#x1', '삼리'); await page.fill('#x2', '소장소해');
  await page.click('#chk');
  ok('줄임 「통곡 · 삼리 · 소장소해」 받음', /^맞음/.test((await page.textContent('#fb')).trim()));
  c = await askCell('ST', '勝格');
  await page.fill('#b1', '임읍'); await page.fill('#b2', '함곡'); await page.fill('#x1', '상구'); await page.fill('#x2', '여태');
  await page.click('#chk');
  fb = await page.textContent('#fb');
  ok('胃 勝格 상구는 틀림(商陽)', !/^맞음/.test(fb.trim()));
  ok('胃 勝格 문장은 상양씨 확정본 + 고침 메모', fb.includes('상양씨는 사퇴시키지 마') && fb.includes('상구씨'));
  await page.screenshot({ path: path.join(OUT, '03_cell.png'), fullPage: true });

  // 6 검산 표
  await tab(page, 's5');
  ok('검산 표 24줄', (await page.$$('button.reveal')).length === 24);
  await page.click('#openAll');
  ok('모두 열기', (await page.$$eval('.ans', a => a.filter(x => !x.hidden).length)) === 24);
  await page.screenshot({ path: path.join(OUT, '04_check.png'), fullPage: true });

  // 7 寒熱格 — 다음 판
  await tab(page, 's6');
  ok('寒熱格은 다음 판 안내', /다음 판/.test(await page.textContent('#main')));

  // 8 전체 빈 표 100%
  await tab(page, 's7'); await page.click('#mF');
  for (const cc of T.cells) {
    for (const k of ['bu', 'xie']) {
      const ins = await page.$$(`input[data-k="${cc.key}"][data-s="${k}"]`);
      await ins[0].fill(ko(cc[k].other)); await ins[1].fill(ko(cc[k].own));
    }
  }
  await page.click('#chk');
  fb = await page.textContent('#fb');
  ok('전체 빈 표 96/96 (100%)', /96\/96 \(100%\)/.test(fb), fb);
  // 거꾸로
  await page.click('#mR');
  const q = await page.textContent('#area .q');
  const rc = T.cells.find(cc => q.includes(P[cc.bu.other].hanja + ' ') && q.includes(P[cc.bu.own].hanja + ' ') && q.includes(P[cc.xie.own].hanja + ' '));
  await page.click(`#area button[data-m="${rc.meridian}"]`); await page.click(`#area button[data-g="${rc.ge}"]`); await page.click('#area #chk');
  ok('거꾸로(혈 넷 → 경 · 격)', /맞음/.test(await page.textContent('#area #fb')));
  await page.screenshot({ path: path.join(OUT, '05_full.png'), fullPage: true });

  // 9 간격 복습 — 오늘 볼 것(틀린 칸) · 세 번 연속이면 빠짐
  const before = await page.evaluate(() => Object.keys(window.__saam.rec().items).filter(k => /^(cell|self|ben):/.test(k) && window.__saam.rec().items[k].due <= new Date().toISOString().slice(0, 10)).length);
  await tab(page, 's8');
  ok('간격 복습에 오늘 볼 것', before > 0 && /남은/.test(await page.textContent('#main')), 'due=' + before);

  // 10 自經 補瀉
  await tab(page, 'self'); await page.click('#tbl');
  ok('自經 補瀉 표 12줄', (await page.$$('#area tbody tr')).length === 12);
  const lu = await page.$eval('#area tbody tr', tr => tr.textContent);
  ok('肺 虛 補 太淵 · 實 瀉 尺澤', lu.includes('太淵') && lu.includes('尺澤'));

  // 11 오답 모음 · 기록 유지
  await tab(page, 'wrong');
  ok('오답 모음에 틀린 칸', (await page.$$('#main tbody tr')).length >= 2);
  await page.reload();
  const kept = await page.evaluate(() => (window.__saam.rec().full || []).length);
  ok('새로 열어도 기록 유지', kept >= 1);
  ok('페이지 오류 없음', errs.length === 0, errs.join(' | '));
  await ctx.close();

  // 12 저장 막힘 → 메모리로 돌고 알림
  ({ ctx, page, errs } = await fresh(browser, { init: () => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } }); } }));
  ok('저장 막힘 알림', await page.isVisible('#storeNotice'));
  await tab(page, 's1'); await page.fill('#yin', '목화토금수'); await page.fill('#yang', '금수목화토'); await page.click('#chk');
  ok('저장 막혀도 동작', /맞음/.test(await page.textContent('#fb')) && errs.length === 0, errs.join(' | '));
  await ctx.close();

  // 13 폭 380px
  ({ ctx, page, errs } = await fresh(browser, { viewport: { width: 380, height: 800 } }));
  await tab(page, 's7'); await page.click('#mF');
  const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok('380px 몸통 가로 넘침 없음(표는 안에서 스크롤)', over <= 1, 'overflow=' + over);
  await page.screenshot({ path: path.join(OUT, '06_mobile_full.png'), fullPage: false });
  await tab(page, 's4');
  await page.screenshot({ path: path.join(OUT, '07_mobile_cell.png'), fullPage: false });
  await ctx.close();

  await browser.close();
  const pass = results.filter(r => r.pass).length;
  results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.name + (r.extra && !r.pass ? '  — ' + r.extra : '')));
  console.log(`\n${pass}/${results.length}`);
  process.exit(pass === results.length ? 0 : 1);
})();
