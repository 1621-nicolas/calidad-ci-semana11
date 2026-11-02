Feature: TiendaDemo - TC-14 a TC-19

  Scenario: TC-14 - Aplicar cupón válido
    Given tengo un producto en el carrito
    When abro el carrito
    And aplico el cupón "DESCUENTO10"
    Then veo el mensaje de cupón aplicado

  Scenario: TC-15 - Aplicar cupón inválido
    Given tengo un producto en el carrito
    When abro el carrito
    And aplico el cupón "INVALIDO"
    Then veo un mensaje de cupón no válido

  Scenario: TC-16 - Aplicar cupón vacío
    Given tengo un producto en el carrito
    When abro el carrito
    And aplico un cupón vacío
    Then se muestra un mensaje de validación

  Scenario: TC-17 - Aplicar cupón repetido
    Given tengo un producto en el carrito con cupón aplicado
    When intento aplicar el mismo cupón otra vez
    Then se muestra un aviso de cupón ya aplicado

  Scenario: TC-18 - Verificar total con descuento
    Given tengo un producto en el carrito
    When aplico el cupón "DESCUENTO10"
    Then el total final refleja el descuento

  Scenario: TC-19 - Verificar total sin descuento
    Given tengo un producto en el carrito
    When no aplico ningún cupón
    Then el total final es el precio base