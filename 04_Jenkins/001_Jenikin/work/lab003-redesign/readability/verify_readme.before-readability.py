#!/usr/bin/env python3
"""Check README code blocks marked lab3-test and the full Jenkinsfile block are identical to the tested sources."""
import re, pathlib, sys
W = pathlib.Path(__file__).resolve().parent.parent; LAB = W.parent.parent / '003_LAB_Docker_Build_Push'
r = (LAB / 'README.md').read_text(); ok = True
for name, body in re.findall(r'<!-- lab3-test:([\w-]+) -->\n```bash\n(.*?)```', r, re.S):
    same = body == (W / 'blocks' / f'{name}.sh').read_text(); ok &= same; print(name, 'OK' if same else 'DIFF')
jf = re.search(r'```groovy\n(// LAB 3.*?)\n```', r, re.S).group(1)
same = jf == (LAB / 'Jenkinsfile').read_text().rstrip('\n'); ok &= same; print('Jenkinsfile', 'OK' if same else 'DIFF')
launch = 'docker network create cicd-net\ndocker run -d --name jenkins --network cicd-net --restart unless-stopped \\\n  -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21\n'
print('jenkins launch exact', launch in r and launch == (W/'blocks'/'jenkins-launch.sh').read_text())
setup = 'docker rm -f devtools\ndocker run -dit --name devtools --privileged --tmpfs /run \\\n  -p 2222:22 -p 8080:8080 -p 3000:3000 -p 8000:8000 \\\n  tuchsanai/devtools:2569_1\nssh root@localhost -p 2222        # password : passwd\n'
print('learner setup exact', setup in r)
for img in re.findall(r'\]\(\./images/([^)]+)\)', r): 
    if not (LAB / 'images' / img).exists(): ok = False; print('missing image', img)
sys.exit(0 if ok else 1)
