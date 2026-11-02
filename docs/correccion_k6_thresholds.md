# Corrección de lectura de umbrales Grafana k6 0.54

## Problema detectado

Al ejecutar `python ci\execute.py unit
python ci\execute.py performance --smoke`, los 20 escenarios R01–R10
aparecían como `FALLÓ`, aunque la consola de k6 informaba un 100 % de checks,
0 % de errores y tiempos p95 inferiores al límite. Por ejemplo, en R01 se
observaron 8,46 ms para Aula Nova y 4,76 ms para TiendaDemo, frente a 500 ms.

El problema estaba en `ci/execute.py`: interpretaba el booleano `false` en
`metrics.*.thresholds` como fracaso. En **el esquema legacy de `--summary-export`
(k6 0.54)** es exactamente al revés: `false` significa que **NO** se violó el
umbral y `true` significa que sí se violó.

## Cambios implementados

- `ci/execute.py`: lectura correcta de umbrales booleanos antiguos; conserva
  compatibilidad con registros `{"ok": true/false}` y falla de forma segura
  cuando no hay umbrales o el formato es desconocido.
- Se elimina el resumen JSON antiguo de cada caso antes de lanzar una nueva
  ejecución para impedir reutilizar accidentalmente métricas obsoletas.
- `ci/tests/test_k6_thresholds.py`: nueve pruebas unitarias y de integración simulada para prevenir
  inversiones del significado de PASS/FAIL. Se ejecutan automáticamente en la
  fase `unit` y el Quality Gate exige su resultado.
- **No se han modificado los límites**, escenarios, duración ni VUs de los
  scripts de k6.

## Aplicar únicamente el parche

Extraer `Parche_K6_Semana11.zip` en el directorio que **contiene** `ci/`.
Por ejemplo, dentro de `calidad-ci-semana11`, ejecutar:

```powershell
Expand-Archive -Path "$env:USERPROFILE\Downloads\Parche_K6_Semana11.zip" -DestinationPath . -Force
python -m unittest discover -s ci/tests -p 'test_k6_thresholds.py' -v
python ci\execute.py performance --smoke
```

No hace falta reconstruir las imágenes: `ci/execute.py` se ejecuta en Windows.
`--smoke` es diagnóstico y su `reports/status/k6-*-rendimiento.json` seguirá
marcado como no validación completa hasta ejecutar `performance` sin `--smoke`.

Para **ver métricas** de un JSON de k6 0.54 desde PowerShell, se debe acceder a
los campos `.value` y `.'p(95)'`, no `.values.rate`.

## Verificación y límites

Las pruebas de regresión del parser se pueden ejecutar sin Docker. Las mediciones
reales de rendimiento y los 20 smoke deben volver a ejecutarse en el equipo con
Docker. El error previo de la capa de reportes no prueba un defecto de la app;
sin embargo, una prueba futura podría fallar legítimamente y el Quality Gate
debe mostrarla.

Referencia histórica del comportamiento legacy:
https://community.grafana.com/t/summary-export-command/98472
