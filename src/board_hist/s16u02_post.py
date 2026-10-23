# s16u02 손질 (2026-10-23): 偏盛 방 마루 앞 땅의 놋요강·나무 뒷간통이 두 남자 사이(배 감싼 陰盛 남자 쪽)에 있어
# 독자 둘이 「누구 몫인지 애매」(blind52z z14 · blind53 B5) → 마루 앞턱·땅 띠째로 왼쪽(陽盛 남자 바로 아래)으로 160px 옮기고,
# 빈 오른쪽은 줄마다 양끝 색을 잇는 선형 보간(앞턱 나뭇결·땅 그늘이 가로줄이라 그대로 이어진다) + 왼쪽 띠의 잔결 무늬로 메운다.
# Argon 구역 편집(ZA4)이 「이미지 도구 비활성」으로 안 돼 PIL로.
# usage: python3 s16u02_post.py in.png out.png
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
src, out = sys.argv[1:3]
A = np.asarray(Image.open(src).convert('RGB')).astype(float)
C = A.copy()
Y0, Y1 = 950, 1092
H = Y1 - Y0
fy = np.ones(H); fy[:6] = np.linspace(0, 1, 6); fy[-10:] = np.linspace(1, 0, 10)
FY = fy[:, None, None]
# 1) 물건 띠(252..500)를 왼쪽으로 160 → 92..340 (왼끝 12px 페더)
band = A[Y0:Y1, 252:500]
fx = np.ones(248); fx[:12] = np.linspace(0, 1, 12)
F = FY * fx[None, :, None]
C[Y0:Y1, 92:340] = C[Y0:Y1, 92:340] * (1 - F) + band * F
# 2) 340..512: 줄마다 C[:,339] → A[:,512] 선형 보간 + 깨끗한 왼쪽 띠의 고주파 무늬
xl, xr = 339, 512
t = (np.arange(xl + 1, xr) - xl) / (xr - xl)
Lc = C[Y0:Y1, xl][:, None, :]; Rc = A[Y0:Y1, xr][:, None, :]
fill = Lc * (1 - t[None, :, None]) + Rc * t[None, :, None]
src_tex = A[Y0:Y1, 92 + (np.arange(xl + 1, xr) - xl - 1) % 160]
tex = src_tex - gaussian_filter(src_tex, (3, 3, 0))
fill = fill + 0.7 * tex
C[Y0:Y1, xl + 1:xr] = C[Y0:Y1, xl + 1:xr] * (1 - FY) + fill * FY
Image.fromarray(C.round().clip(0, 255).astype('uint8')).save(out)
print('saved', out)
