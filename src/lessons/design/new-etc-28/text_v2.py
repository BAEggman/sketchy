# v1 → v2: 말풍선 글자 「NO」 둘과 「?」 하나를 지운다(벽 · 바탕색으로 inpaint). 말하는 선(짧은 획)도 함께.
from PIL import Image; import numpy as np, cv2
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-etc-28/'
a=np.asarray(Image.open(SP+'v1.png').convert('RGB')).copy()
m=np.zeros(a.shape[:2],np.uint8)
# (x0,y0,x1,y1) — 글자와 말하는 선만 들어가는 좁은 상자
for x0,y0,x1,y1 in [(308,618,356,646),(302,648,320,668),(683,618,730,646),(663,646,683,662),(1436,654,1460,697)]:
    lum=a[y0:y1,x0:x1].mean(2)
    m[y0:y1,x0:x1]=(lum<140).astype(np.uint8)*255
m=cv2.dilate(m,np.ones((9,9),np.uint8))   # 글자 둘레 밝은 번짐까지
out=cv2.inpaint(a[:,:,::-1].copy(),m,6,cv2.INPAINT_TELEA)[:,:,::-1]
Image.fromarray(out).save(SP+'v2.png'); print('px',int((m>0).sum()))
