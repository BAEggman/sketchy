import json,sys
lid=sys.argv[1]
SEL=[int(x) for x in sys.argv[2:]]  # 선택 인자: 정거장 번호(n). 없으면 과 전체
d=json.load(open(f'src/lessons/l/{lid}.json'))
n={}
for k in 'ABC':
    n.update(json.load(open(f'runs/20261122-narr-audit/reading_notes_{k}.json')))
notes=[]; body=[]
for i,s in enumerate(d['stations']):
    if SEL and s['n'] not in SEL: continue
    for x in n.get(f'{lid}#{i}',[]): notes.append(f'[{s["n"]}번] {x}')
    body.append(f'[{s["n"]}번]\n{s["tts"]}')
N=len(body)
p=("여기서 gemini TTS 를 사용해 아래 대본 %d개를 읽어 줄 수는 없니? 읽기 전에 먼저 대본을 감수해 줘: 한국어 화자가 소리 내어 읽을 때 잘못 읽히거나 다른 말로 들릴 곳(인명·책 이름·약 이름·한자 훈음, 숫자, 연음)을 찾아서 어떻게 읽을지 정해. 단어·순서·내용은 바꾸지 말고 읽는 방법만 정해. 그다음 반드시 Gemini TTS의 Kore 목소리(여성) 한 명으로만, 차분하고 또렷한 한국어 강의체로 녹음하고(다른 목소리로 바꾸지 마), 만든 음성을 다시 재생해서 발음을 확인한 뒤 틀린 곳이 있으면 다시 녹음해 줘. 번호 표시([1번] 등)는 읽지 말고, 각 번호 사이에 약 3초씩 완전한 무음을 넣어서 하나의 WAV 파일(%s.wav)로 만들어 줘. 마지막에 실제로 쓴 목소리 이름, 감수에서 정한 읽기 방법과 재확인 결과를 짧게 적고, 다운로드할 수 있는 WAV 파일로 첨부해 줘. "
 % (N,lid))
if notes: p+="참고할 읽기 메모: "+" / ".join(notes)+" "
p+="대본은 다음과 같아\n\n"+"\n\n".join(body)
open(f'runs/20261122-narr-prod/{lid}'+('_s'+'-'.join(map(str,SEL)) if SEL else '')+'.prompt.txt','w').write(p)
print(json.dumps(p,ensure_ascii=False))
