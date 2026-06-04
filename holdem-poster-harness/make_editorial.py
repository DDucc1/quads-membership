#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""에디토리얼 A/B/C를 여러 테마로 일괄 렌더 + 컨택트시트."""
import os
from PIL import Image, ImageDraw
from render_poster import noto
import render_editorial as EA
import render_editorial_b as EB
import render_editorial_c as EC

os.makedirs("out/ed", exist_ok=True)
A_TH = ["golden_luxe", "flame_blue", "deep_space", "crimson_smoke", "neon_cyber", "emerald_noir",
        "ocean_teal", "royal_purple", "platinum_mono", "molten_gold"]
B_TH = ["series_purple", "series_red", "series_blue", "royal_purple"]
C_TH = ["series_blue", "series_red", "deep_space"]

A = []
for t in A_TH:
    f = f"out/ed/A_{t}.png"; EA.render(dict(EA.DATA, theme=t), f); A.append((t, f))
Bf = []
for t in B_TH:
    f = f"out/ed/B_{t}.png"; EB.render(dict(EB.DATA, theme=t), EB.B.LV, f); Bf.append((t, f))
Cf = []
for t in C_TH:
    f = f"out/ed/C_{t}.png"; EC.render(dict(EC.DATA, theme=t), f); Cf.append((t, f))

def montage(items, cols, out, title, tw=300):
    th = int(tw * Image.open(items[0][1]).height / Image.open(items[0][1]).width)
    lab, gap, top = 34, 16, 58
    rows = (len(items) + cols - 1) // cols
    Wm = cols * tw + (cols + 1) * gap; Hm = top + rows * (th + lab + gap) + gap
    s = Image.new("RGB", (Wm, Hm), (12, 12, 18)); d = ImageDraw.Draw(s)
    d.text((gap, 22), title, font=noto(28, 800), fill=(240, 240, 250), anchor="lm")
    for i, (n, p) in enumerate(items):
        r, c = divmod(i, cols); x = gap + c * (tw + gap); y = top + r * (th + lab + gap)
        s.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(64, 64, 84))
        d.text((x + tw / 2, y + th + lab / 2), n, font=noto(19, 700), fill=(214, 218, 232), anchor="mm")
    s.save(out, quality=90); print("montage", out, s.size)

montage(A, 5, "out/ed_montage_A.jpg", "에디토리얼 A형(히어로) — 10테마")
montage(Bf, 4, "out/ed_montage_B.jpg", "에디토리얼 B형(스트럭처) — 4테마")
montage(Cf, 3, "out/ed_montage_C.jpg", "에디토리얼 C형(스케줄) — 3테마")
