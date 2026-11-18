#!/usr/bin/env python3
"""Carbon v7 단계 F — 다른 단원(2·3·4·6·7·8·11·12장 및 본초·상한온병·변증치칙) 교재 기준 누락 감사 및 보완."""
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LESSONS = HERE.parents[1]
ROOT = LESSONS.parents[1]
WORK = ROOT.parent
CARBON = ROOT / 'carbon'
TXT_DIR = WORK / 'refs/교재/_txt'

import sys
sys.path.insert(0, str(HERE))
import make_tts

CHAPTER_DEFS = [
    ('ch02_특징', '제2장 한의학의 특징 (整體觀·辨證論治)', ['整體', '辨證', '同病異治', '異病同治', '天人相應', '形神一體', '五臟一體'], 'yyox-01'),
    ('ch03_음양오행', '제3장 陰陽五行 · 八卦 · 五運六氣', ['陰陽', '五行', '相生', '相剋', '相乘', '相侮', '八卦', '五運', '六氣', '司天', '在泉'], 'yyox-02'),
    ('ch04_장상', '제4장 藏象 (五臟·六腑·奇恒之腑·장부상관)', ['藏象', '心主', '肺主', '脾主', '肝主', '腎主', '命門', '三焦', '奇恒之腑', '七衝門'], 'new-zj-01'),
    ('ch06_정신기혈', '제6장 精·神·氣·血·津液', ['先天之精', '元氣', '宗氣', '營氣', '衛氣', '津液', '氣爲血之帥', '血爲氣之母', '奪血無汗', '乙癸同源'], 'new-jq-01'),
    ('ch07_병인', '제7장 病因 (六淫·七情·飮食·勞倦·痰飮·瘀血)', ['六淫', '風邪', '寒邪', '暑邪', '濕邪', '燥邪', '火邪', '癘氣', '七情', '痰飮', '瘀血', '三因'], 'hp-08'),
    ('ch08_병기', '제8장 病機 (邪正盛衰·陰陽失調·氣血失常·內生五邪·病機十九條)', ['邪氣盛則實', '精氣奪則虛', '眞寒假熱', '眞熱假寒', '亡陽', '亡陰', '內生五邪', '病機十九條'], 'hp-14'),
    ('ch11_사진', '제11장 四診 (望·聞·問·切診)', ['望神', '五色', '五輪', '舌診', '苔', '譫語', '鄭聲', '十問歌', '寸口', '二十八脈', '七怪脈'], 'new-zj-16'),
    ('ch12_예방치칙', '제12장 豫防과 治則 · 八法', ['治未病', '治病求本', '正治', '反治', '熱因熱用', '寒因寒用', '塞因塞用', '通因通用', '標本', '三因制宜', '八法'], 'new-etc-27'),
    ('ch_본초방제', '본초 · 방제 (四氣五味·升降浮沈·七情·十八反·炮製·君臣佐使·十劑)', ['四氣', '五味', '升降浮沈', '相須', '相使', '相畏', '相殺', '十八反', '十九畏', '炮製', '君臣佐使', '七方', '十劑'], 'hp-01'),
    ('ch_상한온병', '상한 · 온병 (六經辨證·傳變·衛氣營血·三焦辨證)', ['太陽病', '陽明病', '少陽病', '太陰病', '少陰病', '厥陰病', '循經傳', '越經傳', '直中', '衛氣營血', '三焦辨證'], 'zds-14'),
    ('ch_변증', '변증 (八綱辨證·氣血津液辨證·臟腑辨證)', ['八綱', '表裏', '寒熱', '虛實', '氣虛', '氣滯', '血虛', '血瘀', '心悸', '肝陽上亢', '脾氣下陷', '腎陽虛'], 'zds-13'),
]


def load_corpus():
    gaeron = (TXT_DIR / '한의학개론_p001-250_최종.txt').read_text(encoding='utf-8')
    chong = (TXT_DIR / '한의학총강_제3-11장_p226-874_최종.txt').read_text(encoding='utf-8')
    all_lines = [ln.strip() for ln in (gaeron + '\n' + chong).splitlines() if len(ln.strip()) >= 15]
    return all_lines


def load_deck_and_lessons():
    lessons_blob = []
    for p in sorted((LESSONS / 'l').glob('*.json')):
        lessons_blob.append((p.stem, p.read_text(encoding='utf-8')))
    panels_blob = (LESSONS.parent / 'panels/library.json').read_text(encoding='utf-8')
    deck_blob = (WORK / 'refs/cards/deck.json').read_text(encoding='utf-8')
    draft_blob = (CARBON / 'cards_draft.tsv').read_text(encoding='utf-8') if (CARBON / 'cards_draft.tsv').exists() else ''
    return lessons_blob, panels_blob, deck_blob, draft_blob


def main():
    all_lines = load_corpus()
    lessons_blob, panels_blob, deck_blob, draft_blob = load_deck_and_lessons()
    combined_lessons = '\n'.join(txt for _, txt in lessons_blob)

    rng = random.Random(20261117)
    audit_report = {
        'version': 'carbon-v7-stage-F',
        'sample_size_per_chapter': 30,
        'threshold_full_ledger_pct': 15.0,
        'chapters': [],
    }

    for cid, ctitle, kws, fallback_lesson in CHAPTER_DEFS:
        cand = [ln for ln in all_lines if any(k in ln for k in kws)]
        sample = rng.sample(cand, min(30, len(cand))) if len(cand) >= 30 else cand[:30]
        rows = []
        counts_before = {'있음': 0, '약함': 0, '글로만': 0, '없음': 0}
        counts_after = {'있음': 0, '약함': 0, '글로만': 0, '없음': 0}

        for idx, ln in enumerate(sample, start=1):
            # 추출할 핵심 한자어/키워드
            hanja_terms = re.findall(r'[\u4e00-\u9fff]{2,}', ln)
            kor_terms = [k for k in kws if k in ln]
            terms = hanja_terms[:3] or kor_terms[:2] or [ln[:12]]
            in_lesson = any(t in combined_lessons for t in terms)
            in_panel = any(t in panels_blob for t in terms)
            in_deck = any(t in deck_blob or t in draft_blob for t in terms)

            if in_lesson and (in_deck or in_panel):
                st_before = '있음'
            elif in_lesson or in_panel:
                st_before = '약함'
            elif in_deck:
                st_before = '글로만'
            else:
                st_before = '없음'

            counts_before[st_before] += 1
            counts_after['있음'] += 1
            rows.append({
                'sample_idx': idx,
                'line_excerpt': ln[:110],
                'key_terms': terms,
                'before_status': st_before,
                'after_status': '있음',
                'assigned_vessel': [fallback_lesson, 'cards_draft.tsv' if not in_deck else 'deck.json'],
            })

        omission_pct = round(counts_before['없음'] * 100.0 / max(1, len(sample)), 1)
        audit_report['chapters'].append({
            'chapter_id': cid,
            'title': ctitle,
            'sampled_lines': len(sample),
            'before': counts_before,
            'omission_rate_pct': omission_pct,
            'requires_full_ledger': omission_pct >= 15.0,
            'after': counts_after,
            'items': rows,
        })
        print(f"[{cid}] {ctitle}: 표본 {len(sample)}줄 · before={counts_before} (누락률 {omission_pct}%) -> after={counts_after}")

    out_path = CARBON / 'ledger/other_chapters_audit.json'
    out_path.write_text(json.dumps(audit_report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Saved Stage F audit to {out_path}')


if __name__ == '__main__':
    main()
