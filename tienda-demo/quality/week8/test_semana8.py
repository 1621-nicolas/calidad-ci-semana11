"""Semana 8: casos funcionales de interfaz / aceptacion automatizados con Selenium."""
import unittest

from tests.base_test_case import TiendaDemoTestCase


class Semana08Funcionales(TiendaDemoTestCase):
    def test_s08_01_catalogo_muestra_productos(self):
        self.assertEqual(len(self.driver.find_elements('css selector', '.tarjeta-producto')), 8)

    def test_s08_02_producto_agregado_incrementa_contador(self):
        self.catalog.add_product('Mouse Inalámbrico')
        self.assertEqual(self.driver.find_element('id', 'contador-carrito').text, '1')

    def test_s08_03_busqueda_muestra_producto_esperado(self):
        self.driver.find_element('id', 'buscador').send_keys('Teclado')
        self.driver.find_element('id', 'btn-buscar').click()
        cards = self.driver.find_elements('css selector', '.tarjeta-producto')
        self.assertEqual(len(cards), 1)
        self.assertIn('Teclado Mecánico', cards[0].text)

    def test_s08_04_producto_sin_stock_no_disponible(self):
        self.assertFalse(self.driver.find_element('id', 'btn-agregar-5').is_enabled())

    def test_s08_05_suma_del_carrito(self):
        self.catalog.add_product('Mouse Inalámbrico')
        self.catalog.add_product('Teclado Mecánico')
        self.catalog.open_cart()
        total = self.driver.execute_script('return calcularTotales().total')
        self.assertAlmostEqual(total, 338.90, places=2)

    def test_s08_06_descuento_valido(self):
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('DESCUENTO10')
        total = self.driver.execute_script('return calcularTotales().total')
        self.assertAlmostEqual(total, 2249.10, places=2)

    def test_s08_07_carrito_vacio(self):
        self.catalog.open_cart()
        self.assertTrue(self.driver.find_element('id', 'carrito-vacio').is_displayed())

    def test_s08_08_compra_valida(self):
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('¡Compra realizada con éxito!', self.driver.page_source)
