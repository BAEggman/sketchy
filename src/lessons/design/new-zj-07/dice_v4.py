# new-zj-07 v3 -> v4 주사위(코드로 눈 수 정확, v1 -> v2에도 왼쪽 아래 자리로 썼음): 오른쪽 탑 곁으로 옮긴 두루마리 노학자 위 3 · 6 = 難經 三十六難(左腎右命門 · 男子藏精 女子繫胞)
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-07/'
D='/home/claude/s7/work/src/lessons/design/new-zj-07/'
im=Image.open(SP+'v3.png').convert('RGB'); d=ImageDraw.Draw(im)
PIPS={3:[(.25,.25),(.5,.5),(.75,.75)],6:[(.27,.22),(.27,.5),(.27,.78),(.73,.22),(.73,.5),(.73,.78)]}
def die(x,y,s,n):
    d.rounded_rectangle((x+5,y+6,x+s+5,y+s+6),radius=s//6,fill=(70,90,60))
    d.rounded_rectangle((x,y,x+s,y+s),radius=s//6,fill=(252,248,236),outline=(15,15,15),width=max(3,s//18))
    r=s*.09
    for px,py in PIPS[n]:
        cx,cy=x+px*s,y+py*s; d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(15,15,15))
F=2048/1410
for (cx,cy,n) in [(1352,318,3),(1352,372,6)]: die(int(cx*F),int(cy*F),66,n)
im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((1650,380,2048,1144)).save(SP+'../g_dice7.png')
