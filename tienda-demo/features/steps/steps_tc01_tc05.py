from behave import given, then, when

from features.steps.common_steps import prepare_browser


# TC-01 a TC-05: Preparar el catálogo para agregar productos.
@given('estoy en el catálogo de TiendaDemo')
def step_impl(context):
    """Abre la tienda en la vista del catálogo."""
    prepare_browser(context)


# TC-01 a TC-05: Agregar uno o más productos al carrito.
@when('agrego "{producto}" al carrito')
def step_impl(context, producto):
    """Agrega al carrito el producto indicado en el escenario."""
    context.catalog.add_product(producto)


# TC-01: Comprobar que el producto agregado aparece en el carrito.
@then('veo el producto "{producto}" en el carrito')
def step_impl(context, producto):
    """Comprueba que el producto indicado aparezca en el carrito."""
    context.catalog.open_cart()
    assert context.cart.get_item_row(producto) is not None


# TC-02: Comprobar que aparecen los dos productos diferentes.
@then('veo ambos productos en el carrito')
def step_impl(context):
    """Comprueba que ambos productos esperados estén en el carrito."""
    context.catalog.open_cart()
    assert context.cart.get_item_row('Laptop Pro 15') is not None
    assert context.cart.get_item_row('Mouse Inalámbrico') is not None


# TC-03: Comprobar la cantidad al agregar dos veces el mismo producto.
@then('el carrito refleja la cantidad correcta del producto')
def step_impl(context):
    """Comprueba que la cantidad del producto en el carrito sea dos."""
    context.catalog.open_cart()
    assert context.cart.get_quantity('Laptop Pro 15') == 2


# TC-04: Comprobar el contador después de agregar un producto.
@then('el contador del carrito muestra 1')
def step_impl(context):
    """Comprueba que el contador del carrito indique un artículo."""
    assert context.catalog.get_cart_count() == 1


# TC-05: Comprobar el producto en la vista del carrito.
@then('veo "Laptop Pro 15" en la lista del carrito')
def step_impl(context):
    """Comprueba que la laptop aparezca en la lista del carrito."""
    assert context.cart.get_item_row('Laptop Pro 15') is not None