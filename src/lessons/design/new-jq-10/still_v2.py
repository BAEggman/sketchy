# 작은 종(不及) 오른쪽의 떨림 표시 두 무리를 벽 색으로 지움 — '떨림이 보이지 않는 종'
import sys, numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(int).copy()
for (x0, y0, x1, y1) in [(2016, 570, 2044, 628), (2005, 651, 2040, 682)]:
    reg = a[y0:y1, x0:x1]; med = np.median(reg.reshape(-1, 3), 0)
    far = np.abs(reg - med).sum(2) > 10
    reg[far] = med; a[y0:y1, x0:x1] = reg
    print((x0, y0), 'filled', int(far.sum()))
Image.fromarray(a.astype('uint8')).save(out)
