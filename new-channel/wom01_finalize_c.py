"""Adopt the approved C delivery for v04, correct 秤, and rebuild both SRTs.

Uses existing free local models only. WOM_EPISODE_ROOT must be a new folder.
WOM_PREVIOUS_ROOT=v03; WOM_AUDITION_ROOT=approved audition; WOM_SOURCE_ROOT=legacy assets.
Stages: prepare, narration, timeline, visuals, audio, pictures, package.
"""
import argparse,copy,json,os,re,shutil,subprocess
from dataclasses import asdict
from pathlib import Path
import numpy as np
import soundfile as sf
from voicevox_core.blocking import Onnxruntime,OpenJtalk,Synthesizer,VoiceModelFile
from wom01_multilingual_narration import spoken_ja
from wom01_日本語自然さ試聴 import ROLES,SPEED,INTONATION,PAUSES
from wom01_multilingual_render import read,save,sha,ff,probe,measure,build_timeline,make_audio
from wom01_refine_av import pictures
import wom01_multilingual_visuals as visuals
SR,FPS=24000,30

def role_for(cid,text):
    if cid in ROLES:return ROLES[cid]
    if text.startswith(('なぜ','では、')) or 'でしょう' in text:return 'question'
    if text.startswith(('けれど','しかし','ただ、','一方','たしかに')):return 'contrast'
    if text.startswith(('それでは','ここで','次に','最後に')):return 'transition'
    if any(x in text for x in ('美術館','解説','紀元前','記されています')):return 'explanation'
    return 'plain'

def prepare(root,previous):
    assert root!=previous and not (root/"records/qc_v04.json").exists()
    for d in ['records','audio/en','audio/ja/sentences','assets','review','deliverables','_work/render']:(root/d).mkdir(parents=True,exist_ok=True)
    for name in ['content.json','content_en.json','narration_segments_en.json']:
        shutil.copy2(previous/'records'/name,root/'records'/name)
    en=read(root/'records/narration_segments_en.json');hashes=[]
    for seg in en['segments']:
        src=previous/seg['audio_file']
        if not src.exists():src=Path(read(previous/'records/revision_request.json')['source_root'])/seg['audio_file']
        dst=root/seg['audio_file'];shutil.copy2(src,dst)
        assert sha(src)==sha(dst);hashes.append({'segment_id':seg['id'],'sha256':sha(dst)})
    save(root/'records/revision_request.json',{'version':'v04','owner_selected_japanese_delivery':'C',
        'voice_ja':'VOICEVOX:冥鳴ひまり','voice_en':'Kokoro:af_heart (B), existing segment audio',
        'source_root':str(previous),'english_segment_hashes':hashes,'style_id':14,
        'reading_fix':'Standalone 秤 -> はかり in speech input only; 天秤 and 秤量 preserved.',
        'subtitles_burned_in':False,'subtitle_safe_layout':True,'crf':18,'paid_services':False,'publication':False})

def narration(root):
    runtime=Path(os.environ['WOM_VOICEVOX_RUNTIME']);audition=Path(os.environ['WOM_AUDITION_ROOT'])
    model=runtime/'models/vvms/1.vvm';assert sha(model)=='8df20815be9a84a4b4723b9e778d2ef6a4df277e4872fe9efe29676a60e02774'
    synth=Synthesizer(Onnxruntime.load_once(filename=str(next((runtime/'onnxruntime/lib').glob('*.dylib')))),OpenJtalk(str(runtime/'dict/open_jtalk_dic_utf_8-1.11')),acceleration_mode='CPU',cpu_num_threads=2)
    with VoiceModelFile.open(str(model)) as m:synth.load_voice_model(m)
    old={x['sentence_id']:x for x in read(audition/'records/queries.json') if x['variant']=='C'}
    records=[];queries=[];fixes=[];counts={'approved_C_reused':0,'new':0,'current_cache':0}
    for seg in read(root/'records/content.json')['segments']:
        texts=re.findall(r'[^。！？]+[。！？]?',seg['text']);pieces=[];cursor=0;cues=[]
        for j,text in enumerate(texts,1):
            cid=f'{seg["id"]}-{j:02}';role=role_for(cid,text);spoken=spoken_ja(text);q=synth.create_audio_query(spoken,14)
            q.speed_scale=SPEED[role]-.015;q.intonation_scale=INTONATION[role]+.10
            q.pre_phoneme_length=.055;q.post_phoneme_length=.09;q.output_sampling_rate=SR
            pi=0
            for phrase in q.accent_phrases:
                if phrase.pause_mora is not None:
                    values=PAUSES.get(cid,[]);base=values[pi] if pi<len(values) else .20
                    phrase.pause_mora['vowel_length']=base+.055;pi+=1
            if re.search(r'(?<!天)秤(?!量)',text):
                kana=q.kana.replace("'",'').replace('_','').replace('/','')
                assert 'ハカリ' in kana and 'バカリ' not in kana,(cid,q.kana)
                fixes.append({'id':cid,'display_text':text,'spoken_text':spoken,'kana':q.kana,'asserted_reading':'ハカリ'})
            config=asdict(q);path=root/f'audio/ja/sentences/{cid}.wav';stamp=path.with_suffix('.json')
            if path.exists() and stamp.exists() and read(stamp)==config:counts['current_cache']+=1
            elif cid in old and old[cid]['query']==config:
                src=audition/f'_work/C/{cid}.wav';assert sha(src)==old[cid]['audio_sha256']
                shutil.copy2(src,path);counts['approved_C_reused']+=1
            else:path.write_bytes(synth.synthesis(q,14));counts['new']+=1
            save(stamp,config);audio,sr=sf.read(path,dtype='float32');assert sr==SR and audio.ndim==1
            start=cursor/SR;pieces.append(audio);cursor+=len(audio)
            cues.append({'id':cid,'text':text,'spoken_text':spoken,'start':start,'end':cursor/SR,'audio_file':str(path.relative_to(root)),'audio_sha256':sha(path)})
            gap=(.30 if role in ['opening','contrast','question','conclusion'] else .22)+.10
            if j<len(texts):pieces.append(np.zeros(round(gap*SR),np.float32));cursor+=len(pieces[-1])
            queries.append({'sentence_id':cid,'role':role,'query':config,'gap_after_seconds':gap if j<len(texts) else None,'audio_sha256':sha(path)})
        assembled=np.concatenate(pieces);out=root/f'audio/ja/{seg["id"]}.wav';sf.write(out,assembled,SR,subtype='PCM_16')
        records.append({**seg,'duration_seconds':len(assembled)/SR,'audio_file':str(out.relative_to(root)),'cues':cues,'delivery':'approved C; no slot fitting'})
        save(root/'records/narration_progress.json',{'completed_segments':len(records),'counts':counts})
        print('NARRATION',seg['id'],round(len(assembled)/SR,3),counts,flush=True)
    assert sum(len(s['cues']) for s in records)==115 and len(fixes)==4
    save(root/'records/narration_segments_ja.json',{'language':'ja','sample_rate':SR,'voice':'VOICEVOX:冥鳴ひまり','delivery':'C','cache_counts':counts,'human_auditory_review_completed':False,'segments':records})
    save(root/'records/queries.json',queries);save(root/'records/reading_corrections.json',fixes)
    # A short pronunciation check with the four corrected sentences, no BGM.
    clips=[]
    for f in fixes:
        audio,sr=sf.read(root/f'audio/ja/sentences/{f["id"]}.wav',dtype='float32');clips.extend([audio,np.zeros(SR,np.float32)])
    out=root/'_work/hakari_check.wav';sf.write(out,np.concatenate(clips),SR,subtype='PCM_16')
    ff(['-i',out,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k','-metadata','artist=VOICEVOX:冥鳴ひまり',root/'deliverables/EP001_ja_hakari_check.m4a'])

def package(root):
    picture=root/'_work/picture_cfr.mp4';raw=root/'_work/picture_master.mp4'
    assert probe(raw)['streams'][0]['time_base']=='1/15360'
    ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',picture])
    master=read(root/'records/master_timeline.json');duration=master['duration_seconds'];files=[]
    for lang in ['en','ja']:
        stem=f'EP001_Anubis_{lang}_v04_1080p30';out=root/f'deliverables/{stem}.mp4'
        shutil.copy2(root/f'deliverables/EP001_字幕_{lang}.srt',root/f'deliverables/{stem}.srt')
        ff(['-i',picture,'-i',root/f'deliverables/EP001_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),'-metadata','comment=Japanese voice: VOICEVOX:冥鳴ひまり; English: Kokoro/af_heart; external subtitles','-movflags','+faststart',out])
        ff(['-i',out,'-f','null','-']);info=probe(out);levels=measure(out)
        assert info['streams'][0]['avg_frame_rate']=='30/1'
        assert int(info['streams'][0]['nb_frames'])==round(duration*FPS)
        assert abs(float(info['format']['duration'])-duration)<1/FPS
        assert abs(float(levels['input_i'])+16)<.2 and float(levels['input_tp'])<-2
        vh=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
        files.append({'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'video_stream_hash':vh,'probe':info,'levels':levels,'full_decode':'pass'})
        print('PACKAGED',lang,round(duration,3),levels['input_i'],flush=True)
    assert files[0]['video_stream_hash']==files[1]['video_stream_hash']
    ff(['-i',root/'deliverables/EP001_Anubis_ja_v04_1080p30.mp4','-t',90,'-map','0','-c','copy','-movflags','+faststart',root/'deliverables/EP001_ja_v04_first90s.mp4'])
    save(root/'records/qc_v04.json',{'version':'v04','duration_seconds':duration,'fps':30,'subtitles_burned_in':False,'human_full_listening':False,'files':files})
    (root/'deliverables/音声クレジット.txt').write_text('English: Kokoro / af_heart (B)\n日本語音声：VOICEVOX:冥鳴ひまり（C採用）\nhttps://www.meimeihimari.com/terms-of-use\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','narration','timeline','visuals','audio','pictures','package']);args=p.parse_args()
    root=Path(os.environ['WOM_EPISODE_ROOT']);previous=Path(os.environ['WOM_PREVIOUS_ROOT'])
    os.environ['WOM_SUBTITLE_SAFE']='1';os.environ['WOM_VIDEO_CRF']='18';os.environ['WOM_LANGUAGES']='en,ja';os.environ['WOM_SENTENCE_BLOCK_GAP']='.9';os.environ['WOM_BGM_DBFS']='-33.5'
    if args.stage=='prepare':prepare(root,previous)
    elif args.stage=='narration':narration(root)
    elif args.stage=='timeline':build_timeline(root)
    elif args.stage=='visuals':visuals.main()
    elif args.stage=='audio':make_audio(root)
    elif args.stage=='pictures':pictures(root)
    elif args.stage=='package':package(root)
if __name__=='__main__':main()
