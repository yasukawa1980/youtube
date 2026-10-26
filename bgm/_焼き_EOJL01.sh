#!/bin/zsh
# EOJL01（EOJ総集編・8時間46分52秒）の映像を焼いて音と合わせる。約9時間。
# 分割片は seg/*.done があれば飛ばすので、止まっても同じコマンドで再開できる。
setopt pipefail
cd /Users/ryo/youtube/bgm || exit 1
D="/Volumes/ESD-02/BGM/5_Echoes of Old Japan/EOJL01_素材_8時間"
caffeinate -dims /usr/bin/python3 -m bgmkit video eojl01 2>&1 | tee -a "$D/_work/video.log" || exit 1
caffeinate -dims /usr/bin/python3 -m bgmkit mux eojl01 2>&1 | tee -a "$D/_work/video.log"
