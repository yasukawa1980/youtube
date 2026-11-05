"""RDG03：冒頭の同じ本文をElevenLabsで合成し、今の声と聞き比べる。

使い方：
  python 声の聞き比べ_eleven.py voices                 使える声の一覧
  python 声の聞き比べ_eleven.py make モデル 声ID:名前 ...  冒頭を合成
キーは ~/.config/bgmkit/env の ELEVENLABS_API_KEY だけを読み、表示しない。
本文は声の聞き比べ_google.py と同じものを使う。
"""
import importlib.util
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('google_sample', HERE / '声の聞き比べ_google.py')
google = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google)
API = 'https://api.elevenlabs.io'


def key():
    for line in Path('~/.config/bgmkit/env').expanduser().read_text().splitlines():
        if line.startswith('ELEVENLABS_API_KEY='):
            v = line.split('=', 1)[1].strip()
            if v:
                return v
    sys.exit('ELEVENLABS_API_KEY が見つかりません')


def call(path, body=None):
    req = urllib.request.Request(API + path, headers={'xi-api-key': key(), 'Content-Type': 'application/json'},
                                 data=json.dumps(body).encode() if body else None)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read().decode()[:600]}')


def main():
    if sys.argv[1] == 'voices':
        for v in json.loads(call('/v2/voices?page_size=100'))['voices']:
            lab = v.get('labels') or {}
            print(v['voice_id'], v['name'], v.get('category'), lab.get('gender'), lab.get('age'), lab.get('accent'), sep=' | ')
        return
    model = sys.argv[2]
    text = '\n'.join(google.opening_text())
    print('字数', len(text))
    for spec in sys.argv[3:]:
        vid, name = spec.split(':', 1)
        audio = call(f'/v1/text-to-speech/{vid}?output_format=mp3_44100_128', {
            'text': text, 'model_id': model, 'language_code': 'ja',
        })
        path = google.OUT / f'eleven_{model}_{name}_raw.mp3'
        path.write_bytes(audio)
        print(name, model, path.stat().st_size)


if __name__ == '__main__':
    main()
