# v1 오른쪽 위 비행기(이륙처럼 기수가 들림)를 기수가 아래로 향하게 기울여 '착륙'으로 — 하늘은 행별 색으로 메움
import sys, numpy as np
from PIL import Image, ImageFilter
src, out, ang, dy = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
im = Image.open(src).convert('RGB'); a = np.asarray(im).astype(int)
x0, y0, x1, y1 = 1580, 165, 2040, 314
reg = a[y0:y1, x0:x1]
r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
sky = (b > r + 40) & (b > 170) & (g > 120)
plane = ~sky
from scipy import ndimage
plane = ndimage.binary_fill_holes(plane)  # 동체 안 하늘색 반사가 구멍으로 남지 않게
# 작은 구멍 메우고 가장자리 조금 넓힘
m = Image.fromarray((plane * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
# 하늘 채우기: 같은 행의 하늘 픽셀 중앙값
big = np.asarray(m.filter(ImageFilter.MaxFilter(9))) > 0  # 원래 윤곽의 번진 가장자리까지 지움
fill = a.copy()
for yy in range(y0, y1):
    row = a[yy, 1450:2040]; rr, gg, bb = row[:, 0], row[:, 1], row[:, 2]
    s = (bb > rr + 40) & (bb > 170) & (gg > 120)
    col = np.median(row[s], 0) if s.sum() > 20 else np.median(row, 0)
    fill[yy, x0:x1][big[yy - y0]] = col
    if yy < 312: fill[yy, 1945:x1] = col  # 꼬리 뒤 옅은 속도선 조각까지 하늘로
base = Image.fromarray(fill.astype('uint8'))
pm = np.asarray(m).copy(); pm[:, 1972 - x0:] = 0  # 꼬리 뒤 속도선은 붙이지 않음(돌리면 점으로 흩어짐)
pl = Image.fromarray(reg.astype('uint8')).convert('RGBA'); pl.putalpha(Image.fromarray(pm))
rot = pl.rotate(ang, resample=Image.BICUBIC, expand=True)
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + dy
base.paste(rot, (cx - rot.width // 2, cy - rot.height // 2), rot)
base.save(out); print('ok', rot.size)
