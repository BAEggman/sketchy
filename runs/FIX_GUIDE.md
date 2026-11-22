# 고쳐 그리기 일꾼 안내 (11-22, 판독자가 엇나가게 · 헷갈리게 읽은 곳)

너는 이미 있는 장면을 **같은 소품 · 같은 동작으로** 다시 그려, 프롬프트 끝의 `FIX:` 문장이 말하는 점만 또렷하게 만든다. 소품 · 피규어를 바꾸지 않는다. 커밋하지 않는다. 계정 · 결제는 건드리지 않는다. SendMessage는 쓰지 않는다(횟수 한도) — 기록은 `/home/claude/zt/scene/log_fix.md`, 끝나면 최종 보고만.

## 맡을 일 목록
| run | id | 먼저 끝나야 할 스티커 |
|---|---|---|
| 20261122-p3-suchi | P12 · P16 · P17 · P18 · P20 · P22 | 없음 |
| 20261122-p3-banwe | F1 · F2 · G1 · G2 · G3 · G4 · S4 · S10 | 없음 |
| 20261122-p3-suchi | P02(H089) · P08(H105) · P09(H150) · P11(H110) | 괄호 안 스티커 |
| 20261122-p3-banwe | F4(H009) · S6(H158) · S7(H145) · S9(H009 · H145 · H161) | 괄호 안 스티커 |

스티커가 다시 그려졌는지: `/home/claude/zt/scene/stickers_done`(빈 파일)이 있으면 S30 · S31 판이 끝난 것이다. 없으면 스티커가 필요한 장면은 건너뛰고 나중에 다시 돈다.

## 장면 하나(<id>, <run>)
0. 차지: `mkdir /home/claude/zt/scene/claimF_<id>` — 실패하면 건너뛴다.
1. `python3 /home/claude/work/src/lessons/tools/scene_ref.py <id> <run>` → `/home/claude/zt/scene/<id>_ref.jpg` · `<id>_prompt.txt`(끝에 `FIX:` 문장이 붙어 있다). 한 줄로: `tr '\n' ' ' < /home/claude/zt/scene/<id>_prompt.txt | sed 's/  */ /g'`.
2. 옛 그림 `/home/claude/work/runs/<run>/scenes/_v1/<id>.jpeg`를 Read로 한 번 본다(무엇이 이미 맞았는지 기억).
3. 그리기 절차는 `/home/claude/zt/scene/SCENE_GUIDE.md`의 3~8단계 그대로(새 채팅 · 참조판 직접 올리기 · 이미지 만들기 · 16:9 · Neon 높음 · 보내기 버튼 · 잠금 안에서 내려받기). 내려받기 이름은 `fix_<id>`, 재시도는 `fix_<id>_r2` …. 이 Mac에서 전체 선택은 cmd+a. 입력칸에 다른 일꾼의 영어 프롬프트가 남아 있으면 지운다.
4. **판정**: (a) `FIX:` 문장이 말한 점이 그림에서 **분명히** 보이는가 (b) 옛 그림에서 맞았던 것(피규어 · 순서 · 연결 · 칸 · 표지 · 글자 없음 · 맨벽 배경)이 그대로 맞는가. 둘 다 맞으면 accept: `cp /mnt/user-data/uploads/sketchy_opus/zone_test/fix_<id>….jpeg /home/claude/work/runs/<run>/scenes/<id>.jpeg`. 크기가 1376×768이면 `python3 -c "from PIL import Image; im=Image.open('…'); im.resize((2752,1536),Image.LANCZOS).save('/home/claude/work/runs/<run>/scenes/<id>.jpeg',quality=93)"`.
5. 아니면 새 채팅에서 다시. 셋째부터는 틀린 점만 또렷이 적는 영어 문장 하나를 끝에 더한다(소품 · 동작은 그대로). **여섯 번 해도 (a)와 (b)를 함께 못 맞추면** 옛 그림을 그대로 두고 log에 「고침 실패 — 옛 그림 유지, 가장 나은 시도 파일 이름」. 실패 그림으로 scenes/<id>.jpeg를 덮지 않는다.
6. log 한 줄: `<id> · 시작 · 끝 · 시도 수 · accept/유지 · 무엇이 고쳐졌나 한 줄`.

## 멈출 때
reCAPTCHA · 브라우저 2~3번 무응답 · 처음 보는 한국어 글이 입력칸에 있으면 멈추고 보고. 1095는 20초 쉬고 새 채팅, 세 번 연달아면 그 장면을 건너뛰고(차지는 풀지 말고) 다음 장면.
