"""Approved five English remakes. Native speech, sentence captions, unique originals.
P1R 24.733333 seconds was explicitly approved by the user on 2026-11-02.
"""
import argparse,difflib,json,math,re,subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom_shorts_remake import ROOT,REQUEST,MODELS,MEDIA,sha,save
from wom_shorts_produce import levels,rms,font
import imageio_ffmpeg
BIN=imageio_ffmpeg.get_ffmpeg_exe();FPS=30;SR=24000
read=lambda p:json.loads(Path(p).read_text())
def ff(args):subprocess.run([BIN,'-nostdin','-y','-v','warning',*map(str,args)],check=True)
MAIN={
 'EP001':MEDIA/'EP001_Anubis/Quiet_Origins_v08_20261021',
 'EP003':MEDIA/'EP003_Medusa/確認版_v02_20261023',
 'EP004':MEDIA/'EP004_Pandora/確認版_v01_20261023',
 'EP005':MEDIA/'EP005_Tengu/確認版_v02_20261024',
}
EPISODES={'A1R':'EP001','A3R':'EP001','M1R':'EP003','P1R':'EP004','T1R':'EP005'}
CAPTION_LENGTHS={
 'A1R':[5,3,4,8,2,8,10,4],
 'M1R':[8,4,8,8,6,8,5],
 'P1R':[5,8,8,6,10,8,4],
 'T1R':[5,5,8,10,5,8,7],
 'A3R':[10,5,5,10,8,4,4],
}
# Sentence-aware partitioning prioritizes exact copy and complete years over 4–5 words.
def caption_texts(text):
 out=[]
 for sentence in re.split(r'(?<=[.!?])\s+',text):
  words=sentence.split();n=len(words)
  # Dynamic programming: 4/5/8/9/10 are ideal; 2/3/6/7 only when sentence lengths force them.
  @lru_cache(None)
  def rec(k):
   if k==n:return (0,[])
   best=(1e9,[])
   for size in range(2,min(10,n-k)+1):
    if k+size<n and (words[k+size-1].rstrip(',.') in ['700','637','720','1508'] or words[k+size].rstrip(',.')=='BC'):continue
    cost,tail=rec(k+size) if k+size==n or n-k-size>=2 else (1e9,[])
    penalty=0 if size in [4,5,8,9,10] else 10
    val=cost+penalty+1
    if val<best[0]:best=(val,[size]+tail)
   return best
  sizes=rec(0)[1];assert sum(sizes)==n,(sentence,sizes);k=0
  for z in sizes:out.append(' '.join(words[k:k+z]));k+=z
 return out
CAPTIONS={s['id']:caption_texts(s['text']) for s in read(ROOT/'records/narration.json')['scripts']}

def captions():
 from kokoro_onnx.tokenizer import Tokenizer
 # Use the same tokenizer through the existing model session, without synthesizing again.
 import onnxruntime as ort
 ort.disable_telemetry_events()
 from kokoro_onnx import Kokoro
 opt=ort.SessionOptions();opt.intra_op_num_threads=2
 tts=Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(MODELS/'voices-v1.0.bin'))
 nar=read(ROOT/'records/narration.json');assert all(s['within_24_seconds'] or (s['id']=='P1R' and s['final_duration_seconds']<=24.733334) for s in nar['scripts']);allrows=[]
 for s in nar['scripts']:
  cfg=read(ROOT/f'audio/{s["id"]}_native.json');PHONEMES={r['display']:r['phonemes'] for r in cfg['applied_readings'] if 'phonemes' in r};REPLACEMENTS={r['display']:r['spoken'] for r in cfg['applied_readings']}
  times=read(ROOT/f'records/{s["id"]}_phoneme_timings.json')['timings'];words=s['text'].split();ignored=set(' \t\nˈˌː.,;:!?—-()');expected=[];owners=[]
  for i,w in enumerate(words):
   key=re.sub(r"^[^A-Za-z]+|[^A-Za-z']+$",'',w);ph=PHONEMES.get(key.rstrip("'"),tts.tokenizer.phonemize(REPLACEMENTS.get(w.rstrip(',.'),w),'en-us'))
   clean=[c for c in ph if c not in ignored];expected.extend(clean);owners.extend([i]*len(clean))
  native=[t for t in times if t['phoneme'] not in ignored];matcher=difflib.SequenceMatcher(None,expected,[t['phoneme'] for t in native],autojunk=False);assert matcher.ratio()>.8
  aligned={i:[] for i in range(len(words))}
  for block in matcher.get_matching_blocks():
   for j in range(block.size):aligned[owners[block.a+j]].append(block.b+j)
  # Context changes articles (standalone "a" vs unstressed schwa). Attribute those
  # edit spans to their neighboring native phoneme interval, preserving order.
  context_mapped=[]
  for tag,i1,i2,j1,j2 in matcher.get_opcodes():
   if tag=='equal':continue
   for index in range(i1,i2):
    target=j1+round((index-i1)/max(1,i2-i1-1)*max(0,j2-j1-1));target=min(len(native)-1,target)
    aligned[owners[index]].append(target);context_mapped.append(owners[index])
  assert all(aligned.values())
  wordtimes=[{'word':w,'start':native[min(aligned[i])]['start'],'end':native[max(aligned[i])]['end']} for i,w in enumerate(words)]
  assert all(a['start']<=b['start'] for a,b in zip(wordtimes,wordtimes[1:]))
  texts=CAPTIONS[s['id']]
  groups=[];pos=0
  for text in texts:
   end=pos+len(text.split());groups.append({'text':text,'word_start':pos,'word_end':end});pos=end
  for protected in ['670 BC.']:
   if protected in s['text']:assert any(protected in g['text'] for g in groups),protected
  cta_frame=math.ceil(s['native_audio_duration']*FPS);nframes=cta_frame+75;assert nframes<= (742 if s['id']=='P1R' else 720)
  for i,g in enumerate(groups):
   g['start_frame']=max(0,round(wordtimes[g['word_start']]['start']*FPS)) if i else 0
   g['end_frame']=max(g['start_frame']+1,round(wordtimes[groups[i+1]['word_start']]['start']*FPS)) if i+1<len(groups) else math.ceil(s['native_audio_duration']*FPS)
   assert g['end_frame']<=nframes
  assert ' '.join(g['text'] for g in groups)==s['text']
  row={**s,'episode':EPISODES[s['id']],'title_ja':s['title'],'words_timed':wordtimes,'alignment_ratio':matcher.ratio(),'context_adjusted_word_indices':sorted(set(context_mapped)),'alignment_method':'Native Kokoro phoneme durations mapped to script words by sequence alignment, with contextual phoneme substitutions assigned within adjacent aligned spans. These are model-derived word estimates, not human auditory verification.','caption_groups':groups,'frames':nframes,'duration_seconds':nframes/FPS,'cta_start':cta_frame/FPS,'cta_start_frame':cta_frame,'cta_text':'SUBSCRIBE FOR MORE ORIGINS', 'cta_subtext':'Full story: related video below'}
  allrows.append(row);print('CAPTIONS',s['id'],len(groups),'pages',nframes/FPS,'seconds',matcher.ratio(),flush=True)
 save(ROOT/'records/shorts.json',{'shorts':allrows,'request_sha256':sha(REQUEST)})

def phrase_frame(s, phrase):
    words=[re.sub(r"[^a-z0-9']",'',w['word'].lower()) for w in s['words_timed']]
    needle=phrase.lower().split()
    j=next(j for j in range(len(words)) if words[j:j+len(needle)]==needle)
    return round(s['words_timed'][j]['start']*FPS)

def audio():
    reports=[]
    musicroot=Path('/Users/ryo/Desktop/新チャンネル/_共通/BGM/20261029_Suno')
    for i,s in enumerate(read(ROOT/'records/shorts.json')['shorts']):
        sid=s['id'];n=s['frames']*SR//FPS
        normal=ROOT/f'audio/{sid}_normalized.wav'
        q=levels(Path(s['audio_file']))
        filt=f"loudnorm=I=-14:TP=-1.5:LRA=7:linear=true:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}"
        ff(['-i',s['audio_file'],'-af',filt,'-ar',SR,'-c:a','pcm_f32le',normal])
        voice,sr=sf.read(normal,dtype='float32');assert sr==SR and len(voice)<=n
        voice=np.pad(voice,(0,n-len(voice)))
        source=MAIN[s['episode']]/'audio'/('common_bgm.wav' if s['episode']=='EP001' else 'common_bgm_and_brand.wav')
        if s['episode']=='EP005':source=MEDIA/'EP005_Tengu/確認版_v01_20261024/audio/common_bgm_and_brand.wav'
        assert source.exists()
        start=100;musicpath=ROOT/f'audio/{sid}_filtered_music.wav'
        ff(['-ss',start,'-i',source,'-t',n/SR,'-af','highpass=f=100,equalizer=f=2828:t=o:w=1:g=-3.5','-ar',SR,'-ac',2,'-c:a','pcm_f32le',musicpath])
        music,sr=sf.read(musicpath,dtype='float32');assert sr==SR and len(music)>=n
        music=music[:n];active=np.zeros(n,bool);active[round(s['voice_onset_seconds']*SR):round(s['last_voice_activity_seconds']*SR)]=True
        music*=10**((rms(voice[active])-15-rms(music[active]))/20)
        music[-round(.12*SR):]*=np.linspace(1,0,round(.12*SR))[:,None]
        gain=0;mix=ROOT/f'audio/{sid}_mix.wav'
        for attempt in range(5):
            factor=10**(gain/20);sf.write(mix,(voice[:,None]+music)*factor,SR,subtype='FLOAT')
            q=levels(mix);delta=-14-float(q['input_i'])
            if abs(delta)<.04:break
            gain+=delta
        out=ROOT/f'audio/{sid}_final.m4a'
        ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k',out]);final=levels(out)
        limiter=None
        if float(final['input_tp'])>-1:
            correction=0
            for attempt in range(4):
                limiter='192kHz oversampled limiter, -2dBFS ceiling (FFmpeg 7.1)'
                filt=f'volume={correction}dB,aresample=192000,alimiter=limit={10**(-2/20)}:level=false:latency=true,aresample=48000'
                import imageio_ffmpeg
                subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(mix),'-af',filt,'-ar','48000','-c:a','aac','-b:a','192k',str(out)],check=True);final=levels(out)
                if abs(float(final['input_i'])+14)<=.1 and float(final['input_tp'])<=-1:break
                correction+=-14-float(final['input_i'])
        assert abs(float(final['input_i'])+14)<=.15 and float(final['input_tp'])<=-1, final
        sf.write(ROOT/f'audio/{sid}_bgm.wav',music*factor,SR,subtype='FLOAT')
        onset_rms=rms(music[:240]*factor);assert onset_rms>-70
        reports.append(dict(id=sid,mix=final,voice_onset_native=s['voice_onset_seconds'],bgm_source=str(source),bgm_source_sha256=sha(source),bgm_excerpt_start_seconds=start,bgm_excerpt_end_seconds=start+n/SR,bgm_during_narration_dbfs=rms(music[active]*factor),voice_during_narration_dbfs=rms(voice[active]*factor),bgm_relative_to_voice_db=-15,bgm_first_10ms_dbfs=onset_rms,bgm_fade_in=False,filter='highpass 100Hz; EQ 2828Hz, 1 octave, -3.5dB',final_file=str(out),sha256=sha(out),voice_rate_or_pitch_processing=False,peak_limiter=limiter))
        print('AUDIO',sid,final['input_i'],final['input_tp'],flush=True)
    save(ROOT/'records/audio_qc.json',dict(passed=True,target_lufs=-14,maximum_true_peak_db=-1,reports=reports))

FONTS=Path('/System/Library/Fonts/Supplemental')
SPECS={
'A1R':[('met_590939',None),('met_557657','On this Egyptian papyrus'),('met_552247','Thoth the ibisheaded god')],
'M1R':[('A24',None),('A07','Around 700 BC'),('D_timeline','comes later')],
'P1R':[('A01',None),('A12','The box came'),('A10','and the word stuck')],
'T1R':[('met_40011_DP206881',None),('ndl_1182143_010','In the Nihon Shoki')],
'A3R':[('met_570223',None),('met_544075','Canines roamed')],
}
HEADLINES={'A1R':['WHO REALLY','JUDGED THE DEAD?'],'M1R':['NO CURSE IN','THE OLDEST STORY'],'P1R':['IT WAS NEVER','A BOX'],'T1R':['THE FIRST TENGU','WAS A STAR'],'A3R':['WHY A','CANINE HEAD?']}

def fitfont(text,width,height,path='Arial Bold.ttf'):
 for n in range(200,12,-1):
  f=ImageFont.truetype(str(FONTS/path),n);b=f.getbbox(text)
  if b[2]-b[0]<=width and b[3]-b[1]<=height:return f,b
 raise ValueError(text)

def puttext(layer,text,y,width=752,height=84,path='Arial Bold.ttf',color=(244,239,223,255),center=480):
 f,b=fitfont(text,width,height,path);w=b[2]-b[0];h=b[3]-b[1];x=round(center-w/2)
 ImageDraw.Draw(layer).text((x-b[0],y-b[1]),text,font=f,fill=color)
 return dict(text=text,glyph_bbox=[x,y,x+w,y+h],glyph_height=h,font=path,font_size=f.size,horizontal_scale=1)

def registry(s):
 ep=s['episode'];items={}
 if ep=='EP001':
  for a in read(Path(__file__).parent/'episodes/EP001_Anubis/records/museum_assets.json'):
   k='met_'+str(a['object_id']);items[k]=dict(id=k,path=str(MEDIA/'EP001_Anubis/旧制作素材'/a['file']),sha256=a['sha256'],label='MUSEUM OBJECT｜博物館資料',source='The Metropolitan Museum of Art / Open Access (CC0)',title=a['title'],object_number=a['object_number'])
 else:
  folder=MAIN[ep];rs=folder/'records/render_shots.json'
  if ep=='EP004':rs=MEDIA/'EP004_Pandora/確認版_v02_20261023/records/render_shots.json'
  main={a['key']:a for a in read(rs)};ledger=read(folder/'records/source_assets.json')
  raws=ledger.get('items',ledger.get('assets',[]))
  for a in raws:
   k=a.get('id',a.get('key',a.get('asset_id')))
   if k not in main:continue
   original=a['originals'][0] if 'originals' in a else a
   path=original.get('path',original.get('local_path'));items[k]=dict(id=k,path=path,sha256=original['sha256'],label=main[k]['label'],source=main[k]['source'],main=main[k])
  if ep=='EP003':
   m=main['D_timeline'];cardpath=folder/m['file'];cardpath=cardpath if cardpath.exists() else MEDIA/'EP003_Medusa/確認版_v01_20261023'/m['file'];items['D_timeline']=dict(id='D_timeline',path=str(cardpath),sha256=m['sha256'],label=m['label'],source=m['source'],main=m)
 return items

def crop_spec(sid,aid,im):
 w,h=im.size;full=[0,0,w,h]
 fixed={'met_590939':[750,160,1800,1700],'met_570223':[1090,850,1690,1870],'met_552247':[700,267,1880,1133], 'met_557657':[2000,1250,3020,2220], 'A24':[1450,750,2450,2150]}
 if aid in fixed:box=fixed[aid]
 elif aid=='A07':box=[round(w*.18),round(h*.12),round(w*.82),round(h*.9)]
 elif aid=='met_40011_DP206881':box=[round(w*.10),round(h*.10),round(w*.94),round(h*.97)]
 elif aid=='ndl_1182143_010':box=[round(w*.60),round(h*.565),round(w*.655),round(h*.745)]
 else:box=full
 end=box.copy()
 if aid=='met_557657':end=[1750,1250,2770,2220]
 if aid=='met_544075':end=[950,150,2850,1800]
 return box,end

def text_layer(lines,kind,sid):
 layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer);recs=[]
 if kind=='headline':
  top=630 if sid=='T1R' else 300
  d.rounded_rectangle((80,top,880,top+226),16,fill=(0,0,0,173))
  for j,t in enumerate(lines):recs.append(puttext(layer,t,top+20+j*96,height=78,path='Georgia Bold.ttf'))
 elif kind=='cta':
  d.rounded_rectangle((80,1030,880,1256),16,fill=(232,217,183,245));d.rounded_rectangle((80,1280,880,1376),16,fill=(0,0,0,173))
  for t,y in [('SUBSCRIBE',1050),('FOR MORE ORIGINS',1152)]:recs.append(puttext(layer,t,y,height=84,path='DIN Condensed Bold.ttf',color=(59,44,33,255)))
  recs.append(puttext(layer,'Full story: related video below',1300,height=56,path='Arial Narrow Bold.ttf'))
 else:
  # Native font size only: no anisotropic text resizing.
  count=len(lines);ys=[1248] if count==1 else [1198,1294]
  for line,y in zip(lines,ys):
   f,b=fitfont(line,752,60);w=b[2]-b[0];h=b[3]-b[1];x=round(480-w/2);plate=[x-20,y-20,x+w+20,y+h+20]
   assert 80<=plate[0]<plate[2]<=880 and 1150<=plate[1]<plate[3]<=1450
   d.rounded_rectangle(plate,16,fill=(0,0,0,173));r=puttext(layer,line,y,height=60);r.update(plate_bbox=plate,opacity=173/255,padding=20);recs.append(r)
 p=ROOT/f'assets/{sid}_{kind}.png';layer.save(p);return p,recs

def splitlines(text):
 words=text.split();n=len(words)
 if n<=5:return [text]
 cuts=range(max(1,n-5),min(5,n-1)+1)
 return min(([' '.join(words[:k]),' '.join(words[k:])] for k in cuts),key=lambda a:sum((len(x.split())<4)*100 for x in a)+abs(len(a[0])-len(a[1])))

def visuals():
 (ROOT/'assets').mkdir(exist_ok=True);shots=[];caps=[];heads=[];used=[]
 cta,ctarecs=text_layer([], 'cta','common');save(ROOT/'records/cta_design.json',dict(rows=ctarecs,group_bbox=[80,1030,880,1376],horizontal_squeeze=0,main_font='DIN Condensed Bold; naturally condensed typeface, no bitmap width scaling'))
 for s in read(ROOT/'records/shorts.json')['shorts']:
  sid=s['id'];reg=registry(s);hp,hr=text_layer(HEADLINES[sid],'headline',sid);heads.append(dict(id=sid,rows=hr,file=str(hp),fade_start=2,fade_duration=.3))
  for j,g in enumerate(s['caption_groups']):
   lines=splitlines(g['text']);cp,cr=text_layer(lines,f'caption{j:02}',sid);caps.append(dict(short_id=sid,page=j,**g,lines=lines,file=str(cp),rows=cr,word_count_exceptions=[line for line in lines if not 4<=len(line.split())<=5]))
  starts=[0 if cue is None else phrase_frame(s,cue) for aid,cue in SPECS[sid]]
  for i,(aid,cue) in enumerate(SPECS[sid]):
   a=reg[aid];p=Path(a['path']);assert p.exists() and sha(p)==a['sha256'],p;im=Image.open(p).convert('RGB');original=im.size;box,end=crop_spec(sid,aid,im)
   note=None
   if aid=='D_timeline':
    m=a['main']; vals=[t['text'] for t in m['texts'][2:]];piece=Image.new('RGB',(1000,830),'#e8d9b7');dd=ImageDraw.Draw(piece)
    pairs=[(vals[0],vals[1]),(vals[2],vals[3]),(vals[4],vals[5]),(vals[6],vals[7]),(vals[8],vals[9])]
    for k,(author,date) in enumerate(pairs):
     y=20+k*157;dd.rounded_rectangle((20,y,980,y+140),12,fill='#f3e8ce',outline='#bba377',width=2)
     for t,yy in [(author,y+14),(date,y+73)]:
      f=font(42,t,bold=True);dd.text(((1000-f.getlength(t))/2,yy),t,font=f,fill='#3b2c21')
    # Preserve the Japanese explanatory line too; all English strings exactly match main.
    f=font(21,vals[10]);dd.text((500-f.getlength(vals[10])/2,802),vals[10],font=f,fill='#3b2c21')
    note=dict(main_texts=vals,remake_texts=[t for pair in pairs for t in pair]+[vals[10]],all_text_identical=True)
    im=piece;box=end=[0,0,1000,830];original=list(im.size)
   if aid in ['A12','ndl_1182143_010','met_40011_DP206881']:
    im=ImageOps.colorize(ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=.2),black='#443422',white='#f1e4c7')
   if aid=='A12':
    # Original page plus the exact main-film detail rectangle, one continuous source.
    full=ImageOps.contain(im,(1000,580),Image.Resampling.LANCZOS);piece=Image.new('RGB',(1000,830),'#e8d9b7');piece.paste(full,((1000-full.width)//2,0));rect=a['main']['detail_crop_normalized'];c=[round(v*d) for v,d in zip(rect,[im.width,im.height]*2)];detail=im.crop(c);scale=min(960/detail.width,1.6/1.03);detail=detail.resize((round(detail.width*scale),round(detail.height*scale)),Image.Resampling.LANCZOS);piece.paste(detail,((1000-detail.width)//2,630));note=dict(detail_crop_pixels=c,detail_crop_normalized=rect,max_native_scale=scale*1.03);im=piece;box=end=[0,0,1000,830]
   first=i==0;zoom=1.08 if first else (1 if aid=='met_544075' else 1.03)
   # Foreground remains within the dedicated evidence band after the first shot.
   if first:
    scale=min(1480/(box[3]-box[1]),1.6/zoom);vw=min(1080,round((box[2]-box[0])*scale));vh=round((box[3]-box[1])*scale);view=[(1080-vw)//2,290,vw,vh]
   else:
    scale=min(1000/(box[2]-box[0]),830/(box[3]-box[1]),1.6/zoom);vw=round((box[2]-box[0])*scale);vh=round((box[3]-box[1])*scale);view=[(1080-vw)//2,270+(860-vh)//2,vw,vh]
   maxscale=max(vw/(end[2]-end[0]),vh/(end[3]-end[1]))*zoom
   if note and 'max_native_scale' in note:maxscale=max(maxscale,note['max_native_scale'])
   assert maxscale<=1.601,(sid,aid,maxscale)
   prepared=ROOT/f'assets/{sid}_{aid}_source.png';im.save(prepared)
   bg=ImageEnhance.Brightness(ImageOps.fit(im,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.28)
   bgfile=ROOT/f'assets/{sid}_{aid}_bg.jpg';bg.save(bgfile,quality=92)
   header=Image.new('RGBA',(1080,1920));hd=ImageDraw.Draw(header);navy=s['episode']=='EP001';hd.rectangle((0,120,1079,269),fill='#0c1820' if navy else '#e8d9b7');ink='#f4efdf' if navy else '#3b2c21';texts=[]
   vals=[f"QUIET ORIGINS / {s['episode']}",a['label']];source=a['source']
   # Preserve exact source wording; wrap only whitespace.
   f=font(20);wrapped=[];line=''
   for word in source.split():
    t=(line+' '+word).strip()
    if f.getlength(t)>920:wrapped.append(line);line=word
    else:line=t
   if line:wrapped.append(line)
   vals+=wrapped
   if aid=='met_590939':vals+=['Statuette of a canid-headed god, probably Anubis']
   for k,val in enumerate(vals):
    f=font(20 if k<2 else 18,val,bold=k==0);y=140+k*24;bb=hd.textbbox((80,y),val,font=f);assert bb[3]<=260 and bb[2]<=1000;hd.text((80,y),val,font=f,fill=ink);texts.append(dict(text=val,bbox=list(bb)))
   hfile=ROOT/f'assets/{sid}_{aid}_header.png';header.save(hfile);stop=starts[i+1] if i+1<len(starts) else s['frames'];assert stop-starts[i]>=45
   used.append(a['sha256']);shots.append(dict(short_id=sid,episode=s['episode'],asset_id=aid,source=a,start_frame=starts[i],end_frame=stop,frames=stop-starts[i],cut_phrase=cue,cut_seconds=starts[i]/30,file=str(prepared),background=str(bgfile),header=str(hfile),header_texts=texts,crop_start=box,crop_end=end,viewport=view,zoom_end=zoom,native_max_scale=maxscale,foreground_height_fraction=vh/1920 if first else None,note=note))
 assert len(used)==len(set(used))==13
 save(ROOT/'records/visual_manifest.json',dict(shots=shots,unique_originals=13));save(ROOT/'records/caption_manifest.json',caps);save(ROOT/'records/headlines.json',heads)
 print('VISUALS 13 originals',flush=True)

def frame_art(shot,frac,loaded):
 im,bg,header=loaded;x,y,w,h=shot['viewport'];a=np.array(shot['crop_start'],float);b=np.array(shot['crop_end'],float);c=a+(b-a)*frac;z=math.exp(math.log(shot['zoom_end'])*frac);cx=(c[0]+c[2])/2;cy=(c[1]+c[3])/2;cw=(c[2]-c[0])/z;ch=(c[3]-c[1])/z
 # Fractional source sampling prevents integer zoom stepping.
 crop=im.transform((w,h),Image.Transform.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)
 frame=bg.copy();frame.paste(crop,(x,y));return Image.alpha_composite(frame.convert('RGBA'),header)

def render(ids,version="v01"):
 rows=read(ROOT/'records/shorts.json')['shorts'];shots=read(ROOT/'records/visual_manifest.json')['shots'];caps=read(ROOT/'records/caption_manifest.json');cta=Image.open(ROOT/'assets/common_cta.png').convert('RGBA');reports=[]
 for s in rows:
  sid=s['id']
  if sid not in ids:continue
  out=ROOT/f'deliverables/QO_short_remake_{sid}_{version}.mp4';group=[x for x in shots if x['short_id']==sid];caption=[x for x in caps if x['short_id']==sid];cp=[Image.open(x['file']).convert('RGBA') for x in caption];headline=Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA')
  cmd=[BIN,'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-i',str(ROOT/f'audio/{sid}_final.m4a'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',str(out)]
  with (ROOT/f'records/{sid}_encode.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
   try:
    for shot in group:
     # Each still source independently decoded; only RGB frames enter one final encoder.
     loaded=(Image.open(shot['file']).convert('RGB'),Image.open(shot['background']).convert('RGB'),Image.open(shot['header']).convert('RGBA'))
     for local in range(shot['frames']):
      n=shot['start_frame']+local;frame=frame_art(shot,local/max(1,shot['frames']-1),loaded)
      if n<69:
       hh=headline if n<60 else headline.copy()
       if n>=60:hh.putalpha(headline.getchannel('A').point(lambda a:round(a*(69-n)/9)))
       frame=Image.alpha_composite(frame,hh)
      if n>=s['cta_start_frame']:frame=Image.alpha_composite(frame,cta)
      else:
       j=next(j for j,c in enumerate(caption) if c['start_frame']<=n<c['end_frame']);frame=Image.alpha_composite(frame,cp[j])
      proc.stdin.write(frame.convert('RGB').tobytes())
      if n%150==0:print('FRAME',sid,n,'/',s['frames'],flush=True)
    proc.stdin.close();assert proc.wait()==0
   except BaseException:proc.kill();proc.wait();raise
  reports.append(dict(id=sid,path=str(out),sha256=sha(out),command=cmd,method='13 still sources independently decoded by Pillow; RGB frames composited; one H.264 encoder per final short. No bitstream concatenation.'))
  print('RENDERED',sid,flush=True)
 existing=read(ROOT/'records/encoding.json') if (ROOT/'records/encoding.json').exists() else []
 save(ROOT/'records/encoding.json',[r for r in existing if r['id'] not in ids]+reports)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['captions','audio','visuals','render']);p.add_argument('--ids',default='A1R,M1R,P1R,T1R,A3R');a=p.parse_args()
 if a.stage=='render':render(a.ids.split(','))
 else:globals()[a.stage]()
