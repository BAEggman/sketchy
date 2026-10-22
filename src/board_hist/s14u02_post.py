"""本草 ② 瀉·毒·修治 통합판 s14u02 — 합성본 뒤 PIL 손질 (2026-10-22, 재현용).
   大黃의 性 寒을 지는 소품이 없어(원 낱장 s14p03은 얼음 덩이가 §5 위반이었다) 사전 寒 = 눈송이를 s12u03(一問 寒熱의 손바닥 위 눈송이)에서 복사해
   大黃 칸 진열대 위, 苦 커피 잔 앞에 놓는다 — 苦 + 寒 = 苦寒. 마스크: 밝은 흰·푸른 결정 + 검은 윤곽만, 손가락은 잘라 냄.
   usage: python3 s14u02_post.py comp.png out.png  (s12u03.webp 는 images/ 에서 읽음)
"""
import sys, numpy as np
from PIL import Image, ImageFilter
src=Image.open('/home/claude/s7/work/images/s12u03.webp').convert('RGB')
sf=src.crop((108,408,200,500)); a=np.asarray(sf).astype(float)
br=a.mean(-1); blue=a[...,2]-a[...,0]
m=((br>205)&(blue>-5))|(br<120)
h,w=m.shape; yy,xx=np.mgrid[0:h,0:w]
m&=((yy-44)**2+(xx-46)**2)<41**2
m[72:]=False
mi=Image.fromarray(m.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
tgt=Image.open(sys.argv[1]).convert('RGB')
tgt.paste(sf.resize((64,64),Image.LANCZOS),(404,678),mi.resize((64,64),Image.LANCZOS))
tgt.save(sys.argv[2]); print('saved',sys.argv[2])
