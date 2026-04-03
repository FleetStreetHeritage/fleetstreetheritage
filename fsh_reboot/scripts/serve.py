#!/usr/bin/env python3
"""
Serve docs/dev/ on the local network for device testing.
Usage: python fsh_reboot/scripts/serve.py [port]
Default port: 8000
"""

import http.server
import os
import socket
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

SERVE_DIR = Path(__file__).parent.parent.parent / 'docs' / 'dev'

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

os.chdir(SERVE_DIR)

handler = http.server.SimpleHTTPRequestHandler
handler.log_message = lambda *a: None  # suppress per-request noise

ip = local_ip()
print(f'Serving {SERVE_DIR}')
print(f'Local:   http://localhost:{PORT}')
print(f'Network: http://{ip}:{PORT}')
print('Ctrl-C to stop.')

with http.server.HTTPServer(('0.0.0.0', PORT), handler) as httpd:
    httpd.serve_forever()
