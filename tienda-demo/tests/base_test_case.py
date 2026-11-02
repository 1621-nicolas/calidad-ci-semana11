"""Configuración compartida de Selenium para las pruebas funcionales."""

import os
import unittest

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage
from utils.driver_factory import DriverFactory

BASE_URL = os.environ.get("TIENDA_BASE_URL") or ("file:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'tienda_demo.html')).replace('\\', '/'))


class TiendaDemoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa el navegador y los objetos de página compartidos por las pruebas."""
        cls.driver = DriverFactory.create_chrome()
        cls.catalog = CatalogPage(cls.driver)
        cls.cart = CartPage(cls.driver)
        cls.checkout = CheckoutPage(cls.driver)

    @classmethod
    def tearDownClass(cls):
        """Cierra el navegador al finalizar todas las pruebas de la clase."""
        cls.driver.quit()

    def setUp(self):
        """Carga la tienda y restablece el carrito antes de cada prueba."""
        self.driver.get(BASE_URL)
        self.driver.execute_script("""
            estado.carrito = [];
            estado.cuponAplicado = null;
            renderCatalogo();
            mostrarVista('catalogo');
        """)

    def _add_product(self, name):
        """Agrega un producto al carrito y abre la vista del carrito."""
        self.catalog.add_product(name)
        self.catalog.open_cart()

    def _go_to_checkout(self):
        """Abre el carrito y continúa hasta la pantalla de checkout."""
        self.catalog.open_cart()
        self.cart.proceed_to_checkout()

    def _fill_valid_checkout(self):
        """Completa los datos de envío y selecciona un método de pago válido."""
        self.checkout.fill_shipping_info(
            'María López',
            'maria@correo.com',
            'Jr. 9 de Octubre 456',
            'Lima',
            '987654321'
        )
        self.checkout.select_payment_method('yape')