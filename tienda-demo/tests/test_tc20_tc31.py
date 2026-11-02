"""Casos funcionales TC-20 a TC-31: checkout y confirmación."""

from selenium.webdriver.common.by import By

from tests.base_test_case import TiendaDemoTestCase


class TestTC20TC31(TiendaDemoTestCase):
    # TC-20: Bloquear el checkout cuando el carrito está vacío.
    def test_20_checkout_bloqueado_si_carrito_vacio(self):
        """Verifica que no se pueda acceder al checkout con el carrito vacío."""
        self.driver.execute_script("""
            estado.carrito = [];
            irACheckout();
        """)
        self.assertEqual(self.driver.execute_script("return estado.vista;"), 'catalogo')

    # TC-21: Validar todos los campos vacíos del checkout.
    def test_21_validar_checkout_con_campos_vacios(self):
        """Verifica que checkout marque como obligatorios los campos vacíos."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.confirm_payment()
        self.assertEqual(len(self.checkout.get_error_messages()), 5)

    # TC-22: Validar que el nombre sea obligatorio.
    def test_22_validar_nombre_obligatorio(self):
        """Verifica la validación del nombre obligatorio."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
        self.checkout.confirm_payment()
        self.assertTrue(any('nombre' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-23: Validar que se ingresen nombre y apellido.
    def test_23_validar_apellido_obligatorio(self):
        """Verifica la validación del apellido obligatorio."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('María', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
        self.checkout.confirm_payment()
        self.assertTrue(any('apellido' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-24: Validar que el correo sea obligatorio.
    def test_24_validar_email_obligatorio(self):
        """Verifica la validación del correo electrónico obligatorio."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('María López', '', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
        self.checkout.confirm_payment()
        self.assertTrue(any('correo' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-25: Rechazar un correo con formato inválido.
    def test_25_validar_email_invalido(self):
        """Verifica que se rechace un correo con formato inválido."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('María López', 'correo-no-valido', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
        self.checkout.confirm_payment()
        self.assertTrue(any('correo' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-26: Validar que el teléfono sea obligatorio.
    def test_26_validar_telefono_obligatorio(self):
        """Verifica la validación del teléfono obligatorio."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '')
        self.checkout.confirm_payment()
        self.assertTrue(any('teléfono' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-27: Validar que la dirección sea obligatoria.
    def test_27_validar_direccion_obligatoria(self):
        """Verifica la validación de la dirección obligatoria."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('María López', 'maria@correo.com', '', 'Lima', '987654321')
        self.checkout.confirm_payment()
        self.assertTrue(any('dirección' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-28: Validar que la ciudad sea obligatoria.
    def test_28_validar_ciudad_obligatoria(self):
        """Verifica la validación de la ciudad obligatoria."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', '', '987654321')
        self.checkout.confirm_payment()
        self.assertTrue(any('ciudad' in msg.lower() for msg in self.checkout.get_error_messages()))

    # TC-29: Confirmar una compra con datos válidos.
    def test_29_confirmar_compra_con_datos_validos(self):
        """Verifica que se complete una compra con datos válidos."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('¡Compra realizada con éxito!', self.checkout.driver.page_source)

    # TC-30: Confirmar una compra con varios productos.
    def test_30_confirmar_compra_con_varios_productos(self):
        """Verifica que se confirme una compra con varios productos."""
        self.catalog.add_product('Disco SSD 1TB')
        self.catalog.add_product('Teclado Mecánico')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('¡Compra realizada con éxito!', self.checkout.driver.page_source)

    # TC-31: Verificar la pantalla de confirmación de la compra.
    def test_31_pantalla_de_confirmacion_visible(self):
        """Verifica que la confirmación de compra sea visible."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('Gracias', self.checkout.driver.page_source)

    # TC-31: Volver al catálogo desde la confirmación de compra.
    def test_checkout_volver_al_catalogo_desde_confirmacion(self):
        """Verifica que se pueda volver al catálogo tras confirmar la compra."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.driver.find_element(By.ID, 'btn-seguir-comprando').click()
        self.assertTrue(self.driver.execute_script("return document.getElementById('vista-catalogo').classList.contains('activa');"))