#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V6 — 스트럭처 일체형 (Full Structure Sheet)
learn/refs/r001 계열 실습: 헤더(고스트+네온 GTD+플레어) + 좌 INFORMATION/PRIZE/DESCRIPTION
+ 우 BLIND STRUCTURE 풀테이블 + 스폰서 레일. 컬러웨이 시스템(C4) — 테마만 바꿔 시리즈 생성.
적용 크래프트: T1 T2 T3 T5 / L1 L2 L3 L4 / C1 C2 C3 C4 / S1 S2 S3 S4 S5 S6 / I1 I2 I4 / F1 F2 F4
"""
import os
from PIL import Image, ImageDraw
from render_poster import noto, theme_palette
from render_editorial import bebas, grade
import craft_lab as CL

W, H = 1080, 1900
SAFE_L = round(W * 0.06); SAFE_R = W - SAFE_L
CX = W // 2
ASSET = "assets/"

# 좌/우 컬럼
LX0, LX1 = SAFE_L, 515
RX0, RX1 = 545, SAFE_R


def base_bg(theme, acc):
    p = f"{ASSET}bg/{theme}.jpg"
    bg = Image.open(p).convert("RGB").resize((W, H)).convert("RGBA") if os.path.exists(p) \
        else Image.new("RGBA", (W, H), (8, 12, 22, 255))
    img = grade(bg, acc, leak_xy=(0.85, 0.10))
    # C3: 상단 침강 스크림 — 고스트/네온 대비 확보 (r001: 어두운 헤더부)
    col = Image.new("L", (1, H), 0)
    for yy in range(H):
        t = yy / H
        col.putpixel((0, yy), int(110 * max(0.0, (0.22 - t) / 0.22) ** 1.4))
    sc = Image.new("RGBA", (W, H), (3, 5, 10, 255)); sc.putalpha(col.resize((W, H)))
    img.alpha_composite(sc)
    return img


def _info_rows(img, d, TH, y, rows, rh=34, gap=5):
    f = noto(16, 600)
    for i, t in enumerate(rows):
        CL.zebra_row(img, [LX0, y, LX1, y + rh], alpha=20 if i % 2 else 30)
        d.text((LX0 + 14, y + rh / 2), t, font=f, fill=TH["text_hi"], anchor="lm")
        y += rh + gap
    return y


def _prize_rows(img, d, TH, y, prizes):
    # S5: 1위 3중 강조(크기+액센트색+행 배경) · S4 숫자 우측 · S6 행높이 균일
    f1 = bebas(34); fr_ = bebas(26)
    rh1, rh = 48, 38
    CL.zebra_row(img, [LX0, y, LX1, y + rh1], alpha=52)
    d.rectangle([LX0, y, LX0 + 4, y + rh1], fill=TH["accent"])
    rk, amt = prizes[0]
    d.text((LX0 + 18, y + rh1 / 2), rk, font=f1, fill=TH["accent"], anchor="lm")
    d.text((LX1 - 14, y + rh1 / 2), amt, font=f1, fill=TH["accent"], anchor="rm")
    y += rh1 + 4
    for i, (rk, amt) in enumerate(prizes[1:]):
        CL.zebra_row(img, [LX0, y, LX1, y + rh], alpha=20 if i % 2 else 30)
        d.text((LX0 + 18, y + rh / 2), rk, font=fr_, fill=TH["text_hi"], anchor="lm")
        d.text((LX1 - 14, y + rh / 2), amt, font=fr_, fill=TH["text_hi"], anchor="rm")
        y += rh + 4
    return y


def _desc_rows(d, TH, y, lines):
    f = noto(14, 500)
    for t in lines:
        d.text((LX0 + 4, y), t, font=f, fill=TH["text_lo"], anchor="la")
        y += 25
    return y


def _blind_table(img, d, TH, y, lvs):
    # S3 브레이크 밴드 · S4 우측 정렬 · S6 행높이 균일
    fh = bebas(19); fv = bebas(21); fb = bebas(16)
    rh = 30
    cols = [("LEVEL", 590, "m"), ("SB", 723, "r"), ("BB", 826, "r"),
            ("ANTE", 929, "r"), ("TIME", 1003, "r")]
    for t, x, a in cols:
        d.text((x, y + rh / 2), t, font=fh, fill=TH["accent_soft"],
               anchor=("mm" if a == "m" else "rm"))
    y += rh + 4
    lv_no = 0; zi = 0
    for it in lvs:
        if isinstance(it, str):                       # 브레이크 밴드
            CL.break_band(img, [RX0, y + 2, RX1, y + rh - 2], TH["accent"], alpha=54)
            d.text(((RX0 + RX1) / 2, y + rh / 2), it, font=fb, fill=TH["text_hi"], anchor="mm")
            zi = 0
        else:
            lv_no += 1
            if zi % 2 == 0:
                CL.zebra_row(img, [RX0, y + 1, RX1, y + rh - 1], alpha=16)
            sb, bb = it
            d.text((590, y + rh / 2), str(lv_no), font=fv, fill=TH["text_hi"], anchor="mm")
            for val, x in [(sb, 723), (bb, 826), (bb, 929)]:
                d.text((x, y + rh / 2), f"{val:,}", font=fv, fill=TH["text_hi"], anchor="rm")
            d.text((1003, y + rh / 2), "25", font=fv, fill=TH["text_lo"], anchor="rm")
            zi += 1
        y += rh
    return y


def render(data, out="out/practice/p001.png"):
    TH = theme_palette(data["theme"])
    acc = TH["accent"]
    img = base_bg(data["theme"], acc)
    d = ImageDraw.Draw(img)

    # ── 헤더: T1 고스트 → L3 스파클 → T2 킥커(=대회명) → L1 네온 GTD → L2 플레어
    CL.ghost_title(img, data["title"], 160, acc, alpha=50, ls=16, crop=0.40)
    CL.sparkle(img, CX, 132, 17, color=TH["accent_soft"])
    CL.sparkle(img, CX - 56, 114, 8, color=TH["accent_soft"], alpha=190)
    CL.sparkle(img, CX + 58, 144, 7, color=TH["accent_soft"], alpha=170)
    f_t = bebas(48)
    tw = CL._ls_width(data["title"], f_t, 13)
    CL._ls_draw(d, CX - tw / 2, 216, data["title"], f_t, TH["title_lo"], 13)
    CL.neon_text(img, CX, 386, data["gtd"], 168, acc, unit="GTD")
    CL.flare(img, CX, 436, 960, acc)

    # ── 좌/우 컬럼을 QC 패널로 선언(분리된 시각 컨텍스트 — R4 상호 비교 제외)
    CL.panel([LX0, 470, LX1, 1660])
    CL.panel([RX0, 470, RX1, 1660])

    # ── 좌 컬럼
    y = 474
    CL.header_bar(img, d, LX0, LX1, y, 44, "INFORMATION", acc)
    y = _info_rows(img, d, TH, y + 54, data["info"])
    y += 14
    CL.header_bar(img, d, LX0, LX1, y, 44, "PRIZE POOL", acc)
    y = _prize_rows(img, d, TH, y + 54, data["prizes"])
    y += 14
    CL.header_bar(img, d, LX0, LX1, y, 44, "EVENT DESCRIPTION", acc)
    _desc_rows(d, TH, y + 58, data["desc"])

    # ── 우 컬럼
    CL.header_bar(img, d, RX0, RX1, 474, 44, "BLIND STRUCTURE", acc)
    _blind_table(img, d, TH, 530, data["blinds_disp"])

    # ── 풋터: I2 압축 · I4 스폰서 레일(단색 워드마크)
    d.line([(SAFE_L, 1742), (SAFE_R, 1742)], fill=TH["line"], width=1)
    fv = noto(14, 500)
    d.text((CX, 1770), data["footer"], font=fv, fill=TH["text_lo"], anchor="mm")
    fs = bebas(22)
    words = data["sponsors"]
    gap = 58
    tot = sum(fs.getlength(w) for w in words) + gap * (len(words) - 1)
    x = CX - tot / 2
    for w_ in words:
        d.text((x, 1830), w_, font=fs, fill=TH["text_lo"], anchor="ls")
        x += fs.getlength(w_) + gap
    img.convert("RGB").save(out, quality=95)
    print("saved", out)
    return img
