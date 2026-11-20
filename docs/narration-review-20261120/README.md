# 그림 낭독 대본 검토본 — 반말판

[검토 페이지](https://baeggman.github.io/sketchy/narration-review.html) · [이번 검토 결과](audit-report.md)

본편 227과 2,067구간, 부록 737행, 괘도 2종의 2,806개 낭독문을 반말 서술체로 정리했다. ‘45세부터 위가 약해진다’를 포함한 사용자 니모닉, 원대본과 원문 필드, 기존 보류 이력을 보존했다.

본편 주요 그림 단서 227과를 대조했고 누락 용어·연결과 위치 설명을 72개 원고에서 보완했다. 본편 녹음 보류는 464개다. 보류 없는 1603개도 초안이며 무결성이나 음성 생성 승인을 뜻하지 않는다. 부록의 실제 그림 전수 검토와 why 필드의 추가 의미 검토는 미완료다.

- [본편 TXT](narrations.txt) · [CSV](narrations.csv) · [JSON](narrations.json)
- [부록 TXT](panel-narrations.txt) · [JSON](panel-narrations.json)
- [그림 대조](visual-audit.json) · [수동 내용 보완 전후](narration-content-edits.json)
- [어미와 안내말 변경 기록](plain-style-changes.json) · [보존 검사](plain-style-validation.json)
- [반말 변환 후 재검토](post-conversion-review.md) · [추가 수정 전후](post-conversion-review-edits.json)
- [이전 의미 검토 기록](semantic-qc.json) · [Gemini 실행계획](opus-gemini-execution-plan.md)

이전 검토본 기준은 `2fe65baa180138fcd98226bb41c4b68c70c3b918`, 최초 원자료 기준은 `539bab2a87625459874739246d0c5d8ca931d257`다. `python src/lessons/tools/build_plain_narrations.py`로 이 반말판을 재생성한다. 기존 학습 플레이어 say/tts를 덮어쓰거나 음성을 생성하지 않는다.
