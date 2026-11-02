"""Pruebas que documentan comportamientos de TiendaDemo que deben mejorarse."""

from tests.base_test_case import TiendaDemoTestCase


class TestFails(TiendaDemoTestCase):
    # TC-42: Rechazar un teléfono que contiene letras.
    def test_rechazar_telefono_con_letras(self):
        """Debe rechazar un teléfono con letras, aunque empiece por dígitos."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.com',
            'Jr. 9 de Octubre 456',
            'Lima',
            '987654321abc'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertTrue(
            any('teléfono' in message.lower()
                for message in self.checkout.get_error_messages()),
            'Se aceptó un teléfono que contiene letras'
        )

    # TC-43: Aceptar el formato telefónico sugerido en el formulario.
    def test_aceptar_telefono_con_espacios_del_placeholder(self):
        """Debe aceptar el formato de teléfono que sugiere el formulario."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.com',
            'Jr. 9 de Octubre 456',
            'Lima',
            '987 654 321'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertIn('¡Compra realizada con éxito!', self.driver.page_source)

    # TC-44: Conservar el descuento válido si después se intenta aplicar uno inválido.
    def test_cupon_invalido_no_elimina_descuento_aplicado(self):
        """Un cupón inválido no debe quitar un descuento válido ya aplicado."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('DESCUENTO10')
        self.cart.apply_coupon('INVALIDO')
        total = self.driver.execute_script("return calcularTotales().total")

        self.assertAlmostEqual(float(total), 2249.10, places=2)

    # TC-45: Rechazar una ciudad compuesta solo por números.
    def test_rechazar_ciudad_compuesta_solo_por_numeros(self):
        """Debe rechazar una ciudad que no contenga letras."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.com',
            'Jr. 9 de Octubre 456',
            '12345',
            '987654321'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertTrue(
            any('ciudad' in message.lower()
                for message in self.checkout.get_error_messages()),
            'Se aceptó una ciudad compuesta solo por números'
        )

    # TC-46: Reducir el stock del producto al confirmar una compra.
    def test_compra_actualiza_el_stock_del_producto(self):
        """La compra debe reducir el stock disponible del producto."""
        self.catalog.add_product('Laptop Pro 15')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        stock = self.driver.execute_script(
            "return PRODUCTOS.find(producto => producto.id === 1).stock"
        )

        self.assertEqual(stock, 7)

    # TC-47: Rechazar un nombre compuesto solo por números.
    def test_rechazar_nombre_compuesto_solo_por_numeros(self):
        """Debe rechazarse un nombre sin caracteres alfabéticos."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            '123 456',
            'maria@correo.com',
            'Jr. 9 de Octubre 456',
            'Lima',
            '987654321'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertTrue(
            any('nombre' in message.lower()
                for message in self.checkout.get_error_messages()),
            'Se aceptó un nombre compuesto solo por números'
        )

    # TC-48: Rechazar un correo con dominio de una sola letra.
    def test_rechazar_correo_con_dominio_de_una_sola_letra(self):
        """Debe rechazarse un correo con dominio de una sola letra."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.c',
            'Jr. 9 de Octubre 456',
            'Lima',
            '987654321'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertTrue(
            any('correo' in message.lower()
                for message in self.checkout.get_error_messages()),
            'Se aceptó un correo con dominio de una sola letra'
        )

    # TC-49: Rechazar una dirección sin contenido descriptivo.
    def test_rechazar_direccion_sin_contenido_descriptivo(self):
        """Debe rechazarse una dirección compuesta solo por caracteres."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.com',
            'xxxxx',
            'Lima',
            '987654321'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertTrue(
            any('dirección' in message.lower()
                for message in self.checkout.get_error_messages()),
            'Se aceptó una dirección sin contenido descriptivo'
        )

    # TC-50: Rechazar un teléfono con más de quince dígitos.
    def test_rechazar_telefono_con_mas_de_quince_digitos(self):
        """Debe rechazarse un teléfono que excede quince dígitos."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.com',
            'Jr. 9 de Octubre 456',
            'Lima',
            '1234567890123456'
        )
        self.checkout.select_payment_method('yape')
        self.checkout.confirm_payment()

        self.assertTrue(
            any('teléfono' in message.lower()
                for message in self.checkout.get_error_messages()),
            'Se aceptó un teléfono con más de quince dígitos'
        )
