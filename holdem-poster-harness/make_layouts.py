#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B형 레이아웃 변형 5종 — 같은 내용, 배치만 다르게. QC 게이트 경유."""
import os
from PIL import Image, ImageDraw
import qc
A0, EA, EB, EC = qc.load()
import render_poster_b as B0
import layout_variants as LV
from render_poster import noto

os.makedirs("out/layouts", exist_ok=True)

NOTICE = [
    "최종 레지스트레이션은 표기 레벨 시작 전까지 가능합니다.",
    "빅 블라인드 엔티 방식으로 진행됩니다.",
    "국제 TDA 규정을 준수합니다.",
    "테이블은 9max로 진행합니다.",
    "대회 참가자는 본인 신분증을 지참하여 본인 확인을 진행합니다.",
    "상금을 획득한 선수는 세금신고를 의무화 해야합니다.",
    "부정행위 적발 시 전 칩 몰수 및 퇴장 조치됩니다.",
    "타임뱅크는 브레이크별 차등 지급됩니다.",
]
PRIZES = [("1st", "30,000,000"), ("2nd", "19,000,000"), ("3rd", "13,000,000"), ("4th", "9,500,000"),
          ("5th", "7,500,000"), ("6th", "6,000,000"), ("7th", "4,900,000"), ("8th", "4,000,000"),
          ("9th", "3,400,000"), ("10th~12th", "2,900,000"), ("13th~15th", "2,450,000"),
          ("16th~20th", "2,050,000"), ("21st~30th", "1,750,000"), ("31st~40th", "1,500,000"),
          ("41st~50th", "1,300,000"), ("51st~60th", "1,150,000"), ("61st~70th", "1,000,000"),
          ("71st~80th", "880,000"), ("81st~90th", "780,000"), ("91st~99th", "700,000")]

BASE = dict(B0.DATA,
    logo_mark="RP", logo_word="ROYAL POKER CLUB",
    series="ROYAL CROWN SERIES", total="400,000,000", brand="서울 로열포커",
    title="ROYAL MAIN EVENT", gtd="100,000,000",
    date="26.10.17 (SAT) - 14:00", buyin="MAIN 1 TICKET OR 50RP",
    kicker="CROWN SERIES · MAIN EVENT",
    stats=[("STARTING STACK", "60,000"), ("END of REG", "14LV 시작 전"),
           ("DURATION", "30 / 25 mins"), ("ENTRY", "400++")],
    notice=NOTICE, prizes=PRIZES,
    sponsors=[("주관사", "ROYAL POKER CLUB"), ("협력사", "CHIPSTACK · 올인클럽"), ("후원사", "블러프랩")],
    venue_name="로열포커 스타디움", venue_addr="서울 강남구 크라운로 77, 6층")

V1 = dict(BASE, theme="series_purple")
V2 = dict(BASE, theme="series_red")
V3 = dict(BASE, theme="golden_luxe")
V4 = dict(BASE, theme="series_blue")
V5 = dict(BASE, theme="deep_space")

fails = 0
fails += len(qc.run("V1_Classic",  EB.W, EB.H, lambda: EB.render(V1, B0.LV, "out/layouts/V1_Classic.png")))
fails += len(qc.run("V2_Podium",   LV.W, LV.H, lambda: LV.render_v2(V2, B0.LV, "out/layouts/V2_Podium.png")))
fails += len(qc.run("V3_Flank",    LV.W, LV.H, lambda: LV.render_v3(V3, B0.LV, "out/layouts/V3_Flank.png")))
fails += len(qc.run("V4_Sidebar",  LV.W, LV.H, lambda: LV.render_v4(V4, B0.LV, "out/layouts/V4_Sidebar.png")))
fails += len(qc.run("V5_Showcase", LV.W, LV.H, lambda: LV.render_v5(V5, B0.LV, "out/layouts/V5_Showcase.png")))
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

items = [("V1 클래식 스플릿 (기본)", "out/layouts/V1_Classic.png"),
         ("V2 포디움 + 풀폭 블라인드", "out/layouts/V2_Podium.png"),
         ("V3 센터 대칭 + 플랭킹", "out/layouts/V3_Flank.png"),
         ("V4 블라인드 메인 + 사이드바", "out/layouts/V4_Sidebar.png"),
         ("V5 쇼케이스 + 콤팩트 구조", "out/layouts/V5_Showcase.png")]
tw = 310; th = int(tw * 1900 / 1080); lab = 40; gap = 18; top = 64; cols = 5
Wm = cols * tw + (cols + 1) * gap; Hm = top + th + lab + gap
s = Image.new("RGB", (Wm, Hm), (12, 12, 18)); d = ImageDraw.Draw(s)
d.text((gap, 24), "B형 레이아웃 변형 5종 — 같은 내용, 다른 배치", font=noto(28, 800), fill=(240, 240, 250), anchor="lm")
for i, (n, p) in enumerate(items):
    x = gap + i * (tw + gap); y = top
    s.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y))
    d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(64, 64, 84))
    d.text((x + tw / 2, y + th + lab / 2), n, font=noto(17, 700), fill=(214, 218, 232), anchor="mm")
s.save("out/layouts/montage.jpg", quality=90); print("montage", s.size)
