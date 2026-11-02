"""Preparación compartida de Behave/UAT para TiendaDemo.

En Docker, el navegador Selenium es REMOTO: no puede abrir archivos file://
que existan únicamente en el contenedor selenium-tests. Se usa la misma URL
HTTP que la suite unittest/Selenium para evitar errores como
`javascript error: estado is not defined` en la página de error del navegador.
"""

import os
from pathlib import Path

from behave import given, when
from selenium.webdriver.support.ui import WebDriverWait

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage
from utils.driver_factory import DriverFactory


def resolve_base_url():
    """Usa HTTP en Docker/Remote WebDriver y file:// solo para Chrome local."""
    configured = os.getenv("TIENDA_BASE_URL", "").strip()
    if configured:
        return configured
    if os.getenv("SELENIUM_REMOTE_URL"):
        raise RuntimeError(
            "Behave usa Selenium remoto, pero falta TIENDA_BASE_URL. "
            "Configura TIENDA_BASE_URL=http://tienda-demo:8008/ "
            "(en Docker) o la URL HTTP accesible por el navegador remoto."
        )
    return (Path(__file__).resolve().parents[2] / "app" / "tienda_demo.html").as_uri()


BASE_URL = resolve_base_url()


def prepare_browser(context):
    """Abre TiendaDemo, espera la carga real y reinicia el estado de cada caso."""
    if not hasattr(context, "driver") or context.driver is None:
        context.driver = DriverFactory.create_chrome()
    context.driver.get(BASE_URL)

    # El documento puede cargar sin carrito.js (p. ej. URL file:// en Chrome
    # remoto). Verificar la app antes de ejecutar código de la tienda proporciona
    # un error explícito y facilita depurar fallos de Docker/Red.
    WebDriverWait(context.driver, 12).until(
        lambda driver: driver.execute_script(
            "return document.readyState === 'complete' && "
            "typeof estado !== 'undefined' && "
            "typeof renderCatalogo === 'function' && "
            "!!document.getElementById('grid-productos');"
        ),
        message=(
            "TiendaDemo no cargó correctamente en Selenium. "
            f"URL solicitada: {BASE_URL}. "
            "Verifica el servicio tienda-demo, su conectividad y carrito.js."
        ),
    )

    context.driver.execute_script("""
        estado.carrito = [];
        estado.cuponAplicado = null;
        renderCatalogo();
        mostrarVista('catalogo');
    """)
    context.catalog = CatalogPage(context.driver)
    context.cart = CartPage(context.driver)
    context.checkout = CheckoutPage(context.driver)


@when('abro el carrito')
def step_impl(context):
    """Abre la vista del carrito."""
    context.catalog.open_cart()


@given('tengo un producto en el carrito')
def step_impl(context):
    """Prepara la tienda con un producto agregado y el carrito abierto."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()


@given('tengo varios productos en el carrito')
def step_impl(context):
    """Prepara la tienda con varios productos y el carrito abierto."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.add_product('Teclado Mecánico')
    context.catalog.open_cart()


@given('el carrito está vacío')
def step_impl(context):
    """Prepara la tienda con el carrito vacío."""
    prepare_browser(context)
    context.driver.execute_script('estado.carrito = []; renderCarrito();')
