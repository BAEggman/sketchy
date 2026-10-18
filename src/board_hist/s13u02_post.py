"""六經 ② 三陰 통합판 s13u02 — 합성본 뒤 PIL 손질 (2026-10-18, 재현용).
   厥陰 방 선반의 모래시계: 「위 절반은 어둡고 아래 절반은 밝다」(厥熱勝復)가 바탕에서 보통 모래시계로 나와,
   위쪽 유리구 안을 어둡게 칠한다(유리 테두리·받침은 그대로).
   usage: python3 s13u02_post.py comp.png out.png
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(float)

# 위쪽 유리구 안쪽(합성본 2048×1144 좌표) — hg.png(crop 1440,240 ×3)로 눈으로 잡은 다각형
poly = [(1536, 300), (1577, 300), (1579, 312), (1574, 328), (1563, 341), (1557, 348), (1553, 348), (1546, 341), (1538, 328), (1534, 312)]
mask = Image.new('L', im.size, 0)
ImageDraw.Draw(mask).polygon(poly, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(0.7))
m = np.asarray(mask).astype(float) / 255.0
# 밝은 유리 안쪽만 어둡게(검은 윤곽선은 그대로) — 밝기 > 90 인 픽셀을 0.32배 + 푸른 기운
bright = a.mean(2) > 90
k = m * bright
dark = a * 0.32 + np.array([8, 8, 14])
a = a * (1 - k[..., None]) + dark * k[..., None]
Image.fromarray(np.clip(a, 0, 255).astype('uint8')).save(out)
print('saved', out)
