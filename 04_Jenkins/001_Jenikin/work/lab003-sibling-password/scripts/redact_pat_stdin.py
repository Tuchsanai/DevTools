#!/usr/bin/env python3
"""Sanitize the real Docker Hub "token generated" screenshot. Owner: yolo3.
Reads the raw PNG or JPEG from stdin only (the raw capture is never written to disk), covers the token rectangle with an opaque
#202020 fill (no blur, no text), and writes
    images/lab3_hub_05_pat_generated.png       = whole capture, every pixel outside the box untouched
    images/lab3_hub_05_pat_generated_crop.png  = pure crop of the sanitized image
Usage (coordinator):  <capture command that writes PNG/JPEG to stdout> | python3 scripts/redact_pat_stdin.py
       --out DIR writes to DIR instead of images/ (self-test only)."""
import io, pathlib, sys
sys.exit('redact_pat_stdin.py is retired: ภาพที่ 3ก now uses the generated demo images/lab3_hub_pat_demo.png')
from PIL import Image
W = pathlib.Path(__file__).resolve().parent.parent
IMG = pathlib.Path(sys.argv[2]) if sys.argv[1:2] == ['--out'] else W.parent.parent / '003_LAB_Docker_Build_Push' / 'images'
SIZE = (3425, 1244)                     # real CUA bytes (viewport reports 3440x1249); never resized
BOX = (1030, 580, 1450, 655)            # token field, conservative, PIL box (x0, y0, x1, y1), x1/y1 exclusive
CROP = (1020, 100, 1760, 750)
FILL = (0x20, 0x20, 0x20)
FULL, CROPF = IMG / 'lab3_hub_05_pat_generated.png', IMG / 'lab3_hub_05_pat_generated_crop.png'

raw = sys.stdin.buffer.read()
assert raw, 'no image on stdin'
src = Image.open(io.BytesIO(raw))
assert src.format in ('PNG', 'JPEG'), f'stdin is {src.format}, expected PNG or JPEG'
assert src.size == SIZE, f'size {src.size} != {SIZE}'
orig = src.convert('RGB'); del raw, src
im = orig.copy()
im.paste(FILL, BOX)

# opaque box, nothing else changed
assert im.crop(BOX).tobytes() == Image.new('RGB', (BOX[2] - BOX[0], BOX[3] - BOX[1]), FILL).tobytes(), 'box not fully covered'
mask = Image.new('L', SIZE, 255); mask.paste(0, BOX)
blank = Image.new('RGB', SIZE)
assert Image.composite(im, blank, mask).tobytes() == Image.composite(orig, blank, mask).tobytes(), 'pixels outside box changed'
del orig

IMG.mkdir(parents=True, exist_ok=True)
tmp_full, tmp_crop = FULL.with_suffix('.tmp.png'), CROPF.with_suffix('.tmp.png')
im.save(tmp_full, format='PNG', optimize=True)
cr = im.crop(CROP); cr.save(tmp_crop, format='PNG', optimize=True)
assert Image.open(tmp_full).convert('RGB').tobytes() == im.tobytes(), 'full re-read mismatch'
assert Image.open(tmp_crop).convert('RGB').tobytes() == cr.tobytes(), 'crop re-read mismatch'
tmp_full.replace(FULL); tmp_crop.replace(CROPF)
print(f'wrote {FULL.name} {im.size} and {CROPF.name} {cr.size}; box {BOX} filled #202020')
