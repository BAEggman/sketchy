// baeggman.github.io 아래 아무 쪽에서 실행. 결과는 window.__av 에 쌓인다.
(async () => {
  const EXTRA = {"new-gr-14__s7__7d3cc0f23073.mp3": "b3c318903dd46249f694367c7e6117e41ef738b534eccdd47c0aae1c5e549e68", "new-gr-14__s6__3360b942086d.mp3": "337dc0225f774a38f8f7b8d447399ca1f5add1a42c5546ce166ec7cc7ff81ccd"};
  const man = await (await fetch('/sketchy/audio/narration/manifest.json', {cache: 'no-store'})).json();
  const want = {};
  for (const r of Object.values(man.records)) want[r.src.split('/').pop()] = r.audio_sha256;
  Object.assign(want, EXTRA);
  const names = Object.keys(want).sort();
  const S = window.__av = {total: names.length, done: 0, ok: 0, fail: [], lines: [], finished: false};
  const hex = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
  let i = 0;
  async function worker() {
    while (i < names.length) {
      const n = names[i++];
      try {
        const res = await fetch('/sketchy-audio/' + n, {cache: 'no-store'});
        const sha = res.ok ? hex(await crypto.subtle.digest('SHA-256', await res.arrayBuffer())) : '';
        S.lines.push(n + ':' + res.status + ':' + sha);
        if (res.status === 200 && sha === want[n]) S.ok++; else S.fail.push([n, res.status, sha.slice(0, 12)]);
      } catch (e) { S.fail.push([n, 'ERR', String(e)]); S.lines.push(n + ':ERR:'); }
      S.done++;
    }
  }
  await Promise.all(Array.from({length: 8}, worker));
  S.lines.sort();
  S.digest = hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(S.lines.join('\n'))));
  S.finished = true;
})();
'started'
