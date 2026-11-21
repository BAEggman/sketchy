# Run 2 醋炙 첫 장 — 실제로 쓴 Gemini 프롬프트 (2026-11-21)

Gemini 앱 · 이미지 만들기 · 16:9 · 카본 높음. 한 대화에서 바탕 1회 + 편집 3회.
원본: `~/Downloads/sketchy_opus/gemini_raw/`

| 판 | 프롬프트 | 내려받기 | 결과 |
|---|---|---|---|
| v0 바탕 | `final.json` `prompt_en.base` 그대로 | p2-cho_v0-base.jpeg | 다섯 피규어(우유 향수병 · 시계 호랑이 · 부자 · 청피망 복면 · 색동 호스)와 팬 · 현관. 글자 · 숫자 · 지폐 없음. **비워 두라던 틈이 좁았다** |
| 편집 1 | 아래 ① (`edits[0]` + 자리 만들기 한 문장) | 받지 않음 | 물약병 · 세모 날 쇠침 · 튀는 코르크 들어옴. 오른쪽 피규어는 거의 안 밀려 **쇠침과 호랑이 사이 틈이 없음** |
| 편집 2 | 아래 ② (`edits[1]`의 놓는 자리만 「틈」 → 「쇠침 끝 위 · 호랑이 종 바로 위 공중」) | p2-cho_v1-edit2-cabbage.jpeg | 포대기 · 쪽쪽이 초록 아기 배추 인형이 종 위 공중에서 놀라 뜀 |
| 편집 3 | 아래 ③ (`edits[2]` 대신) | **p2-cho_v2-edit3-tumble.jpeg ← 채택** | 소용돌이가 붉은 방석을 쳐내고 부자가 뒤로 넘어지며 향수를 누름. 우유 팩 분무기 옆 짧은 분사선 지움 |

`edits[2]`(글자 · 지폐 · 여분 지우기)는 쓰지 않았다. v1을 원본 크기로 직접 보니 지울 글자 · 숫자 · 지폐 · 여분 병이 없었다. 대신 그림이 심사 명세와 어긋난 두 곳을 고쳤다.
- 부자가 방석에 앉아 웃고만 있었다 → 정거장 6 「방석이 빠진 부자가 뒤로 벌러덩」.
- 우유 팩 분무기 옆에 짧은 분사선이 있었다 → 사용자 결정 「乳香 뿌리지 않고 붓기만」.

소품 · 상황 · 연결은 바꾸지 않았다. 바꾼 것은 놓는 자리와 자세뿐이다(6+1 대상 아님).

## ① 편집 1
Edit this image. First make room: slide the alarm-clock tiger, the rich man, the pepper-mask person, the rainbow hose and the door all to the right so that a wide empty stretch of pan (about one third of the picture width) opens between the milk carton and the tiger; keep all of them exactly as they are otherwise. Then add exactly two things in the left part of that stretch and nothing else. First, right next to the milk carton: a round-bottomed glass flask with a cork, filled with black liquid (no skull, no bubbles, no label), standing in the vinegar; the poured vinegar splashes over it, a wavy green stink line above it turns into a clean white wisp, and its cork is popping off and flying to the right. Second, right of the flask: the tallest object in the whole picture, a giant thick steel needle standing on its blunt end, with a sharp three-edged point whose flat triangular faces and triangular cross-section are clearly visible; it has no face, no legs and no blood. The flying cork hits its head and it tips over to the right. Leave the space between the needle and the tiger empty. No text, no letters, no numbers.

## ② 편집 2
Edit this image. Add exactly one thing, in the open air just above and to the right of the steel needle's sharp three-edged tip, right above the alarm-clock tiger's two bells: a small green cabbage doll (a plush toy shaped like a baby cabbage) wrapped in a soft baby swaddle blanket, with a cute baby face and a pacifier in its mouth. The needle's sharp point has just poked its bottom (a tiny poke spark, no blood); it leaps up with a startled cry and is about to land bottom-first on the tiger's ringing alarm bells. The cabbage is green, not white, and holds nothing in its hands. Keep everything else exactly as it is. No text, no letters, no numbers.

## ③ 편집 3
Edit this image. Change only two things and add nothing new. First, the rich man in the top hat: the tiger's swirling vinegar has just knocked the red cushion out from under him, so the cushion slides away to the side and he is tumbling backward with his legs in the air and a surprised face; as he falls he squeezes the pink perfume bottle hard, and the big pink perfume cloud bursts out toward the pepper-mask person exactly as now. Second, remove the few tiny spray lines next to the milk carton's atomizer nozzle, so the milk carton's atomizer clearly sprays nothing (it only pours vinegar). Keep everything else exactly as it is: same characters, same positions, same colours, no paper money, no coins. No text, no letters, no numbers anywhere.

## 채택 판 점검 (원본 2752×1536을 좌우 반씩 직접 봄)
- 글자 · 숫자 · 간판 · 지폐 · 동전 없음. 시계판은 눈금만 있음.
- 여덟 피규어 모두 있음. 왼→오른 순서: 乳香 · 沒藥 · 三稜 · (莪朮은 위 공중) · 柴胡 · 香附子 · 靑皮 · 玄胡索.
- 악취 김(초록 → 흰): 우유 팩 위의 초록 김과 물약병 위의 흰 김. 「초록이 흰 김으로 바뀌는」 순간이 한 김 안에 그려지지는 않았다. 우유 팩 쪽은 초록, 물약병 쪽은 흰색으로 나뉘어 있다 → 검수 때 볼 것.
- 색동 호스는 현관 문턱에서 꺾임 표시와 함께 펴지고, 검붉은 물은 옆과 아래로 흘러 문밖으로 나간다(위로 솟지 않음).
- 정거장 상자는 같은 원본의 격자 위에서 읽고, 상자 덧그림으로 확인했다.
