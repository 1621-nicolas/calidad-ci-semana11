// Semana 9 - Seguridad HTTP acotada al servidor de recursos estaticos de TiendaDemo.
// No prueba autentificacion/SQL/XSS del navegador: la demo carece de backend.
import http from 'k6/http';
import { check } from 'k6';

const base = __ENV.BASE_URL || 'http://127.0.0.1:8008';
const n = Number(__ENV.CASO || 1);
if (n < 1 || n > 10) throw new Error('Caso S01-S10 inexistente: ' + n);
http.setResponseCallback(http.expectedStatuses(200, 400, 403, 404, 405, 413));
export const options = { vus: 1, iterations: 1, thresholds: { checks: ['rate>0.99'] } };

export default function () {
  let r;
  switch (n) {
    case 1:
      r = http.get(base + '/%2e%2e/%2e%2e/requirements.txt');
      check(r, { 'S01 traversal prohibido': (x) => x.status === 403 }); break;
    case 2:
      r = http.get(base + '/%ED%A0%80');
      check(r, { 'S02 codificacion invalida': (x) => x.status === 400 }); break;
    case 3:
      r = http.post(base + '/', '{', { headers: { 'Content-Type': 'application/json' } });
      check(r, { 'S03 POST denegado en sitio estatico': (x) => x.status === 405 }); break;
    case 4:
      r = http.post(base + '/', 'x'.repeat(17000));
      check(r, { 'S04 body mayor a 16KiB': (x) => x.status === 413 }); break;
    case 5:
      r = http.get(base + '/archivo-que-no-existe.txt');
      check(r, { 'S05 no expone recursos desconocidos': (x) => x.status === 404 }); break;
    case 6:
      r = http.get(base + '/?texto=%3Cscript%3Ewindow.qa%3D1%3C%2Fscript%3E');
      check(r, { 'S06 query no reflejada en HTML': (x) => x.status === 200 && !x.body.includes('window.qa=1') }); break;
    case 7:
      r = http.request('PUT', base + '/', '{}');
      check(r, { 'S07 metodo PUT denegado': (x) => x.status === 405 }); break;
    case 8:
      r = http.get(base + '/');
      check(r, { 'S08 cabeceras basicas': (x) => x.status === 200 && !!x.headers['X-Frame-Options'] && !!x.headers['X-Content-Type-Options'] && !!x.headers['Content-Security-Policy'] }); break;
    case 9:
      r = http.get(base + '/.git/config');
      check(r, { 'S09 datos privados no publicados': (x) => x.status === 404 }); break;
    case 10:
      let success = 0;
      for (let i = 0; i < 50; i++) { r = http.get(base + '/'); if (r.status === 200) success++; }
      check(success, { 'S10 50 solicitudes controladas': (count) => count === 50 }); break;
  }
}
