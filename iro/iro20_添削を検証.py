"""Claudeの修正済みv03と全49章を検証し、検品対象の版をそろえる。"""
from pathlib import Path
import json
import re
import subprocess

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
IRO = ROOT / 'iro'


def times(text):
    values = []
    for match in re.finditer(r'^(\d+:\d{2}(?::\d{2})?)\s', text, re.M):
        seconds = 0
        for part in match[1].split(':'):
            seconds = seconds * 60 + int(part)
        values.append(seconds)
    return values


def main():
    cfg = yaml.safe_load((IRO / 'volumes/iro20.yaml').read_text())
    plan = json.loads((Path(cfg['dir']) / '_work/映像_v01/構成.json').read_text())
    offset = {'A': 1, 'B': 2.666666667, 'C': .666666667, 'D': .666666667}
    expected = [0] + [int(e['seconds'] + offset[e['kind']]) for e in plan['events']]
    assert len(expected) == 49
    assert min(b - a for a, b in zip(expected, expected[1:])) >= 10
    paste = IRO / 'IRO20_しおりを挟むにはまだ早い_貼り付け用'
    for name in ['00_説明文_これを貼る.txt', '05_説明文_日本語.txt', '10_英語ローカライズ_説明文.txt']:
        assert times((paste / name).read_text()) == expected, name
    assert times((paste / '11_チャプター_動き.txt').read_text()) == expected * 2
    assert times((IRO / 'iro20_アップロード情報.md').read_text()) == expected * 2
    assert len(list(paste.glob('*.txt'))) == 15
    path = IRO / 'iro20_完成検品.json'
    report = json.loads(path.read_text())
    rows = {}
    for tag, filename in cfg['shorts']['files'].items():
        check = report['checks'][tag]
        assert filename.endswith('_v03.mp4')
        assert check['technical_pass'] and check['file'] == filename
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-threads', '2', '-i', filename,
            '-an', '-vf', 'scale=96:170', '-pix_fmt', 'gray', '-f', 'rawvideo', '-'])
        frames = np.frombuffer(raw, np.uint8).reshape(-1, 170, 96).astype(np.int16)
        assert len(frames) == 360
        delta = np.abs(frames[1:] - frames[:-1]).mean(axis=(1, 2))
        scope = ('v03の4秒全景とCあくび2.3秒の見本を実見。誘導文「関連動画から」、'
                 '顔・犬全身・尾の非遮蔽を確認。全360コマ差分と厳密デコードで検査。'
                 '本人の連続通し視聴・直接聴取は未実施。')
        rows[tag] = dict(file=filename, decoded_frames=360, analysis_size=[96, 170],
            adjacent_mae_median=float(np.median(delta)), adjacent_mae_max=float(delta.max()),
            max_at_seconds=float((int(np.argmax(delta)) + 1) / 24),
            event_to_base_at_8s_mae=float(delta[191]), visual_review=scope,
            all_frame_adjacent_mae=delta.tolist())
        check.update(visual_review='completed_v03_sampled_frames_and_all_frame_differences',
                     visual_scope=scope)
    def save(name, data):
        (IRO / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    save('iro20_ショート映像確認.json', rows)
    save('iro20_完成検品.json', report)
    keys = ['file', 'file_sha256', 'duration_seconds', 'frames', 'lufs', 'true_peak_dbtp',
            'full_av_decode_exit_code', 'decode_error_bytes', 'technical_pass']
    save('iro20_Claude添削対応_20261026.json', {
        'source_commit': '4ac198f92ad94c4b415d715d7694c8d7dd5fa4d5',
        'source': 'GitHub制作ブランチのClaude添削コミットとローカル修正資料。bgm/_申し送り.mdにIRO20追記なし。',
        'claude_changes': ['日英の動作チャプターを全49件へ展開', '英語題の区切り前の句点を削除',
                          '貼り付け用15ファイルを作成', 'ショート4本の誘導文を「関連動画から」にしてv03へ更新'],
        'codex_followup': ['全49章を本編の全48イベント構成と照合', 'v03の最終AAC全体と全編AVデコードを再検品',
                          'v03の見本と全360コマ差分を更新して実見', '検品版と採用版の不一致で納品処理を停止する保護を追加',
                          '納品資料・SHA一覧・Mac側の写しを同期し、旧版を投稿対象外と記録'],
        'chapter_count_per_language': 49, 'paste_file_count': 15, 'shorts_revision': 'v03',
        'shorts': {tag: {k: report['checks'][tag][k] for k in keys} for tag in 'ABCD'},
        'main_reencoded': False, 'new_generation_credits': 0,
        'direct_listening': 'not_performed', 'youtube_uploaded': False})
    print('v03 four files, 49 chapters, 15 paste files verified', flush=True)


if __name__ == '__main__':
    main()
