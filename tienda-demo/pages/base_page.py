"""
BasePage: clase base del Page Object Model.

Este módulo contiene los métodos comunes que se utilizan en todas
las páginas de la aplicación TiendaDemo.

El patrón Page Object Model separa la lógica de interacción con la UI
de la lógica de los tests, lo cual mejora la mantenibilidad.
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    # Inicializa el Page Object con el driver de Selenium y una espera explícita.
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # Abre una URL en el navegador conectado al driver.
    def open(self, url):
        self.driver.get(url)

    # Busca un elemento usando un localizador y espera a que esté presente.
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    # Hace clic en un elemento encontrado por el localizador.
    def click(self, locator):
        element = self.find(locator)
        element.click()
        return element

    # Llena un campo de texto: limpia primero y escribe el valor.
    def fill(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        return element
