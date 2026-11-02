# TiendaDemo — corrección de fallos y validación (30/10/2026)

## Problemas reportados y soluciones

| ID | Fallo previo | Cambio aplicado | Validación disponible |
|---|---|---|---|
| TC42 | Teléfono con letras era aceptado | Sólo dígitos y separadores permitidos; 7–15 dígitos | Navegador, aprobado |
| TC43 | Teléfono con espacios era rechazado | Se acepta `987 654 321` | Navegador, aprobado |
| TC44 | Cupón inválido eliminaba descuento válido | No restablecer `cuponAplicado` tras código inválido | Navegador, aprobado |
| TC45 | Ciudad numérica era aceptada | Exigir letras Unicode y longitud mínima | Navegador, aprobado |
| TC46 | Stock no disminuía después de comprar | Restar cantidades tras validación y antes de confirmar; proteger contra stock insuficiente | Navegador, aprobado |
| TC47 | Nombre compuesto sólo por números | Exigir nombre y apellido alfabéticos | Navegador, aprobado |
| TC48 | Correo con TLD de una letra | Exigir TLD de al menos dos letras | Navegador, aprobado |
| TC49 | Dirección sin contenido descriptivo | Exigir letras, longitud y más de un componente | Navegador, aprobado |
| TC50 | Teléfono con más de 15 dígitos | Límite superior de 15 dígitos | Navegador, aprobado |
| S11 | XSS DOM en el buscador sin resultados | Construcción del mensaje con nodos DOM y `textContent` | Navegador, aprobado |
| JUnit/k6 | `bool` sin método `.get()` | Analizar umbrales booleanos y `{ok: bool}`; los fallos se mantienen como fallos | 7 pruebas unittest aprobadas |
| Salida Jenkins | Caracteres españoles mal codificados | `chcp 65001` y `PYTHONIOENCODING=utf-8` en Windows | Configuración modificada; requiere validar en Jenkins |

## Alcance de lo comprobado

- Navegador Chromium ejecutado mediante Playwright por carga directa de HTML/JS en una página de prueba (sin navegación externa): **12 de 12 casos** aprobados. Se reprodujeron los escenarios TC42–TC50, XSS, validaciones vacías y búsqueda. No se ejecutaron los archivos `tests/test_fails.py` con Selenium en el ambiente de elaboración por falta de dependencias instalables.
- `python -m unittest discover -s quality/week9 -p test_http_seguridad.py -v`: **10/10** aprobados.
- `python -m unittest discover -s quality/week9 -p test_exportador_k6.py -v`: **7/7** aprobados.
- El lanzador `run_k6_suite` se probó con **un ejecutable simulado**, que generó reportes de estructura válida para tres casos de rendimiento, dos de seguridad y uno de estrés. NO son resultados reales de k6. Por este motivo, esos reportes de simulación se eliminaron de la entrega.
- Sintaxis `node --check app/carrito.js` y de los tres scripts k6: válida.
- No se ejecutó el servidor Jenkins ni Grafana k6 reales de tu Windows. Se requiere volver a lanzar ambas suites heredadas, las funcionales nuevas y la suite k6 después de sustituir el proyecto.

## Actualización en Windows

1. Haz una copia del proyecto anterior. Extrae este ZIP **en otra carpeta**, por ejemplo `C:\QA\TiendaDemo_corregido\proyecto-tiendademo_Jenkins`.
2. Abre Jenkins > TiendaDemo > Configure. Si usas *Pipeline script*, **reemplaza todo el script anterior** por el `Jenkinsfile` dentro de la carpeta corregida. Editar el archivo sin pegarlo en Jenkins **no modifica** el job de tipo inline.
3. En *Build with Parameters*, establece `PROJECT_DIR` en la **nueva ruta real** y confirma `PYTHON_EXE` y `K6_EXE`.
4. Primero ejecuta suites Python y seguridad de navegador. Una vez aprobadas, activa `RUN_K6` con smoke; revisa los JSON/TXT generados. Activa `RUN_FULL_PERFORMANCE` y `RUN_STRESS` sólo cuando estés listo para pruebas largas de carga controlada.
5. Si un paso falla, consulta *Console Output* y *Test Result*; no manipules las aserciones para hacer pasar una prueba defectuosa.

### Verificación manual en la raíz del proyecto

```powershell
python -m pip install -r requirements.txt
python -m xmlrunner discover -s tests -o reports/unittest
python -m behave features --junit --junit-directory reports/behave
python -m xmlrunner discover -s quality/week8 -p test_semana8.py -o reports/semana8
python -m xmlrunner discover -s quality/week9 -p test_funcionales.py -o reports/semana9
python -m xmlrunner discover -s quality/week9 -p test_http_seguridad.py -o reports/seguridad
python -m xmlrunner discover -s quality/week9 -p test_seguridad_ui.py -o reports/seguridad
python -m xmlrunner discover -s quality/week9 -p test_exportador_k6.py -o reports/exportador
python -m scripts.run_k6_suite --group rendimiento --cases 1,2,3 --smoke
```

**Importante:** TiendaDemo es una demo de HTML y JS sin backend. El inventario se actualiza sólo en memoria mientras la página no se recargue; no es persistencia transaccional ni un sistema de comercio electrónico real. Las pruebas k6 miden el servidor local estático, no la rapidez del motor DOM ni el procesamiento de pedidos con persistencia.
