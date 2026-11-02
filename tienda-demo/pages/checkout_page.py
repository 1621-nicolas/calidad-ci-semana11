"""
CheckoutPage: maneja la vista de pago y la validación del formulario.

Este objeto ofrece métodos para completar los datos de envío, seleccionar el
método de pago y confirmar la orden.
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage

class CheckoutPage(BasePage):
    # Selectores de elementos de la vista de checkout.
    NAME_INPUT = (By.ID, "campo-nombre")
    EMAIL_INPUT = (By.ID, "campo-email")
    ADDRESS_INPUT = (By.ID, "campo-direccion")
    CITY_INPUT = (By.ID, "campo-ciudad")
    PHONE_INPUT = (By.ID, "campo-telefono")
    PAYMENT_OPTIONS = (By.CSS_SELECTOR, ".opcion-pago input[type='radio']")
    PAY_BUTTON = (By.ID, "btn-confirmar-pago")
    ERROR_MESSAGES = (By.CSS_SELECTOR, ".error-campo.visible")

    # Completa los datos de envío requeridos en el formulario.
    def fill_shipping_info(self, name, email, address, city, phone):
        self.fill(self.NAME_INPUT, name)
        self.fill(self.EMAIL_INPUT, email)
        self.fill(self.ADDRESS_INPUT, address)
        self.fill(self.CITY_INPUT, city)
        self.fill(self.PHONE_INPUT, phone)

    # Selecciona un método de pago por su valor.
    def select_payment_method(self, method_value):
        radios = self.driver.find_elements(*self.PAYMENT_OPTIONS)
        for radio in radios:
            if radio.get_attribute("value") == method_value:
                radio.click()
                return
        raise ValueError(f"Método de pago '{method_value}' no encontrado")

    # Confirma el pago en el checkout.
    def confirm_payment(self):
        self.click(self.PAY_BUTTON)

    # Devuelve los mensajes de error visibles tras validación.
    def get_error_messages(self):
        return [el.text for el in self.driver.find_elements(*self.ERROR_MESSAGES)]
