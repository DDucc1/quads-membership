#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
craft_lab — 레퍼런스 학습(learn/)에서 증류된 패턴의 실험 스테이징.
learn/distilled.md 상태 보드와 1:1. 검증(실습 2회+긍정 피드백) 후 정식 렌더러로 졸업.

패턴: P1 neon_text · P2 ghost_title · P3 flare · P4 header_bar/zebra/break_band · P5 단위 축소 · P12 sparkle
규약: 장식(고스트/플레어/스파클)은 스크래치 레이어 합성 → QC 비추적.
      본문 텍스트는 qc_text 마킹 또는 캔버스 직접 드로잉 → QC 추적 유지.
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
from render_editorial import bebas, rect_blend

ASSET = "assets/"


def _ls_draw(d, x, y, text, f, fill, ls, anchor_y="ls"):
    """자간 드로잉(문자 단위). x 시작 기준, 전체 폭 반환."""
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=f, fill=fill, anchor="l" + anchor_y[-1])
        cx += f.getlength(ch) + ls
    return cx - ls - x


def _ls_width(text, f, ls):
    return sum(f.getlength(c) for c in text) + ls * (len(text) - 1)


def ghost_title(img, text, size, color, alpha=48, ls=14, crop=0.42):
    """P2/T1 고스트 타이틀 — 초대형 저불투명, 캔버스 상단에서 잘림. 장식(비추적)."""
    W = img.width
    f = bebas(size)
    tw = _ls_width(text, f, ls)
    pad = 40
    sc = Image.new("RGBA", (max(int(tw) + pad * 2, W), size + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(sc)
    _ls_draw(d, pad, pad, text, f, color + (alpha,), ls, anchor_y="la")
    # 상단 crop 비율만큼 위로 올려 붙임 (글자 위쪽이 캔버스 밖)
    off_y = -int(size * crop)
    off_x = (W - sc.width) // 2
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(sc, (off_x, off_y))     # 빈 레이어에 마스크 없이 — 알파 이중 감쇠 방지
    img.alpha_composite(layer)          # qc_text 없음 → 비추적(장식)


def neon_text(img, cx, y, text, size, accent, unit=None, unit_ratio=0.52,
              core=(255, 255, 255), track=True):
    """P1/L1 네온 글로우 — 코어 백색 + 액센트 halo 2겹. P5/T5: unit 접미 축소.
    y = 베이스라인. 본문 텍스트이므로 qc_text 마킹(추적)."""
    f1 = bebas(size)
    f2 = bebas(int(size * unit_ratio)) if unit else None
    w1 = f1.getlength(text)
    w2 = (f2.getlength(unit) + int(size * 0.06)) if unit else 0
    tw = w1 + w2
    pad = int(size * 0.55)
    a1 = f1.getbbox("8")[3]
    sc = Image.new("RGBA", (int(tw) + pad * 2, size + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(sc)
    base = pad + a1

    def put(fill):
        d.text((pad, base), text, font=f1, fill=fill, anchor="ls")
        if unit:
            d.text((pad + w1 + int(size * 0.06), base), unit, font=f2, fill=fill, anchor="ls")

    put(accent + (255,))                                    # 외측 halo — 넓고 옅게
    halo = sc.filter(ImageFilter.GaussianBlur(size * 0.11))
    halo = Image.alpha_composite(halo, halo)                # 2패스 — 발광 강화
    put(accent + (255,))                                    # 내측 halo — 진하게
    inner = sc.filter(ImageFilter.GaussianBlur(size * 0.030))
    inner = Image.alpha_composite(inner, inner)
    halo = Image.alpha_composite(halo, inner)
    img.alpha_composite(halo, (int(cx - tw / 2 - pad), int(y - base)))   # 장식층 — 비추적
    tight = int(size * 0.06)                                # 코어층 — 본문(추적), 타이트 박스
    sc2 = Image.new("RGBA", (int(tw) + tight * 2, a1 + tight * 2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(sc2)
    d2.text((tight, tight + a1), text, font=f1, fill=core + (255,), anchor="ls")
    if unit:
        d2.text((tight + w1 + int(size * 0.06), tight + a1), unit, font=f2,
                fill=core + (255,), anchor="ls")
    if track:
        sc2.qc_text = text + (unit or "")
    img.alpha_composite(sc2, (int(cx - tw / 2 - tight), int(y - a1 - tight)))
    return int(tw)


def flare(img, cx, y, w, accent, core=(255, 255, 255)):
    """P3/L2 호라이즌 플레어 — 중앙 밝고 양끝 소멸하는 수평 광선. 장식(비추적)."""
    h = max(34, int(w * 0.075))
    xs = np.linspace(-1, 1, w)[None, :]
    ys = np.linspace(-1, 1, h)[:, None]
    fall = np.clip(1 - np.abs(xs), 0, 1) ** 1.6 * np.clip(1 - np.abs(ys), 0, 1) ** 2.6
    glow = (fall * 235).astype(np.uint8)                    # 액센트 글로우
    corew = (np.clip(1 - np.abs(xs), 0, 1) ** 3.6 *
             np.clip(1 - np.abs(ys) * (h / 4.0), 0, 1) ** 1.5 * 255).astype(np.uint8)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = Image.new("RGBA", (w, h), accent + (0,)); g.putalpha(Image.fromarray(glow))
    c = Image.new("RGBA", (w, h), core + (0,));   c.putalpha(Image.fromarray(corew))
    layer.paste(g, (int(cx - w / 2), int(y - h / 2)))   # 마스크 없이 — 알파 보존
    layer.alpha_composite(c, (int(cx - w / 2), int(y - h / 2)))
    img.alpha_composite(layer)


def sparkle(img, cx, cy, r, color=(255, 255, 255), alpha=230):
    """P12/L3 십자성 — 4갈래 테이퍼 광점. 장식(비추적, 도형)."""
    sc = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(sc)
    ox, oy = r * 2, r * 2
    t = max(1.6, r * 0.13)
    for (dx, dy, ln) in [(1, 0, r), (-1, 0, r), (0, 1, r * 1.35), (0, -1, r * 1.35)]:
        d.polygon([(ox + dx * ln, oy + dy * ln),
                   (ox + dy * t, oy + dx * t), (ox - dy * t, oy - dx * t)],
                  fill=color + (alpha,))
    d.ellipse([ox - t, oy - t, ox + t, oy + t], fill=(255, 255, 255, 255))
    sc = sc.filter(ImageFilter.GaussianBlur(0.7))
    img.alpha_composite(sc, (int(cx - r * 2), int(cy - r * 2)))


def header_bar(img, d, x0, x1, y, h, text, accent, txt_col=(12, 10, 16), f=None):
    """P4/S1 헤더 반전 바 — 액센트 바탕 + 흑색 텍스트 + 좌우 노치. 텍스트는 추적됨."""
    notch = int(h * 0.42)
    d.rectangle([x0, y, x1, y + h], fill=accent)
    # 좌상/우하 노치(계단 컷)는 인접 배경색 삼각형으로 파낸다
    bgc = img.getpixel((max(0, x0 - 4), min(img.height - 1, y + h + 6)))[:3]
    d.polygon([(x0, y), (x0 + notch, y), (x0, y + notch)], fill=bgc)
    d.polygon([(x1, y + h), (x1 - notch, y + h), (x1, y + h - notch)], fill=bgc)
    ff = f or bebas(int(h * 0.62))
    ls = int(h * 0.10)
    tw = _ls_width(text, ff, ls)
    _ls_draw(d, (x0 + x1) / 2 - tw / 2, y + h / 2 + ff.getbbox("A")[3] / 2, text, ff,
             txt_col, ls)


def panel(box):
    """레이아웃 컬럼을 QC 패널로 등록 — 서로 다른 패널의 텍스트는 R4 크기 비교 제외.
    (frost 패널과 동일 개념 — 시각적으로 분리된 컨텍스트 선언)"""
    try:
        import qc
        if qc.ENABLED:
            qc.PANELS.append([float(v) for v in box])
    except ImportError:
        pass


def zebra_row(img, box, alpha=22):
    """P4/S2 저대비 지브라 행."""
    rect_blend(img, box, (255, 255, 255, alpha))


def break_band(img, box, accent, alpha=64):
    """P4/S3 브레이크 밴드 — 액센트 저채도 띠."""
    rect_blend(img, box, accent + (alpha,))
