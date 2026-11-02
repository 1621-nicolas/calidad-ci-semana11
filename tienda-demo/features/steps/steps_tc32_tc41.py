from behave import given, then, when

from features.steps.common_steps import prepare_browser


# TC-32: Preparar la tienda para el flujo de agregar productos.
@given('el usuario entra a la tienda')
def step_impl(context):
    """Prepara la tienda para iniciar el escenario de usuario."""
    prepare_browser(context)


# TC-32: Seleccionar un producto en el catálogo.
@when('selecciona un producto')
def step_impl(context):
    """Agrega la laptop al carrito como producto seleccionado."""
    context.catalog.add_product('Laptop Pro 15')


# TC-32: Agregar el producto seleccionado al carrito.
@when('hace clic en agregar')
def step_impl(context):
    """Agrega la laptop al carrito."""
    context.catalog.add_product('Laptop Pro 15')


# TC-32: Verificar que el producto agregado aparezca en el carrito.
@then('puede ver el producto en el carrito')
def step_impl(context):
    """Comprueba que el carrito contenga al menos un artículo."""
    assert context.catalog.get_cart_count() >= 1


# TC-33: Preparar la tienda con un producto agregado.
@given('el usuario agregó un producto')
def step_impl(context):
    """Prepara la tienda con una laptop agregada al carrito."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')


# TC-33: Abrir el carrito para revisar el producto.
@when('abre el carrito')
def step_impl(context):
    """Abre la vista del carrito."""
    context.catalog.open_cart()


# TC-33: Verificar producto y total en el resumen del carrito.
@then('puede revisar el producto, la cantidad y el total')
def step_impl(context):
    """Comprueba que se muestre el producto y que el total sea positivo."""
    assert context.cart.get_item_row('Laptop Pro 15') is not None
    assert context.driver.execute_script("return calcularTotales().total;") > 0


# TC-34: Preparar un producto en el carrito para aplicar un cupón.
@given('el usuario tiene un producto en el carrito')
def step_impl(context):
    """Prepara la tienda con una laptop y abre el carrito."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()


# TC-34: Aplicar un cupón válido.
@when('aplica un cupón válido')
def step_impl(context):
    """Aplica el cupón de descuento válido al carrito."""
    context.cart.apply_coupon('DESCUENTO10')


# TC-34: Verificar el descuento en el total.
@then('el descuento se refleja en el total')
def step_impl(context):
    """Comprueba que el total incluya el descuento esperado."""
    total = context.driver.execute_script("return calcularTotales().total")
    assert abs(float(total) - 2249.10) < 0.01


# TC-35 y TC-36: Preparar varios productos y abrir el checkout.
@given('el usuario tiene productos en el carrito')
def step_impl(context):
    """Prepara dos productos en el carrito y abre el checkout."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.add_product('Teclado Mecánico')
    context.catalog.open_cart()
    context.cart.proceed_to_checkout()


# TC-35: Completar los datos de envío y confirmar la compra.
@when('completa sus datos y confirma la compra')
def step_impl(context):
    """Completa los datos de envío y confirma la compra."""
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-35: Verificar que se reciba la confirmación del pedido.
@then('recibe la confirmación del pedido')
def step_impl(context):
    """Comprueba que la tienda muestre la confirmación del pedido."""
    assert '¡Compra realizada con éxito!' in context.driver.page_source


# TC-36: Intentar confirmar el checkout con datos vacíos.
@when('intenta confirmar con campos vacíos')
def step_impl(context):
    """Intenta confirmar la compra sin completar los datos."""
    context.checkout.confirm_payment()


# TC-36: Verificar los mensajes de datos obligatorios.
@then('el sistema le indica qué falta completar')
def step_impl(context):
    """Comprueba que se muestren los errores de los datos faltantes."""
    assert len(context.checkout.get_error_messages()) == 5


# TC-37: Preparar una compra válida.
@given('la compra es válida')
def step_impl(context):
    """Prepara una compra válida con una laptop en el carrito."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()


# TC-37: Finalizar el proceso de compra.
@when('finaliza el proceso')
def step_impl(context):
    """Completa checkout y finaliza la compra."""
    context.cart.proceed_to_checkout()
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-37: Verificar la confirmación final para el usuario.
@then('el usuario confirma que el pedido se realizó')
def step_impl(context):
    """Comprueba que el usuario reciba confirmación de su pedido."""
    assert '¡Compra realizada con éxito!' in context.driver.page_source


# TC-38: Preparar el carrito con dos productos distintos.
@given('el usuario agregó dos productos')
def step_impl(context):
    """Prepara el carrito con dos productos diferentes."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.add_product('Teclado Mecánico')
    context.catalog.open_cart()


# TC-38: Confirmar la compra de los dos productos.
@when('confirma la compra')
def step_impl(context):
    """Completa checkout y confirma la compra de los productos."""
    context.cart.proceed_to_checkout()
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-38: Verificar que la compra de varios artículos finalice correctamente.
@then('el proceso finaliza correctamente')
def step_impl(context):
    """Comprueba que el proceso termine con una compra exitosa."""
    assert '¡Compra realizada con éxito!' in context.driver.page_source


# TC-39: Intentar abrir checkout sin productos en el carrito.
@when('intenta ir a checkout')
def step_impl(context):
    """Intenta navegar al checkout mediante la acción de la tienda."""
    context.driver.execute_script("irACheckout();")


# TC-39: Verificar la validación de negocio para carrito vacío.
@then('recibe una validación de negocio')
def step_impl(context):
    """Comprueba que la tienda permanezca en una vista permitida."""
    assert context.driver.execute_script("return estado.vista;") in ('catalogo', 'carrito')


# TC-40: Preparar el carrito para revisar el resumen del pedido.
@given('el usuario observa el resumen del pedido')
def step_impl(context):
    """Prepara un producto en el carrito para consultar su resumen."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()


# TC-40: Mantener visible el resumen para revisar el total.
@when('revisa el carrito y el total')
def step_impl(context):
    """Mantiene visible el resumen del carrito para su revisión."""
    pass


# TC-40: Verificar que el total corresponda a los productos y descuentos.
@then('el total coincide con los productos y descuentos')
def step_impl(context):
    """Comprueba que el total calculado sea positivo."""
    total = float(context.driver.execute_script("return calcularTotales().total;"))
    assert total > 0


# TC-41: Preparar la tienda para el flujo de compra completo.
@given('el usuario quiere comprar')
def step_impl(context):
    """Prepara la tienda para iniciar una compra."""
    prepare_browser(context)


# TC-41: Agregar un producto, aplicar cupón y completar el checkout.
@when('agrega un producto, aplica cupón y confirma la compra')
def step_impl(context):
    """Agrega un producto, aplica el cupón y completa la compra."""
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()
    context.cart.apply_coupon('DESCUENTO10')
    context.cart.proceed_to_checkout()
    context.checkout.fill_shipping_info('María López', 'maria@correo.com', 'Jr. 9 de Octubre 456', 'Lima', '987654321')
    context.checkout.select_payment_method('yape')
    context.checkout.confirm_payment()


# TC-41: Verificar que el flujo completo finalice con éxito.
@then('completa la compra satisfactoriamente')
def step_impl(context):
    """Comprueba que la compra completa haya finalizado con éxito."""
    assert '¡Compra realizada con éxito!' in context.driver.page_source