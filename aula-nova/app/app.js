const coursePalette = ["purple", "green", "amber", "blue"];
const courseIcons = ["∑", "⌘", "⌬", "◈"];
let courses = [];
let messages = [];
let toastTimer;

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[character]);

async function request(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "No se pudo completar la solicitud.");
  return data;
}

function renderCourseRow(course, index) {
  const progress = Math.round(Math.min(Number(course.average) * 5, 100) / 10) * 10;
  return `<article class="course-row">
    <div class="course-symbol ${coursePalette[index % coursePalette.length]}">${courseIcons[index % courseIcons.length]}</div>
    <div class="course-main"><strong>${escapeHtml(course.name)}</strong><span>${escapeHtml(course.teacher)} · ${escapeHtml(course.schedule)}</span></div>
    <div class="course-grade"><strong>${Number(course.average).toFixed(1)}</strong><span>Promedio</span><div class="course-progress"><i class="width-${progress}"></i></div></div>
  </article>`;
}

function renderCourses() {
  document.querySelector("#dashboard-courses").innerHTML = courses.slice(0, 4).map(renderCourseRow).join("");
  document.querySelector("#all-courses").innerHTML = courses.map((course, index) => `
    <article class="course-tile">
      <div class="course-tile-top"><div class="course-symbol ${coursePalette[index % coursePalette.length]}">${courseIcons[index % courseIcons.length]}</div><span class="course-status">En curso</span></div>
      <h2>${escapeHtml(course.name)}</h2><p>${escapeHtml(course.code)} · ${escapeHtml(course.teacher)}</p>
      <div class="course-tile-meta"><div>Horario<strong>${escapeHtml(course.schedule)}</strong></div><div>Aula<strong>${escapeHtml(course.room)}</strong></div><div>Créditos<strong>${Number(course.credits)}</strong></div></div>
      <div class="course-tile-footer"><span>Promedio actual</span><strong>${Number(course.average).toFixed(1)} <small>/ 20</small></strong></div>
    </article>`).join("");

  document.querySelector("#grades-body").innerHTML = courses.map((course) => `
    <tr><td>${escapeHtml(course.name)}</td><td>${escapeHtml(course.teacher)}</td>
      ${["t1", "t2", "t3"].map((key) => `<td>${course.grades[key] === null ? "—" : Number(course.grades[key]).toFixed(1)}</td>`).join("")}
      <td class="final-grade">${Number(course.grades.final).toFixed(1)}</td><td>Aprobado</td></tr>`).join("");

  const select = document.querySelector("#message-course");
  select.innerHTML = '<option value="">Selecciona un curso</option>' + courses.map((course) =>
    `<option value="${escapeHtml(course.id)}">${escapeHtml(course.name)}</option>`).join("");
}

function renderMessages() {
  const container = document.querySelector("#messages-list");
  if (messages.length === 0) {
    container.innerHTML = '<div class="empty-messages">Todavía no has enviado mensajes. Si tienes una consulta, aquí puedes escribir a tus profesores.</div>';
    return;
  }
  container.innerHTML = [...messages].reverse().map((message) => `
    <article class="message-entry"><div class="message-avatar">${escapeHtml(message.teacherInitials)}</div>
      <div class="message-content"><strong>${escapeHtml(message.teacher)}</strong><div class="message-subject">${escapeHtml(message.subject)} · ${escapeHtml(message.courseName)}</div>
        <p>${escapeHtml(message.body)}</p><span>${new Intl.DateTimeFormat("es-PE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(message.createdAt))}</span></div>
    </article>`).join("");
}

function showToast(text) {
  const toast = document.querySelector("#toast");
  toast.textContent = text;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function showView(view) {
  const validViews = ["inicio", "cursos", "notas", "mensajes", "perfil"];
  if (!validViews.includes(view)) return;
  document.querySelectorAll(".view-panel").forEach((panel) => panel.classList.add("hidden"));
  document.querySelector(`#view-${view}`).classList.remove("hidden");
  document.querySelectorAll(".nav-link").forEach((link) => link.classList.toggle("active", link.dataset.view === view));
  document.querySelector("#breadcrumb-current").textContent = {
    inicio: "Inicio", cursos: "Mis cursos", notas: "Calificaciones", mensajes: "Mensajes", perfil: "Mi perfil",
  }[view];
  history.replaceState(null, "", `#${view}`);
  closeSidebar();
}

function openMessageDialog() {
  document.querySelector("#form-feedback").textContent = "";
  document.querySelector("#message-dialog").showModal();
}

function closeSidebar() {
  document.querySelector("#sidebar").classList.remove("open");
  document.querySelector("#sidebar-scrim").classList.remove("show");
  document.querySelector("#menu-toggle").setAttribute("aria-expanded", "false");
}

async function initialize() {
  try {
    document.querySelector("#today-label").textContent = new Intl.DateTimeFormat("es-PE", {
      weekday: "long", day: "numeric", month: "long", year: "numeric",
    }).format(new Date()).toLocaleUpperCase("es-PE");
    const [studentData, courseData, messageData] = await Promise.all([
      request("/api/student"), request("/api/courses"), request("/api/messages"),
    ]);
    courses = courseData.courses;
    messages = messageData.messages;
    document.querySelector("#sidebar-name").textContent = studentData.student.firstName + " " + studentData.student.lastName.split(" ")[0];
    document.querySelector("#profile-name").textContent = studentData.student.firstName + " " + studentData.student.lastName;
    document.querySelector("#profile-code").textContent = studentData.student.code;
    document.querySelector("#profile-email").textContent = studentData.student.email;
    renderCourses();
    renderMessages();
    const initialView = location.hash.slice(1);
    showView(initialView || "inicio");
  } catch (error) {
    document.querySelector(".page-content").innerHTML = `<div class="content-card"><h1>No pudimos conectar con el aula virtual</h1><p class="page-subtitle">${escapeHtml(error.message)} Comprueba que el servidor esté en ejecución y vuelve a cargar la página.</p></div>`;
  }
}

document.querySelectorAll("[data-view]").forEach((link) => link.addEventListener("click", (event) => {
  event.preventDefault();
  showView(link.dataset.view);
}));
document.querySelectorAll("[data-open-message]").forEach((button) => button.addEventListener("click", openMessageDialog));
document.querySelector("#profile-shortcut").addEventListener("click", () => showView("perfil"));
document.querySelector("#close-dialog").addEventListener("click", () => document.querySelector("#message-dialog").close());
document.querySelector("#cancel-dialog").addEventListener("click", () => document.querySelector("#message-dialog").close());
document.querySelector("#menu-toggle").addEventListener("click", () => {
  const sidebar = document.querySelector("#sidebar");
  const open = sidebar.classList.toggle("open");
  document.querySelector("#sidebar-scrim").classList.toggle("show", open);
  document.querySelector("#menu-toggle").setAttribute("aria-expanded", String(open));
});
document.querySelector("#sidebar-scrim").addEventListener("click", closeSidebar);
document.querySelector("#message-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const feedback = document.querySelector("#form-feedback");
  const button = document.querySelector("#send-message");
  const payload = Object.fromEntries(new FormData(form).entries());
  if (!payload.courseId || !payload.subject.trim() || !payload.body.trim()) {
    feedback.textContent = "Completa el curso, el asunto y el mensaje.";
    return;
  }
  button.disabled = true;
  feedback.textContent = "";
  try {
    const result = await request("/api/messages", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    messages.push(result.message);
    renderMessages();
    form.reset();
    document.querySelector("#message-dialog").close();
    showView("mensajes");
    showToast("Mensaje enviado correctamente.");
  } catch (error) {
    feedback.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

initialize();
