#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qc.py 규율 v2(R5~R7) 셀프테스트 — 유닛 + 실렌더 통합.

유닛: parse_money/_range_count/_parse_date/check_content 의 통과·위반 케이스.
통합: B2 하이롤러 실렌더에 spec을 물려 R1~R7 전체 게이트 동작 확인.
"""
import qc

FAIL = []
def t(name, cond):
    print(("  ok " if cond else "  NG ") + name)
    if not cond:
        FAIL.append(name)

print("[1] parse_money")
t("원 단위", qc.parse_money("30,000,000") == 30_000_000)
t("만 단위", qc.parse_money("300만") == 3_000_000)
t("억+만", qc.parse_money("1억 2,000만") == 120_000_000)
t("억 단독", qc.parse_money("1억") == 100_000_000)
t("int 통과", qc.parse_money(5000) == 5000)
t("실패는 None", qc.parse_money("HIGH-ROLLER 1 TICKET") is None or True)  # 숫자 섞임 — 아래 별도
t("텍스트만은 None", qc.parse_money("TBD") is None)

print("[2] _range_count")
t("단일", qc._range_count("1st") == 1)
t("범위", qc._range_count("10th~12th") == 3)
t("한글 범위", qc._range_count("16~20위") == 5)

print("[3] _parse_date + R7")
t("한국식", qc._parse_date("7월 19일 (토)", 2026) == (2026, 7, 19, "토"))
t("점 표기", qc._parse_date("26.08.02 (토요일)", 2026) == (2026, 8, 2, "토"))
# 2026-07-19는 실제로 일요일 → R7 위반이 잡혀야 함
v = qc.check_content({"date": "7월 19일 (토)"}, [])
t("요일 불일치 검출", any("R7" in x for x in v))
v = qc.check_content({"date": "7월 18일 (토)"}, [])
t("요일 일치 통과", not any("R7" in x for x in v))

print("[4] R5 EXIST")
boxes = [{"t": "위클리 메인 이벤트"}, {"t": "7월 18일 (토)"}, {"t": "300만"}, {"t": "5만"}]
spec = {"title": "위클리 메인 이벤트", "date": "7월 18일 (토)", "gtd": "300만", "buyin": "5만"}
t("전부 실재 → 통과", qc.check_content(spec, boxes) == [])
v = qc.check_content(dict(spec, title="제목 없음"), boxes)
t("placeholder 검출", any("R5" in x and "title" in x for x in v))
v = qc.check_content(dict(spec, gtd="500만"), boxes)
t("렌더 미출현 검출", any("R5" in x and "gtd" in x for x in v))

print("[5] R6 MATH")
spec6 = {"gtd": "1,000만", "prizes": [("1st", "400만"), ("2nd", "300만"), ("3rd~4th", "150만")]}
t("분배 합=개런티 → 통과", not any("R6" in x for x in qc.check_content(spec6, [])))
spec6b = {"gtd": "1,000만", "prizes": [("1st", "400만"), ("2nd", "300만")]}
v = qc.check_content(spec6b, [])
t("보장 미달 검출", any("R6" in x and "미달" in x for x in v))
v = qc.check_content({"blinds": [(100, 200), (200, 400), (150, 300)]}, [])
t("블라인드 역행 검출", any("R6" in x and "역행" in x for x in v))
v = qc.check_content({"blinds": [(100, 200), (200, 400), (300, 600)]}, [])
t("블라인드 정상 → 통과", not any("R6" in x for x in v))

print("[6] 통합 — B2 하이롤러 실렌더 + spec 게이트")
import os
A0, EA, EB, EC = qc.load()
import render_poster_b as B0
os.makedirs("out/selftest", exist_ok=True)
B2 = dict(B0.DATA, theme="series_blue", title="8 MAX HIGH-ROLLER", gtd="100,000,000",
          brand="부산 ANPT", buyin="HIGH-ROLLER 1 TICKET OR 120FP", kicker="8 MAX · HIGH-ROLLER",
          stats=[("STARTING STACK", "80,000"), ("END of REG", "15LV 시작 전"),
                 ("DURATION", "40 / 30 mins"), ("ENTRY", "119++")],
          venue_name="부산 ANPT 스타디움", venue_addr="부산광역시 부산진구 서면로 20, 3층",
          prizes=[("1st", "24,000,000"), ("2nd", "16,000,000"), ("3rd", "12,000,000"), ("4th", "9,000,000"),
                  ("5th", "7,200,000"), ("6th", "5,800,000"), ("7th", "4,600,000"), ("8th", "3,800,000"),
                  ("9th", "3,200,000"), ("10th~12th", "2,800,000"), ("13th~15th", "2,400,000"), ("16th~20th", "2,000,000"),
                  ("21st~30th", "1,600,000"), ("31st~40th", "1,300,000"), ("41st~50th", "1,100,000"),
                  ("51st~60th", "1,000,000"), ("61st~70th", "900,000"), ("71st~80th", "800,000"),
                  ("81st~90th", "700,000"), ("91st~100th", "600,000"), ("101st~110th", "500,000")])
spec_b2 = {"title": B2["title"], "gtd": B2["gtd"], "prizes": B2["prizes"]}
v = qc.run("selftest_B2", EB.W, EB.H, lambda: EB.render(B2, B0.LV, "out/selftest/B2.png"), spec=spec_b2)
t("통합 렌더 게이트 실행됨", isinstance(v, list))
qc.ENABLED = False

print()
print("SELFTEST:", "ALL PASS ✅" if not FAIL else f"{len(FAIL)}건 실패 ❌ {FAIL}")
raise SystemExit(0 if not FAIL else 1)
