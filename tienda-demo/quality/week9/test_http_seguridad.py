"""Pruebas HTTP deterministicas del servidor local usado para las pruebas k6."""
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from scripts.qa_server import create_server


class SeguridadHttp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:%d' % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _request(self, path, method='GET', body=None):
        try:
            with urlopen(Request(self.url + path, method=method, data=body), timeout=3) as r:
                return r.status, r.headers, r.read()
        except HTTPError as e:
            return e.code, e.headers, e.read()

    def test_s09_s01_inicio(self):
        status, _, body = self._request('/')
        self.assertEqual(status, 200)
        self.assertIn(b'TiendaDemo', body)

    def test_s09_s02_archivos_estaticos(self):
        for path in ('/carrito.js', '/estilos.css'):
            with self.subTest(path=path):
                self.assertEqual(self._request(path)[0], 200)

    def test_s09_s03_bloqueo_archivo_privado(self):
        self.assertEqual(self._request('/.git/config')[0], 404)

    def test_s09_s04_traversal(self):
        self.assertEqual(self._request('/%2e%2e/%2e%2e/requirements.txt')[0], 403)

    def test_s09_s05_url_malformada(self):
        self.assertEqual(self._request('/%ZZ')[0], 400)

    def test_s09_s05b_utf8_invalido_rechazado(self):
        # Percent-encoded valid syntax, but invalid UTF-8 code points.
        # This path CAN be transmitted by k6's Go HTTP client.
        self.assertEqual(self._request('/%ED%A0%80')[0], 400)

    def test_s09_s06_post_no_permitido(self):
        self.assertEqual(self._request('/', method='POST', body=b'{}')[0], 405)

    def test_s09_s07_cuerpo_grande(self):
        self.assertEqual(self._request('/', method='POST', body=b'x' * 17000)[0], 413)

    def test_s09_s08_metodo_put(self):
        self.assertEqual(self._request('/', method='PUT', body=b'{}')[0], 405)

    def test_s09_s09_cabeceras(self):
        _, headers, _ = self._request('/')
        for header in ('X-Frame-Options', 'X-Content-Type-Options', 'Content-Security-Policy'):
            with self.subTest(header=header):
                self.assertIn(header, headers)

    def test_s09_s10_ruta_inexistente(self):
        self.assertEqual(self._request('/desconocido')[0], 404)
