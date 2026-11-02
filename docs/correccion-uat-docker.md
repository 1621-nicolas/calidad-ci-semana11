# Corrección UAT en Docker – Semana 11

## Evidencia original

- `ci/execute.py unit`: exportador JUnit 7/7; el bloque Aula Nova generó un XML (el log no muestra el conteo de subpruebas).
- `ci/execute.py selenium`: 41/41 casos aprobados.
- `ci/execute.py playwright`: 42/42 aprobados (41 TC más un control adicional).
- `ci/execute.py functional`: semana 8 TiendaDemo 8/8 y semana 9 TiendaDemo 6/6; el reporte de Aula Nova se escribió en XML.
- `ci/execute.py uat`: **50 escenarios con error**, todos durante los pasos de preparación; `JavascriptException: estado is not defined`. La regresión separada de 9 pruebas sí aprobó 9/9.

## Causa

En `tienda-demo/features/steps/common_steps.py`, Behave forzaba una URL `file:///workspace/.../tienda_demo.html`. Cuando WebDriver está conectado al **contenedor remoto** `selenium/standalone-chrome`, esa ruta local del contenedor de pruebas no existe en el contenedor Chrome. El navegador no carga `carrito.js`, por lo que `estado` no está definido.

El contenedor `selenium-tests` ya dispone de las variables:

- `SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub`
- `TIENDA_BASE_URL=http://tienda-demo:8008/`

La suite Selenium unittest usaba `TIENDA_BASE_URL`, razón por la que sus 41 casos pasaban.

## Cambios aplicados

1. `common_steps.py` ahora usa `TIENDA_BASE_URL` como primera opción y `file://` solo para navegadores locales.
2. Con WebDriver remoto sin URL HTTP configurada, produce un error de configuración explícito.
3. Antes de ejecutar el reinicio del carrito, espera a que `document.readyState`, la variable `estado`, la función `renderCatalogo` y el catálogo estén cargados.
4. No se alteraron las expectativas, los pasos ni los 50 escenarios de Behave para forzar aprobaciones.

## Aplicación en Windows (PowerShell)

Desde la carpeta `calidad-ci-semana11` **después de sobrescribir** el archivo corregido:

```powershell
# El Dockerfile copia tienda-demo/ dentro de la imagen del ejecutor.
# Por ello es necesario reconstruir ese servicio.
docker compose build selenium-tests

# Reejecuta los 50 escenarios Behave y las 9 regresiones
python ci\execute.py uat

# Revisa el reporte y los resultados
docker compose ps
Get-ChildItem .\reports\uat\*.xml
Get-Content .\reports\status\uat.json
```

Si todavía falla, revisar el nuevo log completo en `reports/console/uat.txt` y comparar la salida del navegador.

## Verificación de la corrección

Se comprobó con pruebas locales simulando el entorno remoto que la URL es HTTP, que se espera la carga de la aplicación antes del reinicio de estado y que la ausencia de una URL remota produce un mensaje de configuración. **No se certifica todavía 50/50 en Docker** hasta ejecutar el comando indicado en el equipo con Docker Desktop.
