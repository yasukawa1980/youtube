"""Verify and execute an explicitly approved storage-audit manifest.

No recursive removal, glob deletion, directory removal or unlisted targets.
Execution requires the SHA-256 of the reviewed manifest and a fresh verification.
"""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOTS = ('/Users/ryo/youtube/bgm/', '/Volumes/ESD-EPB/BGM/', '/Volumes/ESD-02/IRO/')


def stamp(path):
    s = os.lstat(path)
    if not stat.S_ISREG(s.st_mode):
        raise ValueError('Not a regular file: ' + path)
    return [s.st_size, s.st_mtime_ns, s.st_dev, s.st_ino]


def sha256(path):
    before = stamp(path)
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024**2), b''):
            h.update(chunk)
    if stamp(path) != before:
        raise ValueError('Changed during hashing: ' + path)
    return h.hexdigest()


def opened_paths():
    r = subprocess.run(['lsof', '-nP', '-Fn'], capture_output=True, text=True, timeout=60)
    if r.returncode not in (0, 1) or not r.stdout:
        raise RuntimeError('Could not inspect open files')
    return {unicodedata.normalize('NFC', line[1:])
            for line in r.stdout.splitlines() if line.startswith('n/')}


def df():
    return subprocess.check_output(['df', '-k', '/System/Volumes/Data',
                                    '/Volumes/ESD-02', '/Volumes/ESD-EPB'], text=True)


def load_plan(path, expected_hash):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('Approved manifest hash mismatch')
    plan = json.loads(raw)
    rows = plan['candidates']
    norm = lambda x: unicodedata.normalize('NFC', x)
    sources = {norm(r['source']) for r in rows}
    if len(sources) != len(rows) or sources & {norm(r['keep']) for r in rows}:
        raise ValueError('Duplicate targets or keeper is also a deletion target')
    for r in rows:
        if not r['source'].startswith(ROOTS) or not r['keep'].startswith('/Volumes/ESD-02/'):
            raise ValueError('Path outside approved storage roots')
        for key in ('source', 'keep'):
            p = Path(r[key])
            if '..' in p.parts or any(a.is_symlink() for a in p.parents):
                raise ValueError('Symlink parent or traversal path')
    for mount in ('/Volumes/ESD-02', '/Volumes/ESD-EPB'):
        if not os.path.ismount(mount):
            raise ValueError('Expected SSD not mounted: ' + mount)
    return plan


def verify(plan, plan_hash, output):
    opened = opened_paths()
    results, cached, probes = [], {}, {}
    for i, r in enumerate(plan['candidates'], 1):
        item = {'source': r['source'], 'keep': r['keep'], 'group': r['group'],
                'bytes': r['bytes'], 'status': 'held'}
        try:
            a, b = stamp(r['source']), stamp(r['keep'])
            if a[:2] != [r['bytes'], r['source_mtime_ns']] or b[:2] != [r['keep_bytes'], r['keep_mtime_ns']]:
                raise ValueError('Changed since approved inventory')
            if any(unicodedata.normalize('NFC', r[k]) in opened for k in ('source', 'keep')):
                raise ValueError('Source or keeper open in another process')
            if r['sha256']:
                for p in (r['source'], r['keep']):
                    if p not in cached:
                        cached[p] = sha256(p)
                    if cached[p] != r['sha256']:
                        raise ValueError('Full SHA-256 does not match approved evidence')
                item['sha256'] = r['sha256']
            else:
                p = r['keep']
                if p not in probes:
                    raw = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration:stream=codec_type', '-of', 'json', p], text=True, timeout=30)
                    probe = json.loads(raw)
                    if not {'video', 'audio'} <= {s['codec_type'] for s in probe['streams']}:
                        raise ValueError('Missing audio/video stream')
                    duration = float(probe['format']['duration'])
                    expected = float(plan['final_probes'][p]['format']['duration'])
                    if abs(duration - expected) > .05:
                        raise ValueError('Keeper duration changed')
                    tail = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-ss', str(max(0, duration-2)),
                        '-i', p, '-t', '2', '-f', 'null', '-'], capture_output=True, text=True, timeout=60)
                    if tail.returncode or tail.stderr:
                        raise ValueError('Keeper tail decoding failed')
                    probes[p] = probe
                item['probe'] = probes[p]
            if stamp(r['source']) != a or stamp(r['keep']) != b:
                raise ValueError('File changed during verification')
            item.update(status='ready', source_stamp=a, keep_stamp=b)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            item['reason'] = str(exc)
        results.append(item)
        if i % 50 == 0:
            print(f'verified {i}/{len(plan["candidates"])}', flush=True)
    record = {'plan_sha256': plan_hash, 'verified_at': time.time(), 'df': df(), 'results': results}
    with open(output, 'x') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(json.dumps({'ready': sum(r['status']=='ready' for r in results),
                      'held': sum(r['status']!='ready' for r in results)}, ensure_ascii=False))


def execute(plan, plan_hash, verification, output):
    checked = json.loads(Path(verification).read_text())
    age = time.time() - checked['verified_at']
    if checked['plan_sha256'] != plan_hash or not 0 <= age < 3600:
        raise ValueError('Verification must match manifest and be less than 1 hour old')
    ready = {r['source']: r for r in checked['results'] if r['status']=='ready'}
    opened = opened_paths()
    before = df()
    # Open exclusively before any deletion so an old log cannot be overwritten.
    with open(output, 'x') as log:
        def write(item):
            log.write(json.dumps(item, ensure_ascii=False)+'\n')
            log.flush()
            os.fsync(log.fileno())
        write({'event': 'start', 'plan_sha256': plan_hash,
               'time': datetime.now(timezone.utc).isoformat(), 'df': before})
        for i, r in enumerate(plan['candidates'], 1):
            item = {'source': r['source'], 'keep': r['keep'], 'group': r['group'], 'bytes': r['bytes']}
            try:
                v = ready.get(r['source'])
                if not v:
                    raise ValueError('Preflight did not authorize this row')
                if any(unicodedata.normalize('NFC', r[k]) in opened for k in ('source', 'keep')):
                    raise ValueError('Source or keeper currently open')
                if stamp(r['source']) != v['source_stamp'] or stamp(r['keep']) != v['keep_stamp']:
                    raise ValueError('Changed after verification')
                write(dict(item, event='intent'))
                # Delete only the exact regular-file path approved in the manifest.
                os.unlink(r['source'])
                if os.path.lexists(r['source']) or stamp(r['keep']) != v['keep_stamp']:
                    raise RuntimeError('Post-deletion check failed')
                write(dict(item, event='deleted'))
            except (OSError, ValueError) as exc:
                write(dict(item, event='held', reason=str(exc)))
            if i % 100 == 0:
                print(f'processed {i}/{len(plan["candidates"])}', flush=True)
        write({'event': 'end', 'time': datetime.now(timezone.utc).isoformat(), 'df': df()})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=['verify', 'execute'])
    ap.add_argument('--plan', required=True)
    ap.add_argument('--approved-plan-sha256', required=True)
    ap.add_argument('--verification')
    ap.add_argument('--output', required=True)
    a = ap.parse_args()
    plan = load_plan(a.plan, a.approved_plan_sha256)
    if a.mode == 'verify':
        verify(plan, a.approved_plan_sha256, a.output)
    else:
        if not a.verification:
            ap.error('--verification is required for execution')
        execute(plan, a.approved_plan_sha256, a.verification, a.output)


if __name__ == '__main__':
    main()
