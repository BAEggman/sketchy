# -*- coding: utf-8 -*-
"""督脈 유주도 시범(pilot-gv) — 코드로 그린 옆모습 유주도 + 재생기 과 JSON

계획서 6-3: 인체 윤곽을 SVG로 두고 경로 · 혈 점 · 방향 화살표를 코드로 그린다. 생성 그림을 좌표 근거로 쓰지 않는다.
- 순행 · 혈명 · 수: 교재 한의학개론 5장 奇經八脈(추출본 1951~1956행), 經穴圖 督脈 GV1~GV28(1841~1842행, 원문 p.88),
  起始-終止 표(1999행: 長强 - 齦交 28혈 · 脊强而折厥 · 諸陽之海), 督脈之絡 = 長强(1917행).
- 혈 위치(척추 높이 · 촌): WHO 표준 경혈 위치(2008)의 일반 기준. 교재 經穴圖 원문 p.88 그림과 칸 단위 대조는 「확인 필요」.
- 이야기: 사용자 기본서 「5장 경락 5월 18일자 수정.docx」 8절 督脈 「외우기」 네 문장을 원문 그대로(괄호 한자는 원문 표기 — 啞門 · 囟會).
- 交會穴 니모닉: 사용자 「교회혈_91_완전니모닉」 ① 督脈 문장 원문 그대로.

실행: python3 src/lessons/tools/make_gv_path.py  → src/lessons/design/pilot-gv/pilot-gv.svg · src/lessons/l/pilot-gv.json
그림(webp)은 qa 쪽 렌더러로 만든다: node src/lessons/tools/render_svg.js src/lessons/design/pilot-gv/pilot-gv.svg images/lessons/pilot-gv.png
"""
import json, math, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
W, H = 2048, 1144

# ── 혈 (교재 經穴圖 순서 · 표기) ─────────────────────────────
GV = [('GV1', '長强', '장강'), ('GV2', '腰兪', '요유'), ('GV3', '腰陽關', '요양관'), ('GV4', '命門', '명문'), ('GV5', '懸樞', '현추'),
      ('GV6', '脊中', '척중'), ('GV7', '中樞', '중추'), ('GV8', '筋縮', '근축'), ('GV9', '至陽', '지양'), ('GV10', '靈臺', '영대'),
      ('GV11', '神道', '신도'), ('GV12', '身柱', '신주'), ('GV13', '陶道', '도도'), ('GV14', '大椎', '대추'), ('GV15', '瘂門', '아문'),
      ('GV16', '風府', '풍부'), ('GV17', '腦戶', '뇌호'), ('GV18', '强間', '강간'), ('GV19', '後頂', '후정'), ('GV20', '百會', '백회'),
      ('GV21', '前頂', '전정'), ('GV22', '顖會', '신회'), ('GV23', '上星', '상성'), ('GV24', '神庭', '신정'), ('GV25', '素髎', '소료'),
      ('GV26', '水溝', '수구'), ('GV27', '兌端', '태단'), ('GV28', '齦交', '은교')]
# 몸통 혈의 척추 높이(棘突 아래) — WHO 2008 일반 기준
SPINE_LV = {'GV3': 'L4', 'GV4': 'L2', 'GV5': 'L1', 'GV6': 'T11', 'GV7': 'T10', 'GV8': 'T9', 'GV9': 'T7', 'GV10': 'T6',
            'GV11': 'T5', 'GV12': 'T3', 'GV13': 'T1', 'GV14': 'C7'}
# 머리 혈: 뒷머리털 경계(0촌) → 앞머리털 경계(12촌) 위의 촌수
HEAD_CUN = {'GV15': 0.5, 'GV16': 1.0, 'GV17': 2.5, 'GV18': 4.0, 'GV19': 5.5, 'GV20': 7.0, 'GV21': 8.5, 'GV22': 10.0, 'GV23': 11.0, 'GV24': 11.5}

STORY = [  # (덮는 혈, 원문 그대로)
    (['GV1', 'GV2', 'GV3', 'GV4', 'GV5'], '장강(長强)처럼 길게 요유(腰兪)히 흐르던 요양관(腰陽關)의 명문(命門)가에 거대한 현추(懸樞) 기둥이 매달려 있었다.'),
    (['GV6', 'GV7', 'GV8', 'GV9', 'GV10', 'GV11', 'GV12', 'GV13', 'GV14'], '척중(脊中)의 중추(中樞) 세력이 근축(筋縮)되어 지양(至陽)의 길로 들어서자, 영대(靈臺)에 모인 신도(神道)들이 신주(身柱)단지 모시듯 도도(陶道)하게 대추(大椎)를 올린다.'),
    (['GV15', 'GV16', 'GV17', 'GV18', 'GV19', 'GV20'], '아문(啞門) 소리 못 내는 풍부(風府)한 뇌호(腦戶)무사가 강간(强間)히 후정(後頂)을 뚫고 백회(百會) 정상의 왕관을 썼다.'),
    (['GV21', 'GV22', 'GV23', 'GV24', 'GV25', 'GV26', 'GV27', 'GV28'], '전정(前頂) 긍긍하며 신회(囟會)를 열어 상성(上星) 장군께 신정(神庭)하게 보고하니, 소료(素髎)한 수구(水溝) 입구에서 태단(兌端)하게 은교(齦交)로운 최후를 맞는다.'),
]
JIAOHUI = '도(陶道)미노 대추(大椎) 두 알에 아문(啞門) 말없이 풍(風府)덩, 뇌(腦戶)리에 백(百會) 불 켜지자 신(神庭)나게 수(水溝)구치며 은(齦交)밀히 모였다.'


# ── 기하 ────────────────────────────────────────────────
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


def sample(seg, n=400):
    pts = [bez(*seg, i / n) for i in range(n + 1)]
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    return pts, acc


def at_frac(seg, f):
    pts, acc = sample(seg)
    target = f * acc[-1]
    for i in range(1, len(acc)):
        if acc[i] >= target:
            r = (target - acc[i - 1]) / max(acc[i] - acc[i - 1], 1e-9)
            a, b = pts[i - 1], pts[i]
            return (a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r), (b[0] - a[0], b[1] - a[1])
    return pts[-1], (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])


# 머리: 뒷머리털 경계 N → 정수리 V (7촌) → 앞머리털 경계 F (5촌)
N, V, F = (792, 318), (952, 92), (1128, 196)
SCALP1 = (N, (720, 262), (790, 92), V)
SCALP2 = (V, (1032, 86), (1104, 128), F)
# 등: C7 아래(대추) ~ 꼬리뼈 끝. 척추 높이별 y
LEVELS = ['C7'] + ['T%d' % i for i in range(1, 13)] + ['L%d' % i for i in range(1, 6)]
Y = {}
y = 404
for lv in LEVELS:
    Y[lv] = y
    y += 26 if lv.startswith(('C', 'T')) else 40
SACRUM_Y, COCCYX_Y = 1000, 1062


def back_x(yy):
    """등선(피부)의 x: 목 오목 · 등 굽음 · 허리 오목 · 엉치를 부드럽게."""
    pts = [(404, 774), (470, 748), (560, 728), (650, 738), (760, 764), (860, 770), (960, 742), (1062, 744)]
    for (y0, x0), (y1, x1) in zip(pts, pts[1:]):
        if y0 <= yy <= y1:
            t = (yy - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return x0 + (x1 - x0) * t
    return pts[-1][1] if yy > pts[-1][0] else pts[0][1]


def point_xy():
    xy = {}
    # 머리 10혈
    for code, cun in HEAD_CUN.items():
        if cun <= 7:
            xy[code], _ = at_frac(SCALP1, cun / 7)
        else:
            xy[code], _ = at_frac(SCALP2, (cun - 7) / 5)
    # 몸통 12혈: 그 척추 棘突 바로 아래(다음 마디와의 사이)
    for code, lv in SPINE_LV.items():
        i = LEVELS.index(lv)
        yy = (Y[lv] + Y[LEVELS[i + 1]]) / 2 if i + 1 < len(LEVELS) else Y[lv] + 20
        xy[code] = (back_x(yy) - 2, yy)
    xy['GV2'] = (back_x(SACRUM_Y) - 4, SACRUM_Y)        # 骶管裂孔
    xy['GV1'] = (back_x(COCCYX_Y) + 18, COCCYX_Y + 22)  # 꼬리뼈 끝과 항문 사이
    # 얼굴 4혈
    xy['GV25'] = (1186, 356)   # 코끝
    xy['GV26'] = (1162, 389)   # 인중 위 1/3
    xy['GV27'] = (1166, 410)   # 윗입술 끝
    xy['GV28'] = (1146, 413)   # 윗입술 안 잇몸(입 안)
    return xy


def svg(blank=False):
    xy = point_xy()
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Noto Sans CJK KR, Noto Sans KR, Apple SD Gothic Neo, sans-serif">')
    a('<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>'
      '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbf7ee"/><stop offset="1" stop-color="#f2ece0"/></linearGradient></defs>')
    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    # 몸 윤곽(옆모습, 오른쪽을 봄)
    body = ('M 792 318 C 720 262 790 92 952 92 C 1032 86 1104 128 1128 196 '        # 뒷머리 → 정수리 → 이마
            'C 1140 240 1146 268 1150 300 C 1166 318 1190 344 1188 360 C 1180 372 1160 374 1158 380 '  # 이마 → 콧등 → 코끝 → 코밑
            'C 1170 396 1174 404 1166 412 C 1156 416 1160 424 1170 430 C 1164 450 1150 470 1124 480 '   # 윗입술 → 입 → 아랫입술 → 턱
            'C 1092 488 1066 492 1052 506 C 1050 540 1060 580 1090 610 '                      # 턱밑 → 목 앞
            'C 1150 650 1170 760 1166 880 C 1162 990 1140 1080 1110 1144 L 690 1144 '        # 가슴 · 배
            'C 700 1110 730 1090 760 1080 C 790 1066 780 1020 760 990 '                        # 엉덩이 · 꼬리 쪽
            + ' '.join('L %.1f %d' % (back_x(yy), yy) for yy in range(1000, 399, -20)) +       # 등선(아래 → 위)
            ' C 776 380 784 350 792 318 Z')
    a(f'<path d="{body}" fill="#f6dcc4" stroke="#b98a64" stroke-width="3"/>')
    # 귀 · 눈 · 척추(희미하게)
    a('<ellipse cx="900" cy="232" rx="26" ry="40" fill="#f1cdb0" stroke="#b98a64" stroke-width="2"/>')
    a('<path d="M 1110 262 q 14 -8 26 0" stroke="#6b4a33" stroke-width="3" fill="none"/><circle cx="1124" cy="268" r="4" fill="#6b4a33"/>')
    for lv in LEVELS:
        yy = Y[lv]
        a(f'<rect x="{back_x(yy) + 22:.0f}" y="{yy - 9}" width="30" height="{18 if lv[0] != "L" else 26}" rx="5" fill="#efe3cf" stroke="#cdb89a" stroke-width="1.5"/>')
        a(f'<text x="{back_x(yy) + 58:.0f}" y="{yy + 5}" font-size="13" fill="#a08a6a">{lv}</text>')
    a(f'<path d="M {back_x(SACRUM_Y - 40) + 20:.0f} {SACRUM_Y - 40} q 22 40 10 {COCCYX_Y - SACRUM_Y + 30}" stroke="#cdb89a" stroke-width="10" fill="none" stroke-linecap="round"/>')
    # 속 갈래(점선): 胞中 → 會陰, 腎에 絡, 心 貫, 腦에 屬
    bao, hui = (930, 1010), (850, 1120)
    a(f'<path d="M {bao[0]} {bao[1]} C 900 1060 880 1100 {hui[0]} {hui[1]}" stroke="#c0392b" stroke-width="4" stroke-dasharray="10 8" fill="none" marker-end="url(#ar)"/>')
    a(f'<circle cx="{bao[0]}" cy="{bao[1]}" r="14" fill="#fff" stroke="#c0392b" stroke-width="3"/><text x="{bao[0] + 22}" y="{bao[1] + 6}" font-size="22" fill="#7a2a20">胞中 출발</text>')
    a(f'<text x="{hui[0] + 18}" y="{hui[1] - 4}" font-size="22" fill="#7a2a20">會陰으로 내려 나옴</text>')
    a(f'<path d="M {hui[0]} {hui[1]} C 800 1130 {xy["GV1"][0] + 30:.0f} {xy["GV1"][1] + 30:.0f} {xy["GV1"][0]:.0f} {xy["GV1"][1]:.0f}" stroke="#c0392b" stroke-width="4" stroke-dasharray="10 8" fill="none"/>')
    kid = (860, Y['L1'])
    a(f'<ellipse cx="{kid[0]}" cy="{kid[1]}" rx="26" ry="38" fill="#e8b4a4" stroke="#a0604c" stroke-width="2"/><text x="{kid[0] + 34}" y="{kid[1] + 7}" font-size="20" fill="#7a2a20">腎에 絡</text>')
    a(f'<path d="M {xy["GV4"][0]:.0f} {xy["GV4"][1]:.0f} L {kid[0] - 26} {kid[1]}" stroke="#c0392b" stroke-width="3" stroke-dasharray="8 7"/>')
    heart = (930, Y['T5'])
    a(f'<path d="M {heart[0]} {heart[1] + 22} c -40 -26 -30 -58 0 -40 c 30 -18 40 14 0 40 z" fill="#e8a39a" stroke="#a0604c" stroke-width="2"/><text x="{heart[0] + 34}" y="{heart[1] + 6}" font-size="20" fill="#7a2a20">心을 貫</text>')
    a(f'<path d="M {xy["GV11"][0]:.0f} {xy["GV11"][1]:.0f} L {heart[0] - 30} {heart[1]}" stroke="#c0392b" stroke-width="3" stroke-dasharray="8 7"/>')
    a('<path d="M 880 160 c 30 -40 110 -40 140 0 c 30 30 10 80 -40 84 c -40 10 -100 0 -100 -84 z" fill="#efd0d6" stroke="#b07c86" stroke-width="2" opacity="0.9"/>')
    a('<text x="905" y="180" font-size="22" fill="#7a2a20">腦에 屬</text>')
    a(f'<path d="M {xy["GV16"][0]:.0f} {xy["GV16"][1]:.0f} C 850 240 880 210 905 196" stroke="#c0392b" stroke-width="3" stroke-dasharray="8 7" fill="none"/>')
    # 겉 경로(실선): 長强 → 등 정중선 → 머리 → 이마 → 코 → 윗입술 → 잇몸
    order = [c for c, _, _ in GV]
    d = 'M ' + ' L '.join('%.1f %.1f' % xy[c] for c in order[:14])
    d += ' L %.1f %.1f' % xy['GV15']
    a(f'<path d="{d}" stroke="#c0392b" stroke-width="7" fill="none" stroke-linejoin="round"/>')
    a('<path d="M %.1f %.1f C %s %s %.1f %.1f C %s %s %.1f %.1f" stroke="#c0392b" stroke-width="7" fill="none"/>' % (
        *xy['GV15'], '%d %d' % (730, 250), '%d %d' % (790, 92), *V, '%d %d' % (1032, 86), '%d %d' % (1104, 128), *F))
    a('<path d="M 1128 196 C 1140 240 1146 268 1150 300 C 1166 318 1190 344 %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="#c0392b" stroke-width="7" fill="none" stroke-linejoin="round"/>' % (
        *xy['GV25'], *xy['GV26'], *xy['GV27'], *xy['GV28']))
    # 방향: 경로 위 작은 화살촉(흐르는 쪽)
    def head(p, q):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
        return f'<path d="M -11 -9 L 11 0 L -11 9 Z" fill="#7a1a10" transform="translate({mx:.1f},{my:.1f}) rotate({ang:.1f})"/>'
    for a_, b_ in [('GV2', 'GV3'), ('GV6', 'GV7'), ('GV11', 'GV12'), ('GV14', 'GV15'), ('GV17', 'GV18'), ('GV21', 'GV22'), ('GV24', 'GV25'), ('GV26', 'GV27')]:
        a(head(xy[a_], xy[b_]))
    # 이야기 네 구간 번호
    for k, (cx2, cy2) in enumerate([(640, 930), (500, 470), (560, 140), (1250, 250)], 1):
        a(f'<circle cx="{cx2}" cy="{cy2}" r="22" fill="#2d7159"/><text x="{cx2}" y="{cy2 + 9}" text-anchor="middle" font-size="26" font-weight="800" fill="#fff">{k}</text>')
    # 혈 점 · 이름표
    for code, hz, ko in GV:
        x, yy = xy[code]
        n = int(code[2:])
        big = code in ('GV1', 'GV4', 'GV14', 'GV16', 'GV20', 'GV26', 'GV28')
        r = 11 if big else 8
        a(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r}" fill="{"#c0392b" if big else "#fff"}" stroke="#c0392b" stroke-width="3"/>')
        if n <= 14:          # 등: 왼쪽으로 이름표
            lx, anchor = x - 30, 'end'
            ly = yy + 7
        elif n <= 20:        # 뒷머리 · 정수리: 바깥(왼쪽 위)
            lx, anchor = x - 24, 'end'
            ly = yy - 2 if n < 20 else yy - 22
            if n == 20:
                lx, anchor = x, 'middle'
        elif n <= 24:        # 앞머리: 오른쪽 위
            lx, anchor = x + 22, 'start'
            ly = yy - 6 if n < 23 else (yy - 12 if n == 23 else yy + 22)
        else:                # 얼굴: 오른쪽으로 끌어냄
            lx, anchor = 1240, 'start'
            ly = {25: 340, 26: 384, 27: 426, 28: 468}[n]
            if not blank: a(f'<path d="M {x + r:.0f} {yy:.0f} L {lx - 8} {ly - 7}" stroke="#7a2a20" stroke-width="1.5"/>')
        if blank: continue
        a(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anchor}" font-size="{25 if big else 22}" fill="#3a2418" font-weight="{700 if big else 500}">'
          f'<tspan fill="#9a7a62" font-size="15" font-weight="500">{code} </tspan>{hz} <tspan font-size="18" fill="#7a5a42">{ko}</tspan></text>')
    # 이야기 소품(작은 그림): 장강 물결 · 명문가 대문 · 현추 기둥 · 대추 두 알 · 백회 왕관 · 상성 별
    def wave(x, y):
        return ''.join(f'<path d="M {x} {y + i * 12} q 12 -10 24 0 t 24 0 t 24 0" stroke="#3a7bd5" stroke-width="4" fill="none"/>' for i in range(3))
    a(wave(470, 1050))
    gx, gy = xy['GV4']; a(f'<g transform="translate({gx - 300:.0f},{gy - 28:.0f})"><rect x="0" y="14" width="52" height="40" fill="#8e5a33"/><path d="M -8 16 L 26 -6 L 60 16 Z" fill="#5c3a22"/><rect x="20" y="30" width="12" height="24" fill="#f1c40f"/></g>')
    px, py = xy['GV5']; a(f'<g transform="translate({px - 270:.0f},{py - 70:.0f})"><line x1="20" y1="0" x2="20" y2="20" stroke="#555" stroke-width="3"/><rect x="8" y="20" width="24" height="58" rx="4" fill="#b08355" stroke="#6b4a33" stroke-width="2"/></g>')
    jx, jy = xy['GV14']; a(f'<g transform="translate({jx - 300:.0f},{jy - 22:.0f})"><ellipse cx="12" cy="16" rx="11" ry="14" fill="#b22222"/><ellipse cx="36" cy="16" rx="11" ry="14" fill="#b22222"/><path d="M 12 2 q 6 -8 12 -2" stroke="#2e7d32" stroke-width="3" fill="none"/></g>')
    cx_, cy_ = xy['GV20']; a(f'<g transform="translate({cx_ - 34:.0f},{cy_ - 78:.0f})"><path d="M 0 30 L 8 0 L 22 18 L 34 0 L 46 18 L 60 0 L 68 30 Z" fill="#f1c40f" stroke="#b7950b" stroke-width="2"/></g>')
    sx, sy = xy['GV23']; a(f'<g transform="translate({sx + 130:.0f},{sy - 64:.0f})"><path d="M 20 0 L 26 14 L 40 14 L 29 23 L 33 38 L 20 29 L 7 38 L 11 23 L 0 14 L 14 14 Z" fill="#f39c12"/></g>')
    # 제목 · 범례
    TX = 1420
    if blank:
        a(f'<text x="{TX}" y="96" font-size="46" font-weight="800" fill="#2b1a10">督脈 — 빈 판</text>')
        a(f'<text x="{TX}" y="140" font-size="24" fill="#5a4030">점마다 혈 이름을 말해 보라(GV1 → GV28)</text>')
        a('</svg>')
        return '\n'.join(o), xy
    a(f'<text x="{TX}" y="96" font-size="46" font-weight="800" fill="#2b1a10">督脈 유주도</text>')
    a(f'<text x="{TX}" y="140" font-size="24" fill="#5a4030">長强(GV1) → 齦交(GV28) · 28혈</text>')
    a(f'<text x="{TX}" y="174" font-size="24" fill="#5a4030">陽脈之海(諸陽之海) · 督總一身之陽經</text>')
    a(f'<text x="{TX}" y="226" font-size="20" fill="#5a4030">실선 = 겉 길(아래 → 위 → 앞 → 입) · 점선 = 속 갈래</text>')
    a(f'<text x="{TX}" y="254" font-size="20" fill="#5a4030">큰 점 = 시험에 자주 묻는 혈 · 초록 번호 = 이야기 구간</text>')
    seg = ['① 長强 → 懸樞 (꼬리 · 허리)', '② 脊中 → 大椎 (등 · 목 아래)', '③ 瘂門 → 百會 (뒷머리 · 정수리)', '④ 前頂 → 齦交 (앞머리 · 얼굴)']
    for k, t in enumerate(seg):
        a(f'<text x="{TX}" y="{560 + k * 40}" font-size="24" fill="#2d7159" font-weight="700">{t}</text>')
    a(f'<text x="{TX}" y="760" font-size="20" fill="#7a2a20">起 胞中 → 會陰 下出 → 背面 正中線 上行</text>')
    a(f'<text x="{TX}" y="790" font-size="20" fill="#7a2a20">腦에 屬 · 腎에 絡 · 心을 貫 · 肝經과 巔에서 만남</text>')
    a(f'<text x="{TX}" y="820" font-size="20" fill="#7a2a20">病症 脊强而折厥 · 督脈之絡 = 長强</text>')
    a('<text x="60" y="1124" font-size="17" fill="#8a7462">혈 위치는 WHO 표준(2008) 기준의 모식도 · 교재 經穴圖(원문 p.88)와 칸 대조는 확인 필요</text>')
    a('</svg>')
    return '\n'.join(o), xy


def bbox(codes, xy, pad=36, extra_left=0):
    xs = [xy[c][0] for c in codes]
    ys = [xy[c][1] for c in codes]
    x0, y0, x1, y1 = min(xs) - pad - extra_left, min(ys) - pad, max(xs) + pad, max(ys) + pad
    return [int(max(0, x0)), int(max(0, y0)), int(min(W, x1) - max(0, x0)), int(min(H, y1) - max(0, y0))]


def lesson(xy):
    st = []
    st.append({'n': 0, 'kind': 'frame', 'obj': '옆모습 인체 — 꼬리뼈 끝에서 등 한가운데를 타고 올라 정수리를 넘어 코 · 윗입술 · 잇몸까지 이어진 붉은 실선, 속으로 胞中 · 會陰 · 腎 · 心 · 腦로 가는 점선',
               'fact': '督脈 — 長强(GV1) → 齦交(GV28) · 28혈 · 陽脈之海(諸陽之海) · 胞中 출발 → 會陰 下出 → 背面正中線 上行 → 骶·腰·項 → 腦에 屬 · 腎에 絡 · 心을 貫',
               'hook': '등 한가운데 한 줄 = 모든 양경을 거느림(督總一身之陽經)',
               'say': '이건 독맥 유주도야. 꼬리뼈 끝 장강에서 출발해서 등 한가운데를 타고 올라가, 정수리를 넘어 이마로 내려와, 코끝, 인중, 윗입술을 지나 잇몸 속 은교에서 끝나. 스물여덟 혈, 양맥지해. 시작은 사실 몸속 포중이고, 회음으로 내려 나왔다가 등으로 올라가. 속으로는 뇌에 속하고, 신에 낙하고, 심을 꿰뚫어.',
               'box': None, 'src': ['교재 1951~1956행', '교재 1999행', '교재 1841~1842행(經穴圖 원문 p.88)']})
    for i, (codes, text) in enumerate(STORY, 1):
        names = ' · '.join(next(h for cc, h, _ in GV if cc == c) for c in codes) + f' ({codes[0]}~{codes[-1][2:]})'
        st.append({'n': i, 'obj': f'붉은 길의 {["", "아래(꼬리 · 허리)", "가운데(등 · 목 아래)", "뒷머리 · 정수리", "앞머리 · 얼굴"][i]} 구간 — ' + ' · '.join(next(h for cc, h, _ in GV if cc == c) for c in codes),
                   'fact': names, 'hook': '이야기 ' + str(i) + ' (사용자 기본서 원문)', 'say': text,
                   'box': bbox(codes, xy, pad=40, extra_left=300 if i <= 2 else 220), 'src': ['사용자 기본서 5장 8절 督脈 외우기', '교재 1841~1842행']})
    st.append({'n': 5, 'obj': '목 아래 큰 점 大椎 — 대추 두 알',
               'fact': '陽經의 經氣 모두가 大椎에서 交會(陽脈之海) · 大椎 = 三陽脈과 督脈의 연계(교재 1677행)',
               'hook': '도미노 대추 두 알 — 交會穴 니모닉(사용자)',
               'say': '목 아래 큰 점이 대추야. 양경의 경기가 모두 여기서 만나. 그래서 독맥이 양맥지해야. 교회혈로 외운 문장: ' + JIAOHUI,
               'box': bbox(['GV13', 'GV14'], xy, pad=50, extra_left=280), 'src': ['교재 1952 · 1677행', '사용자 교회혈_91_완전니모닉 ① 督脈']})
    st.append({'n': 6, 'obj': '정수리 큰 점 百會 — 노란 왕관',
               'fact': '上額與足厥陰交于巔 · 入絡于腦 → 腦 · 肝病이 督脈上에 표현(1954행)',
               'hook': '백회 정상의 왕관(이야기 3) = 간경이 올라와 만나는 꼭대기',
               'say': '정수리 백회야. 이야기에선 뇌호무사가 백회 정상의 왕관을 썼지. 간경이 이마로 올라와 독맥과 바로 이 정수리에서 만나. 그래서 뇌와 간의 병이 독맥 위에 드러나.',
               'box': bbox(['GV19', 'GV20', 'GV21'], xy, pad=70), 'src': ['교재 1954 · 1789행']})
    st.append({'n': 7, 'obj': '꼬리뼈 끝 큰 점 長强 — 물결',
               'fact': '督脈之絡 = 長强(15絡脈, 靈樞 經脈篇 학설) · 起始部 = 小腹以下骨中央 또는 下極之兪(長强) 또는 胞中',
               'hook': '장강처럼 길게 — 시작이자 督脈의 絡穴',
               'say': '꼬리뼈 끝 장강은 독맥이 겉으로 처음 나오는 혈이면서, 독맥의 낙혈이기도 해. 십오낙맥에서 임맥의 낙은 구미, 독맥의 낙은 장강.',
               'box': bbox(['GV1', 'GV2'], xy, pad=60, extra_left=260), 'src': ['교재 1917 · 1955행']})
    st.append({'n': 8, 'kind': 'review', 'obj': '처음부터 끝까지 한 번 — 장강에서 은교까지',
               'fact': '長强 → 腰兪 → 腰陽關 → 命門 → 懸樞 → 脊中 → 中樞 → 筋縮 → 至陽 → 靈臺 → 神道 → 身柱 → 陶道 → 大椎 → 瘂門 → 風府 → 腦戶 → 强間 → 後頂 → 百會 → 前頂 → 顖會 → 上星 → 神庭 → 素髎 → 水溝 → 兌端 → 齦交 · 病症 脊强而折厥',
               'hook': '네 문장 = 네 구간', 'say': ' '.join(t for _, t in STORY) + ' 병증은 척강이절궐, 등이 뻣뻣하고 꺾일 듯해.',
               'box': [0, 0, W, H], 'src': ['교재 1999행', '사용자 기본서 5장 8절']})
    # tts: 한자 · 괄호 한자를 빼고 한글만
    import re
    for s in st:
        t = re.sub(r'\([^)]*[一-鿿][^)]*\)', '', s['say'])
        t = re.sub(r'[一-鿿]+', '', t)
        s['tts'] = re.sub(r'\s+', ' ', t).strip()
    return {'id': 'pilot-gv', 'title': '督脈 유주도 — 長强에서 齦交까지 28혈(시범 · 코드로 그림)', 'place': '옆모습 인체 유주도',
            'image': 'images/lessons/pilot-gv.webp', 'w': W, 'h': H, 'stations': st,
            'attrs': {'pilot': 'P2', 'blank_image': 'images/lessons/pilot-gv-blank.webp', 'drawn_by': 'code (src/lessons/tools/make_gv_path.py)', 'story_src': '사용자 기본서 5장 8절 督脈 외우기 원문',
                      'check': '혈 위치는 WHO 2008 기준 모식도 — 교재 經穴圖 원문 p.88 대조 필요'}}


if __name__ == '__main__':
    s, xy = svg()
    d = os.path.join(ROOT, 'src/lessons/design/pilot-gv')
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'pilot-gv.svg'), 'w', encoding='utf-8').write(s)
    open(os.path.join(d, 'pilot-gv-blank.svg'), 'w', encoding='utf-8').write(svg(blank=True)[0])
    L = lesson(xy)
    json.dump(L, open(os.path.join(ROOT, 'src/lessons/l/pilot-gv.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('written src/lessons/design/pilot-gv/pilot-gv.svg · src/lessons/l/pilot-gv.json — 혈 %d · 정거장 %d' % (len(xy), len(L['stations'])))
