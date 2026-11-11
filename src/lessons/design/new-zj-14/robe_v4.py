# new-zj-14 v3 -> v4: 노인 흰 옷의 짧은 붉은 줄 둘(피 얼룩처럼 보임)을 옷 흰색으로 덮음. 손 · 손수건 붉은 점 · 안장 · 고삐는 그대로
import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/new-zj-14/'
D='/home/claude/s7/work/src/lessons/design/new-zj-14/'
a=np.asarray(Image.open(SP+'v3.png').convert('RGB')).astype(int).copy()
for (x0,y0,x1,y1) in [(1444,559,1475,575),(1454,603,1478,617)]:   # 붉은 줄 둘(손 위 · 손 아래)만 감싼 칸
    sub=a[y0:y1,x0:x1]
    ring=np.concatenate([a[y0-3:y0,x0:x1].reshape(-1,3),a[y1:y1+3,x0:x1].reshape(-1,3)])
    ring=ring[(ring.sum(axis=1)>600)&(np.abs(ring[:,0]-ring[:,2])<8)]   # 둘레의 흰 옷 픽셀만
    robe=np.median(ring,axis=0)
    skin=(sub[:,:,1]-sub[:,:,2]>18)&(sub[:,:,0]>215)
    red=(((sub[:,:,0]-sub[:,:,2]>8)&(sub.sum(axis=2)>250))|((sub[:,:,0]-sub[:,:,1]>25)&(sub[:,:,0]-sub[:,:,2]>25)))&~skin   # 붉은 기(어두운 붉은 점 포함), 살색 제외
    for yy in range(y1-y0):   # 행마다 왼쪽 · 오른쪽 흰 옷 색을 보간(둘레 음영과 맞춤)
        row=a[y0+yy]; L=np.median(row[x0-6:x0-1],axis=0); R=np.median(row[x1+1:x1+6],axis=0)
        for xx in np.nonzero(red[yy])[0]:
            t=xx/(x1-x0); c=(1-t)*L+t*R
            sub[yy,xx]=c if (c.sum()>600 and abs(c[0]-c[2])<10) else robe
    a[y0:y1,x0:x1]=sub
    print((x0,y0),robe,red.sum())
im=Image.fromarray(a.astype('uint8')); im.save(D+'base_v4.webp',quality=80); im.save(SP+'v4.png')
im.crop((1380,520,1560,700)).resize((540,540)).save(SP+'y_robe4.png')
