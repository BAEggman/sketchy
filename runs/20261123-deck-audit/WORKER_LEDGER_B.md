# 교재 대조 2차(확인판) 일꾼 안내

`WORKER_LEDGER.md`를 먼저 읽어라 — 규칙 · 자료 · 판정 낱말 · 금지(교재 문장 옮기지 않음, 고치지 않음, commit 안 함)는 그대로다.
다른 점: 묶음 전체를 다시 하지 않는다. `runs/20261123-deck-audit/ledger/<묶음>_b_todo.json`에 든 것만 **처음부터 네 눈으로** 판정한다. 1차 결과(`<묶음>_a.json`)는 **열지 마라**.
- `stations`: 과 · 정거장마다 사실 칸을 교재와 견줘 check(맞음/다름/교재에없음/갈림/찾지못함) · lines · note.
- `items`: 교재 줄 범위마다 그 항목이 덱 어디에 실렸는지(where)와 verdict(없음/글로만/약함/그림후보). 덱 전체에서 찾아라(과 JSON 전부를 grep — 한자 낱말로).
결과 `runs/20261123-deck-audit/ledger/<묶음>_b.json`: `{"bundle":"…","pass":"b","items":[…],"stations":[…]}` (WORKER_LEDGER.md의 꼴).
마지막 답은 세 줄: 판정 수 · 「다름」 · 「없음」 수.
