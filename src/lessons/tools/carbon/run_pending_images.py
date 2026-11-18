#!/usr/bin/env python3
"""Carbon v7 남은 과 그림 일괄 생성·판독 스크립트:
.env에 GEMINI_API_KEY를 넣은 뒤 실행하면, 아직 이미지가 없는 과(has_image=false)의
src/lessons/design/<id>/prompt_base.txt를 읽어 tools/gen_image.py -> lesson_helper.py -> tools/blind_read.py(2회) -> build_player.py를 자동 수행한다.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LESSONS = HERE.parents[1]
ROOT = LESSONS.parents[1]
WORK = ROOT.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', nargs='*', help='특정 과 id만 지정 (생략 시 이미지 없는 모든 과)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    targets = []
    for p in sorted((LESSONS / 'l').glob('*.json')):
        lid = p.stem
        if args.ids and lid not in args.ids:
            continue
        webp = ROOT / 'images/lessons' / f'{lid}.webp'
        prompt_file = LESSONS / 'design' / lid / 'prompt_base.txt'
        if not webp.exists() and prompt_file.exists():
            targets.append((lid, prompt_file))

    print(f'대기 중인 그림 생성 대상 과: {len(targets)}개')
    for lid, pf in targets:
        out_png = WORK / 'masters' / lid / 'final.png'
        cmd_gen = [
            sys.executable, str(WORK / 'tools/gen_image.py'),
            '--prompt-file', str(pf),
            '--ref', str(WORK / 'masters/_codes/style_hist-02.png'),
            '--ref', str(WORK / 'masters/_codes/numbers.png'),
            '--out', str(out_png),
            '--webp', str(ROOT / 'images/lessons' / f'{lid}.webp'),
        ]
        cmd_proc = [sys.executable, str(HERE / 'lesson_helper.py'), '--process', lid]
        cmd_r1 = [
            sys.executable, str(WORK / 'tools/blind_read.py'),
            '--image', str(ROOT / 'images/lessons' / f'{lid}.webp'),
            '--key', str(ROOT / 'carbon/keys' / f'{lid}.md'),
            '--out', str(ROOT / 'carbon/blind' / f'{lid}_r1.json'),
        ]
        cmd_r2 = [
            sys.executable, str(WORK / 'tools/blind_read.py'),
            '--image', str(ROOT / 'images/lessons' / f'{lid}.webp'),
            '--key', str(ROOT / 'carbon/keys' / f'{lid}.md'),
            '--out', str(ROOT / 'carbon/blind' / f'{lid}_r2.json'),
        ]
        if args.dry_run:
            print(f'  [DRY-RUN] {lid}: {pf.relative_to(ROOT)}')
            continue
        print(f'>>> Generating & verifying {lid} ...')
        subprocess.run(cmd_gen, check=True)
        subprocess.run(cmd_proc, check=True)
        subprocess.run(cmd_r1, check=True)
        subprocess.run(cmd_r2, check=True)

    if not args.dry_run and targets:
        subprocess.run([sys.executable, str(LESSONS / 'build_player.py')], check=True)


if __name__ == '__main__':
    main()
