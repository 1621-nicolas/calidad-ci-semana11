"""41 casos Playwright equivalentes a TC01–TC41 de la suite Selenium.

Cada ID representa un escenario con aserciones observables en el navegador.
No sustituye los 41 casos Selenium: se ejecutan ambas suites de forma independiente.
"""
import os
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright, expect

APP = Path(__file__).resolve().parents[2] / 'tienda-demo' / 'app' / 'tienda_demo.html'
BASE = os.getenv('TIENDA_BASE_URL', APP.as_uri())

@pytest.fixture
def page():
    with sync_playwright() as p:
        executable = os.getenv('PLAYWRIGHT_EXECUTABLE')
        browser = p.chromium.launch(headless=True, executable_path=executable or None, args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        tab = context.new_page()
        tab.goto(BASE)
        # Reset de los datos mutables: cada navegador fresco contiene el stock original.
        yield tab
        context.close()
        browser.close()

def add(page, name='Laptop Pro 15'):
    page.locator('.tarjeta-producto').filter(has_text=name).locator('button.btn-agregar').click()

def cart(page):
    page.locator('#btn-abrir-carrito').click()

def row(page, name='Laptop Pro 15'):
    return page.locator('.item-carrito').filter(has_text=name)

def coupon(page, code):
    page.locator('#input-cupon').fill(code)
    page.locator('#btn-aplicar-cupon').click()

def to_checkout(page):
    cart(page)
    page.locator('#btn-ir-checkout').click()

def fill(page, *, name='María López', email='maria@correo.com', address='Jr. 9 de Octubre 456', city='Lima', phone='987654321'):
    for selector,value in [('#campo-nombre',name),('#campo-email',email),('#campo-direccion',address),('#campo-ciudad',city),('#campo-telefono',phone)]:
        page.locator(selector).fill(value)
    page.locator('input[name=pago][value=yape]').check()

def buy(page, products=('Disco SSD 1TB',), *, valid=True, discount=False):
    for product in products: add(page,product)
    to_checkout(page)
    if valid: fill(page)
    if discount:
        page.locator('#btn-volver-carrito').click()
        coupon(page,'DESCUENTO10')
        page.locator('#btn-ir-checkout').click()
        fill(page)
    page.locator('#btn-confirmar-pago').click()

def total(page):
    return page.evaluate('calcularTotales().total')

def assert_error(page, word):
    page.locator('#btn-confirmar-pago').click()
    assert word.lower() in ' '.join(page.locator('.error-campo.visible').all_text_contents()).lower()

TITLES = [
'Agregar producto','Agregar productos distintos','Agregar mismo producto dos veces','Contador del carrito','Producto visible',
'Aumentar cantidad','Disminuir cantidad','Eliminar cantidad cero','Nunca guardar cantidad negativa','Eliminar producto',
'Carrito vacío al eliminar','Eliminar uno sin afectar otro','Actualizar subtotal','Cupón válido','Cupón inválido','Cupón vacío',
'Cupón repetido','Total con descuento','Total sin descuento','Bloquear checkout vacío','Campos obligatorios',
'Nombre obligatorio','Apellido obligatorio','Correo obligatorio','Correo inválido','Teléfono obligatorio','Dirección obligatoria',
'Ciudad obligatoria','Compra válida','Compra con varios artículos','Pantalla de confirmación',
'UAT agregar producto','UAT producto visible','UAT cupón','UAT checkout válido','UAT datos incompletos',
'UAT pedido confirmado','UAT varios productos','UAT carrito vacío','UAT total correcto','UAT flujo completo con cupón'
]

@pytest.mark.parametrize('case_id', range(1,42), ids=[f'TC{i:02d}' for i in range(1,42)])
def test_41_casos_equivalentes_selenium(page, case_id):
    """Cada caso tiene un identificador estable para TestLink y un criterio observable."""
    cid=case_id
    if cid in (1,32):
        add(page); expect(page.locator('#contador-carrito')).to_have_text('1')
    elif cid in (2,4):
        add(page);add(page,'Teclado Mecánico');expect(page.locator('#contador-carrito')).to_have_text('2')
    elif cid == 3:
        add(page);add(page);expect(page.locator('#contador-carrito')).to_have_text('2')
    elif cid in (5,33):
        add(page);cart(page);expect(row(page)).to_be_visible()
    elif cid in (6,7):
        add(page);cart(page)
        row(page).locator('[data-accion=mas]').click()
        expect(row(page).locator('.cantidad-num')).to_have_text('2')
        if cid==7:
            row(page).locator('[data-accion=menos]').click()
            expect(row(page).locator('.cantidad-num')).to_have_text('1')
    elif cid in (8,9,10,11):
        add(page);cart(page)
        if cid in (8,9):
            page.evaluate("cambiarCantidad(1,'menos');")
            if cid==9: page.evaluate("cambiarCantidad(1,'menos');")
        else: row(page).locator('.btn-eliminar').click()
        expect(row(page)).to_have_count(0)
        if cid==9: assert page.evaluate('estado.carrito.every(i=>i.cantidad>0)')
        if cid==11: expect(page.locator('#carrito-vacio')).to_be_visible()
    elif cid in (12,13):
        add(page);add(page,'Teclado Mecánico');cart(page)
        row(page).locator('.btn-eliminar').click()
        expect(row(page)).to_have_count(0)
        expect(row(page,'Teclado Mecánico')).to_be_visible()
        if cid==13: assert total(page)==249.0
    elif cid in (14,34):
        add(page);cart(page);coupon(page,'DESCUENTO10');expect(page.locator('#msg-cupon')).to_contain_text('DESCUENTO10')
    elif cid==15:
        add(page);cart(page);coupon(page,'INVALIDO');expect(page.locator('#msg-cupon')).to_contain_text('Cupón no válido')
    elif cid==16:
        add(page);cart(page);coupon(page,'');expect(page.locator('#msg-cupon')).to_contain_text('Ingresa un código')
    elif cid in (17,18):
        add(page);cart(page);coupon(page,'DESCUENTO10')
        if cid==17:
            coupon(page,'DESCUENTO10'); expect(page.locator('#msg-cupon')).to_contain_text('ya está aplicado')
        assert abs(total(page)-2249.10)<0.01
    elif cid in (19,40):
        add(page);cart(page);assert abs(total(page)-2499.0)<0.01
    elif cid in (20,39):
        page.evaluate('irACheckout()');assert page.evaluate('estado.vista')=='catalogo'
    elif cid in (21,36):
        buy(page,valid=False);expect(page.locator('.error-campo.visible')).to_have_count(5)
    elif cid in (22,23,24,25,26,27,28):
        add(page,'Disco SSD 1TB');to_checkout(page)
        overrides={22:dict(name=''),23:dict(name='María'),24:dict(email=''),25:dict(email='incorrecto'),26:dict(phone=''),27:dict(address=''),28:dict(city='')}
        fill(page,**overrides[cid]);assert_error(page,{22:'nombre',23:'apellido',24:'correo',25:'correo',26:'teléfono',27:'dirección',28:'ciudad'}[cid])
    elif cid in (29,35):
        buy(page);expect(page.locator('#msg-confirmacion')).to_contain_text('Compra realizada con éxito')
    elif cid in (30,38):
        buy(page,('Disco SSD 1TB','Teclado Mecánico'))
        expect(page.locator('#msg-confirmacion')).to_contain_text('Compra realizada con éxito')
    elif cid==31:
        buy(page);expect(page.locator('#confirmacion-card')).to_contain_text('Gracias')
    elif cid==37:
        buy(page);expect(page.locator('#detalle-orden')).to_contain_text('Confirmado')
    elif cid==41:
        add(page);cart(page);coupon(page,'DESCUENTO10');page.locator('#btn-ir-checkout').click()
        fill(page);page.locator('#btn-confirmar-pago').click()
        expect(page.locator('#msg-confirmacion')).to_contain_text('Compra realizada con éxito')
    else:
        raise AssertionError(f'Caso no implementado: {cid}')
