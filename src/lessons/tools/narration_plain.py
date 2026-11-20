#!/usr/bin/env python3
"""Deterministic, auditable sentence-ending changes; never truncate content.

The originals live in git and in original_tts/source_station. Only narration is
converted. Exact word substitutions are logged; the package builder separately
checks preservation of quoted mnemonics and source fields.
"""
import re

TOKEN = re.compile(r'[가-힣]+(?:니다|세요|시다|지요)(?=[.!?。…\s\"”’,:;)]|$)')
SPECIAL = {
    '봅시다': '보자', '보세요': '보자', '살펴보세요': '살펴보자',
    '기억하세요': '기억하자', '구별하세요': '구별하자',
    '연결하세요': '연결하자', '떠올리세요': '떠올리자',
    '확인하세요': '확인하자', '복원하세요': '복원하자',
    '주의하세요': '주의하자', '두세요': '두자', '마세요': '말자',
    '짝지으세요': '짝짓자', '아프세요': '아픈가',
    '깁니다': '길다', '다릅니다': '다르다',
    '보겠습니다': '보자', '살펴보겠습니다': '살펴보자',
    '연결하겠습니다': '연결하자', '기억하겠습니다': '기억하자',
    '이어가겠습니다': '이어가자',
    '아닙니다': '아니다', '경이지요': '경이다', '수이지요': '수다',
    '윤장통편이지요': '윤장통편이다',
    '가득합니다': '가득하다', '않습니다': '않는다',
}
ADJECTIVES = {'있습니다','없습니다','같습니다','많습니다',
              '적습니다','짧습니다','무겁습니다'}

def plain_word(word):
    if word in SPECIAL:
        return SPECIAL[word]
    past = word.endswith('습니다') and len(word) > 3 and (ord(word[-4])-0xAC00) % 28 == 20
    if word in ADJECTIVES or past:
        return word[:-3] + '다'
    # Verbs whose ending could otherwise be mistaken for the nominal copula.
    if word in {'보입니다', '놓입니다', '붙입니다', '뜨입니다', '먹입니다'}:
        return word[:-3] + '인다'
    if word.endswith('입니다'):
        noun = word[:-3]
        if not noun:
            return '이다'
        final = (ord(noun[-1])-0xAC00) % 28
        return noun + ('이다' if final else '다')
    if word.endswith('습니다'):
        return word[:-3] + '는다'
    if word.endswith('니다'):
        stem = word[:-2]
        if stem and 0xAC00 <= ord(stem[-1]) <= 0xD7A3:
            code = ord(stem[-1]) - 0xAC00
            if code % 28 == 17:  # ㅂ니다 → ㄴ다; 만듭니다 → 만든다
                return stem[:-1] + chr(ord(stem[-1])-17+4) + '다'
    return word

def convert(text):
    edits = []
    def sub(match):
        before = match.group()
        after = plain_word(before)
        if before != after:
            edits.append({'offset': match.start(), 'before': before, 'after': after})
        return after
    return TOKEN.sub(sub, text), edits

if __name__ == '__main__':
    import json, sys
    print(json.dumps(convert(sys.stdin.read()), ensure_ascii=False))
