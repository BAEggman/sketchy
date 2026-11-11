# 방적기 옆판의 'D'처럼 읽히는 걸쇠를 판 색으로 지움(글자 오인 방지)
import sys, numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(int).copy()
x0, y0, x1, y1 = 1618, 722, 1694, 806
ring = np.concatenate([a[y0-8:y0, x0:x1].reshape(-1,3), a[y1:y1+8, x0:x1].reshape(-1,3), a[y0:y1, x0-8:x0].reshape(-1,3), a[y0:y1, x1:x1+8].reshape(-1,3)])
med = np.median(ring, 0)
a[y0:y1, x0:x1] = med
im = Image.fromarray(a.astype('uint8'))
# 경계 살짝 흐리게
box = (x0-4, y0-4, x1+4, y1+4); im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(1.2)), box[:2])
im.save(out); print('ok', med)
