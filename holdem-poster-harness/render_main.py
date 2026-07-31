#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
p002 — 메인 포스터형 (A2 "히어로 메인")
learn/refs/r002~r004 계열 실습: 초대형 메탈릭 타이틀 + 동물 문장 히어로 + 로렐 배지(P6)
+ 훅 카피 슬롯(P8) + 플레어 + 네온 GTD + 문장형 상금 압축(P7) + 압축 풋터.
적용 크래프트: T2 T3 T5 / L1 L2 L3 L4 / C1 C2 C3 / H1 H2 H3(문장 배경) H4 / I1 I2 I3 / F1 F2 F3 F4
"""
import os
from PIL import Image, ImageDraw
from render_poster import noto, text_img, palette
from render_editorial import bebas, grade, metalize
from bg_animals import ANIMALS
import craft_lab as CL

W, H = 1080, 1620
ASSET = "assets/"


def base_bg(theme, acc, k, Wk, Hk):
    p = f"{ASSET}bg/{theme}.jpg"
    if os.path.exists(p):
        src = Image.open(p).convert("RGB")
        # 상단 앵커 크롭(문장 히어로 보존) 후 스케일
        ratio = Wk / Hk
        ch = min(src.height, int(src.width / ratio))
        src = src.crop((0, 0, src.width, ch)).resize((Wk, Hk))
    else:
        src = Image.new("RGB", (Wk, Hk), (10, 12, 20))
    img = grade(src.convert("RGBA"), acc, leak_xy=(0.5, 0.06), sc=k)
    # H2: 상/하단 스크림 — 타이틀·정보 스택 가독 (히어로 중앙부는 보존)
    col = Image.new("L", (1, Hk), 0)
    for yy in range(Hk):
        t = yy / Hk
        v = int(150 * max(0.0, (0.30 - t) / 0.30) ** 1.3) + int(190 * max(0.0, (t - 0.58) / 0.42) ** 1.25)
        col.putpixel((0, yy), min(210, v))
    sc_ = Image.new("RGBA", (Wk, Hk), (4, 5, 9, 255)); sc_.putalpha(col.resize((Wk, Hk)))
    img.alpha_composite(sc_)
    return img


def render(data, out="out/practice/p002.png", scale=1):
    k = scale
    Wk, Hk = W * k, H * k
    CX = Wk // 2
    acc = data["accent"]
    TH = palette(acc)
    img = base_bg(data["theme"], acc, k, Wk, Hk)
    d = ImageDraw.Draw(img)

    # ── 상단: 날짜 라인(윙 브래킷) — I1: 일시 소형
    f_dt = bebas(30 * k)
    dt = data["date_line"]
    tw = CL._ls_width(dt, f_dt, 6 * k)
    d.text((CX, 74 * k), dt, font=f_dt, fill=TH["text_hi"], anchor="mm")
    wing = 46 * k
    for sgn in (-1, 1):
        x0 = CX + sgn * (tw / 2 + 26 * k)
        d.line([(x0, 74 * k), (x0 + sgn * wing, 74 * k)], fill=acc, width=max(1, 2 * k))
        d.line([(x0 + sgn * wing * 0.72, 66 * k), (x0 + sgn * wing, 74 * k),
                (x0 + sgn * wing * 0.72, 82 * k)], fill=acc, width=max(1, 2 * k))

    # ── 타이틀: 메탈릭 디스플레이(F3) + 트래킹 서브(T2) — I1: 개런티 ≥ 대회명
    t_img, t_w, t_h = text_img(data["title"], bebas(138 * k), (250, 248, 255))
    t_img = metalize(t_img, tone=acc)
    CL.sparkle(img, CX - t_w / 2 - 40 * k, 178 * k, 9 * k, color=TH["accent_soft"], alpha=190)
    CL.sparkle(img, CX + t_w / 2 + 44 * k, 140 * k, 12 * k, color=TH["accent_soft"])
    from render_poster import place
    place(img, t_img, CX, 118 * k, shadow=True, glow_col=TH["glow"])
    f_sub = bebas(50 * k)
    sw = CL._ls_width(data["subtitle"], f_sub, 14 * k)
    CL._ls_draw(d, CX - sw / 2, 322 * k, data["subtitle"], f_sub, TH["title_lo"], 14 * k)

    # ── 로렐 배지 2개 (H1) — 좌상/우하 비대칭
    CL.laurel_badge(img, d, 158 * k, 520 * k, 92 * k, acc, data["badge_l"],
                    font=noto(19 * k, 800))
    CL.laurel_badge(img, d, 924 * k, 700 * k, 92 * k, acc, data["badge_r"],
                    font=noto(19 * k, 800))

    # ── 훅 카피 (P8/I3) — 히어로 위 트래킹 소형
    f_hook = noto(21 * k, 600)
    hook = "  ".join(data["hook"])                      # 자간 대신 공백 트래킹(한글)
    d.text((CX, 1006 * k), hook, font=f_hook, fill=TH["text_hi"], anchor="mm")

    # ── 플레어 → 킥커 → 네온 GTD (L1/L2, I1: 개런티 최상)
    CL.flare(img, CX, 1064 * k, 880 * k, acc)
    f_kick = bebas(34 * k)
    kw = CL._ls_width(data["kicker"], f_kick, 10 * k)
    CL._ls_draw(d, CX - kw / 2, 1130 * k, data["kicker"], f_kick, TH["text_lo"], 10 * k)
    CL.neon_text(img, CX, 1284 * k, data["gtd"], 150 * k, acc, unit="GTD")

    # ── 바이인 + 문장형 상금 압축 (P7)
    d.text((CX, 1336 * k), data["buyin_line"], font=noto(19 * k, 700),
           fill=TH["text_hi"], anchor="mm")
    for i, ln in enumerate(data["prize_lines"]):
        d.text((CX, (1388 + i * 34) * k), ln, font=noto(18 * k, 600),
               fill=TH["text_lo"], anchor="mm")

    # ── 풋터 (I2)
    d.line([(round(Wk * 0.06), 1496 * k), (Wk - round(Wk * 0.06), 1496 * k)],
           fill=TH["line"], width=max(1, k))
    d.text((CX, 1522 * k), data["footer"], font=noto(14 * k, 500), fill=TH["text_lo"], anchor="mm")
    f_lg = bebas(24 * k)
    d.text((CX, 1552 * k), data["logo_word"], font=f_lg, fill=TH["text_lo"], anchor="mm")
    img.convert("RGB").save(out, quality=95)
    print("saved", out, f"({Wk}x{Hk})")
    return img
