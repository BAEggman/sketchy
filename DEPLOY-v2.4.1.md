# v2.4.1 공개 배포 및 롤백 (2026-11-06)

기존 GitHub Pages 사이트에 음양오행 보완판과 팔괘 방위 기억방을 함께 반영한다.

- 허브: https://baeggman.github.io/sketchy/
- 음양오행 보완 시작: https://baeggman.github.io/sketchy/#s09x01
- 팔괘 방위 기억방: https://baeggman.github.io/sketchy/bagua.html
- 배포 원본: `main` 브랜치의 루트. GitHub Pages가 업데이트를 빌드한다.
- 공개 배포 태그: `v2.4.1-public-20261106`.

## 복원 기준

배포 직전 공개 버전은 v2.3.1, 커밋 `bd0e22619d976e1b1d529aed60a8da31ba29a816`이다.
보존 태그 `backup/public-before-v2.4.1-20261106`을 GitHub에도 저장한다.
이는 음양오행·팔괘 보완 이전이며, 기존 의도된 말장난 설명과 한글 독음을 포함한다.

로컬에도 `sketchy-backups/v2.3.1-before-coverage-20261106/`의 ZIP·Git bundle·체크섬 장부가 있다.
v2.4와 v2.4.1의 중간 태그도 함께 보존한다.

## 공개 사이트 전체를 직전 버전으로 되돌리기

작업 중인 변경을 먼저 저장한다. 다음 명령은 이력을 삭제하지 않고 배포 변경을 취소하는 새 커밋을 만든다.

```bash
git fetch origin --tags
git switch main
git pull --ff-only origin main
git revert --no-commit backup/public-before-v2.4.1-20261106..v2.4.1-public-20261106
git commit -m "Roll back public v2.4.1 to v2.3.1"
git push origin main
```

이후 GitHub Pages 빌드 완료와 공개 허브의 v2.3.1 표시를 확인한다.
나중에 다른 변경이 추가되어 충돌이 나면 해당 변경을 함께 검토하고 해결한다. 강제 푸시는 사용하지 않는다.

과거 파일만 확인하려면 `git switch --detach backup/public-before-v2.4.1-20261106`을 사용한다.
이 명령만으로 공개 사이트가 변경되지는 않는다.

## 배포 전 확인

기존 패널·이미지 보존, 새 한자 독음, 21개 추가 도해, 팔괘 16개 방위 및 괘의 획,
회상 문항과 빈 방위판 채점 검사를 통과한 산출물을 배포한다.
OneDrive 원본 문서와 로컬 점검 보고서는 포함하지 않는다.
