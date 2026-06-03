#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홀덤 포스터 하네스 — 아키타입 B 렌더러 (스트럭처 시트)
좌: 프라이즈 표 / 우: 블라인드 스트럭처(2-컬럼 그룹) / 상단: 타이틀+스탯.
스트럭처 데이터 = MAIN EVENT 200,000,000 GTD 레퍼런스 기준.
공통 헬퍼는 render_poster.py 에서 재사용.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
from render_poster import noto, anton, measure, fit_font, draw_ls, lsw, text_img

W, H = 1080, 1800
SAFE_L = round(W * 0.06); SAFE_R = W - SAFE_L
SAFE_T = round(H * 0.03); SAFE_B = H - SAFE_T
CW = SAFE_R - SAFE_L; CX = W // 2

ASSET = "assets/"
_base = dict(text_hi=(242,240,250), text_lo=(202,192,218), mute=(150,138,172),
             gold=(244,206,120), gold_lo=(206,156,64), zebra=(255,255,255),
             red=(206,46,74), panel=(22,13,44))
THEMES_B = {
  "series_purple": dict(_base, accent=(186,134,238), accent_soft=(212,178,248), line=(96,70,140), break_bg=(108,64,168)),
  "series_red":    dict(_base, accent=(236,84,86), accent_soft=(255,156,150), line=(128,54,58), break_bg=(150,50,55)),
  "series_blue":   dict(_base, accent=(78,156,246), accent_soft=(160,202,255), line=(58,90,150), break_bg=(44,92,168)),
}
C = THEMES_B["series_purple"]

def bg(theme="series_purple"):
    p = f"{ASSET}bg/{theme}.jpg"
    base = Image.open(p).convert("RGB").resize((W, H)) if os.path.exists(p) else Image.new("RGB", (W, H), (24, 12, 48))
    base = base.point(lambda v: int(v * 0.92)).convert("RGBA")
    # 하단(표 영역) 다크 스크림 — 표 가독 확보
    col = Image.new("L", (1, H), 0)
    for y in range(H):
        t = y / H; v = 0
        if t > 0.30: v = int(min(150, 150 * (t - 0.30) / 0.5))
        col.putpixel((0, y), v)
    sc = Image.new("RGBA", (W, H), (10, 5, 24, 255)); sc.putalpha(col.resize((W, H)))
    base.alpha_composite(sc)
    return base

# ---------- 데이터 (MAIN EVENT 200M) ----------
DATA = dict(
    series="DREAM SERIES", total="400,000,000", brand="대구 ANPT",
    title="MAIN EVENT", gtd="200,000,000",
    date="DAY2 : 26.05.31 (SUN) - 14:00",
    buyin="MAIN 1 TICKET OR 30FP",
    stats=[("STARTING STACK", "40,000"), ("END of REG", "13LV 시작 전"),
           ("DURATION (TURBO)", "30(20) / 30 mins"), ("ENTRY", "955++")],
    venue_name="대구 ANPT 스타디움", venue_addr="대구광역시 북구 고성북로 10길 45",
    sponsors=[("주관사", "POKER of DREAMS"), ("협력사", "SEEDKET · ON&ON"),
              ("후원사", "MOXSYS · 한베교류발전위원회"), ("장소", "ANPT")],
    notice=[
        "ITM & DAY2 진출 인원 12.5% 입니다.", "DAY2 시작 레벨은 LV17 입니다.",
        "빅 블라인드 엔티 방식으로 진행됩니다.", "엔티는 토너먼트가 끝나기 전까지 줄지 않습니다.",
        "국제 TDA 규정을 준수합니다.", "테이블은 9max로 진행합니다.",
        "대회 참가자는 본인 신분증을 지참하여 본인 확인을 진행합니다.",
        "상금을 획득한 선수는 세금신고를 의무화 해야합니다.",
    ],
    prizes=[("1st", "30,000,000"), ("2nd", "20,000,000"), ("3rd", "15,000,000"),
            ("4th", "10,500,000"), ("5th", "7,500,000"), ("6th", "5,500,000"),
            ("7th", "4,100,000"), ("8th", "3,100,000"), ("9th", "2,200,000"),
            ("10th~12th", "1,800,000"), ("13th~20th", "1,500,000"), ("21st~30th", "1,300,000"),
            ("31st~40th", "1,200,000"), ("41st~50th", "1,100,000"), ("51st~60th", "1,000,000"),
            ("61st~70th", "900,000"), ("71st~80th", "800,000"), ("81st~90th", "700,000"),
            ("91st~100th", "600,000"), ("101st~110th", "500,000"), ("111th~119th", "400,000")],
)
# 블라인드: ("LV",sb,bb,ante,blind) 또는 ("BRK", 텍스트)
LV = [
    ("1","100","200","200","30(20)"),("2","200","400","400","30(20)"),
    ("3","300","600","600","30(20)"),("4","400","800","800","30(20)"),
    ("BRK","Break 10min"),
    ("5","500","1,000","1,000","30(20)"),("6","500","1,000","1,000","30(20)"),
    ("7","600","1,200","1,200","30(20)"),("8","800","1,600","1,600","30(20)"),
    ("BRK","Break 10min / Remove 100 Chips"),
    ("9","1,000","2,000","2,000","30(20)"),("10","1,000","2,000","2,000","30(20)"),
    ("11","1,500","2,500","2,500","30(20)"),("12","1,500","3,000","3,000","30(20)"),
    ("BRK","Break 15min  *END of REG"),
    ("13","1,500","3,000","3,000","30"),("14","2,000","4,000","4,000","30"),
    ("15","2,500","5,000","5,000","30"),("16","3,000","6,000","6,000","30"),
    ("BRK","Break 10min / Remove 500 Chips"),
    # ----- 우측 그룹 -----
    ("17","4,000","8,000","8,000","30"),("18","5,000","10,000","10,000","30"),
    ("19","6,000","12,000","12,000","30"),("20","10,000","15,000","15,000","30"),
    ("BRK","Break 10min / Remove 1,000 Chips"),
    ("21","10,000","20,000","20,000","30"),("22","15,000","25,000","25,000","30"),
    ("23","15,000","30,000","30,000","30"),("24","20,000","40,000","40,000","30"),
    ("BRK","Break 10min"),
    ("25","30,000","50,000","50,000","30"),("26","40,000","60,000","60,000","30"),
    ("27","40,000","80,000","80,000","30"),("28","50,000","100,000","100,000","30"),
    ("BRK","Break 10min"),
    ("29","60,000","120,000","120,000","30"),("30","75,000","150,000","150,000","30"),
    ("31","100,000","200,000","200,000","30"),("32","150,000","300,000","300,000","30"),
    ("33","250,000","500,000","500,000","30"),
    ("BRK","T.D DECISION"),
]

def ctext(d, cx, cy, t, f, fill, maxw=None):
    if maxw: f, _ = fit_font(t, lambda s: noto(s, f.size and 600), maxw, f.size, 11) if False else (f, 0)
    d.text((cx, cy), t, font=f, fill=fill, anchor="mm")

def blind_group(d, x0, y0, w, rows, rh, hf, cf):
    """블라인드 표 한 그룹. 헤더 반복 + zebra + BRK 풀폭 강조행."""
    cols = ["LV", "SB", "BB", "ANTE", "BLIND"]
    cw = [0.14, 0.215, 0.215, 0.20, 0.23]
    cen = []
    acc = 0
    for p in cw:
        cen.append(x0 + (acc + p / 2) * w); acc += p
    # 헤더
    d.rounded_rectangle([x0, y0, x0 + w, y0 + rh], radius=6, fill=(C["accent"][0], C["accent"][1], C["accent"][2], 235))
    for c, cx in zip(cols, cen):
        d.text((cx, y0 + rh / 2), c, font=hf, fill=(20, 10, 40), anchor="mm")
    y = y0 + rh + 2
    zi = 0
    for r in rows:
        if r[0] == "BRK":
            d.rounded_rectangle([x0, y, x0 + w, y + rh], radius=5, fill=C["break_bg"] + (210,))
            t = r[1]
            bff = cf
            if measure(t, bff)[0] > w - 16:
                bff, _ = fit_font(t, lambda s: noto(s, 700), w - 16, cf.size, 11)
            d.text((x0 + w / 2, y + rh / 2), t, font=bff, fill=C["text_hi"], anchor="mm")
        else:
            if zi % 2 == 0:
                d.rectangle([x0, y, x0 + w, y + rh], fill=(255, 255, 255, 12))
            vals = list(r)
            for i, (v, cx) in enumerate(zip(vals, cen)):
                fill = C["gold"] if i == 0 else C["text_lo"]
                fnt = cf
                if measure(v, fnt)[0] > w * cw[i] - 4:
                    fnt, _ = fit_font(v, lambda s: noto(s, 600), w * cw[i] - 4, cf.size, 10)
                d.text((cx, y + rh / 2), v, font=fnt, fill=fill, anchor="mm")
            zi += 1
        y += rh
    return y

def render(data, out="demo_B.png"):
    global C
    C = THEMES_B.get(data.get("theme","series_purple"), THEMES_B["series_purple"])
    img = bg(data.get("theme","series_purple")); d = ImageDraw.Draw(img, "RGBA")

    # ---- B0 로고 (TL) ----
    ly = SAFE_T + 6; es = 46
    d.rounded_rectangle([SAFE_L, ly, SAFE_L + es, ly + es], radius=12, outline=C["text_hi"], width=3)
    d.text((SAFE_L + es / 2, ly + es / 2 + 1), "PoD", font=anton(24), fill=C["text_hi"], anchor="mm")
    draw_ls(d, (SAFE_L + es + 14, ly + es / 2), "POKER of DREAMS", noto(20, 700), C["text_hi"], ls=2, anchor="lm")

    # ---- B1 시리즈 뱃지 (TR) ----
    draw_ls(d, (SAFE_R, ly + 2), data["series"], noto(30, 800), C["text_hi"], ls=3, anchor="ra")
    d.text((SAFE_R, ly + 40), data["total"], font=anton(26), fill=C["gold"], anchor="ra")
    draw_ls(d, (SAFE_R, ly + 74), "TOTAL GUARANTEED", noto(15, 500), C["mute"], ls=3, anchor="ra")

    # ---- B2 타이틀 (좌, 실버) ----
    ty = 168
    tf, _ = fit_font(data["title"], anton, CW * 0.74, 150, 96)
    ti, tw, th = text_img(data["title"], tf, (238, 240, 248), (146, 150, 172))
    img.alpha_composite(ti, (SAFE_L - 6, ty))
    # ---- B3 GTD (좌, 골드) ----
    gy = ty + th + 6
    gf, _ = fit_font(data["gtd"] + " GTD", anton, CW * 0.82, 92, 56)
    gi, gw, gh = text_img(data["gtd"] + " GTD", gf, (250, 222, 150), (204, 150, 58))
    img.alpha_composite(gi, (SAFE_L - 4, gy))

    # ---- B4 일시(좌) + 브랜드(우) ----
    dy = gy + gh + 16
    d.text((SAFE_L, dy), data["date"], font=noto(30, 700), fill=C["text_hi"], anchor="la")
    draw_ls(d, (SAFE_R, dy + 4), data["brand"], noto(30, 800), C["text_hi"], ls=2, anchor="ra")
    d.text((SAFE_R, dy + 40), "★ ★ ★ ★", font=noto(16, 700), fill=C["gold"], anchor="ra")

    # ---- B5 BUY-IN 박스(좌) + 스탯 4열(우) ----
    yb = dy + 78; boxh = 92
    # buy-in
    d.text((SAFE_L, yb - 2), "BUY-IN", font=noto(18, 700), fill=C["text_hi"], anchor="la")
    bw = 312
    d.rounded_rectangle([SAFE_L, yb + 24, SAFE_L + bw, yb + boxh], radius=10, fill=C["red"] + (240,))
    bf, _ = fit_font(data["buyin"], lambda s: noto(s, 800), bw - 24, 30, 18)
    d.text((SAFE_L + bw / 2, yb + 24 + (boxh - 24) / 2), data["buyin"], font=bf, fill=(255, 255, 255), anchor="mm")
    # stats 4열 (우측)
    sx0 = SAFE_L + bw + 22; sw = SAFE_R - sx0; n = len(data["stats"]); scw = sw / n
    for i, (lab, val) in enumerate(data["stats"]):
        cxx = sx0 + scw * (i + 0.5)
        if i: d.line([sx0 + scw * i, yb + 6, sx0 + scw * i, yb + boxh - 4], fill=C["line"] + (160,), width=1)
        lf, _ = fit_font(lab, lambda s: noto(s, 500), scw - 12, 17, 11)
        d.text((cxx, yb + 8), lab, font=lf, fill=C["accent_soft"], anchor="ma")
        vf, _ = fit_font(val, lambda s: noto(s, 800), scw - 12, 30, 14)
        d.text((cxx, yb + 40), val, font=vf, fill=C["text_hi"], anchor="ma")

    # ===== BODY: 좌 프라이즈 / 우 블라인드 =====
    body_y = yb + boxh + 30
    # 좌 컬럼
    lx, lw = SAFE_L, 350
    # 트로피 아이콘
    tcx = lx + lw / 2
    d.ellipse([tcx - 22, body_y, tcx + 22, body_y + 36], outline=C["gold"], width=3)
    d.arc([tcx - 34, body_y + 2, tcx - 18, body_y + 26], 90, 270, fill=C["gold"], width=3)
    d.arc([tcx + 18, body_y + 2, tcx + 34, body_y + 26], 270, 90, fill=C["gold"], width=3)
    d.line([tcx, body_y + 36, tcx, body_y + 46], fill=C["gold"], width=3)
    d.line([tcx - 14, body_y + 48, tcx + 14, body_y + 48], fill=C["gold"], width=4)
    draw_ls(d, (tcx, body_y + 58), "본 대회는 우승자에게 공식 트로피 수여", noto(14, 500), C["text_lo"], ls=0, anchor="ma")
    # 프라이즈 표 헤더
    pty = body_y + 86; prh = 31
    d.rounded_rectangle([lx, pty, lx + lw, pty + prh], radius=6, fill=C["accent"] + (235,))
    d.text((lx + lw * 0.30, pty + prh / 2), "RANK", font=noto(18, 800), fill=(20, 10, 40), anchor="mm")
    d.text((lx + lw * 0.74, pty + prh / 2), "PRIZE", font=noto(18, 800), fill=(20, 10, 40), anchor="mm")
    y = pty + prh + 2
    for i, (rk, pz) in enumerate(data["prizes"]):
        if i % 2 == 0: d.rectangle([lx, y, lx + lw, y + prh], fill=(255, 255, 255, 12))
        big = i < 3
        d.text((lx + lw * 0.30, y + prh / 2), rk, font=noto(17, 800 if big else 600),
               fill=C["gold"] if big else C["text_hi"], anchor="mm")
        d.text((lx + lw * 0.74, y + prh / 2), pz, font=noto(17, 800 if big else 600),
               fill=C["gold"] if big else C["text_lo"], anchor="mm")
        y += prh
    left_bottom = y

    # 우 컬럼: 블라인드 2-그룹
    rx = lx + lw + 24; rw = SAFE_R - rx
    gw = (rw - 18) / 2
    g1 = LV[:20]; g2 = LV[20:]
    hf = noto(16, 800); cf = noto(16, 600)
    rh = 30
    blind_group(d, rx, body_y, gw, g1, rh, hf, cf)
    right_bottom = blind_group(d, rx + gw + 18, body_y, gw, g2, rh, hf, cf)

    # ===== 하단: Notice / 스폰서 / 푸터 =====
    ny0 = max(left_bottom, right_bottom) + 24
    d.text((SAFE_L, ny0), "⚠  Notice for Player", font=noto(20, 700), fill=C["text_hi"], anchor="la")
    # 2-컬럼 불릿
    yy = ny0 + 34; colw = CW / 2; lh = 26
    half = (len(data["notice"]) + 1) // 2
    for ci, chunk in enumerate([data["notice"][:half], data["notice"][half:]]):
        bx = SAFE_L + ci * colw; yc = yy
        for line in chunk:
            f = noto(15, 400)
            if measure("· " + line, f)[0] > colw - 24:
                f, _ = fit_font("· " + line, lambda s: noto(s, 400), colw - 24, 15, 11)
            d.text((bx, yc), "·", font=f, fill=C["accent"], anchor="la")
            d.text((bx + 16, yc), line, font=f, fill=C["text_lo"], anchor="la"); yc += lh

    # 스폰서
    spy = SAFE_B - 96; sp = data["sponsors"]; m = len(sp); cw2 = CW / m
    d.line([SAFE_L, spy - 14, SAFE_R, spy - 14], fill=C["line"] + (170,), width=1)
    for i, (lab, name) in enumerate(sp):
        cxx = SAFE_L + cw2 * (i + 0.5)
        draw_ls(d, (cxx, spy), lab, noto(16, 600), C["accent_soft"], ls=2, anchor="ma")
        nf, _ = fit_font(name, lambda s: noto(s, 600), cw2 - 16, 22, 12)
        d.text((cxx, spy + 26), name, font=nf, fill=C["text_hi"], anchor="ma")
    # 푸터
    fy = SAFE_B - 30
    d.line([SAFE_L, fy - 12, SAFE_R, fy - 12], fill=C["line"] + (170,), width=1)
    nf = noto(22, 800); af = noto(20, 400)
    nmw = lsw(data["venue_name"], nf, 0); gap = 16
    fx = CX - (nmw + gap + measure(data["venue_addr"], af)[0]) / 2
    d.text((fx, fy + 6), data["venue_name"], font=nf, fill=C["text_hi"], anchor="la")
    d.text((fx + nmw + gap, fy + 8), data["venue_addr"], font=af, fill=C["text_lo"], anchor="la")

    img.convert("RGB").save(out, quality=95); print("saved", out, "bottom@", int(ny0))

if __name__ == "__main__":
    render(DATA, sys.argv[1] if len(sys.argv) > 1 else "demo_B.png")
