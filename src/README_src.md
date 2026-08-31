# src — Sketchy 소스 트리

## 왜 저장소에 넣었나

2026-08-29 이후 클라우드 컨테이너가 회수되어 **작업 트리 전체가 사라졌다.**
그때까지 저장소에는 산출물인 `index.html` 하나만 올려 두어서, 원본이 컨테이너에만 있었다.
**같은 일이 또 나지 않게 소스를 여기 둔다.**

## 사라졌을 때 되살리는 법

```bash
git clone https://github.com/BAEggman/sketchy.git
cd sketchy
python3 src/coverage/recover_from_html.py index.html <작업경로>   # 그림 110장 + library.json 복원
cp -r src/* <작업경로>/                                          # 나머지 소스
cd <작업경로> && python3 build_local.py                            # index.html 재생성
```
`recover_from_html.py` 는 `index.html` 하나만 있으면 **그림 110장과 library.json(패널 110 · rows 586 · 함정 165 · 도해 문항 335)을 손실 없이** 되돌린다.
왕복 검사 통과 — 되살린 데이터로 다시 빌드해 되읽으면 어긋난 항목 0.

## 무엇이 들어 있나

| 경로 | 무엇 |
|---|---|
| `panels/library.json` | 패널 110 · rows 586 · 도해 문항 335. **이 프로젝트의 본체** |
| `panels/scenes.json` | 장면 21개의 제목과 소속 패널, 상단 칩 |
| `panels/_css.txt` · `_script.txt` | 허브의 CSS·스크립트 원본 |
| `build_local.py` | `library.json` + `images/` → `index.html` |
| `coverage/recover_from_html.py` | **index.html 에서 트리를 되살리는 복구기** |
| `coverage/rule_citations.json` | library.json 이 규칙을 인용한 문장 541개 — RULES 복구의 근거 |
| `RULES_복구부록.md` | 규칙 84~131(복구본) · 146~163(온전) |
| `coverage/blind4_*` | 2026-08-31 블라인드 판독 4차 — 질문지 · 판정 장부 · 낳은 규칙 |

## 여기 없는 것

- **`images/`** — `recover_from_html.py` 가 `index.html` 에서 뽑으므로 중복 저장하지 않는다(8 MB 절약).
- **`RULES.md` 본체(규칙 0~83 · §4 · §5 · §6 · §7)** — 프로젝트 문서 `claude/Sketchy_RULES_최신본.md`(2026-08-15)에 있다. 복구 부록과 함께 읽는다.
- **`coverage/glyph_dict.py`(글자 사전)** — 재건 완료(2026-08-31). 총 100자: 원문 전사 63 + 8/29 신설 15 + 포기 7 + 인용 복구 15(오미 五味 포함). library.json 인용 검산 통과. 기억한 원본 계수 99와 1 어긋남은 파일 안 유실 주석에 기록.
- **`quiz.py` · `verify_hub.py` · `count_bridge.py` · `gapfill.py`** — 컨테이너와 함께 사라졌다. 되살리는 중.
