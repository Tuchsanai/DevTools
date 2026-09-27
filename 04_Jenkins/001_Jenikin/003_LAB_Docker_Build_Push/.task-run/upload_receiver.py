#!/usr/bin/env python3
"""Loopback-only PNG upload receiver for LAB003 screenshots.

PUT or POST /upload/<name>.png with raw PNG bytes as the body.
Files land only in .task-run/images/. Names are restricted to
[A-Za-z0-9_-]{1,64}.png, so no path traversal is possible.

GET /artifact/<basename> serves one of the final README images from
../images/ read-only. Only names in ARTIFACTS are served; anything else is 404.
"""
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "images")
NAME_RE = re.compile(r"^/upload/([A-Za-z0-9_-]{1,64}\.png)$")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 20 * 1024 * 1024
README_IMAGES = os.path.join(os.path.dirname(HERE), "images")
ARTIFACTS = {
    "lab3_shop_tour.gif": "image/gif",
    "lab3_localfix_stages_builds_1_2.png": "image/png",
    "lab3_localfix_shop_v100_build1_full.png": "image/png",
    "lab3_localfix_shop_v110_build2_full.png": "image/png",
    "lab3_shop_tour_01_hero.png": "image/png",
    "lab3_shop_tour_02_products.png": "image/png",
    "lab3_shop_tour_03_filter.png": "image/png",
    "lab3_shop_tour_04_cart.png": "image/png",
    "lab3_shop_tour_05_deployment.png": "image/png",
}


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, msg):
        body = (msg + "\n").encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._reply(200, "ok")
        if self.path == "/list":
            names = sorted(os.listdir(OUT_DIR))
            return self._reply(200, "\n".join(
                f"{n}\t{os.path.getsize(os.path.join(OUT_DIR, n))}" for n in names))
        if self.path.startswith("/artifact/"):
            name = self.path[len("/artifact/"):]
            ctype = ARTIFACTS.get(name)  # exact allow-list match, no path parsing
            if ctype:
                with open(os.path.join(README_IMAGES, name), "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return self.wfile.write(data)
        self._reply(404, "not found")

    def do_PUT(self):
        m = NAME_RE.match(self.path)
        if not m:
            return self._reply(400, "path must be /upload/<[A-Za-z0-9_-]{1,64}>.png")
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self._reply(411, "Content-Length required")
        if length <= 0 or length > MAX_BYTES:
            return self._reply(413, f"body must be 1..{MAX_BYTES} bytes")
        data = self.rfile.read(length)
        if len(data) != length or not data.startswith(PNG_MAGIC):
            return self._reply(400, "body is not a complete PNG")
        final = os.path.join(OUT_DIR, m.group(1))
        tmp = final + ".part"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, final)
        self._reply(201, f"saved images/{m.group(1)} {length} bytes")

    do_POST = do_PUT

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
    os.makedirs(OUT_DIR, exist_ok=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
