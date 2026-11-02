// Semana 9 - Estrés de entrega de archivos ESTATICOS, no de transacciones del carrito.
// Ejecutar solo en el servidor local propio y tras autorizacion.
import http from 'k6/http';
import { check, sleep } from 'k6';

const base = __ENV.BASE_URL || 'http://127.0.0.1:8008';
const n = Number(__ENV.CASO || 1);
const paths = {
  1: ['/'], 2: ['/'], 3: ['/carrito.js'], 4: ['/estilos.css'],
  5: ['/', '/carrito.js', '/estilos.css'], 6: ['/carrito.js'],
  7: ['/tienda_demo.html'], 8: ['/desconocido', '/'],
  9: ['/', '/estilos.css'], 10: ['/', '/carrito.js', '/estilos.css'],
};
if (!paths[n]) throw new Error('Caso E01-E10 inexistente: ' + n);
const fast = __ENV.CI_SMOKE === '1';
const maxVus = [0, 70, 75, 40, 40, 40, 75, 40, 40, 75, 75][n];
export const options = {
  stages: fast ? [
    { duration: '2s', target: 5 }, { duration: '3s', target: 10 }, { duration: '2s', target: 0 }
  ] : [
    { duration: '30s', target: 10 },
    { duration: n === 3 ? '5m' : '1m', target: maxVus },
    { duration: '30s', target: 10 },
    { duration: '15s', target: 0 }
  ],
  thresholds: { checks: ['rate>0.90'] },
};

export default function () {
  const path = paths[n][(__ITER + __VU) % paths[n].length];
  const response = http.get(base + path, { tags: { caso: `E${String(n).padStart(2, '0')}` } });
  check(response, { 'HTTP esperado bajo carga': (r) => r.status === (path === '/desconocido' ? 404 : 200) });
  sleep(0.1);
}
