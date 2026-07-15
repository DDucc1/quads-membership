#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홀덤 포스터 하네스 — 아키타입 A 렌더러
01_master-prompt.md GRID SPEC / STEP4 오토핏 / 세이프존 구현 + 절차적 배경 합성.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

W, H = 1080, 1800
SAFE_L = round(W * 0.06); SAFE_R = W - SAFE_L
SAFE_T = round(H * 0.03); SAFE_B = H - SAFE_T
CW = SAFE_R - SAFE_L; CX = W // 2

ASSET = "assets/"; NOTO = ASSET + "NotoSansKR.ttf"; ANTON = ASSET + "Anton.ttf"

THEMES = {
  "flame_blue":  dict(accent=(80,200,252), accent_soft=(150,220,255), text_hi=(240,247,255),
                      text_lo=(176,196,220), line=(58,92,134), title_lo=(188,226,255),
                      glow=(20,90,150), gtd_lo=(165,215,255)),
  "ocean_teal":  dict(accent=(58,214,192), accent_soft=(150,238,222), text_hi=(238,252,248),
                      text_lo=(178,214,204), line=(40,108,98), title_lo=(168,236,222),
                      glow=(14,118,104), gtd_lo=(150,236,216)),
  "space_blue":  dict(accent=(96,156,250), accent_soft=(166,198,255), text_hi=(238,243,255),
                      text_lo=(182,196,226), line=(50,72,132), title_lo=(182,206,255),
                      glow=(28,72,162), gtd_lo=(172,202,255)),
  "golden_door": dict(accent=(245,196,92), accent_soft=(255,222,150), text_hi=(250,245,236),
                      text_lo=(212,196,170), line=(112,90,52), title_lo=(250,226,160),
                      glow=(140,98,28), gtd_lo=(250,212,122)),
  "series_red":  dict(accent=(242,84,82), accent_soft=(255,152,142), text_hi=(251,240,240),
                      text_lo=(216,186,186), line=(122,52,56), title_lo=(255,182,172),
                      glow=(140,30,34), gtd_lo=(255,162,150)),
}
TH = THEMES["flame_blue"]

# 임의 테마 → accent 색에서 팔레트 자동 유도 (20테마 지원)
try:
    from bg_generate import THEME_ACCENT
except Exception:
    THEME_ACCENT = {}
def _mix(c, d, t): return tuple(int(c[i] * (1 - t) + d[i] * t) for i in range(3))
def palette(acc):
    Wt = (255, 255, 255)
    return dict(accent=acc, accent_soft=_mix(acc, Wt, 0.45),
                text_hi=_mix(Wt, acc, 0.05), text_lo=_mix((205, 210, 220), acc, 0.14),
                line=_mix(tuple(int(x * 0.4) for x in acc), (44, 50, 66), 0.4),
                title_lo=_mix(acc, Wt, 0.55), glow=tuple(int(x * 0.45) for x in acc),
                gtd_lo=_mix(acc, Wt, 0.48))
def theme_palette(name):
    if name in THEMES: return THEMES[name]
    if name in THEME_ACCENT: return palette(THEME_ACCENT[name])
    return THEMES["flame_blue"]

def noto(size, weight=400):
    f = ImageFont.truetype(NOTO, size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f
def anton(size): return ImageFont.truetype(ANTON, size)

_sc = ImageDraw.Draw(Image.new("RGB", (4, 4)))
def measure(t, f):
    b = _sc.textbbox((0, 0), t, font=f); return b[2] - b[0], b[3] - b[1]
def fit_font(t, fac, max_w, start, mn):
    s = start
    while s > mn:
        if measure(t, fac(s))[0] <= max_w: return fac(s), s
        s -= 2
    return fac(mn), mn
def theight(t, f):
    """anchor='la'로 그렸을 때 실제 차지하는 세로 끝(y). measure()는 타이트박스라
    어센더 오프셋을 놓쳐 아래 요소와 겹침을 유발한다 — 간격 계산은 반드시 이걸 쓴다."""
    b = _sc.textbbox((0, 0), t, font=f)
    return b[3]
def lsw(t, f, ls):
    return sum(_sc.textlength(c, font=f) for c in t) + ls * max(0, len(t) - 1)
def draw_ls(d, xy, t, f, fill, ls=0, anchor="la"):
    if ls == 0: d.text(xy, t, font=f, fill=fill, anchor=anchor); return
    x, y = xy; ha = anchor[0]; va = anchor[1] if len(anchor) > 1 else "a"
    tw = lsw(t, f, ls)
    if ha == "m": x -= tw / 2
    elif ha == "r": x -= tw
    for c in t:
        d.text((x, y), c, font=f, fill=fill, anchor="l" + va); x += _sc.textlength(c, font=f) + ls

def text_img(t, f, top, bottom=None, pad=10):
    b = _sc.textbbox((0, 0), t, font=f); w, h = b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((pad - b[0], pad - b[1]), t, font=f, fill=255)
    if bottom is None:
        col = Image.new("RGBA", (w, h), top + (255,))
    else:
        g = Image.new("RGBA", (1, h))
        for y in range(h):
            tt = y / max(1, h - 1)
            g.putpixel((0, y), tuple(int(top[i] * (1 - tt) + bottom[i] * tt) for i in range(3)) + (255,))
        col = g.resize((w, h))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(col, (0, 0), m)
    return out, w, h

def shear_img(im, k=0.16):
    ext = int(im.height * k)
    cv = Image.new("RGBA", (im.width + ext, im.height), (0, 0, 0, 0)); cv.paste(im, (0, 0))
    return cv.transform((im.width + ext, im.height), Image.AFFINE, (1, k, -ext * 0.12, 0, 1, 0), resample=Image.BICUBIC)

def place(base, im, cx, y, shadow=True, glow_col=None):
    """텍스트 이미지 합성 — 가독용 다크 섀도 + 선택적 컬러 글로우."""
    x = int(cx - im.width / 2)
    a = im.split()[3]
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", im.size, (0, 6, 14, 255)), (0, 0), a)
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        base.alpha_composite(sh, (x, int(y) + 3)); base.alpha_composite(sh, (x, int(y) + 3))
    if glow_col:
        gl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        gl.paste(Image.new("RGBA", im.size, glow_col + (255,)), (0, 0), a)
        gl = gl.filter(ImageFilter.GaussianBlur(10)); base.alpha_composite(gl, (x, int(y)))
    base.alpha_composite(im, (x, int(y)))

# ---------- 배경 ----------
def build_bg(theme):
    p = f"{ASSET}bg/{theme}.jpg"
    if os.path.exists(p):
        bg = Image.open(p).convert("RGB").resize((W, H))
        bg = bg.point(lambda v: int(v * 0.80))          # 불꽃 전체 톤 다운(대비 여유)
        bg = bg.convert("RGBA")
    else:
        bg = Image.new("RGBA", (W, H), (6, 10, 22, 255))
    # 상단/하단 스크림(로고·정보 영역 대비)
    top = Image.new("L", (1, H), 0)
    for y in range(H):
        t = y / H; v = 0
        if t < 0.12: v = int(160 * (1 - t / 0.12))                 # 상단
        if t > 0.50: v = int(min(232, 232 * (t - 0.50) / 0.40))    # 하단 정보영역
        top.putpixel((0, y), v)
    scrim = Image.new("RGBA", (W, H), (3, 7, 16, 255)); scrim.putalpha(top.resize((W, H)))
    bg.alpha_composite(scrim)
    # 히어로~BUY-IN 텍스트 뒤 다크 스크림(밝은 불꽃 위 흰 글자 가독) — 세로로 길게
    hs = Image.new("L", (W, H), 0); hd = ImageDraw.Draw(hs)
    hd.ellipse([CX - 560, 150, CX + 560, 900], fill=135)
    hs = hs.filter(ImageFilter.GaussianBlur(95))
    hsc = Image.new("RGBA", (W, H), (2, 6, 14, 255)); hsc.putalpha(hs)
    bg.alpha_composite(hsc)
    # QP8 마감: 미세 필름 그레인 (밴딩 방지·질감)
    grain = Image.effect_noise((W, H), 22).convert("L")
    g = Image.merge("RGBA", (grain, grain, grain, Image.new("L", (W, H), 8)))
    bg.alpha_composite(g)
    return bg

# ---------- 콘텐츠(임의) ----------
DATA = {
  "theme": "flame_blue",
  "trophy": "공식 트로피 수여",
  "logo": "POKER of DREAMS",
  "title": "CHALLENGE", "accent": "in 대전",
  "gtd": "30,000,000",
  "date": "26.07.04 (토요일) 오후 2시", "place": "대전 POD 스타디움",
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
               ("후원사", "MOXSYS"), ("장소", "대전 POD 스타디움")],
  "footer_name": "대전 POD 스타디움", "footer_addr": "대전광역시 서구 둔산로 100, 5층",
}

def rule(d, cx, y, w, col, h=3):
    d.rounded_rectangle([cx - w / 2, y, cx + w / 2, y + h], radius=h / 2, fill=col)

# ===== 디자인 디바이스 (QP7) =====
def corner_frame(d, col, arm=52, off=6, w=3):
    L, R, T, B = SAFE_L + off, SAFE_R - off, SAFE_T + off, SAFE_B - off
    for x, y, sx, sy in [(L, T, 1, 1), (R, T, -1, 1), (L, B, 1, -1), (R, B, -1, -1)]:
        d.line([(x, y), (x + sx * arm, y)], fill=col, width=w)
        d.line([(x, y), (x, y + sy * arm)], fill=col, width=w)

def suit_divider(d, cx, y, w, col):
    g, s = 22, 11
    d.line([(cx - w / 2, y), (cx - g, y)], fill=col, width=2)
    d.line([(cx + g, y), (cx + w / 2, y)], fill=col, width=2)
    d.polygon([(cx, y - s), (cx + s * 0.72, y), (cx, y + s), (cx - s * 0.72, y)], fill=col)

def ribbon(d, cx, cy, w, h, fill, outline):
    n = h * 0.42
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    pts = [(x0, y0), (x1, y0), (x1 + n, cy), (x1, y1), (x0, y1), (x0 - n, cy)]
    d.polygon(pts, fill=fill); d.line(pts + [pts[0]], fill=outline, width=2)
    # 끝단 작은 접힘
    d.polygon([(x0 - n, cy), (x0 - n + 8, cy - 6), (x0 - n + 8, cy + 6)], fill=outline)
    d.polygon([(x1 + n, cy), (x1 + n - 8, cy - 6), (x1 + n - 8, cy + 6)], fill=outline)

def render(data, out="demo_A.png"):
    global TH
    TH = theme_palette(data.get("theme","flame_blue"))
    img = build_bg(data["theme"]); d = ImageDraw.Draw(img, "RGBA")

    # QP7 코너 프레임 (프리미엄 프레이밍)
    corner_frame(d, TH["accent"] + (175,))

    # A0 트로피 뱃지
    by = SAFE_T + 8; bf = noto(18, 500)
    bt = data["trophy"]; tw, th = measure(bt, bf); px, py = 16, 9; bh = th + py * 2
    d.rounded_rectangle([SAFE_L, by, SAFE_L + tw + px * 2 + 20, by + bh], radius=bh / 2,
                        fill=(255, 255, 255, 22), outline=TH["accent"] + (110,), width=1)
    ix, iy = SAFE_L + px + 4, by + bh / 2
    d.ellipse([ix - 5, iy - 6, ix + 5, iy + 2], outline=TH["accent"], width=2)
    d.line([ix, iy + 2, ix, iy + 6], fill=TH["accent"], width=2)
    d.line([ix - 3, iy + 6, ix + 3, iy + 6], fill=TH["accent"], width=2)
    d.text((SAFE_L + px + 16, by + bh / 2), bt, font=bf, fill=TH["text_lo"], anchor="lm")

    # A1 로고
    ly = 118; es = 50
    d.rounded_rectangle([CX - es / 2, ly, CX + es / 2, ly + es], radius=13, outline=TH["accent"], width=3)
    d.text((CX, ly + es / 2 + 1), "PoD", font=anton(27), fill=TH["text_hi"], anchor="mm")
    draw_ls(d, (CX, ly + es + 13), data["logo"].upper(), noto(18, 600), TH["accent_soft"], ls=5, anchor="ma")

    # ===== HERO =====
    # A2 타이틀 (크게, 이탤릭 시어) — 위계 대비 강화
    tf, _ = fit_font(data["title"], anton, CW - 30, 215, 120)
    ti, tw, thh = text_img(data["title"], tf, TH["text_hi"], TH["title_lo"])
    ti = shear_img(ti, 0.15)
    ty = 244
    place(img, ti, CX, ty, shadow=True, glow_col=TH["glow"])
    # 악센트 (타이틀 상단 위, 명확한 갭)
    if data.get("accent"):
        af = noto(40, 700); aw, ah = measure(data["accent"], af)
        ax = min(SAFE_R - aw, CX + tw / 2 - aw + 18)
        d.text((ax, ty - 40), data["accent"], font=af, fill=TH["accent"], anchor="la")
    htb = ty + thh

    # A3 GTD (상금 = 머니 포커스. 크게 + 글로우로 한눈에)
    gy = htb - 4
    gf, gsz = fit_font(data["gtd"], anton, CW - 170, 138, 88)
    gi, gw, gh = text_img(data["gtd"], gf, (255, 255, 255), TH["gtd_lo"])
    sf = anton(int(gsz * 0.38)); sw, _ = measure("GTD", sf)
    tot = gw + sw + 16; x0 = CX - tot / 2
    place(img, gi, x0 + gw / 2, gy, shadow=True, glow_col=TH["glow"])
    d.text((x0 + gw + 16, gy + gh * 0.32), "GTD", font=sf, fill=TH["accent"], anchor="lm")
    # 히어로 구분 디바이더(다이아 모티프)
    suit_divider(d, CX, gy + gh + 18, 150, TH["accent"] + (235,))

    # ===== INFO (수직 리듬 차등: 정보부는 더 촘촘) =====
    # A4 일시/장소
    dy = gy + gh + 52
    draw_ls(d, (CX, dy), data["date"], noto(31, 500), TH["text_lo"], ls=1, anchor="ma")
    pf, _ = fit_font(data["place"], lambda s: noto(s, 800), CW - 80, 50, 32)
    d.text((CX, dy + 46), data["place"], font=pf, fill=TH["text_hi"], anchor="ma")

    # A5 BUY-IN (리본 배너로 강조)
    yb = dy + 122
    draw_ls(d, (CX, yb), data["buyin_label"], noto(22, 700), TH["accent"], ls=9, anchor="ma")
    bf2, _ = fit_font(data["buyin"], lambda s: noto(s, 800), CW - 300, 46, 30)
    rcy = yb + 64; rbw = measure(data["buyin"], bf2)[0] + 76; rbh = measure(data["buyin"], bf2)[1] + 30
    ribbon(d, CX, rcy, min(rbw, CW - 120), rbh, fill=TH["glow"] + (236,), outline=TH["accent"] + (255,))
    d.text((CX, rcy), data["buyin"], font=bf2, fill=TH["text_hi"], anchor="mm")

    # A6 스탯 4열 — 가벼운 헤어라인 패널(딱딱함 완화)
    stats = [s for s in data["stats"] if s[1]]
    sy = yb + 128; bandh = 138
    d.rounded_rectangle([SAFE_L, sy, SAFE_R, sy + bandh], radius=16, fill=(9, 18, 34, 200))
    d.line([SAFE_L + 20, sy, SAFE_R - 20, sy], fill=TH["accent"] + (210,), width=2)
    n = len(stats); colw = CW / n
    for i, (lab, val) in enumerate(stats):
        cxx = SAFE_L + colw * (i + 0.5)
        if i: d.line([SAFE_L + colw * i, sy + 30, SAFE_L + colw * i, sy + bandh - 30], fill=TH["line"] + (160,), width=1)
        draw_ls(d, (cxx, sy + 30), lab, noto(20, 500), TH["accent_soft"], ls=2, anchor="ma")
        vf, _ = fit_font(val, lambda s: noto(s, 800), colw - 26, 38, 21)
        d.text((cxx, sy + 70), val, font=vf, fill=TH["text_hi"], anchor="ma")

    # A7 Notice — 가벼운 박스
    ny0 = sy + bandh + 30; ny1 = 1556
    d.rounded_rectangle([SAFE_L, ny0, SAFE_R, ny1], radius=16, fill=(6, 13, 26, 200), outline=TH["line"] + (150,), width=1)
    hf = noto(28, 700); htxt = "Notice for Player"; hw, _ = measure(htxt, hf)
    tw2 = 28; total = tw2 + 12 + hw; hx = CX - total / 2; hcy = ny0 + 34
    d.polygon([(hx, hcy + 12), (hx + tw2, hcy + 12), (hx + tw2 / 2, hcy - 13)], outline=TH["accent"], width=2)
    d.text((hx + tw2 / 2, hcy + 3), "!", font=noto(18, 800), fill=TH["accent"], anchor="mm")
    d.text((hx + tw2 + 12, hcy), htxt, font=hf, fill=TH["text_hi"], anchor="lm")
    bx = SAFE_L + 34; yy = ny0 + 74; lh = 33; maxw = CW - 70
    for line in data["notice"]:
        f = noto(22, 400)
        if measure("· " + line, f)[0] > maxw: f, _ = fit_font("· " + line, lambda s: noto(s, 400), maxw, 22, 17)
        d.text((bx, yy), "·", font=f, fill=TH["accent"], anchor="la")
        d.text((bx + 20, yy), line, font=f, fill=TH["text_lo"], anchor="la"); yy += lh

    # A8 스폰서
    spy = ny1 + 36; sp = data["sponsors"]; m = len(sp); cw2 = CW / m
    d.line([SAFE_L, spy - 14, SAFE_R, spy - 14], fill=TH["line"] + (160,), width=1)
    for i, (lab, name) in enumerate(sp):
        cxx = SAFE_L + cw2 * (i + 0.5)
        draw_ls(d, (cxx, spy), lab, noto(17, 600), TH["accent"], ls=2, anchor="ma")
        nf, _ = fit_font(name, lambda s: noto(s, 600), cw2 - 16, 22, 12)
        d.text((cxx, spy + 28), name, font=nf, fill=TH["text_hi"], anchor="ma")

    # A9 푸터
    fy = SAFE_B - 30
    d.line([SAFE_L, fy - 12, SAFE_R, fy - 12], fill=TH["line"] + (160,), width=1)
    nf = noto(23, 800); af = noto(21, 400)
    nm = data["footer_name"]; ad = data["footer_addr"]
    nmw = lsw(nm, nf, 0); gap = 18; adw = measure(ad, af)[0]
    fx = CX - (nmw + gap + adw) / 2
    d.text((fx, fy + 6), nm, font=nf, fill=TH["text_hi"], anchor="la")
    d.text((fx + nmw + gap, fy + 8), ad, font=af, fill=TH["text_lo"], anchor="la")

    img.convert("RGB").save(out, quality=95); print("saved", out)

if __name__ == "__main__":
    render(DATA, sys.argv[1] if len(sys.argv) > 1 else "demo_A.png")
