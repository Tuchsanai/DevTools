#!/usr/bin/env python3
"""Build ../Kafka_Slides.html from Kafka_Slides.src.html + image assets.

Every <img data-a="KEY"> in the source is resolved through ASSETS below.
PNG/JPG files are downscaled (max 1400 px wide) and re-encoded as WebP so the
single-file deck stays small; SVG files are embedded as-is.

Run from anywhere:  python3 slides_assets/build_slides.py
"""
import base64, io, json, os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KAFKA = os.path.dirname(HERE)
LAB1 = os.path.join(KAFKA, '001_LAB_Kafka_Setup', 'images')
LAB2 = os.path.join(KAFKA, '002_LAB_Partitions_Keys', 'images')
LAB3 = os.path.join(KAFKA, '003_LAB_Consumer_Groups', 'images')
LAB4 = os.path.join(KAFKA, '004_LAB_Event_Pipeline', 'images')
SVG = os.path.join(HERE, 'svg')          # excalidraw exports kept from the previous deck

ASSETS = {
    # --- excalidraw SVGs from the previous deck (still accurate) ---
    'd01': f'{SVG}/d01.svg', 'd02': f'{SVG}/d02.svg', 'd03': f'{SVG}/d03.svg',
    'd07': f'{SVG}/d07.svg', 'd10': f'{SVG}/d10.svg', 'd11': f'{SVG}/d11.svg',
    'd12': f'{SVG}/d12.svg', 'd15': f'{SVG}/d15.svg',
    # --- concept images already generated for the lab readmes ---
    'c1_queue_log': f'{LAB1}/concept-queue-vs-log.png',
    'c1_replay':    f'{LAB1}/concept-replay.png',
    'c1_ports':     f'{LAB1}/arch-ports.png',
    'c2_listeners': f'{LAB2}/concept-00-two-listeners.png',
    'c2_partitions':f'{LAB2}/concept-01-partitions.png',
    'c2_rules':     f'{LAB2}/concept-02-three-rules.png',
    'c2_hash':      f'{LAB2}/concept-03-hash-routing.png',
    'c2_ordering':  f'{LAB2}/concept-04-ordering.png',
    'c2_repart':    f'{LAB2}/concept-05-repartition-break.png',
    'c2_hot':       f'{LAB2}/concept-06-hot-partition.png',
    'c3_group':     f'{LAB3}/concept-01-consumer-group.png',
    'c3_rebalance': f'{LAB3}/concept-02-rebalance.png',
    'c3_lag':       f'{LAB3}/concept-03-lag.png',
    'c3_ceiling':   f'{LAB3}/concept-04-parallelism-ceiling.png',
    'c3_dispatch':  f'{LAB3}/concept-05-rabbitmq-vs-kafka-dispatch.png',
    'c4_pipeline':  f'{LAB4}/concept-01-pipeline.png',
    'c4_json':      f'{LAB4}/concept-02-json-bytes.png',
    'c4_stage':     f'{LAB4}/concept-03-consumer-plus-producer.png',
    'c4_twogroups': f'{LAB4}/concept-04-two-groups.png',
    'c5_replay':    f'{LAB4}/concept-05-replay-log.png',
    # --- Kafka UI screenshots from the real run ---
    'ui_topics':    f'{LAB4}/ui-01-topics-pipeline.png',
    'ui_group':     f'{LAB3}/ui-02-group-workers.png',
    # --- new images generated for the deck (cyolo1 imagegen) ---
    'bigpicture':   f'{HERE}/concept-big-picture.png',
    'c5_bookmark':  f'{HERE}/concept-bookmark-3-cases.png',
    'c3_close_kill':f'{HERE}/concept-close-vs-kill.png',
    'c6_boot':      f'{HERE}/concept-compose-boot-order.png',
    'c3_offsets':   f'{HERE}/concept-consumer-offsets.png',
    'c5_decoupled': f'{HERE}/concept-pipeline-decoupled.png',
}
# fallbacks if a new image is not available yet
FALLBACK = {'bigpicture': 'd03'}

MAX_W = 1400
WEBP_Q = 82


def encode(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.svg':
        data = open(path, 'rb').read()
        return 'data:image/svg+xml;base64,' + base64.b64encode(data).decode()
    im = Image.open(path)
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA')
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=WEBP_Q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    src = open(os.path.join(HERE, 'Kafka_Slides.src.html'), encoding='utf-8').read()
    used = sorted(set(re.findall(r'data-a="([^"]+)"', src)))
    out, missing, sizes = {}, [], {}
    for key in used:
        path = ASSETS.get(key)
        if not path or not os.path.exists(path):
            fb = FALLBACK.get(key)
            if fb and os.path.exists(ASSETS[fb]):
                print(f'  [fallback] {key} -> {fb}')
                path = ASSETS[fb]
            else:
                missing.append(key)
                continue
        out[key] = encode(path)
        sizes[key] = len(out[key])
    unused = sorted(set(ASSETS) - set(used))
    line = '<script>window.ASSETS=' + json.dumps(out, ensure_ascii=False) + '</script>'
    html = src.replace('<!--ASSETS-->', line)
    target = os.path.join(KAFKA, 'Kafka_Slides.html')
    open(target, 'w', encoding='utf-8').write(html)
    n = len(re.findall(r'<div class="slot">', html))
    print(f'wrote {target}  slides={n}  size={len(html.encode())/1e6:.2f} MB  assets={len(out)}')
    for k in sorted(sizes, key=sizes.get, reverse=True)[:8]:
        print(f'  {k:14s} {sizes[k]/1e3:7.0f} KB')
    if missing:
        print('MISSING assets:', missing)
    if unused:
        print('unused asset keys:', unused)
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
