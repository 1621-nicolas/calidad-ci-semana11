Feature: TiendaDemo - TC-20 a TC-31

  Scenario: TC-20 - Intentar pagar sin productos en carrito
    Given el carrito está vacío
    When intento acceder al checkout
    Then se bloquea la compra o se muestra un mensaje de error

  Scenario: TC-21 - Confirmar checkout con datos vacíos
    Given estoy en la página de checkout con un artículo en el carrito
    When intento confirmar el pago sin completar los datos
    Then veo mensajes de error para los campos obligatorios

  Scenario: TC-22 - Validar nombre obligatorio
    Given estoy en la página de checkout con un artículo en el carrito
    When dejo el nombre vacío y confirmo
    Then veo el error del nombre obligatorio

  Scenario: TC-23 - Validar apellido obligatorio
    Given estoy en la página de checkout con un artículo en el carrito
    When dejo el apellido vacío y confirmo
    Then veo el error del apellido obligatorio

  Scenario: TC-24 - Validar correo obligatorio
    Given estoy en la página de checkout con un artículo en el carrito
    When dejo el correo vacío y confirmo
    Then veo el error del correo obligatorio

  Scenario: TC-25 - Validar correo con formato inválido
    Given estoy en la página de checkout con un artículo en el carrito
    When ingreso un correo sin formato válido
    Then veo un mensaje de correo inválido

  Scenario: TC-26 - Validar teléfono obligatorio
    Given estoy en la página de checkout con un artículo en el carrito
    When dejo el teléfono vacío y confirmo
    Then veo el error del teléfono obligatorio

  Scenario: TC-27 - Validar dirección obligatoria
    Given estoy en la página de checkout con un artículo en el carrito
    When dejo la dirección vacía y confirmo
    Then veo el error de la dirección obligatoria

  Scenario: TC-28 - Validar ciudad obligatoria
    Given estoy en la página de checkout con un artículo en el carrito
    When dejo la ciudad vacía y confirmo
    Then veo el error de la ciudad obligatoria

  Scenario: TC-29 - Confirmar compra con datos válidos
    Given estoy en la página de checkout con un artículo en el carrito
    When completo todos los datos y confirmo el pago
    Then veo la pantalla de confirmación

  Scenario: TC-30 - Confirmar compra con varios productos
    Given tengo varios productos en el carrito
    And estoy en checkout
    When completo los datos válidos y confirmo
    Then la compra se procesa correctamente

  Scenario: TC-31 - Ver pantalla de confirmación
    Given estoy en la página de checkout con un artículo en el carrito
    When completo todos los datos y confirmo el pago
    Then veo la pantalla de confirmación