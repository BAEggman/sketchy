# 일곱 번째(심사) 지시 — 修治 장면 6+1

읽을 것: `runs/RUBRIC.md`, `runs/20261122-p3-suchi/brief.md`, `<묶음>/p1.json`~`p6.json`, 필요한 피규어의 `src/dict/herbs.json` cue · draw_en.

1. `<묶음>/judge.md` 맨 위에 기준 세 줄(5-1을 읽고, 이번 묶음에 어떻게 쓸지).
2. `<묶음>/six.md`: 장마다 여섯 안의 생각을 한 줄씩 표로.
3. 장마다 장면 100점으로 채점(사실 · 출처 20 · 단서 합 30 · 관계가 피규어의 동작에서 일어나는가 20 · 교재 범위와 혼동 짝 10 · 소품 수와 그릴 수 있음 10 · 기존 약속 보존 10), 상위 두 안과 까닭. 새 사전 항목은 단서 25점.
4. 낙제: 사실 오류 · 피규어를 사전과 다르게 그림 · 굳은 물건 사용 · 운반 낱말 셋째 사용 · 새 물건 여덟 초과 · 글자 · 숫자.
5. 가장 적은 구성으로 합친다. 
내는 것: `<묶음>/judge.md`, `six.md`, `final.json`:
```
{"batch":"Q1","sheets":[{"id":"P01","method":"淸炒 · 炒焦","lyric":"산천치빈","setting":"…","stations":[{"herb":"山査","where":"왼쪽 첫째","action":"…","touches":"川楝子"}, …],"aux":"…","boundaries":"…","prompt_en":"Gemini에 넣을 영어 프롬프트 한 덩어리(16:9 · 글자 숫자 없음 · 피규어마다 사전 draw_en의 꼴을 그대로 넣음)","score":0,"from":"p2 · p5"}],
 "new_dict":[{"hanja":"貫衆","reading":"관중","cue":"…","draw_en":"…","decode":"…","carriers":["…"],"type":1,"score":0}],
 "needs_user_ok":[],"check_needed":[]}
```
다 쓰면 「완료」와 needs_user_ok 개수만 답한다.
