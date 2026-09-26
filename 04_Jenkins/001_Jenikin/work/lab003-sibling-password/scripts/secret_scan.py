#!/usr/bin/env python3
"""Narrow gitleaks-style scan of the LAB 3 deliverables and work files. Owner: yolo3. Prints only file names and rule
names, never matched values.
Rules: known secret values (Docker Hub token from env, test admin password, both runs' initial admin password and its
16-char prefix, from private/ while it still exists or from private/scan-values after cleanup), plus generic patterns
(Docker/GitHub/AWS tokens, private-key blocks, the old '<16 hex>•••' unlock redaction, basic-auth URLs).
Usage: secret_scan.py [--git]   --git also scans HEAD (committed blobs) under 04_Jenkins/001_Jenikin."""
import os, pathlib, re, subprocess, sys
W = pathlib.Path(__file__).resolve().parent.parent
ROOT = W.parent.parent                      # 04_Jenkins/001_Jenikin
P = W / 'private'
vals = {}
if os.environ.get('DOCKER_TOKEN'): vals['docker-token'] = os.environ['DOCKER_TOKEN']
for f, rule in (('jpass', 'jenkins-admin-password'), ('initpw', 'initial-admin-password'),
                ('initpw16', 'initial-admin-password-prefix'), ('initpw16_run1', 'run1-initial-admin-password-prefix')):
    if (P / f).exists():
        v = (P / f).read_text().strip()
        if len(v) >= 12: vals[rule] = v
pats = {
    'docker-pat': r'dckr_pat_[A-Za-z0-9_-]{20,}', 'github-token': r'gh[pousr]_[A-Za-z0-9]{30,}',
    'aws-key': r'AKIA[0-9A-Z]{16}', 'private-key': r'-----BEGIN [A-Z ]*PRIVATE KEY-----(?:\\n|\n)[A-Za-z0-9+/=]{40,}',
    'unlock-prefix-redaction': r'[0-9a-f]{16}•', 'url-basic-auth': r'https?://[^/\s:@]+:[^/\s@]{6,}@',
}
targets = [ROOT / '003_LAB_Docker_Build_Push', W]
skip_dirs = {'node_modules', '.next', 'private', '__pycache__'}
files = [p for t in targets for p in t.rglob('*') if p.is_file() and not skip_dirs & set(p.relative_to(ROOT).parts)
         and p.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.svg', '.ico')]
hits = []
def scan(name, text):
    for rule, v in vals.items():
        if v in text: hits.append((name, rule))
    for rule, rx in pats.items():
        if re.search(rx, text): hits.append((name, rule))
for p in files:
    scan(str(p.relative_to(ROOT)), p.read_text(errors='ignore'))
if '--git' in sys.argv:
    ls = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD', '--', '.'], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for n in ls:
        if n.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.ico')) or 'node_modules' in n: continue
        blob = subprocess.run(['git', 'show', f'HEAD:./{n}'], cwd=ROOT, capture_output=True).stdout.decode(errors='ignore')
        scan('HEAD:' + n, blob)
print(f'scanned {len(files)} files, {len(vals)} known-value rules ({", ".join(sorted(vals))}), {len(pats)} pattern rules')
for h in hits: print('HIT', *h)
sys.exit(1 if hits else 0)
