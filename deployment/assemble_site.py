"""GitHub Pages build: copy curated publication files and vendor verified dependencies."""
import concurrent.futures
import hashlib
import json
import shutil
import time
import urllib.request
from pathlib import Path

root = Path.cwd()
site = root / '_site'
site.mkdir(exist_ok=True)
for source in root.iterdir():
    if source.name in {'.git', '.github', '_site', 'deployment', 'README.md'}:
        continue
    target = site / source.name
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    elif source.is_file():
        shutil.copy2(source, target)
manifest = json.loads((root / 'apps/ci/runtime-manifest.json').read_text(encoding='utf-8'))

def fetch(entry):
    if not (entry['url'].startswith('https://cdn.jsdelivr.net/pyodide/v0.28.1/full/')
            or entry['url'] == 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js'):
        raise ValueError('Unexpected dependency origin')
    target = (site / entry['path']).resolve()
    if not target.is_relative_to(site.resolve()):
        raise ValueError('Unexpected dependency destination')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(entry['url'], timeout=90) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise ValueError('Dependency checksum mismatch: ' + entry['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            return entry['path']
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    for path in executor.map(fetch, manifest['files']):
        print('Vendored:', path)
print('Complete GitHub Pages artifact assembled.')
