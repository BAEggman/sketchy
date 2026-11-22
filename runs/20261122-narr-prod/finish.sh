#!/bin/bash
# 사용: finish.sh <lid>  (wav는 /mnt/user-data/uploads/.../prod_<lid>.wav)
set -e
cd /home/claude/work
l=$1
cp /mnt/user-data/uploads/sketchy_opus/narr_pilot/prod_$l.wav runs/20261122-narr-prod/wav/$l.full.wav
python3 runs/20261122-narr-prod/ingest.py $l runs/20261122-narr-prod/wav/$l.full.wav | tail -1
python3 src/lessons/build_player.py 2>&1 | tail -1
echo $l >> runs/20261122-narr-prod/done.txt
git add -A
git -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "낭독 본녹음: $l

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MmBfjBsLabvgD3akaViY5Y"
git log --oneline | head -1
