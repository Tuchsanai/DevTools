#!/usr/bin/env python3
"""Verify the generated LAB 3 README against the tested sources and the sibling/password brief. Owner: yolo3.
Exit 0 only if every check passes. Secret values are read from env/private files and never printed."""
import os, pathlib, re, subprocess, sys
W = pathlib.Path(__file__).resolve().parent.parent
LAB = W.parent.parent / '003_LAB_Docker_Build_Push'
r = (LAB / 'README.md').read_text(encoding='utf-8')
jf = (LAB / 'Jenkinsfile').read_text()
ok = True
def check(name, cond, detail=''):
    global ok
    ok &= bool(cond); print(('OK  ' if cond else 'FAIL'), name, detail if not cond else '')

# 1. every marked host block is byte-identical to the tested block and passes bash -n
blocks = re.findall(r'<!-- lab3-test:([\w-]+) -->\n```bash\n(.*?)```', r, re.S)
for name, body in blocks:
    src = (W / 'blocks' / f'{name}.sh').read_text()
    check(f'block {name} identical', body == src)
    check(f'block {name} bash -n', subprocess.run(['bash', '-n'], input=body, text=True).returncode == 0)
check('all 8 host blocks present', {b for b, _ in blocks} == {p.stem for p in (W / 'blocks').glob('*.sh')}, [b for b, _ in blocks])
# 2. embedded Jenkinsfile identical
m = re.search(r'```groovy\n(// LAB 3.*?)\n```', r, re.S)
check('Jenkinsfile embedded identical', m and m.group(1) == jf.rstrip('\n'))
# 3. topology / auth requirements in the Jenkinsfile
ssh_lines = [l for l in jf.splitlines() if re.search(r'(?<![\w-])ssh -', l) and not l.strip().startswith('//')]
check('every ssh call uses sshpass -e + StrictHostKeyChecking=yes',
      len(ssh_lines) == 2 and all('sshpass -e ssh -o StrictHostKeyChecking=yes' in l for l in ssh_lines), ssh_lines)
check('no key auth / gateway in Jenkinsfile', not re.search(r'sshUserPrivateKey|SSH_KEY|devtools-gw|-i "|StrictHostKeyChecking=no|sshpass -p', jf))
check('ssh sh() steps are constant single-quoted strings',
      all(not re.search(r'sh\(script: "', jf) for _ in [0]) and "sh(script: 'sshpass -e ssh" in jf)
check('usernamePassword devtools-ssh bound in onDevtools and Push',
      jf.count("usernamePassword(credentialsId: 'devtools-ssh'") == 2)
# 4. setup is one sequential host workflow with the required topology
setup = (W / 'blocks' / 'host-setup.sh').read_text()
for need in ('docker network create cicd-net', '--name devtools --network cicd-net --privileged', '-p 2222:22 -p 3000:3000',
             '--name jenkins --network cicd-net', '-p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21'):
    check(f'setup has {need!r}', need in setup)
check('jenkins has no docker socket / docker CLI install', 'docker.sock' not in setup and 'docker.io' not in (W / 'blocks' / 'sshpass.sh').read_text())
# 5. removed alternatives and old mechanisms
banned = {'ทาง A': 'ทาง A', 'ทาง B': 'ทาง B', 'devtools-gw': 'devtools-gw', 'gateway': r'gateway(?! ของ)', 'authorized_keys': 'authorized_keys',
          'ssh-keygen -t': 'ssh-keygen -t', 'private key file': 'jenkins_devtools', 'SSH Agent': r'ssh-agent|SSH Agent', 'host-gateway': 'host-gateway',
          'StrictHostKeyChecking=no': 'StrictHostKeyChecking=no', 'SSH Username with private key': 'SSH Username with private key'}
for name, pat in banned.items():
    check(f'no {name}', not re.search(pat, r), re.findall(r'.{0,40}' + pat + r'.{0,40}', r)[:2])
# 6. images, placeholders, fences, whitespace
imgs = re.findall(r'\]\(\./images/([^)]+)\)', r)
check('all image links exist', all((LAB / 'images' / i).exists() for i in imgs), [i for i in imgs if not (LAB / 'images' / i).exists()])
old_topology = [i for i in imgs if re.match(r'lab3_(jenkins|stage|app|hub_0[123]|diagram_(architecture|pipeline_flow))', i)]
check('no old-topology screenshots referenced', not old_topology, old_topology)
check('no unfilled placeholders', not re.search(r'\{\{\w+:', r))
check('code fences balanced', len(re.findall(r'^```', r, re.M)) % 2 == 0)
check('no trailing whitespace', not re.search(r'[ \t]+$', r, re.M))
check('figure numbers sequential', [int(n) for n in re.findall(r'^\*ภาพที่ (\d+) ', r, re.M)] == list(range(1, len(re.findall(r'^\*ภาพที่ \d+ ', r, re.M)) + 1)))
# 7. secrets never in README, evidence, blocks or scripts
secrets = [v for v in (os.environ.get('DOCKER_TOKEN'),) if v]
for f in ('jpass',):
    p = W / 'private' / f
    if p.exists(): secrets.append(p.read_text().strip())
hub = os.environ.get('DOCKER_USER')
files = [LAB / 'README.md', LAB / 'Jenkinsfile'] + [p for d in ('out', 'blocks', 'scripts') if (W / d).exists() for p in (W / d).rglob('*') if p.is_file()]
leaks = [str(p.relative_to(W.parent.parent)) for p in files for s in secrets if s and s in p.read_text(errors='ignore')]
check(f'no secret values in {len(files)} files ({len(secrets)} secrets checked)', not leaks, leaks)
check('Docker Hub account name replaced in README', not hub or not re.search(r'(?<![A-Za-z])' + re.escape(hub) + r'/catfood-shop', r))
print('README lines', len(r.splitlines()), 'figures', len(re.findall(r'^\*ภาพที่ \d+ ', r, re.M)), 'blocks', len(blocks))
sys.exit(0 if ok else 1)
