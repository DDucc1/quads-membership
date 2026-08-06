#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실습 p004 러너 — 방향2: AI 생성 히어로(Pollinations/Flux, 키리스) 3종. QC 스펙 포함."""
import os
from PIL import Image
import qc
A0, EA, EB, EC = qc.load()
import render_main as RM
from make_p002 import BASE, SPEC_BASE

os.makedirs("out/practice", exist_ok=True)

VARIANTS = [
    dict(BASE, hero="assets/heroes/ai_ember.jpg", theme="", accent=(255, 122, 36),
         title="EMBER HOOD", subtitle="MIDNIGHT TONER", ktitle="엠버 후드 나이트",
         hook=list("재가 될 때까지, 올인은 계속된다")),
    dict(BASE, hero="assets/heroes/ai_chips.jpg", theme="", accent=(255, 182, 46),
         title="GOLD STACK", subtitle="CHIP RACE OPEN", ktitle="골드 스택 오픈",
         hook=list("칩은 거짓말을 하지 않는다")),
    dict(BASE, hero="assets/heroes/ai_crown.jpg", theme="", accent=(180, 77, 255),
         title="CROWN GAMBIT", subtitle="KING MAKER", ktitle="크라운 갬빗 킹메이커",
         hook=list("왕관은 폴드하지 않는 자의 것")),
]

fails = 0
outs = []
for v in VARIANTS:
    name = v["title"].split()[0].lower()
    out = f"out/practice/p004_{name}.png"
    spec = dict(SPEC_BASE, title=v["title"] + " " + v["subtitle"])
    fails += len(qc.run(f"P004_{name}", RM.W, RM.H,
                        lambda vv=v, o=out: RM.render(vv, o), spec=spec))
    outs.append(out)
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

thumbs = []
for p in outs:
    im = Image.open(p).convert("RGB"); im.thumbnail((360, 540)); thumbs.append(im)
gap = 14
s = Image.new("RGB", (len(thumbs) * 360 + gap * (len(thumbs) + 1), 540 + gap * 2), (12, 12, 18))
for i, t in enumerate(thumbs):
    s.paste(t, (gap + i * (360 + gap), gap))
s.save("out/practice/p004_montage.jpg", quality=90); print("montage", s.size)
