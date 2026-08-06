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
