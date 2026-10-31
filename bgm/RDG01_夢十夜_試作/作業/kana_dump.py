"""全文の読み（カナ）を書き出して、読み間違いを検品する。"""
import json, sys
from pathlib import Path
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
R = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/VOICEVOX_core_0.17.0_model_0.16.4')
HERE = Path(__file__).resolve().parent
ort = Onnxruntime.load_once(filename=str(next((R/'onnxruntime/lib').glob('*.dylib'))))
synth = Synthesizer(ort, OpenJtalk(str(R/'dict/open_jtalk_dic_utf_8-1.11')))
with VoiceModelFile.open(str(R/'models/vvms/1.vvm')) as m:
    synth.load_voice_model(m)
rows = []
for o in json.load(open(HERE/'sentences.json')):
    for s in ([o['spoken']] if o['kind'] == 'title' else o['sentences']):
        q = synth.create_audio_query(s, 14)
        rows.append(f"{o['night']}\t{s}\t{q.kana}")
(HERE/'kana_check.tsv').write_text('\n'.join(rows))
print(len(rows))
