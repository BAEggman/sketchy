# -*- coding: utf-8 -*-
"""hist_ledger.json 검사: 모든 hanja(사람 · 책 · 字號 · 이표기 · 기관 · 묶음 · 왕조)와
facts 글 속 한자 덩어리가 ref 줄(±2행) 안에 글자 그대로 있는지 본다.

    python3 -I check_ledger.py [hist_ledger.json]

source가 workbook인 사실 · ref_wb · source workbook 字號는 문제집 줄로 본다. 어긋난 것을 한 줄씩 찍고,
어긋남 수를 마지막 줄에 찍는다. 어긋남이 있으면 종료 코드 1.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "hist_ledger.json")
TB = "/mnt/user-data/uploads/refs/교재/_txt/한의학개론_p001-250_최종.txt"
WB = "/mnt/user-data/uploads/refs/교재/_txt/한의학개론_문제집_정답_최종수정본_전체.txt"
WIN = 2
CJK = "㐀-䶿一-鿿豈-﫿"
CHUNK = re.compile(f"[{CJK}]+")

L = json.load(open(LEDGER, encoding="utf-8"))
FILES = {"textbook": open(TB, encoding="utf-8").read().split("\n"),
         "workbook": open(WB, encoding="utf-8").read().split("\n")}
bad = []

def window(which, refs):
    lines = FILES[which]
    out = []
    for r in refs:
        if not isinstance(r, int) or r < 1 or r > len(lines):
            out.append(None); continue
        out.append("".join(lines[max(0, r - 1 - WIN):min(len(lines), r + WIN)]))
    return out

def need_each(owner, what, s, refs, which):
    """s가 refs 줄마다(각 ±2) 있어야 한다."""
    if not s: return
    if not refs:
        bad.append(f"{owner} · {what} 「{s}」: ref 없음"); return
    for r, w in zip(refs, window(which, refs)):
        if w is None:
            bad.append(f"{owner} · {what} 「{s}」: {which} {r}행 범위 밖")
        elif s not in w:
            bad.append(f"{owner} · {what} 「{s}」: {which} {r}행 ±{WIN}에 없음")

def need_any_chunks(owner, what, text, refs, which):
    """text의 한자 덩어리 하나하나가 refs 창(합집합) 안에 있어야 한다."""
    if not refs:
        bad.append(f"{owner} · {what}: ref 없음"); return
    ws = window(which, refs)
    if any(w is None for w in ws):
        bad.append(f"{owner} · {what}: {which} {refs} 범위 밖"); return
    pool = "\n".join(ws)
    for c in CHUNK.findall(text):
        if c not in pool:
            bad.append(f"{owner} · {what} 「{c}」: {which} {refs} ±{WIN}에 없음  ← {text[:60]}")

def which_of(src): return "workbook" if src == "workbook" else "textbook"

def check_entity(e, label):
    oid = e["id"]
    h = e.get("hanja")
    if h:
        if e.get("ref"): need_each(oid, f"{label} hanja", h, e["ref"], "textbook")
        if e.get("ref_wb"): need_each(oid, f"{label} hanja", h, e["ref_wb"], "workbook")
        if not e.get("ref") and not e.get("ref_wb"):
            bad.append(f"{oid} · {label} hanja 「{h}」: ref · ref_wb 모두 없음")
    elif not e.get("name_ko"):
        bad.append(f"{oid}: hanja도 name_ko도 없음")
    if e.get("name_ko") and not h:
        # 한글 이름은 사실 줄에 있어야 한다
        pool_refs = [(f["ref"], which_of(f["source"])) for f in e.get("facts", [])]
        if not any(e["name_ko"] in (w or "") for refs, wh in pool_refs for w in window(wh, refs)):
            bad.append(f"{oid} · name_ko 「{e['name_ko']}」: 사실 ref 줄 어디에도 없음")
    if e.get("dynasty") and e.get("dynasty_basis") in ("명시", "절제목", "workbook"):
        wh = "workbook" if e["dynasty_basis"] == "workbook" else "textbook"
        dt = e.get("dynasty_text") or e["dynasty"]   # dynasty_text = 교재가 한글로 쓴 왕조(예: 「원」)
        pool = "\n".join(w or "" for w in window(wh, e.get("dynasty_ref", [])))
        for r, w in zip(e.get("dynasty_ref", []), window(wh, e.get("dynasty_ref", []))):
            if w is None or dt not in w:
                bad.append(f"{oid} · {label} 왕조 「{dt}」: {wh} {r}행 ±{WIN}에 없음")
    for z in e.get("zi_hao", []):
        need_each(oid, f"字號({z['kind']})", z["hanja"], z["ref"], which_of(z.get("source")))
    for v in e.get("variants", []):
        need_each(oid, "이표기", v["hanja"], v["ref"], "textbook")
    for k, f in enumerate(e.get("facts", [])):
        need_any_chunks(oid, f"facts[{k}]({f['kind']})", f["text"], f["ref"], which_of(f["source"]))

for e in L["people"]: check_entity(e, "사람")
for e in L["books"]: check_entity(e, "책")
for e in L["institutions"]: check_entity(e, "기관")
for g in L["groups"]:
    need_any_chunks(g["id"], "묶음 이름", g["hanja"], g["ref"], "textbook")

# 내부 연결
ids = {e["id"] for c in ("people", "books", "institutions") for e in L[c]}
for e in L["people"]:
    for b in e["books"]:
        if b not in ids: bad.append(f"{e['id']} · books: 없는 id {b}")
for e in L["books"]:
    for a in [e.get("author")] + e.get("co_authors", []):
        if a and a not in ids: bad.append(f"{e['id']} · author: 없는 id {a}")
for g in L["groups"]:
    for m in g["members"]:
        if m not in ids: bad.append(f"{g['id']} · members: 없는 id {m}")
for m in L["missing_in_lessons"]:
    if m["item"] not in ids: bad.append(f"missing_in_lessons: 없는 id {m['item']}")

for b in bad: print(b)
print(f"어긋남 {len(bad)}")
sys.exit(1 if bad else 0)
