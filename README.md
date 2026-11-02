# Calidad y Pruebas de Software — Semana 11

**Proyecto de integración continua de TiendaDemo + Aula Nova**. Reúne los trabajos de las semanas 8 y 9 en **un único repositorio** y ejecuta **las mismas fases Docker en Jenkins y GitHub Actions**. No incluye secretos reales.

## 1. Qué contiene

- `tienda-demo/`: aplicación corregida, 41 pruebas Selenium TC01-TC41, Behave/UAT, regressiones, pruebas funcionales de semanas 8 y 9, servidor QA.
- `aula-nova/`: aplicación con Node.js, 6 subpruebas originales y 25 casos funcionales adicionales F01-F25.
- `tests/playwright/`: 41 escenarios Playwright TC01-TC41 + una prueba DOM adicional S06 de Aula Nova.
- `tests/k6/aula-nova/`: 10 escenarios R01–R10, 10 E01–E10, 10 S01–S10 conforme a Semana 9.
- `tests/k6/tienda-demo/`: otros 30 escenarios para el servidor HTTP estático de TiendaDemo. **Ambas suites k6 se ejecutan**; no confundir pruebas de archivos estáticos con pruebas de la API de Aula Nova.
- `docker/`, `docker-compose.yml`: imágenes y servicios para las dos apps, Selenium Grid, ejecutores Selenium/Playwright y k6.
- `Jenkinsfile`, `.github/workflows/ci.yml`: dos pipelines que llaman a `python ci/execute.py <fase>`.
- `ci/quality_gate.py`: gate que falla ante casos ausentes, pruebas fallidas y reportes XML inválidos.
- `ci/testlink_sync.py`: integración real TestLink XML-RPC para registrar casos y resultados (requiere claves).
- `docs/matriz_trazabilidad.csv`: IDs de casos, requisito, suite, herramienta y resultado esperado.

## 2. Requisitos en Windows

- Docker Desktop ejecutándose con motor Linux y capacidad para varias imágenes de navegador.
- Git y Python 3.12 disponibles en PATH.
- Jenkins instalado y accesible en `http://localhost:8080` para el pipeline local.
- Cuenta GitHub y repositorio **privado** para publicar el código.
- TestLink con API XML-RPC habilitada, permisos para crear proyecto/plan/casos y una Developer Key.

**No necesitas instalar Selenium, Playwright ni k6 directamente en Windows** si utilizas Docker. Docker instala sus dependencias en imágenes separadas. El `Jenkinsfile` asume agente **Windows** con `python` y `docker compose` disponibles.

## 3. Ejecución local reproducible

Desde la raíz del repositorio, en PowerShell:

```powershell
python ci/execute.py build
python ci/execute.py environment
python ci/execute.py unit
python ci/execute.py selenium
python ci/execute.py playwright
python ci/execute.py functional
python ci/execute.py uat
python ci/execute.py performance
python ci/execute.py stress
python ci/execute.py security
python ci/execute.py reports
python ci/execute.py quality
python ci/execute.py cleanup
```

Para diagnóstico muy breve (no sirve como evidencia de los 10 casos completos):

```powershell
python ci/execute.py performance --smoke
python ci/execute.py stress --smoke
```

El quality gate **no aprueba** smoke como sustituto del conjunto completo. El caso R09 de rendimiento se ejecuta durante 30 minutos cuando no usas `--smoke`.

**Aula Nova:** `http://localhost:3000`. **TiendaDemo:** `http://localhost:8008`.

## 4. GitHub y GitHub Actions

1. Crea un repositorio vacío, preferentemente privado, llamado `calidad-ci-semana11` desde GitHub. No subas `.env`, claves ni reportes generados.
2. En la raíz ejecuta:

```powershell
git init
git add .
git commit -m "Semana 11: pipelines QA, Docker, TestLink"
git branch -M main
git remote add origin https://github.com/1621-nicolas/calidad-ci-semana11.git
git push -u origin main
```

3. Abre **Actions → Calidad - Semana 11**. El workflow se inicia en `push` a `main` o `develop`, `pull_request` a `main` y manualmente.
4. Para proteger la rama `main`, configura la regla de protección que requiera **ci** (nombre del job de GitHub Actions) antes de permitir merges.
5. En **Settings → Secrets and variables → Actions**, registra: secreto `TESTLINK_DEVKEY`; variables `TESTLINK_URL`, `TESTLINK_PROJECT`, `TESTLINK_PLAN`, `TESTLINK_AUTHOR_LOGIN`. No pongas las claves en `.yml`.

> Se entregan scripts de CI listos para subir. Este ZIP no implica que se haya creado o ejecutado un repositorio remoto.

## 5. Jenkins

En el job Jenkins:
1. **Configure → Pipeline → Definition: Pipeline script from SCM**.
2. SCM: **Git**, URL del repositorio privado, credentials si corresponde, rama `*/main`, **Script Path: Jenkinsfile**.
3. Jenkins necesita plugins `Pipeline`, `Git`, `JUnit`, `Credentials` y `Docker Pipeline` (el script usa Docker CLI, no es obligatorio que emplee `docker.build`).
4. Habilita Docker Desktop y asegúrate de que el usuario que ejecuta Jenkins puede usar `docker compose version`.
5. Selecciona **Build with Parameters**. Por defecto ejecutará todas las suites y los 60 casos k6 (30 por aplicación), incluyendo dos R09 de 30 minutos.
6. El `Jenkinsfile` usa `pollSCM('H/5 * * * *')` para detectar cambios cuando Jenkins está en localhost. Se puede sustituir por webhook seguro si Jenkins dispone de URL pública correctamente protegida.
7. `REQUIRE_TESTLINK` permite exigir el registro real de resultados, siempre que exista una credencial Jenkins Secret Text con ID `testlink-devkey` y las variables de TestLink estén configuradas en Jenkins.

Para ver pruebas: **TiendaDemo → Build → Test Result / Artifacts / Console Output**.

## 6. TestLink (integración de verdad, no capturas ficticias)

1. Configura un TestLink propio con API XML-RPC (o un servidor autorizado). Puede usarse `docker-compose.testlink.yml` únicamente en laboratorio aislado; su imagen antigua no está actualizada ni es apta para uso público.
2. Activa API XML-RPC y crea una Developer Key de usuario con permisos de proyecto, casos y ejecuciones.
3. Define `TESTLINK_URL` (URL completa a `lib/api/xmlrpc/v1/xmlrpc.php` según tu instalación), `TESTLINK_DEVKEY`, `TESTLINK_PROJECT`, `TESTLINK_PLAN` y `TESTLINK_AUTHOR_LOGIN`. Variables en entorno o Jenkins Credentials/GitHub Secrets.
4. Ejecuta después de generar JUnit:

```powershell
python ci/execute.py testlink
```

5. En TestLink comprueba proyecto, suites, plan, build y casos con estado Passed/Failed/Blocked. **No declarar la integración completa hasta confirmar el resultado en un servidor real**.

La matriz `docs/matriz_trazabilidad.csv` se genera de nuevo con `python ci/make_matrix.py`. El sincronizador es idempotente por nombre; diferentes versiones de TestLink pueden requerir ajustar sus opciones XML-RPC.

### Arranque opcional TestLink local

Copia `.env.example` a `.env`, cambia las contraseñas `CHANGE_ME` por valores fuertes, y ejecuta en laboratorio:

```powershell
Copy-Item .env.example .env
# Editar .env con contraseñas privadas
# Advertencia: imagen TestLink legacy sin mantenimiento de seguridad
docker compose -f docker-compose.yml -f docker-compose.testlink.yml --profile testlink up -d testlink-db testlink
```

Luego entra a `http://localhost:8090`. La conectividad y las rutas XML-RPC dependen de la versión efectiva de TestLink instalada.

## 7. Qué se publica y cómo se comprueba

- `reports/**/*.xml`: JUnit para Jenkins, GitHub Actions y TestLink.
- `reports/k6/aula-nova/<grupo>/<caso>.json`: resumen real de k6 y umbrales.
- `reports/status/*.json`: estado de cada fase (señala suites omitidas o fallidas).
- `reports/console/*.txt`: stdout/stderr.
- En GitHub, descarga el artifact `quality-reports-<número>`; en Jenkins abre **Archived Artifacts**.
- Los casos fallidos quedan en rojo; no se borran ni se aceptan mediante `allowEmptyResults`.

## 8. Entrega según la rúbrica

Ver `docs/entregables.md`, `docs/informe-tecnico.md` y `docs/comparacion-jenkins-github-actions.md`. Las **capturas reales**, la **ejecución en GitHub/Jenkins** y la **prueba de sincronización con TestLink** son evidencias que deben capturarse desde los servicios conectados, no falsificarse.

## 9. Diagnóstico previo

```powershell
python ci/preflight.py
```

Antes de la exposición, consulta `docs/demostracion-fallo-controlado.md` para mostrar un fallo auténtico y su corrección en una rama temporal.
