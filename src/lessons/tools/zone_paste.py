# -*- coding: utf-8 -*-
"""구역 편집 결과를 원본 그림에 다시 붙인다 (2026-11-21, P3 金元 시험).

절차: 원본에서 잘라 Gemini 새 대화에 첨부 → 편집 → 원본 크기로 내려받음 → 이 도구.
- 편집본(보통 2배 크기)을 잘라 낸 구역 크기로 줄인다.
- 위상 상관으로 몇 화소 어긋남을 찾아 맞춘다.
- 바뀐 곳만 붙인다: 흐린 차이 > 문턱인 곳을 넓히고 가장자리를 부드럽게(feather).
  --region x,y,w,h(구역 안 좌표)를 주면 그 상자 안을 통째로 바꾼다(밖의 미세한 다시 그림은 버림). 여러 번 줄 수 있다.
- 결과와 함께 차이 지도(_mask.png)를 남겨 사람이 확인한다.

python3 -I src/lessons/tools/zone_paste.py BASE EDIT x y w h OUT [--region rx,ry,rw,rh ...] [--thr 28] [--grow 18] [--feather 10]
"""
import sys, argparse
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes


def shift_est(a, b):
    """a, b: 회색 float 배열(같은 크기). b를 a에 맞출 정수 이동(dy, dx)."""
    fa = np.fft.fft2(a - a.mean()); fb = np.fft.fft2(b - b.mean())
    r = fa * np.conj(fb); r /= np.abs(r) + 1e-9
    c = np.fft.ifft2(r).real
    dy, dx = np.unravel_index(np.argmax(c), c.shape)
    H, W = a.shape
    if dy > H // 2: dy -= H
    if dx > W // 2: dx -= W
    return int(dy), int(dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('edit')
    ap.add_argument('x', type=int); ap.add_argument('y', type=int); ap.add_argument('w', type=int); ap.add_argument('h', type=int)
    ap.add_argument('out')
    ap.add_argument('--region', action='append', default=[])
    ap.add_argument('--thr', type=float, default=28)
    ap.add_argument('--grow', type=int, default=18)
    ap.add_argument('--feather', type=float, default=10)
    ap.add_argument('--noshift', action='store_true')
    a = ap.parse_args()
    B = Image.open(a.base).convert('RGB')
    crop = np.asarray(B.crop((a.x, a.y, a.x + a.w, a.y + a.h))).astype(float)
    E = Image.open(a.edit).convert('RGB').resize((a.w, a.h), Image.LANCZOS)
    e = np.asarray(E).astype(float)
    dy = dx = 0
    if not a.noshift:
        dy, dx = shift_est(crop.mean(2), e.mean(2))
        if abs(dy) > 40 or abs(dx) > 40:
            dy = dx = 0
        e = np.roll(e, (dy, dx), axis=(0, 1))
    diff = np.abs(gaussian_filter(crop, (3, 3, 0)) - gaussian_filter(e, (3, 3, 0))).mean(2)
    m = diff > a.thr
    m = binary_dilation(m, iterations=a.grow)
    m = binary_fill_holes(m)
    if a.region:
        # 상자를 주면 상자 안을 통째로 바꾼다(지운 자리 · 새 물건이 문턱에 덜 잡히는 것을 막음)
        R = np.zeros_like(m)
        for r in a.region:
            rx, ry, rw, rh = map(int, r.split(','))
            R[ry:ry + rh, rx:rx + rw] = True
        m = R
    # 구역 테두리 쪽은 원본을 지킨다(이음매 방지)
    edge = np.zeros_like(m); g = 6
    edge[:g, :] = edge[-g:, :] = edge[:, :g] = edge[:, -g:] = True
    m &= ~edge
    M = gaussian_filter(m.astype(float), a.feather)[..., None]
    out = crop * (1 - M) + e * M
    Bn = np.asarray(B).astype(float).copy()
    Bn[a.y:a.y + a.h, a.x:a.x + a.w] = out
    Image.fromarray(np.clip(Bn, 0, 255).astype('uint8')).save(a.out)
    vis = (np.clip(M[..., 0], 0, 1) * 255).astype('uint8')
    Image.fromarray(vis).save(a.out.rsplit('.', 1)[0] + '_mask.png')
    print(f'shift dy={dy} dx={dx} · 바뀐 넓이 {100 * m.mean():.1f}% · 저장 {a.out}')


if __name__ == '__main__':
    main()
