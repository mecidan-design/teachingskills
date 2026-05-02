from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json

ROOT = Path.cwd()

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/manifest':
            manifest = ROOT / 'data' / 'manifest.json'
            if manifest.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(manifest.read_bytes())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error':'Manifest no encontrado. Ejecutá python3 build_data.py'}).encode())
            return
        return super().do_GET()

if __name__ == '__main__':
    import os
    os.chdir(ROOT / 'public')
    server = ThreadingHTTPServer(('0.0.0.0', 3000), Handler)
    print('Servidor en http://localhost:3000')
    server.serve_forever()
