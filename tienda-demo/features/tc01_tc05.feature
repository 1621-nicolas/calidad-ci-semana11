Feature: TiendaDemo - TC-01 a TC-05

  Scenario: TC-01 - Agregar producto al carrito
    Given estoy en el catálogo de TiendaDemo
    When agrego "Laptop Pro 15" al carrito
    Then veo el producto "Laptop Pro 15" en el carrito

  Scenario: TC-02 - Agregar varios productos diferentes
    Given estoy en el catálogo de TiendaDemo
    When agrego "Laptop Pro 15" al carrito
    And agrego "Mouse Inalámbrico" al carrito
    Then veo ambos productos en el carrito

  Scenario: TC-03 - Agregar el mismo producto dos veces
    Given estoy en el catálogo de TiendaDemo
    When agrego "Laptop Pro 15" al carrito
    And agrego "Laptop Pro 15" al carrito
    Then el carrito refleja la cantidad correcta del producto

  Scenario: TC-04 - Verificar contador del carrito
    Given estoy en el catálogo de TiendaDemo
    When agrego "Laptop Pro 15" al carrito
    Then el contador del carrito muestra 1

  Scenario: TC-05 - Ver producto en la vista del carrito
    Given estoy en el catálogo de TiendaDemo
    When agrego "Laptop Pro 15" al carrito
    And abro el carrito
    Then veo "Laptop Pro 15" en la lista del carrito