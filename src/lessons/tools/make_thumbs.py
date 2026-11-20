#!/usr/bin/env python3
"""과 그림 썸네일 — images/lessons/<id>.webp → images/thumbs/<id>.webp (가로 240, 세로는 비율대로).

    python3 src/lessons/tools/make_thumbs.py          # 없거나 원본보다 오래된 것만
    python3 src/lessons/tools/make_thumbs.py --all    # 전부 다시
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC, DST, W = ROOT / 'images/lessons', ROOT / 'images/thumbs', 240


def main():
    force = '--all' in sys.argv
    DST.mkdir(parents=True, exist_ok=True)
    ids = sorted(p.stem for p in (ROOT / 'src/lessons/l').glob('*.json'))
    made = skipped = missing = 0
    for i in ids:
        s, d = SRC / f'{i}.webp', DST / f'{i}.webp'
        if not s.is_file():
            missing += 1
            continue
        if d.is_file() and not force and d.stat().st_mtime >= s.stat().st_mtime:
            skipped += 1
            continue
        im = Image.open(s).convert('RGB')
        h = round(im.height * W / im.width)
        im.resize((W, h), Image.LANCZOS).save(d, 'WEBP', quality=72, method=6)
        made += 1
    print(f'thumbs: made {made} · kept {skipped} · no image {missing} · total {len(ids)}')


if __name__ == '__main__':
    main()
