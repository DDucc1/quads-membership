#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V6 — 스트럭처 일체형 (Full Structure Sheet)
learn/refs/r001 계열 실습: 헤더(고스트+네온 GTD+플레어) + 좌 INFORMATION/PRIZE/DESCRIPTION
+ 우 BLIND STRUCTURE 풀테이블 + 스폰서 레일. 컬러웨이 시스템(C4) — 테마만 바꿔 시리즈 생성.
적용 크래프트: T1 T2 T3 T5 / L1 L2 L3 L4 / C1 C2 C3 C4 / S1 S2 S3 S4 S5 S6 / I1 I2 I4 / F1 F2 F4

고해상: render(..., scale=k) — 모든 좌표·폰트·배경을 k배 네이티브로 그린다(업스케일 아님).
k=4 → 4320×7600 ≈ A2 300DPI 인쇄급 (백로그 2번 구현, V6 선행 적용).
"""
import os
from PIL import Image, ImageDraw
from render_poster import noto, theme_palette
from render_editorial import bebas, grade
import craft_lab as CL

W, H = 1080, 1900
ASSET = "assets/"


def base_bg(theme, acc, k, Wk, Hk):
    if k == 1:
        p = f"{ASSET}bg/{theme}.jpg"
        bg = Image.open(p).convert("RGB").resize((Wk, Hk)).convert("RGBA") if os.path.exists(p) \
            else Image.new("RGBA", (Wk, Hk), (8, 12, 22, 255))
    else:
        # 네이티브 재생성 — bg_generate 모듈 해상도를 k배로 올려 같은 시드로 다시 그림
        import bg_generate as BG
        oW, oH = BG.W, BG.H
        try:
            BG.W, BG.H = Wk, Hk
            seed = 7 + BG.THEME_LIST.index(theme) * 3 if theme in BG.THEME_LIST else 7
            bg = BG.GENERATORS[theme](seed).convert("RGBA") if theme in BG.GENERATORS \
                else Image.new("RGBA", (Wk, Hk), (8, 12, 22, 255))
        finally:
            BG.W, BG.H = oW, oH
    img = grade(bg, acc, leak_xy=(0.85, 0.10), sc=k)
    # C3: 상단 침강 스크림 — 고스트/네온 대비 확보 (r001: 어두운 헤더부)
    col = Image.new("L", (1, Hk), 0)
    for yy in range(Hk):
        t = yy / Hk
        col.putpixel((0, yy), int(110 * max(0.0, (0.22 - t) / 0.22) ** 1.4))
    sc_ = Image.new("RGBA", (Wk, Hk), (3, 5, 10, 255)); sc_.putalpha(col.resize((Wk, Hk)))
    img.alpha_composite(sc_)
    return img


def render(data, out="out/practice/p001.png", scale=1):
    k = scale
    Wk, Hk = W * k, H * k
    CX = Wk // 2
    LX0, LX1 = round(Wk * 0.06), 515 * k
    RX0, RX1 = 545 * k, Wk - round(Wk * 0.06)
    TH = theme_palette(data["theme"])
    acc = TH["accent"]
    img = base_bg(data["theme"], acc, k, Wk, Hk)
    d = ImageDraw.Draw(img)

    # ── 헤더: T1 고스트 → L3 스파클 → T2 킥커(=대회명) → L1 네온 GTD → L2 플레어
    CL.ghost_title(img, data["title"], 160 * k, acc, alpha=50, ls=16 * k, crop=0.40)
    CL.sparkle(img, CX, 132 * k, 17 * k, color=TH["accent_soft"])
    CL.sparkle(img, CX - 56 * k, 114 * k, 8 * k, color=TH["accent_soft"], alpha=190)
    CL.sparkle(img, CX + 58 * k, 144 * k, 7 * k, color=TH["accent_soft"], alpha=170)
    f_t = bebas(48 * k)
    tw = CL._ls_width(data["title"], f_t, 13 * k)
    CL._ls_draw(d, CX - tw / 2, 216 * k, data["title"], f_t, TH["title_lo"], 13 * k)
    CL.neon_text(img, CX, 386 * k, data["gtd"], 168 * k, acc, unit="GTD")
    CL.flare(img, CX, 436 * k, 960 * k, acc)

    # ── 좌/우 컬럼을 QC 패널로 선언(분리된 시각 컨텍스트 — R4 상호 비교 제외)
    CL.panel([LX0, 470 * k, LX1, 1660 * k])
    CL.panel([RX0, 470 * k, RX1, 1660 * k])

    # ── 좌 컬럼
    y = 474 * k
    CL.header_bar(img, d, LX0, LX1, y, 44 * k, "INFORMATION", acc)
    f_i = noto(16 * k, 600)
    y += 54 * k
    for i, t in enumerate(data["info"]):                    # S2 지브라
        CL.zebra_row(img, [LX0, y, LX1, y + 34 * k], alpha=20 if i % 2 else 30)
        d.text((LX0 + 14 * k, y + 17 * k), t, font=f_i, fill=TH["text_hi"], anchor="lm")
        y += 39 * k
    y += 14 * k
    CL.header_bar(img, d, LX0, LX1, y, 44 * k, "PRIZE POOL", acc)
    y += 54 * k
    f1 = bebas(34 * k); fr_ = bebas(26 * k)                 # S4/S5/S6
    CL.zebra_row(img, [LX0, y, LX1, y + 48 * k], alpha=52)
    d.rectangle([LX0, y, LX0 + 4 * k, y + 48 * k], fill=acc)
    rk, amt = data["prizes"][0]
    d.text((LX0 + 18 * k, y + 24 * k), rk, font=f1, fill=acc, anchor="lm")
    d.text((LX1 - 14 * k, y + 24 * k), amt, font=f1, fill=acc, anchor="rm")
    y += 52 * k
    for i, (rk, amt) in enumerate(data["prizes"][1:]):
        CL.zebra_row(img, [LX0, y, LX1, y + 38 * k], alpha=20 if i % 2 else 30)
        d.text((LX0 + 18 * k, y + 19 * k), rk, font=fr_, fill=TH["text_hi"], anchor="lm")
        d.text((LX1 - 14 * k, y + 19 * k), amt, font=fr_, fill=TH["text_hi"], anchor="rm")
        y += 42 * k
    y += 14 * k
    CL.header_bar(img, d, LX0, LX1, y, 44 * k, "EVENT DESCRIPTION", acc)
    y += 58 * k
    f_d = noto(14 * k, 500)
    for t in data["desc"]:
        d.text((LX0 + 4 * k, y), t, font=f_d, fill=TH["text_lo"], anchor="la")
        y += 25 * k

    # ── 우 컬럼: 블라인드 풀테이블 (S3 브레이크 밴드 · S4 우측 정렬 · S6 행높이 균일)
    CL.header_bar(img, d, RX0, RX1, 474 * k, 44 * k, "BLIND STRUCTURE", acc)
    fh = bebas(19 * k); fv = bebas(21 * k); fb = bebas(16 * k)
    rh = 30 * k
    y = 530 * k
    cols = [("LEVEL", 590, "m"), ("SB", 723, "r"), ("BB", 826, "r"),
            ("ANTE", 929, "r"), ("TIME", 1003, "r")]
    for t, x, a in cols:
        d.text((x * k, y + rh / 2), t, font=fh, fill=TH["accent_soft"],
               anchor=("mm" if a == "m" else "rm"))
    y += rh + 4 * k
    lv_no = 0; zi = 0
    for it in data["blinds_disp"]:
        if isinstance(it, str):
            CL.break_band(img, [RX0, y + 2 * k, RX1, y + rh - 2 * k], acc, alpha=54)
            d.text(((RX0 + RX1) / 2, y + rh / 2), it, font=fb, fill=TH["text_hi"], anchor="mm")
            zi = 0
        else:
            lv_no += 1
            if zi % 2 == 0:
                CL.zebra_row(img, [RX0, y + k, RX1, y + rh - k], alpha=16)
            sb, bb = it
            d.text((590 * k, y + rh / 2), str(lv_no), font=fv, fill=TH["text_hi"], anchor="mm")
            for val, x in [(sb, 723), (bb, 826), (bb, 929)]:
                d.text((x * k, y + rh / 2), f"{val:,}", font=fv, fill=TH["text_hi"], anchor="rm")
            d.text((1003 * k, y + rh / 2), "25", font=fv, fill=TH["text_lo"], anchor="rm")
            zi += 1
        y += rh

    # ── 풋터: I2 압축 · I4 스폰서 레일(단색 워드마크)
    d.line([(LX0, 1742 * k), (RX1, 1742 * k)], fill=TH["line"], width=max(1, k))
    d.text((CX, 1770 * k), data["footer"], font=noto(14 * k, 500), fill=TH["text_lo"], anchor="mm")
    fs = bebas(22 * k)
    words = data["sponsors"]
    gap = 58 * k
    tot = sum(fs.getlength(w_) for w_ in words) + gap * (len(words) - 1)
    x = CX - tot / 2
    for w_ in words:
        d.text((x, 1830 * k), w_, font=fs, fill=TH["text_lo"], anchor="ls")
        x += fs.getlength(w_) + gap
    img.convert("RGB").save(out, quality=95)
    print("saved", out, f"({Wk}x{Hk})")
    return img
