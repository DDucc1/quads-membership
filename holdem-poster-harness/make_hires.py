#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""고해상 렌더 러너 — V6 스트럭처 일체형 4× (4320×7600 ≈ A2 300DPI). QC 스펙 포함."""
import os
import qc
A0, EA, EB, EC = qc.load()
import render_structure as RS
from make_practice import DATA, SPEC

os.makedirs("out/hires", exist_ok=True)
K = 4
fails = len(qc.run(f"P001_Cyan_{K}x", RS.W * K, RS.H * K,
                   lambda: RS.render(DATA, f"out/hires/p001_cyan_{K}x.png", scale=K), spec=SPEC))
qc.ENABLED = False
print("QC TOTAL:", "ALL PASS ✅" if fails == 0 else f"{fails}건 위반 ❌")
