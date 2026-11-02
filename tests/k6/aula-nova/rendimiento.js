// R01-R10: escenarios de rendimiento de Aula Nova, semanas 9 y 11.
import http from 'k6/http';
import {check,sleep} from 'k6';
const BASE=__ENV.BASE_URL || 'http://aula-nova:3000';
const n=Number(__ENV.CASO||1); const quick=__ENV.CI_SMOKE==='1';
if(n<1||n>10) throw new Error('R01..R10');
const thresholds={http_req_failed:['rate<0.01'],checks:['rate>0.99']};
if([1,5,9,10].includes(n)) thresholds.http_req_duration=['p(95)<500'];
if([2,3,4].includes(n)) thresholds.http_req_duration=['p(95)<300'];
export const options=n===10?{stages:quick?[{duration:'3s',target:5},{duration:'4s',target:10},{duration:'3s',target:0}]:[{duration:'30s',target:5},{duration:'1m',target:15},{duration:'1m',target:30},{duration:'30s',target:0}],thresholds}:{vus:n===9?10:5,duration:quick?'5s':n===9?'30m':'45s',thresholds};
const GET=['/','/api/student','/api/courses','/api/messages'];
function send(length){return http.post(BASE+'/api/messages',JSON.stringify({courseId:'calc-201',subject:'Consulta de rendimiento',body:'x'.repeat(length)}),{headers:{'Content-Type':'application/json'}});}
export default function(){
 let r;
 if(n<=4) r=http.get(BASE+GET[n-1]);
 else if(n===5||n===9||n===10)r=http.get(BASE+GET[(__ITER+__VU)%4]);
 else if(n===6)r=send(20);
 else if(n===7)r=(__ITER%2===0)?http.get(BASE+'/api/courses'):send(20);
 else if(n===8)r=send((__ITER%2===0)?5:1000);
 check(r,{'R caso status HTTP correcto': x=>x.status===((n===6||n===8||(n===7&&__ITER%2!==0))?201:200),'R respuesta no vacía': x=>x.body.length>0});
 sleep(0.1);
}
