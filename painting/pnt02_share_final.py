"""Add v01 review deliveries to the existing private draft and verify REST downloads."""
import hashlib
import subprocess
from pnt02_produce import ROOT, REPO, read, save, sha
from pnt02_share_checkpoint import api, REPOSITORY

RELEASE_ID=439743216
RECORD=REPO/'painting/pnt02_確認版_v01_20261110/final_sharing.json'


def main():
    qc=read(REPO/'painting/pnt02_確認版_v01_20261110/final_summary.json')
    assert qc['technical_checks_passed']
    files=[]
    for lang in ['en','ja']:
        files.extend(sorted((ROOT/lang/'deliverables').glob('*.mp4')))
    assert len(files)==5
    files += [ROOT/'deliverables'/name for name in [
        'PNT02_audio_subtitles_final_v01.zip',
        'PNT02_final_QC_metadata_thumbnails_v01.zip']]
    assert all(p.is_file() for p in files)
    release=api(f'repos/{REPOSITORY}/releases/{RELEASE_ID}')
    assert release['draft'] is True
    original_assets={a['id'] for a in release['assets']}
    state=dict(release_id=RELEASE_ID,draft=True,status='uploading_v01',assets=[])
    save(RECORD,state)
    for path in files:
        expected=sha(path)
        old=next((a for a in release['assets'] if a['name']==path.name),None)
        if old:
            assert old['digest']=='sha256:'+expected,'Preserve old asset; choose a new name for changed content'
        else:
            subprocess.run(['gh','api','--method','POST',
                f'https://uploads.github.com/repos/{REPOSITORY}/releases/{RELEASE_ID}/assets?name={path.name}',
                '-H','Content-Type: application/octet-stream','--input',str(path),'--silent'],check=True)
        print('UPLOADED',path.name,flush=True)
        # Explicit release ID lookup followed by the numeric asset ID download.
        release=api(f'repos/{REPOSITORY}/releases/{RELEASE_ID}')
        assert release['draft'] is True
        asset=next(a for a in release['assets'] if a['name']==path.name)
        assert asset['digest']=='sha256:'+expected and asset['size']==path.stat().st_size
        process=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',
            f'repos/{REPOSITORY}/releases/assets/{asset["id"]}'],stdout=subprocess.PIPE)
        digest=hashlib.sha256();size=0
        for chunk in iter(lambda:process.stdout.read(1024*1024),b''):
            digest.update(chunk);size+=len(chunk)
        assert process.wait()==0 and digest.hexdigest()==expected and size==path.stat().st_size
        state['assets'].append(dict(name=path.name,asset_id=asset['id'],bytes=size,sha256=expected,rest_download_verified=True))
        save(RECORD,state)
        print('REST VERIFIED',path.name,flush=True)
    body='確認版v01：英日1080p、英語4K、英日字幕入りの動画5本、最終音声・字幕、検品記録・サムネ2案・投稿情報。旧 preliminary ZIP 2件は制作途中資料として保全。年代帯は訂正1238455を反映。固有名・難読語の音声資料との実聴照合および本人の全編試聴は未完了。切替時刻は文音声と字幕内の文字位置から補間。公開・投稿・予約しない。取得案内：bgm/production の painting/pnt02_確認版_v01_20261110/README.md。'
    release=api(f'repos/{REPOSITORY}/releases/{RELEASE_ID}','PATCH',dict(
        name='Quiet Origins 絵画02 pnt02 確認版v01（非公開・本人試聴待ち）',body=body,draft=True))
    assert release['draft'] is True and original_assets <= {a['id'] for a in release['assets']}
    hidden=subprocess.check_output(['curl','-q','-sS','-o','/dev/null','-w','%{http_code}',
        '-H','Accept: application/vnd.github+json',f'https://api.github.com/repos/{REPOSITORY}/releases/{RELEASE_ID}'],text=True)
    assert hidden=='404'
    state.update(status='v01_shared_pending_user_listening',anonymous_http_status=hidden,
                 previous_assets_preserved=True,url=release['html_url'])
    save(RECORD,state)
    print('DRAFT VERIFIED',RELEASE_ID,len(files),flush=True)


if __name__=='__main__':
    main()
