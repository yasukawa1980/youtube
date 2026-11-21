"""Record EP015 measurements and build the bilingual review index."""
from collections import Counter
from pathlib import Path
import shutil
import subprocess
from wom15_art import ASSETS, SCRIPT, MANIFEST
from wom15_boards import WORDS
from wom15_voice import HERE, ROOT, read, save, sha

SHARE = HERE / 'wom15_確認版_v01_20261121'
OUT = ROOT / 'deliverables'
VERSIONS = [('en', ''), ('ja', ''), ('en', '_4k')]

def audio_hash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
        '-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def collect():
    measurements = []
    for asset in MANIFEST['assets']:
        assert sha(Path(asset['original_path'])) == asset['sha256'], asset['candidate_id']
    for lang, suffix in VERSIONS:
        base = ROOT / lang
        records = base / 'records'
        qc = read(records / f'technical_qc{suffix}.json')
        cuts = read(records / f'render_shots{suffix}.json')
        uses = Counter(c['key'] for c in cuts if c['key'] in ASSETS)
        assert uses == Counter(ASSETS.keys()) and len(uses) == 20
        assert all(a['end'] == b['start'] for a, b in zip(cuts, cuts[1:]))
        assert qc['sha256'] == sha(base / 'deliverables' / qc['file'])
        standalone=audio_hash(OUT/f'EP015_audio_{lang}.m4a')
        assert audio_hash(base/'deliverables'/qc['file'])==standalone
        assert all(m['ratio'] is not None and 0 < m['ratio'] <= 2.5 for m in qc['motion']), qc['motion']
        all_board = next(c for c in cuts if c['key'] == 'D_board_all')
        assert (all_board['frames'] - 7) / 30 >= 1.5
        printed = read(Path(all_board['stages'][-1]['meta']))['text']
        strings = [r['text'] for r in printed]
        for key, pair in WORDS.items():
            assert pair in SCRIPT and all(t in strings for t in pair.split('｜')), key
        credit = next(c for c in cuts if c['key'] == 'credits')
        assert any('日本語の声' in row['text'] and 'VOICEVOX:冥鳴ひまり' in row['text']
                   for row in read(Path(credit['stages'][0]['meta']))['text'])
        rows = qc['layout']
        sub = read(records / 'subtitle_layout_validation.json')
        by_id = {k: max(a['scale'] for a in qc['scales'] if a['key'] == k) for k in ASSETS}
        holds = {a['segment']: a['gap'] for a in read(records / 'voice_gaps.json')['gaps']
                 if a['segment'] in ('P05', 'P07', 'P10', 'P12')}
        assert len(holds) == 4 and min(holds.values()) >= .9
        size_factor = 2 if suffix else 1
        gap = min(sub['minimum_top'] * size_factor - 891 * size_factor,
                  min(row['gap'] for row in rows))
        assert gap > 0
        art_bottom = max(t['ink_box'][3] for c in cuts if c['key'] in ASSETS
                         for stage in c['stages'] for t in read(Path(stage['meta']))['text'])
        art_gap = sub['minimum_top'] * size_factor - art_bottom
        assert art_gap > 0
        if not suffix:
            review = read(records / 'subtitled_review.json')
            assert review['sha256'] == sha(base / 'deliverables' / review['file'])
            assert audio_hash(base/'deliverables'/review['file'])==standalone
        measurements.append(dict(lang=lang, suffix=suffix, size_factor=size_factor, n=qc['decoded_frames'],
            total=qc['decoded_frames']/30, shots=len(cuts), sound=qc['loudness'], qc=qc, by_id=by_id,
            holds=holds, board_hold=(all_board['frames']-7)/30, gap=gap, art_gap=art_gap))
    return measurements


def clock(seconds):
    return f'{int(seconds)//60}:{seconds%60:06.3f}'


def metrics():
    versions = collect()
    en, ja = versions[:2]
    report = ['# Quiet Origins 第15話「クリスマスはなぜ12月25日なのか」確認版v01', '',
       '公開予定は2026年12月2日（水）09:00 JST。英語音声で公開し、日本語は題と概要欄の翻訳を登録する。英日の公開用概要欄には Kokoro / Heart (af_heart) を記載した。将来日本語音声も公開するときは両方の声を載せるよう、貼り付け用本文の下の担当者メモに記載した。',
       '', '確認版のP16は英日の声を明示。日本語MP4には「日本語の声　VOICEVOX:冥鳴ひまり」を表示し、日本語M4A・WAVは同じ表記のREADMEを音声・字幕ZIPに同梱した。[英語投稿情報](EP015_upload_info_en.md)・[日本語投稿情報](EP015_upload_info_ja.md)・[音声クレジット](EP015_audio_README.txt)。',
       '', '## 映像と音声', '',
       '|版|総尺|8分10秒との差|フレーム数|ショット数|音量 LUFS|ピーク dBTP|',
       '|---|---:|---:|---:|---:|---:|---:|']
    for v in versions:
        report.append(f"|{v['lang']} {1080*v['size_factor']}p|{clock(v['total'])}|{v['total']-490:+.3f}秒|{v['n']}|{v['shots']}|{v['sound']['input_i']}|{v['sound']['input_tp']}|")
    report.extend(['', '全ショットを個別にデコードし、共通オープニングとエンドカードを含め、非圧縮フレームを各版1つのエンコーダーへ入力。通常3本は全フレームの画素形式・解像度が各1種類、PTSの間隔が一定。字幕入り2本を含む5本はH.264 High / yuv420p / 30fps、全編連続デコード警告0。英語4Kはショットごとにチェックポイントを作成した。共通OP・EDは1080pの共通版を拡大。',
       '', 'BGMはQO_THEME_A02。通常3本とも−60 dB以下が1秒以上続く無音は0件。オープニングはP02の後に4秒。エンドカードは英 '+clock(en['total']-10)+'、日 '+clock(ja['total']-10)+' から各10秒。',
       '', '### 字幕・画面内文字', '', '|版|字幕本文|最短|最大字数/行|字幕上端|ボード等との間隔*|素材注記との間隔*|','|---|---|---:|---:|---:|---:|---:|'])
    for v in versions:
        lang=v['lang'];s=v['size_factor'];rec=ROOT/lang/'records'
        sub=read(rec/'subtitle_validation.json'); top=read(rec/'subtitle_layout_validation.json')['minimum_top']
        assert sub['script_matches'] and sub['count']==106
        report.append(f"|{lang} {1080*s}p|106件・台本と一致|{sub['min_seconds']:.3f}秒|{sub['max_line']}|{top*s}px|{v['gap']}px|{v['art_gap']}px|")
    report.extend(['','* 1080pは全106キューを字幕入り版と同じlibass設定で描画し、字幕背景箱の最も高い上端と画面要素の最下端から算出した保守的な間隔。ボード最下段は外枠までを含む。4K欄は1080pの字幕位置を2倍して比較した参考値。英日とも1キュー2行以内。','',
         '|版・種類|最小コントラスト|枠内最小余白|主要英字行の最小字高|','|---|---:|---:|---:|'])
    for v in versions:
        s=v['size_factor']
        for tag, keys in [('証拠ボード',{'D_board_empty','D_board_sun','D_board_sun_return','D_board_calc','D_board_both','D_board_all'}),
                          ('月の帯',{'D_count'}),('地図',{'D_map'}),('暦の模式図',{'D_markers'})]:
            rows=[r for r in v['qc']['layout'] if r['key'] in keys]
            heads={v.split('｜')[0] for k,v in WORDS.items() if k in ('rome','temple','margin','leo','tertullian','sermon','augustine','pliny')}
            if tag=='月の帯':heads={'MAR 25','DEC 25','+ 9 months'}
            if tag=='地図':heads={'ROME','ANTIOCH'}
            if tag=='暦の模式図':heads={'DEC 25 · WINTER SOLSTICE','MAR 25 · SPRING EQUINOX'}
            heights=[r['ink_height'] for r in rows if r['text'] in heads]
            assert heights and min(heights)>=(40 if tag=='証拠ボード' else 52)*s
            pads=[r['padding'] for r in rows if r['padding'] is not None]
            padding=f'{min(pads)}px' if pads else '枠なし'
            report.append(f"|{v['lang']} {s*1080}p・{tag}|{min(r['contrast'] for r in rows):.3f}|{padding}|{min(heights)}px|")
    for v in versions:
        colors=v['qc'].get('decoded_board_colors')
        if colors:
            report.append(f"|{v['lang']} {1080*v['size_factor']}p・盤面中央線（完成映像実測）|{colors['contrast']:.3f}|—|—|")
    report.extend(['','カードと朱札は依頼書の英日両行と照合。左右の主要カードは同じ枠寸法・書体・色。見出しの英字行は1080pで52px以上。通常カードの登場は30fpsの8フレームで表現。','',
       '### ボードを語り終わりから保持した時間', '', '|言語|P05|P07|P10|P12|P14 最終カード静止後|','|---|---:|---:|---:|---:|---:|'])
    for v in (en,ja):
        report.append('|'+v['lang']+'|'+ '|'.join(f"{v['holds'][k]:.3f}秒" for k in ('P05','P07','P10','P12'))+f"|{v['board_hold']:.3f}秒|")
    report.extend(['','### 証拠ボードのカード・札の登場', '', '|区間|カードまたは札|英語の合図・実時刻|日本語の合図・実時刻|','|---|---|---|---|'])
    event_lists=[{e['key']:e for e in read(ROOT/lang/'records/phrase_events.json')} for lang in ('en','ja')]
    for key in ['rome','temple','margin','leo','before','saturnalia','tertullian','sermon','augustine','after','neither','pliny']:
        ev=[e[key] for e in event_lists]
        report.append('|'+ev[0]['segment']+'|'+WORDS[key].split('｜')[1]+('・筆者／年代の札' if key=='margin' else '')+'|'+'|'.join(f"{e['words']} · {clock(e['frame']/30)}（f{e['frame']}）" for e in ev)+'|')
    report.extend(['','### 素材とカメラの動き','','全画面の採用素材は20点。D_board_sunはP07前半の続きをミトラスの文頭で再表示し、サトゥルナリアの行を追加した。P06のシリア語からラテン語への移動は「そこで教会の指導者たちは」の頭。P11は第4章のショット割りに従い、西方への言及を頁の最後に先に囲み、「西の人々は」の頭で地図へ切り替えた。','',
       '|素材|各言語の使用回数|英1080p 原寸比|日1080p 原寸比|英4K 原寸比|','|---|---:|---:|---:|---:|'])
    for k in ASSETS:
        report.append('|'+k+'|1|'+'|'.join(f"{v['by_id'][k]:.4f}" for v in versions)+'|')
    report.extend(['','冒頭はサヴォルドの幼子・白布と照らされた手を中心に1.10→1.00倍。原寸比は上表のとおり。冒頭0・1・2・3秒、全ショット先頭／中央／末尾、原文の囲みを検品ZIPへ収録。D05-Aは natus Christus、D06-Aは N. Invicti. CM. XXX. を囲む。D08-Aは左へ90度回転、D14-Aは1748年のラテン語引用の札。','',
        '|動く素材|英1080p p95/中央値|日1080p|英4K|','|---|---:|---:|---:|'])
    motion=[{m['key']:m['ratio'] for m in v['qc']['motion']} for v in versions]
    for k in ASSETS:
        if any(k in q for q in motion):
            report.append('|'+k+'|'+'|'.join(f'{q[k]:.3f}' if k in q else '原寸上限・静止' for q in motion)+'|')
    report.extend(['','各連続カメラ移動は、完成MP4の被写体領域で隣接する全フレームの輝度差を測定。頁の寄りとカードの登場は指定フレームで始まり、その後は静止する演出として別に検品。','',
        '## 本人試聴用の資料','','初回の無置換音声（英87・日92断片）を保存。読みの修正は合成入力に適用し、字幕は台本v02の文言を保持。固有名のTXTは該当文の開始時刻。発音・語りのテンポ・画面の読みやすさ・サムネA/Bの採用は本人試聴とClaudeの確認待ち。[英語の読みと時刻](EP015_pronunciation_en.txt)・[日本語の読みと時刻](EP015_pronunciation_ja.txt)。'])
    report.extend(['','日本語の合成クエリで、200年（ニヒャクネン）、274年（ニヒャクナナジュウヨネン）、336年（サンビャクサンジュウロクネン）、354年（サンビャクゴジュウヨネン）、380年代（サンビャクハチジュウネンダイ）、1721年（センナナヒャクニジュウイチネン）を確認。「主」はシュ、「一冊」はイッサツ、「一つ目」はヒトツメ、「一覧」はイチラン。素材台帳26点は指定SSD上のSHA-256と再照合した。'])
    return report


def final():
    info=read(ROOT/'records/sharing.json')
    assert info['status']=='verified' and info['draft'] and len(info['assets'])==8
    parts=metrics()
    for lang in ('en','ja'):
        for name in ('credits_'+lang+'.jpg', 'subtitle_'+lang+'_D_board_all.jpg', 'subtitle_'+lang+'_credits.jpg'):
            shutil.copy2(ROOT/lang/'review'/name, SHARE/name)
    for lang, suffix in VERSIONS:
        dest=SHARE/'records'/lang
        dest.mkdir(parents=True,exist_ok=True)
        for name in (f'technical_qc{suffix}.json',f'decoded_plates{suffix}.json','subtitled_review.json','subtitle_layout_validation.json'):
            shutil.copy2(ROOT/lang/'records'/name, dest/name)
    links=['', '## 取得', '', f"[非公開Draft Release]({info['release_url']})（ID `{info['release_id']}`）。8添付すべてをRelease IDから特定したasset IDでREST再取得し、SSD原本とバイト数・SHA-256が一致。匿名取得は404。YouTubeへの投稿・予約は未実施。", '', '[添付別の取得案内・検品画像](README.md)。']
    folder=SHARE.name
    report=('\n'.join(parts+links)+'\n').replace('](EP015_',']('+folder+'/EP015_').replace('](README.md)',']('+folder+'/README.md)')
    (HERE/'wom15_制作結果_v01_20261121.md').write_text(report)
    save(SHARE/'records/sharing.json',info)
    lines=['# Quiet Origins 第15話 確認版v01の取得案内','',f"[非公開Draft Release]({info['release_url']})（ID `{info['release_id']}`）。[制作結果と検品表](../wom15_制作結果_v01_20261121.md)。",'',
        '試聴には字幕入り1080pを使用できます。公開用は英語音声のみ。日本語のM4A・WAVを単体で渡す際は、音声・字幕ZIP内の EP015_audio_README.txt を同梱してください。','',
        '|添付|asset ID|バイト数|SHA-256|','|---|---:|---:|---|']
    for a in sorted(info['assets'],key=lambda a:a['name']):
        lines.append(f"|{a['name']}|{a['asset_id']}|{a['bytes']:,}|`{a['sha256']}`|")
    lines.extend(['', '[日本語P16](credits_ja.jpg)・[日本語P16と実字幕](subtitle_ja_credits.jpg)・[英語の証拠ボードと実字幕](subtitle_en_D_board_all.jpg)・[日本語の証拠ボードと実字幕](subtitle_ja_D_board_all.jpg)。'])
    lines.extend(['','認証済みのGitHub CLIを使う場合は、次のコマンドの ASSET_ID と FILE_NAME を上の表の値に置き換えてください。','',
       '```sh',f"gh api repos/yasukawa1980/youtube/releases/{info['release_id']}",
       "gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME",'```','',
       '[英語投稿情報](EP015_upload_info_en.md)・[日本語投稿情報](EP015_upload_info_ja.md)・[日本語音声のクレジット](EP015_audio_README.txt)。',
       '',f'SSD保存先は `{ROOT}/deliverables/`。検品ZIPには両言語の全ショット一覧・冒頭4枚・原文行の切り出し・各解像度の測定記録を収録。'])
    (SHARE/'README.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    final()
