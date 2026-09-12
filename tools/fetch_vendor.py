"""Development only. Runtime uses the included local modules, with no CDN."""
from pathlib import Path
from urllib.request import urlopen
import hashlib
import json

base = "https://raw.githubusercontent.com/mrdoob/three.js/r169/"
files = {"build/three.module.js": "three.module.js", "examples/jsm/controls/OrbitControls.js": "OrbitControls.js", "examples/jsm/controls/TransformControls.js": "TransformControls.js", "LICENSE": "THREE-LICENSE.txt"}
manifest = {}
for source, output in files.items():
    output = output.replace('.js', '.mjs')
    raw = urlopen(base + source).read()
    data = raw.replace(b"from 'three'", b"from './three.module.mjs'")
    (Path(__file__).resolve().parents[1] / "web" / "vendor" / output).write_bytes(data)
    manifest[output] = {"source": base+source, "source_sha256": hashlib.sha256(raw).hexdigest(), "local_sha256": hashlib.sha256(data).hexdigest()}
(Path(__file__).resolve().parents[1] / "web" / "vendor" / "manifest.json").write_text(json.dumps(manifest,indent=2))
