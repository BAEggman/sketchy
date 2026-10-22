"""方劑 통합판 s14u03 — 합성본 뒤 PIL 손질 (2026-10-22, 재현용). 좌표는 합성본 2048×1144 기준.
   1) 腎氣丸 사발 속 검은 덩이(附子)에 Pro가 만화 얼굴(눈·입)을 그려 넣음 → 덩이의 제 색으로 메움.
   2) 六味地黃丸 사발의 붉은 환약 다섯 → 하나 복사해 여섯(六 수 다리).
   3) 八珍 쟁반이 일곱(川芎 둘, 甘草·茯苓 없음) → 오른쪽 위 川芎을 지우고 四君子 쟁반의 甘草 막대를 복사, 왼쪽 아래에 茯苓 흰 덩이 복사 → 여덟.
   4) 四物 쟁반이 다섯(오른쪽 아래 칸에 川芎이 하나 더) → 지워서 넷, 칸마다 하나.
   usage: python3 s14u03_post.py comp.png out.png
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
im=Image.open(sys.argv[1]).convert('RGB'); a=np.asarray(im).astype(float); H,W=a.shape[:2]
def flat(mean, sigma, seed):
    rng=np.random.default_rng(seed)
    f=np.broadcast_to(mean,(H,W,3))+rng.normal(0,sigma,(H,W,1))
    return np.asarray(Image.fromarray(np.clip(f,0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)
def cover(a, ellipses, mean, sigma, seed, blur):
    mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
    for e in ellipses: d.ellipse(e,fill=255)
    m=np.asarray(mask.filter(ImageFilter.GaussianBlur(blur))).astype(float)/255
    return a*(1-m[...,None])+flat(mean,sigma,seed)*m[...,None]
# 1) 얼굴 지우기
a=cover(a,[(1247,356,1269,377),(1273,355,1291,371),(1260,369,1290,385)], a[357:367,1240:1250].reshape(-1,3).mean(0), 2.5, 3, 2.0)
# 2) 여섯째 환약
src=a[379:402,770:795].copy()
pm=Image.new('L',(25,23),0); ImageDraw.Draw(pm).ellipse((2,2,22,20),fill=255)
pm=np.asarray(pm.filter(ImageFilter.GaussianBlur(0.8))).astype(float)/255
a[381:404,734:759]=a[381:404,734:759]*(1-pm[...,None])+src*pm[...,None]
# 3) 八珍 쟁반: 川芎 하나 지우고 甘草·茯苓 복사
def patch(a, src_box, dst_box, blur=3.0):
    sx0,sy0,sx1,sy1=src_box; dx0,dy0,dx1,dy1=dst_box
    src=Image.fromarray(np.clip(a[sy0:sy1,sx0:sx1],0,255).astype('uint8')).resize((dx1-dx0,dy1-dy0),Image.LANCZOS)
    full=np.zeros_like(a); full[dy0:dy1,dx0:dx1]=np.asarray(src).astype(float)
    mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).ellipse(dst_box,fill=255)
    m=np.asarray(mask.filter(ImageFilter.GaussianBlur(blur))).astype(float)/255
    return a*(1-m[...,None])+full*m[...,None]
def keyed(box, cond, dil=3, blur=0.8):
    x0,y0,x1,y1=box; sub=a[y0:y1,x0:x1]; mi=Image.fromarray(cond(sub).astype(np.uint8)*255)
    for _ in range(dil): mi=mi.filter(ImageFilter.MaxFilter(3))
    return Image.fromarray(np.clip(sub,0,255).astype('uint8')), mi.filter(ImageFilter.GaussianBlur(blur))
stick,sm=keyed((345,668,485,725), lambda s: (s[...,0]>170)&(s[...,1]>140)&(s[...,2]<120))
lump,lm=keyed((235,660,315,725), lambda s: (s.mean(-1)>185)&(np.abs(s[...,0]-s[...,2])<40))
a=cover(a,[(900,912,1000,980)], a[1020:1035,800:830].reshape(-1,3).mean(0), 2.0, 5, 2.5)   # 쟁반 바닥 색으로 川芎 자리를 메움
# 4) 四物 쟁반의 다섯째(오른쪽 아래 川芎) 지우기
a=cover(a,[(955,666,1032,738)], a[690:725,835:865].reshape(-1,3).mean(0), 3.0, 7, 2.5)      # 칸 바닥 색으로 다섯째 川芎 자리를 메움
out=Image.fromarray(np.clip(a,0,255).astype('uint8'))
def paste(src,mask,scale,pos,rot=0):
    w,h=src.size; s2=src.resize((int(w*scale),int(h*scale)),Image.LANCZOS); m2=mask.resize(s2.size,Image.LANCZOS)
    if rot: s2=s2.rotate(rot,expand=True,resample=Image.BICUBIC); m2=m2.rotate(rot,expand=True,resample=Image.BICUBIC)
    out.paste(s2,pos,m2)
paste(stick,sm,0.6,(910,925),rot=-12); paste(lump,lm,0.65,(700,985))
# 5) 캡처 오버레이의 분홍 띠가 오른쪽 끝 두 열에 남음 → 안쪽 열로 덮음
o=np.asarray(out).copy(); o[:,-2:]=o[:,-3:-2]; out=Image.fromarray(o)
out.save(sys.argv[2]); print('saved',sys.argv[2])
