#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홀덤 포스터 — 에디토리얼 크래프트 렌더러 (사람 디자이너 느낌)
핵심: 비대칭 좌측 정렬 · 프로스티드 글래스 패널(배경 실제 블러) · 거대 머니 타이포 ·
      혼합 굵기 락업 · 세로 사이드 레일 · 시네마틱 컬러 그레이딩 · 클리셰 장식 제거.
hero_image 경로가 주어지면 그 사진을 히어로 배경으로 합성(사진형 경로).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from render_poster import (noto, anton, measure, fit_font, draw_ls, lsw, text_img,
                           theme_palette, ASSET)

W, H = 1080, 1800
ML = 96            # content left margin (비대칭 좌측 기준선)
MR = W - 70
RAILX = 66
SAFE_B = H - 54

def grade(bg, acc):
    base = bg.convert("RGB")
    base = ImageEnhance.Color(base).enhance(1.14)
    base = ImageEnhance.Contrast(base).enhance(1.10)
    base = ImageEnhance.Brightness(base).enhance(0.80)
    img = base.convert("RGBA")
    # 하단 시네마틱 다크 그라데이션
    col = Image.new("L", (1, H), 0)
    for y in range(H):
        t = y / H
        col.putpixel((0, y), int(245 * max(0, (t - 0.34) / 0.66) ** 1.3))
    dk = Image.new("RGBA", (W, H), (2, 4, 10, 255)); dk.putalpha(col.resize((W, H)))
    img.alpha_composite(dk)
    # 좌상단 미세 악센트 광원
    gl = Image.new("L", (W, H), 0); ImageDraw.Draw(gl).ellipse([-300, -380, 560, 420], fill=70)
    gl = gl.filter(ImageFilter.GaussianBlur(120))
    tint = Image.new("RGBA", (W, H), acc + (255,)); tint.putalpha(gl)
    img = Image.alpha_composite(img, tint)
    # 필름 그레인
    grain = Image.effect_noise((W, H), 20).convert("L")
    img.alpha_composite(Image.merge("RGBA", (grain, grain, grain, Image.new("L", (W, H), 9))))
    return img

def spade(d, cx, cy, r, fill):
    d.pieslice([cx - r, cy - r, cx, cy + r * 0.2], 0, 360, fill=fill)
    d.pieslice([cx, cy - r, cx + r, cy + r * 0.2], 0, 360, fill=fill)
    d.polygon([(cx, cy - r * 1.25), (cx + r, cy + r * 0.1), (cx - r, cy + r * 0.1)], fill=fill)
    d.polygon([(cx - r * 0.08, cy), (cx + r * 0.08, cy), (cx + r * 0.3, cy + r * 0.7),
               (cx - r * 0.3, cy + r * 0.7)], fill=fill)

def frost(img, box, radius, acc, alpha=140):
    x0, y0, x1, y1 = map(int, box)
    reg = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(17))
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], radius, fill=255)
    img.paste(reg, (x0, y0), m)
    panel = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], radius, fill=(8, 12, 22, alpha),
                         outline=(255, 255, 255, 26), width=1)
    img.alpha_composite(panel, (x0, y0))
    ImageDraw.Draw(img, "RGBA").line([(x0 + 26, y0), (x0 + 120, y0)], fill=acc + (255,), width=3)

def vtext(text, font, fill, ls=3):
    w = int(lsw(text, font, ls)) + 10; h = measure(text, font)[1] + 10
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ls(ImageDraw.Draw(im), (5, 3), text, font, fill, ls, "la")
    return im.rotate(90, expand=True)

def build_bg(data, TH):
    hero = data.get("hero_image")
    if hero and os.path.exists(hero):                       # 사진형 경로
        im = Image.open(hero).convert("RGB")
        s = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * s), int(im.height * s)))
        x = (im.width - W) // 2; y = (im.height - H) // 2
        bg = im.crop((x, y, x + W, y + H)).convert("RGBA")
    else:
        p = f"{ASSET}bg/{data['theme']}.jpg"
        bg = Image.open(p).convert("RGB").resize((W, H)).convert("RGBA") if os.path.exists(p) \
            else Image.new("RGBA", (W, H), (8, 10, 20, 255))
    return grade(bg, TH["accent"])

def render(data, out="demo_E.png"):
    TH = theme_palette(data.get("theme", "flame_blue"))
    acc, soft, hi, lo = TH["accent"], TH["accent_soft"], TH["text_hi"], TH["text_lo"]
    img = build_bg(data, TH); d = ImageDraw.Draw(img, "RGBA")

    # 거대 고스트 스페이드(깊이감, 우하단 블리드)
    gw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spade(ImageDraw.Draw(gw), int(W * 0.82), int(H * 0.62), 360, acc + (26,))
    img.alpha_composite(gw.filter(ImageFilter.GaussianBlur(2)))

    # 세로 사이드 레일
    d.line([(RAILX, 250), (RAILX, 1500)], fill=acc + (120,), width=2)
    rt = vtext(f"POKER OF DREAMS — {data.get('rail','TOURNAMENT')}", noto(15, 600), soft + (220,), ls=3)
    img.alpha_composite(rt, (RAILX - rt.width - 10, 250))

    # 상단 바: 로고(좌) / 날짜(우)
    d.text((ML, 78), "PoD", font=anton(30), fill=hi, anchor="lm")
    draw_ls(d, (ML + 64, 78), "POKER of DREAMS", noto(16, 700), lo, ls=2, anchor="lm")
    draw_ls(d, (MR, 78), data.get("date_short", "26.07.04 SAT"), noto(18, 600), soft, ls=3, anchor="rm")
    d.line([(ML, 116), (MR, 116)], fill=(255, 255, 255, 40), width=1)

    # ===== HERO (비대칭 좌측) =====
    # 키커
    ky = 250
    d.line([(ML, ky), (ML + 46, ky)], fill=acc, width=3)
    draw_ls(d, (ML + 58, ky), data.get("kicker", "GUARANTEED TOURNAMENT"), noto(17, 700), acc, ls=4, anchor="lm")
    # 이벤트명 (혼합: 블랙 + 악센트 경량)
    ey = 278
    ef, _ = fit_font(data["title"], lambda s: noto(s, 900), MR - ML - 200, 78, 48)
    d.text((ML, ey), data["title"], font=ef, fill=hi, anchor="la")
    enw = measure(data["title"], ef)[0]
    if data.get("accent"):
        d.text((ML + enw + 20, ey + measure(data["title"], ef)[1] * 0.32),
               data["accent"], font=noto(34, 400), fill=acc, anchor="la")
    # TOTAL GUARANTEED 라벨
    gy = ey + measure(data["title"], ef)[1] + 44
    draw_ls(d, (ML + 4, gy), "TOTAL GUARANTEED", noto(20, 600), lo, ls=5, anchor="la")
    # 거대 머니 (단일 포커스)
    my = gy + 32
    money = "₩" + data["gtd"]
    mf, msz = fit_font(money, anton, MR - ML, 168, 92)
    mi, mw, mh = text_img(money, mf, (255, 255, 255), TH["gtd_lo"])
    # 고스트 복제(깊이)
    gh = mi.copy(); gha = gh.split()[3].point(lambda v: int(v * 0.25))
    gh.putalpha(gha)
    img.alpha_composite(gh, (ML + 8, int(my) + 8))
    img.alpha_composite(mi, (ML, int(my)))
    # 긴 룰
    ry = my + mh + 18
    d.line([(ML, ry), (MR, ry)], fill=(255, 255, 255, 46), width=1)
    d.line([(ML, ry), (ML + 90, ry)], fill=acc, width=3)

    # ===== 프로스티드 인포 카드 =====
    cx0, cy0, cx1, cy1 = 64, 660, W - 64, 1066
    frost(img, (cx0, cy0, cx1, cy1), 20, acc)
    pad = 38
    # 카드 상단: 좌 DATE/VENUE, 우 BUY-IN
    def kv(x, y, k, v, vw, big=34):
        draw_ls(d, (x, y), k, noto(15, 600), acc, ls=3, anchor="la")
        vf, _ = fit_font(v, lambda s: noto(s, 800), vw, big, 20)
        d.text((x, y + 22), v, font=vf, fill=hi, anchor="la")
    kv(cx0 + pad, cy0 + pad, "DATE", data.get("date", ""), 380)
    kv(cx0 + pad, cy0 + pad + 78, "VENUE", data.get("place", ""), 380)
    # 우측 BUY-IN 강조
    bx = cx0 + (cx1 - cx0) * 0.56
    draw_ls(d, (bx, cy0 + pad), "BUY-IN", noto(15, 600), acc, ls=3, anchor="la")
    bvf, _ = fit_font(data["buyin"], lambda s: noto(s, 900), cx1 - pad - bx, 48, 26)
    d.text((bx, cy0 + pad + 26), data["buyin"], font=bvf, fill=hi, anchor="la")
    # 카드 내 구분선
    midy = cy0 + 196
    d.line([(cx0 + pad, midy), (cx1 - pad, midy)], fill=(255, 255, 255, 32), width=1)
    # 하단 4스탯
    stats = [s for s in data["stats"] if s[1]]
    n = len(stats); inw = (cx1 - cx0) - pad * 2; cw = inw / n
    for i, (lab, val) in enumerate(stats):
        sx = cx0 + pad + cw * i
        if i: d.line([(sx, midy + 22), (sx, cy1 - 28)], fill=(255, 255, 255, 28), width=1)
        draw_ls(d, (sx + 16, midy + 26), lab, noto(15, 600), soft, ls=2, anchor="la")
        vf, _ = fit_font(val, lambda s: noto(s, 800), cw - 24, 32, 18)
        d.text((sx + 16, midy + 50), val, font=vf, fill=hi, anchor="la")

    # ===== NOTICE (절제된 2단, 좌측 세로 라벨) =====
    ny = 1110
    nt = vtext("NOTICE", noto(15, 700), lo + (200,), ls=4)
    img.alpha_composite(nt, (ML - 6, ny))
    nx = ML + 34; colw = (MR - nx) / 2; yy = ny; lh = 30
    half = (len(data["notice"]) + 1) // 2
    for ci, chunk in enumerate([data["notice"][:half], data["notice"][half:]]):
        bx2 = nx + ci * colw; yc = yy
        for line in chunk:
            f = noto(16, 400)
            if measure("· " + line, f)[0] > colw - 22:
                f, _ = fit_font("· " + line, lambda s: noto(s, 400), colw - 22, 16, 12)
            d.text((bx2, yc), "·", font=f, fill=acc, anchor="la")
            d.text((bx2 + 16, yc), line, font=f, fill=lo, anchor="la"); yc += lh

    # ===== 스폰서 / 푸터 (좌 정렬, 절제) =====
    spy = 1560
    d.line([(ML, spy - 16), (MR, spy - 16)], fill=(255, 255, 255, 34), width=1)
    sp = data["sponsors"]; sx = ML
    for lab, name in sp:
        draw_ls(d, (sx, spy), lab, noto(13, 600), acc, ls=2, anchor="la")
        d.text((sx, spy + 20), name, font=noto(18, 700), fill=hi, anchor="la")
        sx += measure(name, noto(18, 700))[0] + 52
    # 푸터
    fy = SAFE_B - 18
    draw_ls(d, (ML, fy), data["footer_name"], noto(19, 800), hi, ls=1, anchor="lm")
    d.text((MR, fy), data["footer_addr"], font=noto(17, 400), fill=lo, anchor="rm")

    img.convert("RGB").save(out, quality=95); print("saved", out)

# 데모 데이터 (render_poster.DATA 확장)
import render_poster as A
DATA = dict(A.DATA, kicker="GUARANTEED TOURNAMENT", rail="DAEJEON 2026", date_short="26.07.04 SAT")

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "golden_luxe"
    render(dict(DATA, theme=t), sys.argv[2] if len(sys.argv) > 2 else "demo_E.png")
