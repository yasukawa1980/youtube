# -*- coding: utf-8 -*-
"""KCF08「囲炉裏端」の完成MP4とショート3本を検品する（2026年11月8日）。
_検品_KCF07.py の写し。ショートは volumes/kcf08.yaml の shorts から読み、無いものは飛ばす。
`_検品_EOJ07-10_動画.py` をKCFに当てた形。照合先の wav はSSDの `_work/music_bed.wav`。

★KCFの manifest は `xf: 0.0`（ハードカット）なので、切替は**2秒差**で出る。
  ECJ/EOJのようにディゾルブ8秒の巻では12秒差で見ること。
"""
import json, os, re, subprocess, sys
import numpy as np

B = '/Volumes/ESD-EPB/BGM/7_Kominka Cafe/KCF08_素材_囲炉裏端'
MP4 = B + '/kcf08_完成.mp4'
WAV = B + '/_work/music_bed.wav'
MAN = B + '/_work/manifest.json'
import yaml
def _sec(x):
    p=[int(v) for v in str(x).split(':')]; return p[0]*3600+p[1]*60+p[2] if len(p)==3 else p[0]*60+p[1]
_Y = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'volumes/kcf08.yaml')))
SHORTS = [(s['tag'], f"{B}/ショート/kcf08_ショート_{s['tag']}.mp4", _sec(s['at'])) for s in _Y.get('shorts', [])]
SHORTS = [x for x in SHORTS if os.path.exists(x[1])]

sh = lambda a: subprocess.run(a, capture_output=True, text=True)

def pcm(path, ss=None, t=None):
    a = ['ffmpeg', '-v', 'error']
    if ss is not None: a += ['-ss', str(ss)]
    a += ['-i', path]
    if t is not None: a += ['-t', str(t)]
    a += ['-map', '0:a', '-ac', '1', '-ar', '8000', '-f', 's16le', '-']
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, dtype=np.int16).astype(np.float32)

def dur(f):
    return float(sh(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).stdout)

def loud(f):
    r = sh(['ffmpeg','-hide_banner','-nostats','-i',f,'-af','ebur128=peak=true:framelog=quiet','-f','null','-']).stderr
    g = dict(re.findall(r'^\s+(I|LRA|Peak):\s+(-?[\d.]+)', r, re.M))
    return g.get('I'), g.get('LRA'), g.get('Peak')

def vframe(f, t, W=1920, H=1080):
    r = subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',f,'-frames:v','1',
                        '-f','rawvideo','-pix_fmt','gray','-'], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.uint8)
    return a.reshape(H, W).astype(float) if a.size == W*H else None

def diff(f, t, gap=2.0, W=1920, H=1080):
    a, b = vframe(f, t, W, H), vframe(f, t+gap, W, H)
    return float(np.abs(a-b).mean()) if a is not None and b is not None else float('nan')

man = json.load(open(MAN)); want = man['total']; cuts = [t['start'] for t in man['tracks']]

print('■ KCF08 本編  %s' % os.path.basename(MP4), flush=True)
D = dur(MP4)
print('   尺 %.6f（狙い %.6f・差 %+.6f）／ %.1fMB' % (D, want, D-want, os.path.getsize(MP4)/1048576), flush=True)
I, LRA, P = loud(MP4)
print('   音量 %s LUFS / LRA %s / Peak %s dBFS' % (I, LRA, P), flush=True)
rs = []
for ss in (30, D/2, max(0, D-90)):
    a, b = pcm(MP4, ss, 60), pcm(WAV, ss, 60); m = min(len(a), len(b))
    if m >= 8000: rs.append((ss, float(np.corrcoef(a[:m], b[:m])[0,1])))
print('   music_bedとの相関: %s' % '  '.join('%.0fs %.5f' % r for r in rs), flush=True)
on  = [diff(MP4, c-1.0) for c in cuts[1:]]
mid = [diff(MP4, (cuts[i]+cuts[i+1])/2) for i in range(len(cuts)-1)]
print('   切替をまたぐ2秒差 %s ／ 場面の中 %s'
      % (' / '.join('%.1f' % x for x in on), ' / '.join('%.2f' % x for x in mid)), flush=True)
print('   終わり: %.0f秒地点 %.2f ／ %.0f秒地点 %.2f' % (D-12, diff(MP4, D-12), D-5, diff(MP4, D-5)), flush=True)
r = sh(['ffmpeg','-v','error','-i',MP4,'-f','null','-'])
print('   全編デコード: %s' % ('通過' if not r.stderr.strip() else '★'+r.stderr[:200]), flush=True)

for tag, f, at in SHORTS:
    print('■ ショート %s  %s' % (tag, os.path.basename(f)), flush=True)
    d = dur(f); I, LRA, P = loud(f)
    a, b = pcm(f, 2, 40), pcm(WAV, at+2, 40); m = min(len(a), len(b))
    c = float(np.corrcoef(a[:m], b[:m])[0,1]) if m >= 8000 else float('nan')
    r = sh(['ffmpeg','-v','error','-i',f,'-f','null','-'])
    print('   尺 %.3f秒 ／ %s LUFS / LRA %s / Peak %s ／ 本編%s との相関 %.5f ／ デコード %s'
          % (d, I, LRA, P, '%d:%02d' % (at//60, at%60), c,
             '通過' if not r.stderr.strip() else '★'+r.stderr[:120]), flush=True)
