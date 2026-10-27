"""Read-only storage inventory. No source files are changed or removed.

Usage: python3 -m bgm.bgmkit.storage_audit --output /tmp/inventory.json ROOT ...
Paths retain their filesystem spelling; NFC is used only for comparisons.
Hidden directories, symlinks and AppleDouble files are excluded and recorded.
Logical bytes and allocated bytes are distinct; neither guarantees freed space.
"""
import argparse
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path


def inventory(roots):
    rows, errors, skipped = [], [], []
    for root in roots:
        root = os.path.abspath(root)
        if not os.path.isdir(root) or os.path.islink(root):
            errors.append({'path': root, 'error': 'Missing root or symlink root'})
            continue
        def onerror(exc):
            errors.append({'path': exc.filename, 'error': str(exc)})
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
            for name in list(dirs):
                path = os.path.join(directory, name)
                if name.startswith('.') or os.path.islink(path):
                    skipped.append(path)
                    dirs.remove(name)
            for name in files:
                path = os.path.join(directory, name)
                if name.startswith('.'):
                    continue
                try:
                    s = os.lstat(path)
                    if not stat.S_ISREG(s.st_mode):
                        skipped.append(path)
                        continue
                    rows.append({'path': path, 'root': root,
                                 'relative': os.path.relpath(path, root),
                                 'bytes': s.st_size, 'allocated_bytes': s.st_blocks * 512,
                                 'mtime_ns': s.st_mtime_ns, 'device': s.st_dev,
                                 'inode': s.st_ino, 'links': s.st_nlink})
                except OSError as exc:
                    errors.append({'path': path, 'error': str(exc)})
    return {'measured_at': datetime.now(timezone.utc).isoformat(),
            'files': rows, 'errors': errors, 'skipped': skipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('roots', nargs='+')
    args = parser.parse_args()
    output = args.output.absolute()
    for root in args.roots:
        if os.path.commonpath([str(output.resolve()), str(Path(root).resolve())]) == str(Path(root).resolve()):
            parser.error('Output must be outside the scanned roots')
    if output.exists():
        parser.error('Output already exists; choose a new output path')
    data = inventory(args.roots)
    with output.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(json.dumps({'files': len(data['files']), 'errors': data['errors'],
                      'skipped': len(data['skipped']), 'output': str(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
