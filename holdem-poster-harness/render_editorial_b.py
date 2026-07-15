#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""에디토리얼 크래프트 — B형(스트럭처 시트). 프로스티드 표 패널 + 거대 머니 + 새 타이포."""
import os, sys
from PIL import Image, ImageDraw
from render_poster import noto, measure, fit_font, draw_ls, lsw, text_img, theight, theme_palette, ASSET
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
    d.text((ML, 78), "PoD", font=bebas(40), fill=hi, anchor="lm")
    draw_ls(d, (ML + 70, 78), "POKER OF DREAMS", oswald(15, 600), lo, ls=3, anchor="lm")
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

    # BUY-IN 전용 행 (전폭 — 좌 라벨 + 값)
    bi_y = yb + 16
    draw_ls(d, (ML, bi_y + 8), "BUY-IN", oswald(14, 600), acc, ls=3, anchor="la")
    bvf, _ = fit_font(data["buyin"], lambda s: noto(s, 800), MR - ML - 160, 26, 15)
    d.text((ML + 118, bi_y), data["buyin"], font=bvf, fill=hi, anchor="la")

    # 스탯 4열 (프로스티드 스트립)
    sy0 = bi_y + 48; sy1 = sy0 + 96
    frost(img, (ML, sy0, MR, sy1), 14, acc, tab=False)
    st = data["stats"]; n = len(st); cw = (MR - ML) / n
    for i, (lab, val) in enumerate(st):
        sx = ML + cw * (i + 0.5)
        if i: d.line([(ML + cw * i, sy0 + 18), (ML + cw * i, sy1 - 18)], fill=(255, 255, 255, 30), width=1)
        lf, _ = fit_font(lab, lambda s: oswald(s, 600), cw - 16, 15, 10)
        draw_ls(d, (sx, sy0 + 22), lab, lf, soft, ls=1, anchor="ma")
        vf, _ = fit_font(val, lambda s: noto(s, 800), cw - 16, 30, 15)
        d.text((sx, sy0 + 50), val, font=vf, fill=hi, anchor="ma")

    # BODY: 좌 프라이즈 / 우 블라인드 (프로스티드 패널)
    by0 = sy1 + 24; by1 = 1608   # Notice 4행 + 푸터가 세이프존 안에 들어오는 상한
    lw = 340
    frost(img, (ML, by0, ML + lw, by1), 16, acc)
    rx0 = ML + lw + 22
    frost(img, (rx0, by0, MR, by1), 16, acc)

    # 프라이즈
    pad = 22
    draw_ls(d, (ML + pad, by0 + 20), "PRIZE", oswald(16, 700), acc, ls=4, anchor="la")
    d.text((ML + lw - pad, by0 + 16), "RANK", font=oswald(13, 600), fill=soft, anchor="ra")
    py = by0 + 50; prh = (by1 - py - 16) / len(data["prizes"])
    for i, (rk, pz) in enumerate(data["prizes"]):
        yy = py + prh * i
        if i % 2 == 0: rect_blend(img, [ML + 8, yy, ML + lw - 8, yy + prh], (255, 255, 255, 16))
        big = i < 3
        d.text((ML + pad, yy + prh / 2), rk, font=oswald(15, 700 if big else 500),
               fill=gold if big else hi, anchor="lm")
        d.text((ML + lw - pad, yy + prh / 2), pz, font=oswald(15, 700 if big else 500),
               fill=gold if big else soft, anchor="rm")

    # 블라인드 2 서브컬럼
    cols = ["LV", "SB", "BB", "ANTE", "BLIND"]; prop = [0.13, 0.215, 0.215, 0.20, 0.24]
    g1 = lv[:20]; g2 = lv[20:]
    gw = (MR - rx0 - 16) / 2
    rh = (by1 - (by0 + 20) - 30) / (max(len(g1), len(g2)) + 1)
    rh = min(rh, 34)
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
                t = r[1]; f = oswald(13, 600)
                if measure(t, f)[0] > gw - 10: f, _ = fit_font(t, lambda s: oswald(s, 600), gw - 10, 13, 9)
                d.text((x0 + gw / 2, y + rh / 2), t, font=f, fill=hi, anchor="mm")
            else:
                if zi % 2 == 0: rect_blend(img, [x0, y, x0 + gw, y + rh], (255, 255, 255, 14))
                for i, (v, cx) in enumerate(zip(r, cen)):
                    f = oswald(14, 600)
                    if measure(v, f)[0] > gw * prop[i] - 3: f, _ = fit_font(v, lambda s: oswald(s, 600), gw * prop[i] - 3, 14, 9)
                    d.text((cx, y + rh / 2), v, font=f, fill=gold if i == 0 else soft, anchor="mm")
                zi += 1
            y += rh
    col(rx0, g1); col(rx0 + gw + 16, g2)

    # NOTICE + 스폰서 + 푸터
    ny = by1 + 22
    nt = vtext("NOTICE", oswald(14, 700), lo + (200,), ls=4); img.alpha_composite(nt, (ML - 6, ny))
    nx = ML + 30; colw = (MR - nx) / 2; lh = 26; half = (len(data["notice"]) + 1) // 2
    for ci, chunk in enumerate([data["notice"][:half], data["notice"][half:]]):
        bx2 = nx + ci * colw; yc = ny
        for line in chunk:
            f = noto(14, 400)
            if measure("· " + line, f)[0] > colw - 20: f, _ = fit_font("· " + line, lambda s: noto(s, 400), colw - 20, 14, 11)
            d.text((bx2, yc), "·", font=f, fill=acc, anchor="la"); d.text((bx2 + 14, yc), line, font=f, fill=lo, anchor="la"); yc += lh
    # 좌: 스폰서(최대 3구역) / 우: 지점명+주소 2행 — 세이프존 하단 내 수용
    spy = SAFE_B - 44
    d.line([(ML, spy - 14), (MR, spy - 14)], fill=(255, 255, 255, 32), width=1)
    sx = ML
    for lab, name in data["sponsors"][:3]:
        if sx > MR - 460: break
        draw_ls(d, (sx, spy), lab, noto(12, 600), acc, ls=1, anchor="la")
        d.text((sx, spy + 18), name, font=noto(15, 700), fill=hi, anchor="la")
        sx += measure(name, noto(15, 700))[0] + 40
    d.text((MR, spy), data["venue_name"], font=noto(14, 700), fill=hi, anchor="ra")
    d.text((MR, spy + 18), data["venue_addr"], font=noto(13, 400), fill=lo, anchor="ra")

    img.convert("RGB").save(out, quality=95); print("saved", out)

DATA = dict(B.DATA, kicker="CHAMPIONSHIP MAIN EVENT")
if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "series_purple"
    render(dict(DATA, theme=t), B.LV, sys.argv[2] if len(sys.argv) > 2 else "demo_EB.png")
