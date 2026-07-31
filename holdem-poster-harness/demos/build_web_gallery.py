#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""웹 갤러리 빌드 — Bebas 폰트 + 동물 문장 배경 3종(다운스케일 jpg)을 base64 주입.
사용: python demos/build_web_gallery.py (하네스 루트, 폰트·배경 복원 후)"""
import base64, io, os
from PIL import Image

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def b64_font():
    return base64.b64encode(open(os.path.join(root, "assets/BebasNeue.ttf"), "rb").read()).decode()

def b64_bg(name, w=540):
    im = Image.open(os.path.join(root, f"assets/bg/{name}.jpg")).convert("RGB")
    # 메인 포스터 비율(1080:1620) 상단 앵커 크롭 후 축소
    ch = min(im.height, int(im.width * 1620 / 1080))
    im = im.crop((0, 0, im.width, ch))
    im.thumbnail((w, w * 3))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

tpl = open(os.path.join(root, "demos/web_gallery_template.html"), encoding="utf-8").read()
out = (tpl.replace("__BEBAS_B64__", b64_font())
          .replace("__BG_STAG__", b64_bg("animal_stag"))
          .replace("__BG_WOLF__", b64_bg("animal_wolf"))
          .replace("__BG_EAGLE__", b64_bg("animal_eagle")))
p = os.path.join(root, "demos/web_gallery.html")
open(p, "w", encoding="utf-8").write(out)
print("built", p, f"{os.path.getsize(p)//1024}KB")
