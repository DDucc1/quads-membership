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

def flame_bg(stops, smoke_col, seed=11):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    nx = (xx - W / 2) / (W * 0.5)
    ny = yy / H
    warp = (fbm(H, W, seed + 100, 5) - 0.5) * 0.55
    nxw = nx + warp
    width = 0.12 + 0.26 * ny
    col = np.exp(-(nxw / width) ** 2)
    vert = np.clip(1.1 - np.abs(ny - 0.30) / 0.42, 0, 1) ** 1.3
    licks = value_noise_xy(H, W, 10, 70, seed + 5)
    licks = (licks + value_noise_xy(H, W, 20, 130, seed + 9)) / 2
    turb = fbm(H, W, seed, 6)
    flame = col * vert
    flame *= (0.25 + 1.15 * licks) * (0.45 + 0.95 * turb)
    flame = np.clip(flame * 2.1, 0, 1) ** 1.15
    smoke = fbm(H, W, seed + 60, 5)
    smoke = np.clip((smoke - 0.42) * 1.9, 0, 1) * (0.3 + 0.5 * vert)
    base_bg = np.array(stops[0][1]) / 255.0
    fcol = ramp(flame, stops) / 255.0
    scol = np.array(smoke_col) / 255.0
    img = base_bg[None, None, :] * np.ones((H, W, 1))
    img = 1 - (1 - img) * (1 - fcol)
    img = img + scol[None, None, :] * smoke[..., None] * 0.22
    rng = np.random.default_rng(seed + 200)
    spark = (rng.random((H, W)) > 0.9993).astype(float) * col * vert
    tip = np.array(stops[-1][1]) / 255.0
    img = img + spark[..., None] * tip[None, None, :]
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

def diag(base, colors, seed, gain=1.0, angles=None, **kw):
    """대각선 광선 리본(범용). angles=None이면 기본 대각, 작은 값이면 거의 수평(오로라/파도)."""
    A = angles or [-0.55, -0.42, -0.62, -0.30]
    F = [2.1, 1.4, 2.7, 1.1]; AM = [0.10, 0.14, 0.08, 0.18]
    Wd = [0.05, 0.085, 0.03, 0.12]; G = [0.95, 0.7, 0.85, 0.5]
    ribs = [(A[i], F[i], AM[i], Wd[i], colors[i % len(colors)], G[i] * gain) for i in range(4)]
    return ribbon_bg(base, ribs, seed, **kw)

# ===== 20 테마 스펙: name -> (builder(seed)->Image, accent_rgb) =====
THEME_SPECS = {
 # --- 불꽃 계열 ---
 "flame_blue":  (lambda s: flame_bg([(0,(4,8,18)),(.2,(10,26,64)),(.42,(22,84,170)),(.66,(46,152,230)),(.86,(118,206,252)),(1,(190,230,255))],(60,100,145),s), (90,200,250)),
 "flame_red":   (lambda s: flame_bg([(0,(14,6,4)),(.2,(52,14,6)),(.42,(150,44,16)),(.66,(232,96,30)),(.86,(255,170,80)),(1,(255,232,180))],(120,70,45),s), (255,120,70)),
 "crimson_smoke":(lambda s: flame_bg([(0,(12,4,8)),(.2,(48,8,18)),(.45,(140,24,46)),(.7,(220,52,78)),(.88,(255,120,150)),(1,(255,205,218))],(110,55,70),s), (240,84,96)),
 "molten_gold": (lambda s: flame_bg([(0,(14,9,3)),(.2,(52,30,6)),(.45,(150,96,18)),(.7,(232,168,46)),(.88,(255,214,96)),(1,(255,246,196))],(120,92,40),s), (255,182,72)),
 # --- 대각 광선 리본 ---
 "series_purple":(lambda s: diag([(0,(58,20,96)),(.45,(40,14,74)),(1,(16,7,34))],[(190,90,230),(120,70,220),(230,150,250),(70,40,150)],s), (190,130,240)),
 "series_red":  (lambda s: diag([(0,(74,16,22)),(.45,(44,10,14)),(1,(16,4,6))],[(240,70,60),(200,40,40),(255,150,110),(130,24,28)],s,star=(.9,.7,.6)), (242,84,82)),
 "series_blue": (lambda s: diag([(0,(14,34,78)),(.45,(8,20,50)),(1,(3,7,22))],[(70,160,252),(40,110,235),(160,210,255),(24,60,150)],s), (78,156,246)),
 "royal_purple":(lambda s: diag([(0,(48,20,80)),(.45,(30,12,56)),(1,(12,6,26))],[(200,130,245),(245,205,120),(225,160,250),(120,70,180)],s), (212,150,245)),
 "neon_cyber":  (lambda s: diag([(0,(10,16,40)),(.45,(8,8,28)),(1,(3,4,14))],[(60,235,235),(255,70,200),(120,250,250),(180,60,230)],s), (70,235,235)),
 "emerald_noir":(lambda s: diag([(0,(8,30,22)),(.45,(5,18,14)),(1,(2,8,6))],[(60,225,150),(30,170,120),(150,250,200),(20,90,70)],s), (70,225,150)),
 "sunset_orange":(lambda s: diag([(0,(70,28,42)),(.45,(44,16,30)),(1,(16,7,16))],[(255,150,80),(255,90,120),(255,200,120),(150,50,90)],s), (255,140,90)),
 "electric_violet":(lambda s: diag([(0,(34,16,70)),(.45,(22,10,50)),(1,(8,4,24))],[(170,110,255),(120,70,240),(210,170,255),(80,40,180)],s), (178,120,255)),
 "aurora":      (lambda s: diag([(0,(8,28,40)),(.45,(6,18,30)),(1,(2,8,16))],[(90,240,170),(140,120,250),(180,250,210),(60,180,200)],s,angles=[0.08,0.14,0.05,0.18],vcenter=0.26,star=(.8,.95,.9)), (110,240,180)),
 "carbon_steel":(lambda s: diag([(0,(26,28,34)),(.45,(16,17,21)),(1,(6,7,9))],[(170,185,205),(120,135,155),(200,212,228),(80,90,105)],s,gain=0.6,star=(.8,.8,.85)), (185,198,216)),
 "ocean_teal":  (lambda s: diag([(0,(16,70,78)),(.4,(8,44,52)),(1,(3,18,24))],[(90,220,205),(50,170,165),(170,245,235),(20,90,95)],s,angles=[0.06,0.10,0.02,0.14],vcenter=0.25,star=(.7,.9,.85)), (58,214,192)),
 # --- 중앙 발광(스포트라이트/도어) ---
 "golden_luxe": (lambda s: vglow_bg([(0,(18,13,6)),(.5,(9,7,3)),(1,(2,2,2))],(255,190,80),s,gw=0.14,turb=True,ray=True), (245,196,92)),
 "ice_blue":    (lambda s: vglow_bg([(0,(8,16,28)),(.5,(5,9,18)),(1,(2,4,9))],(150,205,255),s,gw=0.16,turb=True), (155,212,255)),
 "jade_dragon": (lambda s: vglow_bg([(0,(6,18,13)),(.5,(4,11,8)),(1,(2,5,4))],(70,215,150),s,gw=0.15,turb=True,ray=True), (80,215,155)),
 "platinum_mono":(lambda s: vglow_bg([(0,(18,19,23)),(.5,(10,11,13)),(1,(3,3,4))],(212,218,230),s,gw=0.18,turb=True), (208,215,228)),
 # --- 라디얼(우주/네뷸라) ---
 "deep_space":  (lambda s: radial_bg([(0,(10,18,44)),(.5,(6,11,30)),(1,(2,4,12))],(70,150,240),s), (110,160,250)),
 "nebula_pink": (lambda s: radial_bg([(0,(36,14,40)),(.5,(22,8,28)),(1,(8,3,12))],(245,90,190),s,cy=0.30,rad=0.55), (255,120,200)),
}
# 하위호환 별칭
_ALIAS = {"golden_door": "golden_luxe", "space_blue": "deep_space"}
GENERATORS = {k: v[0] for k, v in THEME_SPECS.items()}
GENERATORS.update({a: THEME_SPECS[t][0] for a, t in _ALIAS.items()})
THEME_ACCENT = {k: v[1] for k, v in THEME_SPECS.items()}
THEME_ACCENT.update({a: THEME_SPECS[t][1] for a, t in _ALIAS.items()})
THEME_LIST = list(THEME_SPECS.keys())   # 20종

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "flame_blue"
    if arg == "all":
        import os; os.makedirs("assets/bg", exist_ok=True)
        for i, name in enumerate(THEME_LIST):
            GENERATORS[name](7 + i * 3).save(f"assets/bg/{name}.jpg", quality=90)
            print("saved", name)
    else:
        out = sys.argv[2] if len(sys.argv) > 2 else f"assets/bg/{arg}.jpg"
        GENERATORS[arg]().save(out, quality=90); print("saved", out)
