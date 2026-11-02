# TiendaDemo — Integración Jenkins: semanas 8 y 9

Este proyecto conserva el trabajo original de **TiendaDemo** y agrega pruebas acordes con su funcionalidad real. No trasplanta endpoints de **Aula Nova** ni de **Talenvía**, porque no existen en esta aplicación. Se siguió la guía entregada **«Instrucciones - replicar el job TiendaDemo en Jenkins.pdf»**: instalar dependencias, ejecutar unittest y Behave, publicar JUnit, archivar `reports/` y mantener la ejecución de las siguientes etapas aunque fallen las anteriores.

## 1. Qué se añadió

| Suite | Archivo o carpeta | Propósito |
|---|---|---|
| TC01–TC50 (original) | `tests/` | 51 unittest existentes. Incluyen **9 casos de defectos conocidos**, documentados por el proyecto original. |
| TC01–TC50 (original) | `features/` | Escenarios Behave existentes (50 en el informe original). Algunos detectan defectos conocidos. |
| Semana 8 | `quality/week8/test_semana8.py` | **8 casos funcionales Selenium** sobre catálogo, búsqueda, carrito, cupón y compra. |
| Semana 9 funcional | `quality/week9/test_funcionales.py` | **6 casos funcionales Selenium** sobre límites y compra. |
| Semana 9 seguridad HTTP | `quality/week9/test_http_seguridad.py` | **10 casos HTTP verificables** de rutas, métodos, cabeceras y tamaño de solicitudes. |
| Semana 9 seguridad del navegador | `quality/week9/test_seguridad_ui.py` | **1 caso Selenium** de regresión XSS sobre el buscador, corregido en `renderCatalogo()`. |
| Publicación JUnit k6 | `quality/week9/test_exportador_k6.py` | **7 casos unittest** que validan umbrales k6 booleanos y objetos, errores y ausencia de resumen. |
| Semana 9 rendimiento | `k6/rendimiento.js` | **R01–R10**, rendimiento HTTP **del sitio estático**, no del checkout en navegador. |
| Semana 9 estrés | `k6/estres.js` | **E01–E10**, estrés HTTP de recursos estáticos; se ejecuta solo si se habilita. |
| Semana 9 seguridad k6 | `k6/seguridad.js` | **S01–S10**, controles HTTP del servidor de pruebas. |

**Limitación de alcance:** TiendaDemo es un HTML con JavaScript en el navegador, sin API de login, curso, mensajes ni persistencia remota. k6 mide las respuestas del **servidor HTTP local de prueba** (`scripts/qa_server.py`), y **no** el rendimiento del carrito, pagos reales, SQL Server, autenticación, transacciones ni concurrencia del DOM. Los escenarios de seguridad HTTP verifican el servidor de prueba; la inyección de HTML del buscador se verifica aparte con Selenium.

## 2. Requisitos en Windows

1. Jenkins en `http://localhost:8080`, con plugins **Pipeline** y **JUnit**.
2. Python 3 y Google Chrome instalados **para la cuenta que ejecuta Jenkins**.
3. Instalar k6 para las pruebas no funcionales con `winget install k6 --source winget`. Cierra y reabre la consola; prueba `k6 version`.
4. Permisos de lectura/escritura de Jenkins sobre el proyecto, especialmente `reports/`.
5. Internet inicialmente para instalar Selenium, Behave, xmlrunner y/o ChromeDriver con Selenium Manager.

## 3. Configurar el job de Jenkins

### A. Desde carpeta local (igual que el PDF)

1. Extrae el ZIP en una ruta estable, por ejemplo `C:\QA\proyecto-tiendademo_Jenkins` (evita OneDrive si causa bloqueos).
2. En **New Item** crea `TiendaDemo`, tipo **Pipeline**. Si ya existe: **TiendaDemo > Configure**.
3. En **Pipeline > Definition** elige **Pipeline script**.
4. Copia **todo** el contenido de `Jenkinsfile` en el campo Script y guarda. **Si el job sigue usando el script antiguo, editar Jenkinsfile no cambia nada**.
5. Pulsa **Build with Parameters**. Configura `PROJECT_DIR` con la ruta de la carpeta que contiene `Jenkinsfile`, `app/`, `tests/`, `k6/` y `requirements.txt`.
6. Configura `PYTHON_EXE` con `python` si está en PATH, o la ruta completa a `python.exe` (por ejemplo `C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python314\python.exe`). **No uses la ruta de otra persona del PDF.**
7. Si k6 no está en PATH, configura `K6_EXE` con la ruta completa a `k6.exe`.
8. Ejecuta **Build with Parameters** y consulta **Console Output**, **Test Result** y **Artifacts**.

### B. Desde Git (preferido para CI/CD)

1. Publica el código en un repositorio Git sin tokens, `.venv`, `.git` ajenos ni `reports/`.
2. Selecciona **Pipeline script from SCM** > Git > repositorio > rama > **Script Path: `Jenkinsfile`**.
3. Deja `PROJECT_DIR` **vacío**: el pipeline trabajará desde el workspace descargado.
4. Si Jenkins corre en tu PC y no es accesible desde GitHub, configura **Poll SCM** como `H/5 * * * *` (sin exponer Jenkins directamente a Internet).

## 4. Parámetros del pipeline

- `RUN_K6=true` (predeterminado): ejecuta **R01–R03 en modo *smoke* de 5 segundos** y **S01–S10**. No equivale a completar R01–R10.
- `RUN_FULL_PERFORMANCE=true`: ejecuta **R01–R10 completos**, incluida la estabilidad **R09 por 30 minutos**. Requiere `RUN_K6=true`.
- `RUN_STRESS=true`: ejecuta **E01–E10**, intencionalmente intensivos; se mantiene desactivado por defecto. Requiere `RUN_K6=true`. Ejecutar únicamente en entorno local autorizado.
- `RUN_UI_SECURITY=true`: ejecuta una prueba de regresión DOM contra XSS que se corrigió en el buscador. Si vuelve a fallar, no ocultar el defecto.
- `PROJECT_DIR`: vacío si se usa Git; ruta absoluta si el proyecto está en una carpeta fuera del workspace.

Si todavía no tienes k6 instalado, usa `RUN_K6=false` durante la preparación, pero **esas pruebas quedarán sin ejecutar** y el informe debe indicarlo. Si está activado y falta k6, la etapa **falla de forma explícita**, sin inventar resultados.

## 5. Ejecución manual en PowerShell

Dentro de la carpeta raíz del proyecto:

```powershell
python -m pip install -r requirements.txt
python -m scripts.clean_reports

# Suites originales:
python -m xmlrunner discover -s tests -o reports/unittest
python -m behave features --junit --junit-directory reports/behave

# Semana 8 y 9, funcionales:
python -m xmlrunner discover -s quality/week8 -p test_semana8.py -o reports/semana8
python -m xmlrunner discover -s quality/week9 -p test_funcionales.py -o reports/semana9

# Seguridad de transporte HTTP y navegador:
python -m xmlrunner discover -s quality/week9 -p test_http_seguridad.py -o reports/seguridad
python -m xmlrunner discover -s quality/week9 -p test_seguridad_ui.py -o reports/seguridad
python -m xmlrunner discover -s quality/week9 -p test_exportador_k6.py -o reports/exportador

# k6: iniciar y cerrar automáticamente un servidor HTTP local solo para las pruebas:
python -m scripts.run_k6_suite --group rendimiento --cases 1,2,3 --smoke
python -m scripts.run_k6_suite --group seguridad --cases all

# Opt-in: todas las pruebas completas (R09 dura 30 min):
python -m scripts.run_k6_suite --group rendimiento --cases all
python -m scripts.run_k6_suite --group estres --cases all
```

Los casos k6 generan por separado `reports/rendimiento`, `reports/estres`, `reports/seguridad`, cada uno con JUnit XML, consola TXT y resumen JSON cuando se ejecutan. Jenkins usa **JUnit** para agrupar resultados, y **Artifacts** para guardar evidencia.

## 6. Estado de la corrección (30/10/2026)

En el paquete **anterior** se observaron 9 fallos en `tests/test_fails.py` y otros 9 en `tc_fails.feature`; también se detectó un XSS en el buscador y un `AttributeError` del exportador k6.

En esta revisión **no se cambiaron las afirmaciones de las pruebas**: se corrigió el comportamiento de `app/carrito.js` (teléfono, correo, ciudad, dirección, nombre, descuento, stock, búsqueda segura) y `scripts/run_k6_suite.py` (umbral booleano u objeto).

Verificación en el entorno de preparación:
- **12/12 verificaciones de navegador Chromium** ejecutadas con un harness Playwright de evaluación sobre el HTML+JS (incluye las 9 regresiones TC42–TC50, XSS, campos vacíos y búsqueda); no es la suite Selenium del usuario.
- **10/10 controles HTTP** reales aprobados con `unittest`.
- **7/7 pruebas del exportador JUnit** aprobadas con `unittest`.
- **6 casos del orquestador k6 comprobados con un ejecutable de prueba simulado**, sólo para confirmar que genera archivos TXT/JSON/XML y recorre casos. **No son resultados de k6 real ni métricas de rendimiento**.
- La ejecución completa **Selenium/Behave**, **k6 real** y **Jenkins** requiere tu equipo Windows. No se declaran como aprobadas hasta ejecutar allí.

Los XML heredados permanecen en `evidencias_previas/` como línea base anterior; no atribuirlos al estado corregido. Consulta `INFORME_CORRECCIONES.md` para detalles y guía.

## 7. Interpretación para el docente

- **Semana 8**: automatización de pruebas funcionales y de aceptación: pasos, datos, resultados y evidencia.
- **Semana 9**: pruebas funcionales adicionales para preparar las no funcionales, seguridad HTTP y DOM, rendimiento y estrés con k6.
- **Jenkins**: ejecución repetible por etapas, consolidación JUnit y evidencias archivadas. Una prueba diseñada **no equivale** a prueba ejecutada.

**Recomendación:** conserva el archivo original `README.md` como historial y utiliza este manual para la ampliación de semanas 8 y 9.
