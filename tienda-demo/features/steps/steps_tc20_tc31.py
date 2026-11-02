from behave import given, then, when

from features.steps.common_steps import prepare_browser


# TC-20: Intentar acceder al checkout desde el carrito vacío.
@when('intento acceder al checkout')
def step_impl(context):
    """Intenta abrir el checkout desde el estado actual de la tienda."""
    context.driver.execute_script("irACheckout();")


# TC-20: Verificar que no se permita continuar sin productos.
@then('se bloquea la compra o se muestra un mensaje de error')
def step_impl(context):
    """Comprueba que el checkout no se abra sin artículos en el carrito."""
    assert context.driver.execute_script("return estado.vista;") in ('catalogo', 'carrito')


# TC-30: Preparar el checkout desde el carrito con un producto.
@given('estoy en checkout')
def step_impl(context):
    """Prepara el navegador en checkout con un producto en el carrito."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()
    context.cart.proceed_to_checkout()


# TC-21 a TC-29 y TC-31: Preparar el checkout con un artículo.
@given('estoy en la página de checkout con un artículo en el carrito')
def step_impl(context):
    """Prepara checkout con un artículo listo para comprar."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()
    context.cart.proceed_to_checkout()


# TC-21: Confirmar el pago sin completar los campos.
@when('intento confirmar el pago sin completar los datos')
def step_impl(context):
    """Intenta confirmar el pago sin completar los datos de envío."""
    context.checkout.confirm_payment()


# TC-21: Verificar los errores de todos los campos obligatorios.
@then('veo mensajes de error para los campos obligatorios')
def step_impl(context):
    """Comprueba que se muestren errores para los campos obligatorios."""
    assert len(context.checkout.get_error_messages()) == 5


# TC-29 y TC-31: Completar datos válidos y confirmar el pago.
@when('completo todos los datos y confirmo el pago')
def step_impl(context):
    """Completa datos válidos, selecciona el pago y confirma la compra."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        'Lima',
        '987654321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-29 y TC-31: Verificar que se muestre la confirmación de compra.
@then('veo la pantalla de confirmación')
def step_impl(context):
    """Comprueba que se muestre la confirmación de compra."""
    assert '¡Compra realizada con éxito!' in context.driver.page_source


# TC-22: Confirmar el pago dejando vacío el nombre.
@when('dejo el nombre vacío y confirmo')
def step_impl(context):
    """Confirma el pago dejando vacío el campo de nombre."""
    context.checkout.fill_shipping_info('', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-22: Verificar el error del nombre obligatorio.
@then('veo el error del nombre obligatorio')
def step_impl(context):
    """Comprueba que se indique que el nombre es obligatorio."""
    assert any('nombre' in message.lower() for message in context.checkout.get_error_messages())


# TC-23: Confirmar el pago dejando vacío el apellido.
@when('dejo el apellido vacío y confirmo')
def step_impl(context):
    """Confirma el pago dejando vacío el campo de apellido."""
    context.checkout.fill_shipping_info('María', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-23: Verificar el error del apellido obligatorio.
@then('veo el error del apellido obligatorio')
def step_impl(context):
    """Comprueba que se indique que el apellido es obligatorio."""
    assert any('apellido' in message.lower() for message in context.checkout.get_error_messages())


# TC-24: Confirmar el pago dejando vacío el correo.
@when('dejo el correo vacío y confirmo')
def step_impl(context):
    """Confirma el pago dejando vacío el campo de correo."""
    context.checkout.fill_shipping_info('María López', '', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-24: Verificar el error del correo obligatorio.
@then('veo el error del correo obligatorio')
def step_impl(context):
    """Comprueba que se indique que el correo es obligatorio."""
    assert any('correo' in message.lower() for message in context.checkout.get_error_messages())


# TC-25: Enviar el checkout con un correo mal formado.
@when('ingreso un correo sin formato válido')
def step_impl(context):
    """Envía el checkout con una dirección de correo mal formada."""
    context.checkout.fill_shipping_info('María López', 'correo-no-valido', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-25: Verificar el error de formato del correo.
@then('veo un mensaje de correo inválido')
def step_impl(context):
    """Comprueba que se indique el error de validación del correo."""
    assert any('correo' in message.lower() for message in context.checkout.get_error_messages())


# TC-27: Confirmar el pago dejando vacía la dirección.
@when('dejo la dirección vacía y confirmo')
def step_impl(context):
    """Confirma el pago dejando vacía la dirección."""
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', '', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-27: Verificar el error de dirección obligatoria.
@then('veo el error de la dirección obligatoria')
def step_impl(context):
    """Comprueba que se indique que la dirección es obligatoria."""
    assert any('dirección' in message.lower() for message in context.checkout.get_error_messages())


# TC-28: Confirmar el pago dejando vacía la ciudad.
@when('dejo la ciudad vacía y confirmo')
def step_impl(context):
    """Confirma el pago dejando vacía la ciudad."""
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', '', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-28: Verificar el error de ciudad obligatoria.
@then('veo el error de la ciudad obligatoria')
def step_impl(context):
    """Comprueba que se indique que la ciudad es obligatoria."""
    assert any('ciudad' in message.lower() for message in context.checkout.get_error_messages())


# TC-26: Confirmar el pago dejando vacío el teléfono.
@when('dejo el teléfono vacío y confirmo')
def step_impl(context):
    """Confirma el pago dejando vacío el teléfono."""
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-26: Verificar el error de teléfono obligatorio.
@then('veo el error del teléfono obligatorio')
def step_impl(context):
    """Comprueba que se indique que el teléfono es obligatorio."""
    assert any('teléfono' in message.lower() for message in context.checkout.get_error_messages())


# TC-30: Completar datos válidos y confirmar la compra con varios productos.
@when('completo los datos válidos y confirmo')
def step_impl(context):
    """Completa los datos de compra válidos y confirma el pago."""
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-30: Verificar que se procese la compra de varios productos.
@then('la compra se procesa correctamente')
def step_impl(context):
    """Comprueba que el sistema confirme el procesamiento de la compra."""
    assert '¡Compra realizada con éxito!' in context.driver.page_source