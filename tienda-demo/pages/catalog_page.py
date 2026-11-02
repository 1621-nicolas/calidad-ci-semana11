"""
CatalogPage: encapsula las acciones disponibles en la vista del catálogo.

Incluye operaciones como agregar productos al carrito, realizar búsquedas,
filtrar por categoría y leer el contador del carrito.
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage

class CatalogPage(BasePage):
    # Selectores de elementos de la vista de catálogo.
    CART_COUNT = (By.ID, "contador-carrito")
    SEARCH_INPUT = (By.ID, "buscador")
    SEARCH_BUTTON = (By.ID, "btn-buscar")
    CATEGORY_FILTER = (By.ID, "filtro-categoria")
    CART_BUTTON = (By.ID, "btn-abrir-carrito")

    # Agrega un producto al carrito usando el nombre del producto.
    def add_product(self, name):
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".tarjeta-producto")
        for card in cards:
            if name in card.text:
                btn = card.find_element(By.CSS_SELECTOR, ".btn-agregar")
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", btn)
                return True
        raise ValueError(f"Producto '{name}' no encontrado en el catálogo")

    # Abre la vista del carrito desde el catálogo.
    def open_cart(self):
        self.click(self.CART_BUTTON)

    # Realiza una búsqueda con el texto provisto.
    def search(self, query):
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)

    # Cambia el filtro de categoría del catálogo.
    def filter_category(self, category):
        select = self.find(self.CATEGORY_FILTER)
        select.send_keys(category)

    # Retorna el número actual de artículos en el contador del carrito.
    def get_cart_count(self):
        return int(self.find(self.CART_COUNT).text)
