#!/usr/bin/env python3
"""Write CAPTURE_READY.json for the host coordinator's real-browser screenshots. Owner: yolo3.
Contains names, ports, URLs and build results only; the admin password stays in private/browser-auth.json."""
import datetime, json, pathlib, re, subprocess
W = pathlib.Path(__file__).resolve().parent.parent
O = W / 'out'
st = dict(l.split('=', 1) for l in (W / 'state.env').read_text().split() if '=' in l)
ip = lambda c: subprocess.run(['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', c],
                              capture_output=True, text=True).stdout.strip()
jl, al = f"http://localhost:{st['P_JENKINS']}", f"http://localhost:{st['P_APP']}"
builds = []
for n in range(1, 6):
    j = json.loads((O / f'b{n}.json').read_text()); txt = (O / f'b{n}.txt').read_text()
    d = re.search(r'([\w.-]+-\d+): digest: (sha256:[0-9a-f]{64})', txt)
    builds.append({'build': n, 'result': j['result'], 'stages': (O / f'b{n}.stages').read_text().splitlines(),
                   **({'tag': d.group(1), 'digest': d.group(2)} if d else {})})
prefix = re.sub(r'-\d+$', '', builds[0]['tag'])
shots = []
for i, (key, _alt, _cap, url, what) in enumerate(json.loads((W / 'shots.json').read_text()), 1):
    full = {'APP': al + '/', 'HUB': f'https://hub.docker.com/r/<DOCKER_USER>/catfood-shop/tags?name={prefix}'}.get(url, jl + url if url.startswith('/') else url)
    shots.append({'save_as': f'host-captures/{i:02d}-{key}.png', 'url': full, 'capture': what})
ready = {
    'written_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'owner': 'yolo3 (LAB003 sibling/password run)', 'run_hash': st['H'],
    'containers': {'devtools': st['DC'], 'jenkins': st['JC']}, 'network': st['NET'], 'jenkins_home_volume': st['VOL'],
    'host_loopback_ports': {'jenkins': f"127.0.0.1:{st['P_JENKINS']}->8080", 'devtools_ssh': f"127.0.0.1:{st['P_SSH']}->22", 'app': f"127.0.0.1:{st['P_APP']}->3000 (devtools) -> catfood-web:3000"},
    'container_ips_on_run_network': {'jenkins': ip(st['JC']), 'devtools': ip(st['DC'])},
    'urls': {'jenkins': jl + '/', 'jenkins_via_container_ip': f"http://{ip(st['JC'])}:8080/", 'app': al + '/', 'app_health': al + '/api/health',
             'dockerhub_tags': f'https://hub.docker.com/r/<DOCKER_USER>/catfood-shop/tags?name={prefix}'},
    'jenkins_login': {'username': 'admin', 'password_file': 'work/lab003-sibling-password/private/browser-auth.json (mode 600, git-ignored, shredded at cleanup)'},
    'jenkins_url_setting': jl + '/', 'job': 'docker-build-push', 'tag_prefix': prefix, 'builds': builds,
    'app_now': (O / 'web-b5.txt').read_text().splitlines()[0],
    'shots': shots,
    'rules': [
        'Real host browser only; clip each capture to the readable region (about 900-1400 px wide) and save it under the given save_as name (PNG or JPEG data both fine).',
        'Do NOT click Build / Build Now / Save / Delete, do not edit credentials, and do not restart or remove the containers: the running shop must stay build #2.',
        '01-unlock.png already exists (captured from run 1 of this same topology before its wizard); keep it.',
        'Log in as admin with the password from browser-auth.json; do not show that password or the Docker Hub token in any capture.',
        'When done, create work/lab003-sibling-password/CAPTURE_DONE (empty is fine); yolo3 then integrates the images, rebuilds and verifies the README, and removes all run resources.',
    ],
}
(W / 'CAPTURE_READY.json').write_text(json.dumps(ready, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: ready[k] for k in ('urls', 'host_loopback_ports', 'container_ips_on_run_network')}, indent=1))
