#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실습 p003 러너 — 실사 히어로 합성(무료 스톡, Pexels 라이선스) 3종. QC 스펙 포함."""
import os
from PIL import Image
import qc
A0, EA, EB, EC = qc.load()
import render_main as RM
from make_p002 import BASE, PRIZES, SPEC_BASE

os.makedirs("out/practice", exist_ok=True)

VARIANTS = [
    dict(BASE, hero="assets/heroes/px_29095597.jpg", theme="", accent=(255, 122, 36),
         title="SMOKE BLUFF", subtitle="NIGHT ENTRY TONER", ktitle="스모크 블러프 나이트",
         hook=list("블러프는 연기처럼, 스택은 재처럼")),
    dict(BASE, hero="assets/heroes/px_9859353.jpg", theme="", accent=(255, 182, 46),
         title="GOLDEN FAN", subtitle="DEEPSTACK OPEN", ktitle="골든 팬 딥스택",
         hook=list("핸드는 부채처럼 펼치고 입은 닫는다")),
    dict(BASE, hero="assets/heroes/px_4253621.jpg", theme="", accent=(255, 76, 56),
         title="BLACK ACES", subtitle="FREEZE OUT", ktitle="블랙 에이스 프리즈아웃",
         hook=list("에이스 두 장, 리버에서 우는 이유")),
    dict(BASE, hero="assets/heroes/px_33006404.jpg", theme="", accent=(180, 77, 255),
         title="THE PILGRIM", subtitle="MONDAY DEEPRUN", ktitle="더 필그림 먼데이",
         hook=list("순례는 끝났다, 이제 쇼다운이다")),
    dict(BASE, hero="assets/heroes/px_8247082.jpg", theme="", accent=(34, 211, 255),
         title="LAST PRAYER", subtitle="BOUNTY HUNTER", ktitle="라스트 프레이 바운티",
         hook=list("기도는 짧게, 밸류는 길게")),
    dict(BASE, hero="assets/heroes/px_19406595.jpg", theme="", accent=(23, 232, 138),
         title="SILENT MASK", subtitle="MYSTERY STACK", ktitle="사일런트 마스크",
         hook=list("표정을 지운 자가 텔을 지운다")),
    dict(BASE, hero="assets/heroes/px_35448382.jpg", theme="", accent=(255, 182, 46),
         title="TOWER 25K", subtitle="HIGH ROLLER", ktitle="타워 하이롤러",
         hook=list("탑은 무너지라고 쌓는 게 아니다")),
]

fails = 0
outs = []
for v in VARIANTS:
    name = v["title"].split()[0].lower()
    out = f"out/practice/p003_{name}.png"
    spec = dict(SPEC_BASE, title=v["title"] + " " + v["subtitle"])
    fails += len(qc.run(f"P003_{name}", RM.W, RM.H,
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
s.save("out/practice/p003_montage.jpg", quality=90); print("montage", s.size)
