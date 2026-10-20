"""Technical delivery checks; no claim of a human auditory review."""
import json, subprocess, re, hashlib
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont
R=Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve();D=R/'deliverables'
final=D/'EP001_アヌビス_完成試作_v01.mp4'
t=json.loads((R/'records/narration_timeline.json').read_text())
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(final)]))
(R/'records/final_ffprobe.json').write_text(json.dumps(p,ensure_ascii=False,indent=2))
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1920,1080)
assert v['r_frame_rate']=='30/1'
assert a['sample_rate']=='48000' and a['channels']==2
assert abs(float(p['format']['duration'])-t['duration_seconds'])<.1
decode=subprocess.run(['ffmpeg','-hide_banner','-v','error','-threads','2','-i',str(final),'-f','null','-'],capture_output=True,text=True)
(R/'records/full_decode.log').write_text(decode.stderr)
assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
audio=subprocess.run(['ffmpeg','-hide_banner','-i',str(final),'-vn','-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
levels=json.loads(re.search(r'\{\s*"input_i".*?\}',audio.stderr,re.S).group())
(R/'records/final_audio_levels.json').write_text(json.dumps(levels,indent=2))
assert abs(float(levels['input_i'])+16)<1
assert float(levels['input_tp'])<=-1.0
q=[c for seg in t['segments'] for c in seg['cues']]
assert all(0<=c['start']<c['end']<=t['duration_seconds'] for c in q)
assert all(q[i]['end']<=q[i+1]['start'] for i in range(len(q)-1))
assert all((R/c['audio_file']).exists() for c in q)
assert all((R/'assets/composed'/f'{name}.png').exists() for s in t['segments'] for name in s['visuals'])
assets=json.loads((R/'records/museum_assets.json').read_text())
assert len(assets)==10 and all(x['is_public_domain'] for x in assets)
for x in assets:assert hashlib.sha256((R/x['file']).read_bytes()).hexdigest()==x['sha256']
samples=[9,29,65,119,183,265,326,375,456,505,547,590,614]
shots=R/'records/final_frames';shots.mkdir(exist_ok=True)
for second in samples:
    out=shots/f'{second:03}s.jpg'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(final),'-frames:v','1','-q:v','2',str(out)],check=True)
contact=Image.new('RGB',(1920,4*300),(8,13,21));d=ImageDraw.Draw(contact)
ft=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',21)
for i,s in enumerate(samples):
    im=Image.open(shots/f'{s:03}s.jpg');im.thumbnail((480,270));x=i%4*480;y=i//4*300
    contact.paste(im,(x,y));d.text((x+8,y+273),f'{s//60:02}:{s%60:02}',font=ft,fill='white')
contact.save(R/'records/final_contact_sheet.jpg',quality=93)
preview=D/'EP001_冒頭90秒.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(final),'-t','90','-c','copy','-movflags','+faststart',str(preview)],check=True)
qc={'video':{'codec':v['codec_name'],'width':v['width'],'height':v['height'],'fps':30,'duration_seconds':float(p['format']['duration']),'size_bytes':final.stat().st_size},
    'audio':{'codec':a['codec_name'],'sample_rate':48000,'channels':2,'integrated_lufs':float(levels['input_i']),'true_peak_dbtp':float(levels['input_tp']),'loudness_range_lu':float(levels['input_lra'])},
    'checks':{'full_file_decode':'pass','subtitle_sentence_cues':len(q),'subtitle_monotonic_and_in_bounds':'pass','source_assets_present':'pass','museum_assets_public_domain_and_hash':'pass','sampled_frames_exported':samples,'visual_frame_review':'pending','human_full_watch':'pending','human_auditory_review':'pending','independent_expert_review':'not_performed'},
    'costs':{'additional_paid_contracts':0,'paid_api_calls':0,'suno_credits_used':0,'kling_credits_used':0,'built_in_image_generations':4,'notes':'既存契約内の画像生成枠と計算機資源は使用。電気代・既存月額・人件費は算入していない。80%の削減率は未測定。'},'publication':'not_uploaded_or_scheduled','generated_at_jst':'2026-10-15'}
(R/'records/qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qc,ensure_ascii=False,indent=2))
