#!/usr/bin/env python3
"""Static validation of README.md vs Jenkinsfile (no builds)."""
import os, re, json, subprocess
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LAB = os.path.abspath(os.path.join(W, '..', '..'))
R = open(f'{LAB}/README.md', encoding='utf-8').read(); JF = open(f'{LAB}/Jenkinsfile', encoding='utf-8').read()
res = {}
# 1 local links
links = re.findall(r'\]\((\./[^)#\s]+)', R)
missing = sorted({l for l in links if not os.path.exists(os.path.join(LAB, l))})
res['local_links'] = {'count': len(set(links)), 'missing': missing}
# 2 full embed exact
m = re.search(r'<summary><b>Jenkinsfile ฉบับสมบูรณ์.*?```groovy\n(.*?)\n```\n\n</details>', R, re.S)
res['full_embed_exact'] = bool(m) and m.group(1) + '\n' == JF
# 3 every groovy snippet is a contiguous excerpt (modulo leading indentation)
jl = [l.strip() for l in JF.split('\n')]
bad = []; blocks = re.findall(r'```groovy\n(.*?)\n```', R, re.S)
SK = '// Jenkinsfile — โครงเปล่า'
skel = [b for b in blocks if b.startswith(SK)]
blocks = [b for b in blocks if not b.startswith(SK)]
for b in blocks:
    bl = [l.strip() for l in b.split('\n')]
    if not any(jl[i:i + len(bl)] == bl for i in range(len(jl))):
        bad.append(b.split('\n')[0])
    elif b + '\n' != JF:
        raw = b.split('\n')
        if not all(l.rstrip() == l for l in raw): bad.append('trailing ws: ' + raw[0])
res['groovy_blocks'] = {'count': len(blocks), 'not_excerpt': bad}
# 3b skeleton + bash excerpts + excerpt line labels
def nocomment(t): return re.sub(r'//[^\n]*', '', re.sub(r"'[^'\n]*'|\"[^\"\n]*\"", "''", t))
res['skeleton'] = {'count': len(skel), 'braces_balanced': bool(skel) and nocomment(skel[0]).count('{') == nocomment(skel[0]).count('}'),
                   'parens_balanced': bool(skel) and nocomment(skel[0]).count('(') == nocomment(skel[0]).count(')')}
jraw = JF.split('\n'); badlab = []
for s_, e_, lang, body in re.findall(r'📄 \*ส่วนหนึ่งของ `Jenkinsfile` บรรทัด (\d+)–(\d+) [^\n]*\n\n```(\w+)\n(.*?)\n```', R, re.S):
    want = [l.strip() for l in jraw[int(s_) - 1:int(e_)]]
    got = [l.strip() for l in (body.replace('\\', '\\\\') if lang == 'bash' else body).split('\n')]
    if want != got: badlab.append((s_, e_, lang))
res['labelled_excerpts'] = {'count': len(re.findall('📄 ', R)), 'mismatch': badlab, 'bash_raw_blocks_labelled': len(re.findall(r'แสดงแบบที่ bash ได้รับ\*\n\n```bash', R))}
res['forbidden_phrases'] = [p for p in ('ไม่ต้องพิมพ์หรือคัดลอกไฟล์', 'ดึงเฉพาะ `Jenkinsfile`', 'มุมขวาบน*', 'ใช้ `Jenkinsfile` เดียวกันแบบวาง') if p in R]
# 4 fences balanced
res['fences_even'] = len(re.findall(r'^```', R, re.M)) % 2 == 0
# 5 figure numbering sequence
figs = re.findall(r'^\*ภาพที่ (\d+)([ก-ฮ]?)', R, re.M)
nums = [int(n) for n, s in figs if not s]
allnums = sorted({int(n) for n, _ in figs})
res['figures'] = {'sequence': [n + s for n, s in figs], 'numbers_consecutive_in_order': [int(n) for n, _ in figs] == sorted(int(n) for n, _ in figs) and allnums == list(range(1, max(allnums) + 1)), 'duplicates': sorted({n + s for n, s in figs if [x + y for x, y in figs].count(n + s) > 1})}
ranges = re.findall(r'ภาพที่ (\d+)–(\d+)', R)
res['figure_range_refs'] = [(a, b, int(b) <= max(nums)) for a, b in ranges]
# 6 step headings and refs
steps = [int(x) for x in re.findall(r'^## ขั้นที่ (\d+)', R, re.M)]
refs = sorted({int(x) for x in re.findall(r'ขั้นที่ (\d+)', R)})
subs = set(re.findall(r'^### (\d+\.\d+)\)', R, re.M)) | set(re.findall(r'^\*\*(\d+\.\d+)\)', R, re.M))
subrefs = set(re.findall(r'ขั้นที่ (\d+\.\d+)', R))
res['steps'] = {'headings': steps, 'consecutive': steps == list(range(1, len(steps) + 1)), 'refs_out_of_range': [r for r in refs if r > len(steps)], 'subrefs_missing': sorted(subrefs - subs), 'header_count_matches': f'🧪 {len(steps)} ขั้น' in R}
# 7 required content
need = ['Pipeline script from SCM', 'https://github.com/Tuchsanai/DevTools.git', '04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile', '*/main', 'skipDefaultCheckout()', 'devtools-ssh', 'dockerhub', 'Lightweight checkout']
res['required_terms_missing'] = [t for t in need if t not in R]
res['removed'] = {'dashboard_fig_gone': 'lab3_sib_dashboard' not in R, 'old_pipeline_script_fig_gone': 'lab3_sib_pipeline_config' not in R}
order = [R.index(x) for x in ['## ขั้นที่ 2 ', '## ขั้นที่ 3 — สร้าง Jenkins Credentials', '### 4.1) ติดตั้ง `sshpass`', '### 4.2) pin host key', '## ขั้นที่ 5 ', '## ขั้นที่ 6 — สร้าง job แบบ Pipeline script from SCM']]
res['section_order_ok'] = order == sorted(order)
layers = [R.index(x) for x in ['ชั้นที่ 1 — Credentials', 'ชั้นที่ 2 — SSH ไป devtools', 'ชั้นที่ 3 — git clone', 'ชั้นที่ 4 — Docker build', 'ชั้นที่ 5 — Docker Hub']]
res['incremental_layers_ordered'] = layers == sorted(layers)
# 8 secrets
# the public course image name <owner>/devtools:2569_1 is allowed (published image, already in the original README)
scan = re.sub(r'\b[a-z0-9]+/devtools:2569_1', 'IMAGE', R + JF)
# public Docker Hub owner of the course image (user-approved, shown in the genuine Docker Hub screenshot caption)
scan = re.sub(r'\b[a-z0-9]+/catfood-shop\b', 'IMAGE', scan)
leaks = [k for k in ('DOCKER_USER', 'DOCKER_TOKEN', 'GITHUB_TOKEN', 'SSH_PASSWORD') if os.environ.get(k) and len(os.environ[k]) > 3 and os.environ[k] in scan and os.environ[k] != 'passwd']
pw = open(f'{W}/secrets/jenkins-admin-password').read().strip()
res['secret_leaks'] = leaks + (['jenkins-admin-password'] if pw in R + JF else [])
# 9 Jenkinsfile diff vs upstream
d = subprocess.run(['diff', f'{W}/evidence/upstream-Jenkinsfile.orig', f'{LAB}/Jenkinsfile'], capture_output=True, text=True).stdout
res['jenkinsfile_diff_vs_upstream'] = d.splitlines()
ok = (not missing and res['full_embed_exact'] and not bad and res['fences_even'] and res['steps']['consecutive'] and not res['steps']['refs_out_of_range']
      and not res['steps']['subrefs_missing'] and res['steps']['header_count_matches'] and not res['required_terms_missing'] and all(res['removed'].values())
      and res['figures']['numbers_consecutive_in_order'] and not res['figures']['duplicates'] and res['section_order_ok'] and res['incremental_layers_ordered'] and not res['secret_leaks'] and res['skeleton']['braces_balanced'] and res['skeleton']['parens_balanced'] and not badlab and res['labelled_excerpts']['count'] >= 12 and not res['forbidden_phrases'])
res['ALL_STATIC_CHECKS_PASS'] = ok
print(json.dumps(res, ensure_ascii=False, indent=1))
