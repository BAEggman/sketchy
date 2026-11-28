# Sketchy 나 선 고치기 — 실행 지시서 (2026-11-28)

사용자 결정(11-28 10:34): 가 선 ①이 20분 만에 끝나 **나 선까지** 다른 대화에 맡겨 본다. 나 선 = 가 선 + 「중간」 흠 과. 이 문서는 **가 선에 없는 165과**만 다룬다. 가 선 ②~⑥은 `claude/Sketchy_가선_실행지시서_20261128.md` 그대로 간다. 공통 규칙은 가 선 지시서의 「모든 번호에 공통」을 그대로 쓰되, 기록 폴더는 `runs/20261128-line-na/<번호>/`, 꾸러미 이름은 `sketchy_line-na-<번호>_<날짜>.bundle`, 녹음 대기 목록은 가 선과 같은 `runs/20261128-line-ga/rerecord.json`에 더한다.

**꾸러미 만들기 직전에 반드시** `git fetch origin main && git rebase origin/main`(다른 대화가 먼저 올린 것 위에 얹는다). 충돌이 나면 고치지 말고 멈춰 알린다.

## 차례

| 번호 | 할 일 | 과 | 모델 · effort | 어림(가 ① 실측 반영) |
|---|---|---|---|---|
| 나① | 글만 고침 | 60 | Opus 5.5 · high | 1시간 안팎 |
| 나② | 표 연습으로 옮김 + 舍岩 12방을 표 연습에 잇기 | 14 + 12 | Opus 5.5 · high | 1~2시간 (**가 ② 뒤에** — 가 ②가 정한 표 꼴을 그대로 쓴다) |
| 나③ | 유주도 12장(코드로 그림) | 12 | Opus 5.5 · high | 3~5시간 |
| 나④a~d | 구역 고침 | 65 (16 · 16 · 16 · 17) | Opus 5.5 · high | 대화마다 4~7시간 |
| 나⑤ | 다시 그림 | 2 | Opus 5.5 · high | 2~4시간 |
| 녹음 · 마감 | 가 ⑤ · ⑥에 합친다 | — | — | 녹음 과가 약 55과 늘어 ⑤가 6~9시간 |

- 나①은 가 ②와 과가 겹치지 않아 **지금 바로** 동시에 돌려도 된다. 그림 쓰는 대화(가 ③ · ④, 나③ 이후 Gemini 쓰는 것)는 한 번에 하나.
- 여섯 안은 로컬 꾸러미로 미리 뽑아 둘 수 있다: `sketchy_outsource_na_briefs_20261128.zip`의 브리프 67개를 `sketchy_외주꾸러미_20261128/T34_여섯안/briefs/`에 더 넣고 `run_six.py`.

## 과 목록

- **나① 글만(60)**: new-gr-17 · new-gr-16 · new-gr-09 · new-gr-08 · mer-02 · new-gr-01 · new-gr-02 · new-gr-12 · mer-03 · hp-19 · new-gr-11 · zds-16 · yyox-10 · new-uk-11 · new-jq-18 · new-jq-15 · new-jq-07 · yyox-01 · new-jq-16 · new-zj-02 · new-jq-09 · new-jq-11 · zds-02 · zds-03 · new-gr-06 · hp-06 · new-jq-21 · hp-14 · new-jq-08 · new-uk-02 · new-uk-12 · new-zj-16 · zds-04 · zds-05 · new-zj-06 · new-uk-05 · zds-10 · new-gr-04 · new-gr-05 · new-etc-10 · hp-09 · new-etc-12 · new-gr-10 · new-etc-06 · new-gr-31 · zds-08 · new-etc-16 · new-zj-08 · new-etc-30 · hist-14 · suchi-ju-cho · hist-05b · fan18 · hist-05a · suchi-dan · suchi-gabo2 · hist-10 · suchi-qingchao · suchi-suhwa · suchi-yeom-gang
- **나② 표(14)**: hp-05 · mer-05 · new-etc-19 · new-etc-20 · new-gr-36 · hist-11 · mer-07 · mer-06 · hp-18 · yyox-05 · new-uk-01 · yyox-04 · new-etc-14 · new-etc-31
- **나② 舍岩(12, 보관함)**: new-gr-19 ~ new-gr-30 — 그림은 그대로 두고 정거장마다 `saam.html`의 해당 경 연습으로 가는 이음만 단다(寒熱格 세 칸은 원표 확인 전이라 건드리지 않음).
- **나③ 유주도(12)**: new-gr-35 · 37 · 38 · 39 · 40 · 41 · 42 · 43 · 44 · 45 · 46 · 47 — 지금 물건 칸이 틀 문구 그대로다. `pilot-gv`(督脈) 방식(`make_gv_path.py` + `render_svg.js`)으로 경락 유주도를 코드로 그리고, 사용자 유주 니모닉(프로젝트 `claude/5장경락_0518수정_본문추출.md`, Mac `~/Downloads/_정리됨/한의학/학습자료/`)을 보존 그대로 얹는다. 순행 사실은 교재 줄만.
- **나④a 구역(16)**: qiqing-coop · qiqing-conflict · hist-13 · hist-01a · new-etc-05 · new-etc-25 · new-zj-14 · new-etc-18 · yyox-14 · new-zj-13 · new-uk-07 · new-zj-25 · hp-17 · new-zj-12 · yyox-12 · new-jq-20
- **나④b 구역(16)**: new-jq-10 · new-jq-19 · new-jq-04 · new-zj-05 · new-jq-03 · new-jq-22 · yyox-06 · new-etc-27 · new-zj-01 · zds-01 · new-jq-02 · new-zj-28 · yyox-09 · new-etc-07 · new-zj-15 · new-etc-09b
- **나④c 구역(16)**: new-zj-03 · new-etc-24 · new-zj-10 · new-etc-28 · new-etc-13 · new-zj-22 · new-etc-29 · hp-11 · new-uk-10 · new-etc-23 · new-zj-11 · new-etc-17 · zds-11 · hist-06a · hist-09 · hist-08b
- **나④d 구역(17)**: hist-02b · hist-04 · pilot-wangbing · suchi-gabo1 · hist-12 · new-uk-14 · zds-12 · new-zj-21 · new-etc-15 · new-etc-04 · new-etc-02 · new-etc-03 · hist-01b · hist-02a · hist-07a · pilot-tao · pilot-xue
- **나⑤ 다시 그림(2)**: yyox-13 · new-zj-17

## 번호별 덧붙임

- **나①**: 가 ①과 같은 방법(사실 · 고리 칸 · 정거장 가르기, 이미 있는 고리만 — 사전 · 보존 목록 · 교재 암기요령 · 사용자 문장). 그림이 필요하면 「나④로 넘김」에 적는다. 의학사 · 본초 새 문법 과(hist-* · suchi-* · fan18)는 명세(`runs/<run>/built/*.spec.json`)를 고치고 `make_zone_lesson.py`로 다시 만든다.
- **나②**: 가 ②가 남긴 「표 꼴」 결정(DECISIONS.md)을 먼저 읽고 그대로 쓴다. 가 ②가 아직이면 멈추고 알린다.
- **나③**: 12장 모두 같은 틀(인체 윤곽 · 경로 · 혈 점 · 방향)로. 혈 위치는 WHO 2008 일반 기준이고 교재 經穴圖 대조는 「확인 필요」로 남긴다. 그림에 글자 · 숫자를 넣지 않는 규칙은 유주도에도 적용하되, 빈 판과 혈 이름 판 둘을 만든다(`pilot-gv`처럼).
- **나④**: 가 ③과 같다. 여섯 안 · 심판을 GPT · 로컬이 미리 했으면 `~/Downloads/sketchy_opus/outsourced/<과>/final.json`을 쓰고, RUBRIC으로 한 번 훑어 교재 줄 · 사용자 결정에 어긋나는 것만 고친다. 의학사 · 본초 새 문법 과는 구역 편집 뒤 명세를 맞춰 `make_zone_lesson.py`로.
- **나⑤**: 가 ④와 같다.

## 사용자 결정 (11-28 10:37)

- **나①**: `new-zj-07` 제목의 「실체설 셋(… 李時珍)」을 **교재 命門 절대로 고친다**(교재 命門 절에는 李時珍이 없다 — 교재 2164 · 2599는 李時珍 = 腦爲元神之府). 이 과는 가 ③a에서 그림을 고치므로, 나①은 제목 · 사실 글만 고치고 그림은 건드리지 않는다.
- **나④d**: `hist-03a` · `hist-07b`의 그림 고리(滑壽 · 陳會 · 두 賦)를 **덧붙일 후보로** 함께 본다 — 6+1로 정하고, 그 대화 끝에 사용자에게 보인다.
- `new-gr-13` 齦交 다시 녹음은 가 ⑤에서 한다.

## 진행표

| 번호 | 상태 | 커밋 | 비고 |
|---|---|---|---|
| 나① | 끝(11-28 · Opus 5.5) · 사용자 올림 대기 | 나 선 ① 커밋들(`22b1bc6` 위) | 57과(`new-zj-07` 제목 · 글 — 사용자 결정 10:37 포함) · 속성 줄 210정거장(글로만 262줄) · 이름 고리 29 · 녹음 11 재검토 대기 · 74 해시만 · 넘김: 나④ 구역 15 · 가름 31 / ② 표 12 · `runs/20261128-line-na/①/README.md` |
| 나② | 대기(가 ② 뒤) | | |
| 나③ | 대기 | | |
| 나④a | 대기 | | |
| 나④b | 대기 | | |
| 나④c | 대기 | | |
| 나④d | 대기 | | |
| 나⑤ | 대기 | | |