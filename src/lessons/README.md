# src/lessons — Sketchy 과(lesson) 덱

「Sketchy와의 차이 33가지 없애는 법」 지침(2026-11-09)에 따라 허브 79판 740행을 진짜 Sketchy 꼴로 다시 짜는 작업. 허브(index.html)는 그대로 두고 새 덱은 여기서 따로 만든다.

## 과 지도 v2.1 (2026-11-09)
- `lesson_map.json` — **191과 · 정거장 1815**. 시험 카드 2016장 중 2006장이 정거장에 걸리고 10장은 뺐다(`skipped_cards`).
  - 허브 행 과 75개(`hist` · `yyox` · `zds` · `hp` · `mer`) — 허브 79판 740행을 다시 묶음. 과마다 `title` · `place`(장소 후보) · `frame_rows` · `stations`(행 · 카드 id · split · note) · `n_stations`.
  - 새 과 116개(`new-jq` 23 · `new-gr` 18 · `new-zj` 29 · `new-uk` 15 · `new-etc` 31) — 허브에 판이 없던 주제의 카드로 짠 과. 정거장은 `row: null, card_only: true, fact, cards`(사실은 카드 답에서만). 기존 과 정거장에 붙인 카드는 `attach_log`.
  - 끝에 `dropped`(188행, 이유) · `held`(약재 각론 11행 보류) · `flags`(사실·카드 충돌, 풀린 것은 `resolved`) · `decisions` · `coverage`(장별 카드 · 정거장 · 뺀 카드).
- 결정(2026-11-09): 361혈 = 李學川 『針灸逢源』(醫宗金鑑 360) · hist-07(鍼灸書 계보)과 mer-01(經絡學 발전사)을 hist-07 한 과로 · 약재 각론 행 보류 · 허브 그림은 모두 새 과 꼴로 다시 그림(허브는 새 덱이 다 설 때까지 그대로).
- 한 과 = 한 주제 · 한 장소 · 16:9 한 장 · 정거장 6~14(틀 · 되짚기 포함).
- 시험 카드 = 인출훈련 SRS 덱(BAEggman/qoaq `한의학_인출훈련_학습과학.html`의 FULLDECK 2016장). 이 지도를 짜며 찾은 카드 오류 54건은 qoaq에서 고쳤다(교정 1~3차).
- 만든 방법: `map_brief_20261109.md`(허브 행 다섯 영역) · `newmap_brief_20261109.md`(새 과 다섯 그룹). 검토 문서: Claude Docs 「한의학 Sketchy 과 지도」(탭 「새 과 116」).

## 도구
- `tools/fetch_deck.sh` — qoaq에서 덱을 받아 `.cache/deck.json`(커밋 안 함).
- `tools/cards.py '<정규식>' [장]` — 카드 검색.
- `tools/make_tts.js <qoaq html> <l/과.json>…` — 내레이션(say)을 한글 독음 읽기 대본(tts)으로 바꿔 넣는다(qoaq `HanjaSong.toReading` · `npm i jsdom` 필요). 「꽃(華)을」 꼴은 「꽃 화를」처럼 뜻+음으로, 기호는 쉼표로. 새 과를 만들 때마다 돌린다.
- `tools/check_map.py` — 740행이 정확히 한 번씩(과 · dropped · held) · 정거장 6~14 · 카드 id · 모든 카드가 정거장이나 skipped에 한 번씩(덱이 있으면) · 장소 겹침.

## 재생기
- 빌드: `python3 src/lessons/build_player.py` → 저장소 루트 `lessons.html`(단일 파일 · 외부 라이브러리/폰트/CDN 없음). 원본은 `player-template.html` + `player.js`, 과는 `l/*.json`에서 읽어 인라인한다. 그림은 `images/lessons/<id>.webp`를 링크하고, 없으면 회색 자리표시.
- 화면: 과 목록(`lessons.html?l=<id>`로 바로, `&m=review|test`) · 투어(상자만 밝힘 · ko-KR TTS 0.8~1.4 · 자동 넘김 — 음성은 tts 대본을 읽는다. 브라우저 음성이 한자를 중국어로 읽기 때문) · 복습(그림을 누르면 사실·고리) · 시험(순서대로, 틀·되짚기 제외 → 점수·틀린 정거장). 시험 기록은 localStorage `sketchy_lessons_v1` = `{과id: [{date, score, total, wrong:[n…]}]}`, JSON 내보내기. 키: ←/→ · 스페이스.
- 과 JSON 꼴(`l/<과id>.json`):
  ```json
  {"id": "hist-02", "title": "…", "place": "…", "image": "images/lessons/hist-02.webp", "w": 2048, "h": 1144,
   "stations": [
    {"n": 0, "kind": "frame", "obj": "장소 전체", "fact": "…", "hook": "…", "say": "…", "box": null, "src": []},
    {"n": 1, "obj": "…", "fact": "60자 이내", "hook": "…", "say": "2~4문장(화면용, 한자 그대로)", "tts": "say의 한글 독음 대본(읽어 주기용)", "box": [x, y, w, h], "src": ["카드 id"]},
    {"n": 9, "kind": "review", "obj": "되짚기", "fact": "…", "hook": "…", "say": "…", "box": [[x, y, w, h], [x, y, w, h]], "src": []}
   ]}
  ```
  box는 w×h(보통 2048×1144) 기준 픽셀. 빌드는 꼴 오류(필수 칸 · 상자 꼴 · 번호/과 id 겹침)에서 멈추고, 정거장 6~14 · 사실 60자 · 상자 범위는 경고만.
- `l/_demo.json`(+ `images/lessons/_demo.webp`)은 재생기 시험용 자리표시 과다(한의학 내용 없음). 진짜 과가 들어오면 지워도 된다.

## 다음
시범 과 `hist-02`(南北朝·隋)는 끝났다(설계 · 그림 `images/lessons/hist-02.webp` · 재생기 · 일치 검사). 사용자 유지 시험(하루 뒤 · 일주일 뒤 시험 모드 점수)을 받은 뒤 나머지 190과를 같은 걸음으로 그린다. 예약표는 `reserved.md`.
