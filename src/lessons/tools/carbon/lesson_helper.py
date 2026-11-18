#!/usr/bin/env python3
"""Carbon v7 과 제작 보조 도구:
1. --init-refs: 화풍 참조(hist-02, mer-06, mer-11) 및 12경락 정본 인물 참조 그림을 masters/_codes/에 PNG로 저장
2. --process <id>:
   - masters/<id>/final.png → sketchy/images/lessons/<id>.webp (q90, >2MB면 q85, 크기 유지)
   - masters/<id>/final.png → sketchy/carbon/blind/raw/<id>.png (판독용 복사본)
   - src/lessons/l/<id>.json에 make_tts 적용
   - 정거장 상자 확인 그림 sketchy/carbon/boxes/<id>.png 생성 및 짧은 변 >= 240px 검사
   - 단서 그림 sketchy/images/cues/<id>/<n>.webp 생성 (확대 금지, 긴 변 800px 이하)
"""
import argparse
import json
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
LESSONS_DIR = HERE.parents[1]           # sketchy/src/lessons
ROOT = LESSONS_DIR.parents[1]           # sketchy/
WORK = ROOT.parent                      # sketchy_carbon/
MASTERS = WORK / 'masters'
CARBON = ROOT / 'carbon'

sys.path.insert(0, str(HERE))
import make_tts


def init_refs():
    codes_dir = MASTERS / '_codes'
    chars_dir = codes_dir / 'chars'
    chars_dir.mkdir(parents=True, exist_ok=True)

    for name in ('hist-02', 'mer-06', 'mer-11', 'mer-12'):
        src = ROOT / 'images/lessons' / f'{name}.webp'
        if src.exists():
            im = Image.open(src).convert('RGB')
            im.save(codes_dir / f'style_{name}.png')

    # mer-06에서 12경락 정본 인물 크롭
    mer06_path = ROOT / 'images/lessons/mer-06.webp'
    mer06_json = LESSONS_DIR / 'l/mer-06.json'
    if mer06_path.exists() and mer06_json.exists():
        im = Image.open(mer06_path).convert('RGB')
        data = json.loads(mer06_json.read_text(encoding='utf-8'))
        names = {
            1: '01_LU_폐_흰수염노인',
            2: '02_LI_대장_솔흰작업복',
            3: '03_ST_위_국자요리사',
            4: '04_SP_비_밀짚모자농부',
            5: '05_HT_심_붉은용포임금',
            6: '06_SI_소장_체붉은앞치마',
            7: '07_BL_방광_물지게검은옷',
            8: '08_KI_신_검은옷대머리장사',
            9: '09_PC_심포_붉은갑옷호위무사',
            10: '10_TE_삼초_삽주황옷일꾼',
            11: '11_GB_담_저울초록판관',
            12: '12_LR_간_초록갑옷장군',
        }
        for st in data['stations']:
            n = st.get('n')
            if n in names and st.get('box'):
                x, y, w, h = st['box']
                crop = im.crop((x, y, x + w, y + h))
                crop.save(chars_dir / f'{names[n]}.png')
    print(f'Reference PNGs initialized in {codes_dir}')


def get_boxes(st):
    b = st.get('box')
    if not b:
        return []
    if isinstance(b[0], (int, float)):
        return [b]
    return b


def process_lesson(lid: str):
    master_png = MASTERS / lid / 'final.png'
    if not master_png.exists():
        sys.exit(f'오류: {master_png} 파일이 없습니다')

    im = Image.open(master_png).convert('RGB')
    W, H = im.size

    # 1. WebP 저장 (q90, 2MB 초과 시 q85)
    webp_out = ROOT / 'images/lessons' / f'{lid}.webp'
    webp_out.parent.mkdir(parents=True, exist_ok=True)
    im.save(webp_out, 'WEBP', quality=90)
    if webp_out.stat().st_size > 2 * 1024 * 1024:
        im.save(webp_out, 'WEBP', quality=85)

    # 2. 판독용 PNG 복사
    raw_dir = CARBON / 'blind/raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(master_png, raw_dir / f'{lid}.png')

    # 3. JSON 읽기 및 w, h, tts 갱신
    jpath = LESSONS_DIR / 'l' / f'{lid}.json'
    if not jpath.exists():
        sys.exit(f'오류: {jpath} 파일이 없습니다')

    L = json.loads(jpath.read_text(encoding='utf-8'))
    L['w'] = W
    L['h'] = H
    L['image'] = f'images/lessons/{lid}.webp'
    for st in L.get('stations', []):
        if st.get('say'):
            st['tts'] = make_tts.convert_text_to_tts(st['say'])[0]
    jpath.write_text(json.dumps(L, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    # 4. 상자 그림 생성 및 240px 검사
    box_im = im.copy()
    draw = ImageDraw.Draw(box_im)
    short_errors = []
    colors = [
        (230, 57, 70), (42, 157, 143), (233, 196, 106), (244, 162, 97),
        (38, 70, 83), (155, 93, 229), (241, 91, 181), (0, 187, 249),
        (0, 245, 212), (254, 228, 64), (131, 56, 236), (255, 0, 110)
    ]

    cues_dir = ROOT / 'images/cues' / lid
    cues_dir.mkdir(parents=True, exist_ok=True)

    for st in L.get('stations', []):
        n = st.get('n', 0)
        kind = st.get('kind')
        bs = get_boxes(st)
        col = colors[n % len(colors)]
        for idx, (x, y, w, h) in enumerate(bs):
            if kind is None:
                if min(w, h) < 240:
                    short_errors.append(f'정거장 #{n}: 상자 [{x},{y},{w},{h}] 짧은 변 {min(w,h)}px < 240px')
                if x < 0 or y < 0 or x + w > W or y + h > H:
                    short_errors.append(f'정거장 #{n}: 상자 [{x},{y},{w},{h}]가 이미지({W}x{H}) 범위 초과')
            draw.rectangle([x, y, x + w, y + h], outline=col, width=4)
            label = f'#{n} ({w}x{h})' if len(bs) == 1 else f'#{n}.{idx+1} ({w}x{h})'
            draw.rectangle([x, max(0, y - 22), x + len(label) * 8 + 8, max(22, y)], fill=col)
            draw.text((x + 4, max(0, y - 18)), label, fill=(255, 255, 255))

        # 단서 그림 생성 (내용 정거장만, 확대 금지, 긴 변 800 이하)
        if kind is None and bs:
            x0 = min(b[0] for b in bs)
            y0 = min(b[1] for b in bs)
            x1 = max(b[0] + b[2] for b in bs)
            y1 = max(b[1] + b[3] for b in bs)
            crop = im.crop((max(0, x0), max(0, y0), min(W, x1), min(H, y1)))
            cw, ch = crop.size
            if max(cw, ch) > 800:
                scale = 800.0 / max(cw, ch)
                crop = crop.resize((int(round(cw * scale)), int(round(ch * scale))), Image.LANCZOS)
            crop.save(cues_dir / f'{n}.webp', 'WEBP', quality=90)

        # attrs 상자 점선/얇은 선 표시
        for a in st.get('attrs', []) or []:
            ab = a.get('box')
            if ab:
                ax, ay, aw, ah = ab
                draw.rectangle([ax, ay, ax + aw, ay + ah], outline=(255, 255, 255), width=2)

    boxes_out = CARBON / 'boxes' / f'{lid}.png'
    boxes_out.parent.mkdir(parents=True, exist_ok=True)
    box_im.save(boxes_out)

    print(f'[{lid}] processed: {W}x{H}, webp={webp_out.stat().st_size // 1024}KB, boxes={boxes_out}')
    if short_errors:
        for e in short_errors:
            print('  [BOX ERROR]', e)
        sys.exit(1)
    else:
        print('  [BOX OK] 모든 내용 정거장 상자 짧은 변 >= 240px 및 범위 내')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--init-refs', action='store_true')
    ap.add_argument('--process', type=str)
    args = ap.parse_args()
    if args.init_refs:
        init_refs()
    if args.process:
        process_lesson(args.process)
