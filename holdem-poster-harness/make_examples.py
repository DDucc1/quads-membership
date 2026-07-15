#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""입력값만 바꿔 5장 예시 렌더 (인풋→아웃풋 검증). B 3장 + A 1장 + C 1장."""
import os
from PIL import Image, ImageDraw
import qc
A0, EA, EB, EC = qc.load()
import render_poster_b as B0
from render_poster import noto

os.makedirs("out/ex", exist_ok=True)
BD = B0.DATA

# ---- B1: 메인이벤트 (퍼플 / 대구 ANPT) ----
B1 = dict(BD, theme="series_purple", kicker="CHAMPIONSHIP MAIN EVENT")

# ---- B2: 하이롤러 (블루 / 부산 ANPT) ----
B2 = dict(BD, theme="series_blue", title="8 MAX HIGH-ROLLER", gtd="100,000,000",
          brand="부산 ANPT", buyin="HIGH-ROLLER 1 TICKET OR 120FP", kicker="8 MAX · HIGH-ROLLER",
          stats=[("STARTING STACK","80,000"),("END of REG","15LV 시작 전"),
                 ("DURATION","40 / 30 mins"),("ENTRY","119++")],
          venue_name="부산 ANPT 스타디움", venue_addr="부산광역시 부산진구 서면로 20, 3층",
          prizes=[("1st","24,000,000"),("2nd","16,000,000"),("3rd","12,000,000"),("4th","9,000,000"),
                  ("5th","7,200,000"),("6th","5,800,000"),("7th","4,600,000"),("8th","3,800,000"),
                  ("9th","3,200,000"),("10th~12th","2,800,000"),("13th~15th","2,400,000"),("16th~20th","2,000,000"),
                  ("21st~30th","1,600,000"),("31st~40th","1,300,000"),("41st~50th","1,100,000"),
                  ("51st~60th","1,000,000"),("61st~70th","900,000"),("71st~80th","800,000"),
                  ("81st~90th","700,000"),("91st~100th","600,000"),("101st~110th","500,000")])

# ---- B3: 딥스택 오프닝 (레드 / 대전 POD) ----
B3 = dict(BD, theme="series_red", title="DEEP STACK OPENING", gtd="30,000,000", total="120,000,000",
          brand="대전 POD", buyin="1 TICKET OR 20FP", kicker="DAY 1 · DEEP STACK",
          stats=[("STARTING STACK","50,000"),("END of REG","13LV 시작 전"),
                 ("DURATION","20 / 20 mins"),("ENTRY","300++")],
          venue_name="대전 POD 스타디움", venue_addr="대전광역시 서구 둔산로 100, 5층")

# ---- A1: 챌린지 (플레임블루 / 청주 킹덤) ----
A1 = dict(A0.DATA, theme="flame_blue", title="CHALLENGE", accent="in 청주", gtd="20,000,000",
          place="청주 킹덤 율량점", date="26.08.02 (토요일) 오후 2시", buyin="1 Challenge Ticket",
          kicker="GUARANTEED TOURNAMENT", rail="CHEONGJU 2026", date_short="26.08.02 SAT",
          footer_name="청주 킹덤 율량점", footer_addr="청주시 청원구 율량로 100, 3층",
          stats=[("ENTRY","150 Entry++"),("STARTING","60,000 Chips"),
                 ("LATE REG","15Lv 시작 전"),("BLIND","25/20 Mins")],
          sponsors=[("주관사","POKER of DREAMS"),("협력사","SEEDKET"),("후원사","MOXSYS"),("장소","청주 킹덤")])

# ---- C1: 시리즈 스케줄 (블루) ----
C1 = dict(EC.DATA, theme="series_blue")

fails = 0
fails += len(qc.run("1_MainEvent", EB.W, EB.H, lambda: EB.render(B1, B0.LV, "out/ex/1_MainEvent.png")))
fails += len(qc.run("2_HighRoller", EB.W, EB.H, lambda: EB.render(B2, B0.LV, "out/ex/2_HighRoller.png")))
fails += len(qc.run("3_DeepStack", EB.W, EB.H, lambda: EB.render(B3, B0.LV, "out/ex/3_DeepStack.png")))
fails += len(qc.run("4_Challenge", EA.W, EA.H, lambda: EA.render(A1, "out/ex/4_Challenge.png")))
fails += len(qc.run("5_Series", EC.W, EC.H, lambda: EC.render(C1, "out/ex/5_Series.png")))
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

items=[("① MAIN EVENT 200M · B","out/ex/1_MainEvent.png"),
       ("② HIGH-ROLLER 100M · B","out/ex/2_HighRoller.png"),
       ("③ DEEP STACK 30M · B","out/ex/3_DeepStack.png"),
       ("④ CHALLENGE 20M · A","out/ex/4_Challenge.png"),
       ("⑤ DREAM SERIES · C","out/ex/5_Series.png")]
tw=310; th=int(tw*Image.open(items[0][1]).height/Image.open(items[0][1]).width)
lab=40; gap=18; top=64; cols=5
W=cols*tw+(cols+1)*gap; H=top+th+lab+gap
s=Image.new("RGB",(W,H),(12,12,18)); d=ImageDraw.Draw(s)
d.text((gap,24),"입력값만 바꿔 5장 — 같은 시스템, 다른 결과",font=noto(28,800),fill=(240,240,250),anchor="lm")
for i,(n,p) in enumerate(items):
    x=gap+i*(tw+gap); y=top
    s.paste(Image.open(p).convert("RGB").resize((tw,th)),(x,y))
    d.rectangle([x,y,x+tw-1,y+th-1],outline=(64,64,84))
    d.text((x+tw/2,y+th+lab/2),n,font=noto(18,700),fill=(214,218,232),anchor="mm")
s.save("out/ex/montage.jpg",quality=90); print("montage",s.size)
