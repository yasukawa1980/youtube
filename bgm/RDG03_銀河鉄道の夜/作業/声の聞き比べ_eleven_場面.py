"""RDG03：後半の会話の場面を、本番と同じく文ごとに合成して間を入れ、仕上がりを確かめる。

使い方：python 声の聞き比べ_eleven_場面.py 声ID:名前 ...
文ごとにキャッシュする。キーは表示しない。
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('eleven_sample', HERE / '声の聞き比べ_eleven.py')
eleven = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eleven)
OUT = eleven.google.OUT
CACHE = OUT / '場面_cache'
FIRST, LAST = 272, 281  # sentences.json の段落（なぐさめ→苹果の場面）
MODEL = 'eleven_v4'
SPEED = 0.9
GAP = dict(sentence=0.7, para=1.6)


def synth(vid, text, prev, nxt):
    body = {'text': text, 'model_id': MODEL, 'language_code': 'ja',
            'voice_settings': {'speed': SPEED},
            'previous_text': prev, 'next_text': nxt}
    k = hashlib.sha256(json.dumps([vid, body], ensure_ascii=False).encode()).hexdigest()[:16]
    p = CACHE / f'{k}.mp3'
    if not p.exists():
        p.write_bytes(eleven.call(f'/v1/text-to-speech/{vid}?output_format=mp3_44100_128', body))
    return p


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    items = json.loads((HERE / 'sentences.json').read_text())[FIRST:LAST + 1]
    seq = []
    for i, o in enumerate(items):
        for j, s in enumerate(o['sentences']):
            last = j + 1 == len(o['sentences'])
            seq.append((s, GAP['para'] if last else GAP['sentence']))
    print('字数', sum(len(s) for s, _ in seq), '文', len(seq))
    for arg in sys.argv[1:]:
        vid, name = arg.split(':', 1)
        lines = []
        for n, (s, gap) in enumerate(seq):
            prev = seq[n - 1][0] if n else ''
            nxt = seq[n + 1][0] if n + 1 < len(seq) else ''
            lines.append(f"file '{synth(vid, s, prev, nxt)}'")
            sil = CACHE / f'sil{gap}.mp3'
            if not sil.exists():
                subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                                'anullsrc=r=44100:cl=mono', '-t', str(gap), '-b:a', '128k', str(sil)], check=True)
            lines.append(f"file '{sil}'")
        lst = CACHE / f'{name}.txt'
        lst.write_text('\n'.join(lines))
        o = OUT / f'v4_場面_{name}.mp3'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst),
                        '-af', 'loudnorm=I=-20:TP=-2:LRA=11', '-ar', '44100', '-b:a', '192k', str(o)], check=True)
        print(o.name)


if __name__ == '__main__':
    main()
