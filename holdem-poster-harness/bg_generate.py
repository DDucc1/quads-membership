#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
절차적 배경 생성기 — 프랙탈 노이즈 기반.
외부 이미지 없이(저작권 클린) 테마별 히어로 배경을 합성한다.
현재: flame_blue(푸른 불꽃 기둥 + 연기). 다른 테마는 ramp/형상만 바꾸면 확장 가능.
"""
import sys, math
import numpy as np
from PIL import Image

W, H = 1080, 1800

def value_noise(h, w, cells, seed):
    rng = np.random.default_rng(seed)
    g = (rng.random((cells, cells)) * 255).astype("uint8")
    return np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), dtype=float) / 255.0

def value_noise_xy(h, w, cy, cx, seed):
    """세로/가로 셀 수를 따로 줘서 방향성 있는 노이즈(예: 세로 줄무늬 = 불꽃 혀)."""
    rng = np.random.default_rng(seed)
    g = (rng.random((cy, cx)) * 255).astype("uint8")
    return np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), dtype=float) / 255.0

def fbm(h, w, seed, octaves=6):
    out = np.zeros((h, w)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        cells = 2 ** (o + 1) + 1
        out += amp * value_noise(h, w, cells, seed + o * 7)
        tot += amp; amp *= 0.55
    return out / tot

def ramp(t, stops):
    """t(0..1) → RGB. stops=[(pos,(r,g,b))...] 정렬됨."""
    t = np.clip(t, 0, 1)
    r = np.zeros_like(t); g = np.zeros_like(t); b = np.zeros_like(t)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]; p1, c1 = stops[i + 1]
        m = (t >= p0) & (t <= p1)
        f = (t[m] - p0) / max(1e-6, (p1 - p0))
        r[m] = c0[0] + (c1[0] - c0[0]) * f
        g[m] = c0[1] + (c1[1] - c0[1]) * f
        b[m] = c0[2] + (c1[2] - c0[2]) * f
    return np.stack([r, g, b], -1)

def flame_blue(seed=11):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    nx = (xx - W / 2) / (W * 0.5)
    ny = yy / H

    # 가로 워프(노이즈로 기둥을 좌우로 흔들어 유기적 윤곽)
    warp = (fbm(H, W, seed + 100, 5) - 0.5) * 0.55
    nxw = nx + warp

    # 불꽃 기둥 마스크: 아래로 넓어짐 + 워프
    width = 0.12 + 0.26 * ny
    col = np.exp(-(nxw / width) ** 2)
    # 세로 프로파일: 중상단(0.30) 피크, 위·아래로 감쇠
    vert = np.clip(1.1 - np.abs(ny - 0.30) / 0.42, 0, 1) ** 1.3

    # 불꽃 혀: 세로 줄무늬 노이즈(가로 셀 많고 세로 셀 적음)
    licks = value_noise_xy(H, W, 10, 70, seed + 5)
    licks = (licks + value_noise_xy(H, W, 20, 130, seed + 9)) / 2
    # 난류 디테일
    turb = fbm(H, W, seed, 6)

    flame = col * vert
    flame *= (0.25 + 1.15 * licks) * (0.45 + 0.95 * turb)  # 텍스처가 형상을 지배
    flame = np.clip(flame * 2.1, 0, 1) ** 1.15             # 감마로 코어 과노출 억제

    # 연기: 저주파 푸른 회색
    smoke = fbm(H, W, seed + 60, 5)
    smoke = np.clip((smoke - 0.42) * 1.9, 0, 1) * (0.3 + 0.5 * vert)

    base_bg = np.array([4, 8, 18]) / 255.0
    # 컬러램프: 화이트 비중을 줄여 시안 위주(중앙 가독 확보)
    fcol = ramp(flame, [
        (0.00, (4, 8, 18)), (0.20, (10, 26, 64)), (0.42, (22, 84, 170)),
        (0.66, (46, 152, 230)), (0.86, (118, 206, 252)), (1.0, (190, 230, 255)),
    ]) / 255.0
    scol = np.array([60, 100, 145]) / 255.0

    img = base_bg[None, None, :] * np.ones((H, W, 1))
    img = 1 - (1 - img) * (1 - fcol)                          # screen 불꽃
    img = img + scol[None, None, :] * smoke[..., None] * 0.22  # 연기
    # 미세 스파크(상승 입자)
    rng = np.random.default_rng(seed + 200)
    sp = rng.random((H, W))
    spark = (sp > 0.9993).astype(float) * col * vert
    img = img + spark[..., None] * np.array([0.8, 0.95, 1.0])[None, None, :]
    img = np.clip(img, 0, 1)

    # 비네팅
    r = np.sqrt(nx ** 2 + ((ny - 0.34) * 1.25) ** 2)
    vig = np.clip(1.05 - (r - 0.5) * 0.85, 0.4, 1.0)
    img *= vig[..., None]

    return Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB")

def ribbon_bg(stops, ribbons, seed, vcenter=0.32, vstr=0.9, star=(0.7, 0.6, 0.8)):
    yy, xx = np.mgrid[0:H, 0:W].astype(float); nx = xx / W; ny = yy / H
    img = (ramp(ny, stops) / 255.0).copy()
    for ang, freq, amp, width, color, gain in ribbons:
        ca, sa = math.cos(ang), math.sin(ang)
        u = nx * ca + ny * sa; v = -nx * sa + ny * ca
        center = 0.5 + amp * np.sin(freq * math.pi * (u * 2 - 0.5))
        band = np.exp(-((v - center) / width) ** 2) * gain
        band *= (0.6 + 0.6 * fbm(H, W, seed + 200 + int(abs(ang) * 100), 5))
        col = np.array(color) / 255.0
        img = 1 - (1 - img) * (1 - col[None, None, :] * band[..., None])
    rng = np.random.default_rng(seed + 50)
    sp = (rng.random((H, W)) > 0.9994).astype(float)
    img = img + sp[..., None] * np.array(star)[None, None, :]
    r = np.sqrt(((nx - 0.5) * 1.1) ** 2 + ((ny - vcenter) * 1.2) ** 2)
    img = img * np.clip(1.06 - (r - 0.45) * vstr, 0.38, 1.0)[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB")

def vglow_bg(stops, glow_color, seed, gx=0.5, gw=0.18, turb=False, ray=False):
    """중앙 세로 발광(스포트라이트/도어) 배경."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float); nx = (xx - W * gx) / (W * 0.5); ny = yy / H
    img = (ramp(ny, stops) / 255.0).copy()
    width = gw + 0.10 * ny
    col = np.exp(-(nx / width) ** 2)
    vert = np.clip(1.1 - np.abs(ny - 0.34) / 0.5, 0, 1) ** 1.1
    g = col * vert
    if turb: g *= (0.5 + 0.9 * fbm(H, W, seed, 6))
    g = np.clip(g * 1.7, 0, 1)
    c = np.array(glow_color) / 255.0
    img = 1 - (1 - img) * (1 - c[None, None, :] * g[..., None])
    if ray:
        for k in range(7):
            a = (k - 3) * 0.16
            rr = np.exp(-((nx - a * ny) / 0.02) ** 2) * np.clip(1 - ny, 0, 1) * 0.25
            img = 1 - (1 - img) * (1 - c[None, None, :] * rr[..., None])
    r = np.sqrt(nx ** 2 + ((ny - 0.34) * 1.25) ** 2)
    img = img * np.clip(1.05 - (r - 0.5) * 0.85, 0.4, 1.0)[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB")

def radial_bg(stops, glow_color, seed, cx=0.5, cy=0.28, rad=0.5):
    """우주/네뷸라 — 라디얼 발광 + 별."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float); nx = xx / W; ny = yy / H
    img = (ramp(ny, stops) / 255.0).copy()
    r = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    neb = np.clip(1 - r / rad, 0, 1) ** 1.6 * (0.5 + 0.8 * fbm(H, W, seed, 6))
    c = np.array(glow_color) / 255.0
    img = 1 - (1 - img) * (1 - c[None, None, :] * neb[..., None])
    rng = np.random.default_rng(seed + 9)
    img = img + (rng.random((H, W)) > 0.9985).astype(float)[..., None] * np.array([0.8, 0.85, 1.0])
    img = img + (rng.random((H, W)) > 0.99965).astype(float)[..., None] * np.array([1.0, 1.0, 1.0])
    rr = np.sqrt(((nx - 0.5) * 1.05) ** 2 + ((ny - cy) * 1.15) ** 2)
    img = img * np.clip(1.05 - (rr - 0.5) * 0.7, 0.4, 1.0)[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB")

def series_purple(s=3):
    return ribbon_bg([(0.0, (58, 20, 96)), (0.45, (40, 14, 74)), (1.0, (16, 7, 34))],
        [(-0.55, 2.1, 0.10, 0.045, (190, 90, 230), 0.9), (-0.40, 1.5, 0.14, 0.075, (120, 70, 220), 0.7),
         (-0.62, 2.8, 0.08, 0.030, (230, 150, 250), 0.8), (-0.30, 1.2, 0.18, 0.110, (70, 40, 150), 0.5)], s)

def series_red(s=7):
    return ribbon_bg([(0.0, (74, 16, 22)), (0.45, (44, 10, 14)), (1.0, (16, 4, 6))],
        [(-0.55, 2.0, 0.10, 0.05, (240, 70, 60), 0.9), (-0.42, 1.4, 0.14, 0.085, (200, 40, 40), 0.7),
         (-0.62, 2.7, 0.08, 0.03, (255, 150, 110), 0.8), (-0.30, 1.1, 0.18, 0.12, (130, 24, 28), 0.5)],
        s, star=(0.9, 0.7, 0.6))

def series_blue(s=5):
    return ribbon_bg([(0.0, (14, 34, 78)), (0.45, (8, 20, 50)), (1.0, (3, 7, 22))],
        [(-0.55, 2.1, 0.10, 0.05, (70, 160, 252), 0.95), (-0.42, 1.4, 0.14, 0.085, (40, 110, 235), 0.7),
         (-0.62, 2.7, 0.08, 0.03, (160, 210, 255), 0.85), (-0.30, 1.1, 0.18, 0.12, (24, 60, 150), 0.5)], s)

def ocean_teal(s=8):
    return ribbon_bg([(0.0, (16, 70, 78)), (0.4, (8, 44, 52)), (1.0, (3, 18, 24))],
        [(0.06, 2.6, 0.06, 0.06, (90, 220, 205), 0.9), (0.10, 1.8, 0.09, 0.10, (50, 170, 165), 0.7),
         (0.02, 3.4, 0.05, 0.035, (170, 245, 235), 0.8), (0.14, 1.3, 0.12, 0.14, (20, 90, 95), 0.5)],
        s, vcenter=0.25, star=(0.7, 0.9, 0.85))

def space_blue(s=2):
    return radial_bg([(0.0, (10, 18, 44)), (0.5, (6, 11, 30)), (1.0, (2, 4, 12))], (70, 150, 240), s)

def golden_door(s=4):
    return vglow_bg([(0.0, (16, 12, 6)), (0.5, (8, 6, 3)), (1.0, (2, 2, 2))], (255, 188, 78), s,
        gw=0.14, turb=True, ray=True)

GENERATORS = {"flame_blue": flame_blue, "series_purple": series_purple, "series_red": series_red,
              "series_blue": series_blue, "ocean_teal": ocean_teal, "space_blue": space_blue,
              "golden_door": golden_door}

if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "flame_blue"
    out = sys.argv[2] if len(sys.argv) > 2 else f"assets/bg/{theme}.jpg"
    GENERATORS[theme]().save(out, quality=90)
    print("saved", out)
