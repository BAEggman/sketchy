// Gemini 결과 그림을 원본 화소로 내려받기 위한 오버레이 캡처 도우미 (2026-10-13)
// Gemini 페이지는 TrustedHTML 정책이라 innerHTML 을 못 쓴다 → createElement 로만 만든다.
// 사용: javascript_tool 로 이 파일 내용을 한 번 실행 → window.__setup() → window.__show2(tx,ty,tw,th) → zoom 캡처 → window.__show2(-1)
window.__setup = function (idx) {
  // idx 생략 시 화면의 마지막 생성 그림(사용자 첨부 썸네일 제외)
  const ims = [...document.querySelectorAll('img')].filter(i => i.naturalWidth > 400 && !i.closest('user-query'));
  const im = idx === undefined ? ims[ims.length - 1] : ims[idx];
  window.__src = im.src; window.__W = im.naturalWidth; window.__H = im.naturalHeight;
  return window.__W + 'x' + window.__H + ' (생성 그림 ' + ims.length + '장 중 ' + (idx === undefined ? ims.length - 1 : idx) + '번)';
};
window.__show2 = function (tx, ty, tw, th) {
  // 그림의 (tx,ty)부터 tw×th CSS px 를 화면 왼쪽 위에 원본 배율로 띄우고, 오른쪽·아래 24px 를 마젠타로 두른다.
  let d = document.getElementById('__ov'); if (d) d.remove();
  if (tx < 0) return 'off';
  d = document.createElement('div'); d.id = '__ov';
  d.style.cssText = 'position:fixed;left:0;top:0;width:' + (tw + 24) + 'px;height:' + (th + 24) + 'px;background:#ff00ff;z-index:2147483647;';
  document.body.appendChild(d);
  const inner = document.createElement('div');
  inner.style.cssText = 'position:absolute;left:0;top:0;width:' + tw + 'px;height:' + th + 'px;overflow:hidden;background:#ff00ff';
  const im = document.createElement('img'); im.src = window.__src;
  im.style.cssText = 'position:absolute;left:' + (-tx) + 'px;top:' + (-ty) + 'px;width:' + window.__W + 'px;height:' + window.__H + 'px;max-width:none;display:block';
  inner.appendChild(im); d.appendChild(inner);
  return [tx, ty, tw, th].join(':');
};
