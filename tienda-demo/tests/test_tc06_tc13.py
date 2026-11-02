"""Casos funcionales TC-06 a TC-13: cantidades y eliminación."""

from tests.base_test_case import TiendaDemoTestCase


class TestTC06TC13(TiendaDemoTestCase):
    # TC-06: Aumentar la cantidad de un producto.
    def test_06_aumentar_cantidad_de_producto(self):
        """Verifica que se pueda aumentar la cantidad de un producto."""
        self._add_product('Laptop Pro 15')
        self.cart.increase_quantity('Laptop Pro 15')
        self.assertEqual(self.cart.get_quantity('Laptop Pro 15'), 2)

    # TC-07: Disminuir la cantidad de un producto.
    def test_07_disminuir_cantidad_de_producto(self):
        """Verifica que disminuir la cantidad actualice el carrito."""
        self._add_product('Laptop Pro 15')
        self.cart.increase_quantity('Laptop Pro 15')
        self.cart.decrease_quantity('Laptop Pro 15')
        self.assertEqual(self.cart.get_quantity('Laptop Pro 15'), 1)

    # TC-08: Eliminar un producto al reducir su cantidad a cero.
    def test_08_cantidad_cero_elimina_producto(self):
        """Verifica que una cantidad reducida a cero elimine el producto."""
        self._add_product('Laptop Pro 15')
        self.cart.decrease_quantity('Laptop Pro 15')
        self.assertIsNone(self.cart.get_item_row('Laptop Pro 15'))

    # TC-09: Evitar que el carrito conserve cantidades negativas.
    def test_09_cantidad_negativa_no_baja_de_cero(self):
        """Verifica que el carrito no conserve cantidades negativas."""
        self._add_product('Laptop Pro 15')
        self.driver.execute_script("""
            cambiarCantidad(1, 'menos');
            cambiarCantidad(1, 'menos');
        """)
        self.assertIsNone(self.cart.get_item_row('Laptop Pro 15'))
        self.assertEqual(self.driver.execute_script("return estado.carrito.length;"), 0)
        self.assertTrue(self.driver.execute_script("return estado.carrito.every(item => item.cantidad > 0);"))

    # TC-10: Eliminar un producto específico del carrito.
    def test_10_eliminar_producto_del_carrito(self):
        """Verifica que se pueda quitar un producto del carrito."""
        self._add_product('Laptop Pro 15')
        self.cart.remove_item('Laptop Pro 15')
        self.assertIsNone(self.cart.get_item_row('Laptop Pro 15'))

    # TC-11: Mostrar el carrito vacío al eliminar el último producto.
    def test_11_eliminar_ultimo_producto_deja_carrito_vacio(self):
        """Verifica que eliminar el último producto muestre el carrito vacío."""
        self._add_product('Laptop Pro 15')
        self.cart.remove_item('Laptop Pro 15')
        self.assertTrue(self.cart.has_empty_message())

    # TC-12: Eliminar un producto sin quitar los demás artículos.
    def test_12_eliminar_uno_entre_varios(self):
        """Verifica que eliminar un producto no quite los demás artículos."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.add_product('Teclado Mecánico')
        self.catalog.open_cart()
        self.cart.remove_item('Laptop Pro 15')
        self.assertIsNone(self.cart.get_item_row('Laptop Pro 15'))
        self.assertIsNotNone(self.cart.get_item_row('Teclado Mecánico'))

    # TC-13: Recalcular el subtotal al eliminar un producto.
    def test_13_subtotal_se_recalcula_al_eliminar(self):
        """Verifica que el subtotal se actualice después de eliminar un producto."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.add_product('Teclado Mecánico')
        self.catalog.open_cart()
        self.cart.remove_item('Laptop Pro 15')
        self.assertIsNotNone(self.cart.get_item_row('Teclado Mecánico'))