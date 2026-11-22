# 다시 그린 장면에 명세 맞추기

장면 그림이 새로 바뀌었다(옛 그림은 같은 폴더 `scenes/_v1/<ID>.jpeg`). 명세 `built/<ID>.spec.json`은 옛 그림 기준이다. 새 그림 `scenes/<ID>.jpeg`(2752×1536)를 Read로 보고 맞춘다.

- 바꿔도 되는 것: 각 정거장의 `box`(새 그림에서 그 물건을 감싸게), `obj`(그림에 보이는 모습 묘사), `say`와 `tts` 안의 그림 묘사 부분(「그림에서는 …」 흠 문장 포함 — 고쳐진 흠은 지우고 새 흠이 있으면 적음), trainer의 그림 흠 줄.
- 바꾸지 않는 것: `fact` · `src` · `hook` · 정거장 수와 순서 · questions의 사실. 교재 사실은 그대로.
- 고친 까닭은 `/home/claude/work/runs/fix_20261122.json`(run별 ID의 FIX 문장)과 `/home/claude/work/runs/fix_log_20261122.md`에 있다.
- tts는 say를 소리 내 읽을 글: 한글 · 공백 · . , ? ! · 만.
- 검사: `python3 /home/claude/work/src/lessons/tools/spec_tools.py boxes <ID> <run>` → `built/<ID>_boxes.jpg`를 Read로 보고 상자를 맞춤, `python3 /home/claude/work/src/lessons/tools/spec_tools.py check <ID> --run <run>` → OK.
- 커밋하지 않는다. 끝나면 장면마다 한 줄(`<ID> OK · 바꾼 것`).
