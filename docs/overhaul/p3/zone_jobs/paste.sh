#!/bin/bash
# paste.sh EID [extra --region args...]  : cur.png + uploads/EID.jpeg -> cur_EID.png (+ side-by-side preview)
E=$1; shift
cd /home/claude/work
read X Y W H < <(python3 -I -c "import json;j=json.load(open('/home/claude/zt/$E.json'));print(*j['crop'])")
REG=$(python3 -I -c "import json;j=json.load(open('/home/claude/zt/$E.json'));print(' '.join('--region '+','.join(map(str,r)) for r in j['region']))")
python3 -I src/lessons/tools/zone_paste.py /home/claude/zt/cur.png /mnt/user-data/uploads/sketchy_opus/zone_test/$E.jpeg $X $Y $W $H /home/claude/zt/cur_$E.png $REG "$@"
python3 -I -c "
from PIL import Image
a=Image.open('/home/claude/zt/cur.png').crop(($X,$Y,$X+$W,$Y+$H)); b=Image.open('/home/claude/zt/cur_$E.png').crop(($X,$Y,$X+$W,$Y+$H))
s=Image.new('RGB',(a.width*2+10,a.height),'white'); s.paste(a,(0,0)); s.paste(b,(a.width+10,0))
r=900/s.width; s.resize((900,int(s.height*r))).save('/home/claude/zt/prev_$E.png')"
