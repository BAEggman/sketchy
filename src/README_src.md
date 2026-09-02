# src — Sketchy 소스 트리

## 왜 저장소에 넣었나

2026-08-29 이후 클라우드 컨테이너가 회수되어 **작업 트리 전체가 사라졌다.**
그때까지 저장소에는 산출물인 `index.html` 하나만 올려 두어서, 원본이 컨테이너에만 있었다.
**같은 일이 또 나지 않게 소스를 여기 둔다.**

## 사라졌을 때 되살리는 법 (2026-09-02 개정 — 훨씬 간단해졌다)

```bash
git clone https://github.com/BAEggman/sketchy.git <작업경로>
cd <작업경로>
cp -r src/* .                 # panels/ · build_local.py · coverage/ 를 작업 위치로
EXTERNAL=1 python3 build_local.py     # index.html 재생성 (0.58 MB)
```

**그림은 이제 저장소의 `images/` 에 파일 그대로 있다.** 클론하면 원본 110장(8.2 MB)이
같이 딸려 온다 — 뽑아낼 것도, 되돌릴 것도 없다.

### 이전 방식(참고용)

2026-09-02 이전에는 그림이 `index.html` 안에 base64로 박혀 있었고,
`coverage/recover_from_html.py` 가 그걸 뽑아 `images/` 와 `library.json` 을 되살렸다.
그 복구기는 남겨 둔다 — **옛 판본의 index.html 하나만 손에 있을 때** 여전히 쓸 수 있고,
화질 복원(아래)이 바로 이 복구기로 옛 판본들을 훑어서 이루어졌다.

## 빌드 두 갈래 — EXTERNAL 모드가 기본이다

| | `EXTERNAL=1 python3 build_local.py` (**현재 배포판**) | `python3 build_local.py` (단일 파일) |
|---|---|---|
| 그림 | `images/*.webp` 링크 | base64로 index.html 안에 |
| index.html | 0.58 MB | 9.7 MB |
| 화질 | **원본 그대로, 재압축 0** | 예산에 맞춰 재압축 |
| 배포 | index.html + images/ 둘 다 올려야 | 파일 하나만 올리면 됨 |

단일 파일 모드가 화질을 깎았던 이유: GitHub 웹 업로드가 **한 번에 10 MB**가 상한이고
(`file_upload` 도구도 같은 10 MB), base64는 원본 바이트를 4/3배로 부풀린다.
되살린 원본 8.2 MB는 base64로 11.3 MB가 되어 다리를 못 건넌다.
그래서 단일 파일로는 **원본 화질을 실을 수 없다** — 이것이 EXTERNAL 모드로 간 이유다.

## 화질 복원 (2026-09-02)

패널이 쌓이면서 예산 사다리가 화질을 조금씩 깎아 왔다. 되돌린 방법:

1. `coverage/restore_quality.py` — `index.html` 의 **git 이력 15판본**을 모두 훑어
   패널마다 가장 해상도 높고 큰 판본을 고른다.
2. 같은 그림인지 가리는 문턱은 `coverage/local_diff_check.py` 의
   **국소 블록 최대차**(256px를 16×16 블록으로, 밝기·대비 정규화 후 블록별 최대 차이).
   전역 상관계수(≥0.92)는 **소품 몇 개만 고친 재작도를 못 걸러냈다** — 실제로 다섯 판을
   옛 판본으로 되돌릴 뻔했다. 국소 블록차는 d 5~10 구간이 텅 비어 깨끗하게 갈린다(문턱 d≤8).
3. 결과 — **80판이 더 좋은 판본으로 올라갔다.**
   해상도 분포 `{1024: 55, 1250: 17, 1100: 18, 1150: 13, 980: 6, 1032: 1}`

배포 검증(2026-09-02): 라이브 110장을 모두 받아 SHA-256을 매긴 뒤 로컬 원본과
집계 해시를 맞춰 **완전 일치**(`0c9431e9…2728`). 깨진 그림 0.

## 무엇이 들어 있나

| 경로 | 무엇 |
|---|---|
| `panels/library.json` | 패널 110 · rows 586 · 도해 문항 335. **이 프로젝트의 본체** |
| `panels/scenes.json` | 장면 21개의 제목과 소속 패널, 상단 칩 |
| `panels/_css.txt` · `_script.txt` | 허브의 CSS·스크립트 원본 |
| `build_local.py` | `library.json` + `images/` → `index.html` (EXTERNAL 모드 포함) |
| `coverage/glyph_dict.py` | **글자 사전 104자** — 이 그림책의 어휘 그 자체 |
| `coverage/recover_from_html.py` | 옛 판본 index.html 에서 트리를 되살리는 복구기 |
| `coverage/restore_quality.py` · `local_diff_check.py` · `best_images.py` | 화질 복원 도구 |
| `coverage/quality_restore.json` · `local_diff.json` · `panel_redraw_dates.json` | 화질 복원 판정 장부 |
| `coverage/rule_citations.json` | library.json 이 규칙을 인용한 문장 541개 — RULES 복구의 근거 |
| `RULES_복구부록.md` | 규칙 84~131(복구본) · 146~166 |
| `coverage/blind4_*` · `blind5_*` · `blind6_*` | 블라인드 판독 4·5·6차 — 질문지 · 판정 장부 · 판독 기록 · 낳은 규칙 |
| `coverage/redraw5_설계.md` · `patch_redraw5.py` | 재작도 5차(s14p03·s14p08·s20p08·s18p10) 설계와 데이터 반영 |

## 저장소 뿌리에 있는 것

| 경로 | 무엇 |
|---|---|
| `index.html` | 허브 산출물 (EXTERNAL 빌드, 0.58 MB) |
| `images/` | **그림 110장, 원본 해상도 그대로 (8.2 MB)** |

## 여기 없는 것

- **`RULES.md` 본체(규칙 0~83 · §4 · §5 · §6 · §7)** — 프로젝트 문서
  `claude/Sketchy_RULES_최신본.md`(2026-08-15)에 있다. 복구 부록과 함께 읽는다.
- **`quiz.py` · `verify_hub.py` · `count_bridge.py` · `gapfill.py` · `rule_index.py` · `CANON.md`**
  — 컨테이너와 함께 사라졌다. 아직 되살리지 못했다.

## 글자 사전 (`coverage/glyph_dict.py`)

**104자.** 등급별 `{'확정': 35, '갈림': 19, '신설': 31, '성문화': 10, '포기': 9}`.
출처는 세 갈래로 표시한다 — `[원문]`(전사) · `[복구]`(library.json 인용에서 되살림) · `[유실]`.

기억하던 원본 계수 99와 5 어긋난다. 덮지 않고 파일 안 주석에 남겼다.
인용 검산이 **오미(酸·苦·甘·辛·鹹) 다섯 자가 통째로 빠져 있던 것**을 잡아냈다 —
느슨한 `X = ` 정규식이 산문까지 물어 헛짚음이 많길래 인용 전용 패턴으로 좁혔더니
진짜 누락 하나(苦)가 드러났고, 그 실마리로 다섯 자를 모두 찾았다.

> **규칙 165** — 판이 쓰는 문법은 반드시 §5에 등재한다.
> 왜(why) 문장에만 적힌 문법은 독자에게 **없는 문법**이다.
> s18p10이 여섯 번 眞假로 오독된 근본 원인이 이것이었고,
> `補-b`(그릇에 가득) · `瀉-b`(빈 그릇+흘러넘침) · `병표지` · `八卦`를 등재하자
> 판 넷이 그 자리에서 ✓로 돌아섰다.
