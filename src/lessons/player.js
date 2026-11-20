// 한의학 Sketchy 과 재생기 — 과 목록 · 투어 · 복습 · 시험. build_player.py가 lessons.html에 끼워 넣는다.
(function () {
  'use strict';

  var LESSONS = JSON.parse(document.getElementById('lessons-data').textContent);
  var byId = Object.create(null);
  LESSONS.forEach(function (L) { byId[L.id] = L; });

  var KEY = 'sketchy_lessons_v1';          // { <과id>: [{date, score, total, wrong:[n…]}] }
  var PKEY = 'sketchy_lessons_prefs_v1';   // { rate, voice } — 이 브라우저만의 편의 설정
  var HKEY = 'sketchy_hub_v1';             // { stars:{id:1~3}, autoNext, repeat:{mode,a,b}, view, closed:{장id:true} }
  var PLKEY = 'sketchy_hub_playlist_v1';   // 탭 하나의 재생 목록(sessionStorage)
  var MODES = ['tour', 'review', 'test'];

  function $(id) { return document.getElementById(id); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  // ---------- 교재 목차 (curriculum.json) ----------
  var CUR = { chapters: [], shelf: [] };
  try { CUR = JSON.parse(document.getElementById('curriculum-data').textContent) || CUR; } catch (e) { /* 목차 없음 → 아래에서 id 순 */ }
  CUR.chapters = CUR.chapters || []; CUR.shelf = CUR.shelf || [];
  var PLACE = Object.create(null);   // id → { ch, sec, it } | { shelf } | { stray }
  var BOOK = [], SHELF = [];
  CUR.chapters.forEach(function (ch) {
    (ch.sections || []).forEach(function (sec) {
      (sec.items || []).forEach(function (it) {
        if (!byId[it.lesson] || PLACE[it.lesson]) return;
        PLACE[it.lesson] = { ch: ch, sec: sec, it: it };
        BOOK.push(it.lesson);
      });
    });
  });
  CUR.shelf.forEach(function (x) {
    if (!byId[x.lesson] || PLACE[x.lesson]) return;
    PLACE[x.lesson] = { shelf: x }; SHELF.push(x.lesson);
  });
  LESSONS.forEach(function (L) { if (!PLACE[L.id]) { PLACE[L.id] = { stray: true }; BOOK.push(L.id); } });
  var BOOKIDX = Object.create(null);
  BOOK.forEach(function (id, i) { BOOKIDX[id] = i; });
  SHELF.forEach(function (id, i) { BOOKIDX[id] = BOOK.length + i; });
  function levelOf(id) { var p = PLACE[id]; return p && p.it && typeof p.it.level === 'number' ? p.it.level : 2; }
  function chIds(ch) {
    var out = [];
    (ch.sections || []).forEach(function (s) { (s.items || []).forEach(function (it) { if (PLACE[it.lesson] && PLACE[it.lesson].it === it) out.push(it.lesson); }); });
    return out;
  }
  // 추천 학습 순서: 장 안에서 같은 장의 선행을 지키며, 남은 것 가운데 level 낮은 것 → 교재 순서
  function pathOrder(ch) {
    var ids = chIds(ch), inCh = Object.create(null), need = Object.create(null), outs = Object.create(null);
    ids.forEach(function (id) { inCh[id] = true; need[id] = 0; outs[id] = []; });
    ids.forEach(function (id) {
      (PLACE[id].it.prereq || []).forEach(function (p) { if (inCh[p]) { need[id]++; outs[p].push(id); } });
    });
    function key(id) { return levelOf(id) * 100000 + BOOKIDX[id]; }
    var ready = ids.filter(function (id) { return !need[id]; }), out = [];
    while (ready.length) {
      ready.sort(function (a, b) { return key(a) - key(b); });
      var n = ready.shift(); out.push(n);
      outs[n].forEach(function (m) { if (--need[m] === 0) ready.push(m); });
    }
    ids.forEach(function (id) { if (out.indexOf(id) < 0) out.push(id); });   // 순환(빌드가 막는다)이면 교재 순서로
    return out;
  }

  // ---------- 허브 설정 (별표 · 자동 넘김 · 반복 · 보기) ----------
  var REPEATS = ['off', 'one', 'section', 'all'], VIEWS = ['book', 'path', 'stars'];
  function normHub(o, keepClosed) {
    var h = { stars: {}, autoNext: false, repeat: { mode: 'off', a: null, b: null }, view: 'book', closed: {} };
    if (!o || typeof o !== 'object') return h;
    if (o.stars && typeof o.stars === 'object') Object.keys(o.stars).forEach(function (k) {
      var v = Math.round(+o.stars[k]);
      if (byId[k] && v >= 1 && v <= 3) h.stars[k] = v;
    });
    h.autoNext = o.autoNext === true;
    var r = o.repeat && typeof o.repeat === 'object' ? o.repeat : {};
    if (REPEATS.indexOf(r.mode) >= 0) h.repeat.mode = r.mode;
    h.repeat.a = byId[r.a] ? r.a : null; h.repeat.b = byId[r.b] ? r.b : null;
    if (VIEWS.indexOf(o.view) >= 0) h.view = o.view;
    var c = keepClosed || o.closed;
    if (c && typeof c === 'object') Object.keys(c).forEach(function (k) { if (c[k]) h.closed[k] = true; });
    return h;
  }
  var hub = normHub(null), hubBroken = false;
  try { hub = normHub(JSON.parse(localStorage.getItem(HKEY) || 'null')); } catch (e) { hubBroken = true; }
  function saveHub() { try { localStorage.setItem(HKEY, JSON.stringify(hub)); } catch (e) { hubBroken = true; } }
  function starOf(id) { return hub.stars[id] || 0; }

  // ---------- 재생 목록 (재생을 시작한 순간의 보기로 고정) ----------
  var PL = { ids: BOOK.slice(), src: 'book' };
  try {
    var savedPl = JSON.parse(sessionStorage.getItem(PLKEY) || 'null');
    if (savedPl && Array.isArray(savedPl.ids)) {
      var okIds = savedPl.ids.filter(function (i) { return byId[i]; });
      if (okIds.length) PL = { ids: okIds, src: String(savedPl.src || 'book') };
    }
  } catch (e) { /* 탭 저장 막힘 → 메모리 */ }
  function setPlaylist(ids, src) {
    PL = { ids: ids.slice(), src: src };
    try { sessionStorage.setItem(PLKEY, JSON.stringify(PL)); } catch (e) { /* 메모리만 */ }
  }
  function viewIds(view) {
    if (view === 'path') { var o = []; CUR.chapters.forEach(function (ch) { o = o.concat(pathOrder(ch)); }); return o; }
    if (view === 'stars') return BOOK.filter(function (id) { return starOf(id) > 0; });
    return BOOK.slice();
  }
  function ensurePlaylistFor(id) {
    if (PL.ids.indexOf(id) >= 0) return;
    if (PLACE[id] && PLACE[id].shelf) setPlaylist(SHELF, 'shelf'); else setPlaylist(BOOK, 'book');
  }
  function rangeIds() {
    var a = hub.repeat.a, b = hub.repeat.b;
    if (!a || !b) return null;
    var base = PLACE[a] && PLACE[a].shelf ? SHELF : BOOK;
    var i = base.indexOf(a), j = base.indexOf(b);
    if (i < 0 || j < 0) return null;
    if (i > j) { var t = i; i = j; j = t; }
    return base.slice(i, j + 1);
  }
  // 이웃 그림: auto=그림이 끝나서 저절로(이 그림 반복이면 제자리), 아니면 사용자가 누른 이전/다음
  function neighbor(dir, auto) {
    if (!S.L) return null;
    var cur = S.L.id, mode = hub.repeat.mode;
    if (mode === 'one' && auto) return cur;
    var list = mode === 'section' ? (rangeIds() || PL.ids) : PL.ids;
    if (!list.length) return null;
    var i = list.indexOf(cur);
    if (i < 0) return mode === 'section' ? list[dir > 0 ? 0 : list.length - 1] : null;
    var j = i + dir;
    if (j >= 0 && j < list.length) return list[j];
    if (mode === 'all' || mode === 'section') return list[(j + list.length) % list.length];
    return null;
  }

  // ---------- 저장소 (막혀 있어도 페이지는 돈다) ----------
  var memResults = null, storeBroken = false;
  function readResults() {
    if (storeBroken && memResults) return memResults;
    try {
      var raw = localStorage.getItem(KEY);
      var o = raw ? JSON.parse(raw) : {};
      if (o && typeof o === 'object' && !Array.isArray(o)) return o;
    } catch (e) { storeBroken = true; }
    return memResults || {};
  }
  function pushResult(id, rec) {
    var all = readResults();
    if (!Array.isArray(all[id])) all[id] = [];
    all[id].push(rec);
    memResults = all;
    try { localStorage.setItem(KEY, JSON.stringify(all)); return true; }
    catch (e) { storeBroken = true; return false; }
  }
  var prefs = { rate: 1, voice: true };
  try {
    var p = JSON.parse(localStorage.getItem(PKEY) || '{}') || {};
    if (typeof p.rate === 'number') prefs.rate = clamp(Math.round(p.rate * 10) / 10, 0.8, 1.4);
    if (p.voice === false) prefs.voice = false;
  } catch (e) { /* 기본값 */ }
  function savePrefs() { try { localStorage.setItem(PKEY, JSON.stringify(prefs)); } catch (e) { /* 무시 */ } }

  function fmtDate(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return String(iso || '');
    function z(n) { return (n < 10 ? '0' : '') + n; }
    return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate());
  }
  function exportHub() {
    var o = { format: HKEY, exported: new Date().toISOString(), stars: hub.stars, autoNext: hub.autoNext, repeat: hub.repeat, view: hub.view };
    var blob = new Blob([JSON.stringify(o, null, 1) + '\n'], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sketchy_hub_v1_' + fmtDate(o.exported).replace(/-/g, '') + '.json';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }
  function exportResults() {
    var all = readResults();
    var blob = new Blob([JSON.stringify(all, null, 1) + '\n'], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sketchy_lessons_v1_' + fmtDate(new Date().toISOString()).replace(/-/g, '') + '.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  // ---------- 정거장 ----------
  function kindOf(st) { return st.kind === 'frame' || st.kind === 'review' ? st.kind : 'station'; }
  function boxesOf(st) {
    var b = st.box;
    if (!Array.isArray(b) || !b.length) return [];
    if (typeof b[0] === 'number') return b.length === 4 ? [b] : [];
    return b.filter(function (x) { return Array.isArray(x) && x.length === 4; });
  }
  function contentIdx(L) {
    var out = [];
    L.stations.forEach(function (st, i) { if (kindOf(st) === 'station' && boxesOf(st).length) out.push(i); });
    return out;
  }

  // ---------- 읽어 주기 (speechSynthesis, ko-KR) ----------
  var gestured = false;
  ['pointerdown', 'keydown'].forEach(function (ev) {
    window.addEventListener(ev, function () { gestured = true; }, true);
  });
  function activated() {
    if (navigator.userActivation) return navigator.userActivation.hasBeenActive || gestured;
    return gestured;
  }
  var tts = {
    ok: 'speechSynthesis' in window && typeof window.SpeechSynthesisUtterance === 'function',
    voice: null, token: 0,
    pick: function () {
      if (!this.ok) return;
      var vs = window.speechSynthesis.getVoices() || [];
      var ko = vs.filter(function (v) { return /^ko([-_]|$)/i.test(v.lang || ''); });
      this.voice = ko.filter(function (v) { return v.localService; })[0] || ko[0] || null;
    },
    speak: function (text, rate, done) {
      this.stop();
      var my = ++this.token, self = this;
      var parts = (String(text).match(/[^.!?。…]+[.!?。…]*\s*/g) || [String(text)])
        .map(function (s) { return s.trim(); }).filter(Boolean);
      var i = 0;
      function next() {
        if (my !== self.token) return;
        if (i >= parts.length) { done(true); return; }
        try {
          var u = new SpeechSynthesisUtterance(parts[i++]);
          u.lang = 'ko-KR';
          if (self.voice) { try { u.voice = self.voice; } catch (e) { /* lang만으로 */ } }
          u.rate = rate;
          u.onend = next;
          u.onerror = function () { if (my === self.token) done(false); };
          window.speechSynthesis.speak(u);
        } catch (e) { done(false); }
      }
      next();
    },
    stop: function () {
      this.token++;
      if (this.ok) { try { window.speechSynthesis.cancel(); } catch (e) { /* 무시 */ } }
    }
  };
  if (tts.ok) {
    tts.pick();
    try { window.speechSynthesis.addEventListener('voiceschanged', function () { tts.pick(); }); } catch (e) { /* 옛 브라우저 */ }
  }

  // ---------- 상태 ----------
  var S = { L: null, mode: 'tour', i: 0, auto: false, heard: -1, speaking: false, sel: -1, test: null, lastId: null };
  var autoTimer = 0, safetyTimer = 0;
  var recordedAudio = null, playbackToken = 0;
  var lessonTimer = 0, lessonGen = 0, paused = false;   // 다음 그림 예약 · 그림을 열 때마다 세대 +1 · 탭 숨김으로 멈춤

  // ---------- 그림 · 덮개 ----------
  var stage = $('stage'), pic = $('pic'), ph = $('ph'), svg = $('dim');
  var SVGNS = 'http://www.w3.org/2000/svg';
  function mountStage(L) {
    stage.style.setProperty('--w', L.w);
    stage.style.setProperty('--h', L.h);
    svg.setAttribute('viewBox', '0 0 ' + L.w + ' ' + L.h);
    ['holes', 'maskBase', 'shade'].forEach(function (id) {
      var el = $(id); el.setAttribute('width', L.w); el.setAttribute('height', L.h);
    });
    ph.textContent = '그림 준비 중 — ' + L.image;
    pic.alt = L.title + ' — ' + (L.place || '');
    pic.onerror = function () { pic.hidden = true; ph.hidden = false; };
    pic.onload = function () { pic.hidden = false; ph.hidden = true; };
    if (L.has_image === false) {
      pic.removeAttribute('src'); pic.hidden = true; ph.hidden = false;
    } else if (pic.getAttribute('src') !== L.image) {
      ph.hidden = true; pic.hidden = false; pic.src = L.image;
    }
    buildHots(L);
  }
  function svgRect(b, cls, extra) {
    var r = document.createElementNS(SVGNS, 'rect');
    r.setAttribute('x', b[0]); r.setAttribute('y', b[1]);
    r.setAttribute('width', b[2]); r.setAttribute('height', b[3]);
    r.setAttribute('rx', 10);
    if (cls) r.setAttribute('class', cls);
    if (extra) Object.keys(extra).forEach(function (k) { r.setAttribute(k, extra[k]); });
    return r;
  }
  function setHoles(boxes) {
    var holeG = $('holeG'), ringG = $('ringG');
    holeG.textContent = '';
    var fresh = ringG.cloneNode(false);           // 새 노드 → 밝힘 애니메이션 다시
    boxes.forEach(function (b) {
      holeG.appendChild(svgRect(b, null, { fill: '#000' }));
      fresh.appendChild(svgRect(b, 'ring-o', { 'vector-effect': 'non-scaling-stroke' }));
      fresh.appendChild(svgRect(b, 'ring', { 'vector-effect': 'non-scaling-stroke' }));
    });
    ringG.parentNode.replaceChild(fresh, ringG);
    stage.classList.toggle('dim', boxes.length > 0);
  }
  function buildHots(L) {
    var hots = $('hots');
    hots.textContent = '';
    var items = [];
    L.stations.forEach(function (st, i) {
      if (kindOf(st) !== 'station') return;
      boxesOf(st).forEach(function (b) { items.push({ i: i, n: st.n, b: b, area: b[2] * b[3] }); });
    });
    items.sort(function (a, b) { return b.area - a.area; });   // 작은 상자가 위에 오도록
    items.forEach(function (it) {
      var el = document.createElement('button');
      el.type = 'button';
      el.className = 'hot';
      el.dataset.i = it.i;
      el.setAttribute('aria-label', '정거장 ' + it.n);
      el.style.left = (it.b[0] / L.w * 100) + '%';
      el.style.top = (it.b[1] / L.h * 100) + '%';
      el.style.width = (it.b[2] / L.w * 100) + '%';
      el.style.height = (it.b[3] / L.h * 100) + '%';
      hots.appendChild(el);
    });
  }

  // ---------- 화면 전환 ----------
  function setText(el, t) { el.textContent = t == null ? '' : String(t); }
  function setHook(el, t) { el.hidden = !t; setText(el.querySelector('span'), t); }
  function setAttrs(el, attrs) {
    if (!el) return;
    el.textContent = '';
    if (!Array.isArray(attrs) || !attrs.length) { el.hidden = true; return; }
    el.hidden = false;
    attrs.forEach(function (a) {
      var li = document.createElement('li');
      var sl = document.createElement('span'); sl.className = 'aslot'; sl.textContent = a.slot || '속성';
      var fc = document.createElement('span'); fc.className = 'afact'; fc.textContent = a.fact || '';
      var ob = document.createElement('span'); ob.className = 'aobj';
      ob.textContent = (a.obj ? '← ' + a.obj : '') + (a.link ? ' (' + a.link + ')' : '');
      li.appendChild(sl); li.appendChild(fc); if (a.obj || a.link) li.appendChild(ob);
      el.appendChild(li);
    });
  }

  // ---------- 목록 = 교재 목차 ----------
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function makeStars(id) {
    var box = el('span', 'stars'), k = starOf(id);
    box.dataset.id = id;
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', '중요도 별표');
    for (var i = 1; i <= 3; i++) {
      var b = el('button', i <= k ? 'on' : '', i <= k ? '★' : '☆');
      b.type = 'button'; b.dataset.star = i; b.dataset.id = id;
      b.setAttribute('aria-label', '별 ' + i + '개' + (k === i ? ' (다시 누르면 0개)' : ''));
      b.setAttribute('aria-pressed', String(i <= k));
      box.appendChild(b);
    }
    return box;
  }
  function refreshStars(id) {
    document.querySelectorAll('.stars[data-id="' + id + '"]').forEach(function (box) {
      box.parentNode.replaceChild(makeStars(id), box);
    });
  }
  function setStar(id, k) {
    if (starOf(id) === k) k = 0;
    if (k) hub.stars[id] = k; else delete hub.stars[id];
    saveHub();
    if (!$('listView').hidden && hub.view === 'stars') renderToc(); else refreshStars(id);
    tocCount();
  }
  function lessonLink(id, cls, ctx, text) {
    var a = el('a', cls, text == null ? id : text);
    a.href = '?l=' + encodeURIComponent(id); a.dataset.go = id; a.dataset.ctx = ctx;
    if (text != null && text !== id) a.title = id;
    return a;
  }
  function lvlBadge(id) {
    var lv = levelOf(id), name = { 0: '사전', 1: '총론', 3: '감별 · 원문' }[lv];
    return name ? el('span', 'lvl l' + lv, name) : null;
  }
  function row(id, ctx, opts) {
    var L = byId[id], P = PLACE[id], it = P.it || {}, li = el('li', 'lrow');
    li.dataset.id = id;
    if (id === S.lastId) li.classList.add('cur');
    if (opts.inR && opts.inR[id]) li.classList.add('inrange');
    var th = lessonLink(id, 'thumb', ctx, '');
    th.setAttribute('aria-label', L.title + ' 그림');
    th.tabIndex = -1;
    if (L.thumb) {
      var img = el('img'); img.src = L.thumb; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async'; img.width = 240; img.height = 135;
      th.appendChild(img);
    }
    li.appendChild(th);
    var m = el('div', 'lmain'), t = lessonLink(id, 'lt', ctx, L.title);
    if (opts.ord) t.insertBefore(el('span', 'ord', opts.ord + '.'), t.firstChild);
    var b = lvlBadge(id); if (b) t.appendChild(b);
    if (L.has_image === false) t.appendChild(el('span', 'lvl', '그림 없음'));
    m.appendChild(t);
    var meta = el('div', 'lmeta');
    meta.appendChild(el('span', '', id + ' · 정거장 ' + L.stations.length));
    var recs = Array.isArray(opts.all[id]) ? opts.all[id] : [];
    if (recs.length) { var last = recs[recs.length - 1]; meta.appendChild(el('span', 'rec', '시험 ' + last.score + '/' + last.total + ' · ' + fmtDate(last.date))); }
    [['prereq', '먼저: '], ['see_also', '같이 보기: ']].forEach(function (pair) {
      var xs = (it[pair[0]] || []).filter(function (x) { return byId[x]; });
      if (!xs.length) return;
      var sp = el('span', '', pair[1]);
      xs.forEach(function (x, k) { if (k) sp.appendChild(document.createTextNode(' · ')); sp.appendChild(lessonLink(x, '', ctx, x)); });
      meta.appendChild(sp);
    });
    if (P.shelf && P.shelf.why) meta.appendChild(el('span', '', P.shelf.why));
    if (it.note) meta.appendChild(el('span', '', '※ ' + it.note));
    m.appendChild(meta);
    li.appendChild(m);
    var side = el('div', 'rside');
    side.appendChild(makeStars(id));
    if (hub.repeat.mode === 'section') {
      var ab = el('span', 'ab');
      [['a', '구간 시작'], ['b', '구간 끝']].forEach(function (x) {
        var bt = el('button', '', x[0].toUpperCase());
        bt.type = 'button'; bt.dataset.ab = x[0]; bt.dataset.id = id;
        bt.setAttribute('aria-label', x[1] + '으로'); bt.setAttribute('aria-pressed', String(hub.repeat[x[0]] === id));
        ab.appendChild(bt);
      });
      side.appendChild(ab);
    }
    li.appendChild(side);
    return li;
  }
  function chStats(ids) {
    var st = 0; ids.forEach(function (id) { if (starOf(id)) st++; });
    return '그림 ' + ids.length + (st ? ' · ★' + st : '');
  }
  function chapterBox(key, titleText, metaText, shut) {   // shut: 기본으로 접힌 상자(보관함)
    var det = el('details', 'ch'); det.dataset.ch = key;
    det.open = shut ? !!hub.closed[key + ':open'] : !hub.closed[key];
    var sum = el('summary');
    sum.appendChild(el('span', 'ch-t', titleText));
    sum.appendChild(el('span', 'ch-m', metaText));
    det.appendChild(sum);
    det.addEventListener('toggle', function () {
      if (shut) { if (det.open) hub.closed[key + ':open'] = true; else delete hub.closed[key + ':open']; }
      else if (det.open) delete hub.closed[key]; else hub.closed[key] = true;
      saveHub();
    });
    var body = el('div', 'secs'); det.appendChild(body);
    return { det: det, body: body };
  }
  function renderToc() {
    var root = $('toc'), view = hub.view, all = readResults();
    var range = hub.repeat.mode === 'section' ? rangeIds() : null, inR = Object.create(null);
    (range || []).forEach(function (id) { inR[id] = true; });
    var opts = { all: all, inR: inR };
    root.textContent = '';
    document.querySelectorAll('[data-view]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.view === view)); });
    var shown = 0;
    CUR.chapters.forEach(function (ch) {
      var ids = chIds(ch);
      if (view === 'stars') ids = ids.filter(function (id) { return starOf(id) > 0; });
      if (view === 'stars' && !ids.length) return;
      var C = chapterBox(ch.id, ch.title, (ch.page ? 'p.' + ch.page + ' · ' : '') + chStats(chIds(ch)));
      if (view === 'path') {
        var ul = el('ul', 'rows');
        pathOrder(ch).forEach(function (id, k) { ul.appendChild(row(id, 'path', { all: all, inR: inR, ord: k + 1 })); shown++; });
        if (!ul.children.length) C.body.appendChild(el('p', 'empty', '그림 없음 — 감사 대상'));
        else C.body.appendChild(ul);
      } else {
        (ch.sections || []).forEach(function (sec) {
          var its = (sec.items || []).filter(function (it) { return PLACE[it.lesson] && PLACE[it.lesson].it === it; });
          if (view === 'stars') its = its.filter(function (it) { return starOf(it.lesson) > 0; });
          if (view === 'stars' && !its.length) return;
          var box = el('section', 'sec'), h = el('div', 'sec-h');
          var lone = ch.sections.length === 1 && !/^제\s*\d+\s*절/.test(sec.title);   // 절이 하나뿐이고 장 이름과 같으면 제목을 거듭 쓰지 않는다
          if (!lone) {
            h.appendChild(el('h3', 'sec-t', sec.title));
            h.appendChild(el('span', 'sec-m', (sec.page ? 'p.' + sec.page + ' · ' : '') + '그림 ' + its.length));
            box.appendChild(h);
          }
          if (sec.note) box.appendChild(el('p', 'sec-note', sec.note));
          if (sec.gap && view === 'book') box.appendChild(el('p', 'gap', '빈 곳(예비 판정): ' + sec.gap));
          if (!its.length) { box.appendChild(el('p', 'empty', '그림 없음 — 감사 대상')); C.body.appendChild(box); return; }
          var ul = el('ul', 'rows'), lastSub = null;
          its.forEach(function (it) {
            if (it.sub && it.sub !== lastSub) { var sh = el('li', 'sub', it.sub); sh.setAttribute('role', 'presentation'); ul.appendChild(sh); }
            lastSub = it.sub || null;
            ul.appendChild(row(it.lesson, view, opts)); shown++;
          });
          box.appendChild(ul);
          C.body.appendChild(box);
        });
      }
      root.appendChild(C.det);
    });
    if (view === 'stars' && !shown) root.appendChild(el('p', 'empty', '별표한 그림이 없다. 목차의 ☆을 눌러 표시한다.'));
    if (SHELF.length && view !== 'stars') {
      var B = chapterBox('shelf', '보관함 — 내린 그림', chStats(SHELF), true);
      B.det.classList.add('shelf');
      var ul2 = el('ul', 'rows');
      SHELF.forEach(function (id) { ul2.appendChild(row(id, 'shelf', opts)); });
      B.body.appendChild(ul2);
      root.appendChild(B.det);
    } else if (SHELF.length) {
      var sIds = SHELF.filter(function (id) { return starOf(id) > 0; });
      if (sIds.length) {
        var B2 = chapterBox('shelf', '보관함 — 별표한 것', chStats(sIds)), ul3 = el('ul', 'rows');
        sIds.forEach(function (id) { ul3.appendChild(row(id, 'shelf', opts)); });
        B2.body.appendChild(ul3); root.appendChild(B2.det);
      }
    }
    tocCount();
  }
  function tocCount() {
    var n = Object.keys(hub.stars).length;
    setText($('tocCount'), '목차 ' + BOOK.length + '과 · 보관함 ' + SHELF.length + ' · 별표 ' + n);
  }
  function syncHubControls() {
    document.querySelectorAll('[data-act="autonext"]').forEach(function (b) { b.setAttribute('aria-pressed', String(hub.autoNext)); });
    document.querySelectorAll('select[data-role="repeat"]').forEach(function (sel) { sel.value = hub.repeat.mode; });
    var r = rangeIds();
    document.querySelectorAll('[data-role="rangenote"]').forEach(function (n) {
      n.hidden = hub.repeat.mode !== 'section';
      n.textContent = '';
      if (hub.repeat.mode !== 'section') return;
      if (!r) { n.textContent = '구간: 목차 줄 오른쪽의 A(시작) · B(끝)로 고른다'; return; }
      n.appendChild(document.createTextNode('구간: '));
      n.appendChild(el('b', '', hub.repeat.a)); n.appendChild(document.createTextNode(' → '));
      n.appendChild(el('b', '', hub.repeat.b)); n.appendChild(document.createTextNode(' (' + r.length + '개)'));
    });
  }

  function showList(missing) {
    stopAll(); setAuto(false); clearTimeout(lessonTimer); lessonGen++; hideErr();
    if (S.L) S.lastId = S.L.id;
    S.L = null;
    $('lessonView').hidden = true; $('listView').hidden = false; $('homeLink').hidden = true;
    document.title = '한의학 Sketchy 과 — 교재 목차';
    var note = $('listNotice');
    note.hidden = !missing;
    if (missing) note.textContent = '과 「' + missing + '」를 찾지 못했다. 아래 목차에서 고르세요.';
    syncHubControls();
    renderToc();
    var msgs = [];
    if (storeBroken) msgs.push('브라우저 저장소가 막혀 시험 기록은 이 탭에만 남는다.');
    if (hubBroken) msgs.push('별표 · 설정도 이 탭에만 남는다 — 「별표 · 설정 내보내기」로 보관하세요.');
    $('storeNote').textContent = msgs.join(' ');
    if (S.lastId) {
      var cur = document.querySelector('.lrow[data-id="' + S.lastId + '"]');
      if (cur && cur.scrollIntoView) { try { cur.scrollIntoView({ block: 'center' }); } catch (e) { cur.scrollIntoView(); } }
    }
  }

  function renderPlNav() {
    var L = S.L; if (!L) return;
    var pos = PL.ids.indexOf(L.id), src = { book: '교재 순서', path: '추천 학습 순서', stars: '별표만', shelf: '보관함' }[PL.src] || PL.src;
    setText($('plPos'), pos < 0 ? '재생 목록 밖' : '재생 목록 ' + (pos + 1) + ' / ' + PL.ids.length + ' · ' + src);
    var holder = $('lessonStars');
    holder.textContent = ''; holder.appendChild(makeStars(L.id));
    document.querySelector('[data-act="prevlesson"]').disabled = !neighbor(-1, false);
    document.querySelector('[data-act="nextlesson"]').disabled = !neighbor(1, false);
    var P = PLACE[L.id], tp = $('lToc');
    tp.textContent = '';
    if (P && P.ch) tp.appendChild(document.createTextNode(P.ch.title + ' › ' + P.sec.title + (P.it.sub ? ' › ' + P.it.sub : '')));
    else if (P && P.shelf) tp.appendChild(document.createTextNode('보관함 — ' + (P.shelf.why || '')));
    var pre = P && P.it ? (P.it.prereq || []).filter(function (x) { return byId[x]; }) : [];
    if (pre.length) {
      tp.appendChild(document.createTextNode(' · 먼저: '));
      pre.forEach(function (x, k) { if (k) tp.appendChild(document.createTextNode(' · ')); tp.appendChild(lessonLink(x, '', 'lesson', x)); });
    }
    syncHubControls();
  }

  function openLesson(id, mode, keepAuto) {
    var L = byId[id];
    if (S.L !== L) {
      var carry = keepAuto && S.auto;
      stopAll(); setAuto(false); clearTimeout(lessonTimer); lessonGen++; paused = false; hideErr();
      S.L = L; S.i = 0; S.sel = -1; S.heard = -1; S.lastId = id; mountStage(L);
      if (carry) markAuto(true);
      ensurePlaylistFor(id);
    }
    $('listView').hidden = true; $('lessonView').hidden = false; $('homeLink').hidden = false;
    setText($('lTitle'), L.title);
    setText($('lPlace'), L.place ? '장소 · ' + L.place : '');
    document.title = L.title + ' — Sketchy 과';
    buildDots(L);
    renderPlNav();
    setMode(mode, true, keepAuto);
  }
  function goLesson(id, keepAuto) {
    if (!id || !byId[id]) return;
    clearTimeout(lessonTimer);
    if (S.L && S.L.id === id) {                       // 이 그림 반복 → 같은 과를 처음부터
      var carry = keepAuto && S.auto;
      stopAll(); lessonGen++; paused = false; hideErr(); S.heard = -1; S.i = 0;
      if (S.mode !== 'tour') { setMode('tour', false, keepAuto); return; }
      if (carry) markAuto(true);
      goTour(0); return;
    }
    try { history.pushState(null, '', urlFor(id, 'tour')); }
    catch (e) { location.href = urlFor(id, 'tour'); return; }
    openLesson(id, 'tour', keepAuto);
  }
  function scheduleNextLesson() {
    clearTimeout(lessonTimer);
    if (!hub.autoNext || S.mode !== 'tour' || paused || !S.L) return;
    var id = neighbor(1, true);
    if (!id) { setAuto(false); note('재생 목록 끝 — 반복이 꺼져 있어 멈췄다.'); return; }
    var gen = lessonGen;
    note('다음 그림으로 넘어간다 — ' + byId[id].title);
    lessonTimer = setTimeout(function () {
      lessonTimer = 0;
      if (gen !== lessonGen || !hub.autoNext || S.mode !== 'tour' || paused || document.hidden) return;
      goLesson(id, true);
    }, 1500);
  }
  function note(t) { var n = $('autoNote'); n.hidden = !t; setText(n, t || ''); }
  function showErr(msg, kind) {
    var bar = $('playErr');
    setText($('playErrMsg'), msg);
    bar.querySelector('[data-act="replay"]').hidden = kind === 'resume';
    bar.querySelector('[data-act="skip"]').hidden = kind === 'resume';
    bar.querySelector('[data-act="resume"]').hidden = kind !== 'resume';
    bar.hidden = false;
  }
  function hideErr() { $('playErr').hidden = true; note(''); }

  function setMode(mode, fromRoute, keepAuto) {
    if (MODES.indexOf(mode) < 0) mode = 'tour';
    var carry = keepAuto && S.auto && mode === 'tour';
    stopAll(); setAuto(false); clearTimeout(lessonTimer); hideErr();
    if (carry) markAuto(true);
    S.mode = mode;
    document.querySelectorAll('.modes button[data-mode]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.mode === mode));
    });
    $('tourCtrl').hidden = $('tourCard').hidden = $('tourOpts').hidden = mode !== 'tour';
    $('reviewCtrl').hidden = $('reviewCard').hidden = mode !== 'review';
    $('testCtrl').hidden = $('testCard').hidden = mode !== 'test';
    $('hots').hidden = mode !== 'review';
    if (!fromRoute) replaceUrl(S.L.id, mode);
    if (mode === 'tour') goTour(S.i);
    else if (mode === 'review') { setHoles([]); selectReview(S.sel); }
    else startTest();
  }

  // ---------- 투어 ----------
  function buildDots(L) {
    var box = $('tDots');
    box.textContent = '';
    L.stations.forEach(function (st, i) {
      var k = kindOf(st), d = document.createElement('button');
      d.type = 'button'; d.className = 'dot ' + k; d.dataset.act = 'goto'; d.dataset.i = i;
      d.textContent = k === 'frame' ? '틀' : k === 'review' ? '↺' : st.n;
      d.setAttribute('aria-label', (k === 'frame' ? '틀' : k === 'review' ? '되짚기' : '정거장 ' + st.n) + (st.obj ? ' — ' + st.obj : ''));
      box.appendChild(d);
    });
  }
  function renderTour() {
    var L = S.L, st = L.stations[S.i], k = kindOf(st);
    setHoles(k === 'frame' ? [] : boxesOf(st));
    var bd = $('tBadge');
    bd.className = 'badge ' + k;
    bd.textContent = k === 'frame' ? '틀' : k === 'review' ? '되짚기' : '정거장 ' + st.n;
    var obj = k === 'frame' ? (L.place || st.obj) : st.obj;
    setText($('tObj'), obj === bd.textContent ? '' : obj);    // 「되짚기 되짚기」 겹침 피하기
    setText($('tFact'), st.fact);
    setHook($('tHook'), st.hook);
    setAttrs($('tAttrs'), st.attrs);
    setText($('tSay'), st.say);
    var src = $('tSrc'), cards = Array.isArray(st.src) ? st.src : [];
    src.hidden = !cards.length; src.textContent = cards.length ? '카드 ' + cards.join(' · ') : '';
    setText($('tCount'), (S.i + 1) + ' / ' + L.stations.length);
    document.querySelector('[data-act="prev"]').disabled = S.i === 0;
    document.querySelector('[data-act="next"]').disabled = S.i === L.stations.length - 1;
    document.querySelectorAll('#tDots .dot').forEach(function (d) {
      d.setAttribute('aria-current', String(+d.dataset.i === S.i));
    });
  }
  function goTour(i) {
    clearTimeout(lessonTimer);
    S.i = clamp(i, 0, S.L.stations.length - 1);
    renderTour();
    playStation(false);
  }
  function estimateMs(text) { return Math.max(4000, String(text || '').length * 95 / prefs.rate); }
  function clearTimers() { clearTimeout(autoTimer); clearTimeout(safetyTimer); }
  function setSpeaking(on) {
    S.speaking = on;
    setText($('replayBtn'), on ? '읽기 멈춤' : '다시 듣기');
  }
  function stopAll() {
    playbackToken++;
    clearTimers(); tts.stop();
    if (recordedAudio) {
      recordedAudio.onended = recordedAudio.onerror = null;
      recordedAudio.pause(); recordedAudio.removeAttribute('src'); recordedAudio.load();
      recordedAudio = null;
    }
    setSpeaking(false);
  }
  function afterStation() {
    clearTimers();
    if (S.mode !== 'tour' || !S.L || paused) return;
    if (S.i >= S.L.stations.length - 1) {          // 되짚기까지 끝 → 다음 그림(켜져 있을 때만)
      if (hub.autoNext) { scheduleNextLesson(); return; }
      if (S.auto) setAuto(false);
      return;
    }
    if (!S.auto) return;
    autoTimer = setTimeout(function () { goTour(S.i + 1); }, 900);
  }
  function playStation(force) {
    stopAll(); hideErr();
    if (S.mode !== 'tour') return;
    var st = S.L.stations[S.i];
    var chain = S.auto || (hub.autoNext && S.i >= S.L.stations.length - 1);   // 이 정거장이 끝나면 저절로 넘어가야 하나
    // 읽어 주기는 한글 독음 대본(tts)을 쓴다 — 브라우저 음성이 한자를 중국어로 읽기 때문. 화면에는 한자가 든 say가 그대로 보인다.
    var text = st.recording ? st.recording.text : (st.tts || st.say || st.fact || ''), at = S.i;
    var token = playbackToken;
    if (st.recording && (prefs.voice || force) && activated() && typeof Audio !== 'undefined') {
      var audio = recordedAudio = new Audio(st.recording.src);
      audio.playbackRate = prefs.rate;
      setSpeaking(true);
      audio.onended = function () {
        if (token !== playbackToken) return;
        S.heard = at; stopAll(); afterStation();
      };
      function failed() {
        if (token !== playbackToken) return;
        var was = S.auto || hub.autoNext;
        stopAll(); setAuto(false); clearTimeout(lessonTimer);
        showErr('녹음을 재생하지 못했다.' + (was ? ' 자동 넘김을 멈췄다.' : ''));
      }
      audio.onerror = failed;
      try { var playing = audio.play(); if (playing && playing.catch) playing.catch(failed); }
      catch (e) { failed(); }
      return; // WAV는 추정 타이머 대신 실제 ended 이벤트로 다음 구간에 이동한다.
    }
    if (tts.ok && (prefs.voice || force) && activated() && text) {
      setSpeaking(true);
      tts.speak(text, prefs.rate, function (ok) {
        if (token !== playbackToken) return;
        clearTimers(); setSpeaking(false);
        if (ok) { S.heard = at; afterStation(); }
        else { var was = S.auto || hub.autoNext; setAuto(false); clearTimeout(lessonTimer); showErr('읽어 주기가 실패했다.' + (was ? ' 자동 넘김을 멈췄다.' : '')); }
      });
      // 끝 신호가 오지 않으면 실패로 친다(완료로 치지 않는다). 자동 넘김을 나중에 켜도 걸리도록 늘 건다.
      safetyTimer = setTimeout(function () {
        if (token !== playbackToken) return;
        var wanted = S.auto || (hub.autoNext && S.i >= S.L.stations.length - 1);
        stopAll();
        if (wanted) { setAuto(false); clearTimeout(lessonTimer); showErr('읽어 주기가 끝나지 않았다. 자동 넘김을 멈췄다.'); }
      }, estimateMs(text) * 2 + 4000);
    } else if (chain) {                               // 소리 없이: 글자 수로 잡은 체류 시간 뒤
      var shown = (st.fact || '') + (st.hook || '') + (st.say || '');
      autoTimer = setTimeout(afterStation, estimateMs(shown));
    }
  }
  function markAuto(on) {
    S.auto = !!on;
    var b = document.querySelector('[data-act="auto"]');
    if (b) b.setAttribute('aria-pressed', String(S.auto));
  }
  function setAuto(on) {
    markAuto(on);
    if (!S.auto) { clearTimers(); return; }
    if (S.mode !== 'tour' || !S.L) return;
    if (S.i >= S.L.stations.length - 1) { goTour(0); return; }
    if (S.speaking) return;                       // 지금 읽는 것이 끝나면 넘어간다
    if (S.heard === S.i) { afterStation(); return; }   // 이미 다 들은 정거장이면 바로 다음으로
    playStation(false);
  }

  // ---------- 복습 ----------
  function selectReview(i) {
    var L = S.L;
    S.sel = i;
    document.querySelectorAll('#hots .hot').forEach(function (h) { h.classList.toggle('sel', +h.dataset.i === i); });
    var idx = contentIdx(L), pos = idx.indexOf(i);
    setText($('rCount'), (pos < 0 ? '–' : pos + 1) + ' / ' + idx.length);
    if (i < 0 || !L.stations[i]) { $('rHint').hidden = false; $('rBody').hidden = true; return; }
    var st = L.stations[i];
    $('rHint').hidden = true; $('rBody').hidden = false;
    setText($('rBadge'), '정거장 ' + st.n);
    setText($('rObj'), st.obj);
    setText($('rFact'), st.fact);
    setHook($('rHook'), st.hook);
    setAttrs($('rAttrs'), st.attrs);
  }
  function stepReview(d) {
    var idx = contentIdx(S.L);
    if (!idx.length) return;
    var pos = idx.indexOf(S.sel);
    pos = pos < 0 ? (d > 0 ? 0 : idx.length - 1) : (pos + d + idx.length) % idx.length;
    selectReview(idx[pos]);
  }

  // ---------- 시험 (순서대로, 틀·되짚기 제외) ----------
  function startTest() {
    var idx = contentIdx(S.L);
    S.test = { idx: idx, k: 0, phase: idx.length ? 'ask' : 'done', right: 0, wrong: [], saved: null };
    renderTest();
  }
  function renderTest() {
    var T = S.test, L = S.L;
    $('tsAsk').hidden = T.phase !== 'ask';
    $('tsJudge').hidden = T.phase !== 'shown';
    $('tsDone').hidden = T.phase !== 'done';
    $('sAsk').hidden = T.phase !== 'ask';
    $('sShow').hidden = T.phase !== 'shown';
    $('sDone').hidden = T.phase !== 'done';
    if (T.phase === 'done') {
      setHoles([]);
      setText($('sBadge'), '결과');
      setText($('sProg'), '');
      setText($('sScore'), T.idx.length ? T.right + ' / ' + T.idx.length : '시험할 정거장이 없다');
      setText($('sSaved'), T.saved === null ? '' : T.saved ? '기록을 남겼다.' : '브라우저 저장소가 막혀 기록은 이 탭에만 남는다 — 내보내기로 보관하세요.');
      var ul = $('sWrong');
      ul.textContent = '';
      T.wrong.forEach(function (n) {
        var i = -1;
        L.stations.forEach(function (st, j) { if (st.n === n && kindOf(st) === 'station') i = j; });
        if (i < 0) return;
        var st = L.stations[i], li = document.createElement('li'), b = document.createElement('button');
        b.type = 'button'; b.dataset.act = 'goto-tour'; b.dataset.i = i;
        var f = document.createElement('span'); f.className = 'wf'; f.textContent = st.n + '. ' + (st.fact || '');
        var o = document.createElement('span'); o.className = 'wo'; o.textContent = (st.obj || '') + (st.hook ? ' · ' + st.hook : '') + ' — 투어로 보기';
        b.appendChild(f); b.appendChild(o); li.appendChild(b); ul.appendChild(li);
      });
      if (T.idx.length && !T.wrong.length) {
        var ok = document.createElement('li'); ok.className = 'hint'; ok.textContent = '틀린 정거장 없음.'; ul.appendChild(ok);
      }
      var recs = (readResults()[L.id] || []).slice(-6, -1).reverse();
      setText($('sPast'), recs.length ? '지난 기록 · ' + recs.map(function (r) { return r.score + '/' + r.total + ' (' + fmtDate(r.date) + ')'; }).join(' · ') : '');
      return;
    }
    var st = L.stations[T.idx[T.k]];
    setHoles(boxesOf(st));
    setText($('sBadge'), '정거장 ' + st.n);
    setText($('sProg'), (T.k + 1) + ' / ' + T.idx.length + ' · 맞음 ' + T.right);
    if (T.phase === 'shown') {
      setText($('sObj'), st.obj);
      setText($('sFact'), st.fact);
      setHook($('sHook'), st.hook);
      setAttrs($('sAttrs'), st.attrs);
    }
  }
  function judge(ok) {
    var T = S.test;
    if (!T || T.phase !== 'shown') return;
    var st = S.L.stations[T.idx[T.k]];
    if (ok) T.right++; else T.wrong.push(st.n);
    T.k++;
    if (T.k >= T.idx.length) {
      T.phase = 'done';
      T.saved = pushResult(S.L.id, { date: new Date().toISOString(), score: T.right, total: T.idx.length, wrong: T.wrong.slice() });
    } else T.phase = 'ask';
    renderTest();
  }

  // ---------- 주소 ----------
  function urlFor(id, mode) {
    if (!id) return location.pathname;
    return '?l=' + encodeURIComponent(id) + (mode && mode !== 'tour' ? '&m=' + mode : '');
  }
  function pushUrl(id, mode) {
    try { history.pushState(null, '', urlFor(id, mode)); route(); }
    catch (e) { location.href = urlFor(id, mode); }
  }
  function replaceUrl(id, mode) {
    try { history.replaceState(null, '', urlFor(id, mode)); } catch (e) { /* file:// 등 */ }
  }
  function route() {
    var q = new URLSearchParams(location.search);
    var id = q.get('l') || (location.hash ? location.hash.slice(1) : '');
    if (id && byId[id]) openLesson(id, q.get('m') || 'tour');
    else showList(id || null);
  }
  window.addEventListener('popstate', route);
  window.addEventListener('hashchange', route);

  // ---------- 입력 ----------
  document.addEventListener('click', function (e) {
    var t = e.target.closest('a[data-go], [data-act], [data-mode], [data-star], [data-ab], [data-view], .hot');
    if (!t) return;
    if (t.matches('a[data-go]')) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      var ctx = t.dataset.ctx;
      if (ctx === 'shelf') setPlaylist(SHELF, 'shelf');
      else if (ctx === 'book' || ctx === 'path' || ctx === 'stars') setPlaylist(viewIds(ctx), ctx);
      pushUrl(t.dataset.go, 'tour'); return;
    }
    if (t.dataset.star) { setStar(t.dataset.id, +t.dataset.star); return; }
    if (t.dataset.ab) {
      var k = t.dataset.ab;
      hub.repeat[k] = hub.repeat[k] === t.dataset.id ? null : t.dataset.id;
      saveHub(); syncHubControls(); renderToc(); return;
    }
    if (t.dataset.view) {
      if (VIEWS.indexOf(t.dataset.view) >= 0) { hub.view = t.dataset.view; saveHub(); renderToc(); }
      return;
    }
    if (t.tagName === 'BUTTON' && e.detail > 0) t.blur();   // 마우스로 누른 뒤 스페이스가 단추를 다시 누르지 않게
    if (t.classList.contains('hot')) { selectReview(+t.dataset.i); return; }
    if (t.dataset.mode) { if (t.dataset.mode !== S.mode) setMode(t.dataset.mode); return; }
    switch (t.dataset.act) {
      case 'export': exportResults(); break;
      case 'prev': goTour(S.i - 1); break;
      case 'next': goTour(S.i + 1); break;
      case 'goto': goTour(+t.dataset.i); break;
      case 'goto-tour': S.i = +t.dataset.i; setMode('tour'); break;
      case 'auto': setAuto(!S.auto); break;
      case 'voice':
        prefs.voice = !prefs.voice; savePrefs();
        t.setAttribute('aria-pressed', String(prefs.voice));
        if (prefs.voice) playStation(false); else { stopAll(); if (S.auto) playStation(false); }
        break;
      case 'replay': if (S.speaking) { setAuto(false); stopAll(); } else playStation(true); break;
      case 'rprev': stepReview(-1); break;
      case 'rnext': stepReview(1); break;
      case 'reveal': if (S.test && S.test.phase === 'ask') { S.test.phase = 'shown'; renderTest(); } break;
      case 'right': judge(true); break;
      case 'wrong': judge(false); break;
      case 'retest': startTest(); break;
      case 'autonext':
        hub.autoNext = !hub.autoNext; saveHub(); syncHubControls();
        if (!hub.autoNext) { clearTimeout(lessonTimer); note(''); }
        else if (S.L && S.mode === 'tour' && !S.auto) note('정거장 자동이 꺼져 있으면 되짚기까지 직접 넘긴 뒤 다음 그림으로 간다.');
        break;
      case 'prevlesson': goLesson(neighbor(-1, false), false); break;
      case 'nextlesson': goLesson(neighbor(1, false), false); break;
      case 'skip':
        hideErr();
        if (S.i < S.L.stations.length - 1) goTour(S.i + 1);
        else goLesson(neighbor(1, false), true);
        break;
      case 'resume':
        paused = false; hideErr();
        if (!S.speaking) afterStation();
        break;
      case 'openall': case 'closeall':
        CUR.chapters.forEach(function (ch) { if (t.dataset.act === 'openall') delete hub.closed[ch.id]; else hub.closed[ch.id] = true; });
        saveHub(); renderToc(); break;
      case 'hubexport': exportHub(); break;
    }
  });
  document.querySelectorAll('select[data-role="repeat"]').forEach(function (sel) {
    sel.addEventListener('change', function () {
      if (REPEATS.indexOf(sel.value) < 0) return;
      hub.repeat.mode = sel.value; saveHub(); syncHubControls();
      if (!$('listView').hidden) renderToc();
      if (S.L) renderPlNav();
    });
  });
  $('hubImport').addEventListener('change', function () {
    var f = this.files && this.files[0], input = this;
    if (!f) return;
    var rd = new FileReader();
    rd.onload = function () {
      var o = null;
      try { o = JSON.parse(String(rd.result)); } catch (e) { o = null; }
      if (!o || typeof o !== 'object' || !o.stars) { $('storeNote').textContent = '가져오지 못했다 — 「별표 · 설정 내보내기」로 만든 파일인지 확인하세요.'; input.value = ''; return; }
      hub = normHub(o, hub.closed); saveHub(); syncHubControls(); renderToc();
      $('storeNote').textContent = '가져왔다 — 별표 ' + Object.keys(hub.stars).length + '개' + (hubBroken ? ' (저장소가 막혀 이 탭에만)' : '') + '.';
      input.value = '';
    };
    rd.readAsText(f);
  });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {                            // 숨기면 걸린 타이머를 지운다(재생 중인 소리는 그대로)
      var pending = autoTimer || lessonTimer || safetyTimer;
      clearTimers(); clearTimeout(lessonTimer); lessonTimer = 0;
      if (S.L && S.mode === 'tour' && (S.auto || hub.autoNext) && (pending || S.speaking)) paused = true;
    } else if (paused && S.L && S.mode === 'tour') {
      if (S.speaking) paused = false;                 // 아직 읽는 중이면 끝 신호로 그대로 잇는다
      else showErr('탭을 떠난 사이 자동 넘김을 멈췄다.', 'resume');
    }
  });
  $('homeLink').addEventListener('click', function (e) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault(); pushUrl(null);
  });
  var rate = $('rate');
  function showRate() { setText($('rateOut'), prefs.rate.toFixed(1) + '×'); }
  rate.value = prefs.rate; showRate();
  rate.addEventListener('input', function () { prefs.rate = clamp(+rate.value, 0.8, 1.4); showRate(); });
  rate.addEventListener('change', function () { savePrefs(); if (S.speaking) playStation(true); });
  document.querySelector('[data-act="voice"]').setAttribute('aria-pressed', String(prefs.voice));
  if (!tts.ok && typeof Audio === 'undefined') {
    $('ttsNote').hidden = false;
    ['voice', 'replay'].forEach(function (a) { document.querySelector('[data-act="' + a + '"]').disabled = true; });
    rate.disabled = true;
  }

  document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey || !S.L || $('lessonView').hidden) return;
    var t = e.target, tag = t && t.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable)) return;
    var k = e.key, space = k === ' ' || k === 'Spacebar';
    if (space && tag === 'BUTTON') return;                    // 키보드로 고른 단추는 제 일을 한다
    if (!space && k !== 'ArrowLeft' && k !== 'ArrowRight') return;
    e.preventDefault();
    if (S.mode === 'tour') {
      if (k === 'ArrowLeft') goTour(S.i - 1);
      else if (k === 'ArrowRight') goTour(S.i + 1);
      else setAuto(!S.auto);
    } else if (S.mode === 'review') {
      if (!space) stepReview(k === 'ArrowLeft' ? -1 : 1);
    } else if (S.test) {
      if (S.test.phase === 'ask' && space) { S.test.phase = 'shown'; renderTest(); }
      else if (S.test.phase === 'shown' && !space) judge(k === 'ArrowRight');
    }
  });

  route();
})();
