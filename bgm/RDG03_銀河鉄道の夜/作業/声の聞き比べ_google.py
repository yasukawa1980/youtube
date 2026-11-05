"""RDG03：冒頭の同じ本文をGoogle Cloud TTSで合成し、今の声と聞き比べる。

使い方：
  python 声の聞き比べ_google.py voices        日本語の声の一覧
  python 声の聞き比べ_google.py make 声名...  冒頭を合成（字数を表示）
キーは ~/.config/bgmkit/env の GOOGLE_TTS_API_KEY だけを読み、表示しない。
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path('/Volumes/ESD-EPB/BGM/9_朗読/RDG03_素材_銀河鉄道の夜/声の聞き比べ')
API = 'https://texttospeech.googleapis.com/v1'
TARGET_CHARS = 330  # 冒頭およそ1分ぶん


def key():
    for line in Path('~/.config/bgmkit/env').expanduser().read_text().splitlines():
        if line.startswith('GOOGLE_TTS_API_KEY='):
            v = line.split('=', 1)[1].strip()
            if v:
                return v
    sys.exit('GOOGLE_TTS_API_KEY が見つかりません')


def call(path, body=None):
    req = urllib.request.Request(API + path, headers={'X-Goog-Api-Key': key(), 'Content-Type': 'application/json'},
                                 data=json.dumps(body).encode() if body else None)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read().decode()[:600]}')


def opening_text():
    """読み替え済みの本文（spoken）を、段落の切れ目で目標字数まで集める。"""
    parts = ['みやざわけんじ、ぎんがてつどうのよる。']
    n = len(parts[0])
    for o in json.loads((HERE / 'sentences.json').read_text()):
        ss = [o['spoken']] if o['kind'] == 'title' else o['sentences']
        parts += ss
        n += sum(map(len, ss))
        if n >= TARGET_CHARS and o['kind'] != 'title':
            break
    return parts


def main():
    if sys.argv[1] == 'voices':
        for v in call('/voices?languageCode=ja-JP')['voices']:
            print(v['name'], v['ssmlGender'], v['naturalSampleRateHertz'])
        return
    parts = opening_text()
    text = '\n'.join(parts)
    print('字数', len(text))
    print(text)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[2:]:
        r = call('/text:synthesize', {
            'input': {'text': text},
            'voice': {'languageCode': 'ja-JP', 'name': name},
            'audioConfig': {'audioEncoding': 'LINEAR16', 'sampleRateHertz': 24000},
        })
        path = OUT / f'google_{name}.wav'
        path.write_bytes(base64.b64decode(r['audioContent']))
        print(name, path.stat().st_size)


if __name__ == '__main__':
    main()
