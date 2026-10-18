"""Copy approved thumbnails and record dimensions and checksums; no image generation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / 'iro/全巻サムネ変更_20261018'
specs = json.loads((DOC / 'manifest.json').read_text())
main = {}
for filename in ['generated_paths.json', 'outputs_batch2.json', 'outputs_batch3.json']:
    main.update(json.loads((DOC / filename).read_text()))
short = json.loads((DOC / 'short_generated_paths.json').read_text())
rows = []
for spec in specs:
    slug = spec['slug']
    dest = Path('/Users/ryo/Desktop/BGM/IRO') / spec['series'] / spec['folder'][3:]
    dest.mkdir(parents=True, exist_ok=True)
    for kind, mapping in [('main', main), ('short', short)]:
        suffix = '_ショート_サムネ' if kind == 'short' else '_サムネ'
        jpg = ROOT / 'サムネ確認用/IRO Sounds' / (slug + suffix + '.jpg')
        out = dest / (slug + suffix + '_用途中心_20261018.jpg')
        shutil.copy2(jpg, out)
        if slug in mapping:
            shutil.copy2(mapping[slug], dest / (slug + suffix + '_用途中心_20261018.png'))
        info = subprocess.check_output(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(jpg)], text=True)
        dims = [int(line.split(':')[1]) for line in info.splitlines() if 'pixel' in line]
        assert dims == ([720, 1280] if kind == 'short' else [1280, 720]), (slug, dims)
        assert jpg.stat().st_size < 1_000_000
        assert out.exists() and hashlib.sha256(out.read_bytes()).digest() == hashlib.sha256(jpg.read_bytes()).digest()
        rows.append(dict(volume=slug, kind=kind, jpg=str(jpg.relative_to(ROOT)), mac=str(out), width=dims[0], height=dims[1], bytes=jpg.stat().st_size, sha256=hashlib.sha256(jpg.read_bytes()).hexdigest()))
(DOC / 'asset_checks.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
print(f'{len(rows)} JPG files checked and copied; maximum {max(x["bytes"] for x in rows)} bytes')
