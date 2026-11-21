# 十八反 · 十九畏 · 七情 장면 일꾼 안내 (Gemini 탭 하나 = 일꾼 하나)

너는 정해진 장면 프롬프트와 스티커 참조판을 Gemini에 넣어 장면 그림을 받고, 판정해 저장하는 일만 한다. 프롬프트 · 소품 · 동작은 바꾸지 않는다(6+1로 정했다). 커밋하지 않는다. 계정 · 결제는 건드리지 않는다.

## 준비
- ToolSearch 한 번: `select:mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__file_upload,mcp__remote-devices__device_bash,mcp__remote-devices__device_stage_files`
- 지시문의 탭 id 하나만 쓴다. 새 탭을 만들지 않는다.
- 장면 설계: `/home/claude/work/runs/20261122-p3-banwe/merged.json` (sheets[].id · stations · boundaries · prompt_en). 스티커 목록: `scene_jobs.json`. 사전: `/home/claude/work/src/dict/herbs.json`.
- 기록: `/home/claude/zt/scene/log_banwe.md` 에 장면마다 `Pxx · 시작 HH:MM · 끝 HH:MM · 시도 수 · accept/fail · 본 것 한 줄`.
- 이미 끝난 장면: `/home/claude/work/runs/20261122-p3-banwe/scenes/Pxx.jpeg` 가 있으면 건너뛴다.

## 장면 하나(Pxx)의 순서
1. `python3 /home/claude/work/src/lessons/tools/scene_ref.py Pxx 20261122-p3-banwe` → `OK`면 `/home/claude/zt/scene/Pxx_ref.jpg`(참조판)와 `Pxx_prompt.txt`가 생긴다. `MISSING`이면 스티커가 아직 없으니 다음 장면으로 넘어간다(다른 탭이 스티커를 그리는 중).
2. 프롬프트를 한 줄로: `tr '\n' ' ' < /home/claude/zt/scene/Pxx_prompt.txt | sed 's/  */ /g'` 출력을 그대로 쓴다.
3. 탭을 `https://gemini.google.com/app`로 navigate → 3초. 입력칸에 낯선 글이 있으면 지운다(오디오 · 낭독 요청 글, 다른 일꾼의 영어 프롬프트 — 사용자 허락).
4. 「업로드 및 도구」 클릭 → find로 「메뉴 옵션」 안의 file-input ref를 받는다 → `file_upload`(origin `https://gemini.google.com`, paths `["/home/claude/zt/scene/Pxx_ref.jpg"]`). 2초 뒤 입력칸 위에 썸네일이 보이는지 확인.
5. 「업로드 및 도구」 → 「이미지 만들기」 → 「가로세로 비율」 → **16:9** → 모델 버튼(「모드 선택 도구 열기 …」, 안 열리면 입력칸 오른쪽 「Neon」 글자 좌표를 클릭) → 「사고 수준」 → 「높음 매우 철저함」 → 모델 버튼 라벨에 「Neon 높음」 확인. ref는 매번 find로 받는다.
6. 입력칸 클릭 → 2의 한 줄 프롬프트를 type → screenshot으로 입력칸에 내 첨부 하나와 내 글만 있는지 확인 → **보내기 버튼**(입력칸 오른쪽 아래 파란 화살표). 10초씩 기다리며 「원본 크기 이미지 다운로드」가 나오면 다음(보통 2~3분, 6분 넘으면 새 채팅에서 다시).
   - 1095(「문제가 발생했습니다」)면 20초 쉬고 새 채팅에서 다시. 세 번 연달아면 멈추고 보고.
7. **내려받기는 잠금 안에서**: `device_bash` `bash $HOME/mnt/sketchy_opus/zone_test/_lock.sh` → LOCKED면 다운로드 클릭 → 10초 → `bash $HOME/mnt/sketchy_opus/zone_test/_grab.sh banwe_Pxx` → `bash $HOME/mnt/sketchy_opus/zone_test/_unlock.sh`. BUSY면 15초 뒤 다시. unlock을 빼먹지 않는다. 재시도 그림은 `banwe_Pxx_r2`, `_r3` …
8. `device_stage_files` paths `["/Users/mac/Downloads/sketchy_opus/zone_test/banwe_Pxx.jpeg"]` → 2초 → Read로 `/mnt/user-data/uploads/sketchy_opus/zone_test/banwe_Pxx.jpeg` 를 본다.
9. **판정**(merged.json의 그 장면 stations · boundaries와 대조):
   - 피규어마다 스티커(참조판)와 같은 꼴 · 색 · 소품으로 알아볼 수 있는가(사전 cue의 소리 낱말이 보이는가). 피규어가 빠지거나 다른 것으로 바뀌면 실패.
   - stations 순서(왼→오)와 「touches」 연결(앞 피규어의 동작이 다음 피규어에 닿음)이 대체로 보이는가.
   - boundaries의 칸 · 경계 표지(모래턱, 빈 틈, 단지 등)와 목적 표지(보라 독구름 흩어짐, 초록 악취 김 → 흰 김, 술 김 기둥, 반창고, 불꽃 → 눈송이 등 그 장면에 적힌 것)가 보이는가.
   - 그림 안에 글자 · 숫자 · 라벨이 없는가. 배경 쪽지 · 간판 · 책등의 **글씨 흉내 줄**도 실패(zoom으로 꼭 본다). 배경에 선반 · 병 · 단지가 가득해도 실패. 엉뚱한 인물 · 왕관 · 해골 · 메달이 생기지 않았는가. 손 · 팔다리가 망가지지 않았는가.
   - 모두 맞으면 accept: `cp /mnt/user-data/uploads/sketchy_opus/zone_test/banwe_Pxx.jpeg /home/claude/work/runs/20261122-p3-banwe/scenes/Pxx.jpeg` (재시도 그림이면 그 파일을 Pxx.jpeg로). 작은 흠(연결 한 군데가 약함 등)은 log에 한 줄 적고 accept.
10. 틀리면 새 채팅에서 같은 프롬프트로 다시. 재시도 횟수 제한 없음(사용자 규칙). 셋째부터는 소품 · 동작은 그대로 두고 틀린 점만 또렷이 적는 영어 문장 하나를 프롬프트 끝에 덧붙인다(예: 「The hippo is clearly sneezing a puff of white powder.」). 덧붙인 문장은 log에. 소품 자체를 바꿔야 할 것 같으면 log에 「6+1 필요」로 적고 다음 장면으로.

## 순서
장면 id는 F1~F4(十八反) · G1~G4(十九畏) · S1~S12(七情), 「Pxx」 자리에 이 id를 넣는다. 일꾼 1은 F1 → G4 → S1 … 차례, 일꾼 2는 S12 → S1 → G4 … 거꾸로. 장면을 시작하기 전에 `mkdir /home/claude/zt/scene/claimB_<id>`로 차지하고, 실패하면 건너뛴다. 모두 accept 또는 「6+1 필요」가 되면 끝.
**이 장면들의 판정에 더할 것**: 十九畏(G) 장은 짝마다 빨강 · 흰 바리케이드가 있고 두 약이 등을 맞대고 닿지 않으며, 독구름 · 겁먹은 표정이 없어야 한다. 十八反(F) · 相反 장은 닿는 자리에 보라 독구름이 터진다. 七情(S) 장은 맨벽 체육관 · 짝마다 둥근 파란 매트, 노란 빛 · 보라 구름 표지가 설계대로. 單行(S1)은 人參과 附子가 서로 닿지 않는다.

## 멈춰야 할 때
- reCAPTCHA(「로봇이 아닙니다」)가 뜨면 아무것도 누르지 말고 즉시 멈추고 보고한다.
- 브라우저가 2~3번 연속 응답이 없으면 멈추고 보고한다.
- 처음 보는 종류의 한국어 글이 입력칸에 있으면(오디오 · 낭독 요청이 아닌 것) 지우지 말고 멈추고 보고한다.

## 보고
장면 하나가 끝날 때마다 log_banwe.md에 한 줄(SendMessage는 쓰지 않는다 — 횟수 한도): `Pxx accept (시도 n) — 경로 · 흠 한 줄` 또는 `Pxx 6+1 필요 — 까닭`. 모두 끝나면 log 요약 10줄 이내.
