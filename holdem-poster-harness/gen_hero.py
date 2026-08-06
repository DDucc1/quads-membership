#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
방향2 스캐폴드 — AI 히어로 이미지 생성 연동 (실사풍).
프로바이더 추상화: 환경변수 키만 넣으면 동작. 키 없으면 안내만 출력.

사용:  python gen_hero.py "hooded poker player, smoke" out.jpg [--provider openai]
키:    OPENAI_API_KEY (openai) / STABILITY_API_KEY (stability)
"""
import os, sys, base64, json, urllib.request

# 실사 지향 공통 프롬프트 랩퍼 — 아이포스터 무드(시네마틱·단색조·드라마틱 림라이트)
WRAP = ("cinematic photorealistic poster hero shot, {subject}, dramatic rim lighting, "
        "dark moody background, film grain, shallow depth of field, high contrast, "
        "monochromatic color grade, 4k, no text, no watermark")

def gen_pollinations(prompt, out, w=1080, h=1620, seed=7):
    """키리스 무료(Flux) — 기본 프로바이더. 무료 티어 해상도 상한 ~627×940(요청 비율 유지).
    화면용 충분·인쇄급(4×)은 키 기반 프로바이더 필요."""
    import urllib.parse
    u = ("https://image.pollinations.ai/prompt/"
         + urllib.parse.quote(WRAP.format(subject=prompt))
         + f"?width={w}&height={h}&model=flux&nologo=true&seed={seed}")
    req = urllib.request.Request(u, headers={"User-Agent": "curl/8"})
    open(out, "wb").write(urllib.request.urlopen(req, timeout=180).read())
    print("saved", out); return True

def gen_openai(prompt, out, size="1024x1536"):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("OPENAI_API_KEY 없음 — 키 설정 후 재실행"); return False
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps({"model": "gpt-image-1", "prompt": WRAP.format(subject=prompt),
                         "size": size, "quality": "high"}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=180))
    open(out, "wb").write(base64.b64decode(r["data"][0]["b64_json"]))
    print("saved", out); return True

def gen_stability(prompt, out):
    key = os.environ.get("STABILITY_API_KEY")
    if not key:
        print("STABILITY_API_KEY 없음 — 키 설정 후 재실행"); return False
    import urllib.request
    body = json.dumps({"prompt": WRAP.format(subject=prompt), "output_format": "jpeg",
                       "aspect_ratio": "2:3"}).encode()
    req = urllib.request.Request("https://api.stability.ai/v2beta/stable-image/generate/sd3",
                                 data=body, headers={"Authorization": f"Bearer {key}",
                                                     "Accept": "image/*",
                                                     "Content-Type": "application/json"})
    open(out, "wb").write(urllib.request.urlopen(req, timeout=180).read())
    print("saved", out); return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    prompt, out = sys.argv[1], sys.argv[2]
    provider = sys.argv[sys.argv.index("--provider") + 1] if "--provider" in sys.argv else "pollinations"
    {"pollinations": gen_pollinations, "openai": gen_openai,
     "stability": gen_stability}[provider](prompt, out)
