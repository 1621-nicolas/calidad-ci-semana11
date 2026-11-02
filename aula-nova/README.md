# Aula Nova — Aula virtual universitaria

Aplicación de demostración para estudiantes universitarios con perfil académico, cursos matriculados, calificaciones por evaluación y comunicación con docentes.

## Requisitos

- Node.js 18 o posterior (utiliza módulos nativos; no requiere dependencias adicionales).

## Ejecución

Desde la raíz del proyecto:

```powershell
npm start
```

Abre [http://localhost:3000](http://localhost:3000). Para cambiar el puerto, define `PORT` antes de iniciar el servidor.

## Estructura

- `app/`: interfaz web adaptable (HTML, CSS y JavaScript).
- `backend/`: servidor HTTP, API y pruebas automatizadas.

La API ofrece `GET /api/student`, `GET /api/courses`, `GET /api/messages` y `POST /api/messages`. El perfil, los cursos y las calificaciones son datos de demostración; los mensajes se mantienen en memoria mientras el servidor está activo.

## Pruebas

```powershell
npm test
```

Las pruebas comprueban la entrega de la interfaz, los datos académicos, el envío y validación de mensajes y el bloqueo de acceso a archivos fuera de la aplicación.
