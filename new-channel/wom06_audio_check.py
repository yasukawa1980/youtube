"""Check existing local audio and subtitles; does not publish media."""
import json,re,subprocess
import soundfile as sf
from wom06_produce import ROOT,read,save,sha,measure,probe

def main():
 m=read(ROOT/'records/master_timeline.json');duration=m['duration_seconds'];records=[]
 for lang in ['en','ja']:
  wav=ROOT/f'deliverables/EP006_audio_{lang}.wav';aac=ROOT/f'deliverables/EP006_audio_{lang}.m4a'
  wi=sf.info(wav);assert wi.samplerate==48000 and wi.frames==round(duration*48000) and wi.subtype=='PCM_24' and wi.channels==2
  levels=measure(aac);assert abs(float(levels['input_i'])+16)<=.3 and float(levels['input_tp'])<=-1
  p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(aac),'-af','silencedetect=noise=-60dB:d=1','-f','null','-'],capture_output=True,text=True,check=True)
  silent=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',p.stderr)];assert not silent
  for src in [wav,aac]:
   dec=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(src),'-f','null','-'],capture_output=True,text=True,check=True);assert not dec.stderr.strip(),dec.stderr
  records.append({'language':lang,'aac_sha256':sha(aac),'wav_sha256':sha(wav),'wav_sample_rate':wi.samplerate,'wav_samples':wi.frames,'wav_subtype':wi.subtype,'loudness':levels,'silence_at_minus60dB_over_1s':silent,'audio_full_decode_warnings':0})
 result={'passed':True,'duration_seconds':duration,'opening':m['brand_intervals']['opening'],'endcard':m['brand_intervals']['endcard'],'japanese_wait_before_opening':m['ja_wait_before_opening'],'subtitle_validation':read(ROOT/'records/subtitle_validation.json'),'audio':records,'human_auditory_review':False,'final_video_checks_completed':False}
 save(ROOT/'records/audio_subtitle_checks.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
