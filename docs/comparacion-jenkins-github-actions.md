# Comparación Jenkins vs GitHub Actions — Semana 11

| Criterio | Jenkins | GitHub Actions |
|---|---|---|
| Instalación | Requiere servidor, plugins y agente con Docker | Runner Linux hospedado por GitHub |
| GitHub | SCM + Poll SCM/webhook | Eventos push, PR, manual integrados |
| Definición | `Jenkinsfile` (Groovy declarativo) | `.github/workflows/ci.yml` (YAML) |
| Suites | `python ci/execute.py <fase>` | **Exactamente el mismo comando** |
| Entorno | `docker compose`, mismas imágenes | `docker compose`, mismas imágenes |
| TestLink | Clave Jenkins Credentials | Clave GitHub Actions Secrets |
| Evidencias | `junit` + `archiveArtifacts` | `upload-artifact` |
| Fallos | `catchError`, quality gate final | `continue-on-error`, quality gate final |
| Tiempo | Depende de recursos del agente Windows/servidor | Depende de runner de GitHub y cuotas disponibles |
| Mantenimiento | Administrar plugins, servidor y agentes | Mantener acciones, versiones y secretos |

## Respuestas a las preguntas del docente
1. **Más sencilla de configurar:** GitHub Actions cuando ya existe un repositorio GitHub y runners disponibles.
2. **Menor complejidad inicial:** GitHub Actions evita instalar servidor propio.
3. **Ventaja de Jenkins:** mayor control de agentes, red, hardware y plugins en instalaciones privadas.
4. **Ventaja de Actions:** integración nativa de eventos y PR, sin gestionar el servidor.
5. **Aporte de Docker:** dependencias, navegador y servicios encapsulados; reproducibilidad.
6. **Dificultad de TestLink:** configurar API XML-RPC, claves, derechos de autor, proyecto/plan y vinculación de versiones/casos. Requiere verificarlo contra el servidor real.
7. **Resultados:** permiten detectar regresiones, auditar ejecución y dar trazabilidad.
8. **Falla crítica en PR:** quality gate devuelve error y debe bloquearse el merge con protección de rama.
9. **Proyecto real:** elegiría Actions por menor mantenimiento en GitHub, o Jenkins si las pruebas requieren red interna o hardware especial.
10. **Mejora de calidad:** pruebas repetibles y comparables antes de integrar cambios, diagnósticos y evidencia histórica.

**Nota:** Comparación de capacidades y configuración, no una medición experimental de tiempos; los tiempos reales deben registrarse tras ejecutar ambos pipelines.
