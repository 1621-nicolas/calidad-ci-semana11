from pathlib import Path
import csv,re
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for f in sorted((ROOT/'tienda-demo/tests').glob('test_tc*.py')):
    text=f.read_text(encoding='utf-8')
    for number,name in re.findall(r'def test_(\d\d)_([\w]+)\(',text):
        for prefix,suite,tool in [('SEL','Selenium 41','Selenium'),('PW','Playwright 41','Playwright')]:
            rows.append(dict(case_id=f'{prefix}-TC{number}',suite=suite,requirement=f'TIENDA-TC{number}',description=name.replace('_',' '),tool=tool,expected='El resultado debe coincidir con el criterio de TC'+number,execution='CI/Docker',priority='Alta'))
        rows.append(dict(case_id=f'UAT-TC{number}',suite='UAT Behave',requirement=f'TIENDA-TC{number}',description=name.replace('_',' '),tool='Behave',expected='Escenario de aceptación según features',execution='CI/Docker',priority='Media'))
for number,desc in enumerate([
'Inicio HTML cabeceras','CSS','JS','Perfil','Cursos','Notas','Bandeja vacía','Enviar mensaje','Persistencia mensaje','Asunto mínimo','Asunto máximo','Mensaje mínimo','Mensaje máximo','Recortar espacios','Curso inválido','Asunto corto','Asunto largo','Mensaje corto','Mensaje largo','Campos vacíos','JSON inválido','Body >16KiB','Traversal','URL inválida','Ruta y método inválidos'],1):
    rows.append(dict(case_id=f'AULA-F{number:02d}',suite='Funcional Aula Nova',requirement=f'AULA-RF-{number:02d}',description=desc,tool='Node test',expected='Status y estructura correctos según el caso',execution='CI/Docker',priority='Alta'))
for label,group in [('R','Rendimiento'),('E','Estrés'),('S','Seguridad')]:
    for n in range(1,11):
        rows.append(dict(case_id=f'AULA-{label}{n:02d}',suite=f'k6 {group}',requirement=f'AULA-RNF-{label}{n:02d}',description=f'Escenario {group} {label}{n:02d}',tool='Grafana k6',expected='Cumple umbrales y comprobaciones definidas en script y consigna',execution='CI/Docker',priority='Alta'))
for group,file_pattern,prefix,tool,req in [
    ('Tienda Semana 8','tienda-demo/quality/week8/test_semana8.py','TIENDA-S08','Selenium','TIENDA-S08'),
    ('Tienda Semana 9 Funcional','tienda-demo/quality/week9/test_funcionales.py','TIENDA-S09-F','Selenium','TIENDA-S09'),
    ('Tienda Seguridad','tienda-demo/quality/week9/test_http_seguridad.py','TIENDA-S09-S','HTTP unittest','TIENDA-SEC'),
    ('Tienda Seguridad','tienda-demo/quality/week9/test_seguridad_ui.py','TIENDA-S09-S','Selenium','TIENDA-SEC')]:
    text=(ROOT/file_pattern).read_text(encoding='utf-8')
    for name in re.findall(r'def (test_[a-z0-9_]+)\(',text):
        if prefix=='TIENDA-S08':number=re.search(r's08_(\d\d)',name).group(1);key=f'TIENDA-S08-{number}'
        elif '-F' in prefix:number=re.search(r's09_f(\d\d)',name).group(1);key=f'TIENDA-S09-F{number}'
        else:number=re.search(r's09_s(\d\d)',name).group(1);key=f'TIENDA-S09-S{number}'
        rows.append(dict(case_id=key,suite=group,requirement=req,description=name.replace('_',' '),tool=tool,expected='Comprobación según criterio automatizado',execution='CI/Docker',priority='Alta'))
for label,group in [('R','Rendimiento'),('E','Estrés'),('S','Seguridad')]:
    for n in range(1,11):
        rows.append(dict(case_id=f'TIENDA-{label}{n:02d}',suite=f'Tienda k6 {group}',requirement=f'TIENDA-RNF-{label}{n:02d}',description=f'Escenario tienda {group} {label}{n:02d}',tool='Grafana k6',expected='Criterio HTTP y umbrales del escenario de TiendaDemo',execution='CI/Docker',priority='Alta'))
assert len([x for x in rows if x['suite']=='Selenium 41'])==41
assert len([x for x in rows if x['suite']=='Playwright 41'])==41
p=ROOT/'docs/matriz_trazabilidad.csv';p.parent.mkdir(exist_ok=True)
with p.open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=['case_id','suite','requirement','description','tool','expected','execution','priority']);writer.writeheader();writer.writerows(rows)
print(f'{len(rows)} casos catalogados en matriz')
