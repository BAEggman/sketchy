// 표에서 연습 — 칸을 가리고 떠올린 뒤 열어 ○ · ✗ 로 스스로 채점한다. 기록은 이 브라우저(localStorage)에만.
(function () {
  'use strict';
  var D = window.TABLES, KEY = 'sketchy_tables_v1';
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { return {}; } }
  var rec = load();
  function save() { try { localStorage.setItem(KEY, JSON.stringify(rec)); return true; } catch (e) { return false; } }
  var state = {};   // 표 id → {hidden: {r:c: true}, open: {r:c: true}, ok, no}

  function lessonsOf() {
    var out = [];
    D.tables.forEach(function (t) { if (out.indexOf(t.lesson) < 0) out.push(t.lesson); });
    return out;
  }
  function cellKey(t, r, c) { return t.id + ':' + r + ':' + c; }

  function render(t) {
    var S = state[t.id] || (state[t.id] = { hidden: {}, open: {}, ok: 0, no: 0 });
    var box = $('t-' + t.id);
    box.textContent = '';
    box.appendChild(el('h2', '', t.title));
    var ctl = el('div', 'row');
    function btn(label, fn) { var b = el('button', '', label); b.type = 'button'; b.onclick = fn; ctl.appendChild(b); return b; }
    btn('모두 보기', function () { S.hidden = {}; S.open = {}; render(t); });
    btn('모두 가리기', function () { hideWhere(t, S, function () { return true; }); });
    t.cols.forEach(function (col, c) {
      if (col.key) return;
      btn(col.h + ' 가리기', function () { hideWhere(t, S, function (r, cc) { return cc === c; }); });
    });
    btn('지난번 틀린 칸만', function () { hideWhere(t, S, function (r, c) { var x = rec[cellKey(t, r, c)]; return x && x.last === 'no'; }); });
    box.appendChild(ctl);
    var score = el('p', 'score muted', '이번 판 ○ ' + S.ok + ' · ✗ ' + S.no);
    box.appendChild(score);
    var wrap = el('div', 'wrap'), tb = el('table');
    var thead = el('thead'), hr = el('tr');
    t.cols.forEach(function (col) { hr.appendChild(el('th', '', col.h)); });
    hr.appendChild(el('th', '', '그림'));
    thead.appendChild(hr); tb.appendChild(thead);
    var tbody = el('tbody');
    t.rows.forEach(function (row, r) {
      var tr = el('tr');
      row.c.forEach(function (txt, c) {
        var k = r + ':' + c, td = el('td', t.cols[c].key ? 'key' : '');
        var x = rec[cellKey(t, r, c)];
        if (x && x.last === 'no') td.classList.add('was-no');
        if (!t.cols[c].key && S.hidden[k] && !S.open[k]) {
          td.classList.add('hid');
          var b = el('button', 'show', '?'); b.type = 'button';
          b.setAttribute('aria-label', '가린 칸 열기 — ' + t.cols[c].h);
          b.onclick = function () { S.open[k] = true; render(t); };
          td.appendChild(b);
        } else {
          td.appendChild(document.createTextNode(txt));
          if (S.hidden[k] && S.open[k] && !(S.done && S.done[k])) {
            var g = el('div', 'grade');
            [['ok', '○ 맞음'], ['no', '✗ 틀림']].forEach(function (p) {
              var gb = el('button', p[0], p[1]); gb.type = 'button';
              gb.onclick = function () { grade(t, S, r, c, p[0]); };
              g.appendChild(gb);
            });
            td.appendChild(g);
          }
        }
        tr.appendChild(td);
      });
      var st = el('td', 'st'), a = el('a', '', t.lesson + ' #' + row.st.join(' · '));
      a.href = 'lessons.html?l=' + encodeURIComponent(t.lesson);
      st.appendChild(a); tr.appendChild(st);
      tbody.appendChild(tr);
    });
    tb.appendChild(tbody); wrap.appendChild(tb); box.appendChild(wrap);
    if (t.notes && t.notes.length) {
      var ul = el('ul', 'notes');
      t.notes.forEach(function (n) { ul.appendChild(el('li', '', n)); });
      box.appendChild(ul);
    }
  }
  function hideWhere(t, S, pred) {
    S.hidden = {}; S.open = {}; S.done = {}; S.ok = 0; S.no = 0;
    t.rows.forEach(function (row, r) {
      row.c.forEach(function (_, c) { if (!t.cols[c].key && pred(r, c)) S.hidden[r + ':' + c] = true; });
    });
    render(t);
  }
  function grade(t, S, r, c, v) {
    var k = r + ':' + c;
    S.done = S.done || {};
    if (S.done[k]) return;
    S.done[k] = v;
    if (v === 'ok') S.ok++; else S.no++;
    var ck = cellKey(t, r, c), x = rec[ck] || { ok: 0, no: 0 };
    x[v]++; x.last = v; x.date = new Date().toISOString().slice(0, 10);
    rec[ck] = x; save();
    render(t);
  }

  function show(lesson) {
    document.querySelectorAll('#tabs button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.l === lesson)); });
    document.querySelectorAll('section.panel').forEach(function (s) { s.hidden = s.dataset.l !== lesson; });
  }
  function init() {
    $('lead').textContent = D.note;
    var tabs = $('tabs'), main = $('main');
    lessonsOf().forEach(function (l) {
      var first = D.tables.filter(function (t) { return t.lesson === l; })[0];
      var b = el('button', '', first.label.replace(/ 표$/, '')); b.type = 'button'; b.dataset.l = l;
      b.onclick = function () { history.replaceState(null, '', '#' + first.id); show(l); };
      tabs.appendChild(b);
    });
    D.tables.forEach(function (t) {
      var s = el('section', 'panel'); s.id = 't-' + t.id; s.dataset.l = t.lesson;
      main.appendChild(s); render(t);
    });
    var want = (location.hash || '').slice(1), hit = D.tables.filter(function (t) { return t.id === want; })[0];
    show(hit ? hit.lesson : D.tables[0].lesson);
    if (hit) { var s = $('t-' + hit.id); if (s.scrollIntoView) s.scrollIntoView(); }
  }
  window.__tables = { data: D, rec: function () { return rec; }, state: state };
  init();
})();
