"""Prepare approved EP005 posting text and verify inputs against private release manifests."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parent
MAIN=Path('/Users/ryo/Desktop/新チャンネル/EP005_Tengu/確認版_v02_20261024/deliverables')
SHORT=Path('/Users/ryo/Desktop/新チャンネル/ショート/EP005_確認版_v01_20261024/deliverables')
def api(endpoint,binary=False):
 args=['gh','api']+(['-H','Accept: application/octet-stream'] if binary else [])+[endpoint]
 b=subprocess.check_output(args);return b if binary else json.loads(b)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def verify(rid,folder,names):
 r=api(f'repos/yasukawa1980/youtube/releases/{rid}');assert r['draft']
 a=next(a for a in r['assets'] if a['name']=='SHA256SUMS_shared.txt')
 b=api(f'repos/yasukawa1980/youtube/releases/assets/{a["id"]}',True)
 assert b==(folder/'SHA256SUMS_shared.txt').read_bytes()
 expected={line.split(maxsplit=1)[1].strip():line.split()[0] for line in b.decode().splitlines()}
 rows=[]
 for name in names:
  p=folder/name;actual=digest(p);assert actual==expected[name]
  rows.append(dict(path=str(p),name=name,bytes=p.stat().st_size,sha256=actual,release_id=rid,manifest_asset_id=a['id']))
 return rows
text=(REPO/'wom05_投稿情報_EP005_確定版_20261024.md').read_text()
en,ja=re.findall(r'```\n(.*?)\n```',text,re.S)
sources=en.split('Sources\n',1)[1].split('\nReferences only',1)[0]
museums=en.split('The Metropolitan Museum of Art, Open Access:',1)[1].split('\nNational Diet Library',1)[0]
museums='The Metropolitan Museum of Art, Open Access:'+museums
ja=ja.replace('（英語版の「Sources」の6行をそのまま貼る）',sources).replace('（英語版の「The Metropolitan Museum of Art, Open Access:」から「https://collections.lacma.org/object/89199」の行までをそのまま貼る）',museums)
assert en.count('```')==ja.count('```')==0 and 'そのまま貼る' not in ja and len(en)<=5000 and len(ja)<=5000
checks=verify(422536334,MAIN,['EP005_Tengu_en_v02_1080p30.mp4','EP005_audio_ja.wav','EP005_Tengu_en_v02_1080p30.srt','EP005_Tengu_ja_v02_1080p30.srt','EP005_thumbnail_met_24145.jpg'])
checks+=verify(422594196,SHORT,[f'QO_short_EP005_T{i}_v01.mp4' for i in range(1,4)])
request=(REPO/'wom_ショート投稿依頼_EP005_20261024.md').read_text()
titles=re.findall(r'^\| (10/\d+（.）\d+:\d+) \| `([^`]+)` \| (.+?) \| (.+?) \|$',request,re.M);assert len(titles)==3
blurbs=re.findall(r'^\| (T[123]) \| (.+?) \| (.+?) \|$',request,re.M);assert len(blurbs)==3
headings={'met':'The Metropolitan Museum of Art, Open Access:','ndl':'National Diet Library Digital Collections (public domain):','lacma':'Los Angeles County Museum of Art:'}
urls={'met':'https://www.metmuseum.org/hubs/open-access','ndl':'https://dl.ndl.go.jp/','lacma':'https://collections.lacma.org/object/89199'}
specs={'T1':[('ndl','- Nihon Shoki, vols. 23–24')],'T2':[('met','- Shibata Zeshin,')],'T3':[('met',"- Mask in the Shape of a Mountain Demon's Face"),('ndl','- Katsushika Hokusai, Hokusai Manga'),('lacma','- Kawanabe Kyōsai,')]}
expected={'T1':{'V01','ndl_1182143_010'},'T2':{'met_57203','V02'},'T3':{'met_24145','ndl_851648_028','lacma_89199'}}
usage=list(csv.DictReader((SHORT/'asset_usage.csv').open()))
shorts=[]
for i,((date,name,title_en,title_ja),(id,blurb_en,blurb_ja)) in enumerate(zip(titles,blurbs)):
 assert {a['asset_id'] for a in usage if a['short_id']==id}==expected[id]
 credits=[]
 for museum,prefix in specs[id]:
  line=next(line for line in en.splitlines() if line.startswith(prefix));credits += [headings[museum],line,urls[museum]]
 common='Images — Public Domain / CC0\n'+'\n'.join(credits)+'\nNarration: Kokoro / Heart (af_heart), synthetic speech.'+(' AI reconstruction labelled on screen (Kling AI).' if id in ['T1','T2'] else '')+'\nMusic: original ambient score by Quiet Origins.'
 den=blurb_en+'\nFull episode: https://youtu.be/{{EP005_VIDEO_ID}}\n\n'+common+'\n\n#Shorts #History #Tengu #JapaneseFolklore'
 dja=blurb_ja+'\n本編：https://youtu.be/{{EP005_VIDEO_ID}}\n\n'+common+'\n\n#Shorts #歴史 #天狗 #日本の伝説'
 shorts.append(dict(id=id,file=str(SHORT/name),title_en=title_en,title_ja=title_ja,description_en_template=den,description_ja_template=dja,schedule_jst=['2026-10-30T12:00:00+09:00','2026-10-30T18:00:00+09:00','2026-10-31T12:00:00+09:00'][i]))
payload=dict(channel=dict(name='Quiet Origins',handle='@QuietOriginsJP',id='UCfLJOojEY9VB3rvrjICk90Q'),main=dict(title_en='The First Tengu Was a Star | What the Oldest Sources Say',title_ja='最初の天狗は、星だった',description_en=en,description_ja=ja,schedule_jst='2026-10-27T09:00:00+09:00',end_screen_seconds=[358.833333,368.833333]),shorts=shorts,files_verified=checks,settings=dict(language='English',category='Education',made_for_kids=False,altered_content=True),status='prepared_no_uploads_yet')
out=REPO/'records/posting_EP005_prepared_20261024.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(verified_files=len(checks),main_description_chars=dict(en=len(en),ja=len(ja)),shorts=len(shorts),output=str(out)),ensure_ascii=False))
