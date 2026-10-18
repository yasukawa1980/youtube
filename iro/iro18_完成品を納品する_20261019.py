"""全検査が通った成果だけを投稿用・SSD・Git共有用に揃える。投稿操作なし。"""
from pathlib import Path
import importlib.util,json,shutil,re
s=importlib.util.spec_from_file_location('finish',Path(__file__).with_name('iro18_完成品を仕上げる_20261019.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 r=m.REVIEW;q=json.loads((r/'完成品検証_main.json').read_text())[0];shorts=json.loads((r/'完成品検証_shorts.json').read_text());check=json.loads((r/'完成画面と章_検証.json').read_text());data=json.loads((m.WORK/'構成.json').read_text())
 assert len(shorts)==4 and len(check['chapters'])==18
 for x in[q]+shorts:assert x['decode']['exit']==0 and x['audio_bitstream_equal_to_source']and m.sha(x['file'])==x['sha256']
 assert check['chapter_text_unchanged']
 lv=q['levels'];v=q['video'];mbps=int(v['bit_rate'])/1e6
 # 原稿と選曲は旧版から必要な変更だけ。実際の原本ハッシュも記録。
 (r/'映像構成.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 sources=[m.TRIAL/f'Kling_編み物試作{i}_原本.mp4'for i in[1,2]]+[m.TRIAL/f'試作{i}_境界修正_犬1.4倍_8秒.mp4'for i in[1,2]]+[m.OLD/f'Kling素材/{n}.mp4'for n in['B1','C','D_v2']]+[m.TRIAL/'18_start_編む手元_犬1.4倍.png',m.WORK/'配信用音声.m4a']
 (r/'入力素材_検証.json').write_text(json.dumps([{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':m.sha(p)}for p in sources],ensure_ascii=False,indent=2)+'\n')
 selected=json.loads((m.OLD/'_work/選曲結果.json').read_text())
 summary=f'''# IRO18「毛糸の季節が、やってきた。」完成検品

**手直し完成・未投稿。本人の通し視聴とClaude完成検品待ち。投稿・予約なし。** [試作2本の合格指示](../iro18_手直し_20261018/Claude検品結果_2本目_20261019.md) を反映。

- **本編**：{q['duration']:.3f}秒（2時間00分17.643秒）、1920×1080・24fps・{mbps:.2f}Mbps、q:v85。全{m.TOTAL:,}コマ復号成功、欠落・重複0。扉v5と間、最後15秒の終了カード。
- **音**：最終AACを全体通しで測定し **{lv['input_i']:.2f} LUFS／TP {lv['input_tp']:.2f} dBTP／LRA {lv['input_lra']:.1f}**。承認済みaac_at版を `--reuse-audio` で無再圧縮コピーし、音声ビットストリームSHA256一致。既存31曲・6系統（Aフェルトピアノ6／Bマリンバ5／C弦四重奏5／Dテナーサックス5／Eビブラフォン5／Fホルン5）・曲順を保持。
- **映像**：合格した試作1・2を898区間へ不規則配置（1={data['take_counts']['1']}、2={data['take_counts']['2']}、連続最大2回）。女性の旧出来事A/Bは不使用。房と糸を含む同一範囲・ぼかし18px、犬1.4倍。瞬き追加・目元貼替え・時間変更・人物ループのクロスフェードなし。1→2・2→1の切替コマも確認。
- **犬の章**：大あくび12回・走る夢6回を旧時刻に維持。章テキストは旧版とバイト一致。全18か所の開始・4秒後と、完成本編0:30・30:00・1:30:00は連結部品との最大画素差0。
- **ショート**：A「ひと目ずつ、ゆっくりと。」／B「もうひと段、編んだら休憩。」。C/Dの題は維持し犬1.4倍。4本×15秒・360コマ、1080×1920、幅608・上下延長なし。全編デコードと最終AAC検査合格、4本とも旧音声とビットストリーム一致。題字は手元・犬を避ける既存の帯。
- **サムネ・本文**：編む女性＋犬1.4倍。題・黄の太字60px「編み物BGM 2時間」・帯を維持、1280×720・{(m.KIT/'iro18_サムネ.jpg').stat().st_size:,}bytes・168px確認済み。日英説明を「編み物を続ける」に修正。章・タグ・ハッシュタグは維持。
- **費用と保存**：今回Suno/Kling追加0、手直しKling累計128/192のまま、残り64不使用・購入なし。Macと指定ESD-02へ保存しSHA256照合。旧本編は元の場所に保持、旧投稿用はコピー保全。移動・削除なし。ESD-EPBは未接続・未同期。

[完成見本](Claude検品用_見本.jpg) ／ [サムネ原寸](iro18_サムネ.jpg) ／ [開始絵新旧・犬の境界](開始画像新旧と犬の境界.jpg) ／ [全18章](完成本編_犬の章18か所.jpg) ／ [全4通りのつなぎ目](試作1と2_全4通りのつなぎ目.jpg) ／ [扉と終了カード](完成本編_扉と終了カード.jpg)

手元6fps：試作1 [前](完成本編_試作1_手元6fps_前半.jpg)・[後](完成本編_試作1_手元6fps_後半.jpg)、試作2 [前](完成本編_試作2_手元6fps_前半.jpg)・[後](完成本編_試作2_手元6fps_後半.jpg)。顔3fps：[試作1](完成本編_試作1_顔3fps.jpg)・[試作2](完成本編_試作2_顔3fps.jpg)。[本編検証](完成品検証_main.json)・[ショート検証](完成品検証_shorts.json)・[保存照合](Mac_SSDコピー検証.json)・[投稿情報](../iro18_アップロード情報.md)。

本編・ショート4本・サムネ・本文：Mac `{m.KIT}`。SSD `/Volumes/ESD-02/BGM/IRO/Chill/18_毛糸の季節がやってきた/完成_20261019/投稿用/`。動画はGitへ入れず、見本と測定を共有。本人の2時間通し視聴は未確認。
'''
 assert selected['track_count']==31
 (r/'Claude検品用_要約.md').write_text(summary)
 for p in [m.R/'iro/iro18_アップロード情報.md']:
  p.write_text(p.read_text().replace('状態：手直し仕上げ中・未投稿。完成後も本人の通し視聴とClaude完成検品待ち。','状態：手直し完成・未投稿。本人の通し視聴とClaude完成検品待ち。'))
 ledger=m.R/'iro/iro18_手直し_20261018/Kling_試作台帳.json'
 j=json.loads(ledger.read_text());assert j['submitted_credits_total']==128 and j['submitted_clips']==2
 j.update(status='手直し完成・未投稿。合格した2本だけ使用、残り64不使用。',additional_generations_for_finalization=0,finalized_date='2026-10-19');ledger.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
 manifest={'main':str(m.MAIN),'shorts':[x['file']for x in shorts],'thumbnail':str(m.KIT/'iro18_サムネ.jpg'),'review':str(r/'Claude検品用_要約.md'),'published':False,'scheduled':False,'extra_generation_credits':0}
 (m.KIT/'納品一覧.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 # 既存投稿用の入口を最新成果へ同期。旧データは既にコピー保全済み。
 for p in m.KIT.iterdir():
  if p.is_file()and p!=m.MAIN:shutil.copy2(p,m.OLD/'投稿用'/p.name)
 for x in shorts:shutil.copy2(x['file'],m.OLD/'ショート'/Path(x['file']).name)
 shutil.copy2(m.KIT/'iro18_サムネ.jpg',m.OLD/'iro18_サムネ.jpg');shutil.copy2(m.KIT/'iro18_サムネ.jpg',m.OLD.parent/'IRO_upload_iro18_thumb.jpg')
 thumb=m.R/'サムネ確認用/IRO Sounds/iro18_サムネ.jpg';thumb.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(m.KIT/'iro18_サムネ.jpg',thumb)
 for p in m.KIT.glob('*.txt'):shutil.copy2(p,m.R/'iro/iro18_投稿用'/p.name)
 shutil.copy2(m.KIT/'納品一覧.json',m.R/'iro/iro18_投稿用/納品一覧.json')
 # 公開本文の変更が指定範囲だけであることを確認。
 for name in ['01_タイトル_日本語.txt','02_タイトル_英語.txt','07_ハッシュタグ.txt','08_タグ.txt','09_再生リスト_タイトル.txt','11_チャプター_犬の動き.txt','15_ショートC.txt','16_ショートD.txt']:
  assert(m.KIT/name).read_bytes()==(m.OUT/'旧投稿用_保全'/name).read_bytes()
 reviewcopy=m.OUT/'検品用';reviewcopy.mkdir(exist_ok=True)
 for p in r.iterdir():
  if p.is_file():shutil.copy2(p,reviewcopy/p.name)
 ssd=Path('/Volumes/ESD-02/BGM/IRO/Chill/18_毛糸の季節がやってきた/完成_20261019');assert ssd.parent.is_dir();copied=[]
 for p in sorted(m.OUT.rglob('*')):
  if not p.is_file() or '_work'in p.relative_to(m.OUT).parts or p.name=='Mac_SSDコピー検証.json':continue
  dest=ssd/p.relative_to(m.OUT);dest.parent.mkdir(parents=True,exist_ok=True);h=m.sha(p)
  if not dest.exists() or m.sha(dest)!=h:shutil.copy2(p,dest)
  assert h==m.sha(dest)
  copied.append({'source':str(p),'destination':str(dest),'bytes':p.stat().st_size,'sha256':h,'match':True})
 (r/'Mac_SSDコピー検証.json').write_text(json.dumps({'date':'2026-10-19','ssd':'ESD-02','ESD_EPB':'未接続・未同期','files':copied},ensure_ascii=False,indent=2)+'\n')
 # 照合表そのものは自己参照ハッシュを避け、コピー後に別途一致確認。
 for base in[reviewcopy,ssd/'検品用']:
  dest=base/'Mac_SSDコピー検証.json';shutil.copy2(r/dest.name,dest);assert m.sha(dest)==m.sha(r/dest.name)
 for link in re.findall(r'\]\(([^)]+)\)',summary):assert (r/link).is_file(),link
 print('納品・旧入口同期・SSD照合完了',len(copied),'files',flush=True)
if __name__=='__main__':main()
