#!/usr/bin/env python3
"""Read-only source; exclusive new outputs; ffmpeg encode, then independent decoded QC."""
import subprocess, json, hashlib, re, datetime, os, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
REC=ROOT/'制作記録'
SRC=Path('/Volumes/ESD-02/_内蔵_youtube_bgm/WAVE09_天の川の高原/本編音声v2/wave09_3時間_自前合成_v2_整音.flac')
AAC=Path('/Volumes/ESD-02/BGM/4_Waves of Japan/WAVE09_素材_天の川の高原/wave09_天の川の高原_3時間.mp4')
OUT=ROOT/'live02_音声_8h05.flac'
REPORT=ROOT/'live02_検品.json'
RATE=48000;TOTAL=29100;END=10790;START=30;FADE=60;SHIFT=10700;GAIN=0.0
SEAMS=[10760,21460]
def exclusive_json(path,data):
 with path.open('x') as f: json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def stat(path):
 s=path.stat();return {'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':sha(path)}
def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
def run_log(cmd,name):
 print(name,flush=True)
 with (REC/name).open('x') as f:
  subprocess.run(cmd,stdout=f,stderr=f,check=True)
def decode(path,start,duration):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t',str(duration),'-f','f32le','-acodec','pcm_f32le','-']),dtype='<f4').reshape(-1,2)
def clock(t):
 return f'{int(t)//3600:02d}:{int(t)%3600//60:02d}:{int(t)%60:02d}'
# ★2回目：1回目で書き出し済みのFLACを使い、エンコードと全編測定は省く（1回目のログを読む）。
REUSE=OUT.exists() and (REC/'完成全編_EBUR128.log').exists()
for p in [REPORT,ROOT/'継目1_試聴.m4a',ROOT/'継目2_試聴.m4a']+([] if REUSE else [OUT]):
 if p.exists():raise FileExistsError(p)
originals={str(p):stat(p) for p in [SRC,AAC]}
exclusive_json(REC/'入力ファイルの作業前記録.json',originals)
# First segment ends before its 10-second source fade; repeats begin after the 3-second fade.
# D=10700 seconds gives an integer cycle count for BOTH 130.31Hz and 131.31Hz.
# Both seams therefore have identical phase-aligned overlap material.
filters=(f'[0:a]atrim=start=0:end={END},asetpts=PTS-STARTPTS[a];'
 f'[1:a]atrim=start={START}:end={END},asetpts=PTS-STARTPTS[b];'
 f'[2:a]atrim=start={START}:end=7700,asetpts=PTS-STARTPTS[c];'
 f'[a][b]acrossfade=d={FADE}:c1=qsin:c2=qsin[ab];'
 f'[ab][c]acrossfade=d={FADE}:c1=qsin:c2=qsin,'
 f'atrim=end_sample={TOTAL*RATE},afade=t=in:st=0:d=3,'
 f'afade=t=out:st={TOTAL-30}:d=30,volume={GAIN}dB[out]')
cmd=['ffmpeg','-hide_banner','-nostdin','-n','-stats_period','20']
for _ in range(3):cmd+=['-i',str(SRC)]
cmd+=['-filter_complex_threads','1','-filter_complex',filters,'-map','[out]','-map_metadata','-1',
 '-ar','48000','-ac','2','-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24','-compression_level','6',
 '-metadata','title=LIVE02 天の川の高原 8時間5分','-metadata','comment=60-second phase-aligned crossfades; lossless WAVE09 mastered source',str(OUT)]
exclusive_json(REC/'制作コマンド.json',{'argv':cmd,'filter_complex':filters})
if not REUSE:run_log(cmd,'本番エンコード.log')
pr=probe(OUT);stream=pr['streams'][0]
assert int(stream['duration_ts'])==TOTAL*RATE
assert stream['codec_name']=='flac' and int(stream['bits_per_raw_sample'])==24
assert int(stream['sample_rate'])==48000 and stream['channels']==2
# Independently decode the finished 24-bit FLAC. Full-file EBU R128 / 4x true-peak scan.
if not REUSE:run_log(['ffmpeg','-hide_banner','-nostats','-v','info','-i',str(OUT),'-af','ebur128=peak=true','-f','null','-'],'完成全編_EBUR128.log')
log=(REC/'完成全編_EBUR128.log').read_text();summary=log.rsplit('Summary:',1)[-1]
i=float(re.search(r'I:\s*([\-\d.]+) LUFS',summary)[1]);tp=float(re.search(r'Peak:\s*([\-\d.]+)',summary)[1]);lra=float(re.search(r'LRA:\s*([\d.]+) LU',summary)[1])
passed=(-17<=i<=-16 and tp<=-2.5)
if not passed:raise RuntimeError(f'QC failed I={i}, TP={tp}')
seams=[]
for n,center in enumerate(SEAMS,1):
 start=center-150;duration=300
 # Include 30-second preroll for valid rolling short-term windows and before/after comparison.
 logfile=f'継目{n}_EBUR128.log'
 run_log(['ffmpeg','-hide_banner','-nostats','-ss',str(start),'-i',str(OUT),'-t',str(duration),'-af','ebur128=peak=true','-f','null','-'],logfile)
 rows=[]
 for line in (REC/logfile).read_text().splitlines():
  m=re.search(r'\bt:\s*([\d.]+).*?\bM:\s*([\-\d.]+)\s+S:\s*([\-\d.]+)',line)
  if m:
   t=float(m[1]);absolute=start+t
   if center-60<=absolute<=center+60:
    rows.append({'time_seconds':round(absolute,6),'relative_to_center_seconds':round(absolute-center,6),'short_term_lufs':float(m[3]),'momentary_lufs':float(m[2])})
 assert len(rows)>=1199
 # 1-second series for convenient inspection, full 100ms measurements preserved in report.
 one_second=[v for j,v in enumerate(rows) if j%10==0]
 x=decode(OUT,center-120,240)
 assert len(x)==240*RATE
 beat=[]
 # ★WAVE09は左右が床のC3（130.81Hz）から0.5Hzしか離れていない。5秒の矩形窓では床が漏れ込み、
 #   継目のない元音源でも位相が0.07rad揺れ、継目では0.17radになって止まった（1回目）。40秒ハン窓で測る。
 WIN=40
 for s in range(0,240-WIN+1,5):
  z=x[s*RATE:(s+WIN)*RATE].astype(np.float64);w=np.hanning(len(z))
  # Demodulate relative to the ORIGINAL source absolute phase. Both repeats have integer shifts.
  times=np.arange(len(z))/RATE+(10640+s)
  c=[2*np.sum(w*z[:,ch]*np.exp(-2j*np.pi*f*times))/np.sum(w) for ch,f in enumerate([130.31,131.31])]
  beat.append({'relative_to_center_seconds':s+WIN/2-120,'window_seconds':WIN,'window':'hann','carrier_dbfs':[round(float(20*np.log10(abs(v))),4) for v in c],
   'phase_radians':[round(float(np.angle(v)),6) for v in c],
   'interchannel_phase_residual_radians':round(float(np.angle(c[1]/c[0])),6)})
 phase=np.unwrap(np.array([b['interchannel_phase_residual_radians'] for b in beat]))
 deviation=float(np.max(np.abs(phase-np.median(phase))))
 # 各チャンネルの位相そのものも見る（左右とも同じだけ動くずれは差では見えないため）。
 ch_dev=[float(np.ptp(np.unwrap([b['phase_radians'][k] for b in beat]))) for k in (0,1)]
 assert deviation<0.3 and max(ch_dev)<0.3, (deviation,ch_dev)
 # Encode the +/-2 minute source-accurate excerpt, without any extra preview fades.
 preview=ROOT/f'継目{n}_試聴.m4a'
 run_log(['ffmpeg','-hide_banner','-nostats','-nostdin','-n','-ss',str(center-120),'-i',str(OUT),'-t','240','-map','0:a:0','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-movflags','+faststart',str(preview)],f'継目{n}_試聴エンコード.log')
 pp=probe(preview);assert abs(float(pp['format']['duration'])-240)<.1
 seams.append({'number':n,'crossfade_start_seconds':center-30,'crossfade_end_seconds':center+30,
  'crossfade_center_seconds':center,'crossfade_start_hhmmss':clock(center-30),
  'crossfade_end_hhmmss':clock(center+30),'crossfade_center_hhmmss':clock(center),
  'crossfade_duration_seconds':60,'curve':'quarter sine equal power (qsin / qsin)',
  'source_outgoing_range_seconds':[10730,10790],'source_incoming_range_seconds':[30,90],
  'short_term_measurement_interval_seconds':.1,'short_term_lufs_100ms':rows,'short_term_lufs_1s':one_second,
  'short_term_min_lufs':min(v['short_term_lufs'] for v in rows),'short_term_max_lufs':max(v['short_term_lufs'] for v in rows),
  'binaural_phase_5s_windows':beat,'interchannel_phase_max_deviation_radians':round(deviation,6),'per_channel_phase_range_radians':[round(v,6) for v in ch_dev],
  'preview_file':str(preview),'preview_duration_seconds':float(pp['format']['duration']),
  'preview_begin_output_seconds':center-120,'preview_seam_center_seconds':120,'preview_sha256':sha(preview)})
print('Verifying original hashes',flush=True)
final_originals={p:stat(Path(p)) for p in originals}
assert originals==final_originals
report={'status':'PASS','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'output_file':str(OUT),'output_bytes':OUT.stat().st_size,'output_sha256':sha(OUT),'duration_seconds':TOTAL,
 'duration_hhmmss':'08:05:00','sample_count_per_channel':TOTAL*RATE,'sample_rate_hz':RATE,'channels':2,'bits_per_sample':24,'codec':'FLAC',
 'source_file':str(SRC),'source_is_lossless':True,'source_priority_reason':'可逆の公開版マスターがESD-02の内蔵控えに残っていたため、指定MP4のAACより優先。',
 'master_search_locations':['/Users/ryo/youtube','/Volumes/ESD-02'],
 'original_source_measurement':{'first_fade_in_seconds_approx':3,'last_fade_out_seconds_approx':10,
  'measurement_file':'LIVE01と同じ合成スクリプト（wavekit/連続合成.py の afade 3秒/10秒）','method':'1秒RMS・130.31/131.31Hz成分の振幅低下を測定し、既存の合成スクリプトの3秒/10秒指定と照合。リミッターの遅延約5msを含む。'},
 'editing':{'repeat_count':3,'crossfade_count':2,'source_trimmed_end_seconds':10790,'repeat_source_start_seconds':30,
  'phase_alignment_source_time_difference_seconds':SHIFT,'left_carrier_hz':130.31,'right_carrier_hz':131.31,
  'left_cycles_in_shift':round(130.31*SHIFT,8),'right_cycles_in_shift':round(131.31*SHIFT,8),
  'beat_frequency_hz':1,'static_gain_db':GAIN,'initial_fade_in_seconds':3,'initial_fade_note':'素材の冒頭フェードを保持し、3秒フェードを重ねた。',
  'final_fade_out_seconds':30,'final_fade_start_seconds':29070,
  'crossfade_note':'両チャンネルとも整数周期だけ戻す位置で接続。qsin等電力クロスフェードで音量の落ち込みを避ける。同位相のビート成分は継目中央で緩やかに約3dB増える。'},
 'loudness':{'integrated_lufs':i,'true_peak_dbtp':tp,'loudness_range_lu':lra,'target_integrated_lufs':-16.5,'integrated_tolerance_lu':.5,
  'max_true_peak_dbtp':-2.5,'method':'ffmpeg ebur128 full decoded file, 100ms frames, 3s short term, 4x oversampled true peak','summary':summary.strip(),
  'report_precision_db':.1,'passed':passed},
 'seams':seams,'original_files_unchanged':originals==final_originals,'esd02_read_only':True,'originals_before':originals,'originals_after':final_originals,
 'limitations':['音響測定と位相検査は実施済み。人による試聴・8時間の通し試聴は未実施。試聴用M4AはAACのため、本番FLACとはエンコードが異なる。']}
exclusive_json(REPORT,report)
print(json.dumps({'status':'PASS','LUFS':i,'TP':tp,'output':str(OUT),'seams':[clock(s) for s in SEAMS]},ensure_ascii=False),flush=True)
