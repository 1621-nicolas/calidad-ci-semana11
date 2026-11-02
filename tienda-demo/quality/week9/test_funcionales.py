"""Semana 9: validaciones de limites y flujos de TiendaDemo mediante navegador."""
from tests.base_test_case import TiendaDemoTestCase


class Semana09Funcionales(TiendaDemoTestCase):
    def test_s09_f01_limite_de_stock(self):
        self.assertFalse(self.driver.find_element('id', 'btn-agregar-5').is_enabled())
        self.assertEqual(self.driver.find_element('id', 'contador-carrito').text, '0')

    def test_s09_f02_busqueda_inexistente(self):
        self.driver.find_element('id', 'buscador').send_keys('NoExisteProducto12345')
        self.driver.find_element('id', 'btn-buscar').click()
        self.assertTrue(self.driver.find_element('id', 'sin-resultados').is_displayed())

    def test_s09_f03_multiples_unidades_actualizan_total(self):
        self.catalog.add_product('Mouse Inalámbrico')
        self.catalog.add_product('Mouse Inalámbrico')
        self.catalog.open_cart()
        self.assertAlmostEqual(self.driver.execute_script('return calcularTotales().total'), 179.80, places=2)

    def test_s09_f04_se_puede_regresar_a_catalogo(self):
        self.catalog.open_cart()
        self.driver.execute_script("mostrarVista('catalogo')")
        self.assertTrue(self.driver.find_element('id', 'vista-catalogo').get_attribute('class').find('activa') != -1)

    def test_s09_f05_cupon_invalido_no_descuenta(self):
        self._add_product('Disco SSD 1TB')
        self.cart.apply_coupon('CODIGO_NO_EXISTE')
        self.assertAlmostEqual(self.driver.execute_script('return calcularTotales().total'), 329.0, places=2)

    def test_s09_f06_checkout_valido_finaliza(self):
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertTrue(self.driver.find_element('id', 'confirmacion-card').is_displayed())
