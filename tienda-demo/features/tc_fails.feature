Feature: Casos fallidos de TiendaDemo

  Scenario: TC-42 - Rechazar un teléfono que contiene letras
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso un teléfono con letras y confirmo
    Then veo un mensaje de teléfono inválido

  Scenario: TC-43 - Aceptar el formato de teléfono mostrado en el formulario
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso un teléfono con espacios y confirmo
    Then veo la pantalla de confirmación

  Scenario: TC-44 - Conservar un cupón válido tras intentar aplicar uno inválido
    Given tengo un producto en el carrito
    When aplico un cupón válido y luego uno inválido
    Then se conserva el descuento del cupón válido

  Scenario: TC-45 - Rechazar una ciudad compuesta solo por números
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso una ciudad compuesta solo por números y confirmo
    Then veo un mensaje de ciudad inválida

  Scenario: TC-46 - Actualizar el stock después de confirmar una compra
    Given estoy en la página de checkout con un artículo en el carrito
    When completo la compra de una unidad de Laptop Pro 15
    Then el stock de Laptop Pro 15 disminuye en una unidad

  Scenario: TC-47 - Rechazar un nombre compuesto solo por números
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso un nombre compuesto solo por números y confirmo
    Then veo un mensaje de nombre inválido

  Scenario: TC-48 - Rechazar un correo con dominio de una sola letra
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso un correo con dominio de una sola letra y confirmo
    Then el correo con dominio corto se rechaza

  Scenario: TC-49 - Rechazar una dirección sin contenido descriptivo
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso una dirección sin contenido descriptivo y confirmo
    Then veo un mensaje de dirección inválida

  Scenario: TC-50 - Rechazar un teléfono con más de quince dígitos
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso un teléfono con más de quince dígitos y confirmo
    Then el teléfono excesivo se rechaza
