# HANDOFF — 세션 이어서 작업하기

> 새 세션(또는 새 환경)에서 이 문서만 읽으면 바로 이어서 작업할 수 있도록 정리한 현황판.
> 브랜치: `claude/holdem-poster-harness-I58wz` · 마지막 갱신: 2026-07-15 세션 (로컬 Windows PC)

---

## 0. 환경 복원 (새 컨테이너에서 최초 1회)

폰트/배경/산출물은 gitignore 되어 있어 재생성이 필요하다:

```bash
cd holdem-poster-harness
pip install Pillow numpy
bash assets/fetch_fonts.sh        # 폰트 6종 (GitHub에서 다운로드 — 이 환경은 GitHub만 허용)
python3 bg_generate.py all        # 일반 테마 배경 21종
python3 bg_animals.py             # 동물 테마 배경 5종
```

검증(전부 QC PASS가 나와야 정상):

```bash
python3 make_examples.py          # 기본 5장 (B3+A1+C1)
python3 make_animals.py           # 동물 컨셉 5장 (가상 브랜드)
python3 make_layouts.py           # B형 레이아웃 변형 5장 (V1~V5)
```

---

## 1. 무엇을 만들었나 (아키텍처)

**목표**: 게임 내용만 입력하면 레퍼런스급 홀덤 토너먼트 포스터가 자동 산출되는 시스템.
**기본 베이스 = B형(블라인드+상금표 포함)**. A(히어로)/C(일정표)는 파생.

```
입력(JSON dict) → 렌더러(A/B/C, 레이아웃 V1~V5) → Codex QC 게이트 → PASS만 출고
```

| 파일 | 역할 |
|---|---|
| `render_poster.py` | 공용 헬퍼(폰트/measure/fit_font/**fit_common**/**theight**/text_img/팔레트 자동유도) + 구형 A렌더러 |
| `render_editorial.py` | **A형** 에디토리얼 렌더러 + 공용 크래프트(grade/frost/**rect_blend**/vtext/spade) |
| `render_editorial_b.py` | **B형(기본 베이스)** — V1 클래식 스플릿(좌 상금/우 블라인드 2그룹) |
| `render_editorial_c.py` | **C형** 시리즈 스케줄 그리드 |
| `layout_variants.py` | **B형 변형 V2~V5** (포디움/센터대칭/사이드바/쇼케이스) — 공용 컴포넌트 조립식 |
| `qc.py` | **Codex QC 게이트** — 아래 3절 |
| `bg_generate.py` | 일반 테마 배경 21종(THEME_SPECS/THEME_ACCENT) |
| `bg_animals.py` | 동물 문장 배경 5종(울프문/이글/타이거/샤크/스태그) |
| `make_examples.py` / `make_animals.py` / `make_layouts.py` | 데모 러너(QC 경유 + 몽타주) |
| `wizard.html` | **배포용 단독 위저드**(사장님 입력 플로우, 의존성 0) |
| `01~08_*.md`, `schema/` | 하네스 스펙 문서(골격/분류/평가/품질/QC) |

## 2. 핵심 불변 규칙 (건드리면 안 되는 것)

- **fit_common**: 동일 역할 요소(스탯 값/라벨, 표 셀, 불릿)는 공통 크기 하나로 — 열마다 제각각 축소 금지.
- **theight**: 세로 간격 계산은 measure()가 아니라 theight()(어센더 포함) — 겹침 버그의 근원이었음.
- **rect_blend**: RGBA 캔버스 반투명 사각형은 반드시 이걸로(ImageDraw.rectangle은 알파 SET → 불투명 순백 버그).
- **브랜드는 데이터**: `logo_mark`/`logo_word` 필드 — 하드코딩 금지(레퍼런스 브랜드 배제 요구).
- QC를 통과 못 하면 출고하지 않는다(무승인 자동 발행의 전제).

## 3. Codex QC 게이트 (`qc.py`)

렌더 중 모든 텍스트 bbox를 자동 계측(ImageDraw 전역 패치 + text_img/vtext/frost 마킹) 후 검사:

| 규칙 | 내용 |
|---|---|
| R1 CANVAS | 캔버스 이탈 |
| R2 SAFE | 세이프존(좌우6%/상하3%) 침범 |
| R3 OVERLAP | 텍스트 상호 겹침(양축 3px 초과) |
| R4 SIZE | 같은 행 인접 텍스트의 어중간한 크기 차(1.04~1.75x). **frost 패널이 다르면 비교 제외**(패널 인지) |

사용: `import qc; A0,EA,EB,EC = qc.load()` (이 순서 필수 — 패치 후 렌더러 로드) → `qc.run(name, W, H, fn)`.
한계: 색 대비(R5)는 아직 육안 — 백로그 참조.

## 4. 사용자가 확정한 방향 (의사결정 기록)

1. **B형(블라인드+상금표)이 기본 베이스** — 나머지는 특수 요청. 단일 양식 고수 X → V1~V5 변형 제공.
2. **레퍼런스 브랜드(POD/ANPT 등) 완전 배제** — 가상 브랜드로 데모. 어떤 요구든 **현재 수준이 최소 퀄리티**.
3. **규칙은 Claude가 추출 → 사용자가 승인**. 규율 없는 업계이므로 우리가 하우스 스타일을 정의.
4. **인쇄급 초고해상**이 최종 화질 목표(현재 1080폭은 화면용 — 백로그).
5. 서비스 형태: 사장님이 **위저드에 입력만** 하면 QC 통과본이 무승인 자동 발행. 형태 규정이 아니라 **품질 규정**(불변식+게이트)로 자유도 확보.
6. C형 그리드 폰트 상향(12→최대 19px), 위저드는 이모지 없는 전문 톤.
7. **(2026-07-15) 서비스 제공 맥락 4종 확정** — 사장님 사용 흐름 시뮬레이션 결과: ① 최초 온보딩(1회) ② 정규 토너먼트(최빈, 복제→바뀐 것만 수정, 목표 30초) ③ 특별 이벤트(풀 입력→시안 3종 비교) ④ 부분 수정(발행본 요소 클릭→해당 요소만 재렌더·재검수). **"언제든 요청에 따라 수정 가능한 유연함"이 전 맥락 필수 요건.**
8. **(2026-07-15) 디자인 유사성·취향 이슈 해소 = A+B 전략 확정** — A: 브랜드 킷(문장/컬러/타이포 무드를 데이터로 주입, 매장 고유 시드로 배경 변형) + B: 온보딩 취향 캘리브레이션(A/B 선택 3문항→서체·밀도·구도 개인화). C(상권 배타 배정)는 스케일 단계에 설계만. → 여러 업체가 써도 디자인이 겹치지 않게 하는 구조적 해법.

## 4.5. 서비스 맥락 데모 4종 (`demos/`, 2026-07-15)

의존성 0 단독 HTML. wizard.html 디자인 시스템 계승(그린 액센트, 라이트/다크, 이모지 없는 전문 톤). 포스터 미리보기는 브랜드 킷 파라미터에 실시간 반응하는 CSS/SVG 목업(실제 렌더는 파이썬 엔진 몫).

| 파일 | 맥락 | 핵심 장치 |
|---|---|---|
| `demos/demo1_onboarding.html` | 최초 온보딩 | 브랜드 킷(문장 8종×팔레트 8종) + 취향 A/B 3문항 → 하우스 스타일 확정, 미니 포스터 3장 |
| `demos/demo2_regular.html` | 정규 토너먼트 | 지난 포스터 복제→4개 필드만 수정, 경과 타이머, "다른 것도 바꾸기" 아코디언(유연 수정), QC 체크리스트 애니메이션 |
| `demos/demo3_special.html` | 특별 이벤트 | 풀 입력→시안 3종(V1/V3/V4) 동시 생성·비교, 강조 요소 토글(개런티/대회명) |
| `demos/demo4_edit.html` | 부분 수정 | 발행본 포스터에서 요소 클릭→인라인 수정→해당 요소만 재렌더+재검수→재발행, 수정 이력 로그 |

## 5. 아트팩트 링크 (검토용 페이지)

- **데모 1 온보딩(브랜드 킷+취향)**: https://claude.ai/code/artifact/329a06f6-077d-411b-b81b-b214ed11498a
- **데모 2 정규 토너먼트(30초 플로우)**: https://claude.ai/code/artifact/5434f119-3f6d-4ec4-a9d5-3b2c803328af
- **데모 3 특별 이벤트(시안 3종)**: https://claude.ai/code/artifact/70b2eb0b-ce09-4c39-a0a5-e78aaf89abc2
- **데모 4 부분 수정(클릭 편집)**: https://claude.ai/code/artifact/a5bf3fdf-95f9-4f81-95cb-3a344b669bc4
- 동물 5종 상세 갤러리: https://claude.ai/code/artifact/200c1b20-26b6-4242-8ad6-6f8e5234b6f4
- 주문 위저드(전문판): https://claude.ai/code/artifact/e5767e6d-3979-42e5-ad27-51272f751f8c (= `wizard.html`)
- 서비스 설계 기획안: https://claude.ai/code/artifact/143247c6-a3df-4ceb-9d23-87a8f96acd18
- 재설계 의사결정 브리프: https://claude.ai/code/artifact/021da3f3-a3d6-485f-95da-cbd13fbf199a
- (구) 기본 5장 갤러리: https://claude.ai/code/artifact/a6c7f70d-7550-4957-adc4-3432180e6f00

## 6. 백로그 (다음 작업 후보, 우선순위 순)

0. **데모 4종 사용자 피드백 반영** — 아트팩트 검토 후 플로우·문구·수정 유연성 보강 (진행 중인 축).
1. **레이아웃 선택을 위저드에 반영** — 데모 3에서 시안 3종 비교 방식으로 방향 잡힘. wizard.html 본편에 역이식.
2. **인쇄급 고해상 렌더 플래그** — 2400px+ 네이티브(전역 스케일 팩터로 좌표·폰트 일괄 확대).
3. **R5 CONTRAST** — 렌더 픽셀 샘플링 기반 색 대비 자동검사(QC의 마지막 육안 몫 제거).
4. **위저드 실사용화** — 입력값 → JSON 다운로드/전송 → CLI 렌더 연동.
5. 실사 사진 히어로(hero_image 경로는 구현됨 — 사용자 업로드 대기).
6. 하네스 문서(01/03)에 V1~V5 정식 등재.
7. GitHub Pages 배포(머지 필요).

## 7. 주의사항

- 이 원격 환경은 **네트워크가 GitHub만 허용** — 외부 스톡/폰트 CDN 불가. 이미지가 필요하면 채팅 업로드 또는 레포 경유.
- `make_examples.py`에는 아직 레퍼런스 브랜드(POD 등)가 남아 있음(회귀 테스트용 구데이터) — 대외 데모에는 `make_animals.py`/`make_layouts.py` 사용.
- 환경 재시작 시 pip 패키지·폰트·배경이 사라짐 → 0절 복원 절차 실행.
- **로컬 Windows PC에서 작업 시**: `python3` 대신 `python`, 실행 전 `PYTHONUTF8=1` 필요(qc.py의 ✅ 출력이 cp949에서 크래시). 폰트는 fetch_fonts.sh 대신 PowerShell Invoke-WebRequest로 받아도 됨. 2026-07-15 로컬 복원 완료 상태(렌더 15장 전부 QC PASS 확인).
