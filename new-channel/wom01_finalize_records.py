"""Finalize the reviewed delivery records, without publishing anything."""
import json,hashlib
from pathlib import Path
import os
from datetime import datetime,timezone,timedelta
R=Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve();D=R/'deliverables'
Q=json.loads((R/'records/qc.json').read_text())
Q['checks']['visual_frame_review']='pass: Codex reviewed 13 sampled final frames in contact sheet, two full-size source frames, and the subtitle overlay preview; not a human full watch'
Q['delivery_status']='complete_prototype_ready_for_owner_review'
Q['storage']={name:sum(p.stat().st_size for p in (R/name).rglob('*') if p.is_file()) for name in ['assets','audio','render','deliverables','records','scripts']}
Q['storage']['project_bytes_snapshot']=sum(Q['storage'].values())
Q['storage']['temporary_voice_runtime_bytes']=sum(p.stat().st_size for name in ['/private/tmp/wom_voicevox_py','/private/tmp/wom_voicevox_core'] for p in Path(name).rglob('*') if p.is_file())
jst=timezone(timedelta(hours=9))
start=datetime.fromtimestamp(R.stat().st_birthtime,jst);end=datetime.fromtimestamp((D/'EP001_アヌビス_完成試作_v01.mp4').stat().st_mtime,jst)
Q['timing']={'folder_created_jst':start.isoformat(),'final_video_updated_jst':end.isoformat(),'observed_folder_to_final_minutes':round((end-start).total_seconds()/60,1),'scope':'filesystem observation; excludes any research before folder creation; not human labor or a measured automation savings ratio'}
(R/'records/qc.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n')
size=Q['video']['size_bytes']/1024**2;storage=Q['storage']['project_bytes_snapshot']/1024**3;temporary=Q['storage']['temporary_voice_runtime_bytes']/1024**2
review=f'''# EP001 視聴確認と残作業

**完成試作：10分17秒／日本語／1920×1080・30fps。**

本編は `EP001_アヌビス_完成試作_v01.mp4`（{size:.1f} MiB）。まず `EP001_冒頭90秒.mp4` で声と導入を確認できます。元のナレーションは `../audio/narration.wav`。字幕はSRT・ASSも付属しています。

## 実施した検品

- 本編全体をFFmpegでデコードし、エラーなし。
- 動画と音声の尺は約617.23秒。H.264、AAC・48kHz・ステレオ。
- 本編の統合ラウドネスは {Q['audio']['integrated_lufs']:.2f} LUFS、トゥルーピークは {Q['audio']['true_peak_dbtp']:.2f} dBTP。
- 字幕120文の時刻が順序通りで、本編内に収まることを検証。文の音声ファイルの境界から時刻を作成。
- 最終版の代表13場面、史料画像の原寸2場面、字幕合成の確認画像を目視。文字化け、字幕と出典表示の重なり、史料・模写・AI再現画の識別に重大な問題なし。
- 史料画像10点の公式APIのパブリックドメイン表示、ファイルのハッシュ、構成中の素材の存在を確認。

人による全編視聴・耳での音声確認は未実施です。音量の数値検査だけで、発音や語り口の自然さを保証していません。検品の詳細は `../records/qc.json` と最終フレーム一覧にあります。

## 最終試聴で見る項目

1. VOICEVOX:雀松朱司 の声と速度を採用するか。今回は声・言語を試作用に選択しました。
2. ナウニ、マアト、ナクトアメン、イミウト、アメミト、アメンエムハト一世の読みと聞き取り。
3. 史料と説明の対応、章のつながり、静かなBGMとナレーションのバランス。
4. 公開時は末尾の「付属の資料」の説明を、実際に配置する概要欄・資料への案内に合わせる。

通しの視聴は10分17秒、メモ込みなら15〜25分ほどが目安です。変更はこのエピソード内だけで行い、従来の2チャンネルには反映しません。

## 今回の費用・容量・観測時間

追加の有料契約・有料API呼び出し・クレジット購入は0。Suno・Klingの生成枠は使用せず、既存の組み込み画像生成を4回使用しました。電気代、既存月額、人件費は含めていません。

制作フォルダ全体は約{storage:.2f} GiB（検品時点）。このほか一時領域の音声ランタイム・モデルは約{temporary:.1f} MiB。動画の区間キャッシュ・映像マスターも保存しており、これは最小限のアーカイブ容量ではありません。今回は静止画と図解を動かす構成で、Klingの多数の動画素材を使う場合の容量とは異なります。

フォルダ作成 {start.strftime('%H:%M')}〜最終MP4更新 {end.strftime('%H:%M')} の観測区間は約{Q['timing']['observed_folder_to_final_minutes']:.1f}分。この範囲より前の調査、本人の試聴、今後の修正・投稿は含めず、人の作業時間でもありません。初回の区間映像の書き出しは合計約9.3分。80%の自動化・時間削減を達成したという実測値はまだありません。

## 公開と引き継ぎ

本編は確認できる完成試作です。新チャンネルの開設、アップロード、予約、公開、有料契約追加は実施していません。Whispers of Japan・IRO Soundsの制作物、設定、公開予約、定期実行も変更していません。

Claudeへは同じフォルダの `Claudeへの制作引き継ぎ.md` を渡してください。台本・出典・素材・再生成スクリプトを同封しました。CodexからClaudeへの送信や起動は行っていません。
'''
(D/'視聴確認と残作業.md').write_text(review)
readme=R/'README.md';s=readme.read_text().replace('まとめます。','まとめました。').replace('保存します。','保存しました。').replace('完成後に技術検品と画面の確認を行い、結果を','技術検品と代表画面の確認を完了し、結果を').replace('へ記録します。','へ記録しました。').replace('全出典は`records/content.json`と納品台本に記載します。','全出典は`records/content.json`と納品台本に記載しています。');readme.write_text(s)
manifest=[]
for p in sorted(D.glob('*')):
    if p.is_file() and p.name!='SHA256SUMS.txt':manifest.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name)
(D/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n')
print('FINALIZED',round(storage,2),'GiB',Q['timing'])
