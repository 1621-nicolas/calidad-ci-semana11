"""Casos funcionales TC-32 a TC-41: aceptación de usuario."""

from tests.base_test_case import TiendaDemoTestCase


class TestTC32TC41(TiendaDemoTestCase):
    # TC-32: Agregar un producto desde la perspectiva del usuario.
    def test_32_uat_agregar_producto_desde_perspectiva_usuario(self):
        """Verifica desde la perspectiva del usuario que se agregue un producto."""
        self.catalog.add_product('Laptop Pro 15')
        self.assertEqual(self.catalog.get_cart_count(), 1)

    # TC-33: Ver el producto agregado en el carrito.
    def test_33_uat_ver_carrito_con_producto_agregado(self):
        """Verifica que el usuario pueda ver en el carrito el producto agregado."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.open_cart()
        self.assertIsNotNone(self.cart.get_item_row('Laptop Pro 15'))

    # TC-34: Aplicar un cupón válido desde el flujo UAT.
    def test_34_uat_aplicar_cupon_valido(self):
        """Verifica que el usuario pueda aplicar un cupón válido."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('DESCUENTO10')
        self.assertIn('DESCUENTO10', self.cart.get_coupon_message())

    # TC-35: Completar el checkout con datos normales.
    def test_35_uat_completar_checkout_con_datos_normales(self):
        """Verifica que se complete el checkout con datos normales."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('¡Compra realizada con éxito!', self.checkout.driver.page_source)

    # TC-36: Solicitar los datos faltantes antes de completar la compra.
    def test_36_uat_compra_con_datos_incompletos(self):
        """Verifica que checkout solicite los datos de compra faltantes."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self.checkout.confirm_payment()
        self.assertEqual(len(self.checkout.get_error_messages()), 5)

    # TC-37: Confirmar el estado final del pedido.
    def test_37_uat_confirmar_pedido_final(self):
        """Verifica que el pedido confirmado muestre su estado final."""
        self.catalog.add_product('Disco SSD 1TB')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('Confirmado', self.driver.page_source)

    # TC-38: Comprar más de un artículo.
    def test_38_uat_comprar_con_mas_de_un_articulo(self):
        """Verifica que se pueda comprar más de un artículo."""
        self.catalog.add_product('Disco SSD 1TB')
        self.catalog.add_product('Teclado Mecánico')
        self._go_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('¡Compra realizada con éxito!', self.checkout.driver.page_source)

    # TC-39: Bloquear la compra cuando el carrito está vacío.
    def test_39_uat_intentar_compra_con_carrito_vacio(self):
        """Verifica que la compra con el carrito vacío sea bloqueada."""
        self.driver.execute_script("""
            estado.carrito = [];
            irACheckout();
        """)
        self.assertEqual(self.driver.execute_script("return estado.vista;"), 'catalogo')

    # TC-40: Verificar el total final del pedido.
    def test_40_uat_validar_total_final_correcto(self):
        """Verifica que el total final coincida con el precio del producto."""
        self._add_product('Laptop Pro 15')
        total = self.driver.execute_script("return calcularTotales().total")
        self.assertAlmostEqual(float(total), 2499.00, places=2)

    # TC-41: Ejecutar el flujo completo de compra con cupón.
    def test_41_uat_flujo_completo_de_compra(self):
        """Verifica de principio a fin el flujo de compra con cupón."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.open_cart()
        self.cart.apply_coupon('DESCUENTO10')
        self.cart.proceed_to_checkout()
        self._fill_valid_checkout()
        self.checkout.confirm_payment()
        self.assertIn('¡Compra realizada con éxito!', self.checkout.driver.page_source)