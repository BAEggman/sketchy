"""本草 ① 補·溫 통합판 s14u01 — 합성본 뒤 PIL 손질 (2026-10-22, 재현용).
   炙黃芪(꿀 발라 구운 뿌리)가 검붉은 광택으로 나와 사전 地黃(검붉은 뿌리 조각)과 충돌 →
   그 뿌리 안쪽(타원 마스크)의 색상만 황토빛으로 돌린다(HSV: 색상을 꿀빛 32° 로, 채도 유지, 명도 +). 윤곽선은 그대로.
   usage: python3 s14u01_post.py comp.png out.png
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
W, H = im.size
# 뿌리만 감싸는 타원(합성본 2048×1144 좌표) — 바지(y<600)·숟가락(x>1930)은 밖
mask = Image.new('L', (W, H), 0)
ImageDraw.Draw(mask).ellipse((1776, 606, 1958, 702), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1.2))
m = np.asarray(mask).astype(float) / 255.0
hsv = np.asarray(im.convert('HSV')).astype(float)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
# 검붉은 색(색상 0~20 또는 230~255, 채도 > 60)만 대상 — 흰 하이라이트·검은 윤곽은 제외
red = ((h < 22) | (h > 228)) & (s > 90) & (v > 40) & (v < 205)   # 채도 낮은 탁자 나무·흰 하이라이트는 제외(흰 테 방지)
k = m * red
h2 = np.where(k > 0, 26.0, h)                 # PIL HSV 0~255 스케일: 26 ≈ 37°(꿀빛 황토)
s2 = np.where(k > 0, np.clip(s * 0.92, 0, 255), s)
v2 = np.where(k > 0, np.clip(v * 1.15 + 12, 0, 255), v)
hsv2 = np.stack([h * (1 - k) + h2 * k, s * (1 - k) + s2 * k, v * (1 - k) + v2 * k], -1)
Image.fromarray(np.clip(hsv2, 0, 255).astype('uint8'), 'HSV').convert('RGB').save(out)
print('recoloured px', int((k > 0.5).sum()), 'saved', out)
