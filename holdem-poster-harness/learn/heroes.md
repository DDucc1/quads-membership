# 히어로 이미지 자산 대장 (assets/heroes/)

> 방향1: 무료 스톡 리서치. 전 파일 **Pexels License**(상업 이용 무료·출처표기 불요·수정 허용).
> 원칙: 식별 가능한 실존 인물(프로 선수 등) 사진 금지 — 후드/마스크/손/사물만 채택(초상권 리스크 최소화).
> Openverse(CC) 검색은 실존 프로 사진 위주라 배제함(라이선스는 저작권만 해결, 초상권 별개).

| 파일 | 피사체 | 출처 (pexels.com/photo/{id}) | p003 사용 |
|---|---|---|---|
| px_29095597.jpg | 후드에서 연기 나는 인물(비식별) | 29095597 | SMOKE BLUFF |
| px_9859353.jpg | 카드 부채 펼친 손 | 9859353 | GOLDEN FAN |
| px_4253621.jpg | 블랙 에이스 4장 | 4253621 | BLACK ACES |
| px_33006404.jpg | 스포트라이트 로브 인물 | 33006404 | THE PILGRIM |
| px_8247082.jpg | 후드 기도 자세(비식별) | 8247082 | LAST PRAYER |
| px_19406595.jpg | 후드+마스크 | 19406595 | SILENT MASK |
| px_35448382.jpg | 25K 칩 타워(다크 레더) | 35448382 | TOWER 25K |

주의: assets/는 gitignore 대상 — 파일 자체는 커밋되지 않으므로 재복원 시
`https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=1600` 로 재다운로드.

## AI 생성 히어로 (방향2 — Pollinations/Flux, 키리스)

| 파일 | 프롬프트 요지 | p004 사용 |
|---|---|---|
| ai_ember.jpg | 후드+오렌지 엠버·연기, 림라이트 | EMBER HOOD |
| ai_chips.jpg | 골드 칩 타워 매크로, 스포트라이트 | GOLD STACK |
| ai_crown.jpg | golden crown 체스 킹, 대리석+연기 | CROWN GAMBIT |
| ai_hood_cards.jpg | 후드+카드(테스트, 카드 아티팩트) | (미사용) |

- 재생성: `python gen_hero.py "프롬프트" out.jpg` (기본 pollinations, 키 불요)
- 한계: 무료 티어 ~627×940 → 1080 업스케일 합성(화면용 OK, 인쇄 4×는 OPENAI_API_KEY 필요)

## 연기·후드 심화 (p005 — 사용자 확정 무드, 2026-07-31)

프롬프트 베이스: `cinematic photorealistic poster hero shot, dramatic rim lighting, film grain, high contrast,
black background, no text, no watermark, face completely hidden in deep shadow under the hood` + 변주.
축: 색온도(앰버/틸/마젠타/레드/그린) × 자세(정면/뒷모습/듀오/딜러 손) × 연기 밀도.
얼굴 식별되는 생성물은 재생성(비식별 원칙) — teal/red 2회, dealer 3회.

| 파일 | 변주 | p005 |
|---|---|---|
| sm_amber | 앰버 백라이트+엠버, 옆얼굴 실루엣 | AMBER EXHALE |
| sm_teal | 틸 연기, 후드 그늘 | COLD FRONT |
| sm_magenta | 마젠타 연기, 카드 | VIOLET WHISPER |
| sm_duo | 흑백 후드 듀오 | HEADS UP |
| sm_back | 안개 속 뒷모습 | WALK IN |
| sm_red | 레드 헤일로 실루엣 | RED HALO |
| sm_dealer | 그린 펠트 테이블 후드 | GREEN FELT |
| sm_green | 그린 연기 팬텀 | PHANTOM STACK |
