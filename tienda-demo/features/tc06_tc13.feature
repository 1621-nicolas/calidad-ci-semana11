Feature: TiendaDemo - TC-06 a TC-13

  Scenario: TC-06 - Aumentar cantidad de un producto
    Given tengo un producto en el carrito
    When aumento la cantidad del producto a 2
    Then el total del producto se actualiza correctamente

  Scenario: TC-07 - Disminuir cantidad de un producto
    Given tengo un producto en el carrito con cantidad 2
    When disminuyo la cantidad del producto a 1
    Then la cantidad del producto queda en 1

  Scenario: TC-08 - Cambiar cantidad a cero
    Given tengo un producto en el carrito
    When cambio la cantidad del producto a 0
    Then el producto se elimina del carrito

  Scenario: TC-09 - Ingresar cantidad negativa
    Given tengo un producto en el carrito
    When ingreso una cantidad negativa
    Then el sistema impide una cantidad negativa

  Scenario: TC-10 - Eliminar un producto del carrito
    Given tengo varios productos en el carrito
    When elimino "Laptop Pro 15"
    Then el producto ya no aparece en el carrito

  Scenario: TC-11 - Eliminar el último producto del carrito
    Given tengo un producto en el carrito
    When elimino el producto
    Then el carrito queda vacío

  Scenario: TC-12 - Eliminar un producto cuando hay varios
    Given tengo varios productos en el carrito
    When elimino uno de ellos
    Then el producto eliminado desaparece y los demás permanecen

  Scenario: TC-13 - Actualizar subtotal al eliminar un producto
    Given tengo dos productos en el carrito
    When elimino uno de ellos
    Then el subtotal se recalcula correctamente