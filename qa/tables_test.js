// 표에서 연습 시험 — node qa/tables_test.js [port]   (저장소 뿌리에서 python3 -m http.server <port> 를 먼저 띄운다)
// 표 11개가 다 그려지는지 · 가리기 → 열기 → ○/✗ 채점 · 기록 저장 · #주소로 바로 열기 · 재생기 정거장의 「표에서 연습」 잇기 · 폭 380px 가로 넘침.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const PORT = +(process.argv[2] || 8765);
const ROOT = path.resolve(__dirname, '..');
const T = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/tables/tables.json'), 'utf8'));
const results = [];
function ok(name, cond, extra) { results.push({ name, pass: !!cond, extra: extra || '' }); }
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto(`http://127.0.0.1:${PORT}/tables.html#zhuke`);
  ok('표 11개 그림', await page.locator('section.panel').count() === T.tables.length);
  ok('#zhuke 로 主客原絡 표가 보임', await page.locator('#t-zhuke').isVisible());
  ok('다른 과 표는 숨김', !(await page.locator('#t-tiangui').isVisible()));
  const z = page.locator('#t-zhuke');
  await z.getByRole('button', { name: '客 (짝의 絡穴) 가리기' }).click();
  ok('客 열 12칸 가림', await z.locator('td.hid').count() === 12);
  await z.locator('td.hid button.show').first().click();
  ok('연 칸에 偏歷', (await z.locator('tbody tr').first().innerText()).includes('偏歷'));
  await z.getByRole('button', { name: '✗ 틀림' }).click();
  ok('점수 ✗ 1', (await z.locator('p.score').innerText()).includes('✗ 1'));
  const rec = await page.evaluate(() => JSON.parse(localStorage.getItem('sketchy_tables_v1')));
  ok('기록 저장', rec && rec['zhuke:0:2'] && rec['zhuke:0:2'].last === 'no');
  await page.reload();
  await page.locator('#t-zhuke').getByRole('button', { name: '지난번 틀린 칸만' }).click();
  ok('틀린 칸만 다시 가림', await page.locator('#t-zhuke td.hid').count() === 1);
  ok('페이지 오류 없음', !errs.length, errs.join(' | '));
  // 재생기 → 표
  await page.goto(`http://127.0.0.1:${PORT}/lessons.html?l=mer-09`);
  await page.waitForSelector('#tourCard');
  await page.locator('[data-act="next"]').click();
  const link = page.locator('#tTable a');
  ok('재생기 정거장에 표 잇기', await link.isVisible() && (await link.getAttribute('href')) === 'tables.html#zhuke');
  await page.locator('[data-act="prev"]').click();
  ok('틀에는 잇기 없음', !(await page.locator('#tTable').isVisible()));
  // 폭 380px
  const p2 = await (await browser.newContext({ viewport: { width: 380, height: 800 } })).newPage();
  for (const id of ['tiangui', 'paozhi', 'wuyin']) {
    await p2.goto(`http://127.0.0.1:${PORT}/tables.html#${id}`);
    const w = await p2.evaluate(() => document.documentElement.scrollWidth);
    ok(`380px 가로 넘침 없음 (${id})`, w <= 380, 'scrollWidth ' + w);
  }
  await browser.close();
  const bad = results.filter(r => !r.pass);
  results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.name + (r.extra ? ' — ' + r.extra : '')));
  console.log(`${results.length - bad.length}/${results.length} 통과`);
  process.exit(bad.length ? 1 : 0);
})();
