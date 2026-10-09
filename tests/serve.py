#!/usr/bin/env python3
"""Local preview with the same static 404 document used by GitHub Pages."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]

class Handler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)
        content = (ROOT / '404.html').read_bytes()
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        if self.command != 'HEAD': self.wfile.write(content)

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    os.chdir(ROOT)
    print('Preview: http://127.0.0.1:4174/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 4174), Handler).serve_forever()
