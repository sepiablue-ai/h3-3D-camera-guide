"""Read-only release checks / 読み取り専用の公開ファイル確認. No generation."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
required = ["__init__.py", "nodes.py", "camera.py", "renderer.py", "README.md",
            "LICENSE", "THIRD_PARTY_NOTICES.md", ".gitignore", ".gitattributes",
            "requirements.txt", "web/extension.js", "web/editor.html", "web/editor.mjs", "web/camera.mjs"]
public = [ROOT / p for p in required]
for directory in ["web", "workflows", "tools", "tests", "docs"]:
    public.extend(p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
public = sorted(set(public))
for path in public:
    assert path.is_file(), f'Missing: {path}'
    text = path.read_text(encoding='utf-8-sig')
    assert not re.search(r'[A-Za-z]:[\\/]+Users[\\/]', text), f'Personal path: {path}'
    assert not re.search(r'testS\d+_T\d+_ref_', text), f'Personal reference filename: {path}'
    if path.suffix == '.md':
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            assert (path.parent / target.split('#')[0]).exists(), f'Broken link: {path}: {target}'

manifest = json.loads((ROOT/'web/vendor/manifest.json').read_text())
for name, record in manifest.items():
    actual = hashlib.sha256((ROOT/'web/vendor'/name).read_bytes()).hexdigest()
    assert actual == record['local_sha256'], f'Vendor hash mismatch: {name}'
assert manifest['THREE-LICENSE.txt']['source_sha256'] == manifest['THREE-LICENSE.txt']['local_sha256']

for path in (ROOT/'workflows').glob('*.json'):
    workflow = json.loads(path.read_text(encoding='utf-8-sig'))
    if 'nodes' not in workflow:
        assert workflow['1001']['inputs']['video'] == ['1000', 1]
        continue
    nodes = {n['id']: n for n in workflow['nodes']}
    links = {v[0]: v for v in workflow['links']}
    assert len(nodes) == len(workflow['nodes']) and len(links) == len(workflow['links'])
    for link in links.values():
        lid, source, slot, target, target_slot, kind = link
        assert lid in nodes[source]['outputs'][slot]['links']
        assert nodes[target]['inputs'][target_slot]['link'] == lid
        assert nodes[source]['outputs'][slot]['type'] == kind
    if path.name == 'minimax_h3_ref2va.json':
        inp = next(i for i in nodes[131]['inputs'] if i['name'] == 'ref_videos.ref_video_0')
        assert links[inp['link']][1:3] == [1000, 0]
        for nid in [901, 902, 903]:
            assert nodes[nid]['widgets_values_named']['image'] == f'reference_{nid-900}.png'
        prompt = nodes[131]['widgets_values_named']['prompt']
        assert '<Video 1>' in prompt and '85 degrees' not in prompt and '1.00 seconds' not in prompt

ignore = (ROOT/'.gitignore').read_text()
assert '/validation/' in ignore and '/MiniMax_H3_3D_Camera_Guide.json' in ignore
print(f'PASS: {len(public)} public files; documentation links, workflow wiring, vendor hashes and local-file exclusions.')
