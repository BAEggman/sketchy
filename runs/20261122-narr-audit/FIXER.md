# 녹음 전 대본 수정 — 수정자 지시서

사용자 승인(2026-11-22 12:37): 감사에서 나온 사실 오류(상, 그리고 중 등급 가운데 FACT)는 교재 줄에 맞춰 고친다. 그림과 대본이 어긋나는 것(PIC 중)은 **대본 쪽을 그림에 맞춘다** — 그림은 이번에 고치지 않는다. 동음이의어·발음(PRON)은 대본 낱말을 바꾸지 않고 발음층(읽기 메모)으로 넘긴다. 단 「사전 피규어」「이 과는 활수로 둔다」 같은 제작 메모가 tts에 섞인 것은 대본에서 자연스러운 말로 바꾼다.

## 입력
- 감사 결과: /home/claude/work/runs/20261122-narr-audit/<그룹>.md
- 과 JSON: src/lessons/l/<id>.json (빌드 결과물 — 직접 고치지 않는다)
- 정본 명세: 과 JSON의 attrs.run → runs/<run>/built/<id>.spec.json (본초는 runs/20261122-p3-suchi/built/Pnn.spec.json, runs/20261122-p3-banwe/built/<F|G|S>n.spec.json; 과 id ↔ 명세 이름: suchi-NN=PNN, qiqing-NN=S<N>, fan18-N=F<N>, wei19-N=G<N>). 같은 폴더에 gen*.py가 있고 그것이 spec.json을 만든다면 gen*.py 쪽 문자열도 같이 고쳐 다음 재생성에서 되돌아가지 않게 한다.
- 교재: /mnt/user-data/uploads/refs/교재/_txt/한의학개론_p001-250_최종.txt (줄 번호). 문제집: 같은 폴더 한의학개론_문제집_정답_최종수정본_전체.txt.

## 고치는 법
1. 감사 항목마다 교재 줄을 직접 읽고 지적이 맞는지 먼저 확인한다. 지적이 틀렸으면 고치지 않고 「반려 — 이유」로 적는다.
2. 고칠 때는 tts와 fact(·say·hook에 같은 내용이 있으면 그것도)를 함께 고친다. tts는 한글·공백·. , ? ! · 만. fact 90자 이내.
3. **고치지 않는 것**: 사용자 암기 문장·두문자·말장난(예: 오두방정 반과 패백, 감대원상 오), src/lessons/reserved.md·계획서 8절 보존 목록에 있는 문구. 이런 데에 걸리면 고치지 말고 「사용자 확인 필요」로 적는다.
4. 교재와 원전·문제집이 서로 다르고 둘 다 원리상 맞을 수 있으면 한쪽을 택하지 않는다. 「교재는 …, 문제집은 …」처럼 나란히 둔다. 교재에 줄이 없는 것을 단정하지 않는다(「확인 필요」 항목은 단정하는 말을 빼거나 「문제집 답」이라고 출처를 밝히는 정도로).
5. 사실을 지어내지 않는다. 교재 원본 글자 확인이 필요한 것(예: 蓍油, 紫菀/紫蘇 OCR)은 대본을 바꾸지 말고 「사용자 확인 필요」로 적는다.
6. 명세를 고친 뒤 과를 다시 만든다:
   python3 src/lessons/tools/spec_tools.py check <명세이름> --run <run>   (본초 run만 해당; 의학사 run은 runs/<run>/built/check.py가 있으면 그것)
   python3 src/lessons/tools/make_zone_lesson.py <id> <그림> <명세.json>
   그림 경로: 본초 = runs/<run>/scenes/<명세이름>.jpeg, 의학사 = 그 과를 만든 원본 그림(과 JSON image의 webp가 아니라 runs/<run>/ 안의 완성 png/jpeg; 찾을 수 없으면 images/lessons/<id>.webp를 png로 변환해 써도 된다 — 크기 2752×1536 확인). 
7. 발음 문제(PRON)와 동음이의는 /home/claude/work/runs/20261122-narr-audit/reading_notes_<그룹>.json 에 모은다: {"<id>#<n>": ["마시는 인명(명나라 의가), 동사 마시다가 아님", …]} — Gemini 낭독자에게 넘길 짧은 읽기 메모. 낱말을 바꾸라는 메모가 아니라 어떻게 읽고 어디서 끊을지 알려 주는 메모다.
8. git commit은 하지 않는다(메인이 묶어서 한다). 다른 그룹의 파일은 건드리지 않는다.

## 결과
/home/claude/work/runs/20261122-narr-audit/fix_<그룹>.md 에:
- 고친 것: id#n · 무엇을 → 무엇으로(요지) · 근거 줄
- 반려: id#n · 이유
- 사용자 확인 필요: id#n · 무엇을 · 왜
최종 응답은 5줄 이내 요약.
