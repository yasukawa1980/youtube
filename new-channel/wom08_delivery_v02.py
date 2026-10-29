"""第8話v02の出典追記。v01の英日文章と発音抜粋は維持する。"""
import os
os.environ['WOM08_ROOT']='/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v02_20261030'
import shutil
from wom08_produce import ROOT,REPO,read,save,sha
OLD=ROOT.parent/'確認版_v01_20261029'
def main():
 color=read(ROOT/'records/color_assets_v02.json');selected=[a for a in color['assets'] if a['selected']]
 credit=(OLD/'deliverables/EP008_source_credits.md').read_text()+'\n## v02追加：The Metropolitan Museum of Art (Open Access / CC0)\n\n'
 for a in selected:
  credit+=f"### {a['id']} — {a['title']} / {a['object_number']}\n\n{a['artist']}、{a['date']}。The Metropolitan Museum of Art。\n\n{a['object_url']}\n\n条件：{a['rights_statement']}\n\n"+'\n'.join(a['rights_urls'])+f"\n\n取得日：{a['retrieved_at']}。SHA-256：{a['sha256']}。配信画像寸法：{a['dimensions']}。\n\n"
 credit+='C01はフイの墓TT40の壁画を1923–27年に模写したもの。KV62の壁画ではない。C02・C04は同時代の品で、KV62の出土品としては扱わない。C04は現代の再連結。C03はペルネブの礼拝室で、台本が引用するヘテプヘルアクティの礼拝室とは別の墓。\n'
 (ROOT/'deliverables/EP008_source_credits.md').write_text(credit)
 addition='\nThe Metropolitan Museum of Art — Open Access (CC0): Wilkinson, Tomb of Huy facsimile (1923–27), 30.4.21; signet ring, 22.9.3; Perneb chapel, 13.183.3; necklace (modern restringing), 66.99.163.\nhttps://www.metmuseum.org/hubs/open-access\n'
 for l in ['en','ja']:
  p=OLD/f'deliverables/EP008_upload_info_{l}.md';s=p.read_text();s=s.replace('\nEnglish voice:',addition+'\nEnglish voice:');s=s.replace('Kling64クレジット（379→315）。','v02はv01のろうそく映像を再利用。追加生成・支出0。')
  s=s.replace('本人の試聴待ち。','本人のv02全編視聴待ち。')
  disclosure=('The Huy scene is a 1923–27 facsimile from another tomb. Color objects are contemporary examples, not KV62 finds. Perneb is a different chapel from the one quoted. Archival photographs use a single warm tone.\n' if l=='en' else 'フイの場面は別の墓の1923–27年の模写です。カラーの品は同時代の資料でKV62の出土品ではありません。ペルネブは引用された礼拝室とは別の墓です。発掘写真には単色の暖かい色調を付けています。\n')
  s=s.replace('\nChapters\n','\n'+disclosure+'\nChapters\n') if l=='en' else s.replace('\nチャプター\n','\n'+disclosure+'\nチャプター\n')
  body=s.split('## Description\n\n')[1].split('## 制作メモ')[0];assert len(body)<=5000,(l,len(body));(ROOT/f'deliverables/EP008_upload_info_{l}.md').write_text(s)
 shutil.copy2(OLD/'records/chapters.json',ROOT/'records/chapters.json')
 md='# 第8話v02 追加カラー資料の選定（2026-10-30）\n\n各IDで2〜3候補を確認し、異なる4作品を採用。第1〜7話の記録を作品IDの数字境界で照合し、一致0件。人の遺体・ミイラを含む画像なし。画像は作品ページのPublic Domain表示とMet Open AccessのCC0方針を確認した。\n\n'
 byid={a['met_id']:a for a in color['assets']}
 for cid,ids in color['candidate_groups'].items():
  md+=f"## {cid}\n\n採用：Met {color['selection'][cid]}。{color['reasons'][cid]}\n\n"
  for oid in ids:
   a=byid[oid];md+=f"- [{a['title']}（{a['object_number']}）]({a['object_url']}) — {a['artist']}、{a['date']}。\n"
 md+='\nC02の指輪は1922年寄贈の22.9.3、C04の首飾りは1966年購入の66.99.163で現行所蔵ページを確認。2010年の返還品を選定していない。C03は彩色が残るペルネブ内壁を選び、他の2候補は不採用。C01の船の模写は王への貢ぎ物が見える採用品より語りとの対応が弱いため不採用。\n\n候補全7点の取得URL・権利URL・取得日・寸法・SHA-256は [JSON台帳](wom08_追加カラー素材_20261030.json) に保存。原寸はMacの素材フォルダに保存し、Gitには確認JPGのみ。追加生成・購入・支出0。\n'
 (REPO/'new-channel/research/wom08_追加カラー素材_20261030.md').write_text(md)
 print('V02 METADATA COMPLETE',flush=True)
if __name__=='__main__':main()
