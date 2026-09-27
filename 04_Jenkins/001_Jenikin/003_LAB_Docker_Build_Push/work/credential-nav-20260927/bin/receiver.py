#!/usr/bin/env python3
"""Minimal screenshot receiver (loopback only).

PUT or POST /images/<filename>  body = raw PNG bytes  -> saved as <lab>/images/<filename>
GET /health                                          -> {"ok": true}
GET /allowlist                                       -> filenames accepted (from screenshot-plan.json)
GET /received                                        -> receipts so far

Only filenames listed in screenshot-plan.json are accepted, only valid PNG bytes, max 15 MB.
Nothing is written outside <lab>/images/ except the receipts log in this work dir."""
import hashlib, http.server, json, os, struct, sys, tempfile, time

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.abspath(os.path.join(W, '..', '..'))
IMAGES = os.path.join(LAB, 'images')
PLAN = os.path.join(W, 'screenshot-plan.json')
RECEIPTS = os.path.join(W, 'evidence', 'receiver-receipts.jsonl')
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8790
MAX = 15 * 1024 * 1024
PNG_SIG = b'\x89PNG\r\n\x1a\n'


def allowlist():
    with open(PLAN, encoding='utf-8') as f:
        plan = json.load(f)
    names = set()
    for shot in plan['shots']:
        names.update(shot['files'])
    return names


class H(http.server.BaseHTTPRequestHandler):
    server_version = 'lab3-nav-receiver/1'

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=1).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            return self._json(200, {'ok': True, 'images_dir': IMAGES})
        if self.path == '/allowlist':
            return self._json(200, sorted(allowlist()))
        if self.path == '/received':
            rows = []
            if os.path.exists(RECEIPTS):
                with open(RECEIPTS, encoding='utf-8') as f:
                    rows = [json.loads(l) for l in f if l.strip()]
            return self._json(200, rows)
        return self._json(404, {'error': 'not found'})

    def do_PUT(self):
        if not self.path.startswith('/images/'):
            return self._json(404, {'error': 'use /images/<filename>'})
        name = self.path[len('/images/'):]
        if '/' in name or '\\' in name or name.startswith('.') or name not in allowlist():
            return self._json(403, {'error': 'filename not in allowlist', 'name': name})
        try:
            n = int(self.headers.get('Content-Length', '-1'))
        except ValueError:
            n = -1
        if n <= 0 or n > MAX:
            return self._json(413 if n > MAX else 411, {'error': 'Content-Length required, max 15 MB'})
        data = self.rfile.read(n)
        if len(data) != n or not data.startswith(PNG_SIG) or data[12:16] != b'IHDR':
            return self._json(415, {'error': 'body is not a PNG'})
        width, height = struct.unpack('>II', data[16:24])
        fd, tmp = tempfile.mkstemp(prefix='.upload-', dir=IMAGES)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
            os.chmod(tmp, 0o644)
            dest = os.path.join(IMAGES, name)
            replaced = os.path.exists(dest)
            os.replace(tmp, dest)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        rec = {'time': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'name': name, 'bytes': n,
               'width': width, 'height': height, 'sha256': hashlib.sha256(data).hexdigest(),
               'replaced_previous_upload': replaced}
        with open(RECEIPTS, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        return self._json(201, rec)

    do_POST = do_PUT

    def log_message(self, fmt, *args):
        sys.stderr.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), fmt % args))


if __name__ == '__main__':
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
