#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex QC 레이어 — 까다로운 규격 검증 리뷰어.

렌더 중 그려지는 모든 텍스트(직접 draw + 텍스트 이미지 합성)의 바운딩박스를
자동 기록하고, 다음 위반을 검출한다:
  R1 CANVAS  : 캔버스 이탈
  R2 SAFE    : 세이프존(좌우 6% / 상하 3%) 침범
  R3 OVERLAP : 텍스트 상호 겹침 (양축 3px 초과 침투)

위반이 하나라도 있으면 FAIL — 해당 산출물은 출고 금지.

사용:
    import qc
    rp, EA, EB, EC = qc.load()          # 계측 패치 후 렌더러 로드 (이 순서 필수)
    qc.run("이름", W, H, lambda: EA.render(...))
"""
from PIL import Image, ImageDraw

BOXES = []
ENABLED = True
CANVAS = None      # run()이 지정한 메인 캔버스 크기 — 이 크기의 이미지에 그린 것만 기록
                   # (text_img/vtext의 내부 스크래치 캔버스 드로잉을 제외하기 위함)

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
            b = self.textbbox(xy, str(text), font=kw.get("font"), anchor=kw.get("anchor"))
            BOXES.append({"k": "text", "t": str(text)[:26], "b": [float(v) for v in b]})
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
                            float(dest[0] + im.width), float(dest[1] + im.height)]})
    return _orig_ac(self, im, dest, *args, **kw)
Image.Image.alpha_composite = _pac

def load():
    """text_img/vtext 산출물에 qc_text 마킹을 심은 뒤 렌더러들을 로드한다."""
    import render_poster as rp
    _oti = rp.text_img
    def ti(t, f, top, bottom=None, pad=10):
        out, w, h = _oti(t, f, top, bottom, pad)
        out.qc_text = str(t)[:26]
        return out, w, h
    rp.text_img = ti
    import render_editorial as EA
    _ovt = EA.vtext
    def vt(text, font, fill, ls=3):
        out = _ovt(text, font, fill, ls)
        out.qc_text = "|" + str(text)[:24]
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
                a["t"] = (a["t"] + c["t"])[:26]
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

def check(boxes, W, H, tol=1.5, depth=3.0):
    sl, st = round(W * 0.06), round(H * 0.03)
    sr, sb = W - sl, H - st
    bs = _merge_runs(boxes)
    v = []
    for x in bs:
        b = x["b"]
        if b[0] < -tol or b[1] < -tol or b[2] > W + tol or b[3] > H + tol:
            v.append(f"R1 CANVAS  '{x['t']}' box={list(map(round, b))}")
        elif b[0] < sl - tol or b[2] > sr + tol or b[1] < st - tol or b[3] > sb + tol:
            v.append(f"R2 SAFE    '{x['t']}' box={list(map(round, b))} safe=[{sl},{st},{sr},{sb}]")
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, c = bs[i]["b"], bs[j]["b"]
            if _iou(a, c) > 0.8:            # 동일 요소 중복 드로우(섀도 등)
                continue
            iw = min(a[2], c[2]) - max(a[0], c[0])
            ih = min(a[3], c[3]) - max(a[1], c[1])
            if iw > depth and ih > depth:
                v.append(f"R3 OVERLAP '{bs[i]['t']}' × '{bs[j]['t']}' depth=({round(iw)},{round(ih)})")
    return v

def run(name, W, H, fn):
    global CANVAS
    CANVAS = (W, H)
    BOXES.clear()
    fn()
    snap = list(BOXES)
    v = check(snap, W, H)
    print(f"[QC] {name}: " + ("PASS ✅" if not v else f"FAIL ❌ {len(v)}건"))
    for x in v[:20]:
        print("     -", x)
    return v
