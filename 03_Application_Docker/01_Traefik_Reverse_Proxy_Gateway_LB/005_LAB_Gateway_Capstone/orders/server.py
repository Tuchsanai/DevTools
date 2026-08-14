import json
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOSTNAME = socket.gethostname()
LOCK = threading.Lock()
STATE = {"served": 0}


class Handler(BaseHTTPRequestHandler):
    server_version = "DevToolsOrders/1.0"

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self.respond(200, b"OK\n", "text/plain; charset=utf-8")
            return

        with LOCK:
            STATE["served"] += 1
            served = STATE["served"]
        body = json.dumps(
            {
                "service": "orders",
                "hostname": HOSTNAME,
                "message": "Order service accepted the gateway request",
                "served_count": served,
                "path": path,
                "forwarded_host": self.headers.get("X-Forwarded-Host", ""),
                "forwarded_proto": self.headers.get("X-Forwarded-Proto", ""),
            },
            separators=(",", ":"),
        ).encode()
        self.respond(200, body, "application/json")

    def respond(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"LAB005 orders listening on :{port} hostname={HOSTNAME}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
