const test = require("node:test");
const assert = require("node:assert/strict");
const { createServer } = require("./server");

test("API y aplicación web del aula virtual", async (suite) => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const baseUrl = `http://127.0.0.1:${server.address().port}`;

  suite.after(() => new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve())));

  await suite.test("entrega la página de inicio y cabeceras de seguridad", async () => {
    const response = await fetch(baseUrl);
    assert.equal(response.status, 200);
    assert.match(response.headers.get("content-type"), /text\/html/);
    assert.equal(response.headers.get("x-frame-options"), "DENY");
    assert.match(await response.text(), /Aula Nova/);
  });

  await suite.test("expone el perfil y los cuatro cursos con calificaciones", async () => {
    const [studentResponse, coursesResponse] = await Promise.all([
      fetch(`${baseUrl}/api/student`), fetch(`${baseUrl}/api/courses`),
    ]);
    const profile = await studentResponse.json();
    const data = await coursesResponse.json();
    assert.equal(profile.student.code, "202310458");
    assert.equal(data.courses.length, 4);
    assert.deepEqual(Object.keys(data.courses[0].grades), ["t1", "t2", "t3", "final"]);
  });

  await suite.test("envía mensajes y los devuelve en la bandeja", async () => {
    const response = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: "calc-201", subject: "Consulta de práctica", body: "¿Podría explicar el ejercicio número tres?" }),
    });
    assert.equal(response.status, 201);
    const { message } = await response.json();
    assert.equal(message.teacher, "Dra. Elena Torres");
    assert.equal((await (await fetch(`${baseUrl}/api/messages`)).json()).messages.length, 1);
  });

  await suite.test("rechaza mensajes incompletos y cursos desconocidos", async () => {
    const response = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: "desconocido", subject: "Ok", body: "No" }),
    });
    assert.equal(response.status, 400);
    assert.equal((await response.json()).error.length > 0, true);
  });

  await suite.test("rechaza JSON inválido y solicitudes demasiado grandes", async () => {
    const invalid = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{",
    });
    assert.equal(invalid.status, 400);

    const oversized = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body: "x".repeat(17 * 1024) }),
    });
    assert.equal(oversized.status, 413);
  });

  await suite.test("rechaza secuencias UTF-8 invalidas en la URL", async () => {
    // URL sintácticamente válida para un cliente HTTP Go/k6;
    // el servidor debe rechazar su codificación UTF-8 inválida.
    const response = await fetch(`${baseUrl}/%ED%A0%80`);
    assert.equal(response.status, 400);
  });

  await suite.test("no expone archivos fuera de la aplicación", async () => {
    const response = await fetch(`${baseUrl}/..%2Fbackend%2Fserver.js`);
    assert.equal(response.status, 403);
  });
});
