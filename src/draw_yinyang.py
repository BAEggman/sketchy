"""Deterministic SVG diagrams. Counts, arrows and tables are authored data."""
import json, math, html, textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'src/panels/yinyang-v2.4.json').read_text())
C=['#387758','#bc5546','#b18a36','#707f88','#344f72']
EL=['목','화','토','금','수']
def e(s):return html.escape(str(s))
class SVG:
 def __init__(self,p,h=800):
  self.h=h;self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="{h}" viewBox="0 0 1280 {h}" role="img" aria-labelledby="title desc"><title id="title">{e(p["title"])}</title><desc id="desc">{e(" / ".join(p["diagram"]["labels"]))}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs><style>text{{font-family:"Apple SD Gothic Neo","Noto Sans CJK KR",sans-serif;fill:#253b39}}.small{{fill:#65766d}}.han{{font-family:"Apple SD Gothic Neo","Noto Serif CJK KR",serif}}</style><rect width="1280" height="{h}" fill="#faf7ef"/>']
  self.text(44,44,'음양오행  /  연결 도해',18,'#64776d');self.text(44,91,p['title'].split(' — ')[0],34,weight=700)
  self.line(44,116,1236,116,'#d8dfd7',2)
 def text(self,x,y,s,size=26,color=None,anchor='start',weight=400):
  self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"'+(f' style="fill:{color}"'if color else '')+f'>{e(s)}</text>')
 def multiline(self,x,y,s,width=20,size=24,color=None,line=34):
  for i,t in enumerate(textwrap.wrap(s,width=width,break_long_words=True,break_on_hyphens=False)or ['']):self.text(x,y+i*line,t,size,color)
 def line(self,x1,y1,x2,y2,color='#87998e',w=3,arrow=False,dash=False):
  self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"'+(' marker-end="url(#arrow)"'if arrow else '')+(' stroke-dasharray="8 7"'if dash else '')+'/>')
 def rect(self,x,y,w,h,fill='#fffdf8',stroke='#d8dfd7',radius=18):self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
 def circle(self,x,y,r,fill='#fffdf8',stroke='#4d6558',sw=2,meta=''):
  self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {meta}/>')
 def node(self,x,y,label,el=None,r=45):
  col=C[EL.index(el)]if el in EL else '#426f60';self.circle(x,y,r,'#fffdf8',col,3);self.text(x,y+9,label,28,col,'middle',700)
 def card(self,x,y,w,h,title,lines=(),color='#426f60'):
  self.rect(x,y,w,h);self.rect(x,y,7,h,color,color,3);self.text(x+24,y+40,title,26,color,weight=700)
  for i,t in enumerate(lines):self.text(x+24,y+84+i*36,t,23)
 def save(self,p):
  self.text(44,self.h-30,'연결을 읽은 뒤 아래 문항에서 답을 가리고 복원하세요.',20,'#6d7b73');self.parts.append('</svg>')
  (ROOT/p['image']).write_text('\n'.join(self.parts))

def matrix(p):
 rows=p['diagram']['matrix'];h=204+len(rows)*72;s=SVG(p,h);widths=[260,180,180,180,180,180];x0=50;y0=145
 for ri,rr in enumerate(rows):
  x=x0
  for ci,txt in enumerate(rr):
   fill='#edf2eb'if ri==0 else ('#f1f5ee'if ci==0 else '#fffdf8')
   if p['diagram']['kind']=='season' and ci>0:fill=['','#f7e3cc','#e2eddf','#e8edef','#e9e4f0','#e9e9e7'][ci]
   s.rect(x,y0+ri*72,widths[ci],72,fill,'#d8dfd7',0);s.text(x+widths[ci]/2,y0+ri*72+46,txt,23 if ci==0 else 28,anchor='middle',weight=700 if ri==0 else 400);x+=widths[ci]
 s.save(p)

for p in P:
 kind=p['diagram']['kind'];pid=p['id']
 if kind in ['matrix','season']:matrix(p);continue
 s=SVG(p,850)
 if kind=='cycle':
  cx,cy=640,435;s.circle(cx,cy,235,'none','#9dac8f',4);s.circle(cx,cy,125,'none','#a4b8aa',3)
  for i,(x,y,title,sub)in enumerate([(395,435,'아침 / 봄','단혜 · 맑아짐'),(640,200,'한낮 / 여름','주안 · 안정'),(885,435,'저녁 / 가을','석가 · 더해짐'),(640,670,'밤 / 겨울','야심 · 심함')]):
   s.line(cx+(x-cx)*.55,cy+(y-cy)*.55,x,y,'#9dac8f',2);s.rect(x-130,y-47,260,110);s.text(x,y-8,title,27,anchor='middle',weight=700);s.text(x,y+33,sub,23,anchor='middle')
  s.text(cx,cy-15,'천인상응',30,anchor='middle',weight=700);s.text(cx,cy+28,'자연 ↔ 인체',26,anchor='middle');s.text(70,270,'바깥: 계절·주야',23);s.text(70,310,'안쪽: 생리·병리',23);s.text(70,600,'위기: 낮은 양분',23);s.text(70,636,'밤은 음분',23)
 elif kind=='compass':
  s.card(465,145,350,175,'남 · 장양',['낮은 땅 / 산미·발효 음식','연비 → 미침'],C[1]);s.card(465,605,350,175,'북 · 폐장',['고릉·풍한 / 젖 음식','장한생만병 → 구설'],C[4]);s.card(45,355,355,190,'동 · 시생',['해변·어염 / 생선·짠맛','옹양 → 폄석'],C[0]);s.card(880,355,355,190,'서 · 수인',['금옥·사석 / 기름진 음식','병생어내 → 독약'],C[3]);s.card(455,355,370,190,'중앙 · 생만물',['평습 / 식잡이불로','위궐한열 → 도인안교'],C[2]);s.line(640,320,640,350);s.line(640,550,640,600);s.line(405,448,450,448);s.line(830,448,875,448)
 elif kind=='sequence':
  labels=p['diagram']['labels']
  positions=[(60+(i%3 if i//3!=1 else 2-i%3)*407,170+(i//3)*185) for i in range(9)]
  for i,lab in enumerate(labels):
   x,y=positions[i];s.card(x,y,344,135,f'{i+1:02}  {lab}',[],C[i%5])
   if i<8:
    nx,ny=positions[i+1]
    if ny!=y:s.line(x+172,y+139,x+172,ny-10,arrow=True)
    elif nx>x:s.line(x+350,y+68,nx-10,y+68,arrow=True)
    else:s.line(x-8,y+68,nx+354,y+68,arrow=True)
  s.text(70,770,'무 · 역 · 초 · 시 · 소 · 극   /   2 · 4 · 8',28,weight=700)
 elif kind=='relations':
  for i,lab in enumerate(p['diagram']['labels']):
   x=55+(i%2)*610;y=160+(i//2)*302;s.rect(x,y,570,270);s.text(x+24,y+42,lab,27,weight=700)
   if i==0:
    s.rect(x+130,y+95,54,100,'#dce8df');s.rect(x+350,y+95,54,100,'#7b9285');s.line(x+157,y+202,x+377,y+202,'#426f60',8);s.line(x+184,y+140,x+348,y+140,'#426f60',4,True);s.line(x+350,y+175,x+188,y+175,'#426f60',4,True);cap='서로 의지하고 서로 쓰인다'
   elif i==1:
    s.line(x+75,y+155,x+258,y+155,'#b75b4c',7,True);s.line(x+495,y+155,x+312,y+155,'#476d91',7,True);s.line(x+285,y+100,x+285,y+205,'#426f60',8);cap='반대 작용으로 서로 제한한다'
   elif i==2:
    for xx,hh in [(130,45),(200,110),(330,110),(400,45)]:s.rect(x+xx,y+210-hh,44,hh,'#637f70')
    cap='같은 성질의 양이 늘거나 준다'
   else:
    s.circle(x+150,y+150,48,'#344a41');s.circle(x+420,y+150,48,'#fffdf8');s.line(x+210,y+150,x+355,y+150,'#426f60',4,True);s.text(x+280,y+125,'조건·극점',22,anchor='middle');cap='조건을 갖추면 성질이 전환된다'
   s.text(x+285,y+244,cap,23,anchor='middle')
 elif kind=='bars':
  vals=[[(45,45),(105,45)],[(45,105),(105,45)],[(45,45),(105,105)],[(105,105),(45,45)]]
  for i,lab in enumerate(p['diagram']['labels']):
   x=55+(i%2)*610;y=165+(i//2)*300;s.rect(x,y,570,265);s.text(x+24,y+40,lab,26,weight=700)
   for j,(a,b) in enumerate(vals[i]):
    bx=x+100+j*275;s.line(bx-10,y+200,bx+120,y+200,'#b6c1b8',2)
    for k,v in enumerate([a,b]):s.rect(bx+k*60,y+200-v,42,v,'#e8eee4'if k==0 else '#426f60','#648474',4)
    s.text(bx+20,y+230,'음',20,anchor='middle');s.text(bx+80,y+230,'양',20,anchor='middle')
   s.line(x+240,y+150,x+320,y+150,arrow=True)
 elif kind=='elements':
  props=[('가지','생장 · 승발 · 조달'),('불꽃','온열 · 상승'),('밭','파종 · 수확 · 화생'),('금속 틀','변혁 · 수렴 · 숙강'),('물길','자윤 · 하행 · 저장')]
  for i,lab in enumerate(p['diagram']['labels']):
   x=40+i*246;s.rect(x,175,224,530);s.text(x+112,220,lab,27,C[i],'middle',700)
   if i==0:
    s.line(x+112,490,x+112,305,C[i],12);s.line(x+112,380,x+60,330,C[i],8);s.line(x+112,405,x+170,348,C[i],8);s.circle(x+60,320,22,'#95b89c',C[i]);s.circle(x+170,338,22,'#95b89c',C[i])
   elif i==1:
    s.parts.append(f'<path d="M{x+112} 280 C{x+75} 360 {x+170} 345 {x+150} 410 C{x+220} 490 {x+28} 510 {x+55} 410 C{x+95} 370 {x+95} 330 {x+112} 280" fill="{C[i]}"/>');s.line(x+112,290,x+112,250,C[i],3,True)
   elif i==2:
    for k in range(3):s.line(x+35,375+k*38,x+190,375+k*38,C[i],9)
    s.circle(x+65,350,10,C[i]);s.line(x+150,370,x+150,285,C[i],5);s.line(x+150,320,x+175,295,C[i],7);s.line(x+150,340,x+125,315,C[i],7)
   elif i==3:
    s.rect(x+42,295,140,150,'#dce3e4',C[i],2);s.rect(x+73,330,80,84,'#faf7ef',C[i],10);s.text(x+112,495,'재료 → 새 모양',21,anchor='middle')
   else:
    s.parts.append(f'<path d="M{x+95} 280 C{x+180} 355 {x+35} 400 {x+125} 470" stroke="{C[i]}" fill="none" stroke-width="20"/>');s.line(x+125,470,x+145,510,C[i],4,True)
   s.text(x+112,570,props[i][0],25,anchor='middle');s.multiline(x+20,620,props[i][1],width=12,size=22)
 elif kind=='numbers':
  for i,(lab,n)in enumerate(zip(p['diagram']['labels'],range(1,6))):
   x=40+i*246;s.rect(x,180,224,490);s.text(x+112,232,lab,28,anchor='middle',weight=700)
   for num,y in [(n,320),(n+5,485)]:
    for k in range(num):s.circle(x+44+(k%5)*34,y+(k//5)*35,10,'#fff'if num%2 else '#34463d',meta=f'data-number="{num}"')
    s.text(x+112,y+90,str(num),30,anchor='middle')
   s.text(x+112,450,'+ 5',24,'#8a6c2e','middle')
  s.text(640,735,'생성: 수 → 화 → 목 → 금 → 토    /    상생: 목 → 화 → 토 → 금 → 수',25,anchor='middle')
 elif kind=='five_evil':
  s.node(640,440,'나·심화','화',72)
  entries=[(640,220,'어미·간목','허사',C[0]),(640,675,'자식·비토','실사',C[2]),(260,440,'나를 극함·신수','적사',C[4]),(1020,440,'내가 극함·폐금','미사',C[3])]
  for x,y,lab,evil,col in entries:
   dx,dy=640-x,440-y;d=math.hypot(dx,dy);s.line(x+dx/d*72,y+dy/d*72,640-dx/d*86,440-dy/d*86,col,5,True);s.rect(x-155,y-55,310,112);s.text(x,y-10,evil,30,col,'middle',700);s.text(x,y+30,lab,23,anchor='middle')
  s.text(640,478,'정사 = 자기',18,anchor='middle');s.text(60,760,'들어오는 출발점을 묻는다. 병을 받는 장부를 항상 가운데에 고정한다.',26,weight=700)
 elif kind=='feedback':
  s.text(70,175,'① 항성한 목이 토를 지나치게 누름',27,weight=700);s.node(220,285,'목','목');s.node(660,285,'토','토');s.line(280,285,600,285,C[0],10,True);s.text(440,255,'승 · 과도한 제약',25,anchor='middle')
  s.text(70,415,'② 토가 낳는 금이 목을 제약함',27,weight=700);s.node(220,540,'토','토');s.node(660,540,'금','금');s.node(1080,540,'목','목');s.line(280,540,600,540,C[2],4,True);s.line(720,540,1020,540,C[3],7,True);s.text(440,505,'생',25,anchor='middle');s.text(870,505,'복 · 제약',25,anchor='middle');s.text(640,710,'제화: 생화 + 극제   /   항해승제: 지나침을 제한   /   승복: 반응의 선후',24,anchor='middle')
 elif kind=='arrows':
  items=[('모병급자','수','목','생의 방향'),('자병급모','화','목','생의 역방향'),('상승','목','토','극의 같은 방향·과도'),('상모','목','금','극의 반대 방향')]
  for i,(lab,a,b,cap)in enumerate(items):
   x=55+(i%2)*610;y=160+(i//2)*300;s.rect(x,y,570,270);s.text(x+24,y+45,lab,28,weight=700);s.node(x+125,y+130,a,a);s.node(x+445,y+130,b,b);s.line(x+185,y+130,x+385,y+130,C[EL.index(a)],8 if i==2 else 4,True);s.text(x+285,y+225,cap,24,anchor='middle')
 elif kind=='therapies':
  pairs=[('수','목','보하여 기름'),('화','토','보하여 도움'),('토','금','북돋아 도움'),('금','수','함께 자양'),('목','토','억제 / 지지'),('토','수','북돋아 제수'),('금','목','돕고 평정'),('화','수','사남 / 보북')]
  for i,(lab,(a,b,cap))in enumerate(zip(p['diagram']['labels'],pairs)):
   x=40+(i%4)*310;y=165+(i//4)*305;s.rect(x,y,288,275);s.text(x+144,y+45,lab,28,anchor='middle',weight=700);s.node(x+65,y+130,a,a,34);s.node(x+225,y+130,b,b,34)
   if i==7:s.text(x+65,y+188,'−',32,anchor='middle');s.text(x+225,y+188,'+',32,anchor='middle')
   else:
    s.line(x+105,y+130,x+181,y+130,'#667f70',3,True)
    if i==3:s.line(x+181,y+130,x+105,y+130,'#667f70',3,True)
   s.text(x+144,y+226,cap,22,anchor='middle')
 elif kind=='hetu':
  s.rect(35,150,590,590);s.rect(655,150,590,590);s.text(330,195,'하도 · 생성의 짝',29,anchor='middle',weight=700);s.text(950,195,'낙서 · 모든 줄의 합 15',29,anchor='middle',weight=700)
  pairs=[(330,260,'남·화',2,7),(330,610,'북·수',1,6),(130,435,'동·목',3,8),(530,435,'서·금',4,9),(330,435,'중·토',5,10)]
  for x,y,lab,a,b in pairs:
   s.text(x,y-32,lab,23,anchor='middle');s.text(x,y+84,f'{a} · {b}',24,anchor='middle',weight=700)
   for n,yy in [(a,y),(b,y+35)]:
    for k in range(n):s.circle(x+(k-(n-1)/2)*13,yy,5,'#fff'if n%2 else '#2c4338',meta=f'data-hetu="{n}"')
  grid=[[4,9,2],[3,5,7],[8,1,6]]
  for ri,rr in enumerate(grid):
   for ci,n in enumerate(rr):
    x=720+ci*155;y=240+ri*155;s.rect(x,y,150,150,'#edf3e9'if n==5 else '#fffdf8',radius=8);s.text(x+75,y+58,n,42,anchor='middle',weight=700)
    for k in range(n):s.circle(x+38+(k%3)*36,y+88+(k//3)*16,5,'#fff'if n%2 else '#2c4338',meta=f'data-luoshu="{n}"')
  s.text(640,785,'전통 방위: 위 남 · 아래 북 · 왼쪽 동 · 오른쪽 서  |  백점 홀수 · 흑점 짝수',25,anchor='middle')
 elif kind=='bagua':
  s=SVG(p,1040);cx,cy=640,570;rad=340
  for i in range(8):
   a=math.pi+i*math.pi/4;b=math.pi+(i+1)*math.pi/4
   x1,y1=cx+math.cos(a)*rad,cy+math.sin(a)*rad;x2,y2=cx+math.cos(b)*rad,cy+math.sin(b)*rad
   d=math.hypot(x2-x1,y2-y1);ux,uy=(x2-x1)/d,(y2-y1)/d
   inset=min(130/abs(ux) if ux else 9999,40/abs(uy) if uy else 9999)+6
   s.line(x1+ux*inset,y1+uy*inset,x2-ux*inset,y2-uy*inset,'#879d88',3,True)
  directions=['동','동남','남','서남','서','서북','북','동북'];angles=[math.pi,5*math.pi/4,3*math.pi/2,7*math.pi/4,0,math.pi/4,math.pi/2,3*math.pi/4]
  for i,(lab,a)in enumerate(zip(p['diagram']['labels'],angles)):
   x=cx+math.cos(a)*rad;y=cy+math.sin(a)*rad;s.rect(x-130,y-40,260,80);s.text(x,y-12,f'{i+1} · {directions[i]}',21,'#667f70','middle');s.text(x,y+22,lab,23,anchor='middle',weight=700)
  s.text(cx,cy-12,'후천팔괘',34,anchor='middle',weight=700);s.text(cx,cy+34,'끝 → 다시 시작',25,anchor='middle')
 else:
  # Named comparison cards; labels correspond to visible concepts, not new puns.
  labels=p['diagram']['labels'];n=len(labels);cols=3 if n>4 else 2;w=1160/cols;h=270
  for i,lab in enumerate(labels):
   x=55+(i%cols)*(w+12);y=165+(i//cols)*302;s.rect(x,y,w-4,h);s.multiline(x+25,y+45,lab,width=15,size=25)
   if pid=='s09x04':
    if i in [0,2]:
     s.circle(x+w*.39,y+155,48,'#dae7d7');s.circle(x+w*.61,y+155,48,'#728d7c');s.line(x+w*.3,y+220,x+w*.7,y+220,'#426f60',7)
    elif i==1:s.line(x+65,y+170,x+w-65,y+170,'#426f60',4,True);s.line(x+w-65,y+205,x+65,y+205,'#426f60',4,True)
    elif i==3:
     for dx in [70,200]:s.rect(x+dx,y+110,100,110,'#dce7da');s.line(x+dx+50,y+115,x+dx+50,y+215,'#426f60',4)
    else:
     for dx,hh in [(65,65),(130,105),(220,105),(285,65)]:s.rect(x+dx,y+225-hh,35,hh,'#6c8b78')
   elif pid=='s09x13':
    captions=[['주색: 장부의 본색','객색: 계절의 시색'],['목의 청색 ↔ 목의 현맥','색맥상득'],['수의 침맥 → 목의 청색','수생목'],['금의 부맥 → 목의 청색','금극목'],['청·적: 목생화','청·황: 목극토']]
    for j,cap in enumerate(captions[i]):s.text(x+25,y+160+j*45,cap,23)
   elif pid=='s09x15':
    captions=[['간목 → 비토','전변 전에 비를 받침'],['폐금의 어미 = 비토','허즉보기모'],['간목의 자식 = 심화','실즉사기자'],['태과가 주원인','억강 중심'],['불급이 주원인','부약 중심']]
    for j,cap in enumerate(captions[i]):s.text(x+25,y+160+j*45,cap,23)
 s.save(p)
print(f'Wrote {len(P)} SVG diagrams; existing image files unchanged.')
