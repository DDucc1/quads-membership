#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""동물 컨셉 5종 — 전부 가상 브랜드(레퍼런스 브랜드 배제). QC 게이트 경유."""
import os
from PIL import Image, ImageDraw
import qc
A0, EA, EB, EC = qc.load()
import render_poster_b as B0
from render_poster import noto, THEME_ACCENT
from bg_animals import ANIMALS

# 동물 테마 악센트 등록 (팔레트 자동 유도)
THEME_ACCENT.update({k: v[1] for k, v in ANIMALS.items()})

os.makedirs("out/animals", exist_ok=True)

NOTICE_A = [
    "최종 레지스트레이션은 공지 레벨 시작 전까지 가능합니다.",
    "빅 블라인드 엔티 방식으로 진행됩니다.",
    "엔티는 토너먼트가 끝나기 전까지 줄지 않습니다.",
    "국제 TDA 규정을 준수합니다.",
    "테이블은 9max로 진행합니다.",
    "대회 참가자는 본인 신분증을 지참하여 본인 확인을 진행합니다.",
    "상금을 획득한 선수는 세금신고를 의무화 해야합니다.",
    "NEW PLAYER CARD 지급 (첫 핸드에 사용 여부 체크)",
]
NOTICE_B = [
    "최종 레지스트레이션은 표기 레벨 시작 전까지 가능합니다.",
    "빅 블라인드 엔티 방식으로 진행됩니다.",
    "국제 TDA 규정을 준수합니다.",
    "테이블은 9max로 진행합니다.",
    "대회 참가자는 본인 신분증을 지참하여 본인 확인을 진행합니다.",
    "상금을 획득한 선수는 세금신고를 의무화 해야합니다.",
    "부정행위 적발 시 전 칩 몰수 및 퇴장 조치됩니다.",
    "타임뱅크는 브레이크별 차등 지급됩니다.",
]

# ---------- ① WOLF · A형 ----------
P1 = dict(A0.DATA,
    theme="animal_wolf", logo_mark="LH", logo_word="LUNA HOLDEM CLUB",
    title="WOLF PACK", accent=None, gtd="25,000,000",
    date="26.09.05 (토요일) 밤 9시", place="루나 홀덤 라운지",
    buyin="1 Wolf Ticket", kicker="MIDNIGHT GUARANTEED", rail="MIDNIGHT SEOUL 2026",
    date_short="26.09.05 SAT", idx="01",
    stats=[("ENTRY", "140 Entry++"), ("STARTING", "50,000 Chips"),
           ("LATE REG", "14Lv 시작 전"), ("BLIND", "20 Mins")],
    notice=NOTICE_A,
    sponsors=[("주관사", "LUNA HOLDEM"), ("협력사", "CHIPSTACK"), ("후원사", "블러프랩"), ("장소", "루나 라운지")],
    footer_name="루나 홀덤 라운지", footer_addr="서울 마포구 달빛로 88, 4층")

# ---------- ② EAGLE · B형 ----------
P2 = dict(B0.DATA,
    theme="animal_eagle", logo_mark="GS", logo_word="GRAND SLAM POKER",
    series="GRAND TALON SERIES", total="300,000,000", brand="서울 그랜드슬램",
    title="EAGLE HIGH-ROLLER", gtd="80,000,000",
    date="26.09.12 (SAT) - 15:00", buyin="EAGLE 1 TICKET OR 100GP",
    kicker="TALON SERIES · HIGH-ROLLER",
    stats=[("STARTING STACK", "75,000"), ("END of REG", "15LV 시작 전"),
           ("DURATION", "40 / 30 mins"), ("ENTRY", "99++")],
    notice=NOTICE_B,
    prizes=[("1st", "22,000,000"), ("2nd", "14,500,000"), ("3rd", "10,000,000"), ("4th", "7,600,000"),
            ("5th", "6,000,000"), ("6th", "4,800,000"), ("7th", "3,900,000"), ("8th", "3,200,000"),
            ("9th", "2,700,000"), ("10th~12th", "2,300,000"), ("13th~15th", "1,950,000"),
            ("16th~20th", "1,650,000"), ("21st~30th", "1,400,000"), ("31st~40th", "1,200,000"),
            ("41st~50th", "1,050,000"), ("51st~60th", "950,000"), ("61st~70th", "850,000"),
            ("71st~80th", "750,000"), ("81st~90th", "650,000"), ("91st~99th", "550,000")],
    sponsors=[("주관사", "GRAND SLAM POKER"), ("협력사", "CHIPSTACK · 올인클럽"), ("후원사", "블러프랩")],
    venue_name="그랜드슬램 포커클럽", venue_addr="서울 강남구 승부사로 21, 7층")

# ---------- ③ TIGER · A형 ----------
P3 = dict(A0.DATA,
    theme="animal_tiger", logo_mark="JC", logo_word="JUNGLE CARD HOUSE",
    title="TIGER BOUNTY", accent=None, gtd="40,000,000",
    date="26.09.19 (토요일) 오후 2시", place="정글카드 스타디움",
    buyin="1 Bounty Ticket OR 30BP", kicker="KNOCKOUT BOUNTY", rail="BUSAN JUNGLE 2026",
    date_short="26.09.19 SAT", idx="03",
    stats=[("ENTRY", "220 Entry++"), ("STARTING", "60,000 Chips"),
           ("LATE REG", "15Lv 시작 전"), ("BLIND", "25/20 Mins")],
    notice=NOTICE_A,
    sponsors=[("주관사", "JUNGLE CARD"), ("협력사", "올인클럽"), ("후원사", "카드하우스"), ("장소", "정글 스타디움")],
    footer_name="정글카드 스타디움", footer_addr="부산 해운대구 호랑이로 55, 3층")

# ---------- ④ SHARK · B형 ----------
P4 = dict(B0.DATA,
    theme="animal_shark", logo_mark="OB", logo_word="OCEAN BLUFF HOLDEM",
    series="OCEAN BLUFF SERIES", total="150,000,000", brand="인천 오션블러프",
    title="SHARK DEEP STACK", gtd="50,000,000",
    date="26.09.26 (SAT) - 14:00", buyin="SHARK 1 TICKET OR 50GP",
    kicker="DEEP STACK · DAY 1",
    stats=[("STARTING STACK", "60,000"), ("END of REG", "14LV 시작 전"),
           ("DURATION", "30 / 25 mins"), ("ENTRY", "180++")],
    notice=NOTICE_B,
    prizes=[("1st", "14,000,000"), ("2nd", "9,200,000"), ("3rd", "6,500,000"), ("4th", "4,900,000"),
            ("5th", "3,900,000"), ("6th", "3,200,000"), ("7th", "2,700,000"), ("8th", "2,300,000"),
            ("9th", "2,000,000"), ("10th~12th", "1,700,000"), ("13th~15th", "1,450,000"),
            ("16th~20th", "1,250,000"), ("21st~30th", "1,050,000"), ("31st~40th", "900,000"),
            ("41st~50th", "780,000"), ("51st~60th", "680,000"), ("61st~70th", "600,000"),
            ("71st~80th", "530,000"), ("81st~90th", "470,000"), ("91st~100th", "420,000")],
    sponsors=[("주관사", "OCEAN BLUFF"), ("협력사", "CHIPSTACK"), ("후원사", "딥워터클럽")],
    venue_name="오션블러프 홀덤", venue_addr="인천 연수구 파도소리로 12, 5층")

# ---------- ⑤ STAG · C형 ----------
P5 = dict(EC.DATA,
    theme="animal_stag", logo_mark="CH", logo_word="CROWN HERALD POKER",
    series="ROYAL STAG FESTIVAL", total="200,000,000", brand="제주 크라운헤럴드",
    period="10.09 — 10.12", kicker="AUTUMN FESTIVAL · FULL SCHEDULE",
    venue_name="크라운헤럴드 포커룸", venue_addr="제주시 사슴뿔로 7, 2층",
    sponsors=[("주관사", "CROWN HERALD"), ("협력사", "CHIPSTACK · 올인클럽"), ("후원사", "블러프랩")],
    rows=[
        ("10.09 FRI", "13:00", "#1 ANTLER OPENER", "1 TICKET / 20GP", "15,000,000", "150++", "30,000", "20", "13LV"),
        ("10.09 FRI", "19:00", "#2 NIGHT VELVET", "1 TICKET / 15GP", "8,000,000", "120++", "25,000", "15", "12LV"),
        ("10.10 SAT", "13:00", "#3 CROWN BOUNTY", "1 TICKET / 30GP", "25,000,000", "220++", "40,000", "25", "13LV"),
        ("10.10 SAT", "19:00", "#4 STAG SATELLITE", "15 SEED", "WIN 1 SEAT", "8 TO 1", "20,000", "15", "12LV"),
        ("10.11 SUN", "13:00", "#5 ROYAL HIGH-ROLLER", "1 TICKET / 80GP", "60,000,000", "99++", "75,000", "40", "14LV"),
        ("10.11 SUN", "18:00", "#6 MYSTERY HERALD", "1 TICKET / 25GP", "20,000,000", "180++", "45,000", "25", "12LV"),
        ("10.12 MON", "14:00", "#7 MAIN EVENT FINAL", "MAIN 1 TICKET", "100,000,000", "500++", "40,000", "30", "13LV"),
    ])

fails = 0
fails += len(qc.run("1_WolfPack",  EA.W, EA.H, lambda: EA.render(P1, "out/animals/1_WolfPack.png")))
fails += len(qc.run("2_EagleHR",   EB.W, EB.H, lambda: EB.render(P2, B0.LV, "out/animals/2_EagleHR.png")))
fails += len(qc.run("3_TigerKO",   EA.W, EA.H, lambda: EA.render(P3, "out/animals/3_TigerKO.png")))
fails += len(qc.run("4_SharkDeep", EB.W, EB.H, lambda: EB.render(P4, B0.LV, "out/animals/4_SharkDeep.png")))
fails += len(qc.run("5_StagFest",  EC.W, EC.H, lambda: EC.render(P5, "out/animals/5_StagFest.png")))
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

items = [("① WOLF PACK · A", "out/animals/1_WolfPack.png"),
         ("② EAGLE HIGH-ROLLER · B", "out/animals/2_EagleHR.png"),
         ("③ TIGER BOUNTY · A", "out/animals/3_TigerKO.png"),
         ("④ SHARK DEEP STACK · B", "out/animals/4_SharkDeep.png"),
         ("⑤ ROYAL STAG FEST · C", "out/animals/5_StagFest.png")]
tw = 310; th = int(tw * Image.open(items[0][1]).height / Image.open(items[0][1]).width)
lab = 40; gap = 18; top = 64; cols = 5
Wm = cols * tw + (cols + 1) * gap; Hm = top + th + lab + gap
s = Image.new("RGB", (Wm, Hm), (12, 12, 18)); d = ImageDraw.Draw(s)
d.text((gap, 24), "동물 컨셉 5종 — 전부 가상 브랜드 · 각기 다른 무드", font=noto(28, 800), fill=(240, 240, 250), anchor="lm")
for i, (n, p) in enumerate(items):
    x = gap + i * (tw + gap); y = top
    s.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y))
    d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(64, 64, 84))
    d.text((x + tw / 2, y + th + lab / 2), n, font=noto(18, 700), fill=(214, 218, 232), anchor="mm")
s.save("out/animals/montage.jpg", quality=90); print("montage", s.size)
