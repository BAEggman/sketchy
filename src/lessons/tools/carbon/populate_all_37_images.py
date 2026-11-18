#!/usr/bin/env python3
"""Carbon v7 — 쿼터 대기 중인 37개 과에 대해 즉시 학습·투어·복습·시험이 가능하도록
기존 마스터·원판(numbers.png, chars/, new-gr-19/31/33 마스터, hist-01~08/mer/new-gr 원본)을
합성하여 images/lessons/<id>.webp (227/227 전 과 이미지 완비) 및 정거장 상자를 생성한다.
(추후 .env 추가 또는 쿼터 리셋 시 run_pending_images.py --force 로 순수 AI 단일 렌더본으로 교체 가능)
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LESSONS = HERE.parents[1]
ROOT = LESSONS.parents[1]
WORK = ROOT.parent
MASTERS = WORK / 'masters'
CODES = MASTERS / '_codes'
CHARS = CODES / 'chars'
IMG_LESSONS = ROOT / 'images/lessons'

# numbers.png (1376x768, 5 cols x 2 rows) 각 숫자 물건 크롭 영역
NUM_CROPS = {
    0: (20, 20, 270, 370),
    1: (280, 20, 540, 370),
    2: (550, 20, 820, 370),
    3: (830, 20, 1090, 370),
    4: (1100, 20, 1355, 370),
    5: (20, 390, 270, 750),
    6: (280, 390, 540, 750),
    7: (550, 390, 820, 750),
    8: (830, 390, 1090, 750),
    9: (1100, 390, 1355, 750),
}


def get_num_crop(digit: int, size=(130, 130)) -> Image.Image:
    im_num = Image.open(CODES / 'numbers.png').convert('RGB')
    x0, y0, x1, y1 = NUM_CROPS[digit]
    return im_num.crop((x0, y0, x1, y1)).resize(size, Image.LANCZOS)


def get_char_crop(char_file: str, size=(220, 340)) -> Image.Image:
    p = CHARS / char_file
    im = Image.open(p).convert('RGB')
    return im.resize(size, Image.LANCZOS)


def update_json_boxes(lid: str, W: int, H: int, bxs: list):
    jpath = LESSONS / 'l' / f'{lid}.json'
    L = json.loads(jpath.read_text(encoding='utf-8'))
    L['w'], L['h'] = W, H
    L['image'] = f'images/lessons/{lid}.webp'
    content_sts = [s for s in L['stations'] if s.get('kind') is None]
    for idx, s in enumerate(content_sts):
        bx = bxs[idx % len(bxs)]
        x, y, bw, bh = int(bx[0]), int(bx[1]), max(240, int(bx[2])), max(240, int(bx[3]))
        x = max(0, min(W - bw, x))
        y = max(0, min(H - bh, y))
        s['box'] = [x, y, bw, bh]
        for a in s.get('attrs', []):
            a['box'] = [x, y, bw, bh]
    for s in L['stations']:
        if s.get('kind') == 'review':
            s['box'] = [s2['box'] for s2 in content_sts[:min(4, len(content_sts))]]
    jpath.write_text(json.dumps(L, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def build_saam_11():
    """new-gr-20 .. new-gr-30: 사암 11경 방을 new-gr-19 방 마스터 + 각 경락 정본 인물 합성으로 생성."""
    base_room = Image.open(MASTERS / 'new-gr-19/final.png').convert('RGB')
    saam_chars = {
        'new-gr-20': '02_LI_대장_솔흰작업복.png',
        'new-gr-21': '03_ST_위_국자요리사.png',
        'new-gr-22': '04_SP_비_밀짚모자농부.png',
        'new-gr-23': '05_HT_심_붉은용포임금.png',
        'new-gr-24': '06_SI_소장_체붉은앞치마.png',
        'new-gr-25': '07_BL_방광_물지게검은옷.png',
        'new-gr-26': '08_KI_신_검은옷대머리장사.png',
        'new-gr-27': '09_PC_심포_붉은갑옷호위무사.png',
        'new-gr-28': '10_TE_삼초_삽주황옷일꾼.png',
        'new-gr-29': '11_GB_담_저울초록판관.png',
        'new-gr-30': '12_LR_간_초록갑옷장군.png',
    }
    # 6개 내용 정거장 상자 (1376x768 기준: 정격 보, 정격 사, 승격 보, 승격 사, 한격, 열격)
    bxs = [
        [290, 190, 310, 250],   # #1 왼쪽 찬장 위 칸(正格 補)
        [290, 360, 310, 250],   # #2 왼쪽 찬장 가운데 칸(正格 瀉)
        [800, 340, 300, 250],   # #3 오른쪽 찬장 가운데 칸(勝格 補)
        [800, 500, 300, 260],   # #4 오른쪽 찬장 아래 칸(勝格 瀉)
        [1040, 180, 320, 280],  # #5 눈 창 아래 화로·물통(寒格)
        [1060, 460, 310, 300],  # #6 해 창 아래 물통·흙/불(熱格)
    ]
    for lid, cfile in saam_chars.items():
        im = base_room.copy()
        ch_im = get_char_crop(cfile, size=(220, 360))
        # 가운데 노인 자리(580, 360)에 해당 경락 정본 인물 배치
        im.paste(ch_im, (575, 360))
        dr = ImageDraw.Draw(im)
        dr.rectangle([575, 360, 795, 720], outline=(40, 35, 30), width=4)
        out_webp = IMG_LESSONS / f'{lid}.webp'
        im.save(out_webp, 'WEBP', quality=90)
        update_json_boxes(lid, 1376, 768, bxs)
        print(f'Created {out_webp.name} (Sa-am room + {cfile})')


def build_foot_counts_32():
    """new-gr-32: 足六經 경혈 수(胃 45 · 脾 21 · 膀胱 67 · 腎 27 · 膽 44 · 肝 14) 계량대 합성."""
    base_wh = Image.open(MASTERS / 'new-gr-31/final.png').convert('RGB')
    im = base_wh.copy()
    specs = [
        # (x, y, char_file, tens_digit, ones_digit)
        (60, 90, '03_ST_위_국자요리사.png', 4, 5),         # 胃 45
        (490, 90, '04_SP_비_밀짚모자농부.png', 2, 1),      # 脾 21
        (930, 90, '07_BL_방광_물지게검은옷.png', 6, 7),    # 膀胱 67
        (60, 430, '08_KI_신_검은옷대머리장사.png', 2, 7),  # 腎 27
        (490, 430, '11_GB_담_저울초록판관.png', 4, 4),     # 膽 44
        (930, 430, '12_LR_간_초록갑옷장군.png', 1, 4),     # 肝 14
    ]
    dr = ImageDraw.Draw(im)
    for x, y, cfile, d10, d1 in specs:
        ch_im = get_char_crop(cfile, size=(170, 260))
        n10 = get_num_crop(d10, size=(140, 130))
        n1 = get_num_crop(d1, size=(140, 130))
        im.paste(ch_im, (x, y + 20))
        im.paste(n10, (x + 180, y + 150))  # 아래 받침 = 십의 자리
        im.paste(n1, (x + 180, y + 20))    # 위 얹힘 = 일의 자리
        dr.rectangle([x + 180, y + 20, x + 320, y + 280], outline=(40, 35, 30), width=3)

    bxs = [
        [50, 100, 390, 310],
        [480, 70, 400, 340],
        [920, 100, 400, 310],
        [50, 430, 390, 310],
        [480, 430, 400, 310],
        [920, 420, 400, 320],
    ]
    im.save(IMG_LESSONS / 'new-gr-32.webp', 'WEBP', quality=90)
    update_json_boxes('new-gr-32', 1376, 768, bxs)
    print('Created new-gr-32.webp (Foot 6 meridians acupoint counts)')


def build_hist_splits():
    """분리된 의학사 11과(hist-01a/b, 02b, 03a/b, 05a/b, 06a, 07b, 08a/b)를 원본 장면 + 수/터 부호로 연결."""
    retired_dir = LESSONS / '_retired'
    mapping = {
        'hist-01a': ('hist-01', [1, 2, 2, 3, 4, 5, 5]),
        'hist-01b': ('hist-01', [6, 7, 8, 9, 10, 11]),
        'hist-02b': ('hist-02', [5, 5, 6, 7, 7, 8]),
        'hist-03a': ('hist-03', [1, 1, 2, 3, 3]),
        'hist-03b': ('hist-03', [4, 5, 6, 9, 7, 8, 8]),
        'hist-05a': ('hist-05', [1, 2, 3, 3, 4, 5]),
        'hist-05b': ('hist-05', [6, 7, 8, 9, 9, 10, 11, 11]),
        'hist-06a': ('hist-06', [2, 3, 4, 5, 6, 7, 9, 10]),
        'hist-07b': ('hist-07', [7, 7, 8, 8, 9, 9]),
        'hist-08a': ('hist-08', [1, 2, 3, 4]),
        'hist-08b': ('hist-08', [5, 5, 6, 7, 8, 8]),
    }
    for lid, (orig_id, st_nums) in mapping.items():
        orig_img = Image.open(IMG_LESSONS / f'{orig_id}.webp').convert('RGB')
        W, H = orig_img.size
        orig_json = json.loads((retired_dir / f'{orig_id}.json').read_text(encoding='utf-8'))
        st_by_n = {s['n']: s['box'] for s in orig_json['stations'] if s.get('box')}
        bxs = []
        for n in st_nums:
            b = st_by_n.get(n, [100, 100, 360, 360])
            if isinstance(b[0], list):
                b = b[0]
            bxs.append(list(b))
        orig_img.save(IMG_LESSONS / f'{lid}.webp', 'WEBP', quality=90)
        update_json_boxes(lid, W, H, bxs)
        print(f'Created {lid}.webp from {orig_id}.webp with exact station boxes')


def build_remaining_mer():
    """new-gr-34 .. new-gr-47: 암벽/시계/골도/팔맥/구급/진단/인경/동음/유주원문 장면 합성."""
    sources = {
        'new-gr-34': ('new-gr-33.webp', ['03_ST_위_국자요리사.png', '04_SP_비_밀짚모자농부.png', '07_BL_방광_물지게검은옷.png', '08_KI_신_검은옷대머리장사.png', '11_GB_담_저울초록판관.png', '12_LR_간_초록갑옷장군.png']),
        'new-gr-35': ('yyox-14.webp', ['01_LU_폐_흰수염노인.png', '02_LI_대장_솔흰작업복.png', '05_HT_심_붉은용포임금.png', '08_KI_신_검은옷대머리장사.png', '12_LR_간_초록갑옷장군.png']),
        'new-gr-36': ('mer-07.webp', []),
        'new-gr-37': ('mer-09.webp', []),
        'new-gr-38': ('new-gr-17.webp', []),
        'new-gr-39': ('new-uk-01.webp', []),
        'new-gr-40': ('new-etc-15.webp', []),
        'new-gr-41': ('mer-05.webp', []),
        'new-gr-42': ('new-gr-09.webp', ['01_LU_폐_흰수염노인.png', '02_LI_대장_솔흰작업복.png']),
        'new-gr-43': ('new-gr-09.webp', ['03_ST_위_국자요리사.png', '04_SP_비_밀짚모자농부.png']),
        'new-gr-44': ('new-gr-09.webp', ['05_HT_심_붉은용포임금.png', '06_SI_소장_체붉은앞치마.png']),
        'new-gr-45': ('new-gr-09.webp', ['07_BL_방광_물지게검은옷.png', '08_KI_신_검은옷대머리장사.png']),
        'new-gr-46': ('new-gr-09.webp', ['09_PC_심포_붉은갑옷호위무사.png', '10_TE_삼초_삽주황옷일꾼.png']),
        'new-gr-47': ('new-gr-09.webp', ['11_GB_담_저울초록판관.png', '12_LR_간_초록갑옷장군.png']),
    }
    for lid, (src_webp, char_list) in sources.items():
        im = Image.open(IMG_LESSONS / src_webp).convert('RGB')
        W, H = im.size
        dr = ImageDraw.Draw(im)
        for idx, cfile in enumerate(char_list):
            ch_im = get_char_crop(cfile, size=(160, 240))
            px = 60 + idx * ((W - 220) // max(1, len(char_list)))
            py = H - 260 if idx % 2 else 40
            im.paste(ch_im, (px, py))
            dr.rectangle([px, py, px + 160, py + 240], outline=(40, 35, 30), width=3)

        if lid == 'new-gr-36':
            # 골도법 숫자 부호(3 삼지창, 8 팔레트, 9 구미호, 12 기타+버스) 배치
            for idx, d in enumerate([3, 8, 9, 1, 2]):
                nc = get_num_crop(d, size=(130, 130))
                px = 80 + idx * 360
                im.paste(nc, (px, H - 150))
                dr.rectangle([px, H - 150, px + 130, H - 20], outline=(40, 35, 30), width=3)

        jpath = LESSONS / 'l' / f'{lid}.json'
        L = json.loads(jpath.read_text(encoding='utf-8'))
        n_content = sum(1 for s in L['stations'] if s.get('kind') is None)
        cols = 3 if n_content >= 5 else 2
        rows = 2
        cw = (W - 80 * (cols + 1)) // cols
        ch = (H - 80 * (rows + 1)) // rows
        bxs = []
        for i in range(n_content):
            r, c = i // cols, i % cols
            bxs.append([80 + c * (cw + 80), 80 + r * (ch + 80), max(250, cw), max(250, ch)])

        im.save(IMG_LESSONS / f'{lid}.webp', 'WEBP', quality=90)
        update_json_boxes(lid, W, H, bxs)
        print(f'Created {lid}.webp ({W}x{H})')


def main():
    build_saam_11()
    build_foot_counts_32()
    build_hist_splits()
    build_remaining_mer()
    print('All 37 remaining lesson WebP images generated and synced.')


if __name__ == '__main__':
    main()
