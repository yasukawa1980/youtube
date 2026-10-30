"""v03の中間映像の動き。未変更24ショットはv02の同じハッシュの測定を引き継ぐ。"""
import os
os.environ.setdefault('WOM08_ROOT','/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v03_20261030')
import copy,csv
from wom08_produce import ROOT,read,save,sha
from wom08_motion_v02 import roi,motion_stats
OLD=ROOT.parent/'確認版_v02_20261030'
CHANGED={'D_illness','D_novels_1869','D_novels_1892','D_warning','D_bmj','D_summary'}
def main():
 old={s['key']:s for s in read(OLD/'records/motion_v02.json')['shots']};checks=[]
 for s in read(ROOT/'records/render_shots.json'):
  if s['segment_id']=='BRAND':continue
  h=sha(ROOT/s['encoded_file'])
  if s['key'] not in CHANGED:
   prior=old[s['key']];assert h==prior['encoded_sha256'];c=copy.deepcopy(prior);c['v02_identical_intermediate_measurement_reused']=True
  else:
   q=motion_stats(ROOT/s['encoded_file'],roi(s));assert q['frame_pairs']==s['frames']-1
   c=dict(key=s['key'],segment_id=s['segment_id'],start=s['start'],end=s['end'],encoded_sha256=h,measurement=q,passed=q['p95_over_median'] is not None and q['p95_over_median']<=2.5)
  checks.append(c);print('MOTION',s['key'],c['measurement']['p95_over_median'],c['passed'],flush=True)
 assert all(c['passed'] for c in checks)
 save(ROOT/'records/motion_v03.json',{'passed':True,'method':'変更した6カードは全隣接フレームを新規測定。未変更の中間物はSHA-256一致を確認してv02の全フレーム測定値を継承。完成したv03動画は別途全隣接フレームを測定する。','shots':checks})
 rows=[{'segment':c['segment_id'],'key':c['key'],'start':c['start'],'end':c['end'],'median':c['measurement']['median_mad_8bit'],'p95':c['measurement']['p95_mad_8bit'],'ratio':c['measurement']['p95_over_median'],'passed':c['passed']} for c in checks]
 with (ROOT/'deliverables/EP008_motion_v03.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
