"""問診·切診 통합판 s12u03 — 합성본 뒤 PIL 손질 (2026-10-18, 재현용).
   입력: zone_kit compose 결과(2048×1144).  출력: 테두리 정리 + 징검돌 셋 채움 + 살색 맞춤 → zone_kit finish 로 넘김.
   usage: python3 s12u03_post.py comp.png out.png
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')

# 1) 캡처 테두리(위 4행·왼 7열·오른 12열·아래 6행이 검정) 잘라 내고 되늘림
im = im.crop((8, 5, im.width - 12, im.height - 7)).resize((2048, 1144), Image.LANCZOS)

# 2) 징검돌 셋 — Argon 편집이 「셋」을 안 지킨 손목(浮沈 · 虛實)에 기존 돌 하나를 복사해 세 번째를 놓는다
def copy_stone(im, bbox, center):
    x0, y0, x1, y1 = bbox
    patch = im.crop(bbox); w, h = patch.size
    mask = Image.new('L', (w * 4, h * 4), 0)
    ImageDraw.Draw(mask).ellipse((6, 8, w * 4 - 6, h * 4 - 8), fill=255)
    mask = mask.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
    im.paste(patch, (center[0] - w // 2, center[1] - h // 2), mask)

copy_stone(im, (909, 628, 945, 650), (944, 657))      # 浮沈 — 두 돌 사이 아래
copy_stone(im, (1430, 629, 1457, 651), (1460, 667))   # 虛實 — 두 돌 사이 아래 (상자는 홈통 나무 테를 피해 돌만 감싼다 — 1차에 테가 초승달처럼 딸려 왔다)

# 3) 살색 맞춤 — 浮沈·虛實 남자의 살갗이 聾 남자(기준)보다 누렇고 어두워 「黃」으로 샐 위험 → 평균을 기준 쪽으로 60% 당긴다
a = np.asarray(im).astype(float)
def skin_mask(sub):
    # 살색만 — 탁자 나무(어둡고 채도 낮음)·조롱박(주황, R-B 큼)은 빠진다. 마스크는 mask1/mask2.png 로 눈으로 확인했다
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    return (r > 172) & (r - b >= 58) & (r - b <= 100) & (g - b >= 22) & (g - b <= 58) & (r - g >= 22) & (r - g <= 50)
def pull(a, box, ref_mean, k=0.6):
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1]
    m = skin_mask(sub)
    if m.sum() < 200: return
    cur = sub[m].mean(0)
    gain = 1 + k * (ref_mean / cur - 1)
    sub[m] = np.clip(sub[m] * gain, 0, 255)
    print('skin', box, cur.astype(int), '->', sub[m].mean(0).astype(int), 'px', int(m.sum()))
ref = a[380:404, 493:517][skin_mask(a[380:404, 493:517])].mean(0)   # 聾 남자 뺨
print('ref', ref.astype(int))
pull(a, (860, 300, 1010, 470), ref)      # 浮沈 얼굴·목
pull(a, (780, 560, 900, 700), ref)       # 浮沈 왼손(조롱박 x≥900 제외)
pull(a, (975, 560, 1085, 700), ref)      # 浮沈 오른손
pull(a, (1390, 300, 1540, 470), ref)     # 虛實 얼굴·목
pull(a, (1330, 560, 1440, 700), ref)     # 虛實 왼손
pull(a, (1510, 560, 1620, 700), ref)     # 虛實 오른손
pull(a, (840, 760, 1060, 900), ref)      # 浮沈 발
pull(a, (1380, 760, 1600, 900), ref)     # 虛實 발
im = Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
im.save(out)
print('saved', out)
