const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const APP_DIR = path.join(__dirname, "..", "app");
const MAX_BODY_BYTES = 16 * 1024;

const student = {
  firstName: "María",
  lastName: "García López",
  code: "202310458",
  email: "maria.garcia@universidad.edu",
  program: "Ingeniería de Sistemas",
  faculty: "Facultad de Ingeniería",
  cycle: "VI ciclo",
};

const courses = [
  { id: "calc-201", code: "MAT-201", name: "Cálculo diferencial", teacher: "Dra. Elena Torres", schedule: "Lun · Mié · 10:00 a. m.", room: "B-204", credits: 4, average: 16.8, grades: { t1: 17, t2: 16, t3: 18, final: 17.2 } },
  { id: "prog-105", code: "INF-105", name: "Fundamentos de programación", teacher: "Mg. Carlos Mendoza", schedule: "Mar · Jue · 8:00 a. m.", room: "Lab. 3", credits: 4, average: 18.2, grades: { t1: 18, t2: 19, t3: 17, final: 18.2 } },
  { id: "met-220", code: "INV-220", name: "Metodología de investigación", teacher: "Dra. Lucía Herrera", schedule: "Mar · Vie · 2:00 p. m.", room: "C-301", credits: 3, average: 15.6, grades: { t1: 15, t2: 16, t3: null, final: 15.5 } },
  { id: "bd-210", code: "INF-210", name: "Bases de datos", teacher: "Mg. Andrés Paredes", schedule: "Lun · Mié · 4:00 p. m.", room: "Lab. 2", credits: 4, average: 15.2, grades: { t1: 16, t2: 14, t3: 16, final: 15.2 } },
];

const messages = [];
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
};

function sendJson(response, status, body) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  });
  response.end(JSON.stringify(body));
}

function readJson(request) {
  return new Promise((resolve, reject) => {
    let body = "";
    let oversized = false;
    request.on("data", (chunk) => {
      if (oversized) return;
      body += chunk;
      if (Buffer.byteLength(body) > MAX_BODY_BYTES) {
        oversized = true;
        reject(Object.assign(new Error("El mensaje supera el tamaño permitido."), { status: 413 }));
      }
    });
    request.on("end", () => {
      if (oversized) return;
      try {
        resolve(JSON.parse(body));
      } catch {
        reject(Object.assign(new Error("El cuerpo debe ser JSON válido."), { status: 400 }));
      }
    });
    request.on("error", reject);
  });
}

function serveStatic(response, pathname) {
  let requestedPath;
  try {
    requestedPath = pathname === "/" ? "index.html" : decodeURIComponent(pathname.slice(1));
  } catch {
    sendJson(response, 400, { error: "La ruta contiene una codificación inválida." });
    return;
  }
  const filePath = path.resolve(APP_DIR, requestedPath);
  if (!filePath.startsWith(`${APP_DIR}${path.sep}`)) {
    sendJson(response, 403, { error: "Acceso denegado." });
    return;
  }

  fs.readFile(filePath, (error, content) => {
    if (error) {
      sendJson(response, error.code === "ENOENT" ? 404 : 500, { error: error.code === "ENOENT" ? "No encontrado." : "No se pudo leer el recurso." });
      return;
    }
    response.writeHead(200, {
      "Content-Type": contentTypes[path.extname(filePath)] || "application/octet-stream",
      "X-Content-Type-Options": "nosniff",
      "Content-Security-Policy": "default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "X-Frame-Options": "DENY",
    });
    response.end(content);
  });
}

function createServer() {
  return http.createServer(async (request, response) => {
    const url = new URL(request.url, "http://localhost");
    if (request.method === "GET" && url.pathname === "/api/student") {
      sendJson(response, 200, { student });
      return;
    }
    if (request.method === "GET" && url.pathname === "/api/courses") {
      sendJson(response, 200, { courses });
      return;
    }
    if (request.method === "GET" && url.pathname === "/api/messages") {
      sendJson(response, 200, { messages });
      return;
    }
    if (request.method === "POST" && url.pathname === "/api/messages") {
      try {
        const body = await readJson(request);
        const payload = body && typeof body === "object" && !Array.isArray(body) ? body : {};
        const course = courses.find((item) => item.id === payload.courseId);
        const subject = typeof payload.subject === "string" ? payload.subject.trim() : "";
        const content = typeof payload.body === "string" ? payload.body.trim() : "";
        if (!course || subject.length < 3 || subject.length > 100 || content.length < 5 || content.length > 1000) {
          sendJson(response, 400, { error: "Selecciona un curso e ingresa un asunto (3–100 caracteres) y un mensaje (5–1000 caracteres)." });
          return;
        }
        const message = {
          id: `msg-${Date.now()}-${messages.length + 1}`,
          courseId: course.id,
          courseName: course.name,
          teacher: course.teacher,
          teacherInitials: course.teacher.split(" ").filter((part) => /^[A-ZÁÉÍÓÚ]/.test(part)).slice(-2).map((part) => part[0]).join(""),
          subject,
          body: content,
          createdAt: new Date().toISOString(),
        };
        messages.push(message);
        sendJson(response, 201, { message });
      } catch (error) {
        if (!response.headersSent && !response.destroyed) {
          sendJson(response, error.status || 400, { error: error.message || "No se pudo procesar la solicitud." });
        }
      }
      return;
    }
    if (request.method === "GET" && !url.pathname.startsWith("/api/")) {
      serveStatic(response, url.pathname);
      return;
    }
    sendJson(response, 404, { error: "Ruta no encontrada." });
  });
}

if (require.main === module) {
  const port = Number(process.env.PORT || 3000);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    console.error("PORT debe ser un número entre 1 y 65535.");
    process.exitCode = 1;
  } else {
    createServer().listen(port, "0.0.0.0", () => {
      console.log(`Aula Nova disponible en http://localhost:${port}`);
    });
  }
}

module.exports = { createServer };
