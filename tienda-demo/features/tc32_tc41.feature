Feature: TiendaDemo - TC-32 a TC-41

  Scenario: TC-32 - UAT: Agregar producto desde la perspectiva del usuario
    Given el usuario entra a la tienda
    When selecciona un producto
    And hace clic en agregar
    Then puede ver el producto en el carrito

  Scenario: TC-33 - UAT: Ver el carrito con el producto agregado
    Given el usuario agregó un producto
    When abre el carrito
    Then puede revisar el producto, la cantidad y el total

  Scenario: TC-34 - UAT: Aplicar cupón válido
    Given el usuario tiene un producto en el carrito
    When aplica un cupón válido
    Then el descuento se refleja en el total

  Scenario: TC-35 - UAT: Completar checkout con datos normales
    Given el usuario tiene productos en el carrito
    When completa sus datos y confirma la compra
    Then recibe la confirmación del pedido

  Scenario: TC-36 - UAT: Intentar compra con datos incompletos
    Given el usuario tiene productos en el carrito
    When intenta confirmar con campos vacíos
    Then el sistema le indica qué falta completar

  Scenario: TC-37 - UAT: Confirmar pedido final
    Given la compra es válida
    When finaliza el proceso
    Then el usuario confirma que el pedido se realizó

  Scenario: TC-38 - UAT: Comprar con más de un artículo
    Given el usuario agregó dos productos
    When confirma la compra
    Then el proceso finaliza correctamente

  Scenario: TC-39 - UAT: Intentar compra con carrito vacío
    Given el carrito está vacío
    When intenta ir a checkout
    Then recibe una validación de negocio

  Scenario: TC-40 - UAT: Validar total final correcto
    Given el usuario observa el resumen del pedido
    When revisa el carrito y el total
    Then el total coincide con los productos y descuentos

  Scenario: TC-41 - UAT: Flujo completo de compra
    Given el usuario quiere comprar
    When agrega un producto, aplica cupón y confirma la compra
    Then completa la compra satisfactoriamente