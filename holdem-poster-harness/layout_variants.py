#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B형(스트럭처+상금표) 레이아웃 변형 5종 — 상금/블라인드 배치 리서치 구현.
  V1 CLASSIC  : 좌 프라이즈 / 우 블라인드 2그룹 (기본 — render_editorial_b 재사용)
  V2 PODIUM   : 상단 Top3 포디움 + 나머지 상금 칩 그리드 + 하단 풀폭 블라인드 3그룹
  V3 FLANK    : 중앙 대칭 히어로 + 중앙 프라이즈 컬럼 + 좌/우 블라인드 플랭킹
  V4 SIDEBAR  : 좌 대형 블라인드 2그룹 + 우측 정보 사이드바(스탯/바이인/상금 축약)
  V5 SHOWCASE : 히어로+인포카드 중심 + Top5 상금 칩 + 하단 콤팩트 블라인드 3그룹
"""
import math, os, sys
from PIL import Image, ImageDraw
from render_poster import (noto, measure, fit_font, fit_common, draw_ls, lsw,
                           text_img, theight, theme_palette, ASSET)
from render_editorial import bebas, oswald, grade, frost, vtext, rect_blend, metalize

W, H = 1080, 1900
ML, MR, SAFE_B = 80, W - 72, H - 60
CX = W // 2
GOLD = (244, 206, 120)

def split_rows(lv, n):
    k = math.ceil(len(lv) / n)
    return [lv[i * k:(i + 1) * k] for i in range(n)]

def base(theme, acc):
    p = f"{ASSET}bg/{theme}.jpg"
    bg = Image.open(p).convert("RGB").resize((W, H)).convert("RGBA") if os.path.exists(p) \
        else Image.new("RGBA", (W, H), (16, 12, 30, 255))
    return grade(bg, acc, leak_xy=(0.85, 0.10))

def topbar(d, data, hi, lo, soft):
    mark = data.get("logo_mark", "RF")
    d.text((ML, 78), mark, font=bebas(40), fill=hi, anchor="lm")
    mw0 = measure(mark, bebas(40))[0]
    draw_ls(d, (ML + mw0 + 26, 78), data.get("logo_word", "HOLDEM CLUB"), oswald(15, 600), lo, ls=3, anchor="lm")
    draw_ls(d, (MR, 64), data["series"], oswald(20, 700), hi, ls=4, anchor="ra")
    d.text((MR, 92), data["total"], font=bebas(30), fill=GOLD, anchor="ra")
    draw_ls(d, (MR, 122), "TOTAL GUARANTEED", oswald(12, 500), soft, ls=3, anchor="ra")

def hero_left(img, d, data, acc, soft, hi, lo, tw_max, m_max, right_block=True):
    ky = 168
    d.line([(ML, ky), (ML + 44, ky)], fill=acc, width=3)
    draw_ls(d, (ML + 56, ky), data.get("kicker", "MAIN EVENT"), oswald(15, 600), acc, ls=5, anchor="lm")
    ty = 192
    tf, _ = fit_font(data["title"], lambda s: bebas(s), tw_max, 92, 60)
    d.text((ML, ty), data["title"], font=tf, fill=hi, anchor="la")
    th = theight(data["title"], tf)
    if right_block:
        draw_ls(d, (MR, ty + 8), data["brand"], oswald(26, 700), hi, ls=2, anchor="ra")
        d.text((MR, ty + 42), "★ ★ ★ ★", font=noto(15, 700), fill=GOLD, anchor="ra")
        draw_ls(d, (MR, ty + 70), data["date"], oswald(17, 500), soft, ls=1, anchor="ra")
    gy = ty + max(th + 16, 120)
    draw_ls(d, (ML + 2, gy), "GUARANTEED PRIZE POOL", oswald(17, 600), lo, ls=5, anchor="la")
    my = gy + theight("GUARANTEED PRIZE POOL", oswald(17, 600)) + 8
    mf, _ = fit_font(data["gtd"], lambda s: bebas(s), m_max, 150, 90)
    TH = theme_palette(data["theme"])
    mi, mw, mh = text_img(data["gtd"], mf, (255, 255, 255), TH["gtd_lo"])
    mi = metalize(mi, TH["gtd_lo"])
    img.alpha_composite(mi, (ML, int(my)))
    d.text((ML + mw + 16, my + mh * 0.5), "GTD", font=oswald(36, 700), fill=GOLD, anchor="lm")
    yb = my + mh + 18
    d.line([(ML, yb), (MR, yb)], fill=(255, 255, 255, 44), width=1)
    d.line([(ML, yb), (ML + 90, yb)], fill=acc, width=3)
    return yb

def hero_center(img, d, data, acc, soft, hi, lo):
    ky = 164
    kw = lsw(data.get("kicker", "MAIN EVENT"), oswald(15, 600), 5)
    d.line([(CX - kw / 2 - 58, ky), (CX - kw / 2 - 14, ky)], fill=acc, width=3)
    d.line([(CX + kw / 2 + 14, ky), (CX + kw / 2 + 58, ky)], fill=acc, width=3)
    draw_ls(d, (CX, ky - 10), data.get("kicker", "MAIN EVENT"), oswald(15, 600), acc, ls=5, anchor="ma")
    ty = 196
    tf, _ = fit_font(data["title"], lambda s: bebas(s), MR - ML - 160, 96, 60)
    d.text((CX, ty), data["title"], font=tf, fill=hi, anchor="ma")
    th = theight(data["title"], tf)
    dy = ty + th + 14
    draw_ls(d, (CX, dy), f'{data["date"]}   ·   {data["brand"]}', oswald(17, 500), soft, ls=1, anchor="ma")
    gy = dy + 40
    draw_ls(d, (CX, gy), "GUARANTEED PRIZE POOL", oswald(17, 600), lo, ls=5, anchor="ma")
    my = gy + theight("GUARANTEED PRIZE POOL", oswald(17, 600)) + 8
    mf, _ = fit_font(data["gtd"], lambda s: bebas(s), MR - ML - 220, 150, 90)
    TH = theme_palette(data["theme"])
    mi, mw, mh = text_img(data["gtd"], mf, (255, 255, 255), TH["gtd_lo"])
    mi = metalize(mi, TH["gtd_lo"])
    tot = mw + 16 + measure("GTD", oswald(36, 700))[0]
    x0 = CX - tot / 2
    img.alpha_composite(mi, (int(x0), int(my)))
    d.text((x0 + mw + 16, my + mh * 0.5), "GTD", font=oswald(36, 700), fill=GOLD, anchor="lm")
    yb = my + mh + 18
    d.line([(ML, yb), (MR, yb)], fill=(255, 255, 255, 44), width=1)
    d.line([(CX - 45, yb), (CX + 45, yb)], fill=acc, width=3)
    return yb

def buyin_row(img, d, y, data, acc, hi, center=False):
    bh = 56
    frost(img, (ML, y, MR, y + bh), 12, acc, tab=False)
    ccy = y + bh / 2
    chip_f = oswald(12, 700)
    chw = int(lsw("BUY-IN", chip_f, 3)) + 32
    bvf, _ = fit_font(data["buyin"], lambda s: noto(s, 800), MR - ML - chw - 100, 27, 21)
    if center:
        tot = chw + 24 + measure(data["buyin"], bvf)[0]
        x0 = CX - tot / 2
    else:
        x0 = ML + 16
    rect_blend(img, [x0, ccy - 14, x0 + chw, ccy + 14], (acc[0], acc[1], acc[2], 235), radius=14)
    draw_ls(d, (x0 + chw / 2, ccy), "BUY-IN", chip_f, (18, 12, 32), ls=3, anchor="mm")
    d.text((x0 + chw + 24, ccy), data["buyin"], font=bvf, fill=hi, anchor="lm")
    return y + bh

def stats_strip(img, d, y, data, acc, soft, hi, x0=None, x1=None):
    x0 = ML if x0 is None else x0; x1 = MR if x1 is None else x1
    sh = 96
    frost(img, (x0, y, x1, y + sh), 14, acc, tab=False)
    st = data["stats"]; n = len(st); cw = (x1 - x0) / n
    lab_f, _ = fit_common([(lab, cw - 20) for lab, _ in st], lambda s: oswald(s, 600), 15, 9)
    val_f, _ = fit_common([(val, cw - 20) for _, val in st], lambda s: noto(s, 800), 30, 14)
    for i, (lab, val) in enumerate(st):
        sx = x0 + cw * (i + 0.5)
        if i: d.line([(x0 + cw * i, y + 18), (x0 + cw * i, y + sh - 18)], fill=(255, 255, 255, 30), width=1)
        draw_ls(d, (sx, y + 20), lab, lab_f, soft, ls=1, anchor="ma")
        d.text((sx, y + 48), val, font=val_f, fill=hi, anchor="ma")
    return y + sh

def blind_cf(lv, gw, extra=None):
    prop = [0.13, 0.215, 0.215, 0.20, 0.24]
    items = [(v, gw * prop[i] - 4) for r in lv if r[0] != "BRK" for i, v in enumerate(r)]
    items += [(r[1], gw - 12) for r in lv if r[0] == "BRK"]
    if extra: items += extra
    f, _ = fit_common(items, lambda s: oswald(s, 600), 14, 9)
    return f

def blind_block(img, d, x0, gw, y0, rows, rh, acc, soft, hi, cf):
    prop = [0.13, 0.215, 0.215, 0.20, 0.24]; cols = ["LV", "SB", "BB", "ANTE", "BLIND"]
    cen = []; a = 0
    for p in prop: cen.append(x0 + (a + p / 2) * gw); a += p
    y = y0
    d.rounded_rectangle([x0, y, x0 + gw, y + rh], radius=5, fill=acc + (235,))
    hf, _ = fit_common([(c, gw * prop[i] - 4) for i, c in enumerate(cols)], lambda s: oswald(s, 700), 13, 8)
    for c, cx in zip(cols, cen): d.text((cx, y + rh / 2), c, font=hf, fill=(18, 12, 30), anchor="mm")
    y += rh + 1; zi = 0
    for r in rows:
        if r[0] == "BRK":
            rect_blend(img, [x0, y, x0 + gw, y + rh], (acc[0], acc[1], acc[2], 95))
            d.text((x0 + gw / 2, y + rh / 2), r[1], font=cf, fill=hi, anchor="mm")
        else:
            if zi % 2 == 0: rect_blend(img, [x0, y, x0 + gw, y + rh], (255, 255, 255, 14))
            for i, (v, cx) in enumerate(zip(r, cen)):
                d.text((cx, y + rh / 2), v, font=cf, fill=GOLD if i == 0 else soft, anchor="mm")
            zi += 1
        y += rh
    return y

def notice_footer(img, d, ny, data, acc, lo, hi):
    nt = vtext("NOTICE", oswald(14, 700), lo + (200,), ls=4); img.alpha_composite(nt, (ML - 6, ny))
    nx = ML + 30; colw = (MR - nx) / 2; lh = 26; half = (len(data["notice"]) + 1) // 2
    nf, _ = fit_common([("· " + l, colw - 20) for l in data["notice"]], lambda s: noto(s, 400), 14, 11)
    for ci, chunk in enumerate([data["notice"][:half], data["notice"][half:]]):
        bx2 = nx + ci * colw; yc = ny
        for line in chunk:
            d.text((bx2, yc), "·", font=nf, fill=acc, anchor="la")
            d.text((bx2 + 14, yc), line, font=nf, fill=lo, anchor="la"); yc += lh
    spy = SAFE_B - 44
    d.line([(ML, spy - 14), (MR, spy - 14)], fill=(255, 255, 255, 32), width=1)
    sx = ML
    for lab, name in data["sponsors"][:3]:
        if sx > MR - 460: break
        draw_ls(d, (sx, spy), lab, noto(12, 600), acc, ls=1, anchor="la")
        d.text((sx, spy + 18), name, font=noto(15, 700), fill=hi, anchor="la")
        sx += measure(name, noto(15, 700))[0] + 40
    d.text((MR, spy), data["venue_name"], font=noto(15, 700), fill=hi, anchor="ra")
    d.text((MR, spy + 20), data["venue_addr"], font=noto(15, 400), fill=lo, anchor="ra")

# ================= V2 PODIUM =================
def render_v2(data, lv, out):
    TH = theme_palette(data["theme"])
    acc, soft, hi, lo = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"]
    img = base(data["theme"], acc); d = ImageDraw.Draw(img, "RGBA")
    topbar(d, data, hi, lo, soft)
    yb = hero_left(img, d, data, acc, soft, hi, lo, MR - ML - 360, MR - ML - 150)
    y = buyin_row(img, d, yb + 16, data, acc, hi)
    y = stats_strip(img, d, y + 14, data, acc, soft, hi)
    # ---- 상금 포디움 (2nd | 1st | 3rd) ----
    py0 = y + 26
    order = [(1, 168, "2ND"), (0, 200, "1ST"), (2, 152, "3RD")]
    cw_, gap = 286, 18
    total = cw_ * 3 + gap * 2; x0 = CX - total / 2
    amt_f, _ = fit_common([(data["prizes"][i][1], cw_ - 36) for i, _, _ in order], lambda s: oswald(s, 700), 30, 18)
    base_y = py0 + 210
    for k, (idx, ch, lab) in enumerate(order):
        cx0 = x0 + k * (cw_ + gap); cy0 = base_y - ch
        frost(img, (cx0, cy0, cx0 + cw_, base_y), 14, acc, tab=False)
        d.line([(cx0 + 18, cy0), (cx0 + 92, cy0)], fill=(GOLD if idx == 0 else acc) + (255,), width=3)
        draw_ls(d, (cx0 + cw_ / 2, cy0 + 16), lab + " PLACE", oswald(13, 700),
                GOLD if idx == 0 else soft, ls=3, anchor="ma")
        d.text((cx0 + cw_ / 2, cy0 + ch / 2 + 16), data["prizes"][idx][1], font=amt_f,
               fill=GOLD if idx == 0 else hi, anchor="mm")
    # 나머지 상금 칩 그리드 (3행 × 6열)
    rest = data["prizes"][3:]
    gy0 = base_y + 16
    ncol = 6; cw2 = (MR - ML - (ncol - 1) * 8) / ncol
    chip_f, _ = fit_common([(f'{rk} {pz}', cw2 - 14) for rk, pz in rest], lambda s: noto(s, 600), 13, 9)
    for i, (rk, pz) in enumerate(rest):
        r_, c_ = divmod(i, ncol)
        cx0 = ML + c_ * (cw2 + 8); cy0 = gy0 + r_ * 34
        rect_blend(img, [cx0, cy0, cx0 + cw2, cy0 + 28], (255, 255, 255, 16), radius=8)
        d.text((cx0 + cw2 / 2, cy0 + 14), f'{rk} {pz}', font=chip_f, fill=soft, anchor="mm")
    rows_used = math.ceil(len(rest) / ncol)
    # ---- 하단 풀폭 블라인드 3그룹 ----
    by0 = gy0 + rows_used * 34 + 22; by1 = 1608
    frost(img, (ML, by0, MR, by1), 16, acc)
    inx0, inx1 = ML + 18, MR - 18
    ng = 3; gw = (inx1 - inx0 - (ng - 1) * 14) / ng
    chunks = split_rows(lv, ng)
    cf = blind_cf(lv, gw)
    rh = min(32, (by1 - by0 - 36) / (max(len(c) for c in chunks) + 1))
    for gi, ch_ in enumerate(chunks):
        blind_block(img, d, inx0 + gi * (gw + 14), gw, by0 + 18, ch_, rh, acc, soft, hi, cf)
    notice_footer(img, d, by1 + 22, data, acc, lo, hi)
    img.convert("RGB").save(out, quality=95); print("saved", out)

# ================= V3 FLANK =================
def render_v3(data, lv, out):
    TH = theme_palette(data["theme"])
    acc, soft, hi, lo = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"]
    img = base(data["theme"], acc); d = ImageDraw.Draw(img, "RGBA")
    topbar(d, data, hi, lo, soft)
    yb = hero_center(img, d, data, acc, soft, hi, lo)
    y = buyin_row(img, d, yb + 16, data, acc, hi, center=True)
    y = stats_strip(img, d, y + 14, data, acc, soft, hi)
    # ---- 좌 블라인드 | 중앙 프라이즈 | 우 블라인드 ----
    by0 = y + 24; by1 = 1608
    gw = 296; pw = (MR - ML) - gw * 2 - 32
    lx, cx0, rx = ML, ML + gw + 16, MR - gw
    frost(img, (lx, by0, lx + gw, by1), 16, acc)
    frost(img, (cx0, by0, cx0 + pw, by1), 16, acc, tab=False)
    frost(img, (rx, by0, rx + gw, by1), 16, acc)
    chunks = split_rows(lv, 2)
    cf = blind_cf(lv, gw - 24, extra=[(rk, pw * 0.52 - 20) for rk, _ in data["prizes"]] +
                                     [(pz, pw * 0.46 - 20) for _, pz in data["prizes"]])
    rh = min(33, (by1 - by0 - 36) / (max(len(c) for c in chunks) + 1))
    blind_block(img, d, lx + 12, gw - 24, by0 + 18, chunks[0], rh, acc, soft, hi, cf)
    blind_block(img, d, rx + 12, gw - 24, by0 + 18, chunks[1], rh, acc, soft, hi, cf)
    # 중앙 프라이즈
    draw_ls(d, (cx0 + pw / 2, by0 + 20), "PRIZE POOL", oswald(13, 700), acc, ls=4, anchor="ma")
    py = by0 + 52; prh = (by1 - py - 16) / len(data["prizes"])
    pf_big = oswald(cf.size, 700); pf_reg = oswald(cf.size, 500)
    for i, (rk, pz) in enumerate(data["prizes"]):
        yy = py + prh * i
        if i % 2 == 0: rect_blend(img, [cx0 + 10, yy, cx0 + pw - 10, yy + prh], (255, 255, 255, 16))
        big = i < 3
        d.text((cx0 + 22, yy + prh / 2), rk, font=pf_big if big else pf_reg,
               fill=GOLD if big else hi, anchor="lm")
        d.text((cx0 + pw - 22, yy + prh / 2), pz, font=pf_big if big else pf_reg,
               fill=GOLD if big else soft, anchor="rm")
    notice_footer(img, d, by1 + 22, data, acc, lo, hi)
    img.convert("RGB").save(out, quality=95); print("saved", out)

# ================= V4 SIDEBAR =================
def render_v4(data, lv, out):
    TH = theme_palette(data["theme"])
    acc, soft, hi, lo = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"]
    img = base(data["theme"], acc); d = ImageDraw.Draw(img, "RGBA")
    topbar(d, data, hi, lo, soft)
    LX1 = ML + 600                     # 좌 영역 끝
    SB0 = LX1 + 24                     # 사이드바 시작
    yb = hero_left(img, d, data, acc, soft, hi, lo, 540, 430, right_block=False)  # GTD 접미까지 좌영역(600px) 안에
    # 좌: 블라인드 2그룹 (대형)
    by0 = yb + 20; by1 = 1608
    frost(img, (ML, by0, LX1, by1), 16, acc)
    gw = (LX1 - ML - 36 - 14) / 2
    chunks = split_rows(lv, 2)
    cf = blind_cf(lv, gw, extra=[(rk, 150) for rk, _ in data["prizes"]] + [(pz, 130) for _, pz in data["prizes"]])
    rh = min(34, (by1 - by0 - 36) / (max(len(c) for c in chunks) + 1))
    blind_block(img, d, ML + 18, gw, by0 + 18, chunks[0], rh, acc, soft, hi, cf)
    blind_block(img, d, ML + 18 + gw + 14, gw, by0 + 18, chunks[1], rh, acc, soft, hi, cf)
    # 우: 정보 사이드바
    sy0 = 160; sy1 = 1608
    frost(img, (SB0, sy0, MR, sy1), 16, acc)
    inx = SB0 + 24; inw = MR - 24 - inx
    d2y = sy0 + 26
    draw_ls(d, (inx, d2y), data["brand"], oswald(20, 700), hi, ls=1, anchor="la")
    d.text((inx, d2y + 30), data["date"], font=oswald(15, 500), fill=soft, anchor="la")
    d.line([(inx, d2y + 62), (MR - 24, d2y + 62)], fill=(255, 255, 255, 30), width=1)
    ky = d2y + 78
    kvf, _ = fit_common([(v, inw) for _, v in data["stats"]] + [(data["buyin"], inw)],
                        lambda s: noto(s, 800), 24, 13)
    # BUY-IN을 먼저(블라인드 표 헤더 행과 수평선이 겹치지 않도록 배치 순서 조정)
    draw_ls(d, (inx, ky), "BUY-IN", oswald(13, 600), acc, ls=2, anchor="la")
    d.text((inx, ky + 20), data["buyin"], font=kvf, fill=hi, anchor="la")
    ky += 66
    for lab, val in data["stats"]:
        draw_ls(d, (inx, ky), lab, oswald(13, 600), acc, ls=2, anchor="la")
        d.text((inx, ky + 20), val, font=kvf, fill=hi, anchor="la")
        ky += 64
    d.line([(inx, ky), (MR - 24, ky)], fill=(255, 255, 255, 30), width=1)
    draw_ls(d, (inx, ky + 14), "PRIZE POOL", oswald(13, 700), acc, ls=3, anchor="la")
    py = ky + 44; prh = (sy1 - py - 16) / len(data["prizes"])
    pf_big = oswald(cf.size, 700); pf_reg = oswald(cf.size, 500)
    for i, (rk, pz) in enumerate(data["prizes"]):
        yy = py + prh * i
        if i % 2 == 0: rect_blend(img, [SB0 + 10, yy, MR - 10, yy + prh], (255, 255, 255, 16))
        big = i < 3
        d.text((inx, yy + prh / 2), rk, font=pf_big if big else pf_reg, fill=GOLD if big else hi, anchor="lm")
        d.text((MR - 24, yy + prh / 2), pz, font=pf_big if big else pf_reg, fill=GOLD if big else soft, anchor="rm")
    notice_footer(img, d, by1 + 22, data, acc, lo, hi)
    img.convert("RGB").save(out, quality=95); print("saved", out)

# ================= V5 SHOWCASE =================
def render_v5(data, lv, out):
    TH = theme_palette(data["theme"])
    acc, soft, hi, lo = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"]
    img = base(data["theme"], acc); d = ImageDraw.Draw(img, "RGBA")
    topbar(d, data, hi, lo, soft)
    yb = hero_left(img, d, data, acc, soft, hi, lo, MR - ML - 360, MR - ML - 120)
    # 인포 카드 (DATE/VENUE/BUY-IN + 스탯)
    cy0 = yb + 18; cy1 = cy0 + 320
    frost(img, (ML, cy0, MR, cy1), 18, acc)
    pad = 36; bx = ML + (MR - ML) * 0.56
    kvf, _ = fit_common([(data["date"], 400), (data["venue_name"], 400),
                         (data["buyin"], MR - pad - bx)], lambda s: noto(s, 800), 30, 17)
    def kv(x, y, k, v):
        draw_ls(d, (x, y), k, oswald(14, 600), acc, ls=3, anchor="la")
        d.text((x, y + 20), v, font=kvf, fill=hi, anchor="la")
    kv(ML + pad, cy0 + 28, "DATE", data["date"])
    kv(ML + pad, cy0 + 98, "VENUE", data["venue_name"])
    kv(bx, cy0 + 28, "BUY-IN", data["buyin"])
    midy = cy0 + 178
    d.line([(ML + pad, midy), (MR - pad, midy)], fill=(255, 255, 255, 30), width=1)
    st = data["stats"]; n = len(st); cw = (MR - ML - pad * 2) / n
    slab, _ = fit_common([(lab, cw - 18) for lab, _ in st], lambda s: oswald(s, 600), 14, 9)
    sval, _ = fit_common([(val, cw - 18) for _, val in st], lambda s: noto(s, 800), 27, 14)
    for i, (lab, val) in enumerate(st):
        sx = ML + pad + cw * i
        if i: d.line([(sx, midy + 20), (sx, cy1 - 26)], fill=(255, 255, 255, 26), width=1)
        draw_ls(d, (sx + 12, midy + 24), lab, slab, soft, ls=1, anchor="la")
        d.text((sx + 12, midy + 48), val, font=sval, fill=hi, anchor="la")
    # Top5 상금 칩
    ty0 = cy1 + 22
    draw_ls(d, (ML, ty0), "TOP PRIZES", oswald(14, 700), acc, ls=3, anchor="la")
    chips = data["prizes"][:5]
    ncol = 5; cw2 = (MR - ML - (ncol - 1) * 10) / ncol
    cf5, _ = fit_common([(f'{rk}  {pz}', cw2 - 16) for rk, pz in chips], lambda s: noto(s, 700), 15, 10)
    for i, (rk, pz) in enumerate(chips):
        cx0 = ML + i * (cw2 + 10); yy = ty0 + 26
        rect_blend(img, [cx0, yy, cx0 + cw2, yy + 40], (255, 255, 255, 18), radius=10)
        if i == 0: rect_blend(img, [cx0, yy, cx0 + cw2, yy + 40], (GOLD[0], GOLD[1], GOLD[2], 40), radius=10)
        d.text((cx0 + cw2 / 2, yy + 20), f'{rk}  {pz}', font=cf5, fill=GOLD if i == 0 else hi, anchor="mm")
    dotl = ty0 + 78
    d.text((ML, dotl), f'… {data["prizes"][5][0].split("~")[0]}부터 {data["prizes"][-1][0]}까지 총 {len(data["prizes"])}구간 지급 · 상세 상금표는 매장 공지 참조',
           font=noto(13, 400), fill=lo, anchor="la")
    # 하단 콤팩트 블라인드 3그룹
    by0 = dotl + 30; by1 = 1608
    frost(img, (ML, by0, MR, by1), 16, acc)
    inx0, inx1 = ML + 18, MR - 18
    ng = 3; gw = (inx1 - inx0 - (ng - 1) * 14) / ng
    chunks = split_rows(lv, ng)
    cf = blind_cf(lv, gw)
    rh = min(32, (by1 - by0 - 36) / (max(len(c) for c in chunks) + 1))
    for gi, ch_ in enumerate(chunks):
        blind_block(img, d, inx0 + gi * (gw + 14), gw, by0 + 18, ch_, rh, acc, soft, hi, cf)
    notice_footer(img, d, by1 + 22, data, acc, lo, hi)
    img.convert("RGB").save(out, quality=95); print("saved", out)
