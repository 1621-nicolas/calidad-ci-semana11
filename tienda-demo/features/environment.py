def after_scenario(context, scenario):
    """Cierra el navegador y libera los recursos al terminar cada escenario."""
    if hasattr(context, 'driver') and context.driver:
        context.driver.quit()
        context.driver = None
