#!/bin/bash
# zjob.sh LID prep|paste|accept EID [extra zone_paste args]
L=$1; C=$2; E=$3; shift 3; D=/home/claude/zt/job/$L; W=/home/claude/work
case $C in
prep)
  cd $W && python3 -I src/lessons/tools/zone_prep.py $D/cur.png $D/edits.json $E $D >/dev/null
  cp $D/$E.jpg $D/${L}_$E.jpg
  python3 -I -c "import json;j=json.load(open('$D/$E.json'));print('ASPECT',j['aspect']);print('PROMPT',j['prompt_en'])"
  echo "SHA sha256:$(sha256sum $D/${L}_$E.jpg | cut -d' ' -f1):$D/${L}_$E.jpg" ;;
paste)
  IN=/mnt/user-data/uploads/sketchy_opus/zone_test/${L}_$E.jpeg
  read X Y WW H < <(python3 -I -c "import json;j=json.load(open('$D/$E.json'));print(*j['crop'])")
  REG=$(python3 -I -c "import json;j=json.load(open('$D/$E.json'));print(' '.join('--region '+','.join(map(str,r)) for r in j['region']))")
  cd $W && python3 -I src/lessons/tools/zone_paste.py $D/cur.png $IN $X $Y $WW $H $D/cur_$E.png $REG "$@"
  python3 -I -c "
from PIL import Image
a=Image.open('$D/cur.png').crop(($X,$Y,$X+$WW,$Y+$H)); b=Image.open('$D/cur_$E.png').crop(($X,$Y,$X+$WW,$Y+$H))
s=Image.new('RGB',(a.width*2+10,a.height),'white'); s.paste(a,(0,0)); s.paste(b,(a.width+10,0))
r=1000/s.width; s.resize((1000,int(s.height*r))).save('$D/prev_$E.png')"
  echo "PREVIEW $D/prev_$E.png" ;;
accept) cp $D/cur_$E.png $D/cur.png; echo "ACCEPTED $E" ;;
esac
