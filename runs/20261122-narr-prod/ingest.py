import json,sys,re,subprocess,hashlib
from pathlib import Path
R=Path('/home/claude/work'); lid=sys.argv[1]; wav=Path(sys.argv[2])
L=json.loads((R/f'src/lessons/l/{lid}.json').read_text())
sts=L['stations']; N=len(sts)
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
m=json.loads((R/'audio/narration/manifest.json').read_text())
head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,cwd=R).stdout.strip()
img=sha((R/L['image']).read_bytes()); full=sha(wav.read_bytes())
for st,(a,b) in zip(sts,bounds):
    text=st['tts']; th=sha(text.encode())
    name=f"{lid}__s{st['n']}__{th[:12]}.mp3"
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{max(a-0.1,0):.3f}','-to',f'{b+0.25:.3f}','-i',str(wav),'-ac','1','-b:a','96k',str(R/'audio/narration'/name)],check=True)
    ab=(R/'audio/narration'/name).read_bytes()
    m['records'][f"{lid}#{st['n']}"]={'src':f'audio/narration/{name}','text':text,'text_sha256':th,'audio_sha256':sha(ab),'image_sha256':img,'source_commit':head,
      'station_sha256':sha(json.dumps(st,ensure_ascii=False,sort_keys=True).encode()),'original_wav_sha256':full,'original_wav_filename':wav.name}
    print(st['n'],f'{b-a:.1f}s',len(text),'chars',name)
(R/'audio/narration/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=1))
