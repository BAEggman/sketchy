# (v4 = v3 위에 다시 적용) 주사위: 帛書 곁 1·1 = 十一脈 · 약상자 곁 5·2 = 五十二病方
import sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); d = ImageDraw.Draw(im)
PIPS = {1: [(.5, .5)], 2: [(.27, .27), (.73, .73)], 5: [(.27, .27), (.27, .73), (.5, .5), (.73, .27), (.73, .73)], 3: [(.25, .25), (.5, .5), (.75, .75)], 6: [(.27, .22), (.27, .5), (.27, .78), (.73, .22), (.73, .5), (.73, .78)]}
def die(x, y, s, n, rot=0):
    d.rounded_rectangle((x + 5, y + 6, x + s + 5, y + s + 6), radius=s // 6, fill=(60, 70, 60))  # 그림자
    d.rounded_rectangle((x, y, x + s, y + s), radius=s // 6, fill=(252, 248, 236), outline=(15, 15, 15), width=max(3, s // 18))
    r = s * .09
    for px, py in PIPS[n]:
        cx, cy = x + px * s, y + py * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(15, 15, 15))
F = 2048 / 1421
for (vx, vy, n) in [(378, 442, 1), (424, 442, 1), (1158, 690, 5), (1204, 690, 2)]:
    die(int(vx * F), int(vy * F), 60, n)
im.save(out); print('ok')
