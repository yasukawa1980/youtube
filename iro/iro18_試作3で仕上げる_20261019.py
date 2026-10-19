"""IRO18 を試作3（開始画像v2＝針先が交差した棒針編み）だけで仕上げる。Claude 2026-10-19。

前回（iro18_完成品を仕上げる_20261019.py・Codex）と同じ処理：背景は開始画像で固定、人物と犬の範囲だけ Kling を重ね、
犬は1.4倍、犬の出来事（あくび・走る夢）は前回と同じ時刻＝章はそのまま。音声は aac_at 版を再圧縮せずに使う。
変えた点：人物の素材は試作3の1本だけ（試作1・2は手の形が違うので混ぜない）、合成範囲を左の針の頭・髪の上・右肩まで広げた。

  python iro18_試作3で仕上げる_20261019.py parts   # 映像の部品（土台＋犬の出来事の入り）
  python iro18_試作3で仕上げる_20261019.py main    # 扉＋本編＋終了カード＋音声
  python iro18_試作3で仕上げる_20261019.py shorts  # ショートA・B（C・Dは前回のまま）
"""
from pathlib import Path
import argparse, importlib.util, json, shutil, subprocess, hashlib
import cv2, numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
OLD = R / 'bgm/IRO/IRO18_毛糸の季節がやってきた'
SSD = Path('/Volumes/ESD-02/BGM/IRO/Chill/18_毛糸の季節がやってきた')
TRIAL = SSD / '手直し_20261018'
RAW3 = TRIAL / '試作3_20261019/Kling_編み物試作3_原本.mp4'
REF = TRIAL / '18_start_編む手元v2_Kling用.png'
PREV = Path('/Users/ryo/Desktop/BGM/IRO/Chill/18_毛糸の季節がやってきた/完成_20261019')  # 前回の完成（犬の素材・カード・ショートC/D・文言）
OUT = SSD / '完成v3_20261019'; WORK = OUT / '_work'; KIT = OUT / '投稿用'
MAIN = KIT / 'iro18_毛糸の季節がやってきた_扉入り.mp4'
FF = '/opt/homebrew/bin/ffmpeg'; FP = '/opt/homebrew/bin/ffprobe'
PREFIX = 543; TOTAL = 173223; CARD = 360; BODY = TOTAL - PREFIX - CARD

# 前回の人物範囲を、左の針の頭（x≈845）・髪の上端（y=5）・右肩（x≈1480）まで広げた
PERSON = [(1102, 5), (1372, 5), (1440, 201), (1480, 400), (1556, 433), (1635, 585),
          (1560, 599), (1520, 623), (1503, 659), (1511, 704), (1511, 730), (1390, 735),
          (1320, 750), (1220, 850), (1050, 850), (935, 825), (810, 797), (810, 742),
          (840, 700), (845, 600), (900, 530), (943, 493), (1075, 408)]


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


prep = load('prep', R / 'iro/iro18_手直し試作_20261018.py')
door = load('door', R / 'bgm/IRO/irokit/扉ムービーを入れる.py')


def run(args): subprocess.run([FF, '-y', '-v', 'error', *map(str, args)], check=True)
def probe(p): return json.loads(subprocess.check_output([FP, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)]))
def video(p): return next(x for x in probe(p)['streams'] if x['codec_type'] == 'video')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while b := f.read(8 << 20): h.update(b)
    return h.hexdigest()


def encopts():
    return ['-c:v', 'h264_videotoolbox', '-allow_sw', '1', '-q:v', '85', '-profile:v', 'high', '-bf', '0', '-g', '192', '-r', '24',
            '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']


def encoder(p):
    return subprocess.Popen([FF, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '24', '-i', '-', '-an', *encopts(), str(p)], stdin=subprocess.PIPE)


def cached(name, path):
    dest = WORK / (name + '.npy')
    if not dest.exists():
        a = np.lib.format.open_memmap(dest, mode='w+', dtype=np.uint8, shape=(192, 1080, 1920, 3)); c = cv2.VideoCapture(str(path))
        for k in range(192):
            ok, b = c.read(); assert ok
            a[k] = cv2.cvtColor(cv2.resize(b, (1920, 1080), interpolation=cv2.INTER_LANCZOS4), cv2.COLOR_BGR2RGB)
        c.release(); a.flush()
    return np.load(dest, mmap_mode='r')


def plan():
    events = []
    for cycle in range(6):  # 前回と同じ時刻（章の時刻を変えない）
        for tag, t in [('C', 280), ('D', 644), ('C', 1134)]:
            at = (cycle * 1197 + t) * 24
            if at + 192 <= BODY: events.append({'tag': tag, 'body_frame': at, 'final_frame': PREFIX + at, 'final_seconds': (PREFIX + at) / 24})
    rows = []
    for i in range((BODY + 191) // 192):
        ev = next((x for x in events if i * 192 < x['body_frame'] + 192 and (i + 1) * 192 > x['body_frame']), None)
        key = f"take3_{ev['tag']}_{i * 192 - ev['body_frame']:+d}" if ev else 'take3_rgb'
        rows.append({'index': i, 'start_body_frame': i * 192, 'frames': min(192, BODY - i * 192), 'key': key, 'event': ev})
    data = {'fps': 24, 'prefix_frames': PREFIX, 'total_frames': TOTAL, 'body_frames': BODY, 'endcard_frames': CARD,
            'take': 3, 'loop_crossfade': False, 'person_polygon': PERSON, 'events': events, 'segments': rows}
    (WORK / '構成.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n'); return data


def parts():
    data = plan(); pack = WORK / 'parts'; pack.mkdir(exist_ok=True)
    raw = cached('raw_take3', RAW3)
    dogs = {n: np.load(PREV / '_work' / f'dog_{n}.npy', mmap_mode='r') for n in ['B1', 'C', 'D']}  # 前回と同じ犬の素材
    ref = np.array(Image.open(REF).convert('RGB'))
    mask = np.zeros((1080, 1920), np.uint8); cv2.fillPoly(mask, [np.array(PERSON, np.int32)], 255)
    pa = (cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 18) * (mask > 0))[:, :, None]
    dm = np.zeros((1080, 1920), np.float32); cv2.ellipse(dm, (409, 862), (241, 154), 0, 0, 360, 1, -1); dm = (cv2.GaussianBlur(dm, (0, 0), 8) * (dm > 0))[:, :, None]
    x, y, w, h = cv2.boundingRect(mask); ps = (slice(y, y + h), slice(x, x + w))
    x, y, w, h = cv2.boundingRect(np.uint8(dm[:, :, 0] > 0)); ds = (slice(y, y + h), slice(x, x + w))
    dogmask = prep.dog_mask()
    unique = {'take3_rgb': None}; unique.update({r['key']: r for r in data['segments'] if r['event']})
    for count, (key, row) in enumerate(unique.items(), 1):
        dest = pack / (key + '.mp4')
        if dest.exists() and int(video(dest)['nb_frames']) == 192: continue
        enc = encoder(dest); ev = row['event'] if row else None; delta = row['start_body_frame'] - ev['body_frame'] if ev else 0
        for k in range(192):
            base = ref.copy()
            base[ps] = np.uint8(np.clip(ref[ps] * (1 - pa[ps]) + raw[k][ps] * pa[ps] + .5, 0, 255))
            base[ds] = np.uint8(np.clip(base[ds] * (1 - dm[ds]) + dogs['B1'][k][ds] * dm[ds] + .5, 0, 255))
            pos = delta + k
            if ev and 0 <= pos < 192:
                a = min(1, (pos + 1) / 12, (192 - pos) / 12)
                base[ds] = np.uint8(np.clip(base[ds] * (1 - dm[ds] * a) + dogs[ev['tag']][pos][ds] * dm[ds] * a + .5, 0, 255))
            im = Image.fromarray(base); zoom = im.resize((2688, 1512), Image.Resampling.LANCZOS).crop((164, 400, 2084, 1480))
            enc.stdin.write(np.array(Image.composite(zoom, im, dogmask)).tobytes())
        enc.stdin.close(); assert enc.wait() == 0 and int(video(dest)['nb_frames']) == 192
        print('映像部品', count, '/', len(unique), key, flush=True)
    print('parts complete', len(unique), flush=True)


def make_prefix():
    pack = WORK / 'parts'; prefix = WORK / '扉と間_543コマ.mp4'
    if not prefix.exists():
        lead = WORK / '導入19コマ.mp4'
        run(['-i', pack / 'take3_rgb.mp4', '-vf', 'trim=start_frame=173:end_frame=192,setpts=PTS-STARTPTS', '-an', *encopts(), lead])
        fc = ('[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[a];[1:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS,'
              'tpad=start_duration=2.5:start_mode=clone[b];[a][b]xfade=transition=fade:duration=1:offset=19.333333,format=yuv420p[v]')
        run(['-i', door.MOVIE, '-i', lead, '-filter_complex', fc, '-map', '[v]', '-an', '-frames:v', PREFIX, *encopts(), prefix])
    assert int(video(prefix)['nb_frames']) == PREFIX
    return prefix


def main_video():
    data = json.loads((WORK / '構成.json').read_text()); pack = WORK / 'parts'
    files = [make_prefix()]
    for row in data['segments']:
        p = pack / (row['key'] + '.mp4'); assert p.exists(), p
        if row['frames'] != 192:
            tail = WORK / '本編末尾.mp4'; run(['-i', p, '-an', '-frames:v', row['frames'], '-c:v', 'copy', tail]); p = tail
        files.append(p)
    listing = WORK / 'カード背景.txt'; listing.write_text(''.join(f"file '{pack / 'take3_rgb.mp4'}'\n" for _ in range(3)))
    card = WORK / 'エンドカード15秒.mp4'
    run(['-ss', BODY % 192 / 24, '-f', 'concat', '-safe', '0', '-i', listing, '-loop', '1', '-framerate', 24, '-i', PREV / 'iro_エンドカード_IRO18.png',
         '-filter_complex', '[0:v]setpts=PTS-STARTPTS[b];[1:v]setpts=PTS-STARTPTS,format=rgba,fade=t=in:st=0.008333:d=2:alpha=1[c];[b][c]overlay=0:0,format=yuv420p[v]',
         '-map', '[v]', '-an', '-frames:v', CARD, *encopts(), card]); files.append(card)
    listing = WORK / '完成映像_連結.txt'; listing.write_text(''.join(f"file '{p}'\n" for p in files))
    audio = WORK / '配信用音声.m4a'
    if not audio.exists(): shutil.copy2((OLD / '_work/配信用音声.m4a').resolve(), audio)
    assert sha(audio) == sha((OLD / '_work/配信用音声.m4a').resolve())
    run(['-f', 'concat', '-safe', '0', '-i', listing, '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', MAIN])
    assert int(video(MAIN)['nb_frames']) == TOTAL
    (WORK / '本編設定_実測.json').write_text(json.dumps({'file': str(MAIN), 'duration': float(probe(MAIN)['format']['duration']), 'video_frames': TOTAL,
        'take': 3, 'audio_sha256': sha(audio), 'audio_reencoded': False, 'loop_crossfade': False}, ensure_ascii=False, indent=2) + '\n')
    print('MAIN COMPLETE', MAIN, flush=True)


def shorts():
    """A・Bは試作3から（Aは頭から・Bは半周ずらす）。C・Dと文言は前回の完成をそのまま写す。"""
    for p in (PREV / '投稿用').iterdir():
        if p.suffix in ('.txt', '.json', '.jpg') or p.name in ('iro18_ショート_C.mp4', 'iro18_ショート_D.mp4'): shutil.copy2(p, KIT / p.name)
    base = WORK / 'parts/take3_rgb.mp4'
    for tag, start in [('A', 0), ('B', 96)]:
        overlay = PREV / '_work' / f'short_{tag}_文字.png'
        listing = WORK / f'short_{tag}_連結.txt'; listing.write_text(''.join(f"file '{base}'\n" for _ in range(3)))
        vonly = WORK / f'short_{tag}_映像.mp4'; final = KIT / f'iro18_ショート_{tag}.mp4'
        run(['-ss', start / 24, '-f', 'concat', '-safe', '0', '-i', listing, '-i', overlay, '-filter_complex',
             '[0:v]setpts=PTS-STARTPTS,crop=608:1080:918:0,scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=0:0,format=yuv420p[v]',
             '-map', '[v]', '-an', *encopts(), '-frames:v', 360, '-movflags', '+faststart', vonly])
        run(['-i', vonly, '-i', PREV / '投稿用' / final.name, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', final])
        v = video(final); assert int(v['nb_frames']) == 360 and (v['width'], v['height']) == (1080, 1920)
        print('short complete', tag, flush=True)
    (KIT / '本編の保存先.txt').write_text(str(MAIN) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('step', choices=['parts', 'main', 'shorts']); a = ap.parse_args()
    for p in [WORK, KIT]: p.mkdir(parents=True, exist_ok=True)
    {'parts': parts, 'main': main_video, 'shorts': shorts}[a.step]()
