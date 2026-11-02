// S01-S10 basados en la tarea de Aula Nova; los resultados son controles, no un pentest integral.
import http from 'k6/http';
import {check} from 'k6';
const BASE=__ENV.BASE_URL || 'http://aula-nova:3000';
const n=Number(__ENV.CASO||1);if(n<1||n>10)throw new Error('S01..S10');
http.setResponseCallback(http.expectedStatuses(200,201,400,403,404,413));
export const options={vus:1,iterations:1,thresholds:{checks:['rate>0.99']}};
const post=(body)=>http.post(BASE+'/api/messages',body,{headers:{'Content-Type':'application/json'}});
export default function(){let r;
 if(n===1){r=http.get(BASE+'/..%2Fbackend%2Fserver.js');check(r,{'S01 traversal bloqueado':x=>x.status===403});}
 if(n===2){r=http.get(BASE+'/%ED%A0%80');check(r,{'S02 URL inválida':x=>x.status===400});}
 if(n===3){r=post('{');check(r,{'S03 JSON inválido rechazado':x=>x.status===400});}
 if(n===4){r=post('x'.repeat(17000));check(r,{'S04 body >16KiB rechazado':x=>x.status===413});}
 if(n===5){const invalid=[{courseId:'desconocido',subject:'Consulta',body:'mensaje válido'},{courseId:'calc-201',subject:'a',body:'mensaje válido'},{courseId:'calc-201',subject:'x'.repeat(101),body:'mensaje válido'},{courseId:'calc-201',subject:'Consulta',body:'a'},{courseId:'calc-201',subject:'Consulta',body:'x'.repeat(1001)}];let good=0;for(const p of invalid){if(post(JSON.stringify(p)).status===400)good++;}check(good,{'S05 5 validaciones':x=>x===5});}
 if(n===6){r=post(JSON.stringify({courseId:'calc-201',subject:'Prueba XSS',body:'<img src=x onerror=alert(1)>'}));check(r,{'S06 texto HTML almacenado':x=>x.status===201&&x.json('message.body').includes('<img')});}
 if(n===7){const a=http.request('PUT',BASE+'/api/messages','{}'),b=http.get(BASE+'/api/no-existe');check(a,{'S07 método no autorizado':x=>x.status===404});check(b,{'S07 ruta inexistente':x=>x.status===404});}
 if(n===8){r=http.get(BASE+'/');check(r,{'S08 cabeceras':x=>x.status===200&&!!x.headers['Content-Security-Policy']&&!!x.headers['X-Frame-Options']&&!!x.headers['X-Content-Type-Options']&&!!x.headers['Referrer-Policy']});}
 if(n===9){r=http.get(BASE+'/api/student');check(r,{'S09 acceso anónimo observado/documentado':x=>x.status===200});}
 if(n===10){let count=0;for(let i=0;i<50;i++){if(http.get(BASE+'/api/courses').status===200)count++;}check(count,{'S10 50 GET controlados':x=>x===50});}
}
