import sys,subprocess
from pathlib import Path
sys.path.insert(0,'new-channel')
from wom05_produce import ROOT,read,save,sha,ff,probe
prior=Path('/Users/ryo/Desktop/新チャンネル/EP004_Pandora/確認版_v02_20261023');master=prior/'deliverables/EP004_Pandora_en_v02_1080p30.mp4';out=[]
for s in read(prior/'records/render_shots.json'):
 if s['segment_id']!='BRAND':continue
 p=ROOT/f'assets/approved_{s["key"]}_encoded.mp4'
 ff(['-ss',s['start'],'-i',master,'-frames:v',s['frames'],'-map','0:v:0','-c','copy','-an','-avoid_negative_ts','make_zero',p])
 v=probe(p)['streams'][0]
 pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));offset=pts[0];tmp=ROOT/f'_work/brand_normalized_{s["key"]}.mp4'
 ff(['-i',p,'-c','copy','-movie_timescale',48000,tmp]);__import__('shutil').copy2(tmp,p)
 v=probe(p)['streams'][0];print(s['key'],v['nb_frames'],v['duration'],s['frames'])
 out.append({'key':s['key'],'segment_id':'BRAND','encoded_file':str(p),'source_master':str(master),'source_start':s['start'],'source_end':s['end'],'frames':s['frames'],'sha256':sha(p)})
save(ROOT/'records/approved_brand_extracts.json',out)
