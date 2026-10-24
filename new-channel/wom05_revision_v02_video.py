"""Reproduce the accepted V01 grade and V02 replacement from preserved Kling v03 inputs."""
from wom05_revision_v02 import *

media=V1.parent/'素材'
filt="format=gbrp,geq=r='r(X,Y)*(1-0.75*clip((Y/H-0.45)/0.25,0,1))':g='g(X,Y)*(1-0.45*clip((Y/H-0.45)/0.25,0,1))':b='b(X,Y)',format=yuv420p"
night=ROOT/'assets/V01_night_grade_v03.mp4'
ff(['-i',media/'V01_Kling_v03.mp4','-vf',filt,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',16,night]);shutil.copy2(night,ROOT/'deliverables'/night.name)
ff(['-i',night,'-frames:v',1,'-vf','scale=1280:720','-q:v',3,ROOT/'review/V01_night_grade_preview.jpg'])
save(ROOT/'records/V01_night_grade.json',{'source':str(media/'V01_Kling_v03.mp4'),'source_sha256':sha(media/'V01_Kling_v03.mp4'),'output':str(night),'output_sha256':sha(night),'filter':filt,'purpose':'Remove warm dusk-like horizon while retaining the upper meteor and its trailing tail; original video retained.'})
encode_video('V01',night,10)
build_retime()
encode_video('V02',media/'V02_Kling_v03.mp4',6)
preserve_prefix()
video_records()
print('VIDEOS COMPLETE',flush=True)


fire='Quiet Origins EP005 V01 correction v03. One continuous 10-second 16:9 hand-painted oil illustration. DEEP DARK NIGHT, indigo sky with small stars. Lower quarter: gentle LOW ROUNDED HILLS COMPLETELY COVERED IN DENSE JAPANESE CEDAR FOREST, dark leafy silhouettes, like rural Japan. No exposed rocks, no desert, no jagged peaks, no snow, no sunset or daylight. Static wide camera. ONE small bright fireball moves steadily horizontally FROM LEFT TO RIGHT across the upper middle of the sky. The round glowing HEAD is always at the RIGHTMOST tip. Its narrow fading TAIL trails BEHIND the head, entirely TO THE LEFT of the head. The head leads and the tail follows: never a beam ahead of the meteor. Constant slow motion, steady soft warm light, no flicker, flashes, explosions or impacts. The wooded hills remain still. No buildings, people, animals, writing, logos or watermark. Visible brushwork, quiet historical illustration, silent.'
bird='Quiet Origins EP005 V02 falling-kite correction. Start exactly from the supplied frame. One continuous slow respectful illustrated shot, fixed camera, same persimmon tree and warm light. The brown kite bird DOES NOT FLY. Its raised wings slowly relax downward, the wing on the viewer right hangs limp. Its feet lose their grip. Its whole body slowly sinks VERTICALLY DOWNWARD behind and below the branch and disappears through the BOTTOM of the frame. Its apparent size NEVER grows: no movement toward the camera. No flap, no flight, no launching upward, no open strong wings, no dive toward viewer. Only quiet downward falling under gravity. Keep the tree branches and persimmons perfectly still. Do not show the ground, landing, impact, injury, blood, pain, distress or struggle. No other birds, people, text, new objects or camera movement. Soft painted illustration, no cuts, no flicker, silent.'
x={'service':'Kling AI 3.0','date':'2026-10-24','initial_balance':229,'balance_after_V01':149,'final_balance':69,'credits_used':160,'displayed_cost_each':80,'generations':2,'additional_purchase':False}
for k,prompt,slot in [('V01',fire,'942836900879024184'),('V02',bird,'942837317130780741')]:
 p=V1.parent/f'素材/{k}_Kling_v03.mp4';x[k]={'prompt':prompt,'source_path':str(p),'sha256':sha(p),'generation_url':'https://kling.ai/app/creations/grid?ac=12&project=939738663515209766&slotId='+slot,'accepted':True,'source_duration_seconds':float(probe(p)['format']['duration'])}
x['V01']['decision']='Klingで再生成を採用。低い森林の丘、右へ進む光と左へ引く尾を確認。地平線の暖色を局所的な色補正で暗い青に変更し、夜の場面にした'
x['V02'].update(decision='Klingで生成した後半を採用。v01の最初6秒・180フレームを画素一致で保持し、鳶が羽ばたかず枝の下へ消える部分へ接続。後半は動き量に応じて速度配分を調整',reference_image=str(ROOT/'assets/V02_start_frame_v02.png'),reference_sha256=sha(ROOT/'assets/V02_start_frame_v02.png'),kept_source_prefix_seconds=6,used_generated_seconds=[0,6],new_tail_duration_seconds=8.6)
save(ROOT/'records/ai_revision.json',x)
print('AI revision provenance recorded')
