#!/usr/bin/env python3
"""make_tts.js의 파이썬 완전 이식판 — node가 없는 환경에서 qoaq HanjaSong.toReading과 동일한 한글 독음 tts를 생성한다.

    python3 src/lessons/tools/carbon/make_tts.py src/lessons/l/hist-02a.json ...
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
HJ_URO = (HERE / 'hj_uro.txt').read_text(encoding='utf-8')
URO_BASE, URO_END = 0x4E00, 0x9FFF

COMPAT = {
    '﨎': '쌍', '﨏': '곡', '﨑': '기', '﨓': '부', '﨔': '거', '﨟': '알',
    '﨡': '생', '﨣': '두', '﨤': '급', '﨧': '효', '﨨': '행', '﨩': '도', '女': '여'
}
EXT = {
    '䐜': '진', '㾦': '배', '㾆': '배', '㿠': '황', '㑊': '역',
    '㿉': '퇴', '䀮': '황', '䐃': '균', '䐢': '추', '䱐': '포', '䪼': '졸'
}
DOMAIN = {
    '惡寒': '오한', '惡熱': '오열', '惡風': '오풍', '惡心': '오심', '惡阻': '오조', '惡露': '오로',
    '惡血': '악혈', '惡瘡': '악창', '善惡': '선악',
    '數脈': '삭맥', '脈數': '맥삭', '細數': '세삭', '洪數': '홍삭', '滑數': '활삭', '弦數': '현삭',
    '浮數': '부삭', '沈數': '침삭', '虛數': '허삭', '實數': '실삭', '促數': '촉삭', '頻數': '빈삭',
    '疾數': '질삭', '數急': '삭급', '小便頻數': '소변빈삭',
    '大便': '대변', '小便': '소변', '大小便': '대소변', '便秘': '변비', '便血': '변혈', '便溏': '변당',
    '便閉': '변폐', '便通': '변통', '二便': '이변', '溏便': '당변', '後便': '후변', '膿血便': '농혈변',
    '更年': '갱년', '相殺': '상쇄', '炙甘草': '자감초', '癥瘕': '징가', '噦': '얼',
    '瘈瘲': '계종', '口喎': '구와', '喎斜': '와사', '塞因塞用': '색인색용', '閉塞': '폐색', '壅塞': '옹색',
    '通因通用': '통인통용', '寒因寒用': '한인한용', '熱因熱用': '열인열용',
    '不足': '부족', '不定': '부정', '不斷': '부단', '不當': '부당', '不調': '부조',
    '則': '즉', '法則': '법칙', '原則': '원칙', '規則': '규칙', '準則': '준칙', '四則': '사칙',
    '鐵則': '철칙', '總則': '총칙', '細則': '세칙', '變則': '변칙',
    '兪穴': '수혈', '腧穴': '수혈', '五腧穴': '오수혈', '五輸穴': '오수혈',
    '背兪': '배수', '五兪': '오수', '肺兪': '폐수', '心兪': '심수', '肝兪': '간수',
    '脾兪': '비수', '腎兪': '신수', '膽兪': '담수', '胃兪': '위수', '膈兪': '격수', '厥陰兪': '궐음수',
    '三焦兪': '삼초수', '大腸兪': '대장수', '小腸兪': '소장수', '膀胱兪': '방광수', '氣海兪': '기해수',
    '關元兪': '관원수', '督兪': '독수', '兪': '수', '俞': '수', '腧': '수',
    '五臟六腑': '오장육부', '六氣': '육기', '六淫': '육음', '六腑': '육부', '六經': '육경',
    '六經辨證': '육경변증', '六味地黃湯': '육미지황탕', '六君子湯': '육군자탕', '六鬱': '육울',
    '六極': '육극', '六節': '육절', '六元': '육원', '六化': '육화', '六微旨大論': '육미지대론',
    '六律': '육률', '六腑者': '육부자', '十六': '십육', '六月': '유월', '十月': '시월',
    '辨證論治': '변증논치', '論治': '논치', '醫論': '의론', '傷寒論': '상한론', '溫熱論': '온열론',
    '理氣': '이기', '理法方藥': '이법방약', '腠理': '주리', '條理': '조리', '病理': '병리', '生理': '생리',
    '裏證': '이증', '表裏': '표리', '裏急後重': '이급후중', '表裏關係': '표리관계', '裏熱': '이열',
    '裏寒': '이한', '半表半裏': '반표반리', '利水': '이수', '利尿': '이뇨', '通利': '통리', '痢疾': '이질',
    '下痢': '하리',
    '列缺': '열결', '排列': '배열', '分列': '분열', '厲兌': '여태', '廉泉': '염천', '瘰癧': '나력',
    '癃閉': '융폐', '淋證': '임증', '淋瀝': '임력', '五淋': '오림', '足臨泣': '족임읍', '頭臨泣': '두임읍',
    '虛勞': '허로', '勞倦': '노권', '五勞': '오로', '勞宮': '노궁', '勞則氣耗': '노즉기모',
    '老人': '노인', '衰老': '쇠로', '冷汗': '냉한', '冷痛': '냉통', '虛冷': '허랭', '冷積': '냉적',
    '凉血': '양혈', '淸凉': '청량', '凉燥': '양조', '辛凉': '신량', '良方': '양방', '不良': '불량',
    '兩儀': '양의', '兩虛': '양허', '龍骨': '용골', '小靑龍湯': '소청룡탕', '大靑龍湯': '대청룡탕',
    '龍膽瀉肝湯': '용담사간탕', '流注': '유주', '子午流注': '자오유주', '留飮': '유음', '類經': '유경',
    '經絡': '경락', '絡脈': '낙맥', '絡穴': '낙혈', '別絡': '별락', '浮絡': '부락', '孫絡': '손락',
    '刺絡': '자락', '十五絡': '십오락', '霍亂': '곽란', '靈樞': '영추', '靈道': '영도', '承靈': '승령',
    '尿血': '요혈', '遺尿': '유뇨', '尿閉': '요폐', '歷節': '역절', '五輪': '오륜', '輪廓': '윤곽',
    '戰慄': '전율', '女子': '여자', '男女': '남녀', '婦女': '부녀',
}
DOMAIN_KEYS = sorted(DOMAIN.keys(), key=len, reverse=True)
DOMAIN_MAX = len(DOMAIN_KEYS[0]) if DOMAIN_KEYS else 0

PRE = [
    ('葉天士', '섭천사'), ('葉桂', '섭계'), ('戾氣', '려기'), ('沈金鰲', '심금오'), ('沈氏', '심씨'),
    ('金永碩', '김영석'), ('金永錫', '김영석'), ('醫方類聚', '의방유취'), ('鄭禮男', '정예남'),
    ('角徵宮商羽', '각치궁상우'), ('소리 徵', '소리 치'), ('所惡', '소오'), ('四問便', '사문변'),
    ('實在易', '실재이'), ('惡濕', '오습'), ('惡燥', '오조'), ('惡熱', '오열'), ('惡風', '오풍'),
    ('惡寒', '오한'), ('說言乎兌', '열언호태'), ('醋炒則斂', '초초즉렴'),
    ('人蔘惡萊菔子', '인삼오내복자'), ('生薑惡黃芩', '생강오황금'), ('相惡', '상오'), ('相殺', '상살'),
    ('丹參', '단삼'), ('玄參', '현삼'), ('沙參', '사삼'), ('苦參', '고삼'), ('人參', '인삼'),
    ('五參', '오삼'), ('다섯 參', '다섯 삼'), ('杜仲', '두충'), ('黨參', '당삼'),
    ('善行而數變', '선행이삭변'), ('數變', '삭변'), ('易襲陽位', '이습양위'), ('易襲陰位', '이습음위'),
    ('易傷陽氣', '이상양기'), ('著痺', '착비'), ('易耗傷津液', '이모상진액'), ('易傷津液', '이상진액'),
    ('易傷肺', '이상폐'), ('易動血', '이동혈'), ('熱極易生風', '열극이생풍'), ('參附湯', '삼부탕'),
    ('汗稀而涼', '한희이량'), ('少氣懶言', '소기나언'),
]
ALT = {
    '惡': ['오', '악'], '說': ['열', '설', '세'], '樂': ['락', '악', '요'],
    '復': ['복', '부'], '數': ['수', '삭'], '便': ['편', '변'],
    '易': ['역', '이'], '行': ['행', '항'], '降': ['강', '항']
}
HAN_RE = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')


def is_hanja(ch):
    c = ord(ch)
    return (URO_BASE <= c <= URO_END) or (0xF900 <= c <= 0xFAFF) or (0x3400 <= c <= 0x4DBF)


def base_reading(ch):
    c = ord(ch)
    if 0xF900 <= c <= 0xFAFF:
        if ch in COMPAT:
            return COMPAT[ch]
        u = unicodedata.normalize('NFD', ch)
        if len(u) == 1 and u != ch:
            return base_reading(u)
        return None
    if URO_BASE <= c <= URO_END:
        r = HJ_URO[c - URO_BASE]
        return None if r == '\x00' else r
    return EXT.get(ch)


def normalize_hanja(s):
    out = []
    for ch in s:
        if 0xF900 <= ord(ch) <= 0xFAFF and ch not in COMPAT:
            u = unicodedata.normalize('NFD', ch)
            out.append(u if len(u) == 1 else ch)
        else:
            out.append(ch)
    return ''.join(out)


def decomp(s):
    c = ord(s[0]) - 0xAC00
    if c < 0 or c > 11171:
        return None
    return [c // 588, (c % 588) // 28, c % 28]


def comp(L, V, T):
    return chr(0xAC00 + L * 588 + V * 28 + T)


def dueum(syl, hanja_ch=''):
    if hanja_ch and hanja_ch in '衄呂':
        return syl
    d = decomp(syl)
    if not d:
        return syl
    iy = d[1] in (2, 3, 6, 7, 12, 17, 19, 20)
    if d[0] == 5:
        return comp(11 if iy else 2, d[1], d[2])
    if d[0] == 2 and iy:
        return comp(11, d[1], d[2])
    return syl


def hwarumjo(prev, cur):
    if cur not in ('렬', '률'):
        return cur
    p = decomp(prev)
    if not p:
        return cur
    if p[2] in (0, 4):
        return '열' if cur == '렬' else '율'
    return cur


def bu_rule(nxt):
    d = decomp(nxt)
    return bool(d and d[0] in (3, 4, 12, 13))


def to_reading(src):
    src = normalize_hanja(str(src))
    out, unknown = [], []
    i, n = 0, len(src)
    run_start = True
    while i < n:
        ch = src[i]
        if not is_hanja(ch):
            out.append(ch)
            if re.match(r'[\s\u3000·,，.。;；:：!！?？()（）\[\]「」『』"\'/|\-—~]', ch):
                run_start = True
            elif '가' <= ch <= '힣':
                run_start = False
            i += 1
            continue
        hit = None
        for L in range(min(DOMAIN_MAX, n - i), 0, -1):
            key = src[i:i + L]
            if key in DOMAIN:
                hit = (key, DOMAIN[key])
                break
        if hit:
            out.append(hit[1])
            i += len(hit[0])
            run_start = hit[0][-1] in '則而故乃曰云矣也焉兮'
            continue
        r = base_reading(ch)
        if not r:
            unknown.append(ch)
            out.append(ch)
            i += 1
            run_start = False
            continue
        if run_start:
            r = dueum(r, ch)
        elif out and ('가' <= out[-1][-1] <= '힣'):
            r = hwarumjo(out[-1][-1], r)
        if ch == '不' and i + 1 < n:
            nx = src[i + 1]
            nr = base_reading(nx) if is_hanja(nx) else None
            if nr and bu_rule(nr):
                r = '부'
        out.append(r)
        i += 1
        run_start = ch in '則而故乃曰云矣也焉兮'
    return ''.join(out), unknown


def has_batchim(s):
    if not s:
        return False
    c = ord(s[-1])
    return 0xAC00 <= c <= 0xD7A3 and (c - 0xAC00) % 28 != 0


def is_rieul(s):
    if not s:
        return False
    c = ord(s[-1])
    return 0xAC00 <= c <= 0xD7A3 and (c - 0xAC00) % 28 == 8


def same_sound(w, r):
    if w.endswith(r):
        return True
    if not r:
        return False
    c = ord(r[0]) - 0xAC00
    if c < 0 or c > 11171 or c // 588 != 11:
        return False
    rest = c % 588
    return any(w.endswith(chr(0xAC00 + ini * 588 + rest) + r[1:]) for ini in (5, 2))


def fix_particle(r, p):
    if not p:
        return p
    b = has_batchim(r)
    pairs = [('으로', '로'), ('을', '를'), ('은', '는'), ('과', '와'), ('이다', '다'), ('이', '가'), ('아', '야')]
    for with_b, no_b in pairs:
        for cand in (with_b, no_b):
            if p.startswith(cand):
                use = with_b if b else no_b
                if with_b == '으로' and is_rieul(r):
                    use = '로'
                return use + p[len(cand):]
    return p


def convert_text_to_tts(s):
    def repl_paren(m):
        w, h, p = m.group(1), m.group(2), m.group(3)
        r, _ = to_reading(h)
        if same_sound(w, r):
            return w + p
        if len(h) == 1 and any(same_sound(w, x) for x in ALT.get(h, [])):
            return w + p
        return w + ' ' + r + fix_particle(r, p)

    s = re.sub(r'([가-힣]+)\(([\u3400-\u9fff\uf900-\ufaff]+)\)([가-힣]*)', repl_paren, s)
    for k, v in PRE:
        s = s.replace(k, v)
    t, unknown = to_reading(s)
    t = re.sub(r'([가-힣]+)\(\1\)', r'\1', t)
    t = re.sub(r'\(([^()]*)\)(?=[가-힣])', r' \1', t)
    t = re.sub(r'[『』「」★《》〈〉]', '', t)
    t = re.sub(r'\s*[—→↔]\s*', ', ', t)
    t = re.sub(r'\s*·\s*', ', ', t)
    t = re.sub(r'\(\s*', ', ', t)
    t = re.sub(r'\s*\)', ', ', t)
    t = re.sub(r'\s*~\s*', '에서 ', t)
    t = re.sub(r',\s*([,.!?])', r'\1', t)
    t = re.sub(r'(,\s*){2,}', ', ', t)
    t = re.sub(r'\s+([,.!?])', r'\1', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return t, unknown


def process_file(path):
    p = Path(path)
    L = json.loads(p.read_text(encoding='utf-8'))
    bad = 0
    for st in L['stations']:
        s = st.get('say') or st.get('fact') or ''
        t, unk = convert_text_to_tts(s)
        if unk:
            bad += 1
            print(f"{L['id']} #{st['n']}: 독음 모름 {''.join(unk)}")
        if HAN_RE.search(t):
            bad += 1
            print(f"{L['id']} #{st['n']}: 한자가 남음 — {t}")
        st['tts'] = t
    p.write_text(json.dumps(L, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f"{L['id']}: tts {len(L['stations'])}개 완료")
    return bad


if __name__ == '__main__':
    total_bad = 0
    for f in sys.argv[1:]:
        total_bad += process_file(f)
    sys.exit(1 if total_bad else 0)
