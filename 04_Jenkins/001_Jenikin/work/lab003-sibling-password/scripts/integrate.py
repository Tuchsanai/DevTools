#!/usr/bin/env python3
"""Bring the real host-browser captures and the cyolo1 diagrams into 003_LAB_Docker_Build_Push/images. Owner: yolo3.
- diagrams/{architecture,pipeline}-sibling.png (cyolo1) -> images/lab3_diagram_sibling_{architecture,pipeline}.png
- captures.json: host-captures/<src> (JPEG data under .png names) is decoded once, then
    images/lab3_sib_<key>.png       = the whole capture, re-encoded as real PNG (pixels identical to the decoded capture)
    images/lab3_sib_<key>_crop.png  = a pure rectangular crop of those pixels (no resize, no retouch)
- every other images/lab3_*.png that the README does not use -> archive_old_images/ (+ MANIFEST.txt, SHA256SUMS)
Does not touch images/.ipynb_checkpoints or any non-lab3 file. Idempotent."""
import hashlib, json, pathlib, shutil
from PIL import Image
W = pathlib.Path(__file__).resolve().parent.parent
IMG = W.parent.parent / '003_LAB_Docker_Build_Push' / 'images'
ARC = W / 'archive_old_images'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
KEEP = {'lab3_github_01_source.png', 'lab3_github_01_source_crop.png', 'lab3_hub_04_pat_setup.png', 'lab3_hub_04_pat_setup_crop.png'}
man = []
for src, dst in (('architecture-sibling.png', 'lab3_diagram_sibling_architecture.png'), ('pipeline-sibling.png', 'lab3_diagram_sibling_pipeline.png')):
    s = W / 'diagrams' / src
    shutil.copyfile(s, IMG / dst); man.append({'dst': dst, 'src': str(s.relative_to(W)), 'sha256': sha(s)})
for c in json.loads((W / 'captures.json').read_text()):
    s = W / 'host-captures' / c['src']
    im = Image.open(s); fmt = im.format; im = im.convert('RGB')
    full, crop = IMG / f"lab3_sib_{c['key']}.png", IMG / f"lab3_sib_{c['key']}_crop.png"
    im.save(full, format='PNG', optimize=True)
    x0, y0, x1, y1 = c['box']
    assert 0 <= x0 < x1 <= im.width and 0 <= y0 < y1 <= im.height, (c['key'], im.size, c['box'])
    cr = im.crop((x0, y0, x1, y1)); cr.save(crop, format='PNG', optimize=True)
    assert Image.open(full).format == 'PNG' and Image.open(full).convert('RGB').tobytes() == im.tobytes(), 'full pixel mismatch'
    assert Image.open(crop).convert('RGB').tobytes() == cr.tobytes(), 'crop pixel mismatch'
    man.append({'key': c['key'], 'src': str(s.relative_to(W)), 'src_format': fmt, 'src_size': list(im.size), 'sha256_src': sha(s),
                'crop_box': c['box'], 'crop_size': [x1 - x0, y1 - y0], 'full': full.name, 'crop': crop.name})
used = KEEP | {e.get('dst') for e in man} | {e.get('full') for e in man} | {e.get('crop') for e in man}
ARC.mkdir(exist_ok=True)
moved = []
for p in sorted(IMG.glob('lab3_*.png')):
    if p.name not in used:
        shutil.move(str(p), ARC / p.name); moved.append(p.name)
if moved:
    with open(ARC / 'MANIFEST.txt', 'a') as f:
        f.write('# moved from 003_LAB_Docker_Build_Push/images (not used by the final README); restore: mv archive_old_images/<file> ../../003_LAB_Docker_Build_Push/images/\n')
        f.writelines(n + '\n' for n in moved)
    (ARC / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(ARC.glob('*.png'))))
(W / 'integrate-manifest.json').write_text(json.dumps(man, indent=1, ensure_ascii=False))
print(f'integrated {len(man)} images, archived {len(moved)}: {moved}')
