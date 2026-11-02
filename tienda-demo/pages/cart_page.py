"""
CartPage: encapsula la interacción con la vista del carrito de compras.

Permite leer los elementos del carrito, modificar cantidades, aplicar cupones,
eliminar productos y avanzar al checkout.
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage

class CartPage(BasePage):
    # Selectores de elementos de la vista del carrito.
    EMPTY_MESSAGE = (By.ID, "carrito-vacio")
    ITEM_ROWS = (By.CSS_SELECTOR, ".item-carrito")
    COUPON_INPUT = (By.ID, "input-cupon")
    COUPON_BUTTON = (By.ID, "btn-aplicar-cupon")
    COUPON_MESSAGE = (By.ID, "msg-cupon")
    CHECKOUT_BUTTON = (By.ID, "btn-ir-checkout")
    EMPTY_CART_BUTTON = (By.ID, "btn-vaciar-carrito")

    # Devuelve la fila del carrito que contiene el producto indicado.
    def get_item_row(self, name):
        for row in self.driver.find_elements(*self.ITEM_ROWS):
            if name in row.text:
                return row
        return None

    # Devuelve la cantidad actual de un producto en el carrito.
    def get_quantity(self, name):
        row = self.get_item_row(name)
        if not row:
            return 0
        return int(row.find_element(By.CSS_SELECTOR, ".cantidad-num").text)

    # Aumenta la cantidad de un producto existente en el carrito.
    def increase_quantity(self, name):
        row = self.get_item_row(name)
        if row:
            row.find_element(By.CSS_SELECTOR, ".btn-cantidad[data-accion='mas']").click()

    # Disminuye la cantidad de un producto existente en el carrito.
    def decrease_quantity(self, name):
        row = self.get_item_row(name)
        if row:
            row.find_element(By.CSS_SELECTOR, ".btn-cantidad[data-accion='menos']").click()

    # Elimina un producto del carrito.
    def remove_item(self, name):
        row = self.get_item_row(name)
        if row:
            row.find_element(By.CSS_SELECTOR, ".btn-eliminar").click()

    # Aplica un código de cupón en el carrito.
    def apply_coupon(self, code):
        self.fill(self.COUPON_INPUT, code)
        self.click(self.COUPON_BUTTON)

    # Devuelve el mensaje que aparece al aplicar el cupón.
    def get_coupon_message(self):
        return self.find(self.COUPON_MESSAGE).text

    # Avanza desde el carrito hacia el checkout.
    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BUTTON)

    # Vacía el carrito por completo.
    def empty_cart(self):
        self.click(self.EMPTY_CART_BUTTON)

    # Verifica si se muestra el mensaje de carrito vacío.
    def has_empty_message(self):
        return len(self.driver.find_elements(*self.EMPTY_MESSAGE)) > 0
