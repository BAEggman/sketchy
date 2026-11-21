/* 舍岩鍼法 표 트레이너 (正格 · 勝格) — 계획서 6-4
   정본: src/saam/table.json (make_table.py가 규칙 · 노래 · 사용자 문장 세 갈래로 검산해 만든다)
   기록: localStorage 'sketchy_saam_v1' (막히면 메모리로 돌고 알린다) */
(function () {
  'use strict';
  var T = JSON.parse(document.getElementById('saam-data').textContent);
  var KEY = 'sketchy_saam_v1';
  var INTERVALS = [0, 1, 3, 7, 14];          // 당일 · 1 · 3 · 7 · 14일
  var M = {}; T.meridians.forEach(function (m) { M[m.id] = m; });
  var P = T.points;
  var CELLS = T.cells;
  var CELL = {}; CELLS.forEach(function (c) { CELL[c.key] = c; });
  var LENDERS = T.meridians.filter(function (m) { return m.lends; });

  /* ── 저장 ─────────────────────────────────────── */
  var memOnly = false, rec;
  function blank() { return { v: 1, items: {}, stage: { s1: { best: null, passes: 0 }, s2: { streak: 0, passed: false }, s3: { fwd: false, rev: false }, s7: { fast: {} } }, full: [] }; }
  function load() {
    try { var s = localStorage.getItem(KEY); rec = s ? JSON.parse(s) : blank(); }
    catch (e) { memOnly = true; rec = blank(); }
    if (!rec.stage) rec.stage = blank().stage;
    ['s1', 's2', 's3', 's7'].forEach(function (k) { if (!rec.stage[k]) rec.stage[k] = blank().stage[k]; });
    if (!rec.items) rec.items = {}; if (!rec.full) rec.full = [];
  }
  function save() {
    if (memOnly) return;
    try { localStorage.setItem(KEY, JSON.stringify(rec)); }
    catch (e) { memOnly = true; notice('이 브라우저에서 기록을 저장할 수 없어 이번 창에서만 기억합니다. 「기록」 탭에서 내보내기로 옮길 수 있습니다.'); }
  }
  function notice(msg) { var n = document.getElementById('storeNotice'); n.textContent = msg; n.hidden = false; }

  function today(off) { var d = new Date(); d.setHours(0, 0, 0, 0); if (off) d.setDate(d.getDate() + off); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function item(k) { if (!rec.items[k]) rec.items[k] = { r: 0, w: 0, st: 0, t: [], lv: 0, due: today(), last: null }; return rec.items[k]; }
  var sessionStreak = {};   // 이번 창에서의 연속 정답(세 번이면 오늘은 끝)
  function mark(k, ok, ms) {
    var it = item(k);
    it.last = new Date().toISOString();
    if (ok) {
      it.r++; it.st++; if (ms != null) { it.t.push(Math.round(ms)); if (it.t.length > 10) it.t.shift(); }
      sessionStreak[k] = (sessionStreak[k] || 0) + 1;
      if (sessionStreak[k] === 3) { it.lv = Math.min(it.lv + 1, INTERVALS.length - 1); it.due = today(INTERVALS[it.lv]); }
    } else {
      it.w++; it.st = 0; it.lv = 0; it.due = today(); sessionStreak[k] = 0;
    }
    save();
  }

  /* ── 입력 맞춤 ───────────────────────────────── */
  function clean(s) { return String(s || '').replace(/[\s·・,.()（）]/g, ''); }
  function matches(input, hz) {
    var s = clean(input); if (!s) return false;
    var p = P[hz]; if (!p) return false;
    if (s === p.hanja || s === p.ko) return true;
    return (p.alias || []).indexOf(s) >= 0;
  }
  // 두 입력이 기대한 두 혈과 순서 상관없이 맞는가
  function pairOK(a, b, want) {
    return (matches(a, want[0]) && matches(b, want[1])) || (matches(a, want[1]) && matches(b, want[0]));
  }
  function anyOf(input, list) { for (var i = 0; i < list.length; i++) if (matches(input, list[i])) return list[i]; return null; }
  function label(hz) { var p = P[hz]; var tag = (hz === '少海' ? '(心)' : hz === '小海' ? '(小腸)' : ''); return p.hanja + ' ' + p.ko + tag; }
  function mname(id) { return M[id].hanja; }
  function cellPts(c) { return { bu: [c.bu.other, c.bu.own], xie: [c.xie.other, c.xie.own] }; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (ch) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]; }); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }
  function secs(ms) { return (ms / 1000).toFixed(1) + '초'; }

  /* ── 문장 · 노래 검산 칸 ────────────────────────── */
  function sentenceHTML(c) {
    var s = esc(c.sentence.text);
    Object.keys(c.sentence.hits).forEach(function (hz) {
      var frag = esc(c.sentence.hits[hz]);
      s = s.replace(frag, '<mark title="' + esc(label(hz)) + '">' + frag + '</mark>');
    });
    var note = c.sentence.note ? '<div class="small muted">' + esc(c.sentence.note) + '</div>' : '';
    return '<div class="sent">내 문장: ' + s + '</div>' + note +
      '<div class="small">노래 ' + esc(c.song.id) + ' ' + esc(c.song.title) + ': 「' + esc(c.song.line) + '」 · 도출송 ' + esc(c.song.derive_song) +
      ' (<a href="https://baeggman.github.io/" target="_blank" rel="noopener">앱</a> 「사암 補瀉」 탭)</div>';
  }
  function answerHTML(c) {
    function pr(p, kind) {
      var o = M[p.other_meridian];
      return '<div><b>' + kind + ' ' + p.rel + ' 짝(' + p.el + ')</b>: ' + esc(label(p.other)) + ' <span class="small muted">(' + o.hanja + '의 本穴)</span> + ' +
        esc(label(p.own)) + ' <span class="small muted">(' + M[c.meridian].hanja + '의 ' + p.el + '穴)</span></div>';
    }
    return pr(c.bu, '補') + pr(c.xie, '瀉');
  }

  /* ── 화면 틀 ─────────────────────────────────── */
  var TABS = [
    ['guide', '안내'], ['s1', '1 오행 줄'], ['s2', '2 오수혈 60'], ['s3', '3 本穴'], ['s4', '4 한 칸 풀기'], ['s5', '5 검산'],
    ['s6', '6 寒熱格'], ['s7', '7 섞어 묻기'], ['s8', '8 간격 복습'], ['self', '自經 補瀉'], ['wrong', '오답 모음'], ['log', '기록']
  ];
  var main = document.getElementById('main');
  var cur = null, timers = [];
  function clearTimers() { timers.forEach(clearInterval); timers = []; }
  function go(id) {
    clearTimers(); cur = id;
    Array.prototype.forEach.call(document.querySelectorAll('#tabs button'), function (b) { b.setAttribute('aria-pressed', b.dataset.id === id ? 'true' : 'false'); });
    try { history.replaceState(null, '', '#' + id); } catch (e) { }
    VIEWS[id]();
  }
  function tabs() {
    var nav = document.getElementById('tabs');
    nav.innerHTML = TABS.map(function (t) { return '<button type="button" data-id="' + t[0] + '">' + t[1] + '</button>'; }).join('');
    nav.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) go(b.dataset.id); });
  }
  function panel(html) { main.innerHTML = html; }
  function $(sel) { return main.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(main.querySelectorAll(sel)); }

  /* ── 단계 통과 판정 ───────────────────────────── */
  function cellFastCount(limit) { return CELLS.filter(function (c) { var it = rec.items['cell:' + c.key]; return it && it.t.some(function (ms) { return ms <= limit; }); }).length; }
  function stagePass() {
    var s = rec.stage;
    var noHint = CELLS.filter(function (c) { return (rec.stage.s4nohint || {})[c.key]; }).length;
    var lastFull = rec.full.length ? rec.full[rec.full.length - 1] : null;
    return {
      s1: s.s1.best != null && s.s1.best <= 5000,
      s2: !!s.s2.passed,
      s3: !!(s.s3.fwd && s.s3.rev),
      s4: noHint === CELLS.length, s4n: noHint,
      s7: Object.keys(s.s7.fast || {}).length === CELLS.length, s7n: Object.keys(s.s7.fast || {}).length,
      s8: lastFull ? lastFull : null
    };
  }

  var VIEWS = {};

  VIEWS.guide = function () {
    var p = stagePass();
    function b(ok, txt) { return ok ? '<span class="badge pass">통과</span>' : '<span class="badge">' + (txt || '아직') + '</span>'; }
    var due = dueItems().length;
    panel('<div class="panel"><h2>배우는 차례</h2><ol class="stages">' +
      '<li>오행 줄 둘 — 陰經 井木 → 火土金水, 陽經 井金 → 水木火土 · 열 칸을 5초 안에 ' + b(p.s1) + '</li>' +
      '<li>오수혈 60 격자 — 빈 격자를 두 번 연속 다 채움 ' + b(p.s2) + '</li>' +
      '<li>本穴 10 — 경 → 本穴, 本穴 → 경 양방향 ' + b(p.s3) + '</li>' +
      '<li>규칙 넷으로 한 칸을 풀어 낸다 — 힌트 없이 한 칸 20초 안에 ' + b(p.s4, p.s4n + '/24') + '</li>' +
      '<li>내 문장 24줄 · 노래로 검산</li>' +
      '<li>寒格 · 熱格과 예외 <span class="badge next">다음 판</span></li>' +
      '<li>섞어 묻기 — 한 칸 8초 안에(풀지 않고 바로) · 거꾸로 · 전체 빈 표 ' + b(p.s7, p.s7n + '/24') + '</li>' +
      '<li>간격을 두고 다시(당일 · 1 · 3 · 7 · 14일). 한 번에 세 번 연속 맞을 때까지 · 7일 뒤 전체 빈 표 95% ' +
      (p.s8 ? '<span class="badge">마지막 전체 표 ' + p.s8.date + ' ' + p.s8.pct + '%</span>' : '<span class="badge">기록 없음</span>') + ' · 오늘 볼 것 ' + due + '</li>' +
      '</ol></div>' +
      '<div class="panel"><h2>규칙 넷</h2>' +
      '<ol><li>짝 = <b>남의 경 本穴</b> + <b>제 경의 같은 오행 혈</b>. 陰經은 五臟의 本穴, 陽經은 五腑의 本穴을 빌린다. 心包 · 三焦는 火로 치고 心 · 小腸 줄을 빌린다(勞宮 · 支溝는 빌려주지 않음).</li>' +
      '<li>正格(虛) = 補 <b>母</b> 짝 · 瀉 <b>官</b> 짝</li>' +
      '<li>勝格(實) = 補 <b>官</b> 짝 · 瀉 <b>子</b> 짝 → <b>正格의 瀉 = 勝格의 補</b></li>' +
      '<li>母 = 나를 낳는 오행 · 官 = 나를 이기는 오행 · 子 = 내가 낳는 오행</li></ol>' +
      '<p class="muted">입력은 한글 혈명(또는 한자). 한 짝 안의 두 혈은 순서를 바꿔도 맞다. 補와 瀉를 바꾸면 틀린다. 「삼리 · 통곡 · 임읍 · 규음」 줄임도 받는다. 少海 · 小海는 칸 안에서 하나만 나오므로 「소해」로 쓴다.</p>' +
      '<p class="muted small">출전: ' + esc(T.meta.textbook) + ' · ' + esc(T.meta.sentence_src) + ' · ' + esc(T.meta.next) + '</p></div>');
  };

  /* 1 오행 줄 */
  VIEWS.s1 = function () {
    var t0 = null;
    panel('<div class="panel"><h2>1 오행 줄</h2><p class="muted">井 · 滎 · 兪 · 經 · 合 순서로 오행 다섯 글자를 쓴다(목화토금수 또는 木火土金水). 첫 글자를 치는 순간 시계가 간다.</p>' +
      '<div class="row"><b style="width:4em">陰經</b><input class="pt wide" id="yin" autocomplete="off" aria-label="陰經 오행 다섯"></div>' +
      '<div class="row" style="margin-top:6px"><b style="width:4em">陽經</b><input class="pt wide" id="yang" autocomplete="off" aria-label="陽經 오행 다섯"></div>' +
      '<div class="row" style="margin-top:8px"><button class="primary" id="chk">확인</button><button id="again">다시</button><span id="clock" class="muted"></span></div><div id="fb"></div>' +
      '<p class="muted small">최고 기록: ' + (rec.stage.s1.best != null ? secs(rec.stage.s1.best) : '없음') + '</p></div>');
    var KO2H = { '목': '木', '화': '火', '토': '土', '금': '金', '수': '水' };
    function parse(s) { return clean(s).split('').map(function (ch) { return KO2H[ch] || ch; }).join(''); }
    function start() { if (t0 == null) { t0 = now(); } }
    $('#yin').addEventListener('input', start); $('#yang').addEventListener('input', start);
    $('#again').onclick = function () { VIEWS.s1(); };
    $('#chk').onclick = function () {
      var ms = t0 == null ? null : now() - t0;
      var a = parse($('#yin').value), b = parse($('#yang').value);
      var wa = T.order['陰'].join(''), wb = T.order['陽'].join('');
      var ok = a === wa && b === wb;
      $('#yin').className = 'pt wide ' + (a === wa ? 'ok' : 'no'); $('#yang').className = 'pt wide ' + (b === wb ? 'ok' : 'no');
      mark('row:陰', a === wa, ms); mark('row:陽', b === wb, ms);
      if (ok && ms != null && (rec.stage.s1.best == null || ms < rec.stage.s1.best)) { rec.stage.s1.best = ms; }
      if (ok) rec.stage.s1.passes++;
      save();
      $('#fb').innerHTML = '<div class="fb ' + (ok ? 'good' : 'bad') + '">' + (ok ? '맞음 · ' + (ms != null ? secs(ms) : '') + (ms != null && ms <= 5000 ? ' — 통과 기준(5초) 안' : ' — 5초 안을 노린다') :
        '정답: 陰經 ' + wa + ' / 陽經 ' + wb) + '</div>';
    };
  };

  /* 2 오수혈 60 */
  VIEWS.s2 = function () {
    var rows = T.meridians;
    var mode = 'all';
    function render() {
      var list = mode === 'all' ? rows : [pick(rows)];
      var h = '<div class="panel"><h2>2 오수혈 60 격자</h2><p class="muted">12경 × 井滎兪經合. 빈 격자를 두 번 연속 다 채우면 통과(지금 연속 ' + rec.stage.s2.streak + '회).</p>' +
        '<div class="row"><button id="mAll" aria-pressed="' + (mode === 'all') + '">전체 빈 격자</button><button id="mOne" aria-pressed="' + (mode === 'one') + '">한 줄(무작위 경)</button></div>' +
        '<div class="grid-wrap" style="margin-top:8px"><table><thead><tr><th>經</th>' + T.pos.map(function (p) { return '<th>' + p + '</th>'; }).join('') + '</tr></thead><tbody>';
      list.forEach(function (m) {
        var order = T.order[m.yy];
        h += '<tr><th>' + m.hanja + '<div class="small muted">' + m.yy + ' ' + m.el + '</div></th>' + m.shu.map(function (s, i) {
          return '<td><input class="pt" data-hz="' + s.hanja + '" data-m="' + m.id + '" data-pos="' + s.pos + '" autocomplete="off" aria-label="' + m.hanja + ' ' + s.pos + '"><div class="small muted">' + order[i] + '</div></td>';
        }).join('') + '</tr>';
      });
      h += '</tbody></table></div><div class="row" style="margin-top:8px"><button class="primary" id="chk">확인</button><button id="show">답 보기</button></div><div id="fb"></div></div>';
      panel(h);
      $('#mAll').onclick = function () { mode = 'all'; render(); };
      $('#mOne').onclick = function () { mode = 'one'; render(); };
      $('#show').onclick = function () { $$('input[data-hz]').forEach(function (inp) { inp.placeholder = P[inp.dataset.hz].ko; }); };
      $('#chk').onclick = function () {
        var n = 0, ok = 0;
        $$('input[data-hz]').forEach(function (inp) {
          n++; var good = matches(inp.value, inp.dataset.hz);
          inp.className = 'pt ' + (good ? 'ok' : 'no'); if (good) ok++;
          if (!good) inp.title = '정답 ' + label(inp.dataset.hz);
          mark('shu:' + inp.dataset.m + '.' + inp.dataset.pos, good, null);
        });
        if (mode === 'all') {
          if (ok === n) { rec.stage.s2.streak++; if (rec.stage.s2.streak >= 2) rec.stage.s2.passed = true; } else rec.stage.s2.streak = 0;
          save();
        }
        $('#fb').innerHTML = '<div class="fb ' + (ok === n ? 'good' : 'bad') + '">' + ok + ' / ' + n + (mode === 'all' ? ' · 연속 ' + rec.stage.s2.streak + '회' + (rec.stage.s2.passed ? ' — 통과' : '') : '') + ' · 틀린 칸에 마우스를 올리면 정답</div>';
      };
    }
    render();
  };

  /* 3 本穴 */
  VIEWS.s3 = function () {
    var dir = 'fwd', queue = shuffle(LENDERS), idx = 0, errors = 0, t0 = now();
    function render() {
      var h = '<div class="panel"><h2>3 本穴 10</h2><p class="muted">本穴 = 그 경의 오행과 같은 오행의 오수혈. 남의 경에 빌려주는 것은 열(心包 勞宮 · 三焦 支溝는 빌려주지 않는다). 한 바퀴를 틀림 없이 돌면 그 방향 통과.</p>' +
        '<div class="row"><button id="dF" aria-pressed="' + (dir === 'fwd') + '">경 → 本穴</button><button id="dR" aria-pressed="' + (dir === 'rev') + '">本穴 → 경</button>' +
        '<span class="muted small">경 → 本穴 ' + (rec.stage.s3.fwd ? '통과' : '아직') + ' · 本穴 → 경 ' + (rec.stage.s3.rev ? '통과' : '아직') + '</span></div>';
      if (idx >= queue.length) {
        var clean1 = errors === 0;
        if (clean1) { rec.stage.s3[dir] = true; save(); }
        h += '<div class="fb ' + (clean1 ? 'good' : 'bad') + '">한 바퀴 끝 · 틀림 ' + errors + (clean1 ? ' — 이 방향 통과' : ' — 다시 돌기') + '</div><button class="primary" id="re">다시 한 바퀴</button></div>';
        panel(h); bind(); $('#re').onclick = function () { queue = shuffle(LENDERS); idx = 0; errors = 0; render(); }; return;
      }
      var m = queue[idx];
      if (dir === 'fwd') {
        h += '<p class="q">' + (idx + 1) + '/10 · <b>' + m.hanja + '</b>(' + m.yy + ' ' + m.el + ')의 本穴은?</p><div class="row"><input class="pt" id="ans" autocomplete="off" aria-label="本穴"><button class="primary" id="chk">확인</button></div>';
      } else {
        h += '<p class="q">' + (idx + 1) + '/10 · <b>' + esc(label(m.ben)) + '</b>은 어느 경의 本穴?</p><div class="row">' +
          T.meridians.map(function (x) { return '<button data-m="' + x.id + '">' + x.hanja + '</button>'; }).join('') + '</div>';
      }
      h += '<div id="fb"></div></div>';
      panel(h); bind(); t0 = now();
      function judge(ok) {
        mark('ben:' + m.id, ok, now() - t0); if (!ok) errors++;
        $('#fb').innerHTML = '<div class="fb ' + (ok ? 'good' : 'bad') + '">' + (ok ? '맞음' : '정답: ' + m.hanja + ' — ' + esc(label(m.ben))) + '</div>';
        setTimeout(function () { idx++; render(); }, ok ? 500 : 1600);
      }
      if (dir === 'fwd') {
        $('#ans').focus();
        $('#chk').onclick = function () { judge(matches($('#ans').value, m.ben)); };
        $('#ans').addEventListener('keydown', function (e) { if (e.key === 'Enter') $('#chk').click(); });
      } else {
        $$('button[data-m]').forEach(function (b) { b.onclick = function () { judge(b.dataset.m === m.id); }; });
      }
    }
    function bind() {
      $('#dF').onclick = function () { dir = 'fwd'; queue = shuffle(LENDERS); idx = 0; errors = 0; render(); };
      $('#dR').onclick = function () { dir = 'rev'; queue = shuffle(LENDERS); idx = 0; errors = 0; render(); };
    }
    render();
  };

  /* 한 칸 묻기(4 · 7 · 8에서 같이 씀) */
  function cellQuiz(opts) {
    // opts: {cell, hints:bool, limitMs, onDone(ok, ms, usedHint), title}
    var c = opts.cell, m = M[c.meridian], g = T.ge[c.ge], hint = 0, t0 = now();
    var host = opts.host;
    host.innerHTML = '<p class="q"><b class="big">' + m.hanja + '</b> ' + m.full + ' · <b>' + c.ge + '</b>(' + g.state + ')</p>' +
      '<div class="row"><span class="pair"><b>補</b><input class="pt" id="b1" autocomplete="off" aria-label="補 첫째"><input class="pt" id="b2" autocomplete="off" aria-label="補 둘째"></span>' +
      '<span class="pair"><b>瀉</b><input class="pt" id="x1" autocomplete="off" aria-label="瀉 첫째"><input class="pt" id="x2" autocomplete="off" aria-label="瀉 둘째"></span></div>' +
      '<div class="row" style="margin-top:8px"><button class="primary" id="chk">확인</button>' +
      (opts.hints ? '<button id="hint">힌트</button>' : '') + '<span id="clock" class="muted small"></span></div><div id="hints"></div><div id="fb"></div>';
    var q = function (s) { return host.querySelector(s); };
    q('#b1').focus();
    var clock = setInterval(function () { var el = q('#clock'); if (el) el.textContent = secs(now() - t0) + (opts.limitMs ? ' / 목표 ' + secs(opts.limitMs) : ''); }, 200);
    timers.push(clock);
    if (opts.hints) q('#hint').onclick = function () {
      hint = Math.min(hint + 1, 3);
      var mm = M[c.meridian], buEl = c.bu.el, xieEl = c.xie.el;
      var hs = [
        '① 규칙: ' + c.ge + ' = ' + g.rule,
        '② ' + mm.hanja + '은 ' + mm.yy + '經 · ' + mm.el + ' → 補 ' + g.bu + ' = ' + buEl + ', 瀉 ' + g.xie + ' = ' + xieEl,
        '③ 빌릴 本穴(' + (mm.yy === '陰' ? '五臟' : '五腑') + '): ' + buEl + ' = ' + label(c.bu.other) + ', ' + xieEl + ' = ' + label(c.xie.other) + ' — 나머지 둘은 ' + mm.hanja + '經의 ' + buEl + '穴 · ' + xieEl + '穴'
      ];
      q('#hints').innerHTML = hs.slice(0, hint).map(function (s) { return '<div class="hint">' + esc(s) + '</div>'; }).join('');
    };
    function onKey(e) { if (e.key === 'Enter') q('#chk').click(); }
    ['#b1', '#b2', '#x1', '#x2'].forEach(function (s) { q(s).addEventListener('keydown', onKey); });
    q('#chk').onclick = function () {
      clearInterval(clock);
      var ms = now() - t0, pts = cellPts(c);
      var v = ['#b1', '#b2', '#x1', '#x2'].map(function (s) { return q(s).value; });
      var buOK = pairOK(v[0], v[1], pts.bu), xieOK = pairOK(v[2], v[3], pts.xie);
      var swapped = !buOK && !xieOK && pairOK(v[0], v[1], pts.xie) && pairOK(v[2], v[3], pts.bu);
      ['#b1', '#b2'].forEach(function (s, i) { q(s).className = 'pt ' + (anyOf(v[i], pts.bu) ? 'ok' : 'no'); });
      ['#x1', '#x2'].forEach(function (s, i) { q(s).className = 'pt ' + (anyOf(v[i + 2], pts.xie) ? 'ok' : 'no'); });
      var ok = buOK && xieOK;
      var inTime = !opts.limitMs || ms <= opts.limitMs;
      var msg = ok ? '맞음 · ' + secs(ms) + (opts.limitMs ? (inTime ? ' — 목표 안' : ' — 목표 ' + secs(opts.limitMs) + '를 넘김') : '') + (hint ? ' (힌트 ' + hint + '단)' : '') :
        (swapped ? '補와 瀉가 바뀌었다. ' : '') + '정답은 아래.';
      q('#fb').innerHTML = '<div class="fb ' + (ok ? 'good' : 'bad') + '">' + msg + '<div style="margin-top:6px">' + answerHTML(c) + '</div><div style="margin-top:6px">' + sentenceHTML(c) + '</div></div>';
      mark('cell:' + c.key, ok, ok ? ms : null);
      if (opts.onDone) opts.onDone(ok, ms, hint);
    };
  }

  /* 4 한 칸 풀기 */
  VIEWS.s4 = function () {
    var sel = { m: '', g: '' };
    function render() {
      var noHint = rec.stage.s4nohint || {};
      panel('<div class="panel"><h2>4 한 칸 풀기</h2><p class="muted">경 · 격을 보고 혈 넷을 풀어 낸다. 힌트는 세 단(규칙 → 오행 → 빌릴 本穴). 힌트 없이 20초 안에 맞힌 칸: ' + Object.keys(noHint).length + '/24</p>' +
        '<div class="row"><select id="sm"><option value="">경 무작위</option>' + T.meridians.map(function (m) { return '<option value="' + m.id + '"' + (sel.m === m.id ? ' selected' : '') + '>' + m.hanja + '</option>'; }).join('') + '</select>' +
        '<select id="sg"><option value="">격 무작위</option><option' + (sel.g === '正格' ? ' selected' : '') + '>正格</option><option' + (sel.g === '勝格' ? ' selected' : '') + '>勝格</option></select><button id="next">새 칸</button></div>' +
        '<div id="quiz" style="margin-top:10px"></div></div>');
      $('#sm').onchange = function () { sel.m = this.value; };
      $('#sg').onchange = function () { sel.g = this.value; };
      $('#next').onclick = ask;
      ask();
    }
    function ask() {
      clearTimers();
      var pool = CELLS.filter(function (c) { return (!sel.m || c.meridian === sel.m) && (!sel.g || c.ge === sel.g); });
      var c = pick(pool);
      cellQuiz({
        cell: c, hints: true, limitMs: 20000, host: $('#quiz'), onDone: function (ok, ms, h) {
          if (ok && !h && ms <= 20000) { rec.stage.s4nohint = rec.stage.s4nohint || {}; rec.stage.s4nohint[c.key] = today(); save(); }
        }
      });
    }
    render();
  };

  /* 5 검산 */
  VIEWS.s5 = function () {
    var h = '<div class="panel"><h2>5 내 문장 · 노래로 검산</h2><p class="muted">규칙으로 푼 답(가려 둠)과 내 문장 · 노래 가사를 나란히 본다. 칸을 눌러 답을 연다. 노란 칠은 그 혈을 싣는 소리 조각.</p>' +
      '<div class="row"><button id="openAll">모두 열기</button><button id="closeAll">모두 가리기</button></div>';
    ['正格', '勝格'].forEach(function (ge) {
      h += '<h3 style="margin:12px 0 4px">' + ge + '</h3><div class="grid-wrap"><table><thead><tr><th>經</th><th>풀어 낸 답</th><th class="l">문장 · 노래</th></tr></thead><tbody>';
      CELLS.filter(function (c) { return c.ge === ge; }).forEach(function (c) {
        h += '<tr><th>' + mname(c.meridian) + '</th><td><button class="reveal" data-k="' + c.key + '">답 보기</button><div class="ans" hidden>' + answerHTML(c) + '</div></td><td class="l">' + sentenceHTML(c) + '</td></tr>';
      });
      h += '</tbody></table></div>';
    });
    panel(h + '</div>');
    function set(open) { $$('.ans').forEach(function (d) { d.hidden = !open; }); $$('.reveal').forEach(function (b) { b.hidden = open; }); }
    $$('.reveal').forEach(function (b) { b.onclick = function () { b.hidden = true; b.nextElementSibling.hidden = false; }; });
    $('#openAll').onclick = function () { set(true); }; $('#closeAll').onclick = function () { set(false); };
  };

  VIEWS.s6 = function () {
    panel('<div class="panel"><h2>6 寒格 · 熱格 <span class="badge next">다음 판</span></h2><p>寒格 · 熱格은 규칙으로 자동 생성하지 않는다. 원표를 칸 단위로 옮기고, 규칙과 다른 칸(大腸 · 心 · 三焦의 熱格 瀉, 心↔腎 · 小腸↔膀胱 빌림, 心包 · 三焦 · 膽의 다른 짝)을 「예외」로 따로 묻는다.</p>' +
      '<p class="muted">남은 확인: 大腸 = 陽谷 · 陽谿(사용자 결정, 노래 s07 · s10의 「해계」는 메모), 肝 熱格 瀉(太白 · 太衝)는 원표 판독이 아니라 규칙으로 채운 칸.</p></div>');
  };

  /* 7 섞어 묻기 */
  VIEWS.s7 = function () {
    var mode = 'cell';
    function render() {
      panel('<div class="panel"><h2>7 섞어 묻기</h2><p class="muted">풀지 말고 바로. 한 칸 8초 안에 맞힌 칸: ' + Object.keys(rec.stage.s7.fast || {}).length + '/24</p>' +
        '<div class="row"><button id="mC" aria-pressed="' + (mode === 'cell') + '">임의 칸(8초)</button><button id="mR" aria-pressed="' + (mode === 'rev') + '">거꾸로</button><button id="mF" aria-pressed="' + (mode === 'full') + '">전체 빈 표</button></div>' +
        '<div id="area" style="margin-top:10px"></div></div>');
      $('#mC').onclick = function () { mode = 'cell'; render(); };
      $('#mR').onclick = function () { mode = 'rev'; render(); };
      $('#mF').onclick = function () { mode = 'full'; render(); };
      ({ cell: cellMode, rev: revMode, full: fullMode })[mode]();
    }
    function cellMode() {
      clearTimers();
      var host = $('#area');
      host.innerHTML = '<div id="quiz"></div><button id="next" style="margin-top:8px">다음 칸</button>';
      var c = pick(CELLS);
      cellQuiz({ cell: c, hints: false, limitMs: 8000, host: host.querySelector('#quiz'), onDone: function (ok, ms) { if (ok && ms <= 8000) { rec.stage.s7.fast[c.key] = today(); save(); } } });
      host.querySelector('#next').onclick = cellMode;
    }
    function revMode() {
      var c = pick(CELLS), t0 = now(), pts = cellPts(c), chosen = { m: null, g: null };
      var host = $('#area');
      host.innerHTML = '<p class="q">補 <b>' + esc(label(pts.bu[0])) + ' · ' + esc(label(pts.bu[1])) + '</b> / 瀉 <b>' + esc(label(pts.xie[0])) + ' · ' + esc(label(pts.xie[1])) + '</b> — 어느 경, 어느 격?</p>' +
        '<div class="row">' + T.meridians.map(function (m) { return '<button data-m="' + m.id + '">' + m.hanja + '</button>'; }).join('') + '</div>' +
        '<div class="row" style="margin-top:6px"><button data-g="正格">正格</button><button data-g="勝格">勝格</button><button class="primary" id="chk">확인</button></div><div id="fb"></div><button id="next" style="margin-top:8px">다음</button>';
      Array.prototype.forEach.call(host.querySelectorAll('button[data-m]'), function (b) { b.onclick = function () { chosen.m = b.dataset.m; Array.prototype.forEach.call(host.querySelectorAll('button[data-m]'), function (x) { x.setAttribute('aria-pressed', x === b); }); }; });
      Array.prototype.forEach.call(host.querySelectorAll('button[data-g]'), function (b) { b.onclick = function () { chosen.g = b.dataset.g; Array.prototype.forEach.call(host.querySelectorAll('button[data-g]'), function (x) { x.setAttribute('aria-pressed', x === b); }); }; });
      host.querySelector('#chk').onclick = function () {
        var ok = chosen.m === c.meridian && chosen.g === c.ge;
        mark('rev:' + c.key, ok, now() - t0);
        host.querySelector('#fb').innerHTML = '<div class="fb ' + (ok ? 'good' : 'bad') + '">' + (ok ? '맞음 · ' + secs(now() - t0) : '정답: ' + M[c.meridian].hanja + ' ' + c.ge) + '<div style="margin-top:6px">' + sentenceHTML(c) + '</div></div>';
      };
      host.querySelector('#next').onclick = revMode;
    }
    function fullMode() {
      var host = $('#area');
      var h = '<p class="muted">24칸 × 혈 넷 = 96칸. 칸마다 보 둘 · 사 둘(짝 안 순서 자유).</p><div class="grid-wrap"><table><thead><tr><th>經</th><th>正格 補</th><th>正格 瀉</th><th>勝格 補</th><th>勝格 瀉</th></tr></thead><tbody>';
      T.meridians.forEach(function (m) {
        h += '<tr><th>' + m.hanja + '</th>';
        ['正格', '勝格'].forEach(function (ge) {
          ['bu', 'xie'].forEach(function (k) {
            h += '<td><input class="pt" data-k="' + m.id + '.' + ge + '" data-s="' + k + '" data-i="0" autocomplete="off" aria-label="' + m.hanja + ' ' + ge + ' ' + k + ' 1"><input class="pt" data-k="' + m.id + '.' + ge + '" data-s="' + k + '" data-i="1" autocomplete="off" aria-label="' + m.hanja + ' ' + ge + ' ' + k + ' 2"></td>';
          });
        });
        h += '</tr>';
      });
      h += '</tbody></table></div><div class="row" style="margin-top:8px"><button class="primary" id="chk">채점</button></div><div id="fb"></div>';
      host.innerHTML = h;
      host.querySelector('#chk').onclick = function () {
        var cellsOK = 0, slots = 0, slotsOK = 0;
        CELLS.forEach(function (c) {
          var pts = cellPts(c), good = true;
          ['bu', 'xie'].forEach(function (k) {
            var ins = host.querySelectorAll('input[data-k="' + c.key + '"][data-s="' + k + '"]');
            var a = ins[0].value, b = ins[1].value, ok = pairOK(a, b, pts[k]);
            [a, b].forEach(function (v, i) { slots++; var hit = anyOf(v, pts[k]); if (hit) slotsOK++; ins[i].className = 'pt ' + (hit ? 'ok' : 'no'); if (!hit) ins[i].title = '정답 ' + pts[k].map(label).join(' · '); });
            if (!ok) good = false;
          });
          if (good) cellsOK++;
          mark('cell:' + c.key, good, null);
        });
        var pct = Math.round(slotsOK / slots * 1000) / 10;
        rec.full.push({ date: today(), pct: pct, cells: cellsOK }); save();
        host.querySelector('#fb').innerHTML = '<div class="fb ' + (pct >= 95 ? 'good' : 'bad') + '">혈 ' + slotsOK + '/' + slots + ' (' + pct + '%) · 칸 ' + cellsOK + '/24' + (pct >= 95 ? ' — 95% 넘음' : '') + ' · 틀린 칸에 마우스를 올리면 정답</div>';
      };
    }
    render();
  };

  /* 8 간격 복습 */
  function dueItems() {
    var t = today();
    return Object.keys(rec.items).filter(function (k) { var it = rec.items[k]; return /^(cell|self|ben):/.test(k) && it.due <= t; });
  }
  VIEWS.s8 = function () {
    var queue = shuffle(dueItems()), done = 0;
    function render() {
      clearTimers();
      if (!queue.length) {
        panel('<div class="panel"><h2>8 간격 복습</h2><p>오늘 볼 것이 없다(또는 다 끝냈다). 한 번이라도 푼 칸 · 本穴 · 自經 補瀉가 당일 · 1 · 3 · 7 · 14일 간격으로 돌아온다. 한 번에 세 번 연속 맞아야 다음 간격으로 넘어간다.</p>' +
          '<p class="muted">오늘 끝낸 것 ' + done + '. 7일 뒤에는 「7 섞어 묻기 → 전체 빈 표」로 95%를 확인한다.</p></div>');
        return;
      }
      var k = queue[0], kind = k.split(':')[0], id = k.slice(kind.length + 1);
      panel('<div class="panel"><h2>8 간격 복습</h2><p class="muted">남은 ' + queue.length + ' · 이 항목 연속 ' + (sessionStreak[k] || 0) + '/3</p><div id="area"></div><button id="next" style="margin-top:8px" hidden>다음</button></div>');
      var area = $('#area');
      function after(ok) {
        if (ok && (sessionStreak[k] || 0) >= 3) { queue.shift(); done++; }
        else { queue.shift(); queue.splice(Math.min(3, queue.length), 0, k); }
        $('#next').hidden = false; $('#next').onclick = render;
      }
      if (kind === 'cell') {
        cellQuiz({ cell: CELL[id], hints: false, limitMs: 8000, host: area, onDone: function (ok) { after(ok); } });
      } else if (kind === 'ben') {
        var m = M[id], t0 = now();
        area.innerHTML = '<p class="q"><b>' + m.hanja + '</b>(' + m.yy + ' ' + m.el + ')의 本穴은?</p><div class="row"><input class="pt" id="ans" autocomplete="off" aria-label="本穴"><button class="primary" id="chk">확인</button></div><div id="fb"></div>';
        area.querySelector('#ans').focus();
        area.querySelector('#chk').onclick = function () {
          var ok = matches(area.querySelector('#ans').value, m.ben); mark(k, ok, now() - t0);
          area.querySelector('#fb').innerHTML = '<div class="fb ' + (ok ? 'good' : 'bad') + '">' + (ok ? '맞음' : '정답: ' + esc(label(m.ben))) + '</div>'; after(ok);
        };
      } else {
        selfQuiz(area, id, function (ok) { after(ok); });
      }
    }
    render();
  };

  /* 自經 補瀉 */
  function selfQuiz(host, mid, done) {
    var s = T.self_buxie.filter(function (x) { return x.meridian === mid; })[0], m = M[mid], t0 = now();
    host.innerHTML = '<p class="q"><b>' + m.hanja + '</b>(' + m.yy + ' ' + m.el + ') 自經 補瀉 — 虛하면 補 母穴, 實하면 瀉 子穴</p>' +
      '<div class="row"><span class="pair"><b>補</b><input class="pt" id="sb" autocomplete="off" aria-label="補 母穴"></span><span class="pair"><b>瀉</b><input class="pt" id="sx" autocomplete="off" aria-label="瀉 子穴"></span><button class="primary" id="chk">확인</button></div><div id="fb"></div>';
    host.querySelector('#sb').focus();
    host.querySelector('#chk').onclick = function () {
      var a = matches(host.querySelector('#sb').value, s.bu_mother), b = matches(host.querySelector('#sx').value, s.xie_child), ok = a && b;
      host.querySelector('#sb').className = 'pt ' + (a ? 'ok' : 'no'); host.querySelector('#sx').className = 'pt ' + (b ? 'ok' : 'no');
      mark('self:' + mid, ok, now() - t0);
      host.querySelector('#fb').innerHTML = '<div class="fb ' + (ok ? 'good' : 'bad') + '">' + (ok ? '맞음' : '정답: 補 ' + esc(label(s.bu_mother)) + ' · 瀉 ' + esc(label(s.xie_child))) + '</div>';
      if (done) done(ok);
    };
  }
  VIEWS.self = function () {
    panel('<div class="panel"><h2>自經 補瀉 (넷째 표)</h2><p class="muted">제 경 안에서: 虛 → 母穴을 補, 實 → 子穴을 瀉(難經 六十九難 補母瀉子). 舍岩의 짝 규칙과 갈라 둔다.</p><div class="row"><button id="tbl">표 보기</button><button id="q">한 경 묻기</button></div><div id="area" style="margin-top:8px"></div></div>');
    $('#tbl').onclick = function () {
      $('#area').innerHTML = '<div class="grid-wrap"><table><thead><tr><th>經</th><th>오행</th><th>虛 補 母穴</th><th>實 瀉 子穴</th></tr></thead><tbody>' +
        T.self_buxie.map(function (s) { var m = M[s.meridian]; return '<tr><th>' + m.hanja + '</th><td>' + m.el + '</td><td>' + esc(label(s.bu_mother)) + '</td><td>' + esc(label(s.xie_child)) + '</td></tr>'; }).join('') + '</tbody></table></div>';
    };
    $('#q').onclick = function () { selfQuiz($('#area'), pick(T.meridians).id, null); };
    $('#q').click();
  };

  /* 오답 모음 */
  VIEWS.wrong = function () {
    var ks = Object.keys(rec.items).filter(function (k) { return rec.items[k].w > 0; }).sort(function (a, b) { return rec.items[b].w - rec.items[a].w; });
    var h = '<div class="panel"><h2>오답 모음</h2>';
    if (!ks.length) h += '<p class="muted">아직 틀린 것이 없다.</p>';
    else {
      h += '<div class="grid-wrap"><table><thead><tr><th>항목</th><th>틀림</th><th>맞음</th><th>다음</th><th class="l">답 · 문장</th></tr></thead><tbody>';
      ks.forEach(function (k) {
        var it = rec.items[k], kind = k.split(':')[0], id = k.slice(kind.length + 1), body = '';
        if (kind === 'cell' || kind === 'rev') { var c = CELL[id]; body = answerHTML(c) + sentenceHTML(c); }
        else if (kind === 'ben') body = esc(label(M[id].ben));
        else if (kind === 'shu') { var mm = M[id.split('.')[0]], pos = id.split('.')[1]; body = esc(label(mm.shu.filter(function (s) { return s.pos === pos; })[0].hanja)); }
        else if (kind === 'self') { var s = T.self_buxie.filter(function (x) { return x.meridian === id; })[0]; body = '補 ' + esc(label(s.bu_mother)) + ' · 瀉 ' + esc(label(s.xie_child)); }
        else if (kind === 'row') body = id + '經 ' + T.order[id].join('');
        var title = kind === 'cell' || kind === 'rev' ? M[CELL[id].meridian].hanja + ' ' + CELL[id].ge + (kind === 'rev' ? ' (거꾸로)' : '') : kind + ' ' + id;
        h += '<tr><th>' + esc(title) + '</th><td>' + it.w + '</td><td>' + it.r + '</td><td>' + it.due + '</td><td class="l">' + body + '</td></tr>';
      });
      h += '</tbody></table></div>';
    }
    panel(h + '</div>');
  };

  /* 기록 */
  VIEWS.log = function () {
    var p = stagePass();
    panel('<div class="panel"><h2>기록</h2><p>저장: ' + (memOnly ? '이 창 메모리(저장 막힘)' : '이 브라우저 localStorage') + ' · 항목 ' + Object.keys(rec.items).length + '</p>' +
      '<p>전체 빈 표: ' + (rec.full.length ? rec.full.slice(-8).map(function (f) { return f.date + ' ' + f.pct + '%'; }).join(' · ') : '없음') + '</p>' +
      '<p>4단계 힌트 없이 20초: ' + p.s4n + '/24 · 7단계 8초: ' + p.s7n + '/24</p>' +
      '<div class="row"><button id="exp">내보내기(JSON)</button><label class="small">가져오기 <input type="file" id="imp" accept="application/json"></label><button id="rst">기록 지우기</button></div><div id="fb"></div></div>');
    $('#exp').onclick = function () {
      var blob = new Blob([JSON.stringify(rec, null, 1)], { type: 'application/json' });
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'saam_trainer_' + today() + '.json'; a.click();
    };
    $('#imp').onchange = function () {
      var f = this.files[0]; if (!f) return; var r = new FileReader();
      r.onload = function () { try { var d = JSON.parse(r.result); if (!d.items) throw 0; rec = d; load2(); save(); $('#fb').innerHTML = '<div class="fb good">가져왔다</div>'; } catch (e) { $('#fb').innerHTML = '<div class="fb bad">이 파일은 트레이너 기록이 아니다</div>'; } };
      r.readAsText(f);
    };
    $('#rst').onclick = function () {
      var b = $('#rst');
      if (b.dataset.armed) { rec = blank(); save(); VIEWS.log(); return; }
      b.dataset.armed = '1'; b.textContent = '한 번 더 누르면 모두 지움'; setTimeout(function () { if (b.isConnected) { delete b.dataset.armed; b.textContent = '기록 지우기'; } }, 4000);
    };
  };
  function load2() { if (!rec.stage) rec.stage = blank().stage; if (!rec.full) rec.full = []; }

  load();
  if (memOnly) notice('이 브라우저에서 기록을 저장할 수 없어 이번 창에서만 기억합니다. 「기록」 탭에서 내보내기로 옮길 수 있습니다.');
  tabs();
  var start = (location.hash || '').slice(1);
  go(VIEWS[start] ? start : 'guide');
  window.__saam = { T: T, rec: function () { return rec; }, matches: matches, pairOK: pairOK };
})();
