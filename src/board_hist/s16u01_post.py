# s16u01 손질 (2026-10-23): ZB 구역 경계(own 오른끝 css 830)의 페더가 쏟아진 덩이 하나를 반투명 잔상으로 남겨
# 人蔘 수염 왼쪽에 흰 번짐이 생김(902 두 독자 지적) → 그 자리만 ZB 이전 comp 화소로 되돌린다.
# usage: python3 s16u01_post.py comp.png comp2.png out.png
import sys, numpy as np
from PIL import Image, ImageFilter
old, new, out = sys.argv[1:4]
A = np.asarray(Image.open(old).convert('RGB')).astype(float)
B = np.asarray(Image.open(new).convert('RGB')).astype(float)
m = Image.new('L', (A.shape[1], A.shape[0]), 0)
from PIL import ImageDraw
ImageDraw.Draw(m).rectangle((1644, 1067, 1712, 1098), fill=255)
m = np.asarray(m.filter(ImageFilter.GaussianBlur(5))).astype(float)[..., None] / 255
Image.fromarray((B * (1 - m) + A * m).round().clip(0, 255).astype('uint8')).save(out)
print('saved', out)
