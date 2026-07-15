#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홀덤 포스터 — 에디토리얼 크래프트 v2 (A형) + 공용 크래프트 툴킷.
타이포: Bebas Neue / Oswald(영문 디스플레이) + Noto(한글). 텍스처: 라이트릭·스캔라인·그레인.
B/C 렌더러는 이 모듈의 헬퍼를 import 한다.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont, ImageChops
from render_poster import noto, measure, fit_font, fit_common, draw_ls, lsw, text_img, theight, theme_palette, ASSET

W, H = 1080, 1800
# QC 규격: 세이프존(좌 6%=65px) 안에 레일 텍스트까지 들어오도록 마진 재배치
ML, MR, RAILX, SAFE_B = 124, W - 70, 70, H - 54

# ---------- 폰트 ----------
def bebas(s): return ImageFont.truetype(ASSET + "BebasNeue.ttf", s)
def _var(path, s, axes):
    f = ImageFont.truetype(path, s)
    try: f.set_variation_by_axes(axes)
    except Exception: pass
    return f
def oswald(s, w=500): return _var(ASSET + "Oswald.ttf", s, [w])
def playfair(s, w=700): return _var(ASSET + "Playfair.ttf", s, [w])

# ---------- 텍스처/그레이딩 ----------
def grade(bg, acc, leak_xy=(0.82, 0.12)):
    Wd, Hd = bg.size
    base = ImageEnhance.Color(bg.convert("RGB")).enhance(1.16)
    base = ImageEnhance.Contrast(base).enhance(1.12)
    base = ImageEnhance.Brightness(base).enhance(0.78)
    img = base.convert("RGBA")
    col = Image.new("L", (1, Hd), 0)
    for y in range(Hd):
        col.putpixel((0, y), int(248 * max(0, (y / Hd - 0.32) / 0.68) ** 1.3))
    dk = Image.new("RGBA", (Wd, Hd), (2, 4, 9, 255)); dk.putalpha(col.resize((Wd, Hd)))
    img.alpha_composite(dk)
    lk = Image.new("L", (Wd, Hd), 0)
    lx, ly = int(Wd * leak_xy[0]), int(Hd * leak_xy[1])
    ImageDraw.Draw(lk).ellipse([lx - 360, ly - 360, lx + 360, ly + 360], fill=120)
    lk = lk.filter(ImageFilter.GaussianBlur(150))
    leak = Image.new("RGBA", (Wd, Hd), acc + (255,)); leak.putalpha(lk)
    img = Image.alpha_composite(img, leak)
    gl = Image.new("L", (Wd, Hd), 0); ImageDraw.Draw(gl).ellipse([-340, -420, 520, 380], fill=46)
    gl = gl.filter(ImageFilter.GaussianBlur(130))
    t2 = Image.new("RGBA", (Wd, Hd), acc + (255,)); t2.putalpha(gl)
    img = Image.alpha_composite(img, t2)
    sl = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); sd = ImageDraw.Draw(sl)
    for y in range(0, Hd, 3): sd.line([(0, y), (Wd, y)], fill=(0, 0, 0, 12), width=1)
    img.alpha_composite(sl)
    grain = Image.effect_noise((Wd, Hd), 22).convert("L")
    img.alpha_composite(Image.merge("RGBA", (grain, grain, grain, Image.new("L", (Wd, Hd), 10))))
    return img

def rect_blend(img, box, fill, radius=0):
    """RGBA 캔버스에 '진짜 반투명' 사각형. (ImageDraw.rectangle은 알파를 SET해서
    반투명 의도가 불투명으로 찍힌다 — zebra/강조행은 반드시 이걸로 그린다.)"""
    x0, y0, x1, y1 = map(int, box)
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    if radius:
        od.rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=fill)
    else:
        od.rectangle([0, 0, w - 1, h - 1], fill=fill)
    img.alpha_composite(ov, (x0, y0))

def spade(d, cx, cy, r, fill):
    d.pieslice([cx - r, cy - r, cx, cy + r * 0.2], 0, 360, fill=fill)
    d.pieslice([cx, cy - r, cx + r, cy + r * 0.2], 0, 360, fill=fill)
    d.polygon([(cx, cy - r * 1.25), (cx + r, cy + r * 0.1), (cx - r, cy + r * 0.1)], fill=fill)
    d.polygon([(cx - r * 0.08, cy), (cx + r * 0.08, cy), (cx + r * 0.3, cy + r * 0.7),
               (cx - r * 0.3, cy + r * 0.7)], fill=fill)

def frost(img, box, radius, acc, alpha=140, tab=True):
    x0, y0, x1, y1 = map(int, box)
    reg = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(17))
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], radius, fill=255)
    img.paste(reg, (x0, y0), m)
    panel = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], radius,
                                            fill=(8, 12, 22, alpha), outline=(255, 255, 255, 26), width=1)
    img.alpha_composite(panel, (x0, y0))
    if tab:
        ImageDraw.Draw(img, "RGBA").rectangle([x0, y0 + 18, x0 + 4, y0 + 70], fill=acc + (255,))

def vtext(text, font, fill, ls=3):
    w = int(lsw(text, font, ls)) + 10; h = measure(text, font)[1] + 12
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ls(ImageDraw.Draw(im), (5, 4), text, font, fill, ls, "la")
    return im.rotate(90, expand=True)

def hero_scrim(img, focus="left"):
    """업로드 사진(동물/자연) 위 텍스트 가독용 적응형 스크림. 상단+좌측 어둡게."""
    Wd, Hd = img.size
    m = Image.new("L", (Wd, Hd), 0); md = ImageDraw.Draw(m)
    for y in range(Hd):
        t = y / Hd
        top = max(0, 1 - t / 0.52) * 150        # 상단(타이틀/머니)
        md.line([(0, y), (Wd, y)], fill=int(top))
    # 좌측 가중(히어로 텍스트가 좌측)
    lm = Image.new("L", (Wd, Hd), 0); ld = ImageDraw.Draw(lm)
    for x in range(Wd):
        ld.line([(x, 0), (x, Hd)], fill=int(max(0, 1 - x / (Wd * 0.62)) * 120))
    m = ImageChops.lighter(m, lm)
    sc = Image.new("RGBA", (Wd, Hd), (2, 4, 9, 255)); sc.putalpha(m.filter(ImageFilter.GaussianBlur(40)))
    img.alpha_composite(sc); return img

def base_bg(data, TH):
    hero = data.get("hero_image")
    if hero and os.path.exists(hero):
        im = Image.open(hero).convert("RGB"); s = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * s), int(im.height * s)))
        x = (im.width - W) // 2; y = (im.height - H) // 2
        bg = im.crop((x, y, x + W, y + H)).convert("RGBA")
        return hero_scrim(grade(bg, TH["accent"]))
    p = f"{ASSET}bg/{data['theme']}.jpg"
    bg = Image.open(p).convert("RGB").resize((W, H)).convert("RGBA") if os.path.exists(p) \
        else Image.new("RGBA", (W, H), (8, 10, 20, 255))
    return grade(bg, TH["accent"])

def render(data, out="demo_E.png"):
    TH = theme_palette(data.get("theme", "flame_blue"))
    acc, soft, hi, lo = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"]
    img = base_bg(data, TH); d = ImageDraw.Draw(img, "RGBA")

    gw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spade(ImageDraw.Draw(gw), int(W * 0.83), int(H * 0.60), 350, acc + (24,))
    img.alpha_composite(gw.filter(ImageFilter.GaussianBlur(2)))

    d.line([(RAILX, 250), (RAILX, 1500)], fill=acc + (110,), width=2)
    rt = vtext(f"POKER OF DREAMS — {data.get('rail','TOURNAMENT')}", oswald(15, 600), soft + (210,), ls=4)
    img.alpha_composite(rt, (RAILX + 8, 250))
    # 인덱스 번호(디자인 디테일)
    d.text((RAILX + 8, 1540), data.get("idx", "01"), font=bebas(40), fill=acc + (200,), anchor="lm")

    # 상단바
    d.text((ML, 80), "PoD", font=bebas(40), fill=hi, anchor="lm")
    draw_ls(d, (ML + 70, 80), "POKER OF DREAMS", oswald(16, 600), lo, ls=3, anchor="lm")
    draw_ls(d, (MR, 80), data.get("date_short", "26.07.04 SAT"), oswald(16, 500), soft, ls=4, anchor="rm")
    d.line([(ML, 120), (MR, 120)], fill=(255, 255, 255, 38), width=1)

    # HERO
    ky = 252
    d.line([(ML, ky), (ML + 46, ky)], fill=acc, width=3)
    draw_ls(d, (ML + 58, ky), data.get("kicker", "GUARANTEED TOURNAMENT"), oswald(16, 600), acc, ls=5, anchor="lm")
    ey = 280
    ef, _ = fit_font(data["title"], lambda s: bebas(s), MR - ML - 170, 116, 70)
    d.text((ML, ey), data["title"], font=ef, fill=hi, anchor="la")
    ew, eh = measure(data["title"], ef)
    if data.get("accent"):
        d.text((ML + ew + 22, ey + eh * 0.30), data["accent"], font=noto(34, 500), fill=acc, anchor="la")
    gy = ey + theight(data["title"], ef) + 24   # 어센더 포함 실높이 기준(겹침 방지)
    draw_ls(d, (ML + 3, gy), "TOTAL GUARANTEED", oswald(20, 600), lo, ls=6, anchor="la")
    my = gy + theight("TOTAL GUARANTEED", oswald(20, 600)) + 8
    mf, msz = fit_font(data["gtd"], lambda s: bebas(s), MR - ML - 120, 210, 120)
    mi, mw, mh = text_img(data["gtd"], mf, (255, 255, 255), TH["gtd_lo"])
    ghst = mi.copy(); ghst.putalpha(mi.split()[3].point(lambda v: int(v * 0.22)))
    img.alpha_composite(ghst, (ML + 10, int(my) + 10)); img.alpha_composite(mi, (ML, int(my)))
    d.text((ML + mw + 18, my + mh * 0.5), "GTD", font=oswald(40, 700), fill=acc, anchor="lm")
    ry = my + mh + 16
    d.line([(ML, ry), (MR, ry)], fill=(255, 255, 255, 44), width=1)
    d.line([(ML, ry), (ML + 92, ry)], fill=acc, width=3)

    # 프로스티드 인포 카드
    cx0, cy0, cx1, cy1 = 66, 656, W - 66, 1066
    frost(img, (cx0, cy0, cx1, cy1), 20, acc); pad = 40
    bx = cx0 + (cx1 - cx0) * 0.57
    # 카드 상단 3개 값(DATE/VENUE/BUY-IN)은 공통 크기 — 열마다 제각각 축소 금지
    kvf, _ = fit_common([(data.get("date", ""), 360), (data.get("place", ""), 360),
                         (data["buyin"], cx1 - pad - bx)], lambda s: noto(s, 800), 33, 19)
    def kv(x, y, k, v):
        draw_ls(d, (x, y), k, oswald(15, 600), acc, ls=3, anchor="la")
        d.text((x, y + 22), v, font=kvf, fill=hi, anchor="la")
    kv(cx0 + pad, cy0 + pad, "DATE", data.get("date", ""))
    kv(cx0 + pad, cy0 + pad + 78, "VENUE", data.get("place", ""))
    kv(bx, cy0 + pad, "BUY-IN", data["buyin"])
    midy = cy0 + 196
    d.line([(cx0 + pad, midy), (cx1 - pad, midy)], fill=(255, 255, 255, 30), width=1)
    stats = [s for s in data["stats"] if s[1]]; n = len(stats); inw = (cx1 - cx0) - pad * 2; cw = inw / n
    svf, _ = fit_common([(val, cw - 22) for _, val in stats], lambda s: noto(s, 800), 31, 17)
    for i, (lab, val) in enumerate(stats):
        sx = cx0 + pad + cw * i
        if i: d.line([(sx, midy + 22), (sx, cy1 - 28)], fill=(255, 255, 255, 26), width=1)
        draw_ls(d, (sx + 14, midy + 26), lab, oswald(14, 600), soft, ls=2, anchor="la")
        d.text((sx + 14, midy + 48), val, font=svf, fill=hi, anchor="la")

    # NOTICE
    ny = 1112
    nt = vtext("NOTICE", oswald(15, 700), lo + (200,), ls=5); img.alpha_composite(nt, (ML - 6, ny))
    nx = ML + 34; colw = (MR - nx) / 2; lh = 30; half = (len(data["notice"]) + 1) // 2
    nf, _ = fit_common([("· " + l, colw - 22) for l in data["notice"]], lambda s: noto(s, 400), 16, 12)
    for ci, chunk in enumerate([data["notice"][:half], data["notice"][half:]]):
        bx2 = nx + ci * colw; yc = ny
        for line in chunk:
            d.text((bx2, yc), "·", font=nf, fill=acc, anchor="la")
            d.text((bx2 + 16, yc), line, font=nf, fill=lo, anchor="la"); yc += lh

    # 스폰서 / 푸터
    spy = 1562
    d.line([(ML, spy - 16), (MR, spy - 16)], fill=(255, 255, 255, 32), width=1)
    sx = ML
    for lab, name in data["sponsors"]:
        draw_ls(d, (sx, spy), lab, noto(13, 600), acc, ls=2, anchor="la")
        d.text((sx, spy + 20), name, font=noto(18, 700), fill=hi, anchor="la")
        sx += measure(name, noto(18, 700))[0] + 50
    fy = SAFE_B - 16
    draw_ls(d, (ML, fy), data["footer_name"], noto(18, 800), hi, ls=1, anchor="lm")
    d.text((MR, fy), data["footer_addr"], font=noto(18, 400), fill=lo, anchor="rm")

    img.convert("RGB").save(out, quality=95); print("saved", out)

import render_poster as A
DATA = dict(A.DATA, kicker="GUARANTEED TOURNAMENT", rail="DAEJEON 2026", date_short="26.07.04 SAT", idx="01")

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "golden_luxe"
    render(dict(DATA, theme=t), sys.argv[2] if len(sys.argv) > 2 else "demo_E.png")
