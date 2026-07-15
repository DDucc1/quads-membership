#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""에디토리얼 크래프트 — C형(시리즈 스케줄 그리드). 프로스티드 그리드 + 날짜 그룹 + 거대 총보증."""
import os, sys
from PIL import Image, ImageDraw
from render_poster import noto, measure, fit_font, fit_common, draw_ls, lsw, text_img, theight, theme_palette, ASSET
from render_editorial import bebas, oswald, grade, frost, vtext, spade, rect_blend

W, H = 1080, 1860
ML, MR, SAFE_B = 72, W - 72, H - 54

DATA = dict(
    theme="series_blue", series="DREAM SERIES", total="400,000,000",
    brand="대구 ANPT", period="05.27 — 05.31",
    kicker="GRAND FESTIVAL · FULL SCHEDULE",
    venue_name="대구 ANPT 스타디움", venue_addr="대구광역시 북구 고성북로 10길 45",
    sponsors=[("주관사", "POKER OF DREAMS"), ("협력사", "SEEDKET · ON&ON"), ("후원사", "MOXSYS")],
    cols=["DATE", "TIME", "EVENT", "BUY-IN", "GTD", "ENTRY", "STACK", "LV", "CLOSE"],
    prop=[0.105, 0.075, 0.245, 0.135, 0.13, 0.075, 0.085, 0.06, 0.09],
    rows=[
        ("05.27 WED", "13:00", "#1 OPENING DEEP", "1 TICKET / 30FP", "20,000,000", "200++", "30,000", "20", "14LV"),
        ("05.27 WED", "19:00", "#2 NIGHT TURBO", "1 TICKET / 20FP", "10,000,000", "150++", "25,000", "18", "12LV"),
        ("05.28 THU", "18:00", "#3 BOUNTY HUNTER", "1 TICKET / 40FP", "30,000,000", "250++", "40,000", "25", "13LV"),
        ("05.29 FRI", "16:00", "#4 MASTERS w/EUREKA", "1 TICKET / 60FP", "50,000,000", "119++", "60,000", "30", "15LV"),
        ("05.29 FRI", "23:00", "#5 SATELLITE HR", "20 SEED", "WIN 1 SEAT", "8 TO 1", "20,000", "15", "14LV"),
        ("05.30 SAT", "13:00", "#6 HIGH-ROLLER", "1 TICKET / 120FP", "100,000,000", "119++", "80,000", "40", "15LV"),
        ("05.30 SAT", "18:00", "#7 MYSTERY KO", "1 TICKET / 30FP", "40,000,000", "300++", "50,000", "30", "12LV"),
        ("05.31 SUN", "14:00", "#8 MAIN EVENT DAY2", "MAIN 1 TICKET", "200,000,000", "955++", "40,000", "30", "13LV"),
    ],
)

def render(data, out="demo_EC.png"):
    TH = theme_palette(data.get("theme", "series_blue"))
    acc, soft, hi, lo, gold = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"], (244, 206, 120)
    p = f"{ASSET}bg/{data['theme']}.jpg"
    bg = Image.open(p).convert("RGB").resize((W, H)).convert("RGBA") if os.path.exists(p) else Image.new("RGBA", (W, H), (8, 14, 34, 255))
    img = grade(bg, acc, leak_xy=(0.84, 0.10)); d = ImageDraw.Draw(img, "RGBA")
    gw = Image.new("RGBA", (W, H), (0, 0, 0, 0)); spade(ImageDraw.Draw(gw), int(W * 0.85), int(H * 0.5), 330, acc + (20,))
    img.alpha_composite(gw.filter(ImageFilter_safe()))

    # 상단바
    d.text((ML, 78), "PoD", font=bebas(40), fill=hi, anchor="lm")
    draw_ls(d, (ML + 70, 78), "POKER OF DREAMS", oswald(15, 600), lo, ls=3, anchor="lm")
    draw_ls(d, (MR, 64), data["brand"], oswald(20, 700), hi, ls=3, anchor="ra")
    draw_ls(d, (MR, 92), data["period"], oswald(16, 500), soft, ls=3, anchor="ra")
    d.line([(ML, 120), (MR, 120)], fill=(255, 255, 255, 38), width=1)

    # HERO
    ky = 176
    d.line([(ML, ky), (ML + 46, ky)], fill=acc, width=3)
    draw_ls(d, (ML + 58, ky), data["kicker"], oswald(16, 600), acc, ls=5, anchor="lm")
    tf, _ = fit_font(data["series"], lambda s: bebas(s), MR - ML, 132, 90)
    d.text((ML, 198), data["series"], font=tf, fill=hi, anchor="la")
    gyl = 198 + theight(data["series"], tf) + 14   # 어센더 포함 실높이(겹침 방지)
    draw_ls(d, (ML + 2, gyl), "TOTAL GUARANTEED", oswald(20, 600), lo, ls=6, anchor="la")
    my = gyl + theight("TOTAL GUARANTEED", oswald(20, 600)) + 8
    mf, _ = fit_font(data["total"], lambda s: bebas(s), MR - ML - 140, 150, 96)
    mi, mw, mh = text_img(data["total"], mf, (255, 255, 255), TH["gtd_lo"])
    img.alpha_composite(mi, (ML, int(my)))
    d.text((ML + mw + 16, my + mh * 0.52), "KRW", font=oswald(34, 700), fill=gold, anchor="lm")
    ry = my + mh + 16
    d.line([(ML, ry), (MR, ry)], fill=(255, 255, 255, 44), width=1); d.line([(ML, ry), (ML + 90, ry)], fill=acc, width=3)

    # ===== 스케줄 그리드 (프로스티드) =====
    gx0, gy0, gx1, gy1 = ML - 4, ry + 26, MR + 4, SAFE_B - 100
    frost(img, (gx0, gy0, gx1, gy1), 16, acc, alpha=210, tab=False)
    inx0, inx1 = gx0 + 24, gx1 - 24; gw_ = inx1 - inx0
    cen = []; a = 0
    for p_ in data["prop"]:
        cen.append(inx0 + (a + p_ / 2) * gw_); a += p_
    hrow = 44
    hy = gy0 + 16
    for c, cx in zip(data["cols"], cen):
        draw_ls(d, (cx, hy + hrow / 2), c, oswald(14, 700), acc, ls=1, anchor="mm")
    d.line([(inx0, hy + hrow), (inx1, hy + hrow)], fill=acc + (200,), width=2)
    rows = data["rows"]; ry0 = hy + hrow + 4
    rh = (gy1 - ry0 - 14) / len(rows)
    # 그리드 전 셀 공통 크기(행/열 제각각 축소 금지). 굵기·색만 역할 구분.
    items = []
    for row in rows:
        for j, v in enumerate(row):
            if j == 0: items.append((v.split()[0], gw_ * data["prop"][0] - 6))
            else: items.append((v, gw_ * data["prop"][j] - 6))
    gf_c, _ = fit_common(items, lambda s: oswald(s, 700), 14, 9)
    gf_bold = oswald(gf_c.size, 700); gf_reg = oswald(gf_c.size, 500)
    prev_date = None
    for i, row in enumerate(rows):
        yy = ry0 + rh * i
        new_grp = row[0] != prev_date
        if new_grp and i: d.line([(inx0, yy), (inx1, yy)], fill=(255, 255, 255, 40), width=1)
        elif i: d.line([(inx0 + gw_ * data["prop"][0], yy), (inx1, yy)], fill=(255, 255, 255, 16), width=1)
        if i % 2 == 0: rect_blend(img, [inx0 - 8, yy, inx1 + 8, yy + rh], (0, 0, 0, 70))
        for j, (v, cx) in enumerate(zip(row, cen)):
            if j == 0:
                if not new_grp: continue
                d.text((cx, yy + rh / 2), v.split()[0], font=gf_bold, fill=hi, anchor="mm")
                d.text((cx, yy + rh / 2 + 20), v.split()[1], font=oswald(11, 500), fill=soft, anchor="mm")
            elif j == 2:
                d.text((cx, yy + rh / 2), v, font=gf_bold, fill=hi, anchor="mm")
            elif j == 4:
                d.text((cx, yy + rh / 2), v, font=gf_bold, fill=gold, anchor="mm")
            else:
                d.text((cx, yy + rh / 2), v, font=gf_reg, fill=soft, anchor="mm")
        prev_date = row[0]

    # 스폰서 / 푸터
    # 좌: 스폰서(최대 3구역) / 우: 지점명+주소 2행 — 세이프존 하단 내 수용
    spy = SAFE_B - 44
    d.line([(ML, spy - 16), (MR, spy - 16)], fill=(255, 255, 255, 32), width=1)
    sx = ML
    for lab, name in data["sponsors"][:3]:
        if sx > MR - 460: break
        draw_ls(d, (sx, spy), lab, noto(12, 600), acc, ls=1, anchor="la")
        d.text((sx, spy + 18), name, font=noto(15, 700), fill=hi, anchor="la")
        sx += measure(name, noto(15, 700))[0] + 44
    d.text((MR, spy), data["venue_name"], font=noto(15, 700), fill=hi, anchor="ra")
    d.text((MR, spy + 20), data["venue_addr"], font=noto(15, 400), fill=lo, anchor="ra")

    img.convert("RGB").save(out, quality=95); print("saved", out)

def ImageFilter_safe():
    from PIL import ImageFilter
    return ImageFilter.GaussianBlur(2)

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "series_blue"
    render(dict(DATA, theme=t), sys.argv[2] if len(sys.argv) > 2 else "demo_EC.png")
