"""Servidor HTTP local acotado para probar los recursos estaticos de TiendaDemo.

No es el backend de una tienda real: solo entrega los tres archivos publicos.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re

ROOT = Path(__file__).resolve().parents[1] / 'app'
ALLOWED = {'/tienda_demo.html', '/estilos.css', '/carrito.js'}
BAD_PERCENT = re.compile(r'%(?![0-9a-fA-F]{2})')


class DemoHandler(SimpleHTTPRequestHandler):
    server_version = 'TiendaDemoQA'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        # Evita que las pruebas de carga impriman miles de lineas.
        pass

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'")
        super().end_headers()

    def _resource(self):
        raw = urlsplit(self.path).path
        if BAD_PERCENT.search(raw):
            self.send_error(400, 'Codificacion de URL invalida')
            return None
        # Decode percent-encoded bytes strictly. A malformed UTF-8 sequence
        # must be rejected, not silently replaced and treated as a 404.
        try:
            decoded = unquote(raw, encoding='utf-8', errors='strict')
        except UnicodeDecodeError:
            self.send_error(400, 'Codificacion UTF-8 invalida')
            return None
        if any(part in ('..', '.') for part in decoded.replace('\\', '/').split('/')):
            self.send_error(403, 'Ruta prohibida')
            return None
        if decoded == '/':
            decoded = '/tienda_demo.html'
        if decoded not in ALLOWED:
            self.send_error(404, 'Recurso inexistente')
            return None
        return decoded

    def do_GET(self):
        resource = self._resource()
        if resource is not None:
            self.path = resource
            super().do_GET()

    def do_HEAD(self):
        resource = self._resource()
        if resource is not None:
            self.path = resource
            super().do_HEAD()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        if length > 16384:
            self.send_error(413, 'Limite del cuerpo superado')
        else:
            self.send_error(405, 'Metodo no permitido')

    def do_PUT(self):
        self.send_error(405, 'Metodo no permitido')

    def do_DELETE(self):
        self.send_error(405, 'Metodo no permitido')


def create_server(host='127.0.0.1', port=0):
    return ThreadingHTTPServer((host, port), DemoHandler)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8008)
    args = p.parse_args()
    with create_server(args.host, args.port) as server:
        print('TiendaDemo QA disponible en http://%s:%s/' % server.server_address, flush=True)
        server.serve_forever()
