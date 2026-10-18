"""最終MP4の全編デコード・最終AAC通し測定・コピー同一性を記録する。"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,importlib.util,json,subprocess,re
s=importlib.util.spec_from_file_location('finish',Path(__file__).with_name('iro18_完成品を仕上げる_20261019.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def audiohash(path):
 return subprocess.check_output([m.FF,'-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def loudness(path):
 p=subprocess.run([m.FF,'-hide_banner','-nostats','-i',str(path),'-vn','-af','loudnorm=I=-14:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 j=json.loads(re.findall(r'\{\s*"input_i".*?\}',p.stderr,re.S)[-1]);return{k:float(j[k])for k in['input_i','input_tp','input_lra']}
def decode(tag,path):
 progress=m.WORK/f'完成デコード_{tag}.txt'
 p=subprocess.run([m.FF,'-v','error','-xerror','-progress',str(progress),'-stats_period','10','-hwaccel','videotoolbox','-i',str(path),'-f','null','-'],capture_output=True,text=True)
 assert p.returncode==0,p.stderr[-3000:]
 vals=dict(l.split('=',1)for l in progress.read_text().splitlines()if'='in l)
 assert vals['progress']=='end' and int(vals['dup_frames'])==int(vals['drop_frames'])==0,vals
 return {'exit':0,'decoded_frames':int(vals['frame']),'duplicate_frames':int(vals['dup_frames']),'dropped_frames':int(vals['drop_frames'])}
def main(scope):
 files=[('main',m.MAIN)]if scope=='main'else[(x,m.KIT/f'iro18_ショート_{x}.mp4')for x in'ABCD']
 results=[]
 for tag,p in files:
  print('検品開始',tag,flush=True);j=m.probe(p);v=next(x for x in j['streams']if x['codec_type']=='video');a=next(x for x in j['streams']if x['codec_type']=='audio')
  expected=m.TOTAL if tag=='main' else 360;dims=(1920,1080)if tag=='main'else(1080,1920)
  assert int(v['nb_frames'])==expected and(v['width'],v['height'])==dims and v['r_frame_rate']=='24/1'
  assert a['codec_name']=='aac'and a['sample_rate']=='48000'and a['channels']==2
  with ThreadPoolExecutor(max_workers=2)as pool:
   dl=pool.submit(decode,tag,p);lv=pool.submit(loudness,p);decoded=dl.result();levels=lv.result()
  assert decoded['decoded_frames']==expected
  assert -15.5<=levels['input_i']<=-13 and levels['input_tp']<=-2,levels
  source=m.WORK/'配信用音声.m4a'if tag=='main'else m.OUT/'旧投稿用_保全'/p.name
  ah=audiohash(p);original=audiohash(source);assert ah==original,(tag,'音声ストリームが一致しません')
  results.append({'tag':tag,'file':str(p),'duration':float(j['format']['duration']),'video':{k:v.get(k)for k in['codec_name','width','height','r_frame_rate','nb_frames','bit_rate']},'audio':{k:a.get(k)for k in['codec_name','sample_rate','channels','bit_rate']},'levels':levels,'decode':decoded,'audio_bitstream_sha256':ah,'audio_bitstream_equal_to_source':True,'audio_source':str(source),'sha256':m.sha(p),'bytes':p.stat().st_size})
  (m.REVIEW/f'完成品検証_{scope}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('検品完了',tag,levels,flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('scope',choices=['main','shorts']);main(ap.parse_args().scope)
