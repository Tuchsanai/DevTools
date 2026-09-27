#!/usr/bin/env python3
"""Run real SCM builds sequentially and save redacted evidence."""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__)); import jk
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jobs = sys.argv[1:] or ['local-jenkinsfile', 'upstream-main']
summary = []
for job in jobs:
    jp = f'/job/verify-local/job/{job}'
    prefix = 'lab3-reorder-20260927' + ('l' if job.startswith('local') else 'u')
    t0 = time.time()
    n = jk.build(jp, {'TAG_PREFIX': prefix})
    d = jk.wait(jp, n)
    log = jk.console(jp, n)
    open(f'{W}/evidence/build-{job}-{n}.console.txt', 'w', encoding='utf-8').write(log)
    stages = re.findall(r'^\[Pipeline\] \{ \((.+?)\)$', log, re.M)
    rec = {'job': job, 'build': n, 'result': d['result'], 'duration_s': round(d['duration'] / 1000),
           'wall_s': round(time.time() - t0), 'tag_prefix': prefix, 'stages_seen': stages,
           'obtained_line': next((l for l in log.splitlines() if l.startswith('Obtained ')), None),
           'digests': sorted(set(re.findall(r'sha256:[0-9a-f]{64}', log)))}
    summary.append(rec)
    print(json.dumps(rec, ensure_ascii=False), flush=True)
json.dump(summary, open(f'{W}/evidence/builds-summary.json', 'w'), indent=2, ensure_ascii=False)
