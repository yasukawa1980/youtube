#!/bin/zsh
# サムネを日本語版に差し替える（1本ずつ／何本かまとめて）
#
#   ./scripts_サムネ差し替え.sh vol3 vol4
#
# やること3つ：
#   1. いまの英語版を同じ場所に `_英語_控え.png` で退避
#   2. `<巻>_サムネ_16x9_日本語.png` を本番の場所へコピー
#   3. 巻のYAMLから試作用の thumb_out を外す（次から既定の場所に書かれる）
#
# ★退避を必ず取ること。 公開中のサムネはYouTube側にしか残っていない場合がある。
set -e
cd "$(dirname "$0")"
SSD="/Volumes/ESD-EPB/BGM/1_Whispers of Japan"
for v in "$@"; do
  dst=$(python3 -c "
import sys; sys.path.insert(0,'.')
from bgmkit import config; import os
c=config.load('$v'); print(os.path.join(c['dir'], c.slug+'_サムネ_16x9.png'))")
  jp="$SSD/${v}_サムネ_16x9_日本語.png"
  [[ -f "$jp" ]] || { echo "$v: 日本語版が無い（$jp）"; continue; }
  if [[ -f "$dst" && ! -f "${dst%.png}_英語_控え.png" ]]; then
    cp "$dst" "${dst%.png}_英語_控え.png"; echo "$v: 英語版を退避"
  fi
  cp "$jp" "$dst"
  python3 - "$v" <<'PY'
import io, sys, re
v=sys.argv[1]; p=f"volumes/{v}.yaml"; s=io.open(p,encoding="utf-8").read()
s=re.sub(r"\n# ★日本語版は別名で書き出す（公開済みのサムネを潰さないため）\nthumb_out: \".*?\"\n", "\n", s)
io.open(p,"w",encoding="utf-8").write(s)
PY
  echo "$v: 差し替えた → $dst"
  echo "   ★YouTube側の差し替えは手作業。このファイルをアップロードすること。"
done
