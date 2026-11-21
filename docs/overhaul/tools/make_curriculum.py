"""curriculum.json 첫 판 생성(한 번만). 이후 정본은 src/lessons/curriculum.json 이고 손으로 고친다."""
import json, sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/91c49767-1855-5af0-baa3-ba9f1f0c98dc/scratchpad/p1')
from seed import SECTIONS, CHAPTERS

def I(lid, level=2, **kw):
    d = {"lesson": lid, "level": level}
    for k in ("prereq", "see_also"):
        if k in kw: d[k] = kw[k]
    if "sub" in kw: d["sub"] = kw["sub"]
    if "note" in kw: d["note"] = kw["note"]
    return d

P = {}   # sec_id -> items
P["ch01-s1"] = [
  I("new-etc-01", 1, sub="先秦 · 漢 · 晉"), I("hist-01a", sub="先秦 · 漢 · 晉"), I("hist-01b", sub="先秦 · 漢 · 晉"),
  I("hist-02a", sub="南北朝 · 隋"), I("hist-02b", sub="南北朝 · 隋"),
  I("hist-03a", sub="唐"), I("hist-03b", sub="唐"),
  I("hist-04", sub="宋"), I("new-etc-02", sub="宋"), I("new-etc-03", sub="宋"), I("hist-05a", sub="宋"),
  I("hist-06a", sub="金 · 元"), I("hist-06b", sub="金 · 元"), I("hist-05b", sub="金 · 元 → 明 · 淸 本草書", prereq=["hist-05a"]),
  I("hist-07a", sub="鍼灸書 · 혈 수 계보", see_also=["new-gr-02", "new-gr-31", "new-gr-32"]), I("hist-07b", sub="鍼灸書 · 혈 수 계보", prereq=["hist-07a"]),
  I("hist-08a", sub="明 · 淸"), I("hist-08b", sub="明 · 淸", prereq=["hist-08a"]), I("hist-09", sub="明 · 淸"), I("hist-10", sub="明 · 淸"),
  I("new-etc-04", sub="方書 계보(통시)"),
]
P["ch01-s2"] = [I("hist-11", 1), I("hist-12"), I("hist-13"), I("hist-14")]
P["ch02-s1"] = [I("yyox-01", 1), I("yyox-05", prereq=["yyox-03"]), I("new-uk-01", 3, prereq=["yyox-01"])]
P["ch02-s2"] = [I("yyox-02", 1), I("new-uk-04", prereq=["yyox-02"]), I("new-uk-06", prereq=["yyox-02"]),
                I("new-uk-03", 3, prereq=["yyox-02"]), I("new-uk-05", 3, prereq=["yyox-02"])]
P["ch02-s3"] = [I("yyox-03", 1), I("yyox-04"), I("new-uk-07", note="교재 줄 근거 약함 — 확인 필요", see_also=["yyox-06"]),
                I("yyox-07"), I("yyox-08"), I("yyox-09"), I("yyox-10", prereq=["yyox-08"])]
P["ch02-s4"] = [I("yyox-11", 1), I("yyox-12", prereq=["yyox-11"]), I("yyox-13", prereq=["yyox-11"])]
P["ch03-s1"] = [I("yyox-14", 1), I("new-uk-08", prereq=["yyox-14"]), I("new-uk-09", prereq=["new-uk-08"]),
                I("new-uk-10", prereq=["yyox-14"]), I("new-uk-11", prereq=["new-uk-10"]), I("new-uk-12", prereq=["new-uk-11"]),
                I("new-uk-13", 3, prereq=["new-uk-08", "new-uk-11"]), I("new-uk-14", prereq=["new-uk-10"]), I("new-uk-15")]
P["ch04-s0"] = [I("new-jq-01", 1), I("new-jq-02", 1)]
P["ch04-s1"] = [I("new-jq-03", 1), I("new-jq-04"), I("new-jq-05")]
P["ch04-s2"] = [I("new-jq-12", 1), I("new-jq-13"), I("new-jq-14"), ]
P["ch04-s3"] = [I("new-jq-06", 1), I("new-jq-07"), I("new-jq-08"), I("new-jq-09", prereq=["new-jq-06"]),
                I("new-jq-10", prereq=["new-jq-06"]), I("new-jq-11", prereq=["new-jq-06"])]
P["ch04-s4"] = [I("new-jq-16", 1), I("new-jq-17")]
P["ch04-s5"] = [I("new-jq-18", 1), I("new-jq-19")]
P["ch04-s6"] = [I("new-jq-20"), I("new-jq-21"), I("new-jq-22"), I("new-jq-23", 3, prereq=["new-jq-02"])]
P["ch05-s1"] = [I("new-gr-01", 1)]
P["ch05-s2"] = [I("new-gr-02", see_also=["hist-07a", "hist-07b"])]
P["ch05-s3"] = [I("new-gr-04", 1)]
P["ch05-s4"] = [I("new-gr-03")]
P["ch05-s5"] = [I("new-gr-39"), I("new-gr-40", see_also=["new-etc-15"]), I("new-gr-18")]
P["ch05-s6"] = [
  I("mer-02", 1, sub="1. 개념 · 분포"), I("mer-04", sub="1. 개념 · 분포"), I("new-gr-08", sub="1. 개념 · 분포"),
  I("new-gr-07", 1, sub="2. 流注"), I("new-gr-35", sub="2. 流注"), I("new-gr-09", 3, sub="2. 流注", prereq=["new-gr-07"]),
] + [I("new-gr-%d" % i, 3, sub="2. 流注 — 원문", prereq=["new-gr-07"]) for i in range(42, 48)] + [
  I("new-gr-10", 1, sub="3. 是動 · 所生"), I("mer-03", sub="3. 是動 · 所生", prereq=["new-gr-10"]), I("new-gr-11", sub="3. 是動 · 所生", prereq=["new-gr-10"]),
  I("new-gr-15", sub="4. 標本 · 根結 · 氣街"),
  I("new-gr-31", sub="經穴圖 · 혈 수"), I("new-gr-32", sub="經穴圖 · 혈 수"),
  I("new-gr-36", sub="經穴圖 · 혈 수", note="骨度는 교재 본문에 없다(사용자 기본서)"), I("new-gr-41", 3, sub="經穴圖 · 혈 수"),
]
P["ch05-s7"] = [I("new-gr-05", sub="1. 經別 · 4. 經筋"), I("new-gr-12", 1, sub="3. 奇經八脈"),
                I("new-gr-13", sub="3. 奇經八脈", prereq=["new-gr-12"]), I("new-gr-14", sub="3. 奇經八脈", prereq=["new-gr-12"]),
                I("new-gr-06", sub="5. 皮部")]
P["ch05-s8"] = [I("mer-05", 1, sub="五腧穴"), I("mer-06", sub="五腧穴", prereq=["mer-05"]), I("new-gr-16", sub="五腧穴", prereq=["mer-05"]),
                I("mer-09", sub="特殊穴"), I("mer-10", sub="特殊穴"), I("new-gr-33", sub="特殊穴"), I("new-gr-34", sub="特殊穴", prereq=["new-gr-33"]),
                I("mer-08", sub="特殊穴"), I("mer-07", sub="特殊穴"), I("mer-13", sub="特殊穴"), I("new-gr-37", sub="特殊穴"),
                I("new-gr-17", sub="常用穴"), I("new-gr-38", sub="常用穴")]
P["ch05-x1"] = [I("mer-11", prereq=["mer-06"]), I("mer-12", prereq=["mer-11"])]
P["ch06-s0"] = [I("new-zj-01", 1)]
P["ch06-s1"] = [
  I("new-zj-02", sub="1. 肝 · 膽"), I("zds-01", sub="1. 肝 · 膽"),
  I("new-zj-03", sub="2. 心 · 小腸"), I("zds-02", sub="2. 心 · 小腸"),
  I("new-zj-04", sub="3. 脾 · 胃"), I("zds-03", sub="3. 脾 · 胃"),
  I("new-zj-05", sub="4. 肺 · 大腸"), I("zds-04", sub="4. 肺 · 大腸"),
  I("new-zj-06", sub="5. 腎 · 膀胱"), I("zds-05", sub="5. 腎 · 膀胱"),
  I("new-zj-07", sub="6. 命門", prereq=["new-zj-06"]),
  I("new-zj-08", sub="本神(五臟 공통)"), I("new-jq-15", sub="本神(五臟 공통)", prereq=["new-jq-13"]),
  I("new-zj-09", sub="六腑 · 7. 三焦"), I("new-zj-10", sub="六腑 · 7. 三焦"),
  I("new-zj-11", sub="9. 奇恒之府"),
  I("new-zj-13", sub="10. 臟腑 사이의 관계"), I("new-zj-14", sub="10. 臟腑 사이의 관계"),
  I("new-zj-12", sub="11. 七衝門"),
  I("new-zj-15", 3, sub="대조표 · 원문"), I("zds-06", 3, sub="대조표 · 원문"),
]
P["ch07-s1"] = [I("new-etc-05", 1), I("hp-08"), I("hp-09"), I("hp-10"), I("new-etc-08", prereq=["hp-08"]),
                I("hp-11"), I("new-etc-06", prereq=["hp-11"]), I("hp-13"), I("new-etc-07", prereq=["hp-13"]), I("hp-12")]
P["ch08-s1"] = [I("hp-14", 1)]
P["ch08-s2"] = [I("hp-15"), I("new-etc-10", prereq=["hp-15"]), I("hp-16", 3, prereq=["hp-15"]), I("hp-17")]
P["ch08-s3"] = [I("hp-18"), I("new-etc-11", prereq=["hp-18"])]
P["ch08-s4"] = [I("new-etc-12")]
P["ch08-s5"] = [I("hp-19")]
P["ch08-s7"] = [I("new-etc-09")]
P["ch09-s1"] = [I("zds-13", 1)]
P["ch09-s2"] = [I("zds-07", 3, sub="臟腑辨證"), I("zds-08", 3, sub="臟腑辨證"),
                I("zds-14", sub="外感熱病 — 六經"), I("zds-15", sub="外感熱病 — 六經", prereq=["zds-14"]),
                I("new-etc-29", 3, sub="外感熱病 — 六經", prereq=["zds-14"]), I("new-etc-30", 3, sub="外感熱病 — 六經", prereq=["zds-14", "zds-15"]),
                I("zds-16", sub="外感熱病 — 衛氣營血"), I("new-etc-31", sub="外感熱病 — 三焦", prereq=["zds-16"])]
P["ch10-s1"] = [I("new-etc-13", 1)]
P["ch10-s2"] = [I("hp-01", 1), I("yyox-06", prereq=["yyox-03"], see_also=["new-uk-07"]), I("hp-02"), I("new-etc-17", prereq=["hp-01"]),
                I("new-etc-14"), I("new-etc-16"), I("new-etc-15", prereq=["new-etc-14"], see_also=["new-gr-40"]), I("hp-03"), I("new-etc-18")]
P["ch10-s3"] = [I("hp-04", 1)]
P["ch10-s4"] = [I("new-etc-19"), I("new-etc-20"), I("new-etc-21"), I("new-etc-22"), I("hp-05")]
P["ch11-s0"] = [I("hp-06", 1), I("new-etc-23"), I("new-etc-24"), I("hp-07"), I("new-etc-25"), I("new-etc-26")]
P["ch12-s1"] = [
  I("new-zj-16", 1, sub="望診"), I("zds-09", sub="望診"), I("zds-10", sub="望診"), I("new-zj-17", sub="望診"),
  I("new-zj-18", sub="望診 — 舌診"), I("new-zj-19", sub="望診 — 舌診", prereq=["new-zj-18"]), I("new-zj-20", sub="望診 — 舌診", prereq=["new-zj-18"]), I("new-zj-21", sub="望診 — 舌診", prereq=["new-zj-18"]),
  I("new-zj-22", sub="聞診"),
  I("zds-11", sub="問診"), I("new-zj-23", sub="問診"), I("new-zj-24", sub="問診"), I("new-zj-25", sub="問診"),
  I("new-zj-26", 1, sub="切診"), I("zds-12", sub="切診"), I("new-zj-27", sub="切診", prereq=["new-zj-26"]), I("new-zj-28", sub="切診", prereq=["new-zj-26"]),
  I("new-uk-02", 3, sub="切診", prereq=["new-zj-26"]), I("new-zj-29", sub="切診 — 觸診"),
]
P["ch13-s1"] = [I("new-etc-27", 1), I("new-etc-28")]

GAPS = {  # 제목 수준 예비 판정(6-6절) — 내용 대조 전
  "base": "기본상식(동서의학 차이 · 整體觀念 · 辨證論治) 과 없음",
  "ch07-s2": "發病原理 과 없음",
  "ch08-s0": "장 머리(基本病機 개관) 과 없음 — 病機十九條는 7절로",
  "ch08-s6": "經絡病機 과 없음",
  "ch08-s7": "臟腑病機는 病機十九條 1과뿐",
  "ch09-s1": "氣血辨證 과 없음(八綱만)",
  "ch09-s2": "臟腑辨證은 감별 2과뿐 · 經絡辨證 · 體質辨證 과 없음",
  "ch13-s2": "八法 과 없음(消 · 淸만 13장 1절 과에 섞임)",
  "ch13-s3": "藥物外治法 과 없음",
  "ch14-s0": "證候 鑑別 과 없음",
  "ch15-s1": "鍼灸 과 없음(刺法은 5장 5절)",
  "ch15-s2": "內科 ~ 推拿 과 없음",
  "ch16-s1": "養生 · 豫防 과 없음",
  "app-1": "年代簡表 · 時代別 醫家 정리 과 없음 — 의학사 시험과 바로 닿음",
  "app-2": "인체 部位 名稱 과 없음",
}

secs = list(SECTIONS)
# 5장 7절 뒤 腧穴 정리(교재 2024~2114행은 7절 범위 안이지만 經別~皮部 다음에 붙은 腧穴 정리)
i7 = [k for k, s in enumerate(secs) if s[1] == "ch05-s7"][0]
s7 = secs[i7]
secs[i7] = (s7[0], s7[1], s7[2], s7[3], 1889, 2023, None)
secs.insert(i7 + 1, ("ch05", "ch05-s8", "(7절 뒤) 腧穴 — 五腧穴 · 特殊穴 · 常用穴", None, 2024, 2114, None))

out = {"book": "한의학개론(理知 아카데미)", "version": "2026-11-20",
       "source": "목차 = 교재 目次(원문 p.5). 줄 번호 = 한의학개론_p001-250_최종.txt. 배치 근거 = docs/overhaul/P1_placement.md",
       "levels": {"0": "공용 사전", "1": "총론", "2": "각론", "3": "감별 · 혼동 · 원문 · 표 인출"},
       "chapters": []}
for ch, (title, page) in CHAPTERS.items():
    C = {"id": ch, "title": title, "page": page, "sections": []}
    for s in secs:
        if s[0] != ch: continue
        S = {"id": s[1], "title": s[2]}
        if s[3]: S["page"] = s[3]
        if s[4]: S["lines"] = [s[4], s[5]]
        if s[6]: S["note"] = s[6]
        if s[1] in GAPS: S["gap"] = GAPS[s[1]]
        S["items"] = P.get(s[1], [])
        C["sections"].append(S)
    out["chapters"].append(C)
out["shelf"] = [{"lesson": "new-gr-%d" % i, "why": "舍岩 12경 방 그림 — 표 트레이너(P2)로 대체 예정. 그동안 여기서 볼 수 있다"} for i in range(19, 31)]
json.dump(out, open('/home/claude/s7/work/src/lessons/curriculum.json', 'w'), ensure_ascii=False, indent=1)
n = sum(len(S["items"]) for C in out["chapters"] for S in C["sections"]) + len(out["shelf"])
print("items", n)
