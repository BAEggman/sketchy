# -*- coding: utf-8 -*-
# B4 hist-08a 과 명세 — final.json 원안 + 사용자 결정(11-21 17:55 B4: 물통 A · 남색 · 개 안 넣음 · 자잘한 정리 추천대로 / 17:40 근거 없는 號 · 숫자는 낭독에서 뺌)
# 구역 수정 E1~E3 모두 accept(/home/claude/zt/job/hist-08a/log.md). 해 물통 물은 「절반」보다 높게(테 바로 아래) 그려져 「절반」은 말하지 않음
import json, copy
ROOT = '/home/claude/work/'
F = json.load(open(ROOT + 'runs/20261121-p3-b4/final.json', encoding='utf-8'))
RUN = '20261121-p3-b4'


def base(lid):
    L = copy.deepcopy(F['lessons'][lid])
    return {s['n']: s for s in L['stations']}, L['questions'], L['trainer']


def put(st, n, **kw):
    st[n].update(kw)


out = {}
# ---------------- hist-08a
st, qs, tr = base('hist-08a')
put(st, 2, src=["교재 404–405", "문제집 1105–1107 ②"])
put(st, 4, fact="張介賓(景岳 · 張景岳) 『景岳全書』(溫補派) · 그 안의 「十問篇」",
    say="같은 남색 옷의 張介賓이 깜짝 놀라 펄쩍 뛴다 — 경악, 景岳. 교재는 張介賓(景岳), 張景岳으로 적는다. 장 옆의 경악, 이어 읽으면 張景岳. 치켜든 두꺼운 책과 벽의 책 더미가 전집, 『景岳全書』. 그 안의 「十問篇」은 진단에서 다시 묻는다.",
    tts="같은 남색 옷의 장개빈이 깜짝 놀라 펄쩍 뛴다. 경악, 경악. 교재는 장개빈을 장경악이라고도 적는다. 장 옆의 경악, 이어 읽으면 장경악. 치켜든 두꺼운 책과 벽의 책 더미가 전집, 경악전서. 그 안의 십문편은 진단에서 다시 묻는다.",
    src=["교재 387 · 400 · 416 · 2538"])
put(st, 5, obj="주황 해 물통은 물이 테 아래라 넘치지 않고, 회색 달 물통은 옆으로 쓰러져 텅 빔")
qs[2] = {"q": "칸칸이 나뉜 장 앞 학자와 펄쩍 뛰는 사람이 같은 남색 옷인 까닭과 각 책은?",
         "a": "둘 다 張介賓 — 장(欌) 앞 = 『類經』(內經을 12가지로 분류 주석), 경악 = 景岳(張景岳) 『景岳全書』"}
tr = [t.replace("陳復正은 『幼幼集成』(3877, 문제집 1246 ⑤ 함정)", "陳復正은 『幼幼集成』(교재 410, 문제집 1246–1248 ⑤ 함정)") for t in tr]
tr = [t + " · 景岳을 「號」라 부르는 표기(교재는 「張介賓(景岳)」 387 · 「張景岳」 2538뿐)" if t.startswith("과 JSON에서 내린 말") else t for t in tr]
tr.append("그림: 해 물통 물이 편집문의 「절반」보다 높게(테 바로 아래) 그려짐 — 대본은 「넘치지 않는다」만 말함(E3 log)")
tr.append("물통 A(사용자 17:55): 그림 = 「陽非有餘 眞陰不足」, 「陽常不足而陰常有餘」는 말로 병기 — 둘 다 교재 3862, 한쪽 판정 없음. 介賓 「개 + 빈 통」은 넣지 않음")
box = {1: [740, 530, 640, 590], 2: [1060, 1180, 380, 260], 3: [1390, 370, 760, 870], 4: [2150, 380, 600, 900],
       5: [2140, 1170, 570, 290], 6: [2140, 1160, 270, 290]}
out['hist-08a'] = dict(title="溫補學派 ① — 薛己 · 張介賓(景岳)",
    place="온돌방 아궁이 안채 — 붉은 초롱 넷 = 明 · 아궁이 불이 구들 밑으로 = 溫補(腎陽) · 왼쪽 → 오른쪽 백설기 → 칸칸이 장 → 경악 → 해 · 달 물통",
    st=st, qs=qs, tr=tr, box=box, method="구역 수정 E1~E3(Gemini · zone_paste) — Carbon v7 바탕(images/lessons/hist-08a.webp)",
    notes="구역 편집 E1(접시 → 펼친 작은 책) · E2(두루마리 → 남색 책 · 도포 남색 · 일렉기타 · 이층 버스 지움) · E3(치켜든 붉은 책 · 해 물통 노랑-주황 · 달 물통 쓰러져 빔) 모두 반영(cur.png). 12類 수 부호는 그림에서 지우고 말 · 문항으로. 해 물통 물은 「절반」보다 높아 대본은 「넘치지 않음」만. 景岳 「號」 표기 · 立齋 · 會卿 · 類經 1624 · 「內科 서명 처음」 · 左歸丸/右歸丸 귀속은 근거 줄이 없어 trainer 「확인 필요」. 사용자 단서 薛己 백설기 유지.")

for lid, o in out.items():
    sts = []
    for n in sorted(o['st']):
        s = o['st'][n]
        s['box'] = None if s['kind'] in ('frame', 'review') else o['box'][n]
        sts.append({k: s[k] for k in ('n', 'kind', 'obj', 'fact', 'hook', 'say', 'tts', 'src', 'box')})
    spec = {"title": o['title'], "place": o['place'], "run": RUN, "method": o['method'], "stations": sts,
            "questions": o['qs'], "trainer": o['tr'], "notes": o['notes']}
    json.dump(spec, open(ROOT + 'runs/20261121-p3-b4/built/%s.spec.json' % lid, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(lid, len(sts))
