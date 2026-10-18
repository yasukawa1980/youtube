#!/bin/bash
# Waves of Japan Vol.1「月の水鏡」— バイノーラルビート層の生成
#
# 中心 196Hz（G3）に固定し、うなりだけを 12Hz → 8Hz へ3時間かけて直線で落とす。
#   左  = 196 - うなり/2   （190.0Hz → 192.0Hz）
#   右  = 196 + うなり/2   （202.0Hz → 200.0Hz）
# 左右の2音が3時間かけて寄っていき、中心は常に G3 に乗る。
#
# ★キャリアを下げないこと。 200→150Hz にすると途中で E3 と F3 の中間を通り、
#   調性のある床に対して四分音でずれた持続音を3時間敷くことになる。
#
# ★出力は 24bit/48kHz ステレオ 3時間 ＝ 約3.6GB。空きを確認してから回す。

set -euo pipefail

C=196            # 中心周波数（G3）。床の主調と必ず一致させる
B0=12            # 開始のうなり（Hz）
B1=8             # 終了のうなり（Hz）
# ★★尺は「3時間」ではなく本編の実尺に合わせること（2026年8月28日、実際に嵌まった）。
#   track_seconds の合計からクロスフェード分を引いた値が本編の長さで、この巻は
#   10832 − 4×6 = **10808秒**。ちょうど10800で作ったら no_loop の番人に8秒足りずに
#   弾かれ、モザイクを1時間かけて組んだあとで止まった。
#   確認: python3 -c "import yaml;d=yaml.safe_load(open('volumes/wave01.yaml'));\
#          print(sum(d['track_seconds'])-6*(len(d['track_seconds'])-1))"
T=10808          # 尺（秒）＝ 本編の実尺（3時間00分08秒）
# ★★音量はここで焼き込まない（2026年8月28日、二重掛けで嵌まった）。
#   ここで -28dB を焼き込んだうえ `ambient.gain_db: -28` が掛かり、合計 -56dB になって
#   完全に埋もれた（帯域ごとの持ち上がりが全帯 0.0dB）。
#   **高さは genres/waves.yaml の `ambient.gain_db` だけで決めること。**
GAIN=0           # 素材としての基準の高さ。実際の高さは ambient.gain_db が決める
OUT="${1:-wave01_beat_3h.wav}"

echo "生成: 中心 ${C}Hz 固定 / うなり ${B0} → ${B1}Hz / ${T}秒 / ${GAIN}dB"
echo "  左 $(python3 -c "print(f'{$C-$B0/2:.2f} → {$C-$B1/2:.2f}')") Hz"
echo "  右 $(python3 -c "print(f'{$C+$B0/2:.2f} → {$C+$B1/2:.2f}')") Hz"

ffmpeg -hide_banner -y \
  -f lavfi -i "aevalsrc=exprs=sin(2*PI*(($C-$B0/2)*t-($B1-$B0)/2*t*t/(2*$T))):s=48000:d=$T" \
  -f lavfi -i "aevalsrc=exprs=sin(2*PI*(($C+$B0/2)*t+($B1-$B0)/2*t*t/(2*$T))):s=48000:d=$T" \
  -filter_complex "[0:a][1:a]join=inputs=2:channel_layout=stereo,volume=${GAIN}dB[a]" \
  -map "[a]" -ar 48000 -c:a pcm_s24le "$OUT"

echo
echo "=== 検品：頭・中・尻で左右と うなり を測る ==="
python3 - "$OUT" "$T" <<'PY'
import subprocess, sys, numpy as np
path, T = sys.argv[1], float(sys.argv[2]); sr = 48000
def grab(start):
    raw = subprocess.run(["ffmpeg","-v","error","-ss",str(start),"-t","8","-i",path,
                          "-f","f32le","-ac","2","-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1,2)
def pk(s):
    X=np.abs(np.fft.rfft(s*np.hanning(len(s)))); f=np.fft.rfftfreq(len(s),1/sr); i=X.argmax()
    a,b,c=np.log(X[i-1]),np.log(X[i]),np.log(X[i+1])
    return f[i]+0.5*(a-c)/(a-2*b+c)*(f[1]-f[0])
def beat(s):
    e=np.abs(s[:,0]+s[:,1]); e=e-e.mean()
    X=np.abs(np.fft.rfft(e*np.hanning(len(e)))); f=np.fft.rfftfreq(len(e),1/sr)
    m=(f>1)&(f<20); return f[m][X[m].argmax()]
print(f"{'位置':<10}{'左':>11}{'右':>11}{'中心':>11}{'うなり':>11}")
for nm, st in [("頭", 5), ("中", T/2), ("尻", T-15)]:
    s = grab(st); L, R = pk(s[:,0]), pk(s[:,1])
    print(f"{nm:<10}{L:>9.2f}Hz{R:>9.2f}Hz{(L+R)/2:>9.2f}Hz{beat(s):>9.2f}Hz")
print("\n★中心が3か所とも 196.00Hz なら正しい。ずれていたら式を疑う。")
PY
