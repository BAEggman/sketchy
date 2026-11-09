// 한의학 Sketchy 과 재생기 — 과 목록 · 투어 · 복습 · 시험. build_player.py가 lessons.html에 끼워 넣는다.
(function () {
  'use strict';

  var LESSONS = JSON.parse(document.getElementById('lessons-data').textContent);
  var byId = Object.create(null);
  LESSONS.forEach(function (L) { byId[L.id] = L; });

  var KEY = 'sketchy_lessons_v1';          // { <과id>: [{date, score, total, wrong:[n…]}] }
  var PKEY = 'sketchy_lessons_prefs_v1';   // { rate, voice } — 이 브라우저만의 편의 설정
  var MODES = ['tour', 'review', 'test'];

  function $(id) { return document.getElementById(id); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

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
  var S = { L: null, mode: 'tour', i: 0, auto: false, heard: -1, speaking: false, sel: -1, test: null };
  var autoTimer = 0, safetyTimer = 0;

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

  function showList(missing) {
    stopAll(); setAuto(false);
    S.L = null;
    $('lessonView').hidden = true; $('listView').hidden = false; $('homeLink').hidden = true;
    document.title = '한의학 Sketchy 과';
    var note = $('listNotice');
    note.hidden = !missing;
    if (missing) note.textContent = '과 「' + missing + '」를 찾지 못했다. 아래 목록에서 고르세요.';
    var all = readResults(), ul = $('lessonList');
    ul.textContent = '';
    if (!LESSONS.length) {
      var li0 = document.createElement('li'); li0.className = 'hint';
      li0.textContent = '과가 없다 — src/lessons/l/*.json을 넣고 build_player.py를 돌린다.';
      ul.appendChild(li0);
    }
    LESSONS.forEach(function (L) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.className = 'lcard'; a.href = '?l=' + encodeURIComponent(L.id); a.dataset.go = L.id;
      var t = document.createElement('span'); t.className = 'lc-title'; t.textContent = L.title;
      if (L.id.charAt(0) === '_') { var tg = document.createElement('span'); tg.className = 'tag'; tg.textContent = '데모'; t.appendChild(tg); }
      if (L.has_image === false) { var tg2 = document.createElement('span'); tg2.className = 'tag'; tg2.textContent = '그림 없음'; t.appendChild(tg2); }
      var pl = document.createElement('span'); pl.className = 'lc-place'; pl.textContent = L.place || '';
      var m = document.createElement('span'); m.className = 'lc-meta';
      var c = document.createElement('span'); c.textContent = '정거장 ' + L.stations.length + ' · 시험 ' + contentIdx(L).length;
      m.appendChild(c);
      var recs = Array.isArray(all[L.id]) ? all[L.id] : [];
      var r = document.createElement('span');
      if (recs.length) {
        var last = recs[recs.length - 1];
        r.className = 'rec';
        r.textContent = '마지막 시험 ' + last.score + '/' + last.total + ' · ' + fmtDate(last.date) + (recs.length > 1 ? ' (' + recs.length + '회)' : '');
      } else { r.className = 'none'; r.textContent = '시험 기록 없음'; }
      m.appendChild(r);
      a.appendChild(t); a.appendChild(pl); a.appendChild(m);
      li.appendChild(a); ul.appendChild(li);
    });
    $('storeNote').textContent = storeBroken ? '브라우저 저장소가 막혀 있어 기록은 이 탭에만 남는다.' : '';
  }

  function openLesson(id, mode) {
    var L = byId[id];
    if (S.L !== L) { stopAll(); setAuto(false); S.L = L; S.i = 0; S.sel = -1; S.heard = -1; mountStage(L); }
    $('listView').hidden = true; $('lessonView').hidden = false; $('homeLink').hidden = false;
    setText($('lTitle'), L.title);
    setText($('lPlace'), L.place ? '장소 · ' + L.place : '');
    document.title = L.title + ' — Sketchy 과';
    buildDots(L);
    setMode(mode, true);
  }

  function setMode(mode, fromRoute) {
    if (MODES.indexOf(mode) < 0) mode = 'tour';
    stopAll(); setAuto(false);
    S.mode = mode;
    document.querySelectorAll('.modes button').forEach(function (b) {
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
  function stopAll() { clearTimers(); tts.stop(); setSpeaking(false); }
  function afterStation() {
    clearTimers();
    if (!S.auto || S.mode !== 'tour') return;
    if (S.i >= S.L.stations.length - 1) { setAuto(false); return; }
    autoTimer = setTimeout(function () { goTour(S.i + 1); }, 900);
  }
  function playStation(force) {
    clearTimers(); tts.stop(); setSpeaking(false);
    if (S.mode !== 'tour') return;
    var st = S.L.stations[S.i];
    var text = st.say || st.fact || '', at = S.i;
    if (tts.ok && (prefs.voice || force) && activated() && text) {
      setSpeaking(true);
      tts.speak(text, prefs.rate, function () { S.heard = at; setSpeaking(false); afterStation(); });
      if (S.auto) safetyTimer = setTimeout(function () { stopAll(); afterStation(); }, estimateMs(text) * 2 + 4000);
    } else if (S.auto) {
      var shown = (st.fact || '') + (st.hook || '') + (st.say || '');
      autoTimer = setTimeout(afterStation, estimateMs(shown));
    }
  }
  function setAuto(on) {
    S.auto = !!on;
    var b = document.querySelector('[data-act="auto"]');
    if (b) b.setAttribute('aria-pressed', String(S.auto));
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
    var id = q.get('l');
    if (id && byId[id]) openLesson(id, q.get('m') || 'tour');
    else showList(id || null);
  }
  window.addEventListener('popstate', route);

  // ---------- 입력 ----------
  document.addEventListener('click', function (e) {
    var t = e.target.closest('a[data-go], [data-act], [data-mode], .hot');
    if (!t) return;
    if (t.matches('a[data-go]')) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault(); pushUrl(t.dataset.go, 'tour'); return;
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
  if (!tts.ok) {
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
