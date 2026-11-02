"""Casos funcionales TC-01 a TC-05: catálogo y carrito."""

from tests.base_test_case import TiendaDemoTestCase


class TestTC01TC05(TiendaDemoTestCase):
    # TC-01: Agregar un producto al carrito.
    def test_01_agregar_producto_al_carrito(self):
        """Verifica que agregar un producto incremente el contador del carrito."""
        self.catalog.add_product('Laptop Pro 15')
        self.assertEqual(self.catalog.get_cart_count(), 1)

    # TC-02: Agregar varios productos diferentes.
    def test_02_agregar_varios_productos_diferentes(self):
        """Verifica que se puedan agregar productos distintos al carrito."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.add_product('Teclado Mecánico')
        self.assertEqual(self.catalog.get_cart_count(), 2)

    # TC-03: Agregar dos veces el mismo producto.
    def test_03_agregar_el_mismo_producto_dos_veces(self):
        """Verifica que el mismo producto pueda agregarse dos veces."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.add_product('Laptop Pro 15')
        self.assertEqual(self.catalog.get_cart_count(), 2)

    # TC-04: Verificar que el contador refleje la cantidad de artículos.
    def test_04_contador_aumenta_correctamente(self):
        """Verifica que el contador refleje la cantidad total de artículos."""
        self.catalog.add_product('Laptop Pro 15')
        self.catalog.add_product('Mouse Inalámbrico')
        self.assertEqual(self.catalog.get_cart_count(), 2)

    # TC-05: Verificar que el producto aparezca en la vista del carrito.
    def test_05_producto_visible_en_carrito(self):
        """Verifica que el producto agregado aparezca en la vista del carrito."""
        self.catalog.add_product('Teclado Mecánico')
        self.catalog.open_cart()
        self.assertIsNotNone(self.cart.get_item_row('Teclado Mecánico'))