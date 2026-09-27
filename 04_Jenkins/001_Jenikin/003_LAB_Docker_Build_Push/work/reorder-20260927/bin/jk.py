#!/usr/bin/env python3
"""Tiny Jenkins REST helper for the owned LAB 3 validation Jenkins (http://127.0.0.1:8080).
Secrets come from secrets/ or the runtime environment and are never printed; saved logs are redacted."""
import base64, http.cookiejar, json, os, sys, time, urllib.parse, urllib.request

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'http://127.0.0.1:8080'
PW = open(os.path.join(W, 'secrets', 'jenkins-admin-password')).read().strip()
AUTH = 'Basic ' + base64.b64encode(f'admin:{PW}'.encode()).decode()
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
_crumb = None


def redact(text):
    for k in ('DOCKER_USER', 'DOCKER_TOKEN'):
        v = os.environ.get(k)
        if v:
            text = text.replace(v, f'<{k}>')
    return text.replace(PW, '<JENKINS_ADMIN_PASSWORD>')


def req(method, path, data=None, ctype=None):
    global _crumb
    h = {'Authorization': AUTH}
    if method != 'GET':
        if _crumb is None:
            _crumb = json.loads(req('GET', '/crumbIssuer/api/json')[1])
        h[_crumb['crumbRequestField']] = _crumb['crumb']
    if ctype:
        h['Content-Type'] = ctype
    r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with opener.open(r) as resp:
            return resp.status, resp.read().decode('utf-8', 'replace'), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace'), e.headers


def script(groovy):
    return req('POST', '/scriptText', urllib.parse.urlencode({'script': groovy}).encode(),
               'application/x-www-form-urlencoded')


def create_or_update(folder_path, name, xml):
    st, _, _ = req('GET', f'{folder_path}/job/{name}/api/json')
    if st == 200:
        return req('POST', f'{folder_path}/job/{name}/config.xml', xml.encode(), 'application/xml; charset=UTF-8')[0]
    return req('POST', f'{folder_path}/createItem?name={name}', xml.encode(), 'application/xml; charset=UTF-8')[0]


def build(job_path, params):
    st, body, hdr = req('POST', f'{job_path}/buildWithParameters', urllib.parse.urlencode(params).encode(),
                        'application/x-www-form-urlencoded')
    if st != 201:
        raise SystemExit(f'build trigger failed {st}: {redact(body)[:300]}')
    q = hdr['Location'].replace(BASE, '').rstrip('/')
    for _ in range(600):
        st, body, _ = req('GET', q + '/api/json')
        exe = json.loads(body).get('executable') if st == 200 else None
        if exe:
            return exe['number']
        time.sleep(1)
    raise SystemExit('queue timeout')


def wait(job_path, n, timeout=3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st, body, _ = req('GET', f'{job_path}/{n}/api/json?tree=building,result,duration')
        d = json.loads(body)
        if not d['building']:
            return d
        time.sleep(3)
    raise SystemExit('build timeout')


def console(job_path, n):
    return redact(req('GET', f'{job_path}/{n}/consoleText')[1])


def stages(job_path, n):
    st, body, _ = req('GET', f'{job_path}/{n}/wfapi/describe')
    if st == 200:
        return [(s['name'], s['status'], s.get('durationMillis')) for s in json.loads(body)['stages']]
    return f'wfapi {st}'


if __name__ == '__main__':
    print('import me')
