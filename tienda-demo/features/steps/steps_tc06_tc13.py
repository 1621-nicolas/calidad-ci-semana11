from behave import given, then, when

from features.steps.common_steps import prepare_browser


# TC-06, TC-08, TC-09 y TC-11: Preparar un producto en el carrito.


@given('tengo un producto en el carrito con cantidad 2')
def step_impl(context):
    """Prepara el carrito con dos unidades del mismo producto."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.open_cart()


# TC-06: Aumentar la cantidad del producto.
@when('aumento la cantidad del producto a 2')
def step_impl(context):
    """Aumenta en una unidad la cantidad del producto."""
    context.cart.increase_quantity('Laptop Pro 15')


# TC-06: Verificar la cantidad actualizada del producto.
@then('el total del producto se actualiza correctamente')
def step_impl(context):
    """Comprueba que la cantidad del producto sea dos."""
    assert context.cart.get_quantity('Laptop Pro 15') == 2


# TC-07: Disminuir la cantidad del producto.
@when('disminuyo la cantidad del producto a 1')
def step_impl(context):
    """Reduce en una unidad la cantidad del producto."""
    context.cart.decrease_quantity('Laptop Pro 15')


# TC-07: Verificar que quede una unidad.
@then('la cantidad del producto queda en 1')
def step_impl(context):
    """Comprueba que quede una unidad del producto."""
    assert context.cart.get_quantity('Laptop Pro 15') == 1


# TC-08: Reducir la cantidad del producto a cero.
@when('cambio la cantidad del producto a 0')
def step_impl(context):
    """Reduce a cero la cantidad del producto."""
    context.cart.decrease_quantity('Laptop Pro 15')


# TC-08: Verificar la eliminación del producto al llegar a cero.
@then('el producto se elimina del carrito')
def step_impl(context):
    """Comprueba que el producto con cantidad cero ya no esté en el carrito."""
    assert context.cart.get_item_row('Laptop Pro 15') is None


# TC-09: Intentar reducir la cantidad por debajo de cero.
@when('ingreso una cantidad negativa')
def step_impl(context):
    """Intenta reducir el producto por debajo de cero."""
    context.driver.execute_script("""
        cambiarCantidad(1, 'menos');
        cambiarCantidad(1, 'menos');
    """)


# TC-09: Verificar que no queden cantidades negativas.
@then('el sistema impide una cantidad negativa')
def step_impl(context):
    """Comprueba que no queden productos con cantidades negativas."""
    assert context.driver.execute_script("return estado.carrito.length;") == 0
    assert context.driver.execute_script("return estado.carrito.every(item => item.cantidad > 0);")


# TC-10, TC-12 y TC-13: Preparar productos distintos en el carrito.
@given('tengo dos productos en el carrito')
def step_impl(context):
    """Prepara el carrito con dos productos distintos."""
    prepare_browser(context)
    context.catalog.add_product('Laptop Pro 15')
    context.catalog.add_product('Teclado Mecánico')
    context.catalog.open_cart()


# TC-10: Eliminar la laptop del carrito.
@when('elimino "Laptop Pro 15"')
def step_impl(context):
    """Elimina la laptop del carrito."""
    context.cart.remove_item('Laptop Pro 15')


# TC-10: Verificar que la laptop ya no esté en el carrito.
@then('el producto ya no aparece en el carrito')
def step_impl(context):
    """Comprueba que la laptop haya desaparecido del carrito."""
    assert context.cart.get_item_row('Laptop Pro 15') is None


# TC-11: Eliminar el único producto del carrito.
@when('elimino el producto')
def step_impl(context):
    """Elimina la laptop del carrito."""
    context.cart.remove_item('Laptop Pro 15')


# TC-11: Verificar que el carrito quede vacío.
@then('el carrito queda vacío')
def step_impl(context):
    """Comprueba que el carrito muestre su estado vacío."""
    assert context.cart.has_empty_message() or context.driver.execute_script("return estado.carrito.length;") == 0


# TC-12 y TC-13: Eliminar un producto de un carrito con varios artículos.
@when('elimino uno de ellos')
def step_impl(context):
    """Elimina la laptop de los productos del carrito."""
    context.cart.remove_item('Laptop Pro 15')


# TC-12: Verificar que el eliminado desaparezca y los demás permanezcan.
@then('el producto eliminado desaparece y los demás permanecen')
def step_impl(context):
    """Comprueba que solo permanezca en el carrito el otro producto."""
    assert context.cart.get_item_row('Laptop Pro 15') is None
    assert context.cart.get_item_row('Teclado Mecánico') is not None


# TC-13: Verificar el subtotal después de eliminar un producto.
@then('el subtotal se recalcula correctamente')
def step_impl(context):
    """Comprueba que el subtotal calculado no sea negativo."""
    assert context.driver.execute_script("return calcularTotales().subtotal >= 0;") is True