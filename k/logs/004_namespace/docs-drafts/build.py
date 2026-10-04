import json, os, re, sys

D = json.load(open('/root/workspace/DevTools/k/logs/004_namespace/images.json'))
BYID = {x['id']: x for x in D}


def build(src_parts, out, img_prefix='images/', ss_prefix='images/screenshots/'):
    text = ''.join(open(p).read() for p in src_parts)
    figs = []
    pat = re.compile(r'\{\{(FIG|SS):([^|}]+)\|([^|}]+)(?:\|([^}]+))?\}\}')

    def repl(m):
        kind, key, alt, cap = m.group(1), m.group(2), m.group(3), m.group(4)
        n = len(figs) + 1
        if kind == 'FIG':
            x = BYID[key]
            src = img_prefix + os.path.basename(x['path'])
            caption = x['caption_th']
            width = 900
        else:
            src = ss_prefix + key
            caption = cap
            width = 700
        figs.append((n, alt))
        return (f'<p align="center" id="fig-{n}">\n'
                f'  <img src="{src}" alt="รูปที่ {n} {alt}" width="{width}"><br>\n'
                f'  <em><b>รูปที่ {n}</b> {caption}</em>\n'
                f'</p>')

    text = pat.sub(repl, text)
    half = (len(figs) + 1) // 2
    rows = ['| รูปที่ | เรื่อง | รูปที่ | เรื่อง |', '|:---:|---|:---:|---|']
    for i in range(half):
        a = figs[i]
        b = figs[i + half] if i + half < len(figs) else None
        right = f'| {b[0]} | [{b[1]}](#fig-{b[0]}) |' if b else '| | |'
        rows.append(f'| {a[0]} | [{a[1]}](#fig-{a[0]}) {right}')
    text = text.replace('{{FIGTABLE}}', '\n'.join(rows))
    open(out, 'w').write(text)
    print(out, len(figs), 'figures', len(text.encode()), 'bytes')


if __name__ == '__main__':
    which = sys.argv[1]
    base = '/root/workspace/DevTools/k/004_kubernetes_namespace/'
    if which == 'theory':
        build(['/tmp/004/theory1.md', '/tmp/004/theory2.md', '/tmp/004/theory3.md'], base + '01_Theory/README.md')
    else:
        parts = sorted(p for p in os.listdir('/tmp/004') if p.startswith('lab') and p.endswith('.md'))
        build(['/tmp/004/' + p for p in parts], base + '02_LAB/README.md')
