#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""여러 테마로 A/B 포스터를 일괄 렌더 + 비교용 컨택트시트 생성."""
import os
from PIL import Image, ImageDraw
import render_poster as A
import render_poster_b as B
from render_poster import noto

os.makedirs("out", exist_ok=True)

A_THEMES = ["flame_blue", "ocean_teal", "space_blue", "golden_door", "series_red"]
B_THEMES = ["series_purple", "series_red", "series_blue"]

a_files, b_files = [], []
for t in A_THEMES:
    f = f"out/A_{t}.png"; A.render(dict(A.DATA, theme=t), f); a_files.append((t, f))
for t in B_THEMES:
    f = f"out/B_{t}.png"; B.render(dict(B.DATA, theme=t), f); b_files.append((t, f))

def montage(items, cols, out, title):
    tw = 330; th = int(tw * 1800 / 1080); lab = 38; gap = 22
    rows = (len(items) + cols - 1) // cols
    W = cols * tw + (cols + 1) * gap
    top = 64
    H = top + rows * (th + lab + gap) + gap
    sheet = Image.new("RGB", (W, H), (12, 12, 18)); d = ImageDraw.Draw(sheet)
    d.text((gap, 22), title, font=noto(28, 800), fill=(240, 240, 250), anchor="lm")
    for i, (name, path) in enumerate(items):
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap); y = top + r * (th + lab + gap)
        im = Image.open(path).convert("RGB").resize((tw, th))
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(60, 60, 80))
        d.text((x + tw / 2, y + th + lab / 2), name, font=noto(22, 700), fill=(210, 215, 230), anchor="mm")
    sheet.save(out, quality=92); print("montage", out, sheet.size)

montage(a_files, 3, "out/montage_A.jpg", "A형 (히어로) — 테마 5종")
montage(b_files, 3, "out/montage_B.jpg", "B형 (스트럭처) — 테마 3종")
