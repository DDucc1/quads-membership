#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홀덤 포스터 하네스 — 아키타입 A 렌더러 (1차 초안)
01_master-prompt.md 의 GRID SPEC / STEP4 오토핏 / 세이프존 규칙을 좌표로 구현.
입력(JSON)만 바꾸면 동일 골격으로 재현된다.
"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

# ---------- 캔버스 / 세이프존 (FIXED) ----------
W, H = 1080, 1800
SAFE_L = round(W * 0.06)      # 65
SAFE_R = W - SAFE_L           # 1015
SAFE_T = round(H * 0.03)      # 54
SAFE_B = H - SAFE_T           # 1746
CW = SAFE_R - SAFE_L          # 950 content width
CX = W // 2

ASSET = "assets/"
NOTO = ASSET + "NotoSansKR.ttf"
ANTON = ASSET + "Anton.ttf"

# ---------- 테마 토큰: flame_blue ----------
TH = dict(
    bg_top=(9, 16, 33), bg_bottom=(3, 6, 15),
    accent=(56, 189, 248), glow=(34, 211, 238), accent_deep=(14, 116, 178),
    text_hi=(238, 246, 255), text_lo=(150, 172, 198), text_mute=(110, 132, 158),
    panel=(13, 24, 44), line=(40, 70, 110),
)

# ---------- 폰트 ----------
def noto(size, weight=400):
    f = ImageFont.truetype(NOTO, size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f
def anton(size):
    return ImageFont.truetype(ANTON, size)

_scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))
def measure(text, font, ls=0):
    if ls == 0:
        b = _scratch.textbbox((0, 0), text, font=font)
        return b[2] - b[0], b[3] - b[1]
    w = sum(_scratch.textlength(ch, font=font) for ch in text) + ls * max(0, len(text) - 1)
    b = _scratch.textbbox((0, 0), text, font=font)
    return int(w), b[3] - b[1]

def fit_font(text, factory, max_w, start, min_size, ls=0):
    """STEP4 오토핏: max_w 넘으면 폰트 스텝다운(최저 min_size)."""
    s = start
    while s > min_size:
        f = factory(s)
        w, _ = measure(text, f, ls)
        if w <= max_w: return f, s
        s -= 2
    return factory(min_size), min_size

# ---------- 그리기 헬퍼 ----------
def draw_ls(draw, xy, text, font, fill, ls=0, anchor="la"):
    """자간(ls) 지원 텍스트. anchor의 첫 글자(l/m/r)로 정렬."""
    if ls == 0:
        draw.text(xy, text, font=font, fill=fill, anchor=anchor); return
    tw = sum(draw.textlength(ch, font=font) for ch in text) + ls * max(0, len(text) - 1)
    x, y = xy
    ha = anchor[0]
    if ha == "m": x -= tw / 2
    elif ha == "r": x -= tw
    va = anchor[1] if len(anchor) > 1 else "a"
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, anchor="l" + va)
        x += draw.textlength(ch, font=font) + ls

def text_img(text, font, fill_top, fill_bottom=None, pad=8):
    """텍스트를 RGBA 이미지로(세로 그라데이션 옵션). 반환: (img, w, h)."""
    b = _scratch.textbbox((0, 0), text, font=font)
    w, h = b[2] - b[0] + pad * 2, b[3] - b[1] + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - b[0], pad - b[1]), text, font=font, fill=255)
    if fill_bottom is None:
        col = Image.new("RGBA", (w, h), fill_top + (255,))
    else:
        grad = Image.new("RGBA", (1, h))
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = tuple(int(fill_top[i] * (1 - t) + fill_bottom[i] * t) for i in range(3))
            grad.putpixel((0, yy), c + (255,))
        col = grad.resize((w, h))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(col, (0, 0), mask)
    return out, w, h

def paste_center(base, img, cx, y_top):
    base.alpha_composite(img, (int(cx - img.width / 2), int(y_top)))

def radial(size, inner, outer, cx, cy, radius):
    img = Image.new("RGB", size, outer); d = ImageDraw.Draw(img)
    steps = 120
    for i in range(steps, 0, -1):
        t = i / steps; r = radius * t
        c = tuple(int(outer[k] * t + inner[k] * (1 - t)) for k in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    return img

# ================= 배경 =================
def build_bg():
    base = Image.new("RGB", (W, H)); d = ImageDraw.Draw(base)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(TH["bg_top"][i] * (1 - t) + TH["bg_bottom"][i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # 중앙 시안 플레임 글로우 (가독 위해 상단부에)
    glow = radial((W, H), TH["glow"], (0, 0, 0), CX, int(H * 0.30), int(W * 0.55))
    glow = glow.point(lambda v: int(v * 0.55))
    base = ImageChops.screen(base, glow)
    glow2 = radial((W, H), TH["accent_deep"], (0, 0, 0), CX, int(H * 0.30), int(W * 0.30))
    base = ImageChops.screen(base, glow2.point(lambda v: int(v * 0.6)))
    # 비네팅(가장자리 어둡게 → 세이프존 여백 강조 + 텍스트 대비)
    vig = radial((W, H), (255, 255, 255), (70, 70, 70), CX, int(H * 0.42), int(H * 0.62))
    base = ImageChops.multiply(base, vig)
    return base.convert("RGBA")

# ================= 콘텐츠(임의 게임내용) =================
DATA = {
  "theme": "flame_blue",
  "trophy": "본 대회는 우승자에게 공식 트로피가 수여됩니다",
  "logo": "POKER of DREAMS",
  "title": "CHALLENGE", "accent": "in 대전",
  "gtd": "30,000,000",
  "datetime": "26.07.04 (토요일) 오후 2시",
  "place": "대전 POD 스타디움",
  "buyin_label": "BUY-IN", "buyin": "1 Challenge Ticket",
  "stats": [("ENTRY", "120 Entry++"), ("STARTING", "60,000 Chips"),
            ("LATE REG", "16Lv 시작 전"), ("BLIND", "25/20 Mins")],
  "notice": [
      "최종 레지스트레이션은 레벨 16 시작 전까지 가능합니다.",
      "빅 블라인드 엔티 방식으로 진행됩니다.",
      "엔티는 토너먼트가 끝나기 전까지 줄지 않습니다.",
      "국제 TDA 규정을 준수합니다.",
      "테이블은 9max로 진행합니다.",
      "대회 참가자는 본인 신분증을 지참하여 본인 확인을 진행합니다.",
      "상금을 획득한 선수는 세금신고를 의무화 해야합니다.",
      "ENTRY NEW PLAYER CARD 지급 (첫 핸드에 사용 여부 체크)",
  ],
  "sponsors": [("주관사", "POKER of DREAMS"), ("협력사", "SEEDKET"),
               ("후원사", "MOXSYS · 한베교류발전위원회"), ("장소", "대전 POD 스타디움")],
  "footer_name": "대전 POD 스타디움",
  "footer_addr": "대전광역시 서구 둔산로 100, 5층",
}

# ================= 렌더 =================
def render(data, out="demo_A.png"):
    img = build_bg()
    d = ImageDraw.Draw(img)

    # ---- A0 트로피 뱃지 (top-left) ----
    by = SAFE_T + 6
    bf = noto(19, 450)
    bt = data["trophy"]
    pad_x, pad_y = 18, 11
    tw, th = measure(bt, bf)
    bh = th + pad_y * 2
    d.rounded_rectangle([SAFE_L, by, SAFE_L + tw + pad_x * 2, by + bh], radius=bh // 2,
                        fill=(255, 255, 255, 26), outline=TH["accent"] + (120,), width=1)
    # 작은 트로피 아이콘
    icx, icy = SAFE_L + pad_x + 6, by + bh // 2
    d.ellipse([icx - 6, icy - 7, icx + 6, icy + 3], outline=TH["accent"], width=2)
    d.line([icx, icy + 3, icx, icy + 7], fill=TH["accent"], width=2)
    d.line([icx - 4, icy + 7, icx + 4, icy + 7], fill=TH["accent"], width=2)
    d.text((SAFE_L + pad_x + 18, by + bh // 2), bt, font=bf, fill=TH["text_lo"], anchor="lm")

    # ---- A1 로고 (center) ----
    ly = 120
    # 엠블럼: 라운드 사각 + PoD
    es = 56
    d.rounded_rectangle([CX - es//2, ly, CX + es//2, ly + es], radius=14,
                        outline=TH["accent"], width=3)
    ef = anton(30)
    d.text((CX, ly + es//2 + 2), "PoD", font=ef, fill=TH["text_hi"], anchor="mm")
    draw_ls(d, (CX, ly + es + 14), data["logo"].upper(), noto(20, 600), TH["text_hi"], ls=4, anchor="ma")

    # ---- A2 히어로 타이틀 (center, 이탤릭 시어) ----
    ty = 256
    tf, _ = fit_font(data["title"], anton, CW - 40, 200, 110)
    ti, tw, thh = text_img(data["title"], tf, TH["text_hi"], (180, 224, 255))
    # 이탤릭 시어
    shear = 0.16
    ext = int(thh * shear)
    ti2 = Image.new("RGBA", (tw + ext, thh), (0, 0, 0, 0))
    ti2.paste(ti, (0, 0))
    ti2 = ti2.transform((tw + ext, thh), Image.AFFINE, (1, shear, -ext * 0.15, 0, 1, 0),
                        resample=Image.BICUBIC)
    # 글로우(대비 확보)
    glow = Image.new("RGBA", ti2.size, (0, 0, 0, 0))
    gm = ti2.split()[3]
    gcol = Image.new("RGBA", ti2.size, TH["glow"] + (255,))
    glow.paste(gcol, (0, 0), gm)
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    paste_center(img, glow, CX, ty - 2)
    paste_center(img, ti2, CX, ty)
    title_bottom = ty + thh
    # 악센트 "in 대전" (타이틀 우상단, 글자 충돌 방지 위해 타이틀 상단 위로)
    if data.get("accent"):
        af = noto(38, 700)
        aw, ah = measure(data["accent"], af)
        ax = min(SAFE_R - aw, CX + tw / 2 - aw + 10)
        d.text((ax, ty - 34), data["accent"], font=af, fill=TH["accent"], anchor="la")

    # ---- A3 GTD (center) ----
    gy = title_bottom + 18
    gtxt = data["gtd"]
    gf, gsz = fit_font(gtxt, anton, CW - 200, 116, 70)
    gi, gw, gh = text_img(gtxt, gf, (255, 255, 255), (150, 210, 255))
    sf = anton(int(gsz * 0.42))
    sw, sh = measure(" GTD", sf)
    total = gw + sw + 8
    x0 = CX - total / 2
    img.alpha_composite(gi, (int(x0), int(gy)))
    d.text((x0 + gw + 8, gy + gh - sh - 6), "GTD", font=sf, fill=TH["accent"], anchor="la")
    gtd_bottom = gy + gh

    # ---- A4 일시 / 장소 (center) ----
    dy = max(gtd_bottom + 34, 640)
    d.text((CX, dy), data["datetime"], font=noto(34, 500), fill=TH["text_lo"], anchor="ma")
    pf, _ = fit_font(data["place"], lambda s: noto(s, 800), CW - 80, 52, 34)
    d.text((CX, dy + 52), data["place"], font=pf, fill=TH["text_hi"], anchor="ma")

    # ---- A5 BUY-IN (center) ----
    byy = 812
    draw_ls(d, (CX, byy), data["buyin_label"], noto(26, 700), TH["accent"], ls=6, anchor="ma")
    bf2, _ = fit_font(data["buyin"], lambda s: noto(s, 800), CW - 80, 62, 38)
    d.text((CX, byy + 44), data["buyin"], font=bf2, fill=TH["text_hi"], anchor="ma")

    # ---- A6 스탯 4열 (FIXED: 빈 열 제거 후 재균등) ----
    stats = [s for s in data["stats"] if s[1]]
    sy0, sh_band = 966, 150
    d.rounded_rectangle([SAFE_L, sy0, SAFE_R, sy0 + sh_band], radius=18,
                        fill=TH["panel"] + (235,), outline=TH["line"] + (255,), width=1)
    n = len(stats); colw = CW / n
    lab_f = noto(22, 500)
    for i, (lab, val) in enumerate(stats):
        cxx = SAFE_L + colw * (i + 0.5)
        if i > 0:
            d.line([SAFE_L + colw * i, sy0 + 28, SAFE_L + colw * i, sy0 + sh_band - 28],
                   fill=TH["line"], width=1)
        d.text((cxx, sy0 + 34), lab, font=lab_f, fill=TH["text_lo"], anchor="ma")
        vf, _ = fit_font(val, lambda s: noto(s, 800), colw - 28, 40, 22)
        d.text((cxx, sy0 + 78), val, font=vf, fill=TH["text_hi"], anchor="ma")

    # ---- A7 Notice 박스 ----
    ny0 = sy0 + sh_band + 34
    ny1 = 1556
    d.rounded_rectangle([SAFE_L, ny0, SAFE_R, ny1], radius=18,
                        fill=(8, 16, 30, 210), outline=TH["line"] + (255,), width=1)
    # 헤더(경고 삼각형 + 텍스트)
    hf = noto(30, 700)
    htxt = "Notice for Player"
    hw, hh = measure(htxt, hf)
    tri_w = 30
    total_h = tri_w + 12 + hw
    hx = CX - total_h / 2
    hcy = ny0 + 36
    d.polygon([(hx, hcy + 13), (hx + tri_w, hcy + 13), (hx + tri_w / 2, hcy - 14)],
              outline=TH["accent"], width=2)
    d.text((hx + tri_w / 2, hcy + 4), "!", font=noto(20, 800), fill=TH["accent"], anchor="mm")
    d.text((hx + tri_w + 12, hcy), htxt, font=hf, fill=TH["text_hi"], anchor="lm")
    # 불릿
    bf3 = noto(23, 400)
    bx = SAFE_L + 34
    line_h = 34
    yy = ny0 + 78
    maxw = CW - 68
    for line in data["notice"]:
        f = bf3
        if measure("· " + line, f)[0] > maxw:
            f, _ = fit_font("· " + line, lambda s: noto(s, 400), maxw, 23, 18)
        d.text((bx, yy), "·", font=f, fill=TH["accent"], anchor="la")
        d.text((bx + 22, yy), line, font=f, fill=TH["text_lo"], anchor="la")
        yy += line_h

    # ---- A8 스폰서 바 (4구역) ----
    spy = ny1 + 34
    sp = data["sponsors"]; m = len(sp); cw2 = CW / m
    d.line([SAFE_L, spy - 12, SAFE_R, spy - 12], fill=TH["line"], width=1)
    for i, (lab, name) in enumerate(sp):
        cxx = SAFE_L + cw2 * (i + 0.5)
        draw_ls(d, (cxx, spy), lab, noto(18, 600), TH["accent"], ls=2, anchor="ma")
        nf, _ = fit_font(name, lambda s: noto(s, 600), cw2 - 16, 24, 13)
        d.text((cxx, spy + 30), name, font=nf, fill=TH["text_hi"], anchor="ma")

    # ---- A9 푸터 ----
    fy = SAFE_B - 36
    d.line([SAFE_L, fy - 14, SAFE_R, fy - 14], fill=TH["line"], width=1)
    nf = noto(24, 800); af = noto(22, 400)
    nm = data["footer_name"]; ad = "   " + data["footer_addr"]
    nmw = measure(nm, nf)[0]; adw = measure(ad, af)[0]
    fx = CX - (nmw + adw) / 2
    d.text((fx, fy + 6), nm, font=nf, fill=TH["text_hi"], anchor="la")
    d.text((fx + nmw, fy + 8), ad, font=af, fill=TH["text_lo"], anchor="la")

    img.convert("RGB").save(out, quality=95)
    print("saved", out)

if __name__ == "__main__":
    render(DATA, sys.argv[1] if len(sys.argv) > 1 else "demo_A.png")
