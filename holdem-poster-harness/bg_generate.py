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

def series_purple(seed=3):
    """추상 광선 리본 — 딥퍼플 배경에 흐르는 마젠타/바이올렛 곡선광 (시리즈 컨셉)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    nx = xx / W; ny = yy / H

    # 베이스 세로 그라데이션 (상단 진보라 → 하단 암자주)
    base = ramp(ny, [(0.0, (58, 20, 96)), (0.45, (40, 14, 74)),
                     (1.0, (16, 7, 34))]) / 255.0

    img = base.copy()
    ribbons = [
        # (angle, freq, amp, width, color, gain)
        (-0.55, 2.1, 0.10, 0.045, (190, 90, 230), 0.9),
        (-0.40, 1.5, 0.14, 0.075, (120, 70, 220), 0.7),
        (-0.62, 2.8, 0.08, 0.030, (230, 150, 250), 0.8),
        (-0.30, 1.2, 0.18, 0.110, (70, 40, 150), 0.5),
    ]
    for ang, freq, amp, width, color, gain in ribbons:
        ca, sa = math.cos(ang), math.sin(ang)
        u = nx * ca + ny * sa
        v = -nx * sa + ny * ca
        center = 0.5 + amp * np.sin(freq * math.pi * (u * 2 - 0.5))
        band = np.exp(-((v - center) / width) ** 2) * gain
        # 노이즈로 리본에 질감
        band *= (0.6 + 0.6 * fbm(H, W, seed + 200 + int(abs(ang) * 100), 5))
        col = np.array(color) / 255.0
        img = 1 - (1 - img) * (1 - col[None, None, :] * band[..., None])

    # 미세 입자/별
    rng = np.random.default_rng(seed + 50)
    sp = (rng.random((H, W)) > 0.9994).astype(float)
    img = img + sp[..., None] * np.array([0.7, 0.6, 0.8])[None, None, :]

    # 비네팅 (가장자리·하단 어둡게 → 표/텍스트 패널 대비)
    r = np.sqrt(((nx - 0.5) * 1.1) ** 2 + ((ny - 0.32) * 1.2) ** 2)
    vig = np.clip(1.06 - (r - 0.45) * 0.9, 0.38, 1.0)
    img = img * vig[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype("uint8"), "RGB")

GENERATORS = {"flame_blue": flame_blue, "series_purple": series_purple}

if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "flame_blue"
    out = sys.argv[2] if len(sys.argv) > 2 else f"assets/bg/{theme}.jpg"
    GENERATORS[theme]().save(out, quality=90)
    print("saved", out)
