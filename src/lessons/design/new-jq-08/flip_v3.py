# v2 왼쪽 줄 여행객(터미널로 들어가는 쪽을 봄)을 한 사람씩 제자리 좌우 반전 → 문에서 멀어지며 '나가는' 줄로
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); a = np.asarray(im).astype(int)
x0, y0, x1, y1 = 462, 440, 835, 552
reg = a[y0:y1, x0:x1]
mx, mn = reg.max(2), reg.min(2); br = reg.mean(2)
fg = ((mx - mn) >= 22) | (br < 115) | (br > 222)
fgm = np.asarray(Image.fromarray((fg * 255).astype('uint8')).filter(ImageFilter.MaxFilter(5))) > 0
lab, n = ndimage.label(fgm)
sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
print('components', n, sorted([int(s) for s in sizes])[-12:])
# 배경 채우기: 같은 행에서 ±60px 안의 배경 픽셀 중앙값
bg = reg.copy()
for yy in range(reg.shape[0]):
    for xx in np.where(fgm[yy])[0]:
        lo, hi = max(0, xx - 60), min(reg.shape[1], xx + 60)
        s = ~fgm[yy, lo:hi]
        if s.sum() > 5: bg[yy, xx] = np.median(reg[yy, lo:hi][s], 0)
outr = bg.copy()
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    if sizes[i - 1] < 150: 
        outr[sl][lab[sl] == i] = reg[sl][lab[sl] == i]; continue
    m = (lab[sl] == i); pix = reg[sl]
    fm = m[:, ::-1]; fp = pix[:, ::-1]
    tgt = outr[sl]; tgt[fm] = fp[fm]
res = a.copy(); res[y0:y1, x0:x1] = outr
Image.fromarray(res.astype('uint8')).save(out); print('ok')
