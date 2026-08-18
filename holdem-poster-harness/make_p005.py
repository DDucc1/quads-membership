#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실습 p005 러너 — 연기·후드 무드 심화 8종(AI 생성, 비식별 원칙). QC 스펙 포함.
사용자 확정(2026-07-31): "연기·후드 계열이 제일 좋다, 이 무드로 심화" → 하우스 무드 후보."""
import os
from PIL import Image
import qc
A0, EA, EB, EC = qc.load()
import render_main as RM
from make_p002 import BASE, SPEC_BASE

os.makedirs("out/practice", exist_ok=True)
H = "assets/heroes/"

VARIANTS = [
    dict(BASE, hero=H + "sm_amber.jpg",   accent=(255, 150, 40),  title="AMBER EXHALE",  subtitle="NIGHT ENTRY",     ktitle="앰버 엑세일 나이트",   hook=list("내쉰 연기만큼 스택을 밀어라")),
    dict(BASE, hero=H + "sm_teal.jpg",    accent=(34, 211, 255),  title="COLD FRONT",    subtitle="TURBO DEEPRUN",   ktitle="콜드 프론트 터보",     hook=list("차가운 머리, 뜨거운 올인")),
    dict(BASE, hero=H + "sm_magenta.jpg", accent=(255, 61, 160),  title="VIOLET WHISPER", subtitle="LADIES NIGHT",   ktitle="바이올렛 위스퍼",      hook=list("속삭임 한 장, 팟은 통째로")),
    dict(BASE, hero=H + "sm_duo.jpg",     accent=(212, 218, 230), title="HEADS UP",      subtitle="DUEL SERIES",     ktitle="헤즈업 듀얼 시리즈",   hook=list("둘 중 하나는 집에 못 간다")),
    dict(BASE, hero=H + "sm_back.jpg",    accent=(255, 182, 46),  title="WALK IN",       subtitle="MONDAY REBUY",    ktitle="워크 인 먼데이",       hook=list("안개 너머, 테이블은 열려 있다")),
    dict(BASE, hero=H + "sm_red.jpg",     accent=(255, 68, 56),   title="RED HALO",      subtitle="BOUNTY HUNTER",   ktitle="레드 헤일로 바운티",   hook=list("현상금은 후드 안에 있다")),
    dict(BASE, hero=H + "sm_dealer.jpg",  accent=(23, 232, 138),  title="GREEN FELT",    subtitle="DEALER'S CHOICE", ktitle="그린 펠트 딜러스 초이스", hook=list("딜러는 말이 없다, 카드가 말한다")),
    dict(BASE, hero=H + "sm_green.jpg",   accent=(120, 255, 200), title="PHANTOM STACK", subtitle="MYSTERY BOUNTY",  ktitle="팬텀 스택 미스터리",   hook=list("보이지 않는 칩이 제일 무겁다")),
]
for v in VARIANTS:
    v["theme"] = ""

fails = 0
outs = []
for v in VARIANTS:
    name = v["title"].split()[0].lower()
    out = f"out/practice/p005_{name}.png"
    spec = dict(SPEC_BASE, title=v["title"] + " " + v["subtitle"])
    fails += len(qc.run(f"P005_{name}", RM.W, RM.H,
                        lambda vv=v, o=out: RM.render(vv, o), spec=spec))
    outs.append(out)
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

thumbs = []
for p in outs:
    im = Image.open(p).convert("RGB"); im.thumbnail((300, 450)); thumbs.append(im)
gap = 12; cols = 4
rows = (len(thumbs) + cols - 1) // cols
s = Image.new("RGB", (cols * 300 + gap * (cols + 1), rows * 450 + gap * (rows + 1)), (12, 12, 18))
for i, t in enumerate(thumbs):
    s.paste(t, (gap + (i % cols) * (300 + gap), gap + (i // cols) * (450 + gap)))
s.save("out/practice/p005_montage.jpg", quality=90); print("montage", s.size)
