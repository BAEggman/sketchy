# 구역 수정 일꾼 안내 (Gemini 탭 하나 = 일꾼 하나)

너는 이미 정해진 편집문을 Gemini에 넣고, 결과를 원본 그림에 붙이는 일만 한다. 편집문 · 소품 · 대본은 바꾸지 않는다(사람이 6+1로 정했다). 커밋하지 않는다. 사용자 계정 · 비밀번호 · 결제는 건드리지 않는다.

## 준비
- 브라우저 도구를 ToolSearch로 한 번에 불러온다: `select:mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__Google_Drive__create_file,mcp__remote-devices__device_bash,mcp__remote-devices__device_stage_files`
- 네가 쓰는 탭 id는 지시문에 있다. 그 탭만 쓴다. 다른 탭은 건드리지 않는다. 새 탭을 만들지 않는다.
- 작업 폴더: `/home/claude/zt/job/<LID>/` — `cur.png`(지금 그림), `edits.json`(편집 목록), 결과 `log.md`.

## 편집 하나(EID)의 순서
1. `bash /home/claude/zt/zjob.sh <LID> prep <EID>` → ASPECT(비율), PROMPT(편집문), SHA(업로드용 참조)를 출력한다. 편집 목록의 `order`가 「앞 편집 뒤」라고 하면 그 앞 편집을 먼저 accept한 뒤에 prep한다(목록 순서대로 하면 된다).
2. Drive에 올린다: `mcp__Google_Drive__create_file` — title `zt_<LID>_<EID>.jpg`, contentMimeType `image/jpeg`, base64Content = SHA 줄의 `sha256:…:경로` 그대로, parentId `1ejAoCp-iIlvUJyDHxuu1nCGN89Nwai17`, disableConversionToGoogleType true.
3. Gemini 새 채팅: 탭을 `https://gemini.google.com/app`로 navigate → 3초 → find로 「업로드 및 도구」 버튼 ref → 클릭 → find 「Drive에서 파일 추가 menuitem」 → 클릭 → 4초 → 파일 선택 창 검색칸(screenshot으로 위치 확인, 보통 (700,95) 또는 (725,118))에 `sketchy_zone_tmp` 입력 → Enter → 3초 → 폴더 더블클릭(보통 (211,230) 또는 (211,250)) → 3초 → 아래로 스크롤(10) → screenshot으로 `zt_<LID>_<EID>.jpg` 썸네일을 찾아 더블클릭. **파일 이름을 screenshot에서 꼭 확인한다**(다른 일꾼의 파일과 섞이지 않게). Drive 검색은 새 파일을 늦게 찾으니 폴더를 연다.
4. 「업로드 및 도구」 → find 「이미지 만들기 menuitemcheckbox」 클릭 → find 「가로세로 비율 button」 클릭 → ASPECT와 같은 menuitemradio 클릭 → 모델 버튼(「모드 선택 도구 열기…」) 클릭 → 「사고 수준」 → 「높음 매우 철저함」 → find로 모델 버튼 라벨에 **「Neon 높음」**이 있는지 확인(아니면 「심층 분석 4 Neon」을 고르고 다시). ref 번호는 페이지마다 바뀌므로 매번 find로 받는다.
5. find 「Gemini 프롬프트 입력 textbox」 클릭 → PROMPT를 그대로 type → Enter → 10초씩 6번 기다림 → find 「원본 크기 이미지 다운로드 button」(없으면 10초씩 더, 최대 3분).
6. **내려받기는 잠금 안에서**: `device_bash`로 `bash $HOME/mnt/sketchy_opus/zone_test/_lock.sh` → LOCKED가 나오면 다운로드 버튼 클릭 → 10초 → `bash $HOME/mnt/sketchy_opus/zone_test/_grab.sh <LID>_<EID>` → `bash $HOME/mnt/sketchy_opus/zone_test/_unlock.sh`. grab이 NO_NEW면 다운로드를 한 번 더 누르고 grab을 다시 한 뒤 unlock. **unlock을 빼먹지 않는다**(다른 두 일꾼이 기다린다).
7. `mcp__remote-devices__device_stage_files` paths `["/Users/mac/Downloads/sketchy_opus/zone_test/<LID>_<EID>.jpeg"]` → 2초 뒤 `bash /home/claude/zt/zjob.sh <LID> paste <EID>` → Read로 `prev_<EID>.png`(왼쪽 전, 오른쪽 후)를 본다.
8. 판정: 편집문의 번호 매긴 변경이 다 보이고, 「Keep …」에 적힌 것이 그대로이고, 글자 · 숫자가 없고, 붙인 자리에 이음매가 없으면 `bash /home/claude/zt/zjob.sh <LID> accept <EID>`. 하나라도 크게 틀리면(바뀌어야 할 게 안 바뀜, 사람 얼굴 · 자세가 바뀜, 엉뚱한 물건이 생김) 같은 편집문으로 새 채팅에서 **한 번만** 다시(파일 이름은 `<LID>_<EID>b`로 grab · stage · 그리고 paste 전에 `/mnt/user-data/uploads/sketchy_opus/zone_test/<LID>_<EID>b.jpeg`를 `<LID>_<EID>.jpeg`로 cp). 두 번째도 안 되면 accept하지 말고 log에 「실패 — 까닭」을 적고 다음 편집으로.
9. `log.md`에 한 줄: `EID · 비율 · 결과(accept/retry/fail) · 본 것 한 줄`.

## 멈춰야 할 때
- 탭에 「로봇이 아닙니다」(google.com/sorry, reCAPTCHA)가 뜨면 **아무것도 누르지 말고** 즉시 멈추고, 어디까지 했는지 보고한다(사용자가 직접 푼다).
- 브라우저가 2~3번 연속 응답이 없거나 같은 단계가 계속 실패하면 멈추고 보고한다.
- Gemini가 이미지를 거절하거나 글로만 답하면 한 번 다시, 또 그러면 log에 적고 다음으로.

## 끝나면
`log.md` 내용과 accept한 편집 목록, 실패 목록을 10줄 이내로 보고한다. `cur.png`가 최종 그림이다(과 JSON · 커밋은 사람이 한다).

## 시간 · 가볍게 (2026-11-21 18:32 사용자 규칙 — 이 뒤에 띄운 일꾼부터)
- log.md에 편집마다 `시작 HH:MM · 끝 HH:MM`과 가장 오래 걸린 단계를 적는다(`date +%H:%M`).
- 편집 한 건이 그 과의 앞 편집 평균의 두 배(처음 편집이면 12분)를 넘기면 끊고, log에 「시간 초과」로 적고 다음 편집으로 간다.
- 예측되는 클릭(메뉴 열기 → 항목 → 비율 → 모델 → 사고 수준)은 browser_batch 한 번으로 묶고, 그 사이 ref는 find 한 번으로 한꺼번에 받는다. screenshot은 Drive 파일 이름 확인 때와 결과 확인 때만.
- 재시도는 한 번. 두 번째도 실패하면 log에 「실패 — 까닭」을 적고 넘어간다(묶음이 끝난 뒤 모아서 편집문을 고쳐 다시 돌린다).
- 판정: 단서 물건이 안 보이거나 다른 것으로 읽힘 · 근거 없는 메달이 생김 · 보존 단서가 바뀜 · 얼굴이나 팔다리가 망가짐(팔이 엉뚱한 곳에서 솟음 포함) · 이음매가 한눈에 보임 → 다시. 전후를 나란히 놓아야만 보이는 차이는 log에 한 줄 적고 accept.
- 그림 안에 글자 · 숫자가 있으면 실패. 인물 손은 자기 책에 닿아 있어야 한다.
