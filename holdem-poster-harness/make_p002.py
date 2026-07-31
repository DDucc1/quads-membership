#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실습 p002 러너 — 메인 포스터형(동물 문장 히어로) 3종. QC 스펙 포함."""
import os
from PIL import Image
import qc
A0, EA, EB, EC = qc.load()
import render_main as RM
from bg_animals import ANIMALS

os.makedirs("out/practice", exist_ok=True)

PRIZES = [("1위", "5,000,000"), ("2위", "3,000,000"), ("3위", "2,000,000"),
          ("4위", "1,500,000"), ("5위", "1,200,000"), ("6위", "1,000,000"),
          ("7위", "800,000"), ("8위", "700,000"), ("9위", "600,000")]

BASE = dict(
    date_line="26.08.15 (SAT) · 13:00",
    gtd="15,000,000",
    kicker="10 TICKET · MAIN EVENT",
    buyin_line="BUY IN : 매장이용권 10매 OR NV 시드권 · FREEZE OUT",
    prize_lines=["1위 500만 · 2위 300만 · 3위 200만 · 4위 150만 · 5위 120만",
                 "6위 100만 · 7위 80만 · 8위 70만 · 9위 60만 (분배 합 1,580만)"],
    footer="노바 스타디움 강남 · 서울 강남구 노바로 77, 6층 · 문의 010-0000-0000 · 카카오 오픈톡 : 노바홀덤",
    logo_word="NOVA HOLDEM",
    badge_l=["매장이용권", "10매 바인"], badge_r=["노바 스타디움", "강남 본점"])

VARIANTS = [
    dict(BASE, theme="animal_stag", accent=ANIMALS["animal_stag"][1],
         title="IRON STAG", subtitle="INVITATIONAL",
         hook=["뿔", "세", "운", " ", "자", "가", " ", "팟", "을", " ", "가", "져", "간", "다"]),
    dict(BASE, theme="animal_wolf", accent=ANIMALS["animal_wolf"][1],
         title="LONE WOLF", subtitle="MIDNIGHT OPEN",
         hook=["무", "리", "는", " ", "필", "요", " ", "없", "다", ",", " ", "올", "인", "뿐"]),
    dict(BASE, theme="animal_eagle", accent=ANIMALS["animal_eagle"][1],
         title="HIGH EAGLE", subtitle="SKY ROLLER",
         hook=["높", "이", " ", "나", "는", " ", "새", "가", " ", "칩", "을", " ", "본", "다"]),
]

SPEC_BASE = dict(date="26.08.15 (SAT)", time="13:00",
                 buyin="매장이용권 10매 OR NV 시드권", gtd="15,000,000",
                 prizes=PRIZES, year=2026)

fails = 0
outs = []
for v in VARIANTS:
    name = v["theme"].replace("animal_", "")
    out = f"out/practice/p002_{name}.png"
    spec = dict(SPEC_BASE, title=v["title"] + " " + v["subtitle"])
    fails += len(qc.run(f"P002_{name}", RM.W, RM.H,
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
s.save("out/practice/p002_montage.jpg", quality=90); print("montage", s.size)
