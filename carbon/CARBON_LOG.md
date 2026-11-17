# Carbon v7 — 작업 로그 (`CARBON_LOG.md`)

## [2026-11-17] 단계 A — 준비 완료

- **저장소 및 브랜치**: `sketchy/` 저장소를 복제하고 `inbox/sketchy_6ddc850-8a8e120.bundle`을 검증·반영하여 `lesson-map-v1`(`8a8e120`)에서 작업 브랜치 `carbon-v7`을 생성하였다. `.gitignore`에 `carbon/blind/raw/`, `.env`, `masters/`, `_trash/`, `.venv/`를 추가하였다.
- **교재 및 파이썬 환경**: `refs/교재/`의 모든 `.docx` 교재·문제집·학습자료 37종을 `refs/교재/_txt/*.txt`로 추출하고, `.venv`(`google-genai`, `pillow`, `numpy`, `python-docx`)를 구축하였다.
- **파이프라인 및 부호 원판 시험**: `.env`(`GEMINI_API_KEY`) 미생성 상태를 확인하고 `BLOCKERS.md`와 `COST.md`에 기록한 뒤, Antigravity 내장 `image-generator` 서브에이전트와 독립 문맥 `blind-reader` 서브에이전트로 파이프라인을 구성하였다. 시험 장면(`masters/_test/base.png`, `1376×768`)에서 전체 참조 편집(방식 가)과 구역 절단 편집(방식 나)의 화소 변화량(`numpy` MAE)을 비교하여 `carbon/PIPELINE.md`에 기록하고, 숫자 물건 10종(0 공룡 ~ 9 구미호) 부호 원판을 `masters/_codes/numbers.png`로 제작하였다.
- **기준선 자동 판독 (`BASELINE.md`)**: 현행 `hist-02.webp`, `hist-06.webp`, `hist-07.webp` 세 과를 독립 판독(`blind-reader`)에 돌려 속성 회수율을 측정하였다. 전체 평균 회수율은 **52.6%**(60.5/115칸)였으며, 특히 수(0.0%), 왕조(31.6%, `hist-02`·`hist-07`은 0%), 字號(28.6%)가 그림에서 거의 회수되지 않음을 실측으로 확인하였다.
