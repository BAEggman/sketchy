# 포제 장면 → 과 명세 쓰기 (일꾼 안내)

너는 이미 그려진 포제 장면 그림 한 장마다 학습 대본(정거장 명세)을 쓴다. 그림 · 소품 · 피규어 단서는 바꾸지 않는다. 커밋하지 않는다. src/lessons/ 에 파일을 만들지 않는다(과 등록은 메인이 한다).

## 읽을 것
- 본보기 과(말투 · 짜임 그대로 따른다): `/home/claude/work/src/lessons/l/pilot-cho.json` — 醋炙 ①의 시범 과다. frame → 피규어마다 정거장 → review, 반말(「~야」 「~지?」), 소리 단서를 먼저 풀고 사실을 붙이고 다음 피규어로 넘기는 동작으로 끝맺는다.
- 장면 설계: `/home/claude/work/runs/20261122-p3-suchi/merged.json` 의 sheets[id=Pxx] (method · lyric · setting · stations · aux · boundaries)
- 장면 그림: `/home/claude/work/runs/20261122-p3-suchi/scenes/Pxx.jpeg` (2752×1536) — **Read로 직접 보고** 그림에 실제로 있는 것만 obj · say에 쓴다. 설계와 그림이 다르면 그림을 따른다(예: 꿀단지가 쓰러져 있으면 「쓰러진 꿀단지」).
- 그림 일꾼 기록: `/home/claude/work/runs/20261122-p3-suchi/scene_log.md` 의 그 장면 줄(흠 · 덧붙인 문장).
- 피규어 단서: `/home/claude/work/src/dict/herbs.json` (hanja → cue · decode). hook은 decode를 따른다. **단서를 새로 짓지 않는다.**
- 사실 원천: 교재 `/mnt/user-data/uploads/refs/교재/_txt/한의학개론_p001-250_최종.txt` — 修治 3514–3560행, 十八反·十九畏·妊娠 3500–3503행, 韓藥의 分類 3561–3625행. `sed -n '3540,3550p'`처럼 줄을 직접 읽는다.
- 기본값 기록(교재 vs 본초.docx 차이 등): `/home/claude/work/runs/20261122-p3-suchi/defaults_log.md`

## 지킬 것
- **사실은 교재 줄에 있는 것만.** fact · say에 쓰는 사실은 모두 교재 줄 번호를 src에 단다(`"교재 3543"`). 교재에 없는 것(약의 효능 풀이, 이유 설명, 연도 등)은 쓰지 않는다. 확인 못 하면 trainer에 「확인 필요: …」로 적는다.
- **교재와 본초.docx가 다른 곳은 둘 다 나란히, 한쪽을 맞다고 하지 않는다**(사용자 원칙): 米炒 鷰參(교재) ↔ 黨參(본초.docx) · 蜜炙 紫蘇(교재) ↔ 紫菀(본초.docx) · 明煅 龍骨(본초.docx에만) · 油炙 淫羊藿(교재에만). say에 한 문장으로 「교재는 A, 본초 문서는 B — 둘 다 기억」처럼, trainer에도 한 줄.
- 교재 글자를 그대로 쓴다(山査 · 牧丹皮 · 白彊蠶 · 斑猫 · 萹豆 · 宣木瓜 · 鷰參). 사전 글자가 다르면 처음 한 번 괄호로(「牧丹皮(사전 표기 牡丹皮)」).
- 그림이 해석한 장면(예: 砂炒 ④ 잔털이 그을림)은 「그림에서는 …」으로 말하고 교재 사실처럼 쓰지 않는다.
- 같은 약이 여러 포제법에 나오면(麻黃 · 黃連 · 大黃 · 山藥 · 白朮 · 虎骨 · 馬錢子 · 乳香 등) 그 사실을 짧게 이어 준다(「麻黃은 蜜炙 ①에도 ③에도」).
- 시험 함정 짝을 한 번씩 짚는다(brief.md 1절 「시험에서 바꿔 내는 짝」).

## 명세 꼴 — `/home/claude/work/runs/20261122-p3-suchi/built/Pxx.spec.json`
```json
{"title":"<포제법 · 목적 — 두문자>", "place":"<작업대 한 줄>", "run":"20261122-p3-suchi",
 "method":"Gemini 스티커 참조 장면(scene_ref)",
 "stations":[
  {"n":0,"kind":"frame","obj":"…","fact":"…","hook":"…","say":"…","tts":"…","src":["교재 35xx"],"box":null},
  {"n":1,"kind":"herb","obj":"…","fact":"…","hook":"…","say":"…","tts":"…","src":["교재 35xx"],"box":[x,y,w,h]},
  … 피규어마다 하나(교재 순서 = 두문자 순서), 필요하면 목적 표지 정거장(kind "marker", 예: 반창고 = 止血) …
  {"n":N,"kind":"review","obj":"되짚기","fact":"…","hook":"<피규어 → 피규어 …>","say":"…","tts":"…","src":[…],"box":null}],
 "questions":[{"q":"…","a":"…"} ×5],
 "trainer":["…"],
 "notes":"…"}
```
- fact는 90자 이내. say는 pilot-cho 길이 정도(3~6문장).
- **tts**: say를 소리 내 읽을 글. 한글 · 공백 · 마침표 · 쉼표 · 물음표 · 느낌표 · 가운뎃점만. 한자는 한글 독음으로(醋炙 → 초자, 炒 → 볶을 초 처럼 뜻이 갈리면 풀어서), 숫자는 한글로(365 → 삼백육십오), 괄호 · 따옴표 · 줄표 · 「」는 빼거나 쉼표로.
- **box**: 그 정거장 물건을 감싸는 [x, y, 너비, 높이], 2752×1536 좌표, 짧은 변 240 이상, 그림 밖으로 나가지 않게. 그림을 Read하면 줄여 보이므로 「원본은 ×1.38」 안내를 따라 좌표를 원본으로 바꾼다. frame · review는 null.
- questions 5개: 두문자 순서대로 말하기 · 임의 자리 다음 약 · 목적(①②③)별 가르기 · 다른 포제법과 바꿔 낸 함정 · 그림 단서 → 약 이름.

## 검사
1. `python3 /home/claude/work/src/lessons/tools/spec_tools.py boxes Pxx` → `built/Pxx_boxes.jpg`를 Read로 보고 상자가 제 물건을 감싸는지 확인, 어긋나면 고친다.
2. `python3 /home/claude/work/src/lessons/tools/spec_tools.py check Pxx` → OK가 나올 때까지 고친다.

## 끝나면
맡은 장면마다 한 줄: `Pxx OK · 정거장 n개 · 확인 필요 k건`. 확인 필요 목록은 trainer에 있다고만 말한다. 10줄 이내.
