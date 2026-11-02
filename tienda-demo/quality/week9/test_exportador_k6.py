"""Regresiones del exportador JUnit de k6 (no necesitan k6 instalado)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

from scripts.run_k6_suite import junit_file


class ExportadorK6(unittest.TestCase):
    def generar(self, resumen, codigo=0):
        with TemporaryDirectory() as folder:
            destino = Path(folder) / 'R01.xml'
            correcto = junit_file('rendimiento', 1, destino, codigo, resumen, 'salida k6')
            xml = ET.parse(destino).getroot()
            return correcto, xml.attrib['failures'], xml.find('testcase/failure')

    def test_resumen_con_booleanos_aprobados(self):
        resumen = {'metrics': {'checks': {'values': {'rate': 1},
                                        'thresholds': {'rate>0.99': True}}}}
        correcto, fallos, error = self.generar(resumen)
        self.assertTrue(correcto)
        self.assertEqual(fallos, '0')
        self.assertIsNone(error)

    def test_resumen_con_booleanos_fallidos(self):
        resumen = {'metrics': {'checks': {'thresholds': {'rate>0.99': False}}}}
        correcto, fallos, error = self.generar(resumen)
        self.assertFalse(correcto)
        self.assertEqual(fallos, '1')
        self.assertIn('umbral no cumplido', error.attrib['message'])

    def test_resumen_con_objetos_ok(self):
        resumen = {'metrics': {'http_req_duration': {'thresholds': {'p(95)<500': {'ok': True}}}}}
        correcto, fallos, _ = self.generar(resumen)
        self.assertTrue(correcto)
        self.assertEqual(fallos, '0')

    def test_resumen_con_objetos_fallidos(self):
        resumen = {'metrics': {'http_req_duration': {'thresholds': {'p(95)<500': {'ok': False}}}}}
        correcto, fallos, error = self.generar(resumen)
        self.assertFalse(correcto)
        self.assertEqual(fallos, '1')
        self.assertIn('p(95)<500', error.attrib['message'])

    def test_no_fabricar_aprobacion_sin_k6(self):
        correcto, fallos, error = self.generar(None, 127)
        self.assertFalse(correcto)
        self.assertEqual(fallos, '1')
        self.assertIn('No se genero resumen', error.attrib['message'])

    def test_codigo_de_error_con_umbral_ok_se_reporta(self):
        resumen = {'metrics': {'checks': {'thresholds': {'rate>0.99': True}}}}
        correcto, fallos, error = self.generar(resumen, 1)
        self.assertFalse(correcto)
        self.assertEqual(fallos, '1')
        self.assertIn('codigo 1', error.attrib['message'])

    def test_umbral_desconocido_no_aprueba(self):
        resumen = {'metrics': {'checks': {'thresholds': {'rate>0.99': 'unexpected'}}}}
        correcto, fallos, error = self.generar(resumen)
        self.assertFalse(correcto)
        self.assertEqual(fallos, '1')
        self.assertIn('desconocido', error.attrib['message'])


if __name__ == '__main__':
    unittest.main()
