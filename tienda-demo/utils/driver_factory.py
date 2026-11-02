"""
DriverFactory: crea y configura instancias del navegador para los tests.

Centraliza la configuración del driver Chrome para que los archivos de test
mantengan un único punto de creación del navegador.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

class DriverFactory:
    # Crea un driver Chrome configurado para pruebas.
    #
    # El modo headless permite ejecutar los tests sin abrir una ventana
    # visible del navegador, lo cual es útil para entornos de CI o ejecución rápida.
    @staticmethod
    def create_chrome(headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1440,900')
        remote = os.getenv("SELENIUM_REMOTE_URL")
        driver = webdriver.Remote(command_executor=remote, options=options) if remote else webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver
