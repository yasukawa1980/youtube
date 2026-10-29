"""Collect verified EP007 handoff evidence, keeping media out of Git."""
from pathlib import Path
import shutil
from wom07_produce import ROOT,REPO,read,save

def main():
 records=ROOT/'records'; share=read(records/'sharing.json');assert share['status']=='verified' and share['draft']
 for name in ['qc_v01','continuous_qc','final_video_motion','episode_specific_qc','subtitle_layout_validation']:
  assert read(records/(name+'.json'))['passed'],name
 out=REPO/'new-channel/wom07_確認版_v01_20261029';out.mkdir(exist_ok=True)
 evidence=['brand_audio_boundary_correction','sharing','qc_v01','continuous_qc','final_video_motion','motion_v01','episode_specific_qc','audio_qc','bgm_band_comparison','subtitle_validation','subtitle_layout_validation','sentence_boundary_validation','visual_style_review','kling_generation','reading_replacements','pronunciation_locations','first_pass_preserved','container_precision','encoding_method','release_archives','render_shots','source_assets','master_timeline','thumbnail_qc']
 for name in evidence:shutil.copy2(records/(name+'.json'),out/(name+'.json'))
 for pattern in ['*.srt','*.md','*.csv','*pronunciation*.txt']:
  for p in (ROOT/'deliverables').glob(pattern):
   if p.suffix in ['.md','.csv']:(out/p.name).write_text(p.read_text().rstrip()+'\n')
   else:shutil.copy2(p,out/p.name)
 previews=out/'確認画像';previews.mkdir(exist_ok=True)
 from PIL import Image
 for pattern in ['opening_*.jpg','subtitle_opening_*.jpg','continuous_en_sheet_*.jpg','ferris_endpoint_scope.jpg','V*_source_contact.jpg']:
  for p in (ROOT/'review').glob(pattern):
   im=Image.open(p);im.thumbnail((1280,1280));dst=previews/p.name;im.save(dst,quality=85,optimize=True);assert dst.stat().st_size<=1000000
 q=read(records/'qc_v01.json');a=read(records/'audio_qc.json');motion=read(records/'final_video_motion.json');ratio=max(x['ratio'] for x in motion['checks'] if x['motion_ratio_applicable']);band=read(records/'bgm_band_comparison.json')
 lines=['# EP007 暫定確認版 v01（2026-10-29）','', '**技術検査は合格。画風と本人の試聴は未承認で、完成版ではない。**','',f"[非公開Draft Release]({share['release_url']})（ID `{share['release_id']}`、8資産）。GitHubで本人の権限を使って取得する。匿名アクセスは全件404。REST再取得のSHA-256を全8資産で照合済み。公開しない。",'', '## 取得物','', '- `EP007_Thanksgiving_en_v01_subtitled_review_1080p30.mp4`：英語・字幕付き確認版。','- `EP007_Thanksgiving_ja_v01_subtitled_review_1080p30.mp4`：日本語・字幕付き確認版。','- `EP007_Thanksgiving_{en,ja}_v01_1080p30.mp4`：字幕焼き込みなし。','- `EP007_audio_and_subtitles.zip`：英日WAV/M4A/SRT、発音確認用音声と時刻一覧。','- `EP007_thumbnails_and_metadata.zip`：サムネ3案・168px比較、投稿情報、出典。','- `EP007_QA_records.zip`：検査記録と連続デコード確認画像。','- `EP007_AI_scene_review.zip`：採用候補4本と不採用食卓1本の原動画。','', '## 実測結果','',f"- 共通尺 {q['duration_seconds']:.6f}秒、{q['frames']}フレーム、1920×1080、30fps固定、H.264 High / yuv420p。英日映像ストリーム同一。",'- 4本の全編デコードで警告・エラー0。英日それぞれ全21ショットの先頭・中央・末尾を連続デコードから採取。SPS profile_idc=100のみ。',f'- 最終動画の動く16ショットで全隣接フレームのp95/中央値は最大{ratio:.6f}（基準2.5以下）。静止図解3本は元の全差分が0。最終エンコード由来の差分は記録を残し、動きの比率から除外。','- 字幕：英76・日81、最短1.4秒、1行最大英42・日22字、2行以内。台本本文不変。標準/拡大表示で字幕と画面本文が非重複。','- 本人指定の共通A2（QO_THEME_A02）とアメリカ1（QO_AMERICA01）。P04〜P06、P09〜P10でアメリカ1を使用。クロスフェード3秒。']
 for lang,label in [('en','英語'),('ja','日本語')]:
  x=a['languages'][lang];levels=x['levels'];b=x['band_percent'];lines.append(f"- {label}：{levels['input_i']} LUFS / {levels['input_tp']} dBTP。語り{x['voice_during_narration_dbfs']:.3f}、BGM{x['bgm_during_narration_dbfs']:.3f}、休止時BGM{x['bgm_during_full_boost_breaks_dbfs']:.3f} dBFS。帯域比 <200Hz {b['below_200Hz']:.3f}% / 200〜2kHz {b['200_to_2000Hz']:.3f}% / ≥2kHz {b['at_or_above_2000Hz']:.3f}%。")
 lines += [f"- 第6話の共通音源を同じFFT手順で測定すると<200Hzは{band['ep006']['below_200Hz']:.3f}%。申し送りの58%とは測定対象・手順が同一と確認できないため区別する。",'- 共通OPは51.366667〜55.366667秒、エンドカードは349.133333〜359.133333秒。元ファイルのSHA一致、ミックス内ブランド音声のサンプル一致。','- 日本語の各区間末尾の待ちは最大2.440秒。','- 原典12点とAI4点は各1回。P09は権利条件が明確な原画像を確保できず、承認済みD_young。フェリスは色票を除外し、終点でも指定人物範囲を保持。','', '## 未承認事項と次の確認','', '**V01〜V04の画風は指定の絵画風に達していない。** 写実的なCGに近い。初回食卓は現代的カトラリーがあり不採用とし、1回再生成した。合計296/300クレジット、残高675→379。追加生成・購入はしていない。本人・Claudeに現候補の扱いと修正方針を確認してから完成扱いにする。','', '人の目で確認したAI原動画の標本フレームでは人物・読める文字・現代的カトラリーは見られない。標本確認であり、全フレームの意味内容を自動判定したものではない。','', '本人の試聴：','', '1. 英語の Plymouth、Mourt\'s Relation、Massasoit、fowling、venison、Josepha、Cole\'s Hill。','2. 日本語の総督、断食、服喪、ニューイングランド先住民連合、年号。「数行」はすうぎょうへ修正。','3. スマホスピーカーとイヤホンで、新BGMが曲として聞こえ、語りを邪魔しないか。','4. 冒頭0〜3秒で題材が伝わるか。AI4本の画風を採用するか。','5. 先頭から通して連続再生し、乱れと読み違いがないか。音声の聴感確認は未実施。','',f'ローカル成果：`{ROOT}/deliverables/`。動画・音源・原寸素材はGitに含めていない。YouTube未投稿、ReleaseはDraftのまま。','']
 text='\n'.join(lines).replace('人の目で確認したAI原動画の標本フレーム','画像として確認したAI原動画の標本フレーム');(out/'README.md').write_text(text);(REPO/'new-channel/wom07_制作結果_v01_20261029.md').write_text(text)
 (REPO/'new-channel/wom07_制作進捗_20261029.md').write_text('# 第7話 制作進捗（2026-10-29）\n\n暫定確認版の技術検査と非公開Draft共有を完了。画風と本人の試聴は未承認。\n\n[制作結果](wom07_制作結果_v01_20261029.md)／[取得案内と検査記録](wom07_確認版_v01_20261029/README.md)を参照。\n')
 print('FINALIZED',out,flush=True)
if __name__=='__main__':main()
