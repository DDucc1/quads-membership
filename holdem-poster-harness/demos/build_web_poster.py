#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""웹 포스터 빌드 — 템플릿에 Bebas 폰트(base64) 주입해 단독 HTML 생성.
폰트 바이너리 비커밋 원칙에 따라 산출물(web_poster.html)은 생성물로 취급한다.
사용: python demos/build_web_poster.py  (하네스 루트에서, 폰트 복원 후)"""
import base64, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b64 = base64.b64encode(open(os.path.join(root, "assets/BebasNeue.ttf"), "rb").read()).decode()
tpl = open(os.path.join(root, "demos/web_poster_template.html"), encoding="utf-8").read()
out = os.path.join(root, "demos/web_poster.html")
open(out, "w", encoding="utf-8").write(tpl.replace("__BEBAS_B64__", b64))
print("built", out)
