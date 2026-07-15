#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""에디토리얼 크래프트 — B형(스트럭처 시트). 프로스티드 표 패널 + 거대 머니 + 새 타이포."""
import os, sys
from PIL import Image, ImageDraw
from render_poster import noto, measure, fit_font, fit_common, draw_ls, lsw, text_img, theight, theme_palette, ASSET
from render_editorial import bebas, oswald, grade, frost, vtext, spade, rect_blend
import render_poster_b as B

W, H = 1080, 1900
ML, MR, SAFE_B = 80, W - 72, H - 60

def base_bg(theme, acc):
    p = f"{ASSET}bg/{theme}.jpg"
    bg = Image.open(p).convert("RGB").resize((W, H)).convert("RGBA") if os.path.exists(p) \
        else Image.new("RGBA", (W, H), (16, 10, 36, 255))
    return grade(bg, acc, leak_xy=(0.85, 0.10))

def render(data, lv, out="demo_EB.png"):
    TH = theme_palette(data.get("theme", "series_purple"))
    acc, soft, hi, lo, gold = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"], (244, 206, 120)
    img = base_bg(data["theme"], acc)
    d = ImageDraw.Draw(img, "RGBA")

    # 상단바
    mark = data.get("logo_mark", "RFK")
    d.text((ML, 78), mark, font=bebas(40), fill=hi, anchor="lm")
    mw0 = measure(mark, bebas(40))[0]
    draw_ls(d, (ML + mw0 + 26, 78), data.get("logo_word", "HOLDEM CLUB"), oswald(15, 600), lo, ls=3, anchor="lm")
    draw_ls(d, (MR, 64), data["series"], oswald(20, 700), hi, ls=4, anchor="ra")
    d.text((MR, 92), data["total"], font=bebas(30), fill=gold, anchor="ra")
    draw_ls(d, (MR, 122), "TOTAL GUARANTEED", oswald(12, 500), soft, ls=3, anchor="ra")

    # HERO (좌)
    ky = 168
    d.line([(ML, ky), (ML + 44, ky)], fill=acc, width=3)
    draw_ls(d, (ML + 56, ky), data.get("kicker", "CHAMPIONSHIP MAIN EVENT"), oswald(15, 600), acc, ls=5, anchor="lm")
    ty = 192
    tf, _ = fit_font(data["title"], lambda s: bebas(s), MR - ML - 360, 92, 60)
    d.text((ML, ty), data["title"], font=tf, fill=hi, anchor="la")
    th = theight(data["title"], tf)          # 어센더 포함 실높이(겹침 방지)
    # 브랜드(우)
    draw_ls(d, (MR, ty + 8), data["brand"], oswald(26, 700), hi, ls=2, anchor="ra")
    d.text((MR, ty + 42), "★ ★ ★ ★", font=noto(15, 700), fill=gold, anchor="ra")
    draw_ls(d, (MR, ty + 70), data["date"], oswald(17, 500), soft, ls=1, anchor="ra")
    # 거대 머니 (BUY-IN은 아래 전용 행으로 이동 — 겹침 원천 차단)
    gy = ty + max(th + 16, 120)
    draw_ls(d, (ML + 2, gy), "GUARANTEED PRIZE POOL", oswald(17, 600), lo, ls=5, anchor="la")
    my = gy + theight("GUARANTEED PRIZE POOL", oswald(17, 600)) + 8
    mf, _ = fit_font(data["gtd"], lambda s: bebas(s), MR - ML - 150, 150, 96)
    mi, mw, mh = text_img(data["gtd"], mf, (255, 255, 255), TH["gtd_lo"])
    img.alpha_composite(mi, (ML, int(my)))
    d.text((ML + mw + 16, my + mh * 0.5), "GTD", font=oswald(36, 700), fill=gold, anchor="lm")

    yb = my + mh + 18
    d.line([(ML, yb), (MR, yb)], fill=(255, 255, 255, 44), width=1)
    d.line([(ML, yb), (ML + 90, yb)], fill=acc, width=3)

    # BUY-IN 행 — 스탯 스트립과 같은 규격의 프로스트 행 (라벨 칩 + 값, 수직 중앙)
    bi_y = yb + 16; bi_h = 56
    frost(img, (ML, bi_y, MR, bi_y + bi_h), 12, acc, tab=False)
    ccy = bi_y + bi_h / 2
    chip_f = oswald(12, 700)
    chw = int(lsw("BUY-IN", chip_f, 3)) + 32
    rect_blend(img, [ML + 16, ccy - 14, ML + 16 + chw, ccy + 14], (acc[0], acc[1], acc[2], 235), radius=14)
    draw_ls(d, (ML + 16 + chw / 2, ccy), "BUY-IN", chip_f, (18, 12, 32), ls=3, anchor="mm")
    bvf, _ = fit_font(data["buyin"], lambda s: noto(s, 800), MR - ML - chw - 100, 27, 21)
    d.text((ML + 16 + chw + 24, ccy), data["buyin"], font=bvf, fill=hi, anchor="lm")

    # 스탯 4열 (프로스티드 스트립) — 라벨/값 공통 크기(열별 제각각 축소 금지) + 수직 중앙
    sy0 = bi_y + bi_h + 14; sy1 = sy0 + 96
    frost(img, (ML, sy0, MR, sy1), 14, acc, tab=False)
    st = data["stats"]; n = len(st); cw = (MR - ML) / n
    lab_f, _ = fit_common([(lab, cw - 20) for lab, _ in st], lambda s: oswald(s, 600), 15, 9)
    val_f, _ = fit_common([(val, cw - 20) for _, val in st], lambda s: noto(s, 800), 30, 14)
    for i, (lab, val) in enumerate(st):
        sx = ML + cw * (i + 0.5)
        if i: d.line([(ML + cw * i, sy0 + 18), (ML + cw * i, sy1 - 18)], fill=(255, 255, 255, 30), width=1)
        draw_ls(d, (sx, sy0 + 20), lab, lab_f, soft, ls=1, anchor="ma")
        d.text((sx, sy0 + 48), val, font=val_f, fill=hi, anchor="ma")

    # BODY: 좌 프라이즈 / 우 블라인드 (프로스티드 패널)
    by0 = sy1 + 24; by1 = 1608   # Notice 4행 + 푸터가 세이프존 안에 들어오는 상한
    lw = 340
    frost(img, (ML, by0, ML + lw, by1), 16, acc)
    rx0 = ML + lw + 22
    frost(img, (rx0, by0, MR, by1), 16, acc)

    # 표 공통 규격: 프라이즈 행/블라인드 셀은 같은 크기(옆에 나란한 행들 크기 통일)
    cols = ["LV", "SB", "BB", "ANTE", "BLIND"]; prop = [0.13, 0.215, 0.215, 0.20, 0.24]
    g1 = lv[:20]; g2 = lv[20:]
    gw = (MR - rx0 - 16) / 2
    rh = (by1 - (by0 + 20) - 30) / (max(len(g1), len(g2)) + 1)
    rh = min(rh, 34)
    cell_items = [(v, gw * prop[i] - 4) for r in lv if r[0] != "BRK" for i, v in enumerate(r)]
    cell_items += [(rk, 150) for rk, _ in data["prizes"]] + [(pz, 150) for _, pz in data["prizes"]]
    cell_items += [(r[1], gw - 12) for r in lv if r[0] == "BRK"]   # BREAK행도 동일 크기
    cf_c, _ = fit_common(cell_items, lambda s: oswald(s, 600), 14, 9)
    brk_f = cf_c

    # 프라이즈
    pad = 22
    draw_ls(d, (ML + pad, by0 + 20), "PRIZE", oswald(13, 700), acc, ls=4, anchor="la")
    d.text((ML + lw - pad, by0 + 20), "RANK", font=oswald(13, 600), fill=soft, anchor="ra")
    py = by0 + 50; prh = (by1 - py - 16) / len(data["prizes"])
    pf_big = oswald(cf_c.size, 700); pf_reg = oswald(cf_c.size, 500)
    for i, (rk, pz) in enumerate(data["prizes"]):
        yy = py + prh * i
        if i % 2 == 0: rect_blend(img, [ML + 8, yy, ML + lw - 8, yy + prh], (255, 255, 255, 16))
        big = i < 3
        d.text((ML + pad, yy + prh / 2), rk, font=pf_big if big else pf_reg,
               fill=gold if big else hi, anchor="lm")
        d.text((ML + lw - pad, yy + prh / 2), pz, font=pf_big if big else pf_reg,
               fill=gold if big else soft, anchor="rm")
    def col(x0, rows):
        cen = []; a = 0
        for p in prop: cen.append(x0 + (a + p / 2) * gw); a += p
        y = by0 + 20
        d.rounded_rectangle([x0, y, x0 + gw, y + rh], radius=5, fill=acc + (235,))
        for c, cx in zip(cols, cen): d.text((cx, y + rh / 2), c, font=oswald(13, 700), fill=(18, 10, 30), anchor="mm")
        y += rh + 1; zi = 0
        for r in rows:
            if r[0] == "BRK":
                rect_blend(img, [x0, y, x0 + gw, y + rh], (acc[0], acc[1], acc[2], 95))
                d.text((x0 + gw / 2, y + rh / 2), r[1], font=brk_f, fill=hi, anchor="mm")
            else:
                if zi % 2 == 0: rect_blend(img, [x0, y, x0 + gw, y + rh], (255, 255, 255, 14))
                for i, (v, cx) in enumerate(zip(r, cen)):
                    d.text((cx, y + rh / 2), v, font=cf_c, fill=gold if i == 0 else soft, anchor="mm")
                zi += 1
            y += rh
    col(rx0, g1); col(rx0 + gw + 16, g2)

    # NOTICE + 스폰서 + 푸터
    ny = by1 + 22
    nt = vtext("NOTICE", oswald(14, 700), lo + (200,), ls=4); img.alpha_composite(nt, (ML - 6, ny))
    nx = ML + 30; colw = (MR - nx) / 2; lh = 26; half = (len(data["notice"]) + 1) // 2
    nf, _ = fit_common([("· " + l, colw - 20) for l in data["notice"]], lambda s: noto(s, 400), 14, 11)
    for ci, chunk in enumerate([data["notice"][:half], data["notice"][half:]]):
        bx2 = nx + ci * colw; yc = ny
        for line in chunk:
            d.text((bx2, yc), "·", font=nf, fill=acc, anchor="la"); d.text((bx2 + 14, yc), line, font=nf, fill=lo, anchor="la"); yc += lh
    # 좌: 스폰서(최대 3구역) / 우: 지점명+주소 2행 — 세이프존 하단 내 수용
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

    img.convert("RGB").save(out, quality=95); print("saved", out)

DATA = dict(B.DATA, kicker="CHAMPIONSHIP MAIN EVENT")
if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "series_purple"
    render(dict(DATA, theme=t), B.LV, sys.argv[2] if len(sys.argv) > 2 else "demo_EB.png")
