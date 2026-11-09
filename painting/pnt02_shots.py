"""Pure shot/timing plan from unchanged pnt02 speech and subtitle records."""
import re
from pathlib import Path
from pnt02_produce import ROOT,OP,END,read

CORRECTION='123845503f696780213f7f586fcd22c2e661a8f8'

def plan(lang,root=ROOT):
 m=read(root/lang/'records/master_timeline.json')
 seg={s['id']:s for s in m['segments']}
 subs=read(root/lang/f'records/subtitle_cues_{lang}.json')['cues']
 events=[];shots=[]
 clean=lambda t:re.sub(r'\s+','',t.lower())
 def at(p,en,ja):
  target=en if lang=='en' else ja
  c=next(c for c in seg[p]['cues'] if clean(target) in clean(c['text']))
  offset=clean(c['text']).index(clean(target))
  for page in [q for q in subs if q['sentence_id']==c['id']]:
   n=len(clean(page['text']))
   if offset<n:
    f=round(30*(page['start']+offset/n*(page['end']-page['start'])))
    events.append(dict(segment=p,phrase=target,sentence_id=c['id'],frame=f,time=f/30,method='Native sentence / subtitle page with character-offset interpolation; not forced alignment'))
    return f
   offset-=n
  raise ValueError(target)
 st=lambda p:0 if p=='P01' else round(seg[p]['start']*30)
 ed=lambda p:round(seg[p]['end']*30)
 tick1849=at('P08','eighteen forty-nine','1849年')
 today=at('P12','where it hangs today','今もそこに')
 def year(p,f):
  if p in ['P03','P04','P05']:return '1776'
  if p=='P06':return '1777'
  if p in ['P07','P10']:return '—'
  if p=='P08':return '1849' if f>=tick1849 else '—'
  if p=='P09':return '1849'
  if p=='P11':return '1851'
  if p=='P12':return 'today' if f>=today else '1897'
  return None
 def shot(p,k,a,b,changes=None):
  changes=sorted(changes or [(a,0)])
  points=sorted(set([a,b]+[f for f,_ in changes if a<f<b]+[f for f in [tick1849,today] if a<f<b]))
  entries=[]
  for lo,hi in zip(points,points[1:]):
   stage=next((s for f,s in reversed(changes) if f<=lo),0)
   entries.append(dict(start_frame=lo,frames=hi-lo,stage=stage,year=year(p,lo)))
  assert b>a
  shots.append(dict(key=k,segment_id=p,start=a/30,end=b/30,frames=b-a,stages=entries))
 def brand(key,path):
  a,b=m['brand_intervals'][key]
  shots.append(dict(key=key,segment_id='BRAND',start=a,end=b,frames=round((b-a)*30),stages=[],encoded_file=str(path)))
 shot('P01','V01_full_1',0,ed('P01'))
 # P02 names broad periods rather than all six exact years. Illuminate pairs at
 # the three spoken anchors, then shrink over the final second as in painting01.
 river=at('P02','a winter night','冬の夜')
 studio=at('P02',"a painter's studio",'デュッセルドルフ')
 city=at('P02','the city','この絵が有名')
 intro=[(st('P02'),-1),(river,0),(round((river+studio)/2),1),(studio,2),(round((studio+city)/2),3),(city,4),(min(ed('P02')-31,city+30),5)]
 intro += [(ed('P02')-30+i,6+i) for i in range(30)]
 shot('P02','D_timeline_intro',st('P02'),ed('P02'),intro);brand('opening',OP)
 shot('P03','D_letter_head',st('P03'),ed('P03'))
 shot('P04','D_letter',st('P04'),ed('P04'),[(st('P04'),0),(at('P04','He called it','ワシントンはそれを'),1)])
 shot('P05','V01_D1',st('P05'),ed('P05'))
 f=at('P06','On June fourteenth','1777年6月14日')
 shot('P06','V01_D2',st('P06'),f);shot('P06','D_resolution',f,ed('P06'))
 shot('P07','D_leutze',st('P07'),ed('P07'),[(st('P07'),0),(at('P07','As a child','子どものころ'),1),(at('P07','In eighteen forty-one','1841年'),2)])
 shot('P08','V10',st('P08'),ed('P08'))
 f=at('P09','One of them','その一人')
 shot('P09','V01_D3',st('P09'),f);shot('P09','D_whittredge',f,ed('P09'))
 shot('P10','D_bremen',st('P10'),ed('P10'),[(st('P10'),0),(at('P10','The next year','翌年'),1),(at('P10','nineteen forty-two','1942年'),2)])
 shot('P11','D_1853',st('P11'),ed('P11'),[(st('P11'),0),(at('P11','Two years later','2年後には'),1)])
 shot('P12','V01_room',st('P12'),ed('P12'))
 shot('P13','V01_full_2',st('P13'),ed('P14'))
 shot('P15','credits',st('P15'),ed('P15'));brand('endcard',END)
 assert len(shots)==18
 assert sum(s['frames'] for s in shots)==round(m['duration_seconds']*30)
 assert all(round(a['end']*30)==round(b['start']*30) for a,b in zip(shots,shots[1:]))
 assert len({s['key'] for s in shots})==len(shots)
 for s in shots:
  if s['segment_id'] in ['P07','P10']:assert all(e['year']=='—' for e in s['stages'])
 assert st('P08')<=tick1849<ed('P08')
 assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-7
 return dict(language=lang,correction_commit=CORRECTION,master=m,events=events,shots=shots)
