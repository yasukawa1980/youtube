"""RDG04：ElevenLabs v4・Satomi で太宰治4編を文ごとに合成する（RDG03の narrate_satomi.py を流用）。

  python narrate_satomi.py synth     未合成の文だけ合成してキャッシュへ。クレジット切れ等で止まったら、そこまでを保存して終了。
  python narrate_satomi.py status    合成済みの文数・字数
  python narrate_satomi.py assemble  全文がそろったら narration_satomi.wav・narration_satomi.srt・chapters_satomi.json を作る

作品の題は kind='title'。題の前は3秒、題の後は2.5秒。
キーは ~/.config/bgmkit/env の ELEVENLABS_API_KEY だけを読み、表示しない。
"""
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
SSD = Path('/Volumes/ESD-EPB/BGM/9_朗読/RDG04_素材_太宰短編集')
CACHE = SSD / '作業_cache_satomi'
VOICE_ID = 'wcs09USXSN5Bl7FXohVZ'   # Satomi - Calm, Smooth and Clear
MODEL = 'eleven_v4'
SETTINGS = {'speed': 0.9}
SR = 44100
GAP = dict(short=0.35, sentence=0.7, para=1.6, after_title=2.5, before_title=3.0,
           missing=3.0, lead_in=1.5, after_opening=3.0, tail=40.0)
OPENING = ('だざいおさむ、たんぺんしゅう。', '太宰治　短編集')
NOT_TO = ('とんでも', 'とうさん', 'ところ', 'とても', 'とにかく')


def plan():
    """読む順に (spoken, shown, 種類, その後の間) を並べる。"""
    items = json.loads((HERE / 'sentences.json').read_text())
    seq = [(*OPENING, 'opening', GAP['after_opening'])]
    for i, o in enumerate(items):
        nxt = items[i + 1] if i + 1 < len(items) else None
        if o['kind'] == 'title':
            seq.append((o['spoken'], o['display'], 'title', GAP['after_title']))
            continue
        sents = list(zip(o['sentences'], o['display_sentences']))
        for j, (spk, shown) in enumerate(sents):
            if j + 1 < len(sents):
                nd = sents[j + 1][1]
                gap = GAP['short'] if nd.startswith('と') and not nd.startswith(NOT_TO) else GAP['sentence']
            elif o.get('gap_after') == 'missing':
                gap = GAP['missing']
            elif nxt and nxt['kind'] == 'para':
                gap = GAP['para']
            elif nxt and nxt['kind'] == 'title':
                gap = GAP['before_title']
            else:
                gap = 0.0
            if not spk:   # 「……」だけの文は読まずに間にする
                if seq:
                    seq[-1] = (*seq[-1][:3], seq[-1][3] + GAP['sentence'] + gap)
                continue
            seq.append((spk, shown, 'para', gap))
    return seq


def request(n, seq):
    text = seq[n][0]
    body = {'text': text, 'model_id': MODEL, 'language_code': 'ja', 'voice_settings': SETTINGS,
            'previous_text': seq[n - 1][0] if n else '',
            'next_text': seq[n + 1][0] if n + 1 < len(seq) else ''}
    key = hashlib.sha256(json.dumps([VOICE_ID, body], ensure_ascii=False).encode()).hexdigest()[:16]
    return body, CACHE / f'{key}.mp3'


def api_key():
    for line in Path('~/.config/bgmkit/env').expanduser().read_text().splitlines():
        if line.startswith('ELEVENLABS_API_KEY='):
            return line.split('=', 1)[1].strip()
    sys.exit('ELEVENLABS_API_KEY が見つかりません')


def synth():
    CACHE.mkdir(parents=True, exist_ok=True)
    seq, k = plan(), api_key()
    todo = [n for n in range(len(seq)) if not request(n, seq)[1].exists()]
    print(f'全{len(seq)}文・未合成{len(todo)}文・{sum(len(seq[n][0]) for n in todo)}字', flush=True)
    done_chars = 0
    for c, n in enumerate(todo, 1):
        body, path = request(n, seq)
        req = urllib.request.Request(
            f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128',
            headers={'xi-api-key': k, 'Content-Type': 'application/json'}, data=json.dumps(body).encode())
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    data = r.read()
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:400]
                if e.code in (429, 500, 502, 503) and attempt < 3:
                    time.sleep(10 * (attempt + 1))
                    continue
                print(f'停止：{c - 1}文・{done_chars}字を合成したところで HTTP {e.code} {msg}', flush=True)
                sys.exit(2)
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < 3:
                    time.sleep(10 * (attempt + 1))
                    continue
                print(f'停止：通信エラー {e}', flush=True)
                sys.exit(3)
        tmp = path.with_suffix('.part')
        tmp.write_bytes(data)
        tmp.rename(path)
        done_chars += len(body['text'])
        if c % 50 == 0:
            print(f'{c}/{len(todo)}文・{done_chars}字', flush=True)
    print(f'完了：{len(todo)}文・{done_chars}字', flush=True)


def status():
    seq = plan()
    have = [n for n in range(len(seq)) if request(n, seq)[1].exists()]
    print(f'合成済み {len(have)}/{len(seq)}文・{sum(len(seq[n][0]) for n in have)}/{sum(len(s[0]) for s in seq)}字')


def decode(path):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1',
                          '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype='float32')


def ts(t):
    ms = round(t * 1000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def assemble():
    seq = plan()
    missing = [n for n in range(len(seq)) if not request(n, seq)[1].exists()]
    if missing:
        sys.exit(f'未合成が{len(missing)}文あります')
    chunks, cues, chapters, t = [np.zeros(round(GAP['lead_in'] * SR), 'float32')], [], [], GAP['lead_in']
    for n, (spk, shown, kind, gap) in enumerate(seq):
        a = decode(request(n, seq)[1])
        if kind == 'title':
            chapters.append((t, shown))
        cues.append((t, t + len(a) / SR, shown))
        chunks += [a, np.zeros(round(gap * SR), 'float32')]
        t += len(a) / SR + gap
    chunks.append(np.zeros(round(GAP['tail'] * SR), 'float32'))
    t += GAP['tail']
    sf.write(SSD / 'narration_satomi.wav', np.concatenate(chunks), SR, subtype='PCM_16')
    (HERE / 'narration_satomi.srt').write_text('\n'.join(
        f'{i}\n{ts(a)} --> {ts(b)}\n{text}\n' for i, (a, b, text) in enumerate(cues, 1)))
    (HERE / 'chapters_satomi.json').write_text(json.dumps(chapters, ensure_ascii=False))
    print(f'長さ {t / 60:.1f}分・字幕 {len(cues)}')
    for c, name in chapters:
        print(f'{int(c // 60)}:{int(c % 60):02d} {name}')


if __name__ == '__main__':
    {'synth': synth, 'status': status, 'assemble': assemble}[sys.argv[1]]()
