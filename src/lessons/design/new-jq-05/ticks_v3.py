# new-jq-05 v2 → v3: 분홍 관에 눈금 7 · 파란 관에 눈금 8을 코드로 그린다. 사건 눈금(여 2·5·7 / 남 2·3·5·7·8)은 길고 굵게 + 끝에 점.
from lk import *
from PIL import Image, ImageDraw
im=Image.open(SP+'new-jq-05/v2.png').convert('RGBA'); K=2048/1421; S=2
lay=Image.new('RGBA',(im.width*S,im.height*S),(0,0,0,0)); d=ImageDraw.Draw(lay)
def tube(x0,x1,ybot,ytop,n,events,col):
    sp=(ybot-ytop)/n
    for k in range(1,n+1):
        y=ybot-sp*k
        ev=k in events
        xe=x0+(x1-x0)*(0.62 if ev else 0.32)
        w=6 if ev else 3.5
        d.line([(x0*K*S,y*K*S),(xe*K*S,y*K*S)],fill=col,width=int(w*K*S))
        if ev:
            r=7
            d.ellipse([((xe+10)-r)*K*S,(y-r)*K*S,((xe+10)+r)*K*S,(y+r)*K*S],fill=col,outline=(20,20,20,255),width=int(1.5*K*S))
tube(70,190,725,235,7,{2,5,7},(200,40,110,255))
tube(240,360,650,210,8,{2,3,5,7,8},(30,70,180,255))
lay=lay.resize(im.size,Image.LANCZOS); out=Image.alpha_composite(im,lay).convert('RGB')
out.save(SP+'new-jq-05/v3.png'); out.save(R+'design/new-jq-05/base_v3.webp',quality=80)
out.crop((0,150,620,1144)).resize((310,497)).save(SP+'new-jq-05/tubes3.png')
