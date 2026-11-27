"""Package the approved EP016 review and verify draft assets by numeric REST ID."""
import argparse
import hashlib
import shutil
from pathlib import Path
import subprocess
import zipfile

from wom14_share import REPO, api, assert_anonymous_hidden, sha
from wom16_voice import ROOT, read, save

OUT = ROOT / 'deliverables'
RECORD = ROOT / 'records/sharing.json'
TAG = 'quiet-origins-ep016-v01-20261127'
ENDPOINT = f'repos/{REPO}/releases'
GROUPS = {
    'audio_and_subtitles': ['*.wav', '*.m4a', '*.srt', '*.txt'],
    'thumbnails_and_metadata': ['*.jpg', '*.md'],
}


def write_zip(group, members):
    out = OUT / f'EP016_{group}_v01.zip'
    temp = out.with_suffix('.part.zip')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=3) as bundle:
        for name, path in sorted(members):
            bundle.write(path, name)
    with zipfile.ZipFile(temp) as bundle:
        assert bundle.testzip() is None
    temp.replace(out)
    return out


def bundle_initial():
    for lang in ('en', 'ja'):
        copy, note = (OUT / f'EP016_upload_info_{lang}.md').read_text().split('\n---\n')
        assert 'Kokoro / Heart (af_heart)' in copy and 'VOICEVOX' not in copy
        assert 'VOICEVOX:冥鳴ひまり' in note
    assert 'VOICEVOX:冥鳴ひまり' in (OUT / 'EP016_audio_README.txt').read_text()
    files = []
    for group, patterns in GROUPS.items():
        members = [(p.name, p) for pattern in patterns for p in OUT.glob(pattern)]
        assert len(members) == (9 if group == 'audio_and_subtitles' else 6)
        files.append(write_zip(group, members))
    return files


def bundle_qc():
    files = [('technical_review.md', ROOT / 'records/technical_review.md')]
    for pattern in ('EP016_upload_info_*.md','EP016_audio_README.txt','EP016_pronunciation_*.txt'):
        files.extend((p.name,p) for p in OUT.glob(pattern))
    for lang in ('en', 'ja'):
        base = ROOT / lang
        for path in (base / 'records').glob('*.json'):
            files.append((str(path.relative_to(ROOT)), path))
        for path in (base / 'review').glob('*.jpg'):
            files.append((str(path.relative_to(ROOT)), path))
    for path in (ROOT / 'records').glob('*.json'):
        if path != RECORD:
            files.append((str(path.relative_to(ROOT)), path))
    return write_zip('QA_records', files)


def verified_video(lang, record):
    evidence = read(ROOT / lang / 'records' / record)
    source = ROOT / lang / 'deliverables' / evidence['file']
    assert sha(source) == evidence['sha256']
    if 'motion' in evidence:
        assert all(m['ratio'] is not None and 0 < m['ratio'] <= 2.5 for m in evidence['motion'])
        assert evidence['decode_warnings'] == 0
    else:
        assert evidence['continuous_decode_warnings'] == 0
    target = OUT / source.name
    if not target.exists() or sha(target) != evidence['sha256']:
        temp = target.with_suffix('.copying')
        shutil.copy2(source, temp)
        assert sha(temp) == evidence['sha256']
        temp.replace(target)
    return target


def draft():
    if RECORD.exists():
        release = api([f'{ENDPOINT}/{read(RECORD)["release_id"]}'])
    else:
        matches = [r for r in api([f'{ENDPOINT}?per_page=100']) if r['tag_name'] == TAG]
        release = matches[0] if matches else api(['--method', 'POST', ENDPOINT, '--input', '-'], {
            'tag_name': TAG, 'target_commitish': 'bgm/production', 'draft': True,
            'name': 'Quiet Origins 第16話「セイレーンはいつ人魚になったのか」確認版v01',
            'body': '本人試聴・制作確認用。公開用は英語音声、日本語の題と概要欄は翻訳。日本語MP4と単体音声は確認用。単体音声の声クレジットは音声ZIPのREADMEに同梱。'})
    assert release['tag_name'] == TAG and release['draft'] is True
    assert_anonymous_hidden(f'{ENDPOINT}/{release["id"]}')
    return release


def share(paths, final=False):
    release = draft()
    rid = release['id']
    state = read(RECORD) if RECORD.exists() else dict(release_id=rid, tag=TAG, draft=True,
                release_url=release['html_url'], status='uploading', assets=[])
    assert state['release_id'] == rid
    save(RECORD, state)
    for path in paths:
        size = path.stat().st_size
        digest = sha(path)
        current = api([f'{ENDPOINT}/{rid}'])
        assert current['draft'] and current['tag_name'] == TAG
        asset = next((a for a in current['assets'] if a['name'] == path.name), None)
        if asset is None:
            subprocess.run(['gh', 'release', 'upload', TAG, str(path), '--repo', REPO], check=True)
            current = api([f'{ENDPOINT}/{rid}'])
            assert current['draft']
            asset = next(a for a in current['assets'] if a['name'] == path.name)
        assert asset['size'] == size and asset['digest'] == 'sha256:' + digest, path.name
        cached = next((r for r in state['assets'] if r['asset_id'] == asset['id']), None)
        if cached and cached['rest_download_verified'] and cached['sha256'] == digest:
            continue
        endpoint = f'{ENDPOINT}/assets/{asset["id"]}'
        assert_anonymous_hidden(endpoint)
        for attempt in range(3):
            h = hashlib.sha256()
            n = 0
            with subprocess.Popen(['gh', 'api', '-H', 'Accept: application/octet-stream', endpoint],
                                  stdout=subprocess.PIPE) as proc:
                for chunk in iter(lambda: proc.stdout.read(1048576), b''):
                    h.update(chunk)
                    n += len(chunk)
                if proc.wait() == 0 and n == size and h.hexdigest() == digest:
                    break
        else:
            raise RuntimeError(f'REST download mismatch: {path.name}')
        state['assets'].append(dict(name=path.name, asset_id=asset['id'], bytes=n, sha256=digest,
                                    rest_download_verified=True, anonymous_http_status=404))
        save(RECORD, state)
        print('REST verified', path.name, n, flush=True)
    if final:
        remote = api([f'{ENDPOINT}/{rid}'])
        assert remote['draft'] and len(remote['assets']) == len(state['assets']) == len(paths) == 8
        assert {a['id'] for a in remote['assets']} == {a['asset_id'] for a in state['assets']}
        state['status'] = 'verified'
        save(RECORD, state)
    print('Draft', rid, state['status'], len(state['assets']), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('step',choices=['package','share'])
    if parser.parse_args().step=='package':
        for lang in ('en','ja'):
            for record in ['technical_qc.json','subtitled_review.json']:
                verified_video(lang,record)
        verified_video('en','technical_qc_4k.json')
        bundle_initial()
        bundle_qc()
    else:
        outputs=sorted([*OUT.glob('EP016_Sirens_*p30.mp4'),*OUT.glob('EP016_*_v01.zip')])
        assert len(outputs)==8
        share(outputs,final=True)
