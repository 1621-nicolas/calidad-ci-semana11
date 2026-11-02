# Proyecto TiendaDemo

Estructura de proyecto para pruebas funcionales y de aceptación de la aplicación TiendaDemo.

## Estructura

- `app/` — aplicación bajo prueba
- `pages/` — clases Page Object Model
- `tests/` — pruebas funcionales Selenium organizadas por rango TC
- `features/` — escenarios Behave organizados por rango TC
- `utils/` — utilidades compartidas

## Configuración

1. Instala dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecuta la suite funcional con unittest:

```bash
python -m unittest -v
python -m unittest discover -v
python -m unittest discover -s tests
```

La suite se distribuye en `test_tc01_tc05.py`, `test_tc06_tc13.py`, `test_tc14_tc19.py`, `test_tc20_tc31.py` y `test_tc32_tc41.py`.

3. Ejecuta las pruebas de aceptación con Behave:

```bash
behave features
```

Los escenarios y sus steps se organizan en los rangos TC-01 a TC-05, TC-06 a TC-13, TC-14 a TC-19, TC-20 a TC-31 y TC-32 a TC-41. Las definiciones reutilizadas se mantienen en `features/steps/common_steps.py`.

## Jenkins

### Qué se configuró

Jenkins ejecuta automáticamente, en el mismo build, las pruebas funcionales `unittest` y los escenarios de aceptación Behave. También instala las dependencias, genera informes JUnit y archiva los reportes en `reports/`.

La instancia configurada está en `http://localhost:8080` y contiene el job **TiendaDemo**. El job se creó con un pipeline inline (guardado en Jenkins) que apunta a la carpeta local del proyecto y a la instalación local de Python. No está conectado a Git ni usa el `Jenkinsfile` del proyecto. El archivo `Jenkinsfile` se añadió para cuando se conecte el proyecto a un repositorio remoto.

### Paso a paso de la configuración realizada

1. **Preparar el equipo.** Se comprobó que Jenkins estuviera instalado y funcionando en Windows, y que estuvieran disponibles Python 3 y Google Chrome. Selenium Manager obtiene el controlador de Chrome; las pruebas se ejecutan en modo headless.
2. **Instalar los plugins de Jenkins.** En **Manage Jenkins > Plugins**, se instalaron los plugins **Pipeline** y **JUnit**, necesarios para ejecutar el pipeline y mostrar los resultados de las pruebas.
3. **Resolver la conexión segura al catálogo de plugins.** Inicialmente, Java rechazó el certificado TLS al descargar plugins. Se verificó que el certificado raíz `emSign Root CA - G1` ya era de confianza en Windows, se agregó al almacén de confianza Java usado por Jenkins y se reinició el servicio. No se desactivó la validación TLS.
4. **Crear el job.** En el inicio de Jenkins se seleccionó **New Item**, se escribió `TiendaDemo`, se eligió **Pipeline** y se guardó.
5. **Configurar el pipeline local.** En **Configure > Pipeline**, se eligió **Pipeline script**. El script quedó guardado directamente en Jenkins, con la ruta de esta carpeta y la ruta del ejecutable Python instalado en este equipo. Se usa esta modalidad porque el proyecto todavía no tiene un repositorio Git remoto.
6. **Instalar dependencias y preparar informes.** La primera etapa del pipeline elimina los XML de ejecuciones anteriores, crea `reports/unittest` y `reports/behave`, e instala los paquetes de `requirements.txt`. Se agregó `unittest-xml-reporting` a ese archivo para generar informes JUnit de `unittest`.
7. **Ejecutar las suites.** Una etapa corre `xmlrunner discover -s tests`; otra corre Behave sobre `features` con salida JUnit. Los errores de una suite no impiden que se intente ejecutar la otra.
8. **Publicar los resultados.** Al finalizar, incluso si hay pruebas fallidas, Jenkins procesa los XML como resultados JUnit y archiva los archivos de `reports/`. La carpeta `reports/` se agregó a `.gitignore` para no incluir resultados generados en el control de versiones.
9. **Probar el job.** Se inició **Build Now** y se verificó que el build #3 ejecutara las dos suites y archivara los informes. Jenkins informó 51 pruebas `unittest` (9 fallidas) y 50 escenarios Behave (41 pasaron y 9 fallaron): 83 aprobados y 18 fallidos en total. El job funciona, pero el resultado queda **FAILURE** hasta corregir las pruebas que fallan.

### Cómo ejecutar y revisar el job

1. Abre [Jenkins](http://localhost:8080) y entra al job **TiendaDemo**.
2. Selecciona **Build Now** para iniciar una ejecución.
3. Abre el número del build más reciente y revisa **Console Output** si necesitas ver los comandos o diagnosticar un error.
4. En **Test Result**, consulta las pruebas aprobadas y fallidas. En **Artifacts**, descarga los XML archivados.

También puedes ejecutar las suites localmente desde la carpeta del proyecto:

```bash
python -m unittest discover -s tests
behave features
```

### Limitaciones y siguiente paso para automatizar con Git

El job actual depende de la carpeta local de este equipo y se inicia manualmente. No se ejecuta al hacer push, y otros equipos no pueden usar esa ruta local. Para habilitar builds desde Git:

1. Publica el proyecto en un repositorio Git remoto.
2. En la configuración del job, cambia el tipo de definición a **Pipeline script from SCM**.
3. Selecciona Git, introduce la URL del repositorio y las credenciales necesarias.
4. Indica la rama y la ruta `Jenkinsfile`; configura un webhook o un disparador de sondeo si quieres que los pushes inicien builds.
5. Asegúrate de que el agente de Jenkins tenga Python 3, Chrome y acceso a Internet para instalar las dependencias.

El `Jenkinsfile` del proyecto contiene las etapas multiplataforma para esta modalidad: utiliza `py -3` en Windows y `python3` en Linux, instala dependencias, ejecuta ambas suites y publica sus informes. Debe validarse al conectar el repositorio a SCM, ya que el job local actual ejecuta una copia inline distinta.
