#!/bin/zsh
# サムネを日本語版に差し替える（1本ずつ／何本かまとめて）
#
#   ./scripts_サムネ差し替え.sh vol3 vol4
#
# やること3つ：
#   1. いまの英語版を同じ場所に `_英語_控え.png` で退避
#   2. 日本語版を本番の場所（<巻の dir>/<slug>_サムネ_16x9.png）へコピー
#   3. 巻のYAMLから試作用の thumb_out を外す（次から既定の場所に書かれる）
#
# ★★日本語版の在り処は巻の `thumb_out` から引く（2026年8月26日に直した）。
#   以前は「SSDの1箇所にまとまっている」前提でパスを組み立てていたが、
#   SSDをシリーズ別（BGM/1_〜4_）に並べ直したときに日本語版が巻ごとの
#   フォルダへ散り、soj01 で「日本語版が無い」と誤って止まった。
#   **設定に書いてある場所を読むのが唯一正しい。**
set -e
cd "$(dirname "$0")"
for v in "$@"; do
  read -r dst jp <<< "$(python3 -c "
import sys; sys.path.insert(0,'.')
from bgmkit import config; import os
c=config.load('$v')
dst=os.path.join(c['dir'], c.slug+'_サムネ_16x9.png')
print(dst, c.get('thumb_out') or dst)" | tr '\n' ' ')"
  # パスに空白が入るので改めて安全に取り直す
  dst=$(python3 -c "
import sys; sys.path.insert(0,'.')
from bgmkit import config; import os
c=config.load('$v'); print(os.path.join(c['dir'], c.slug+'_サムネ_16x9.png'))")
  jp=$(python3 -c "
import sys; sys.path.insert(0,'.')
from bgmkit import config; import os
c=config.load('$v'); print(c.get('thumb_out') or os.path.join(c['dir'], c.slug+'_サムネ_16x9.png'))")
  if [[ ! -f "$jp" ]]; then echo "$v: 日本語版が無い（$jp）"; continue; fi
  if [[ "$jp" == "$dst" ]]; then echo "$v: すでに本番が日本語版"; continue; fi
  if [[ -f "$dst" && ! -f "${dst%.png}_英語_控え.png" ]]; then
    cp "$dst" "${dst%.png}_英語_控え.png"; echo "$v: 英語版を退避"
  fi
  cp "$jp" "$dst"
  python3 - "$v" <<'PY'
import io, sys, re
v=sys.argv[1]; p=f"volumes/{v}.yaml"; s=io.open(p,encoding="utf-8").read()
s=re.sub(r"\n#[^\n]*日本語版は別名[^\n]*\n", "\n", s)
s=re.sub(r"^thumb_out: .*\n", "", s, flags=re.M)
io.open(p,"w",encoding="utf-8").write(s)
PY
  echo "$v: 差し替えた → $dst"
  echo "   ★YouTube側の差し替えは手作業。このファイルをアップロードすること。"
done
