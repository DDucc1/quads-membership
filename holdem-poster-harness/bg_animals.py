#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동물 컨셉 절차적 배경 5종 — 각기 다른 무드.
  animal_wolf  : 보름달 + 능선 + 하울링 늑대 실루엣 (딥블루 밤)
  animal_eagle : 골드 방사광 + 펼친 날개 깃 문장 (블랙/골드)
  animal_tiger : 어둠 속 호랑이 눈 글로우 + 유기적 스트라이프 (블랙/오렌지)
  animal_shark : 심해 광선 + 수면 물결 + 등지느러미 (딥틸)
  animal_stag  : 대칭 사슴뿔 라인 문장 + 별먼지 (에메랄드/골드)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from bg_generate import ramp, fbm, W, H

def _base(stops):
    ny = np.mgrid[0:H, 0:W][0].astype(float) / H
    return Image.fromarray((ramp(ny, stops)).astype("uint8"), "RGB").convert("RGBA")

def _vignette(img, cx=0.5, cy=0.35, floor=0.42):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    nx = (xx / W - cx) * 1.1; nyv = (yy / H - cy) * 1.2
    r = np.sqrt(nx ** 2 + nyv ** 2)
    v = np.clip(1.05 - (r - 0.45) * 0.9, floor, 1.0)
    a = np.asarray(img.convert("RGB"), dtype=float) * v[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype("uint8"), "RGB").convert("RGBA")
    return out

def _stars(img, seed, thr=0.99935, tint=(0.85, 0.9, 1.0)):
    rng = np.random.default_rng(seed)
    sp = (rng.random((H, W)) > thr).astype(float)
    a = np.asarray(img.convert("RGB"), dtype=float) / 255.0
    a = np.clip(a + sp[..., None] * np.array(tint), 0, 1)
    return Image.fromarray((a * 255).astype("uint8"), "RGB").convert("RGBA")

def _glow_disc(img, cx, cy, r, color, core=230, halo=3.2):
    gl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gl).ellipse([cx - r, cy - r, cx + r, cy + r], fill=core)
    halo_l = gl.filter(ImageFilter.GaussianBlur(r * halo / 3))
    lay = Image.new("RGBA", (W, H), color + (255,)); lay.putalpha(halo_l)
    img.alpha_composite(lay)
    lay2 = Image.new("RGBA", (W, H), color + (255,))
    lay2.putalpha(gl.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(lay2)
    return img

# ---------- WOLF ----------
def animal_wolf(seed=21):
    img = _base([(0, (10, 16, 40)), (0.55, (6, 10, 28)), (1, (3, 5, 14))])
    img = _stars(img, seed)
    # 보름달 (우상단 — 좌측 히어로 텍스트 회피)
    img = _glow_disc(img, int(W * 0.79), int(H * 0.145), 100, (222, 232, 252), core=235)
    d = ImageDraw.Draw(img, "RGBA")
    # 달 표면 미세 크레이터
    mx, mv = int(W * 0.79), int(H * 0.145)
    for dx, dy, r, a in [(-30, -18, 16, 26), (22, 8, 12, 22), (-6, 34, 10, 20), (40, -34, 8, 18)]:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse([mx + dx - r, mv + dy - r, mx + dx + r, mv + dy + r], fill=(150, 165, 200, a))
        img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
    # 능선 2겹 (노이즈)
    ridge = fbm(1, W, seed + 3, 5)[0]
    ridge2 = fbm(1, W, seed + 9, 5)[0]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    pts = [(x, int(H * 0.60 + ridge[x] * 90)) for x in range(0, W, 4)]
    od.polygon(pts + [(W, H), (0, H)], fill=(8, 12, 28, 235))
    img.alpha_composite(ov)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    pts2 = [(x, int(H * 0.72 + ridge2[x] * 70)) for x in range(0, W, 4)]
    od.polygon(pts2 + [(W, H), (0, H)], fill=(4, 6, 16, 255))
    img.alpha_composite(ov)
    # '울프 문' 문장 — 달 원판 안 로우폴리 늑대 머리 실루엣 (대칭이라 형태 안정)
    mxc, myc, s = int(W * 0.79), int(H * 0.145), 90
    head = [(-0.36, -1.02), (-0.16, -0.62), (0.16, -0.62), (0.36, -1.02), (0.56, -0.66),
            (0.64, -0.28), (0.34, 0.12), (0.16, 0.54), (0.0, 0.70), (-0.16, 0.54),
            (-0.34, 0.12), (-0.64, -0.28), (-0.56, -0.66)]
    od = ImageDraw.Draw(img, "RGBA")
    od.polygon([(mxc + int(px * s), myc + int(py * s)) for px, py in head], fill=(6, 9, 24, 245))
    # 달빛색 눈 슬릿(뚫린 형태)
    for sx in (-1, 1):
        ex = mxc + sx * int(s * 0.26); ey = myc - int(s * 0.12)
        od.polygon([(ex - sx * int(s * 0.14), ey + 3), (ex + sx * int(s * 0.10), ey - int(s * 0.09)),
                    (ex + sx * int(s * 0.13), ey + 2)], fill=(215, 226, 250, 255))
    return _vignette(img, cy=0.32, floor=0.5)

# ---------- EAGLE ----------
def animal_eagle(seed=22):
    img = _base([(0, (26, 18, 7)), (0.5, (14, 10, 4)), (1, (4, 3, 2))])
    cx, cy = int(W * 0.5), int(H * 0.34)
    # 방사광
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for k in range(28):
        a0 = k * (360 / 28); a1 = a0 + (3.2 if k % 2 == 0 else 1.6)
        od.pieslice([cx - 1400, cy - 1400, cx + 1400, cy + 1400], a0, a1, fill=(255, 196, 90, 16))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4)))
    img = _glow_disc(img, cx, cy, 60, (255, 208, 110), core=120, halo=6)
    # 펼친 날개 깃 (좌우 대칭 부채꼴) — 문장 워터마크
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for side in (-1, 1):
        for i in range(9):
            ang = math.radians(12 + i * 8.6)
            L = 330 + i * 26
            wdt = 30 - i * 1.6
            x1 = cx + side * math.cos(ang) * L
            y1 = cy - math.sin(ang) * L * 0.62
            perp = (math.sin(ang) * side, math.cos(ang) * 0.62)
            od.polygon([(cx + side * 34, cy + 6),
                        (x1 + perp[0] * wdt, y1 + perp[1] * wdt),
                        (x1 - perp[0] * wdt * 0.4, y1 - perp[1] * wdt)],
                       fill=(232, 178, 84, 54))
    od.polygon([(cx, cy - 36), (cx + 26, cy + 26), (cx, cy + 68), (cx - 26, cy + 26)],
               fill=(246, 198, 104, 84))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1)))
    img = _stars(img, seed, thr=0.9996, tint=(0.9, 0.8, 0.5))
    return _vignette(img, cy=0.34, floor=0.4)

# ---------- TIGER ----------
def animal_tiger(seed=23):
    img = _base([(0, (16, 8, 4)), (0.5, (10, 5, 3)), (1, (3, 2, 1))])
    # 유기적 대각 스트라이프 (노이즈 변조)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    u = (xx * 0.72 + yy * 0.66) / W
    warp = (fbm(H, W, seed, 5) - 0.5) * 0.35
    band = np.abs(((u + warp) * 9.0) % 1.0 - 0.5) * 2
    stripe = np.clip((band - 0.62) * 4.2, 0, 1)
    edge = np.clip((xx / W - 0.42) / 0.58, 0, 1) ** 1.4      # 좌측(텍스트)은 비움
    col = np.array([214, 92, 26]) / 255.0
    a = np.asarray(img.convert("RGB"), dtype=float) / 255.0
    a = 1 - (1 - a) * (1 - col[None, None, :] * (stripe * edge * 0.5)[..., None])
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8"), "RGB").convert("RGBA")
    # 호랑이 눈 한 쌍 (우상단, 어둠 속 발광)
    ex, ey, gap = int(W * 0.74), int(H * 0.14), 92
    for sx in (-1, 1):
        cxe = ex + sx * gap
        gl = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(gl)
        gd.polygon([(cxe - 46, ey), (cxe - 10, ey - 22 - (6 if sx > 0 else 0)),
                    (cxe + 34, ey - 6), (cxe + 44, ey + 4), (cxe + 6, ey + 18), (cxe - 34, ey + 12)],
                   fill=255)
        lay = Image.new("RGBA", (W, H), (255, 176, 60, 255))
        lay.putalpha(gl.filter(ImageFilter.GaussianBlur(16)))
        img.alpha_composite(lay)
        lay2 = Image.new("RGBA", (W, H), (255, 226, 150, 255))
        lay2.putalpha(gl.filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * 0.9)))
        img.alpha_composite(lay2)
        d2 = ImageDraw.Draw(img, "RGBA")
        d2.ellipse([cxe - 7, ey - 14, cxe + 5, ey + 10], fill=(20, 8, 2, 255))  # 세로 동공
    return _vignette(img, cy=0.3, floor=0.42)

# ---------- SHARK ----------
def animal_shark(seed=24):
    img = _base([(0, (30, 84, 96)), (0.24, (14, 56, 68)), (0.6, (6, 30, 40)), (1, (2, 10, 15))])
    # 수중 광선
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    nx = (xx - W * 0.5) / W; ny = yy / H
    a = np.asarray(img.convert("RGB"), dtype=float) / 255.0
    for k in range(6):
        off = (k - 2.5) * 0.16
        ray = np.exp(-((nx - off - ny * off * 0.7) / 0.035) ** 2) * np.clip(1 - ny * 1.4, 0, 1) * 0.30
        a = 1 - (1 - a) * (1 - np.array([0.55, 0.85, 0.85])[None, None, :] * ray[..., None])
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8"), "RGB").convert("RGBA")
    # 수면 물결 라인
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i, yb in enumerate(range(int(H * 0.16), int(H * 0.24), 14)):
        wob = fbm(1, W, seed + i, 4)[0]
        od.line([(x, int(yb + wob[x] * 12)) for x in range(0, W, 6)],
                fill=(150, 226, 226, 40 - i * 5), width=2)
    img.alpha_composite(ov)
    # 등지느러미 실루엣 (우측, 수면 관통) + 물살
    fx, fy = int(W * 0.72), int(H * 0.215)
    od = ImageDraw.Draw(img, "RGBA")
    od.polygon([(fx - 105, fy + 26), (fx - 30, fy - 118), (fx + 6, fy - 128),
                (fx - 4, fy - 60), (fx + 70, fy + 26)], fill=(3, 10, 14, 250))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od2 = ImageDraw.Draw(ov)
    od2.ellipse([fx - 160, fy + 8, fx + 120, fy + 44], outline=(190, 240, 240, 90), width=3)
    od2.ellipse([fx - 210, fy + 2, fx + 170, fy + 54], outline=(190, 240, 240, 45), width=2)
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1)))
    return _vignette(img, cy=0.3, floor=0.46)

# ---------- STAG ----------
def animal_stag(seed=25):
    img = _base([(0, (10, 30, 22)), (0.5, (6, 20, 15)), (1, (2, 8, 6))])
    img = _stars(img, seed, thr=0.9995, tint=(0.75, 0.9, 0.7))
    cx, cy = int(W * 0.5), int(H * 0.50)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    GOLD = (226, 190, 104, 130)
    def branch(x, y, ang, ln, depth, side):
        if depth == 0 or ln < 22:
            return
        x2 = x + math.cos(ang) * ln * side
        y2 = y - math.sin(ang) * ln
        od.line([(x, y), (x2, y2)], fill=GOLD, width=max(3, depth * 2))
        od.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=GOLD)
        branch(x2, y2, ang + 0.42, ln * 0.74, depth - 1, side)
        branch(x2, y2, ang - 0.16, ln * 0.66, depth - 1, side)
    for side in (-1, 1):
        # 메인 빔(줄기) + 상향 가지들 — 왕관형 대칭 뿔
        branch(cx + side * 44, cy + 60, 1.32, 210, 6, side)
        branch(cx + side * 44, cy + 60, 0.72, 150, 4, side)
    # 두상 암시(길쭉한 다이아) + 이중 링
    od.polygon([(cx, cy + 30), (cx + 34, cy + 106), (cx, cy + 210), (cx - 34, cy + 106)], fill=GOLD)
    od.ellipse([cx - 300, cy - 300, cx + 300, cy + 300], outline=(226, 190, 104, 60), width=3)
    od.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], outline=(226, 190, 104, 28), width=2)
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1)))
    gl = ov.filter(ImageFilter.GaussianBlur(16)); img.alpha_composite(gl)
    return _vignette(img, cy=0.42, floor=0.42)

ANIMALS = {
    "animal_wolf": (animal_wolf, (150, 190, 250)),
    "animal_eagle": (animal_eagle, (240, 190, 92)),
    "animal_tiger": (animal_tiger, (250, 150, 62)),
    "animal_shark": (animal_shark, (96, 216, 214)),
    "animal_stag": (animal_stag, (212, 186, 108)),
}

if __name__ == "__main__":
    import os
    os.makedirs("assets/bg", exist_ok=True)
    for name, (fn, _) in ANIMALS.items():
        fn().convert("RGB").save(f"assets/bg/{name}.jpg", quality=90)
        print("saved", name)
