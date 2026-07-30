#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실습 러너 — learn/practice 사이클. V6 스트럭처 일체형, 컬러웨이 2종. QC(스펙 포함) 경유.
DATA/SPEC은 make_hires.py 등에서 재사용(import) — 실행부는 __main__ 가드."""
import os
from PIL import Image, ImageDraw

BLINDS = [(100, 200), (200, 300), (200, 400), "10 MINUTES BREAK",
          (300, 500), (300, 600), (400, 800), "10 MINUTES BREAK & END REGI",
          (500, 1000), (600, 1200), (1000, 1500), (1000, 2000),
          "60 MINUTES DINNER BREAK & CHIP RACE 100",
          (1500, 2500), (1500, 3000), (2000, 4000), (3000, 5000),
          "10 MINUTES BREAK & CHIP RACE 500",
          (3000, 6000), (4000, 8000), (5000, 10000), (6000, 12000),
          "10 MINUTES BREAK & CHIP RACE 1000",
          (10000, 15000), (10000, 20000), (15000, 25000), (15000, 30000),
          "10 MINUTES BREAK",
          (20000, 40000), (25000, 50000), (30000, 60000), (40000, 80000),
          "10 MINUTES BREAK & CHIP RACE 5000",
          (50000, 100000), (60000, 120000), (75000, 150000), (100000, 200000)]

PRIZES = [("1ST", "5,000,000"), ("2ND", "3,000,000"), ("3RD", "2,000,000"),
          ("4TH", "1,500,000"), ("5TH", "1,200,000"), ("6TH", "1,000,000"),
          ("7TH", "800,000"), ("8TH", "700,000"), ("9TH", "600,000")]

DATA = dict(
    theme="ice_blue",
    title="NOVA CHAMPIONS CUP",
    gtd="15,000,000",
    info=["EVENT NAME : NOVA CHAMPIONS CUP",
          "OFFICIAL VENUE : 노바 스타디움 강남",
          "DATE : 26.08.15 (SAT)",
          "STARTING TIME : 13:00",
          "TOTAL PRIZE : 15,000,000 GTD",
          "BUY IN : 매장이용권 10매 OR NV 시드권",
          "FREEZE OUT EVENT",
          "LATE REG : 16:20 (END OF LEVEL 6)",
          "STARTING CHIPS : 50,000 (250BB)",
          "DURATION : 25 MIN"],
    prizes=PRIZES,
    desc=["·  모든 토너먼트 룰은 국제 TDA 규정에 의하며", "    TD의 결정이 최종 결정됩니다.",
          "·  빅 블라인드 엔티 방식으로 진행됩니다.",
          "·  라이브 핸드 중 전자기기 사용을 금지합니다.",
          "·  DEAL MAKING 은 허용하지 않습니다.",
          "·  상금 획득 선수는 세금 신고 의무가 있습니다.",
          "·  본인 계좌로만 후원 시상금을 받을 수 있습니다."],
    blinds_disp=BLINDS,
    footer="노바 스타디움 강남 · 서울 강남구 노바로 77, 6층 · 문의 010-0000-0000 · 카카오 오픈톡 : 노바홀덤",
    sponsors=["NOVA", "WINLAB", "CGX", "MRHB", "OPENDECK"])

SPEC = dict(title=DATA["title"], date="26.08.15 (SAT)", time="13:00",
            buyin="매장이용권 10매 OR NV 시드권", gtd=DATA["gtd"],
            prizes=PRIZES, blinds=[b for b in BLINDS if isinstance(b, tuple)], year=2026)

if __name__ == "__main__":
    import qc
    A0, EA, EB, EC = qc.load()
    import render_structure as RS
    from render_poster import noto

    os.makedirs("out/practice", exist_ok=True)

    fails = 0
    fails += len(qc.run("P001_Cyan", RS.W, RS.H,
                        lambda: RS.render(DATA, "out/practice/p001_cyan.png"), spec=SPEC))
    D2 = dict(DATA, theme="nebula_pink")
    fails += len(qc.run("P001_Pink", RS.W, RS.H,
                        lambda: RS.render(D2, "out/practice/p001_pink.png"), spec=SPEC))
    qc.ENABLED = False
    print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")

    # 몽타주
    items = [("V6 스트럭처 일체형 — Cyan", "out/practice/p001_cyan.png"),
             ("V6 스트럭처 일체형 — Pink (컬러웨이)", "out/practice/p001_pink.png")]
    tw = 430; th = int(tw * RS.H / RS.W); lab = 40; gap = 18; top = 60
    Wm = 2 * tw + 3 * gap; Hm = top + th + lab + gap
    s = Image.new("RGB", (Wm, Hm), (12, 12, 18)); dm = ImageDraw.Draw(s)
    dm.text((gap, 22), "실습 p001 — 스트럭처 일체형 (r001 계열)", font=noto(26, 800),
            fill=(240, 240, 250), anchor="lm")
    for i, (n, p) in enumerate(items):
        x = gap + i * (tw + gap)
        s.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, top))
        dm.rectangle([x, top, x + tw - 1, top + th - 1], outline=(64, 64, 84))
        dm.text((x + tw / 2, top + th + lab / 2), n, font=noto(16, 700), fill=(214, 218, 232), anchor="mm")
    s.save("out/practice/montage.jpg", quality=90); print("montage", s.size)
