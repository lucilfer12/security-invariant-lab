from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

class DashboardHandler(BaseHTTPRequestHandler):
    directory = Path(".silab").resolve()

    def _send(self, body: bytes, content_type: str = "application/json", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            path = "/report.html"
        if path.startswith("/api/"):
            return self._api(path)
        safe = Path(path.lstrip("/")).resolve()
        try:
            safe.relative_to(self.directory)
        except ValueError:
            return self._send(b"forbidden", "text/plain", 403)
        if not safe.exists():
            return self._send(b"not found", "text/plain", 404)
        content_type = "text/html; charset=utf-8" if safe.suffix == ".html" else "text/plain; charset=utf-8"
        return self._send(safe.read_bytes(), content_type)

    def _api(self, path: str) -> None:
        mapping = {
            "/api/scan": "scan.json",
            "/api/properties": "properties.json",
            "/api/surface": "attack-surface.json",
        }
        name = mapping.get(path)
        if not name:
            return self._send(b'{"error":"unknown endpoint"}', status=404)
        target = self.directory / name
        if not target.exists():
            return self._send(b'{"error":"run scan first"}', status=404)
        return self._send(target.read_bytes())

    def log_message(self, format: str, *args) -> None:
        return

def serve(directory: str | Path = ".silab", host: str = "127.0.0.1", port: int = 8765) -> None:
    DashboardHandler.directory = Path(directory).resolve()
    DashboardHandler.directory.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"SIL dashboard: http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".silab")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.dir, args.host, args.port)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
