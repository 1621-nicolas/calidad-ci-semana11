/* ============================================================
   TiendaDemo — carrito.js
   Lógica del carrito, navegación de vistas y checkout
   ============================================================ */

"use strict";

const PRODUCTOS = [
  { id: 1,  nombre: "Laptop Pro 15",     precio: 2499.00, emoji: "💻", categoria: "Electrónica", stock: 8  },
  { id: 2,  nombre: "Mouse Inalámbrico", precio:   89.90, emoji: "🖱️", categoria: "Periféricos", stock: 25 },
  { id: 3,  nombre: "Teclado Mecánico",  precio:  249.00, emoji: "⌨️", categoria: "Periféricos", stock: 12 },
  { id: 4,  nombre: "Monitor 27\" 4K",   precio: 1299.00, emoji: "🖥️", categoria: "Electrónica", stock: 5  },
  { id: 5,  nombre: "Auriculares BT",    precio:  199.00, emoji: "🎧", categoria: "Audio",        stock: 0  },
  { id: 6,  nombre: "Webcam HD 1080p",   precio:  159.90, emoji: "📷", categoria: "Periféricos", stock: 18 },
  { id: 7,  nombre: "Disco SSD 1TB",     precio:  329.00, emoji: "💾", categoria: "Almacenamiento", stock: 30 },
  { id: 8,  nombre: "Hub USB-C 7 en 1",  precio:  149.90, emoji: "🔌", categoria: "Accesorios",  stock: 22 },
];

const CUPONES = {
  "DESCUENTO10": 10,
  "PROMO20":     20,
  "ESTUDIANTE15":15,
};

const estado = {
  carrito: [],
  cuponAplicado: null,
  vista: "catalogo",
  filtro: "",
  categoria: "todas",
};

// Utility shortcuts para buscar elementos del DOM de forma rápida.
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

// Formatea un número como precio en soles peruanos.
function formatPrecio(n) {
  return "S/ " + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Genera un identificador único para cada orden.
function generarOrden() {
  return "ORD-" + Date.now().toString(36).toUpperCase();
}

// Evita insertar texto de usuarios como elementos o atributos HTML en la confirmación.
function escaparHTML(texto) {
  const entidades = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(texto).replace(/[&<>"']/g, caracter => entidades[caracter]);
}

let toastTimer = null;

// Muestra un mensaje temporal en pantalla tipo toast.
function mostrarToast(msg, tipo = "exito") {
  const toast = $("#toast");
  toast.textContent = msg;
  toast.className = `visible ${tipo}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.className = ""; }, 3000);
}

// Cambia entre las vistas del sitio (catálogo, carrito, checkout, confirmación).
function mostrarVista(nombre) {
  estado.vista = nombre;
  $$(".vista").forEach(v => v.classList.remove("activa"));
  const target = $(`#vista-${nombre}`);
  if (target) target.classList.add("activa");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Renderiza la lista de productos en el catálogo aplicando filtro y categoría.
function renderCatalogo() {
  const filtroTexto = estado.filtro.toLowerCase().trim();
  const cat = estado.categoria;

  const filtrados = PRODUCTOS.filter(p => {
    const coincideTexto = p.nombre.toLowerCase().includes(filtroTexto) ||
                          p.categoria.toLowerCase().includes(filtroTexto);
    const coincideCat   = cat === "todas" || p.categoria === cat;
    return coincideTexto && coincideCat;
  });

  const grid = $("#grid-productos");
  if (filtrados.length === 0) {
    // No interpretar como HTML el texto introducido en la búsqueda (XSS DOM).
    const mensaje = document.createElement("p");
    mensaje.className = "sin-resultados";
    mensaje.id = "sin-resultados";
    mensaje.append(document.createTextNode('No se encontraron productos para "'));
    const termino = document.createElement("strong");
    termino.textContent = filtroTexto || cat;
    mensaje.append(termino, document.createTextNode('"'));
    grid.replaceChildren(mensaje);
    return;
  }

  grid.innerHTML = filtrados.map(p => {
    const sinStock = p.stock === 0;
    return `
      <article class="tarjeta-producto" id="producto-${p.id}" data-id="${p.id}">
        <div class="producto-imagen">${p.emoji}</div>
        <div class="producto-cuerpo">
          <span class="producto-categoria">${p.categoria}</span>
          <p class="producto-nombre">${p.nombre}</p>
          <p class="producto-stock ${sinStock ? "sin-stock" : ""}">
            ${sinStock ? "Sin stock" : `Stock: ${p.stock} unidades`}
          </p>
          <p class="producto-precio">${formatPrecio(p.precio)}</p>
        </div>
        <button
          class="btn-agregar"
          id="btn-agregar-${p.id}"
          data-id="${p.id}"
          ${sinStock ? "disabled" : ""}
          aria-label="Agregar ${p.nombre} al carrito"
        >
          ${sinStock ? "Sin stock" : "Agregar al carrito"}
        </button>
      </article>`;
  }).join("");

  $$(".btn-agregar:not(:disabled)").forEach(btn => {
    btn.addEventListener("click", () => agregarAlCarrito(Number(btn.dataset.id)));
  });
}

// Agrega un producto al carrito, manejando incremento y límites de stock.
function agregarAlCarrito(id) {
  const producto = PRODUCTOS.find(p => p.id === id);
  if (!producto || producto.stock === 0) return;

  const itemExistente = estado.carrito.find(i => i.producto.id === id);
  if (itemExistente) {
    if (itemExistente.cantidad >= producto.stock) {
      mostrarToast(`Solo hay ${producto.stock} unidades disponibles`, "error");
      return;
    }
    itemExistente.cantidad++;
  } else {
    estado.carrito.push({ producto, cantidad: 1 });
  }

  actualizarContadorCarrito();
  mostrarToast(`"${producto.nombre}" agregado al carrito ✓`, "exito");

  const contador = $("#contador-carrito");
  contador.classList.add("bump");
  setTimeout(() => contador.classList.remove("bump"), 300);
}

// Actualiza el contador visual de artículos en el carrito.
function actualizarContadorCarrito() {
  const total = estado.carrito.reduce((s, i) => s + i.cantidad, 0);
  $("#contador-carrito").textContent = total;
}

// Calcula subtotal, descuento y total actual del carrito.
function calcularTotales() {
  const subtotal = estado.carrito.reduce((s, i) => s + i.producto.precio * i.cantidad, 0);
  const descuento = estado.cuponAplicado
    ? (subtotal * estado.cuponAplicado.porcentaje) / 100
    : 0;
  const total = subtotal - descuento;
  return { subtotal, descuento, total };
}

// Renderiza la vista del carrito con los productos, controles y resumen.
function renderCarrito() {
  mostrarVista("carrito");

  if (estado.carrito.length === 0) {
    $("#carrito-contenido").innerHTML = `
      <div class="carrito-vacio" id="carrito-vacio">
        <div class="icono-vacio">🛒</div>
        <p>Tu carrito está vacío</p>
        <button class="btn-checkout" onclick="mostrarVista('catalogo')" style="width:auto;padding:10px 28px;">
          Ver productos
        </button>
      </div>`;
    return;
  }

  const { subtotal, descuento, total } = calcularTotales();

  const itemsHTML = estado.carrito.map(({ producto, cantidad }) => `
    <div class="item-carrito" id="item-${producto.id}" data-id="${producto.id}">
      <span class="item-emoji">${producto.emoji}</span>
      <div class="item-info">
        <p class="item-nombre">${producto.nombre}</p>
        <p class="item-precio-unit">${formatPrecio(producto.precio)} / unidad</p>
      </div>
      <div class="item-controles">
        <div class="cantidad-wrap">
          <button class="btn-cantidad" id="btn-menos-${producto.id}" data-id="${producto.id}" data-accion="menos" aria-label="Reducir cantidad">−</button>
          <span class="cantidad-num" id="cantidad-${producto.id}">${cantidad}</span>
          <button class="btn-cantidad" id="btn-mas-${producto.id}" data-id="${producto.id}" data-accion="mas" aria-label="Aumentar cantidad">+</button>
        </div>
        <span class="item-subtotal" id="subtotal-${producto.id}">${formatPrecio(producto.precio * cantidad)}</span>
        <button class="btn-eliminar" id="btn-eliminar-${producto.id}" data-id="${producto.id}" aria-label="Eliminar ${producto.nombre}">✕</button>
      </div>
    </div>`).join("");

  const descuentoHTML = descuento > 0 ? `
    <div class="resumen-fila descuento" id="fila-descuento">
      <span>Descuento (${estado.cuponAplicado.porcentaje}%)</span>
      <span id="valor-descuento">−${formatPrecio(descuento)}</span>
    </div>` : "";

  $("#carrito-contenido").innerHTML = `
    <div class="carrito-header">
      <h2>Mi carrito <span style="color:var(--gris-texto);font-size:14px;font-weight:400">(${estado.carrito.reduce((s,i)=>s+i.cantidad,0)} artículos)</span></h2>
      <button class="btn-vaciar" id="btn-vaciar-carrito">Vaciar carrito</button>
    </div>
    <div class="lista-carrito" id="lista-carrito">${itemsHTML}</div>
    <div class="panel-resumen" style="margin-top:1.5rem">
      <h3>Resumen del pedido</h3>
      <div class="resumen-fila"><span>Subtotal</span><span id="valor-subtotal">${formatPrecio(subtotal)}</span></div>
      <div class="resumen-fila"><span>Envío</span><span>Gratis</span></div>
      ${descuentoHTML}
      <div class="resumen-fila total"><span>Total</span><span id="valor-total">${formatPrecio(total)}</span></div>

      <div class="cupon-wrap">
        <input type="text" id="input-cupon" placeholder="Código de cupón" value="${estado.cuponAplicado ? estado.cuponAplicado.codigo : ""}" aria-label="Código de cupón">
        <button class="btn-cupon" id="btn-aplicar-cupon">Aplicar</button>
      </div>
      <p id="msg-cupon" class="${estado.cuponAplicado ? "ok" : ""}">
        ${estado.cuponAplicado ? `✓ Cupón "${estado.cuponAplicado.codigo}" aplicado` : ""}
      </p>
      <button class="btn-checkout" id="btn-ir-checkout">Proceder al pago →</button>
    </div>`;

  $("#btn-vaciar-carrito").addEventListener("click", vaciarCarrito);
  $("#btn-aplicar-cupon").addEventListener("click", aplicarCupon);
  $("#btn-ir-checkout").addEventListener("click", irACheckout);

  $$(".btn-cantidad").forEach(btn => {
    btn.addEventListener("click", () => cambiarCantidad(Number(btn.dataset.id), btn.dataset.accion));
  });

  $$(".btn-eliminar").forEach(btn => {
    btn.addEventListener("click", () => eliminarItem(Number(btn.dataset.id)));
  });
}

// Cambia la cantidad de un producto en el carrito, con control de stock.
function cambiarCantidad(id, accion) {
  const item = estado.carrito.find(i => i.producto.id === id);
  if (!item) return;

  if (accion === "mas") {
    if (item.cantidad >= item.producto.stock) {
      mostrarToast(`Máximo disponible: ${item.producto.stock}`, "error");
      return;
    }
    item.cantidad++;
  } else {
    item.cantidad--;
    if (item.cantidad <= 0) { eliminarItem(id); return; }
  }

  actualizarContadorCarrito();
  renderCarrito();
}

// Elimina un producto específico del carrito.
function eliminarItem(id) {
  const item = estado.carrito.find(i => i.producto.id === id);
  if (item) mostrarToast(`"${item.producto.nombre}" eliminado del carrito`, "error");
  estado.carrito = estado.carrito.filter(i => i.producto.id !== id);
  actualizarContadorCarrito();
  renderCarrito();
}

// Vacía completamente el carrito y reinicia el cupón aplicado.
function vaciarCarrito() {
  estado.carrito = [];
  estado.cuponAplicado = null;
  actualizarContadorCarrito();
  renderCarrito();
  mostrarToast("Carrito vaciado", "error");
}

// Aplica un cupón al carrito si el código es válido.
// Actualiza el mensaje de resultado y vuelve a renderizar el carrito.
function aplicarCupon() {
  const codigo = $("#input-cupon").value.trim().toUpperCase();
  const msgEl  = $("#msg-cupon");

  if (!codigo) {
    msgEl.textContent = "Ingresa un código de cupón";
    msgEl.className = "error";
    return;
  }

  if (estado.cuponAplicado && estado.cuponAplicado.codigo === codigo) {
    msgEl.textContent = `El cupón "${codigo}" ya está aplicado`;
    msgEl.className = "error";
    return;
  }

  if (CUPONES[codigo] !== undefined) {
    estado.cuponAplicado = { codigo, porcentaje: CUPONES[codigo] };
    msgEl.textContent = `✓ Cupón "${codigo}" aplicado — ${CUPONES[codigo]}% de descuento`;
    msgEl.className = "ok";
    renderCarrito();
  } else {
    // Mantener intacto cualquier descuento válido que ya estuviera aplicado.
    msgEl.textContent = "Cupón no válido o expirado";
    msgEl.className = "error";
  }
}

// Navega al checkout sólo si hay productos en el carrito.
function irACheckout() {
  if (estado.carrito.length === 0) {
    mostrarToast("Agrega productos antes de continuar", "error");
    return;
  }
  renderCheckout();
}

// Renderiza el formulario de checkout con información del pedido.
function renderCheckout() {
  mostrarVista("checkout");
  const { subtotal, descuento, total } = calcularTotales();

  const resumenItems = estado.carrito.map(({ producto, cantidad }) => `
    <div class="resumen-mini-item">
      <span>${producto.emoji} ${producto.nombre} ×${cantidad}</span>
      <span>${formatPrecio(producto.precio * cantidad)}</span>
    </div>`).join("");

  const descuentoMini = descuento > 0 ? `
    <div class="resumen-fila descuento" style="font-size:13px;padding:5px 0;">
      <span>Descuento</span><span>−${formatPrecio(descuento)}</span>
    </div>` : "";

  $("#checkout-contenido").innerHTML = `
    <div class="checkout-layout">
      <div>
        <div class="form-card" id="form-datos">
          <h2>Datos de envío</h2>
          <div class="form-fila">
            <div class="form-grupo">
              <label for="campo-nombre">Nombre completo</label>
              <input type="text" id="campo-nombre" name="nombre" placeholder="Juan Pérez" autocomplete="name">
              <p class="error-campo" id="error-nombre">El nombre es obligatorio</p>
            </div>
            <div class="form-grupo">
              <label for="campo-email">Correo electrónico</label>
              <input type="email" id="campo-email" name="email" placeholder="correo@ejemplo.com" autocomplete="email">
              <p class="error-campo" id="error-email">Ingresa un correo válido</p>
            </div>
          </div>
          <div class="form-grupo">
            <label for="campo-direccion">Dirección de entrega</label>
            <input type="text" id="campo-direccion" name="direccion" placeholder="Av. Principal 123, Lima" autocomplete="street-address">
            <p class="error-campo" id="error-direccion">La dirección es obligatoria</p>
          </div>
          <div class="form-fila">
            <div class="form-grupo">
              <label for="campo-ciudad">Ciudad</label>
              <input type="text" id="campo-ciudad" name="ciudad" placeholder="Lima" autocomplete="address-level2">
              <p class="error-campo" id="error-ciudad">La ciudad es obligatoria</p>
            </div>
            <div class="form-grupo">
              <label for="campo-telefono">Teléfono</label>
              <input type="tel" id="campo-telefono" name="telefono" placeholder="987 654 321" autocomplete="tel">
              <p class="error-campo" id="error-telefono">Ingresa un teléfono válido</p>
            </div>
          </div>
        </div>

        <div class="form-card" id="form-pago" style="margin-top:1rem">
          <h2>Método de pago</h2>
          <div class="metodo-pago" id="metodo-pago">
            <label class="opcion-pago seleccionada" id="opcion-tarjeta">
              <input type="radio" name="pago" value="tarjeta" checked> 💳 Tarjeta de crédito / débito
            </label>
            <label class="opcion-pago" id="opcion-yape">
              <input type="radio" name="pago" value="yape"> 📱 Yape / Plin
            </label>
            <label class="opcion-pago" id="opcion-efectivo">
              <input type="radio" name="pago" value="efectivo"> 💵 Pago contra entrega
            </label>
          </div>
          <button class="btn-pagar" id="btn-confirmar-pago">Confirmar y pagar ${formatPrecio(total)}</button>
          <button class="btn-volver" id="btn-volver-carrito">← Volver al carrito</button>
        </div>
      </div>

      <div class="resumen-mini" id="resumen-checkout">
        <h3>Tu pedido</h3>
        ${resumenItems}
        ${descuentoMini}
        <div class="resumen-mini-total">
          <span>Total</span>
          <span id="total-checkout">${formatPrecio(total)}</span>
        </div>
      </div>
    </div>`;

  $$(".opcion-pago").forEach(op => {
    op.querySelector("input").addEventListener("change", () => {
      $$(".opcion-pago").forEach(o => o.classList.remove("seleccionada"));
      op.classList.add("seleccionada");
    });
  });

  $("#btn-confirmar-pago").addEventListener("click", confirmarPago);
  $("#btn-volver-carrito").addEventListener("click", renderCarrito);
}

// Valida los campos del formulario de checkout.
// Muestra errores junto a cada campo si la entrada es inválida.
function validarCheckout() {
  const tieneLetras = /\p{L}/u;
  const campos = [
    {
      id: "campo-nombre", errorId: "error-nombre",
      validar: valor => /^(?:[\p{L}\p{M}.'-]+\s+)+[\p{L}\p{M}.'-]+$/u.test(valor),
      msg: "Ingresa nombre y apellido válidos"
    },
    {
      id: "campo-email", errorId: "error-email",
      validar: valor => /^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$/.test(valor),
      msg: "Ingresa un correo válido"
    },
    {
      id: "campo-direccion", errorId: "error-direccion",
      validar: valor => valor.length >= 5 && tieneLetras.test(valor) &&
                         valor.split(/\s+/).length >= 2 && /^[\p{L}\p{M}0-9\s.,#º°\/-]+$/u.test(valor),
      msg: "Ingresa una dirección válida y descriptiva"
    },
    {
      id: "campo-ciudad", errorId: "error-ciudad",
      validar: valor => /^(?=.*\p{L})[\p{L}\p{M}\s.'-]{2,}$/u.test(valor),
      msg: "Ingresa una ciudad válida"
    },
    {
      id: "campo-telefono", errorId: "error-telefono",
      validar: valor => /^\+?[0-9\s-]+$/.test(valor) &&
                         /^\d{7,15}$/.test(valor.replace(/[^0-9]/g, "")),
      msg: "Ingresa un teléfono válido (7 a 15 dígitos; espacios permitidos)"
    },
  ];

  let valido = true;
  campos.forEach(({ id, errorId, validar, msg }) => {
    const input = $(`#${id}`);
    const errorEl = $(`#${errorId}`);
    const valor = input.value.trim();
    if (!validar(valor)) {
      input.classList.add("invalido");
      errorEl.textContent = msg;
      errorEl.classList.add("visible");
      valido = false;
    } else {
      input.classList.remove("invalido");
      errorEl.classList.remove("visible");
    }
  });
  return valido;
}

// Procesa el pago: valida el formulario y muestra la pantalla de confirmación.
function confirmarPago() {
  if (!validarCheckout()) {
    mostrarToast("Completa todos los campos correctamente", "error");
    return;
  }
  // No confirmar una venta sin unidades disponibles ni descontar dos veces.
  if (estado.carrito.length === 0 || estado.carrito.some(
      i => !Number.isInteger(i.cantidad) || i.cantidad <= 0 || i.cantidad > i.producto.stock)) {
    mostrarToast("No hay stock suficiente para confirmar la compra", "error");
    return;
  }

  const metodoPago = $("input[name='pago']:checked").value;
  const nombre     = $("#campo-nombre").value.trim();
  const email      = $("#campo-email").value.trim();
  const { total }  = calcularTotales();

  // El inventario de esta demo es local al navegador (sin backend ni persistencia).
  estado.carrito.forEach(i => { i.producto.stock -= i.cantidad; });
  renderConfirmacion({ nombre, email, metodoPago, total });
}

// Muestra la pantalla de confirmación final con los datos de la orden.
function renderConfirmacion({ nombre, email, metodoPago, total }) {
  mostrarVista("confirmacion");
  const numeroOrden = generarOrden();
  const fecha = new Date().toLocaleDateString("es-PE", { day: "2-digit", month: "long", year: "numeric" });

  const etiquetasPago = {
    tarjeta:  "Tarjeta de crédito / débito",
    yape:     "Yape / Plin",
    efectivo: "Pago contra entrega",
  };

  $("#confirmacion-contenido").innerHTML = `
    <div class="confirmacion-card" id="confirmacion-card">
      <div class="confirmacion-icono">✓</div>
      <h2 id="msg-confirmacion">¡Compra realizada con éxito!</h2>
      <p class="subtitulo">Gracias, <strong>${escaparHTML(nombre)}</strong>. Tu pedido ha sido confirmado.</p>
      <div id="numero-orden">${numeroOrden}</div>

      <div class="detalle-orden" id="detalle-orden">
        <div>Fecha <span>${fecha}</span></div>
        <div>Email <span>${escaparHTML(email)}</span></div>
        <div>Método de pago <span>${etiquetasPago[metodoPago] || metodoPago}</span></div>
        <div>Total pagado <span>${formatPrecio(total)}</span></div>
        <div>Estado <span style="color:var(--verde)">✓ Confirmado</span></div>
      </div>

      <p style="font-size:13px;color:var(--gris-texto);margin-bottom:1.5rem">
        Recibirás un resumen en <strong>${escaparHTML(email)}</strong> en los próximos minutos.
      </p>
      <button class="btn-seguir" id="btn-seguir-comprando" onclick="nuevaCompra()">
        Seguir comprando
      </button>
    </div>`;

  estado.carrito = [];
  estado.cuponAplicado = null;
  actualizarContadorCarrito();
}

// Reinicia la experiencia para iniciar una nueva compra.
function nuevaCompra() {
  renderCatalogo();
  mostrarVista("catalogo");
}

// Inicia la búsqueda de productos usando el filtro actual.
function iniciarBusqueda() {
  const texto = $("#buscador").value;
  estado.filtro = texto;
  renderCatalogo();
  if (estado.vista !== "catalogo") mostrarVista("catalogo");
}

// Inicializa los eventos de la interfaz y la vista de catálogo.
function init() {
  renderCatalogo();
  mostrarVista("catalogo");

  $("#btn-abrir-carrito").addEventListener("click", renderCarrito);
  $("#btn-buscar").addEventListener("click", iniciarBusqueda);
  $("#buscador").addEventListener("keydown", e => { if (e.key === "Enter") iniciarBusqueda(); });
  $("#filtro-categoria").addEventListener("change", e => {
    estado.categoria = e.target.value;
    renderCatalogo();
  });
}

document.addEventListener("DOMContentLoaded", init);
