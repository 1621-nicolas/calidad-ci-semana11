# Informe técnico y evidencias — Semana 11

## Situación problemática
TiendaDemo y Aula Nova tenían pruebas ejecutables por separado. La Semana 11 exige un repositorio Git, dos pipelines de CI con Docker compartido y resultados centralizados en TestLink.

## Solución desarrollada
Se consolidaron los proyectos preservando sus pruebas originales. `ci/execute.py` ejecuta las fases Docker, publica estados y convierte k6 JSON en JUnit XML. Jenkins y GitHub Actions consumen ese ejecutor. El script `ci/testlink_sync.py` mantiene la matriz de casos y remite las ejecuciones por XML-RPC cuando se configuren credenciales reales.

## Resultados realmente verificados en este entorno
- `npm test` en Aula Nova: **7 verificaciones del runner de Node, 0 fallidas** (suite más seis subpruebas).
- `node --test backend/functional.week9.test.js`: **25 de 25 aprobadas**.
- Validación sintáctica de scripts JavaScript k6 por `node --check`: completada.
- Python `py_compile` para scripts de CI: completada.
- Matriz de trazabilidad: generada con IDs únicos, incluidas 41 pruebas Selenium y 41 Playwright.

## Pendiente de validación real — no declarar aprobado
- Los contenedores Docker y las imágenes externas **no pudieron ejecutarse** en este entorno: Docker no está instalado.
- Las 41 pruebas Playwright se intentaron ejecutar con Chromium local, pero el navegador del entorno bloqueó toda navegación con `ERR_BLOCKED_BY_ADMINISTRATOR`; no es un resultado sobre TiendaDemo.
- Se requiere ejecutar las 41 pruebas Selenium y 41 Playwright en los contenedores en el equipo del usuario o CI.
- Las 60 pruebas k6 de ambas aplicaciones están codificadas, pero **no hay métricas reales** sin Docker/k6. R09 debe correr 30 minutos por aplicación.
- La sincronización con TestLink no puede verificarse sin servidor/API, usuario y clave.
- Los pipelines GitHub Actions/Jenkins deben ejecutarse en sus plataformas para obtener sus capturas, marcas de tiempo, console logs y reportes.
- La demostración de una ejecución fallida controlada debe hacerse en una rama de prueba y revertirse. No alterar reportes artificialmente.

## Evidencias a capturar en Windows/GitHub (nombres sugeridos)
1. `E01-github-repo.png` — repositorio y ramas.
2. `E02-docker-ps.png` — aplicaciones, Selenium y k6 en Docker.
3. `E03-actions-run.png` — workflow con todas sus fases y enlace.
4. `E04-jenkins-stages.png` — pipeline Jenkins y duración.
5. `E05-selenium-junit.png` — 41 resultados Selenium.
6. `E06-playwright-junit.png` — 41 resultados Playwright.
7. `E07-k6-r09-metricas.png` — R09 sostenido 30 min, p95, errores y checks.
8. `E08-testlink-resultados.png` — TestLink con resultados actualizados automáticamente.
9. `E09-quality-gate-falla.png` — fase fallida de prueba controlada + posterior recuperación.
10. `E10-comparacion.png` — tabla comparativa y tiempos reales de ambos pipelines.

## Criterios de aprobación
El quality gate exige las suites principales presentes y correctas, reportes JUnit válidos y, cuando `REQUIRE_TESTLINK=1`, resultados sincronizados. No se considera aprobado lo que no se ha ejecutado.
