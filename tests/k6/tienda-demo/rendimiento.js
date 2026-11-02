// Semana 9 - Pruebas de rendimiento adaptadas a los recursos HTTP reales de TiendaDemo.
// La tienda es estatica: no existen endpoints de login, alumnos, mensajes ni API de pagos.
import http from 'k6/http';
import { check, sleep } from 'k6';

const base = __ENV.BASE_URL || 'http://127.0.0.1:8008';
const n = Number(__ENV.CASO || 1);
const quick = __ENV.CI_SMOKE === '1';
const paths = {
  1: ['/'],                             // R01 carga de inicio
  2: ['/carrito.js'],                    // R02 motor de carrito
  3: ['/estilos.css'],                   // R03 estilos
  4: ['/tienda_demo.html'],             // R04 documento principal
  5: ['/', '/carrito.js', '/estilos.css'],// R05 mezcla de recursos
  6: ['/', '/'],                        // R06 solicitudes repetidas
  7: ['/', '/carrito.js'],              // R07 HTML y JS simultaneos
  8: ['/estilos.css', '/carrito.js'],   // R08 respuestas de distinto tamano
  9: ['/', '/carrito.js', '/estilos.css'],// R09 estabilidad prolongada
  10: ['/', '/carrito.js', '/estilos.css']// R10 capacidad objetivo
};
if (!paths[n]) throw new Error('Caso R01-R10 inexistente: ' + n);

export const options = n === 10 ? {
  stages: quick ? [
    { duration: '2s', target: 5 }, { duration: '3s', target: 10 }, { duration: '2s', target: 0 },
  ] : [
    { duration: '30s', target: 5 }, { duration: '1m', target: 15 },
    { duration: '1m', target: 30 }, { duration: '30s', target: 0 },
  ],
  thresholds: { http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<500'], checks: ['rate>0.99'] },
} : {
  vus: n === 9 ? 10 : 5,
  duration: quick ? '5s' : (n === 9 ? '30m' : '45s'),
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: [n === 2 || n === 3 || n === 4 ? 'p(95)<300' : 'p(95)<500'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  const requested = paths[n];
  // Modo mixto: un recurso por iteracion para que la carga se distribuya.
  const path = requested[(__ITER + __VU) % requested.length];
  const response = http.get(base + path, { tags: { caso: `R${String(n).padStart(2, '0')}`, recurso: path } });
  check(response, { 'recurso HTTP 200': (r) => r.status === 200, 'cuerpo no vacio': (r) => r.body.length > 0 });
  sleep(0.1);
}
