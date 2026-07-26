#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex QC 레이어 — 까다로운 규격 검증 리뷰어.

렌더 중 그려지는 모든 텍스트(직접 draw + 텍스트 이미지 합성)의 바운딩박스를
자동 기록하고, 다음 위반을 검출한다:
  R1 CANVAS  : 캔버스 이탈
  R2 SAFE    : 세이프존(좌우 6% / 상하 3%) 침범
  R3 OVERLAP : 텍스트 상호 겹침 (양축 3px 초과 침투)
  R4 SIZE    : 같은 행 인접 텍스트의 어중간한 크기 차 (1.04~1.75x)

규율 v2 (demos/plan.html §04) 콘텐츠 정합 — run()에 spec을 넘기면 함께 검사:
  R5 EXIST   : 필수 값(title/date/buyin/gtd) 실재 · placeholder 금지 · 렌더 출현
  R6 MATH    : 상금 분배 합 ≥ 개런티(보장 미달 금지), 블라인드 단조 증가
  R7 DATE    : 표기 요일과 실제 달력 일치

위반이 하나라도 있으면 FAIL — 해당 산출물은 출고 금지.
role() 컨텍스트로 요소 역할 태깅 가능(위계 검사 R8+의 선행 인프라).

사용:
    import qc
    rp, EA, EB, EC = qc.load()          # 계측 패치 후 렌더러 로드 (이 순서 필수)
    qc.run("이름", W, H, lambda: EA.render(...))
"""
import re
from contextlib import contextmanager
from PIL import Image, ImageDraw

BOXES = []
PANELS = []        # frost 패널 경계 — 서로 다른 패널의 텍스트는 R4(크기 일관성) 비교 대상이 아님
ENABLED = True
CANVAS = None      # run()이 지정한 메인 캔버스 크기 — 이 크기의 이미지에 그린 것만 기록
                   # (text_img/vtext의 내부 스크래치 캔버스 드로잉을 제외하기 위함)
_ROLE = []         # role() 컨텍스트 스택 — 규율 v2 위계 검사(R8+)용 역할 태깅

@contextmanager
def role(name):
    """렌더러가 요소의 의미 역할(gtd/title/date/buyin/...)을 선언하는 컨텍스트.
    with qc.role("gtd"): draw.text(...) — 블록 안에서 기록되는 박스에 r=name이 붙는다."""
    _ROLE.append(str(name))
    try:
        yield
    finally:
        _ROLE.pop()

def _on_canvas(draw_or_img):
    if CANVAS is None:
        return True
    try:
        return tuple(draw_or_img.im.size) == tuple(CANVAS)
    except Exception:
        return False

# ---- 계측: ImageDraw.text 전역 패치 ----
_orig_text = ImageDraw.ImageDraw.text
def _ptext(self, xy, text, *args, **kw):
    if ENABLED and text is not None and str(text).strip() and _on_canvas(self):
        try:
            fnt = kw.get("font")
            b = self.textbbox(xy, str(text), font=fnt, anchor=kw.get("anchor"))
            BOXES.append({"k": "text", "t": str(text), "b": [float(v) for v in b],
                          "fs": float(getattr(fnt, "size", 0)) or None,
                          "r": _ROLE[-1] if _ROLE else None})
        except Exception:
            pass
    return _orig_text(self, xy, text, *args, **kw)
ImageDraw.ImageDraw.text = _ptext

# ---- 계측: 텍스트 이미지(alpha_composite) 패치 — qc_text 마킹된 것만 기록 ----
_orig_ac = Image.Image.alpha_composite
def _pac(self, im, dest=(0, 0), *args, **kw):
    if ENABLED and getattr(im, "qc_text", None):
        BOXES.append({"k": "timg", "t": im.qc_text,
                      "b": [float(dest[0]), float(dest[1]),
                            float(dest[0] + im.width), float(dest[1] + im.height)],
                      "r": _ROLE[-1] if _ROLE else None})
    return _orig_ac(self, im, dest, *args, **kw)
Image.Image.alpha_composite = _pac

def load():
    """text_img/vtext 산출물에 qc_text 마킹을 심은 뒤 렌더러들을 로드한다."""
    import render_poster as rp
    _oti = rp.text_img
    def ti(t, f, top, bottom=None, pad=10):
        out, w, h = _oti(t, f, top, bottom, pad)
        out.qc_text = str(t)
        return out, w, h
    rp.text_img = ti
    import render_editorial as EA
    _ofr = EA.frost
    def fr(img, box, radius, acc, alpha=140, tab=True):
        if ENABLED:
            PANELS.append([float(v) for v in box])
        return _ofr(img, box, radius, acc, alpha, tab)
    EA.frost = fr
    _ovt = EA.vtext
    def vt(text, font, fill, ls=3):
        out = _ovt(text, font, fill, ls)
        out.qc_text = "|" + str(text)
        return out
    EA.vtext = vt
    import render_editorial_b as EB
    import render_editorial_c as EC
    return rp, EA, EB, EC

# ---- 검사 ----
def _merge_runs(boxes, gap=14.0):
    """draw_ls가 문자 단위로 남긴 박스를 같은 행의 런으로 병합."""
    bs = [dict(x) for x in boxes]
    changed = True
    while changed:
        changed = False
        out, used = [], [False] * len(bs)
        for i in range(len(bs)):
            if used[i]:
                continue
            a = dict(bs[i]); used[i] = True
            for j in range(i + 1, len(bs)):
                if used[j]:
                    continue
                c = bs[j]
                ah = a["b"][3] - a["b"][1]; ch = c["b"][3] - c["b"][1]
                if max(ah, ch) > 2.2 * min(ah, ch):      # 세로 레일 등 이질 요소 병합 금지
                    continue
                if abs((a["b"][1] + a["b"][3]) / 2 - (c["b"][1] + c["b"][3]) / 2) > 0.6 * min(ah, ch):
                    continue
                hgap = max(a["b"][0], c["b"][0]) - min(a["b"][2], c["b"][2])
                if hgap > gap:
                    continue
                if a.get("fs") != c.get("fs"):
                    a["fs"] = None
                a["t"] = a["t"] + c["t"]
                a["b"] = [min(a["b"][0], c["b"][0]), min(a["b"][1], c["b"][1]),
                          max(a["b"][2], c["b"][2]), max(a["b"][3], c["b"][3])]
                used[j] = True; changed = True
            out.append(a)
        bs = out
    return bs

def _iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    if inter <= 0: return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / max(ua, 1e-6)

def _panel_of(b):
    cx = (b[0] + b[2]) / 2; cy = (b[1] + b[3]) / 2
    for i, p in enumerate(PANELS):
        if p[0] <= cx <= p[2] and p[1] <= cy <= p[3]:
            return i
    return -1

def check(boxes, W, H, tol=1.5, depth=3.0):
    sl, st = round(W * 0.06), round(H * 0.03)
    sr, sb = W - sl, H - st
    bs = _merge_runs(boxes)
    v = []
    for x in bs:
        b = x["b"]
        if b[0] < -tol or b[1] < -tol or b[2] > W + tol or b[3] > H + tol:
            v.append(f"R1 CANVAS  '{x['t'][:26]}' box={list(map(round, b))}")
        elif b[0] < sl - tol or b[2] > sr + tol or b[1] < st - tol or b[3] > sb + tol:
            v.append(f"R2 SAFE    '{x['t'][:26]}' box={list(map(round, b))} safe=[{sl},{st},{sr},{sb}]")
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, c = bs[i]["b"], bs[j]["b"]
            if _iou(a, c) > 0.8:            # 동일 요소 중복 드로우(섀도 등)
                continue
            iw = min(a[2], c[2]) - max(a[0], c[0])
            ih = min(a[3], c[3]) - max(a[1], c[1])
            if iw > depth and ih > depth:
                v.append(f"R3 OVERLAP '{bs[i]['t'][:26]}' × '{bs[j]['t'][:26]}' depth=({round(iw)},{round(ih)})")
    # R4: 같은 행의 인접 텍스트인데 폰트 크기가 어중간하게 다름(의도된 위계 1.75x 이상은 허용)
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, c = bs[i], bs[j]
            fa, fc = a.get("fs"), c.get("fs")
            if not fa or not fc or fa == fc:
                continue
            A, C = a["b"], c["b"]
            ah = A[3] - A[1]; ch = C[3] - C[1]
            if abs((A[1] + A[3]) / 2 - (C[1] + C[3]) / 2) > 0.35 * min(ah, ch):
                continue
            hgap = max(A[0], C[0]) - min(A[2], C[2])
            if hgap <= 0 or hgap > 200:
                continue
            if _panel_of(A) != _panel_of(C):     # 다른 패널(컨테이너)의 텍스트는 비교 제외
                continue
            r = max(fa, fc) / min(fa, fc)
            if 1.04 < r < 1.75:
                v.append(f"R4 SIZE    '{a['t'][:26]}'({fa:g}) × '{c['t'][:26]}'({fc:g}) 같은 행 크기 불일치")
    return v

# ---- 콘텐츠 정합 (규율 v2 · R5~R7) ----
PLACEHOLDERS = {"", "—", "-", "?", "tbd", "미정", "제목 없음", "대회명", "날짜", "시간", "none"}
_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

def _norm(s):
    """존재성 대조용 정규화 — 공백·쉼표·구두점 제거 + casefold."""
    return re.sub(r"[\s,._·|]+", "", str(s)).casefold()

def parse_money(s):
    """'30,000,000' / '300만' / '1억 2,000만' / 5000 → 원 단위 int. 실패 시 None."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    t = str(s).replace(",", "").replace(" ", "")
    total, matched = 0, False
    m = re.search(r"(\d+(?:\.\d+)?)억", t)
    if m:
        total += int(float(m.group(1)) * 100_000_000); matched = True
        t = t[m.end():]
    m = re.search(r"(\d+(?:\.\d+)?)만", t)
    if m:
        total += int(float(m.group(1)) * 10_000); matched = True
    if matched:
        return total
    m = re.fullmatch(r"\d+", re.sub(r"[^\d]", "", t) or "")
    return int(m.group(0)) if m else None

def _range_count(label):
    """상금 순위 라벨의 인원수: '1st'→1, '10th~12th'/'10~12위'→3."""
    nums = [int(n) for n in re.findall(r"\d+", str(label))]
    if len(nums) >= 2 and nums[1] >= nums[0]:
        return nums[1] - nums[0] + 1
    return 1

def _parse_date(s, year):
    """'7월 19일 (토)' / '26.08.02 (토요일)' / '2026-08-02 (토)' → (y,m,d,요일문자) 또는 None."""
    t = str(s)
    wd = None
    m = re.search(r"\(([월화수목금토일])요?일?\)", t)
    if m:
        wd = m.group(1)
    m = re.search(r"(\d{2,4})[.\-/](\d{1,2})[.\-/](\d{1,2})", t)
    if m:
        y = int(m.group(1)); y = y + 2000 if y < 100 else y
        return y, int(m.group(2)), int(m.group(3)), wd
    m = re.search(r"(\d{1,2})월\s*(\d{1,2})일", t)
    if m:
        return year, int(m.group(1)), int(m.group(2)), wd
    return None

def check_content(spec, boxes, year=2026):
    """R5 존재성 · R6 수치 정합 · R7 날짜-요일. spec 키: title/date/buyin/gtd(+time),
    prizes=[(라벨,금액)...], blinds=[(sb,bb)...], year. 없는 키는 해당 검사 생략."""
    v = []
    rendered = _norm("".join(b["t"] for b in boxes))
    # R5 EXIST — 필수 값이 실재하고 placeholder가 아니며 렌더에 나타나는지
    for key in ("title", "date", "buyin", "gtd", "time"):
        if key not in spec:
            continue
        val = spec.get(key)
        if val is None or _norm(val) in {_norm(p) for p in PLACEHOLDERS}:
            v.append(f"R5 EXIST   '{key}' 값이 비었거나 placeholder: {val!r}")
            continue
        if _norm(val) not in rendered:
            v.append(f"R5 EXIST   '{key}'={str(val)[:26]!r} 가 렌더에 나타나지 않음")
    # R6 MATH — 분배 합은 개런티 미달 금지(개런티=최소 보장), 블라인드 단조 증가
    gtd = parse_money(spec.get("gtd"))
    prizes = spec.get("prizes")
    if gtd and prizes:
        s = 0
        for label, amt in prizes:
            a = parse_money(amt)
            if a is None:
                v.append(f"R6 MATH    상금 파싱 실패: {label!r}={amt!r}")
                s = None; break
            s += a * _range_count(label)
        if s is not None and s < gtd:
            v.append(f"R6 MATH    분배 합 {s:,} < 개런티 {gtd:,} — 보장 미달(허위 광고)")
    blinds = spec.get("blinds")
    if blinds:
        prev = None
        for i, (sb, bb) in enumerate(blinds, 1):
            sb, bb = parse_money(sb), parse_money(bb)
            if sb is None or bb is None or bb < sb:
                v.append(f"R6 MATH    LV{i} 블라인드 이상: {blinds[i-1]!r}")
                continue
            if prev and (sb < prev[0] or bb < prev[1]):
                v.append(f"R6 MATH    LV{i} 블라인드 역행: {prev} → {(sb, bb)}")
            prev = (sb, bb)
    # R7 DATE — 표기된 요일이 실제 달력과 일치
    if spec.get("date"):
        p = _parse_date(spec["date"], spec.get("year", year))
        if p and p[3]:
            import datetime
            try:
                actual = _WEEKDAYS[datetime.date(p[0], p[1], p[2]).weekday()]
                if actual != p[3]:
                    v.append(f"R7 DATE    {spec['date']!r} — 실제 요일은 ({actual})")
            except ValueError:
                v.append(f"R7 DATE    존재하지 않는 날짜: {spec['date']!r}")
    return v

def run(name, W, H, fn, spec=None):
    """렌더 검증(R1~R4) + spec이 있으면 콘텐츠 정합(R5~R7)까지."""
    global CANVAS
    CANVAS = (W, H)
    BOXES.clear()
    PANELS.clear()
    fn()
    snap = list(BOXES)
    v = check(snap, W, H)
    if spec:
        v += check_content(spec, snap)
    print(f"[QC] {name}: " + ("PASS ✅" if not v else f"FAIL ❌ {len(v)}건"))
    for x in v[:20]:
        print("     -", x)
    return v
