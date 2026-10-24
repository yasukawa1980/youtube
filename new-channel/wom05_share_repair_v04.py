"""Share only the repaired deliverables in a private draft GitHub Release."""
import json
import subprocess
import urllib.request
import urllib.error
from wom05_repair_encoding_v04 import ROOT, sha

REPO = 'yasukawa1980/youtube'
TAG = 'wom05-tengu-v04-20261025'
assert json.loads((ROOT/'records/repair_qc.json').read_text())['passed']

def assert_not_public(url):
    request = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Draft-visibility-check'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raise AssertionError(f'Draft resource is publicly accessible: HTTP {response.status}')
    except urllib.error.HTTPError as error:
        assert error.code == 404, error.code

names = [
    'EP005_Tengu_en_v04_1080p30.mp4', 'EP005_Tengu_ja_v04_1080p30.mp4',
    'EP005_Tengu_en_v04_1080p30.srt', 'EP005_Tengu_ja_v04_1080p30.srt',
    'EP005_audio_ja.wav', 'EP005_thumbnail_met_24145.jpg', 'SHA256SUMS_shared.txt',
]
paths = [ROOT/'deliverables'/name for name in names] + [ROOT/'records/repair.json', ROOT/'records/repair_qc.json']
for line in (ROOT/'deliverables/SHA256SUMS_shared.txt').read_text().splitlines():
    digest, name = line.split(maxsplit=1)
    assert sha(ROOT/'deliverables'/name.lstrip('* ')) == digest, name

def api(endpoint):
    return json.loads(subprocess.check_output(['gh', 'api', endpoint]))

# The draft was created once with --draft. Resolve it directly rather than
# using the eventually consistent release listing or creating a duplicate.
info = json.loads(subprocess.check_output(['gh', 'release', 'view', TAG,
    '--repo', REPO, '--json', 'databaseId,tagName,isDraft,publishedAt']))
assert info['tagName'] == TAG and info['isDraft'] and info['publishedAt'] is None
release = api(f'repos/{REPO}/releases/{info["databaseId"]}')
assert release['draft']
assert release['published_at'] is None
assert_not_public(release['url'])
assert_not_public(release['html_url'])
for path in paths:
    release = api(f'repos/{REPO}/releases/{release["id"]}')
    assert release['draft'] and release['published_at'] is None
    existing = next((a for a in release['assets'] if a['name'] == path.name), None)
    if existing:
        assert existing['digest'] == 'sha256:' + sha(path)
    else:
        subprocess.run(['gh', 'release', 'upload', TAG, str(path), '--repo', REPO], check=True)
    print('UPLOADED', path.name, flush=True)
release = api(f'repos/{REPO}/releases/{release["id"]}')
assert release['draft'] and release['published_at'] is None
checks = []
for path in paths:
    a = next(a for a in release['assets'] if a['name'] == path.name)
    assert a['digest'] == 'sha256:' + sha(path) and a['size'] == path.stat().st_size
    assert_not_public(a['browser_download_url'])
    checks.append({'name': path.name, 'asset_id': a['id'], 'bytes': a['size'], 'sha256': sha(path)})
record = {'release_id': release['id'], 'tag': TAG, 'draft': release['draft'],
    'published_at': release['published_at'], 'anonymous_release_and_assets_http_status': 404,
    'url': release['html_url'], 'assets': checks, 'verification': 'GitHub server SHA256 digest and size match local files'}
(ROOT/'records/sharing.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(record, ensure_ascii=False, indent=2))
