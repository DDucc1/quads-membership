#!/usr/bin/env bash
# 렌더에 필요한 폰트 다운로드 (저장소에는 폰트 바이너리를 커밋하지 않음)
set -e
cd "$(dirname "$0")"
dl(){ python3 - "$1" "$2" <<'PY'
import sys,urllib.request
u,o=sys.argv[1],sys.argv[2]
r=urllib.request.Request(u,headers={"User-Agent":"curl/8"})
open(o,"wb").write(urllib.request.urlopen(r,timeout=90).read()); print("ok",o)
PY
}
dl "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf" NotoSansKR.ttf
dl "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf" Anton.ttf
dl "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf" BebasNeue.ttf
dl "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald%5Bwght%5D.ttf" Oswald.ttf
dl "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf" Playfair.ttf
dl "https://github.com/google/fonts/raw/main/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf" Archivo.ttf
