# src/lessons — Sketchy 과(lesson) 덱

「Sketchy와의 차이 33가지 없애는 법」 지침(2026-11-09)에 따라 허브 79판 740행을 진짜 Sketchy 꼴로 다시 짜는 작업. 허브(index.html)는 그대로 두고 새 덱은 여기서 따로 만든다.

## 과 지도 v1 (2026-11-09)
- `lesson_map.json` — 76과 · 정거장 751 · 정거장 행 488 · 틀 55 · dropped 197. 과마다 `title` · `place`(장소 후보) · `frame_rows` · `stations`(행 · 카드 id · split · note) · `n_stations`. 끝에 `dropped`(이유) · `gaps`(카드는 있는데 판이 없는 주제 41) · `flags`(사실·카드 충돌, 카드 오류 의심) · `coverage`(장별 카드 수 / 정거장에 걸린 수).
- 한 과 = 한 주제 · 한 장소 · 16:9 한 장 · 정거장 6~14(틀 · 되짚기 포함). 정거장은 시험 카드가 걸린 행에서 고른다(카드 없는 행은 흐름에 꼭 필요할 때만 `no_card`).
- 시험 카드 = 인출훈련 SRS 덱(BAEggman/qoaq `한의학_인출훈련_학습과학.html`의 FULLDECK 2016장). 한자어 자동 매칭 뒤 영역별로 손으로 확인했다(자동 매칭은 절반 가까이 틀리거나 빠졌다).
- 만든 방법: `map_brief_20261109.md`(영역별 작업 지시) — 의학사 · 음양오행 · 장상진단상한 · 본초방제병인병기 · 경락 다섯 영역을 따로 짜서 합쳤다. 검토 문서: Claude Docs 「한의학 Sketchy 과 지도」.

## 도구
- `tools/fetch_deck.sh` — qoaq에서 덱을 받아 `.cache/deck.json`(커밋 안 함).
- `tools/cards.py '<정규식>' [장]` — 카드 검색.
- `tools/check_map.py` — 740행이 정확히 한 번씩 배정됐는지 · 정거장 6~14 · 카드 id(덱이 있으면).

## 재생기
- 빌드: `python3 src/lessons/build_player.py` → 저장소 루트 `lessons.html`(단일 파일 · 외부 라이브러리/폰트/CDN 없음). 원본은 `player-template.html` + `player.js`, 과는 `l/*.json`에서 읽어 인라인한다. 그림은 `images/lessons/<id>.webp`를 링크하고, 없으면 회색 자리표시.
- 화면: 과 목록(`lessons.html?l=<id>`로 바로, `&m=review|test`) · 투어(상자만 밝힘 · ko-KR TTS 0.8~1.4 · 자동 넘김) · 복습(그림을 누르면 사실·고리) · 시험(순서대로, 틀·되짚기 제외 → 점수·틀린 정거장). 시험 기록은 localStorage `sketchy_lessons_v1` = `{과id: [{date, score, total, wrong:[n…]}]}`, JSON 내보내기. 키: ←/→ · 스페이스.
- 과 JSON 꼴(`l/<과id>.json`):
  ```json
  {"id": "hist-02", "title": "…", "place": "…", "image": "images/lessons/hist-02.webp", "w": 2048, "h": 1144,
   "stations": [
    {"n": 0, "kind": "frame", "obj": "장소 전체", "fact": "…", "hook": "…", "say": "…", "box": null, "src": []},
    {"n": 1, "obj": "…", "fact": "60자 이내", "hook": "…", "say": "2~4문장", "box": [x, y, w, h], "src": ["카드 id"]},
    {"n": 9, "kind": "review", "obj": "되짚기", "fact": "…", "hook": "…", "say": "…", "box": [[x, y, w, h], [x, y, w, h]], "src": []}
   ]}
  ```
  box는 w×h(보통 2048×1144) 기준 픽셀. 빌드는 꼴 오류(필수 칸 · 상자 꼴 · 번호/과 id 겹침)에서 멈추고, 정거장 6~14 · 사실 60자 · 상자 범위는 경고만.
- `l/_demo.json`(+ `images/lessons/_demo.webp`)은 재생기 시험용 자리표시 과다(한의학 내용 없음). 진짜 과가 들어오면 지워도 된다.

## 다음
시범 과 `hist-02`(南北朝·隋) — 설계(정거장마다 60자 사실 · 물건 · 고리, 예약표 첫 줄) → 재생기(투어 · 복습 · 시험) → 바탕 그림 → 판독 · 조각 고침 → 일치 검사 → 사용자 유지 시험.
