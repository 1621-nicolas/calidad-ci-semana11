"""Semana 9: prueba de seguridad del DOM. Puede revelar un defecto real."""
from tests.base_test_case import TiendaDemoTestCase
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


class Semana09SeguridadUI(TiendaDemoTestCase):
    def test_s09_s11_busqueda_no_ejecuta_html_introducido(self):
        # Dato de prueba local: no contacta servidores ni extrae informacion.
        payload = '<img src=x onerror="window.__qa_inyeccion=1">'
        self.driver.execute_script('window.__qa_inyeccion = 0')
        self.driver.find_element('id', 'buscador').send_keys(payload)
        self.driver.find_element('id', 'btn-buscar').click()
        # Un evento onerror puede dispararse de manera asincrona.
        try:
            WebDriverWait(self.driver, 1).until(
                lambda d: d.execute_script('return window.__qa_inyeccion === 1'))
        except TimeoutException:
            pass
        self.assertEqual(self.driver.execute_script('return window.__qa_inyeccion'), 0,
                         'Posible XSS basado en DOM: renderCatalogo usa innerHTML con el texto de busqueda')
