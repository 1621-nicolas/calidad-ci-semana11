# Corrección de seguridad S02: URL inválida en k6

## Problema reproducido

Los dos scripts k6 usaban `/%ZZ` y exigían HTTP 400. Sin embargo, el cliente HTTP
Go/k6 rechaza `%ZZ` antes de emitir la petición (`invalid URL escape "%ZZ"`).
Esto no evalúa la validación del servidor: falla el caso por la capa cliente.

## Corrección sin reducir el criterio de aceptación

- Ambos scripts S02 ahora envían `/%ED%A0%80`, secuencia de porcentajes
  sintácticamente correcta como URL, pero inválida como UTF-8 (surrogate).
- **El criterio sigue siendo HTTP 400** en ambos proyectos, sin aceptar un 404,
  200 u otro código como aprobación.
- `tienda-demo/scripts/qa_server.py` valida estrictamente la decodificación UTF-8
  y devuelve 400 si recibe bytes inválidos. Aula Nova ya lo hacía.
- Nuevas pruebas automatizadas verifican el rechazo por ambas aplicaciones.
- No se modificaron los umbrales de k6 ni el Quality Gate.

## Aplicar en Windows

Desde la raíz de `calidad-ci-semana11` y con Docker Desktop activo:

```powershell
Expand-Archive -Path "$env:USERPROFILE\Downloads\Parche_S02_Semana11.zip" -DestinationPath . -Force
# Reconstruir TiendaDemo (servidor corregido) y Aula Nova (nueva prueba Node).
docker compose up -d --build --wait aula-nova tienda-demo
# Se ejecutan de nuevo todas las suites de seguridad, incluyendo S02.
python ci\execute.py security
# El parser se añadía a la fase unit en el parche anterior; repetirla genera su estado.
python ci\execute.py unit
python ci\execute.py quality
```

El directorio `tests/k6/` está montado como volumen de solo lectura en el
contenedor k6, así que sus scripts se actualizan sin reconstruir la imagen k6.
Recrear las imágenes de las aplicaciones permite incluir sus pruebas nuevas.
Conservar los XML/JSON reales de la ejecución y el resultado de los Quality Gates.

## Límite de validación

Se comprobaron localmente los servidores y la sintaxis de la URL mediante
peticiones HTTP válidas; las ejecuciones Docker/k6 deberán validarse en el equipo
que tiene Docker Desktop. Un error de seguridad real seguirá fallando.
