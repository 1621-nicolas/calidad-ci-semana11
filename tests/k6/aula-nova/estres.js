// E01-E10: ejecutarlos solo contra la instancia propia de laboratorio.
import http from 'k6/http';
import {check,sleep} from 'k6';
const BASE=__ENV.BASE_URL || 'http://aula-nova:3000';
const n=Number(__ENV.CASO||1),smoke=__ENV.CI_SMOKE==='1';
if(n<1||n>10)throw new Error('E01..E10');
const max=[0,70,75,40,40,40,75,40,40,75,75][n];
export const options={stages:smoke?[{duration:'2s',target:5},{duration:'3s',target:10},{duration:'2s',target:0}]:n===10?[{duration:'30s',target:10},{duration:'1m',target:75},{duration:'1m',target:10},{duration:'15s',target:0}]:[{duration:'30s',target:10},{duration:n===3?'5m':'1m',target:max},{duration:'30s',target:10},{duration:'15s',target:0}],thresholds:{checks:['rate>0.80']}};
http.setResponseCallback(http.expectedStatuses(200,201,400));
const post=(body)=>http.post(BASE+'/api/messages',body,{headers:{'Content-Type':'application/json'}});
export default function(){
 let r,expected=200;
 if(n===1||n===2||n===3||n===10)r=http.get(BASE+'/');
 if(n===4)r=http.get(BASE+(__ITER%4?' /api/courses':'/api/student').trim());
 if(n===5)r=http.get(BASE+'/api/messages');
 if(n===6){r=post(JSON.stringify({courseId:'calc-201',subject:'Pico de envíos',body:'Prueba de estrés aprobada'}));expected=201;}
 if(n===7){r=post(JSON.stringify({courseId:'calc-201',subject:'Estrés cerca del límite',body:'x'.repeat(1000),padding:' '.repeat(14000)}));expected=201;}
 if(n===8){r=__ITER%2?post('{'):http.get(BASE+'/api/courses');expected=__ITER%2?400:200;}
 if(n===9)r=http.get(BASE+'/api/courses',{headers:{'Connection':'close'}});
 check(r,{'E status controlado':x=>x.status===expected});sleep(0.15);
}
