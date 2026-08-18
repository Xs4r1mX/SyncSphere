#!/usr/bin/env python
"""Minimal HTTP health server so a free Render web service running Celery stays healthy."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class HealthHandler(BaseHTTPRequestHandler):
    _OK_PATHS = ("/", "/health", "/health/", "/api/health/")
    _OK_BODY = b'{"status":"ok","role":"celery-worker"}\n'

    def do_GET(self):
        self._respond(include_body=True)

    def do_HEAD(self):
        # UptimeRobot and similar monitors often probe with HEAD.
        self._respond(include_body=False)

    def _respond(self, *, include_body: bool) -> None:
        if self.path in self._OK_PATHS:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(self._OK_BODY)))
            self.end_headers()
            if include_body:
                self.wfile.write(self._OK_BODY)
            return
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format, *args):
        return


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()


if __name__ == "__main__":
    main()
