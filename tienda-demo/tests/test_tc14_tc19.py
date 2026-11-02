"""Casos funcionales TC-14 a TC-19: cupones y totales."""

from tests.base_test_case import TiendaDemoTestCase


class TestTC14TC19(TiendaDemoTestCase):
    # TC-14: Aplicar un cupón válido.
    def test_14_aplicar_cupon_valido(self):
        """Verifica que se acepte un cupón válido."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('DESCUENTO10')
        self.assertIn('DESCUENTO10', self.cart.get_coupon_message())

    # TC-15: Rechazar un cupón inválido.
    def test_15_aplicar_cupon_invalido(self):
        """Verifica que se rechace un cupón inexistente."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('INVALIDO')
        self.assertIn('Cupón no válido', self.cart.get_coupon_message())

    # TC-16: Solicitar un código si el cupón está vacío.
    def test_16_aplicar_cupon_vacio(self):
        """Verifica que se solicite un código cuando el cupón está vacío."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('')
        self.assertIn('Ingresa un código de cupón', self.cart.get_coupon_message())

    # TC-17: Evitar que un cupón repetido duplique el descuento.
    def test_17_aplicar_cupon_repetido(self):
        """Verifica que un cupón ya aplicado no vuelva a descontarse."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('DESCUENTO10')
        self.cart.apply_coupon('DESCUENTO10')
        self.assertIn('ya está aplicado', self.cart.get_coupon_message().lower())
        total = self.driver.execute_script("return calcularTotales().total")
        self.assertAlmostEqual(float(total), 2249.10, places=2)

    # TC-18: Verificar el total con descuento.
    def test_18_total_con_descuento(self):
        """Verifica que el total incluya el descuento del cupón válido."""
        self._add_product('Laptop Pro 15')
        self.cart.apply_coupon('DESCUENTO10')
        total = self.driver.execute_script("return calcularTotales().total")
        self.assertAlmostEqual(float(total), 2249.10, places=2)

    # TC-19: Verificar el total sin descuento.
    def test_19_total_sin_descuento(self):
        """Verifica que el total conserve el precio base sin cupón."""
        self._add_product('Laptop Pro 15')
        total = self.driver.execute_script("return calcularTotales().total")
        self.assertAlmostEqual(float(total), 2499.00, places=2)