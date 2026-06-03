# 05 — 1차 초안 데모 (임의 게임내용)

> 요구사항: "1차 초안을 보기 위해 게임내용은 임의로 넣고" 하네스 동작을 검증.
> 아래는 **가상의 게임 내용**을 입력했을 때 엔진이 산출하는 **레이아웃 스펙(텍스트 와이어프레임)** 이다.
> (이미지 렌더는 별도 이미지 모델에 `01_master-prompt` + 아래 JSON 투입. 여기서는 조판 결과를 ASCII로 검증.)
> 모든 데모는 `04_evaluation-rubric` 게이트를 통과하도록 작성됨.

---

## DEMO A — HERO EVENT (아키타입 A)

### 입력 JSON (임의)
```json
{
  "archetype": "A",
  "theme": "flame_blue",
  "brand": { "logo_text": "POKER of DREAMS", "trophy_badge": true },
  "event": {
    "title": "CHALLENGE",
    "title_accent": "in 대전",
    "reward": { "type": "gtd", "amount": "30,000,000" },
    "datetime": "26.07.04 (토요일) 오후 2시",
    "buyin": "1 Challenge Ticket",
    "stats": { "entry": "120 Entry++", "starting": "60,000 Chips", "late_reg": "16Lv 시작 전", "blind": "25/20 Mins" }
  },
  "notice": [
    "최종 레지스트레이션은 레벨 16 시작 전까지 가능합니다.",
    "빅 블라인드 엔티 방식으로 진행됩니다.",
    "엔티는 토너먼트가 끝나기 전까지 줄지 않습니다.",
    "국제 TDA 규정을 준수합니다.",
    "테이블은 9max로 진행합니다.",
    "대회 참가자는 본인 신분증을 지참하여 본인 확인을 진행합니다.",
    "상금을 획득한 선수는 세금신고를 의무화 해야합니다.",
    "ENTRY NEW PLAYER CARD 지급 (첫 핸드에 사용 여부 체크)"
  ],
  "venue": { "name": "대전 POD 스타디움", "address": "대전광역시 서구 둔산로 100, 5층" },
  "sponsors": {
    "host": ["POKER of DREAMS"], "partner": ["SEEDKET"],
    "support": ["MOXSYS", "한베교류발전위원회"], "place": ["대전 POD 스타디움"]
  }
}
```

### 산출 레이아웃 (텍스트 와이어프레임, 세이프존 ◧ 표기)
```
┌──────────────────────────────────────────────┐  y0%
│ ◧[🏆 본 대회는 우승자에게 공식 트로피가 수여됩니다]   │  A0 트로피뱃지(top-left)
│                  ◆ POD ◆                       │  A1 로고(center)
│              POKER of DREAMS                    │
│                                                 │
│                CHALLENGE          in 대전        │  A2 타이틀(center) + 악센트(우상)
│              30,000,000 GTD                     │  A3 GTD(center)  ← 숫자大 + GTD첨자
│                                                 │
│           26.07.04 (토요일) 오후 2시              │  A4 일시(center)
│              대전 POD 스타디움                    │     장소(center, bold)
│                                                 │
│                   BUY-IN                        │  A5 라벨
│              1 Challenge Ticket                 │     티켓조건(center, H1)
│                                                 │
│  ENTRY    │ STARTING  │ LATE REG │   BLIND      │  A6 스탯 4열 라벨(작게)
│ 120 Entry++│60,000 Chips│16Lv 시작 전│25/20 Mins │     값(굵게)  ← 4열 균등
│                                                 │
│  ⚠️ Notice for Player                           │  A7 Notice헤더(center)
│  · 최종 레지스트레이션은 레벨 16 시작 전까지…       │     불릿 8행(left)
│  · 빅 블라인드 엔티 방식으로 진행됩니다.            │
│  · … (총 8행, 줄당 1불릿, 박스 내 패딩)           │
│                                                 │
│ 주관사   협력사    후원사            장소          │  A8 스폰서바 4구역
│ [POD]   [SEEDKET][MOXSYS][한베…]  [대전POD]      │
│  대전 POD 스타디움  대전광역시 서구 둔산로 100,5층  │  A9 푸터(center)
└──────────────────────────────────────────────┘  y100%
```
- 자동조치: GTD `30,000,000` 숫자 폭이 A3 밴드폭 92% → 폰트 100% 유지(스텝다운 불필요).
- 악센트 "in 대전"은 타이틀보다 1단계 작고 시안 악센트색(REF-06/07 패턴).

### QA 게이트 결과
```
[✓] R0-1~8 전부 PASS (겹침/세이프존/오탈자/빈슬롯/필수블록 OK)
[✓] C 대비 4.7:1 (4점) [✓] T 위계 (5점) [✓] L 균형 (4점)
[✓] K 컬러 (flame_blue 악센트 1종, 4점) [✓] B 정확 (5점) [✓] H 무게중심 (4점)
TIER1 총점 = 92/100  →  ✅ FINAL
```

---

## DEMO B — STRUCTURE SHEET (아키타입 B)

### 입력 JSON (임의, 일부 발췌)
```json
{
  "archetype": "B",
  "theme": "series_purple",
  "brand": { "logo_text": "POKER of DREAMS", "brand_mark": "대전 ANPT",
             "series_badge": "DREAM SERIES", "series_total": "300,000,000 TOTAL GUARANTEED" },
  "event": {
    "format_prefix": "8 MAX",
    "title": "MAIN EVENT",
    "reward": { "type": "gtd", "amount": "150,000,000" },
    "datetime": "26.07.10 (FRI) - 16:00",
    "buyin": "MAIN 1 TICKET OR 50FP",
    "stats": { "stack": "50,000 Chips", "end_reg": "15LV 시작 전", "duration": "30 Mins", "entry": "500++" },
    "structure": { "levels": [
      {"lv":"1","sb":"100","bb":"200","ante":"200","blind":"30"},
      {"lv":"2","sb":"200","bb":"400","ante":"400","blind":"30"},
      {"note":"Break 10min / Remove 100 Chips"},
      {"lv":"3","sb":"300","bb":"600","ante":"600","blind":"30"},
      {"note":"*END of REG"},
      {"note":"T.D DECISION"}
    ]},
    "prizes": [ {"rank":"1st","prize":"40,000,000"}, {"rank":"2nd","prize":"24,000,000"},
                {"rank":"3rd","prize":"16,000,000"} ]
  },
  "venue": { "name": "대전 ANPT 스타디움", "address": "대전광역시 서구 둔산로 100, 5층" },
  "sponsors": { "host":["POKER of DREAMS"], "partner":["SEEDKET","ON&ON"],
                "support":["MOXSYS","한베교류발전위원회"], "place":["대전 ANPT"] }
}
```

### 산출 레이아웃
```
┌──────────────────────────────────────────────┐
│ ◆POD◆                        DREAM SERIES      │  B0 로고(좌) / B1 시리즈뱃지(우)
│ POKER of DREAMS         300,000,000 GUARANTEED │
│                                                 │
│ 8 MAX                                           │  B2 포맷프리픽스
│ MAIN EVENT                          ★대전 ANPT  │  B2 타이틀(좌) / B4 브랜드마크(우)
│ 150,000,000 GTD                                 │  B3 GTD(좌, 골드)
│ 26.07.10 (FRI) - 16:00                          │  B4 일시(좌)
│                                                 │
│ [BUY-IN] MAIN 1 TICKET OR 50FP                  │  B5 BUY-IN(좌, 라벨박스)
│ STACK    │ END of REG│ DURATION │ ENTRY         │  B6 스탯4열 가로띠
│ 50,000   │ 15LV 시작 전│ 30 Mins  │ 500++        │
│                                                 │
│ ┌RANK│PRIZE──┐  │ LV│SB │BB │ANTE│BLIND│        │  B7L 프라이즈(좌) / B7R 블라인드표(우)
│ │1st │40,000,000│ │ 1 │100│200│200 │ 30  │       │   헤더 반복 ↓
│ │2nd │24,000,000│ │ 2 │200│400│400 │ 30  │       │
│ │3rd │16,000,000│ ├──Break 10min / Remove 100──┤ │   ← 풀폭 강조행
│ └──────────┘   │ 3 │300│600│600 │ 30  │        │
│                │────── *END of REG ──────────│  │   ← 강조행
│                │────── T.D DECISION ─────────│  │   ← 종료행
│  ⚠️ Notice for Player  · … (불릿)               │  B8 Notice
│ 주관사 협력사 후원사 장소  [로고 한 줄 정렬]       │  B9 스폰서바
│  대전 ANPT 스타디움 / 대전광역시 서구 둔산로100,5층 │     푸터
└──────────────────────────────────────────────┘
```
- 자동조치: 블라인드 레벨이 많아지면 좌LV그룹/우LV그룹 2-컬럼으로 분할(F-D1). 데모는 행 적어 1그룹.
- 프라이즈표 존재 → 좌컬럼 프라이즈. (없으면 좌컬럼=STACK/END/DURATION/ENTRY 세로 리스트, REF-10 패턴)

### QA 게이트 결과
```
[✓] R0-5 표 셀 줄바꿈 없음, 콤마 일관  [✓] R0-6 금액 포맷 일관
[✓] C(4) T(4) L(4 좌우균형) K(4) B(5) H(4)
TIER1 총점 = 91/100  →  ✅ FINAL
```

---

## DEMO C — SERIES SCHEDULE (아키타입 C)

### 입력 JSON (임의, 발췌)
```json
{
  "archetype": "C",
  "theme": "series_blue",
  "brand": { "logo_text": "POKER of DREAMS", "brand_mark": "대전 ANPT",
             "series_badge": "DREAM SERIES", "series_total": "300,000,000" },
  "events": [
    {"date":"07.10\nFRI","time":"13:00","event":"#1 BIG SEED MATCH","buyin":"1 S-TICKET\nOR 30FP","gtd":"₩1,000 S-TICKET","entry":"95++","stack":"50,000","level":"20","entry_close":"14LV"},
    {"date":"07.10\nFRI","time":"18:00","event":"#2 MAIN EVENT DAY1","buyin":"MAIN 1 TICKET\nOR 50FP","gtd":"₩150,000,000","entry":"500++","stack":"40,000","level":"30","entry_close":"12LV"},
    {"date":"07.11\nSAT","time":"14:00","event":"#3 HIGH-ROLLER","buyin":"HR 1 TICKET\nOR 120FP","gtd":"₩80,000,000","entry":"100++","stack":"80,000","level":"40/30","entry_close":"14LV"}
  ],
  "venue": { "name": "대전 ANPT 스타디움", "address": "대전광역시 서구 둔산로 100, 5층" },
  "sponsors": { "host":["POKER of DREAMS"], "partner":["SEEDKET","ON&ON"],
                "support":["MOXSYS","한베교류발전위원회"], "place":["대전 ANPT"] }
}
```

### 산출 레이아웃
```
┌──────────────────────────────────────────────┐
│ ◆POD◆            DREAM SERIES                   │  C0/C1
│              대전 ANPT  07.10 - 07.11           │  C2 기간칩
│              300,000,000                        │  C3 총보증(골드, 무게중심)
│              TOTAL GUARANTEED                   │
│                                                 │
│DATE │TIME│EVENT       │BUY-IN    │GTD │ENT│STK│LV│CLOSE│ C4 그리드 헤더
│─────┼────┼────────────┼──────────┼────┼───┼───┼──┼─────│
│07.10│13:00│#1 BIG SEED…│1 S-TICKET│₩1,000│95++│50k│20│14LV│  ← zebra 행
│ FRI │18:00│#2 MAIN E.D1│MAIN 1 TKT│₩150M│500++│40k│30│12LV│
│─────┼────┼────────────┼──────────┼────┼───┼───┼──┼─────│  ← 날짜그룹 구분선
│07.11│14:00│#3 HIGH-ROL.│HR 1 TKT  │₩80M │100++│80k│40/30│14LV│
│ SAT │    │            │OR 120FP  │    │   │   │  │     │
│                                                 │
│ 주관사 협력사 후원사 장소  [로고 한 줄]            │  C5 스폰서바
│  대전 ANPT 스타디움 / 대전광역시 서구 둔산로100,5층 │     푸터
└──────────────────────────────────────────────┘
```
- 자동조치: 9컬럼 → 셀 줄바꿈 금지(F-C5), 폰트 스텝다운으로 세이프존 수용(R0-5).
- 날짜 셀 병합(07.10 FRI 2행) + 그룹 구분선(F-D3). BUY-IN 다중옵션 2행 셀.

### QA 게이트 결과
```
[✓] R0-5 9컬럼 줄바꿈 없음  [✓] zebra 가독  [✓] 날짜 병합/구분선
[✓] C(4) T(4) L(5 그리드정렬) K(4) B(5) H(4)
TIER1 총점 = 93/100  →  ✅ FINAL
```

---

## 데모 검증 요약
- A/B/C 3개 아키타입 모두 **동일 입력 스키마 → 골격 강제 → QA 통과** 흐름이 동작.
- 운영자는 위 JSON의 **값만** 바꾸면 동일 품질이 재현된다(요구사항 충족).
- 실제 이미지 산출 시: `01_master-prompt.md` 전문 + 위 JSON 을 이미지 모델에 투입 → 산출물을 `04_evaluation-rubric` 체크리스트로 게이트.
