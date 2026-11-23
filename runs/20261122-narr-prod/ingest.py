import json,sys,re,subprocess,hashlib,os
# 2026-11-23 음성 분리: mp3는 별도 저장소 sketchy-audio의 사본 폴더에 쓰고, manifest src는 온전한 주소.
# 새 녹음은 48kbps 모노. 같은 이름이 이미 있으면(다시 녹음) _v2, _v3 … 판 번호를 붙인다 — 올린 파일은 덮지 않는다.
AUDIO_DIR=__import__('pathlib').Path(os.environ.get('SKETCHY_AUDIO_DIR','/home/claude/sketchy-audio'))
AUDIO_BASE='https://baeggman.github.io/sketchy-audio/'
BITRATE='48k'
from pathlib import Path
R=Path('/home/claude/work'); lid=sys.argv[1]; wav=Path(sys.argv[2])
L=json.loads((R/f'src/lessons/l/{lid}.json').read_text())
SEL=[int(x) for x in sys.argv[3:]]  # 선택 인자: 정거장 번호(n). 없으면 과 전체
sts=[s for s in L['stations'] if (not SEL or s['n'] in SEL)]; N=len(sts)
if SEL and N!=len(SEL): sys.exit(f'FAIL 정거장 번호 {SEL} 중 없는 것이 있다')
sha=lambda b:hashlib.sha256(b).hexdigest()
out=subprocess.run(['ffmpeg','-hide_banner','-i',str(wav),'-af','silencedetect=noise=-45dB:d=2.6','-f','null','-'],capture_output=True,text=True).stderr
dur=float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',out).group(1))*3600+float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',out).group(2))*60+float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',out).group(3))
ss=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',out)]
se=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',out)]
if len(ss)!=N-1 or len(se)!=N-1: sys.exit(f'FAIL gaps {len(ss)} != {N-1}')
bounds=[]; a=0.0
for i in range(N):
    b=ss[i] if i<N-1 else dur
    bounds.append((a,b)); 
    if i<N-1: a=se[i]
if not (AUDIO_DIR/'.git').is_dir(): sys.exit(f'FAIL 음성 사본 폴더 {AUDIO_DIR}가 git 저장소가 아니다 — git clone https://github.com/BAEggman/sketchy-audio.git {AUDIO_DIR}')
m=json.loads((R/'audio/narration/manifest.json').read_text())
head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,cwd=R).stdout.strip()
img=sha((R/L['image']).read_bytes()); full=sha(wav.read_bytes())
for st,(a,b) in zip(sts,bounds):
    text=st['tts']; th=sha(text.encode())
    base=f"{lid}__s{st['n']}__{th[:12]}"; name=base+'.mp3'; v=1
    used={r['src'].rsplit('/',1)[-1] for r in m['records'].values()}
    while (AUDIO_DIR/name).exists() or (R/'audio/narration'/name).exists() or name in used:
        v+=1; name=f'{base}_v{v}.mp3'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{max(a-0.1,0):.3f}','-to',f'{b+0.25:.3f}','-i',str(wav),'-ac','1','-b:a',BITRATE,str(AUDIO_DIR/name)],check=True)
    ab=(AUDIO_DIR/name).read_bytes()
    m['records'][f"{lid}#{st['n']}"]={'src':AUDIO_BASE+name,'text':text,'text_sha256':th,'audio_sha256':sha(ab),'image_sha256':img,'source_commit':head,
      'station_sha256':sha(json.dumps(st,ensure_ascii=False,sort_keys=True).encode()),'original_wav_sha256':full,'original_wav_filename':wav.name}
    print(st['n'],f'{b-a:.1f}s',len(text),'chars',name)
(R/'audio/narration/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=1))
