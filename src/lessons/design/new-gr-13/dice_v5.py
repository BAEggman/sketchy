# new-gr-13 v4 -> v5 주사위 (v2 -> v3에도 같은 자리로 썼음)(코드로 눈 수 정확): 등 줄기 곁 2·8 = 督脈 28穴 · 임신부 곁 2·4 = 任脈 24穴 · 붉은 분수 곁 1·2 = 衝脈 12穴
import sys
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-gr-13/'
D='/home/claude/s7/work/src/lessons/design/new-gr-13/'
im = Image.open(SP+'v4.png').convert('RGB'); d = ImageDraw.Draw(im)
PIPS = {1: [(.5, .5)], 2: [(.27, .27), (.73, .73)], 4: [(.27, .27), (.73, .27), (.27, .73), (.73, .73)],
        8: [(.25, .2), (.5, .2), (.75, .2), (.25, .5), (.75, .5), (.25, .8), (.5, .8), (.75, .8)]}
def die(x, y, s, n, tint=(252, 248, 236)):
    d.rounded_rectangle((x + 5, y + 6, x + s + 5, y + s + 6), radius=s // 6, fill=(60, 60, 60))
    d.rounded_rectangle((x, y, x + s, y + s), radius=s // 6, fill=tint, outline=(15, 15, 15), width=max(3, s // 18))
    r = s * (.075 if n == 8 else .09)
    for px, py in PIPS[n]:
        cx, cy = x + px * s, y + py * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(15, 15, 15))
F = 2048 / 1410   # 캡처 좌표 → 2048
POS = [(140, 450, 2), (192, 450, 8),     # 督 28
       (735, 610, 2), (787, 610, 4),     # 任 24
       (880, 405, 1), (932, 405, 2)]     # 衝 12
for (cx, cy, n) in POS:
    die(int(cx * F), int(cy * F), 66, n)
im.save(D+'base_v5.webp', quality=80); im.save(SP+'v5.png'); print('ok')
im.resize((1024,572)).save(SP+'../g13_v2s.png')
