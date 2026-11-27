"""Review measurements come from the decoded master and its timed source plates."""
from collections import Counter
from pathlib import Path
import shutil, subprocess
from PIL import Image
from wom16_art import ASSETS,BOXES,NOTES,KEYS,timeline
from wom16_voice import ROOT,HERE,read,sha
from wom16_graphics import CARDS
OUT=ROOT/'deliverables'
GUIDE=HERE/'wom16_確認版_v01_20261127'
REPORT=HERE/'wom16_制作結果_v01_20261127.md'
VERSIONS=[('en','',1),('ja','',1),('en','_4k',2)]
def time(t):return f'{int(t)//60}:{t%60:06.3f}'
def table(rows):
    return ['|'+'|'.join(map(str,row))+'|' for row in [rows[0],['---']*len(rows[0]),*rows[1:]]]
def audio_hash(f):
    return subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(f),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def metrics():
    body=['# Quiet Origins 第16話「セイレーンはいつ人魚になったのか」確認版v01','',
          '承認コミット `aeb1b4e4`。英語台本は14区間・739語、日本語台本は14区間・1,883字。SSD上の素材26点はSHA-256が台帳と一致。','',
          '## 尺と音量','']
    checked=[]; data=[]
    for lang,tail,s in VERSIONS:
        dst=ROOT/lang;recs=dst/'records';q=read(recs/f'technical_qc{tail}.json')
        m=read(recs/'master_timeline.json');subs=read(recs/'subtitle_validation.json');shots=read(recs/f'render_shots{tail}.json')
        tag=lang+' '+str(1080*s)+'p';data.append((tag,q,m,subs,shots,s,lang))
        f=dst/'deliverables'/q['file'];ah=audio_hash(dst/f'deliverables/EP016_audio_{lang}.m4a')
        assert audio_hash(f)==ah
        if not tail:
            review=read(recs/'subtitled_review.json')
            assert audio_hash(dst/'deliverables'/review['file'])==ah
        d=m['duration_seconds'];checked.append([tag,time(d),f'{d-390:+.3f}',q['decoded_frames'],len(shots),q['loudness']['input_i'],q['loudness']['input_tp'],time(d-10)])
    body+=table([['版','総尺','6分30秒との差（秒）','フレーム','ショット','LUFS','dBTP','ED開始'],*checked])
    body+=['','英日独立の時間割。P02後に共通OPを4秒、末尾に共通EDを10秒使用。BGMはQO_THEME_A02。各版の全ショットを個別に非圧縮フレームへデコードし、1基のマスターエンコーダーへ投入した。通常3本では全フレームのPTSと画素形式を検査し、字幕入り2本を含むMP4計5本で全編連続デコードを実施。音声は各言語のM4Aとストリームハッシュが一致。通常3本は1秒以上の無音（−60 dB以下）0件。','',
           '## 字幕と画面内の文字','']
    rows=[['版','SRT件数','最短（秒）','最大字数／行','年表の下端から字幕まで（px）','原典注記等から字幕まで（px）','P09注記の外枠から字幕まで（px）']]
    cards=[['版','年表カードの文字コントラスト最小','年表線の実測コントラスト','カードの最小内余白（px）','主要行の最小字高（px）']]
    uses=[['素材','回数／言語',*[item[0]+' 原寸比' for item in data]]]
    for tag,q,m,subs,shots,s,lang in data:
        layout=q['layout'];top=read(ROOT/lang/'records/subtitle_layout_validation.json')['minimum_top']*s
        bottom=max(max(it['ink_box'][3] for it in read(Path(stage['meta']))['text']) for sh in shots if sh['key'] in KEYS for stage in sh['stages'])
        rows.append([tag,subs['count'],f"{subs['min_seconds']:.3f}",subs['max_line'],top-bottom,min(i['gap'] for i in layout if i['key'] in BOXES),top-894*s])
        main=[i for i in layout if i['key'] in KEYS and i.get('padding') is not None]
        cards.append([tag,min(i['contrast'] for i in main),round(q['decoded_board_colors']['contrast'],3),min(i['padding'] for i in main),min(i['ink_height'] for i in main)])
    body+=table(rows)+['','英日とも台本文字列と照合済み。折り返しは最大2行。字幕の上端は確認版と同じlibass設定で全キューを描画して測定した。','']+table(cards)
    body+=['','## カードの登場と保持','']
    events=[['ショット','英語の合図・時刻','日本語の合図・時刻']]
    for k in KEYS[:-1]+['summary']:
        row=[k]
        for lang in ('en','ja'):
            e=next(v for v in read(ROOT/lang/'records/phrase_events.json') if v['key']==k)
            row.append(e['words']+' · '+time(e['frame']/30)+f"（f{e['frame']}）")
        events.append(row)
    body+=table(events)
    for tag,q,m,subs,shots,s,lang in data[:2]:
        vals=[a['id']+' '+f"{a['end']-a['speech_end']:.3f}秒" for a in m['segments'] if a['id'] in ('P02','P05','P08','P10','P12')]
        p09=next(x for x in shots if x['key']=='SR06-H')
        body+=['',tag+' の語り終わりから区間末尾まで。'+'、'.join(vals)+'。P09注記は '+time(p09['start']/30)+'〜'+time(p09['end']/30)+' の全区間。']
    body+=['','カードは各8フレームで上から着地。4段階の年表は、前のカードを残して史料の登場順を見せるための継続表示。P12は4枚を保ち、最終文の頭から下段のまとめを加えた。各カードは依頼書と文字列照合済み。','']
    for card in CARDS:
        assert card in (HERE/'wom16_制作依頼_20261127.md').read_text()
    allow=set(ASSETS)|set(KEYS)|{'credits','opening','endcard'}
    for _,q,m,subs,shots,s,lang in data:
        assert {v['key'] for v in shots}==allow
    for k in ASSETS:
        use=[sum(sh['key']==k for sh in shots) for _,q,m,subs,shots,s,lang in data]
        assert use==[1,1,1]
        uses.append([k,1,*[f"{max(i['scale'] for i in q['scales'] if i['key']==k):.4f}" for tag,q,m,subs,shots,s,lang in data]])
    body+=['## 素材使用回数と最大表示倍率','','各言語で器物・頁・絵は18点を各1回使用。SR01-B/C/D、SR03-C/D、SR09-D/E、SR14-Bの使用は0回。年表5ショットと共通OP・EDおよびクレジットを合わせて各26ショット。','']+table(uses)
    body+=['','冒頭はSR01-Aの顔と翼。英語4Kは原寸上限の範囲で1.10→1.00倍相当の引きを行い、引き終わりで元写真の幅を超える左右の余白には同じ写真の背景端の列を延長した。器物の画素には補筆していない。720px高の0秒検品画では、顔の髪際から翼の下縁までを目視で採り、1080p版は約600px以上、4K版は約540px以上（それぞれ画面高の約83%以上、約75%以上）。冒頭0〜3秒の完成フレームを検品ZIPに収録。','', '## 英語4K版 P06 の本人承認事項','',
           '2026-11-27本人承認。SR12-A（実寸911×1,352px）は英語4Kで最初の60フレームを画面中央に原寸表示し、周囲を紙色で埋めた。その後も原寸で該当行を切り出し、「翼を願う行」「顔と声が残る行」の順に2pxの朱線で囲んだ。4K内の頁全体の左上は(1464, 404)px。英日1080p版は頁全体を高さいっぱいに2秒見せてから寄る。原典9頁の囲み抜粋、英日各ショットの先頭・中央・末尾、冒頭0・1・2・3秒を検品ZIPに収録。','',
           '## 動きの検品','']
    motion=[['版','ショット','隣接フレーム差の中央値','p95','p95／中央値']]
    for tag,q,m,subs,shots,s,lang in data:
        for item in q['motion']:
            assert item['ratio']<=2.5,(tag,item)
            motion.append([tag,item['key'],f"{item['median']:.4f}",f"{item['p95']:.4f}",f"{item['ratio']:.3f}"])
    body+=table(motion)+['','## 読みと本人確認','',
       '初回の無置換音声（英62文・日65文）と合成クエリをSSDに保存。字幕には承認台本を用いた。英語は sirène、sirena、Boeotia、Euripides、Ovid、Isidore、日本語は「臍」「ヘレネ」の合成入力を修正。日本語の年・巻数・人数の読みと、対象語を含む文の時刻は試聴用TXTに収録。最終的な固有名の発音、テンポ、年表と注の読みやすさ、サムネA・Bの選択は本人試聴およびClaude確認待ち。']
    return '\n'.join(body)+'\n'
def write_guide():
    GUIDE.mkdir(exist_ok=True)
    for pattern in ('EP016_upload_info_*.md','EP016_source_credits.md','EP016_pronunciation_*.txt','EP016_audio_README.txt'):
        for p in OUT.glob(pattern):shutil.copy2(p,GUIDE/p.name)
    state=ROOT/'records/sharing.json'
    shared=read(state) if state.exists() else {}
    delivered=shared.get('status')=='verified'
    status=('非公開Draft Releaseの8添付をRESTで再取得し、バイト数とSHA-256が一致。'+shared['release_url'] if delivered else 'SSDで検品・梱包済み。git は github.com の名前解決に失敗し、gh は api.github.com に接続できなかった。非公開Draft Releaseの作成・添付・REST再取得とリモートブランチへの反映は未完了。')
    files=sorted([*OUT.glob('*.mp4'),*OUT.glob('*.zip')])
    assert len(files)==8
    text=['# 第16話 確認版v01 取得案内','',status,'',str(OUT),'','英語／日本語の字幕入り1080pはファイル名に subtitled_review を含む。通常版・英語4Kは外付けSRT用。音声とSRT、サムネと投稿情報、検品画像と記録はそれぞれZIPに同梱。','']
    text+=table([['ファイル','バイト数','SHA-256'],*[[p.name,p.stat().st_size,sha(p)] for p in files]])
    (GUIDE/'README.md').write_text('\n'.join(text)+'\n')
    REPORT.write_text((ROOT/'records/technical_review.md').read_text()+'\n## 納品\n\n'+status+' [添付別の取得案内](wom16_確認版_v01_20261127/README.md)。\n')
if __name__=='__main__':
    import sys
    if 'guide' in sys.argv:write_guide()
    else:(ROOT/'records/technical_review.md').write_text(metrics())
