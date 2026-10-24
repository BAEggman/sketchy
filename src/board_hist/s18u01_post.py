# s18u01 손질 (2026-10-24): 勝格(첫째 칸) 선반장이 바탕에서 「위 = 김 나는 국물 · 가운데 = 빈 그릇 · 아래 = 빈 그릇 + 빗자루」로 나옴.
# 勝格 = 補官·瀉子 → 위 칸은 비고, 가운데 칸 = 국물. Argon 구역 편집 두 번(7cf041fe3f733024)이 선반 안을 못 바꿔 PIL로:
#   ① 위 칸의 국물 그릇+김 조각을 한 칸(120px) 아래 가운데 칸 그릇 자리에 덮는다 ② 위 칸은 줄마다 좌우 벽 색 보간으로 비운다.
# usage: python3 s18u01_post.py in.png out.png
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
src, out = sys.argv[1:3]
A = np.asarray(Image.open(src).convert('RGB')).astype(float)
C = A.copy()
X0, X1 = 514, 612          # 그릇+김 가로 범위(왼 기둥 안쪽 ~ 빗자루 자루 앞)
Y0, Y1 = 556, 664          # 위 칸: 김 꼭대기 ~ 그릇 밑(판 위)
DY = 120                   # 칸 간격
P = A[Y0:Y1, X0:X1].copy()
h, w = P.shape[:2]
m = np.ones((h, w)); f = 6
m[:f] *= np.linspace(0, 1, f)[:, None]; m[:, :f] *= np.linspace(0, 1, f)[None, :]; m[:, -f:] *= np.linspace(1, 0, f)[None, :]
M = m[..., None]
# ② 위 칸 비우기 — 줄마다 x=514..517 과 626..631 의 벽 색을 잇는다
L = A[Y0:Y1, 514:518].mean(1); R = A[Y0:Y1, 626:632].mean(1)
t = np.linspace(0, 1, X1 - X0)[None, :, None]
fill = L[:, None, :] * (1 - t) + R[:, None, :] * t
fill = gaussian_filter(fill, (8, 0, 0))   # 줄마다 생기는 가로 얼룩을 세로로 고름 (blind59 I5·J5 「지운 얼룩」)
rng = np.random.default_rng(7)
fill = fill + gaussian_filter(rng.normal(0, 2.0, fill.shape[:2]), 2)[..., None]   # 수채 종이결 정도의 잔결
C[Y0:Y1, X0:X1] = C[Y0:Y1, X0:X1] * (1 - M) + fill * M
# ① 가운데 칸에 국물 그릇+김
C[Y0 + DY:Y1 + DY, X0:X1] = C[Y0 + DY:Y1 + DY, X0:X1] * (1 - M) + P * M
# ③ 셋째·넷째 칸 사이 굵은 기둥 주춧돌의 가짜 글씨 두 군데(blind59 I5·J5) — 주춧돌 가운데 색으로 덮는다
st = C[1040:1056, 1472:1512].reshape(-1, 3).mean(0)
for (x0, x1) in [(1446, 1468), (1519, 1543)]:
    C[1040:1057, x0:x1] = C[1040:1057, x0:x1] * 0.0 + st
    C[1037:1060, x0 - 2:x1 + 2] = gaussian_filter(C[1037:1060, x0 - 2:x1 + 2], (1.2, 1.2, 0))
Image.fromarray(C.round().clip(0, 255).astype('uint8')).save(out)
print('saved', out)
