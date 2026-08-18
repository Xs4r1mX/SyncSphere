#!/usr/bin/env python
"""Minimal HTTP health server so a free Render web service running Celery stays healthy."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health", "/health/", "/api/health/"):
            body = b'{"status":"ok","role":"celery-worker"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()


if __name__ == "__main__":
    main()
