# Registro de validación del proyecto ampliado

**Entorno de revisión:** contenedor Linux (no es el agente Jenkins Windows del usuario).

| Verificación | Resultado |
|---|---|
| Extracción de RAR5 e inventario original | Correcto: TiendaDemo, Selenium, Behave, Jenkinsfile y reportes existentes. |
| Análisis sintáctico Python de los scripts nuevos | Correcto: 7 archivos. |
| Análisis sintáctico JavaScript de los scripts k6 | Correcto: 3 archivos, mediante `node --check`. |
| Semana 9: HTTP local con `unittest` | **10/10 aprobados**. |
| Convertidor JSON de k6 a JUnit XML (prueba simulada) | Correcto: produce resultado de éxito o fallo según entrada. |
| Selenium / Behave | **No ejecutado en este entorno**: dependencias no instaladas y sin conectividad para `pip install`. |
| Grafana k6 | **No ejecutado en este entorno**: ejecutable k6 no disponible. |
| Pipeline Jenkins | **No ejecutado**: instancia Jenkins del usuario no disponible en este entorno. |

Se han preservado los XML de la ejecución previa del proyecto en `evidencias_previas/` para evitar confundirlos con los reportes nuevos.

**Aviso:** la aplicación contiene casos intencionalmente fallidos en `test_fails.py` y `tc_fails.feature`. Jenkins puede terminar en `FAILURE` por defectos reales incluso cuando se configure correctamente.

## Revisión posterior: fallos corregidos

Los defectos existentes en esta primera revisión fueron corregidos en la versión actual, según `INFORME_CORRECCIONES.md`. Esta primera tabla describe la línea base anterior, no los resultados finales de la nueva versión. El navegador probó 12/12 regresiones, los 10 controles HTTP y 7 casos JUnit con Python; falta validar las suites Selenium/Behave y k6 reales en Jenkins/Windows.
