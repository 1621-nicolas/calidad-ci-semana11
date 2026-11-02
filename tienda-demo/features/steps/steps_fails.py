from behave import then, when


# TC-42: Rechazar un teléfono que contiene letras.
@when('ingreso un teléfono con letras y confirmo')
def step_impl(context):
    """Confirma el checkout con un teléfono que contiene letras."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        'Lima',
        '987654321abc'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-42: Verificar el rechazo del teléfono con letras.
@then('veo un mensaje de teléfono inválido')
def step_impl(context):
    """Comprueba que el teléfono con letras sea rechazado."""
    assert any(
        'teléfono' in message.lower()
        for message in context.checkout.get_error_messages()
    ), 'Se aceptó un teléfono que contiene letras'


# TC-43: Aceptar el formato telefónico sugerido en el formulario.
@when('ingreso un teléfono con espacios y confirmo')
def step_impl(context):
    """Confirma el checkout con el formato telefónico sugerido en pantalla."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        'Lima',
        '987 654 321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-44: Probar un cupón inválido después de aplicar uno válido.
@when('aplico un cupón válido y luego uno inválido')
def step_impl(context):
    """Prueba un código inválido después de haber aplicado un cupón válido."""
    context.cart.apply_coupon('DESCUENTO10')
    context.cart.apply_coupon('INVALIDO')


# TC-44: Verificar que se conserve el descuento válido aplicado.
@then('se conserva el descuento del cupón válido')
def step_impl(context):
    """Comprueba que un cupón inválido no quite un descuento ya aplicado."""
    total = context.driver.execute_script("return calcularTotales().total")
    assert abs(float(total) - 2249.10) < 0.01, (
        'El intento con un cupón inválido eliminó el descuento existente'
    )


# TC-45: Rechazar una ciudad compuesta solo por números.
@when('ingreso una ciudad compuesta solo por números y confirmo')
def step_impl(context):
    """Confirma el checkout con un nombre de ciudad numérico."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        '12345',
        '987654321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-45: Verificar el rechazo de la ciudad numérica.
@then('veo un mensaje de ciudad inválida')
def step_impl(context):
    """Comprueba que se rechace una ciudad sin letras."""
    assert any(
        'ciudad' in message.lower()
        for message in context.checkout.get_error_messages()
    ), 'Se aceptó una ciudad compuesta solo por números'


# TC-46: Completar la compra de una unidad para comprobar el inventario.
@when('completo la compra de una unidad de Laptop Pro 15')
def step_impl(context):
    """Confirma una compra de una unidad del producto indicado."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        'Lima',
        '987654321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-46: Verificar que el stock disminuya después de la compra.
@then('el stock de Laptop Pro 15 disminuye en una unidad')
def step_impl(context):
    """Comprueba que la compra actualice el inventario del producto."""
    stock = context.driver.execute_script(
        "return PRODUCTOS.find(producto => producto.id === 1).stock"
    )
    assert stock == 7, f'Se esperaba stock 7 después de la compra, se obtuvo {stock}'


# TC-47: Rechazar un nombre compuesto solo por números.
@when('ingreso un nombre compuesto solo por números y confirmo')
def step_impl(context):
    """Confirma el checkout con un nombre sin caracteres alfabéticos."""
    context.checkout.fill_shipping_info(
        '123 456',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        'Lima',
        '987654321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-47: Verificar el rechazo del nombre compuesto solo por números.
@then('veo un mensaje de nombre inválido')
def step_impl(context):
    """Comprueba que el nombre sin letras sea rechazado."""
    assert any(
        'nombre' in message.lower()
        for message in context.checkout.get_error_messages()
    ), 'Se aceptó un nombre compuesto solo por números'


# TC-48: Rechazar un correo con dominio de una sola letra.
@when('ingreso un correo con dominio de una sola letra y confirmo')
def step_impl(context):
    """Confirma el checkout con un dominio de correo demasiado corto."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.c',
        'Jr. 9 de Octubre 456',
        'Lima',
        '987654321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-48: Verificar el rechazo del dominio de correo demasiado corto.
@then('el correo con dominio corto se rechaza')
def step_impl(context):
    """Comprueba que se rechace el dominio de correo demasiado corto."""
    assert any(
        'correo' in message.lower()
        for message in context.checkout.get_error_messages()
    ), 'Se aceptó un correo con dominio de una sola letra'


# TC-49: Rechazar una dirección sin contenido descriptivo.
@when('ingreso una dirección sin contenido descriptivo y confirmo')
def step_impl(context):
    """Confirma el checkout con una dirección que solo contiene caracteres."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'xxxxx',
        'Lima',
        '987654321'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-49: Verificar el rechazo de la dirección sin contenido útil.
@then('veo un mensaje de dirección inválida')
def step_impl(context):
    """Comprueba que se rechace una dirección sin información útil."""
    assert any(
        'dirección' in message.lower()
        for message in context.checkout.get_error_messages()
    ), 'Se aceptó una dirección sin contenido descriptivo'


# TC-50: Rechazar un teléfono con más de quince dígitos.
@when('ingreso un teléfono con más de quince dígitos y confirmo')
def step_impl(context):
    """Confirma el checkout con un número por encima del máximo esperado."""
    context.checkout.fill_shipping_info(
        'María López',
        'maria@correo.com',
        'Jr. 9 de Octubre 456',
        'Lima',
        '1234567890123456'
    )
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-50: Verificar el rechazo del teléfono de longitud excesiva.
@then('el teléfono excesivo se rechaza')
def step_impl(context):
    """Comprueba que se rechace un teléfono de longitud excesiva."""
    assert any(
        'teléfono' in message.lower()
        for message in context.checkout.get_error_messages()
    ), 'Se aceptó un teléfono con más de quince dígitos'
