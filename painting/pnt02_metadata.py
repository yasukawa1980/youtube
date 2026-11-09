"""Local upload-description drafts from approved content and unchanged audio timing."""
import re
from pnt02_produce import REPO,ROOT,read

def main():
 research=(REPO/'painting/research/pnt02_原典訳文_20261110.md').read_text()
 urls={}
 for row in research.splitlines():
  m=re.match(r'\|(S\d+)\|',row)
  if m:urls[m[1]]=re.findall(r'\]\((https?://[^)]+)\)',row)
 for lang in ['en','ja']:
  c=read(ROOT/'records'/('content_en.json' if lang=='en' else 'content.json'))
  timeline=read(ROOT/lang/'records/master_timeline.json')
  description=('A winter night in 1776, a flag adopted in 1777, and a painting made about seventy-five years after the crossing. Follow Emanuel Leutze’s Washington Crossing the Delaware from the river to a studio in Düsseldorf and an exhibition in New York.' if lang=='en' else '1776年の冬の夜、1777年に定められた旗、そして渡河のおよそ75年後に描かれた絵。「デラウェア川を渡るワシントン」の歩みを、川からデュッセルドルフのアトリエ、ニューヨークの展示までたどります。')
  lines=['# '+c['title'],'','確認版v01の投稿情報案。未投稿・未予約。章時刻は英日それぞれの独立タイムラインによる。本人確認後に使用する。','','## タイトル','',c['title'],'','## 説明欄','',description,'','Quiet Origins — Origins of a Masterpiece / 名画の由来','','CHAPTERS / チャプター']
  for i,ch in enumerate(c['chapters']):
   start=0 if i==0 else next(s['start'] for s in timeline['segments'] if s['chapter']==ch['id'])
   t=int(start);lines.append(f'{t//60:02d}:{t%60:02d} {ch["title"]}')
  lines+=['','SOURCES / 出典','Washington’s letter is cited from the Founders Online transcription, and the flag resolution from the U.S. National Archives republication. / ワシントンの手紙はFounders Onlineの翻刻、大陸会議の決議は米国国立公文書館の再掲で確認。','']
  for s in c['sources']:
   lines.append(s['title']);lines.extend(urls[s['id']]);lines.append('')
  lines+=['IMAGE CREDITS / 素材クレジット','Emanuel Leutze, Washington Crossing the Delaware, 1851. The Metropolitan Museum of Art, 97.34. Gift of John Stewart Kennedy, 1897. Open Access, CC0. Full painting, three details and gallery view.','https://www.metmuseum.org/art/collection/search/11417','https://www.metmuseum.org/policies/image-resources','Des Deutschen Vaterland von Moritz Arndt, 1848. Staatliche Museen zu Berlin, Kunstbibliothek, 1900,682. Public Domain Mark 1.0. Photo: Dietmar Katz.','https://id.smb.museum/object/3964830','','VOICE & MUSIC / 声・音楽','English narration: Kokoro / Heart (af_heart)','日本語ナレーション：VOICEVOX：冥鳴ひまり','Music: Quiet Origins Theme A02 (QO_THEME_A02) — Suno','','#QuietOrigins #ArtHistory #WashingtonCrossingTheDelaware','']
  p=REPO/f'painting/pnt02_確認版_v01_20261110/PNT02_upload_info_{lang}.md';p.write_text('\n'.join(lines))
  print(lang,'6 chapters,',len(c['sources']),'sources')
if __name__=='__main__':main()
