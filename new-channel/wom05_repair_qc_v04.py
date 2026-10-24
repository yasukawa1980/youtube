"""Compare every rebuilt frame with its independently decoded shot source.

Do not use the combined v02 as the visual reference: sequential decoding
of that mixed-profile file produces the same corruption being repaired.
"""
import json
import re
import subprocess
from wom05_repair_encoding_v04 import ROOT, SOURCE, sha

dst=ROOT/'deliverables/EP005_Tengu_en_v04_1080p30.mp4'
shots=json.loads((SOURCE/'records/render_shots.json').read_text())
offset=0
checks=[]
all_scores=[]
for index,shot in enumerate(shots):
    stats=ROOT/f'_work/shot_{index:02d}_ssim.txt'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',f'{offset/30:.9f}',
        '-threads','3','-i',str(dst),'-threads','3','-i',shot['encoded_file'],
        '-filter_complex_threads','2','-filter_complex',
        f'[0:v]setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]ssim=stats_file={stats}:shortest=1',
        '-an','-frames:v',str(shot['frames']),'-f','null','-'],check=True)
    scores=[float(x) for x in re.findall(r'All:([\d.]+)',stats.read_text())]
    assert len(scores)==shot['frames'],(shot['key'],len(scores))
    assert min(scores)>.97,(shot['key'],min(scores))
    checks.append({'key':shot['key'],'start_frame':offset,'frames':len(scores),
        'ssim_min':min(scores),'ssim_mean':sum(scores)/len(scores)})
    all_scores.extend(scores)
    offset+=shot['frames']
    print('VERIFIED',shot['key'],len(scores),min(scores),flush=True)
assert len(all_scores)==11065
decode=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(dst),
    '-map','0:v:0','-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr
headers=subprocess.run(['ffmpeg','-v','info','-i',str(dst),'-map','0:v:0','-c','copy',
    '-bsf:v','trace_headers','-f','null','-'],capture_output=True,text=True,check=True)
profiles=re.findall(r'profile_idc\s+[01]+\s+=\s+(\d+)',headers.stderr)
assert set(profiles)=={'100'},set(profiles)
record={'passed':True,'file':dst.name,'sha256':sha(dst),'compared_frames':len(all_scores),
    'independent_reference_shots':len(checks),'ssim_min':min(all_scores),
    'ssim_mean':sum(all_scores)/len(all_scores),'checks':checks,
    'sps_profiles':sorted(set(profiles)),'decode_warnings':decode.stderr,
    'reference':'Each original shot independently decoded, not the defective combined v02'}
(ROOT/'records/repair_qc.json').write_text(json.dumps(record,indent=2)+'\n')
print('ALL PASS',len(all_scores),min(all_scores),sum(all_scores)/len(all_scores),flush=True)
