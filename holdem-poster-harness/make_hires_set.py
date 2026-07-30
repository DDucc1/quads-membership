#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""고해상 컨셉 세트 — V6 스트럭처 일체형, 배경·색 컨셉 5종 × 4배율. QC 스펙 포함."""
import os
from PIL import Image
import qc
A0, EA, EB, EC = qc.load()
import render_structure as RS
from make_practice import DATA, SPEC

os.makedirs("out/hires", exist_ok=True)
K = 4

CONCEPTS = [
    ("golden_luxe", "NOVA GOLDEN LUXE",  "골드 럭스"),
    ("aurora",      "NOVA AURORA OPEN",  "오로라"),
    ("series_red",  "NOVA CRIMSON CUP",  "크림슨"),
    ("deep_space",  "NOVA DEEP SPACE",   "딥스페이스"),
    ("ocean_teal",  "NOVA OCEAN SERIES", "오션 틸"),
]

fails = 0
for theme, title, label in CONCEPTS:
    data = dict(DATA, theme=theme, title=title,
                info=["EVENT NAME : " + title] + DATA["info"][1:])
    spec = dict(SPEC, title=title)
    out = f"out/hires/{theme}_{K}x.png"
    fails += len(qc.run(f"{label}_{K}x", RS.W * K, RS.H * K,
                        lambda d=data, o=out: RS.render(d, o, scale=K), spec=spec))
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

# 확인용 미리보기(1080폭) + 몽타주
prevs = []
for theme, title, label in CONCEPTS:
    im = Image.open(f"out/hires/{theme}_{K}x.png")
    pv = im.copy(); pv.thumbnail((1080, 1900))
    pv.save(f"out/hires/{theme}_preview.jpg", quality=90)
    th = pv.copy(); th.thumbnail((330, 590)); prevs.append(th)
gap = 14
Wm = len(prevs) * 330 + gap * (len(prevs) + 1)
s = Image.new("RGB", (Wm, 590 + gap * 2), (12, 12, 18))
for i, p in enumerate(prevs):
    s.paste(p, (gap + i * (330 + gap), gap))
s.save("out/hires/concepts_montage.jpg", quality=90)
print("montage", s.size)
