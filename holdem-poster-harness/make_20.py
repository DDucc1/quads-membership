#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20개 테마 전부를 A형 포스터에 입혀서 비교 컨택트시트 생성."""
import os
from PIL import Image, ImageDraw
import render_poster as A
from render_poster import noto
from bg_generate import THEME_LIST

os.makedirs("out/themes", exist_ok=True)
files = []
for t in THEME_LIST:
    f = f"out/themes/A_{t}.png"; A.render(dict(A.DATA, theme=t), f); files.append((t, f))

# 컨택트시트 5열 x 4행
cols = 5; tw = 300; th = int(tw * 1800 / 1080); lab = 34; gap = 16; top = 60
rows = (len(files) + cols - 1) // cols
W = cols * tw + (cols + 1) * gap
H = top + rows * (th + lab + gap) + gap
sheet = Image.new("RGB", (W, H), (12, 12, 18)); d = ImageDraw.Draw(sheet)
d.text((gap, 20), "홀덤 포스터 — 20 테마 (A형 동일 내용)", font=noto(30, 800), fill=(240, 240, 250), anchor="lm")
for i, (name, path) in enumerate(files):
    r, c = divmod(i, cols)
    x = gap + c * (tw + gap); y = top + r * (th + lab + gap)
    sheet.paste(Image.open(path).convert("RGB").resize((tw, th)), (x, y))
    d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(64, 64, 84))
    d.text((x + tw / 2, y + th + lab / 2), name, font=noto(20, 700), fill=(214, 218, 232), anchor="mm")
sheet.save("out/montage_20.jpg", quality=90)
print("saved out/montage_20.jpg", sheet.size)
