from behave import given, then, when

from features.steps.common_steps import prepare_browser


# TC-14, TC-15 y TC-18: Aplicar el cupón indicado en el escenario.
@when('aplico el cupón "{cupon}"')
def step_impl(context, cupon):
    """Aplica el código de cupón indicado en el escenario."""
    context.cart.apply_coupon(cupon)


# TC-14: Verificar que se muestre el mensaje del cupón aplicado.
@then('veo el mensaje de cupón aplicado')
def step_impl(context):
    """Comprueba que se muestre un mensaje relacionado con el cupón."""
    assert 'Cupón' in context.cart.get_coupon_message()


# TC-17: Preparar el carrito con un cupón válido ya aplicado.
@given('tengo un producto en el carrito con cupón aplicado')
def step_impl(context):
    """Prepara el carrito con un producto y un cupón válido aplicado."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()
    context.cart.apply_coupon('DESCUENTO10')


# TC-16: Intentar aplicar un cupón vacío.
@when('aplico un cupón vacío')
def step_impl(context):
    """Intenta aplicar un cupón sin código."""
    context.cart.apply_coupon('')


# TC-15: Verificar el mensaje de cupón no válido.
@then('veo un mensaje de cupón no válido')
def step_impl(context):
    """Comprueba que el sistema indique que el cupón no es válido."""
    assert 'Cupón no válido' in context.cart.get_coupon_message()


# TC-16: Verificar el mensaje que solicita ingresar un código.
@then('se muestra un mensaje de validación')
def step_impl(context):
    """Comprueba que el sistema solicite ingresar un código de cupón."""
    assert 'Ingresa un código de cupón' in context.cart.get_coupon_message()


# TC-17: Intentar aplicar nuevamente el cupón existente.
@when('intento aplicar el mismo cupón otra vez')
def step_impl(context):
    """Intenta aplicar nuevamente el cupón ya utilizado."""
    context.cart.apply_coupon('DESCUENTO10')


# TC-17: Verificar que el cupón no se aplique dos veces.
@then('se muestra un aviso de cupón ya aplicado')
def step_impl(context):
    """Comprueba el aviso de cupón repetido y que el descuento no se duplique."""
    assert 'ya está aplicado' in context.cart.get_coupon_message().lower()
    total = context.driver.execute_script("return calcularTotales().total")
    assert abs(float(total) - 2249.10) < 0.01


# TC-18: Verificar el total después de aplicar el descuento.
@then('el total final refleja el descuento')
def step_impl(context):
    """Comprueba que el total corresponda al precio con descuento."""
    total = context.driver.execute_script("return calcularTotales().total")
    assert abs(float(total) - 2249.10) < 0.01


# TC-19: Mantener el carrito sin cupón aplicado.
@when('no aplico ningún cupón')
def step_impl(context):
    """Mantiene el carrito sin aplicar ningún cupón."""
    pass


# TC-19: Verificar el total base cuando no hay descuento.
@then('el total final es el precio base')
def step_impl(context):
    """Comprueba que el total sea el precio base cuando no hay cupón."""
    total = context.driver.execute_script("return calcularTotales().total")
    assert abs(float(total) - 2499.00) < 0.01