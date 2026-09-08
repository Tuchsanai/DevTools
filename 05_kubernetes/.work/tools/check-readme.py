#!/usr/bin/env python3
"""check-readme.py <lab-dir>... — structural lint of lab READMEs against spec section 4 + lab-outline.
Prints one line per check: OK/WARN/FAIL. Exit code = number of FAILs (capped 99)."""
import re, sys, os, glob

OUTLINE = open('/root/workspace/DevTools/05_kubernetes/.work/lab-outline.md', encoding='utf-8').read()
REQUIRED_ORDER = [
    r'^## วัตถุประสงค์ของปฏิบัติการ', r'^## แนวคิดและทฤษฎีที่เกี่ยวข้อง', r'^## ผลการเรียนรู้ที่คาดหวัง', r'^## ภาพรวมของปฏิบัติการ',
    r'^## 0\. การเตรียมสภาพแวดล้อมสำหรับปฏิบัติการ', r'^## 1\. การดึงโค้ดของปฏิบัติการ \(Clone\)', r'การทดลองจำลองความล้มเหลว', r'แบบฝึกหัด \(Exercise\)', r'^## วิธีตรวจสอบผลการทดลอง',
    r'^## ปัญหาที่พบบ่อยและแนวทางแก้ไข', r'Cleanup', r'^## สรุปคำสั่งของปฏิบัติการนี้', r'^## สรุปสิ่งที่ได้เรียนรู้', r'คำถามทบทวนก่อนจบปฏิบัติการ', r'รายการตรวจสอบก่อนจบปฏิบัติการ',
]
SECRET_PAT = re.compile(r'(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|[A-Za-z0-9._%+-]+@(?!example\.)[A-Za-z0-9.-]+\.[a-z]{2,})')

def concept_from_outline(lab):
    m = re.search(r'^## ' + re.escape(lab) + r'\n- \*\*แนวคิดหลัก:\*\* (.+)$', OUTLINE, re.M)
    return m.group(1).strip() if m else None

def check(labdir):
    lab = os.path.basename(labdir.rstrip('/'))
    p = os.path.join(labdir, 'README.md')
    fails = 0
    def out(kind, msg):
        nonlocal fails
        if kind == 'FAIL': fails += 1
        print(f'{kind:4s} {lab}: {msg}')
    if not os.path.exists(p):
        out('FAIL', 'README.md missing'); return 1
    t = open(p, encoding='utf-8').read(); lines = t.splitlines()
    n = len(lines)
    out('OK' if 200 <= n <= 400 else 'WARN', f'length {n} lines (target 200-400)')
    # title + concept
    out('OK' if re.match(r'^# LAB \d+ — ', lines[0]) else 'FAIL', f'title line: {lines[0][:60]}')
    c = concept_from_outline(lab)
    m = re.search(r'💡 \*\*แนวคิดหลักของปฏิบัติการนี้:\*\* (.+)', t)
    if not m: out('FAIL', 'concept block missing')
    elif c and m.group(1).strip().rstrip('*').strip() != c: out('WARN', f'concept differs from outline:\n       README : {m.group(1).strip()[:110]}\n       outline: {c[:110]}')
    else: out('OK', 'concept line matches outline')
    # heading order
    pos = []
    for pat in REQUIRED_ORDER:
        mm = None
        for i, l in enumerate(lines):
            if l.startswith('#') and re.search(pat, l): mm = i; break
        pos.append(mm)
    missing = [REQUIRED_ORDER[i] for i, x in enumerate(pos) if x is None]
    if missing: out('FAIL', f'missing sections: {missing}')
    else:
        order_ok = all(pos[i] < pos[i+1] for i in range(len(pos)-1))
        out('OK' if order_ok else 'FAIL', 'section order ' + ('correct' if order_ok else f'wrong: {pos}'))
    # three-part rule: every ```bash block should be followed (within ~12 lines) by 📝 and ✅
    bash_blocks = [i for i, l in enumerate(lines) if l.strip().startswith('```bash')]
    lacking = []
    for i in bash_blocks:
        # find end of block
        j = i + 1
        while j < n and not lines[j].strip().startswith('```'): j += 1
        window = '\n'.join(lines[j+1:j+14])
        has_note = '📝' in window; has_exp = '✅' in window
        if not (has_note and has_exp): lacking.append((i+1, has_note, has_exp))
    out('OK' if not lacking else 'WARN', f'{len(bash_blocks)} bash blocks; {len(lacking)} lacking 📝/✅ within 13 lines: {lacking[:6]}')
    # expected outputs must have text blocks
    out('OK' if t.count('```text') >= max(3, len(bash_blocks)//2) else 'WARN', f"{t.count('```text')} text (output) blocks")
    # question before start, single-picture closing, next-lab pointer, footer
    for label, pat in [('คำถามนำก่อนเริ่มปฏิบัติการ', r'คำถามนำก่อนเริ่มปฏิบัติการ'), ('ภาพรวมที่ควรจดจำ', r'ภาพรวมที่ควรจดจำ'), ('🧭 การเชื่อมโยงสู่ปฏิบัติการถัดไป', r'🧭 การเชื่อมโยงสู่ปฏิบัติการถัดไป'), ('footer real-run line', r'ผลลัพธ์ที่คาดหวัง \(expected output\) และภาพหน้าจอในเอกสารนี้ได้มาจากการดำเนินการจริง')]:
        out('OK' if re.search(pat, t) else 'FAIL', label)
    # diagram reference
    exp_svg = f'../slides_assets/lab{lab[:3]}-architecture.svg'
    out('OK' if exp_svg in t else 'FAIL', f'diagram ref {exp_svg}')
    # image refs exist
    imgs = re.findall(r'!\[[^\]]*\]\((images/[^)]+)\)', t)
    missing_img = [i for i in imgs if not os.path.exists(os.path.join(labdir, i))]
    out('OK' if not missing_img else 'FAIL', f'{len(imgs)} image refs, missing: {missing_img}')
    unused = [f for f in glob.glob(os.path.join(labdir, 'images', '*')) if os.path.basename(f) not in ' '.join(imgs)]
    if unused: out('WARN', f'images not referenced: {[os.path.basename(u) for u in unused]}')
    # cross-session path refs (forbidden)
    own = os.path.basename(os.path.dirname(os.path.abspath(labdir.rstrip('/'))))
    refs = set(re.findall(r'0[123]_Session[0-9]_[A-Za-z_]+', t))
    bad = sorted(r for r in refs if r != own)
    out('OK' if not bad else 'FAIL', f'cross-session folder refs (other sessions): {bad[:3]}')
    # secrets / real ids
    sec = SECRET_PAT.findall(t)
    out('OK' if not sec else 'FAIL', f'possible real email/token: {sec[:3]}')
    # student env constants
    for s in ['localhost:8080', 'localhost:3000']:
        pass
    out('OK' if 'k8s-course-net' not in t and 'devtools-k8s-lab-' not in t and '172.30.' not in t else 'FAIL', 'no worker-only names/IPs leaked')
    out('OK' if re.search(r'kubectl delete (ns|namespace) lab' + lab[:3], t) else 'WARN', 'cleanup deletes own namespace')
    # checklist count
    cb = len(re.findall(r'^- \[ \]', t, re.M)); out('OK' if 5 <= cb <= 12 else 'WARN', f'{cb} checklist items')
    return fails

if __name__ == '__main__':
    total = 0
    for d in sys.argv[1:]: total += check(d); print()
    sys.exit(min(total, 99))
