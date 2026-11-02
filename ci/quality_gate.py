"""Quality gate estricto: no aprueba suites ausentes, fallidas ni reportes inválidos."""
import os,json,sys,re,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'reports'
REQUIRED=['unit-aula','unit-exporter','unit-k6-parser','selenium','playwright','functional-aula','functional-tienda-week8','functional-tienda-week9','uat','regression','security-tienda-http','security-tienda-dom','k6-aula-nova-rendimiento','k6-aula-nova-estres','k6-aula-nova-seguridad','k6-tienda-demo-rendimiento','k6-tienda-demo-estres','k6-tienda-demo-seguridad']
errors=[]
for name in REQUIRED:
    p=BASE/'status'/f'{name}.json'
    if not p.exists():errors.append(f'{name}: no ejecutado');continue
    try:
        obj=json.loads(p.read_text(encoding='utf-8'))
        if not obj.get('success'):errors.append(f'{name}: falló: {obj.get("details","")}')
    except (ValueError,OSError) as e:errors.append(f'{name}: estado inválido: {e}')
files=list(BASE.rglob('*.xml'))
if not files:errors.append('No existen resultados JUnit XML')
for f in files:
    try:
        root=ET.parse(f).getroot()
        for x in root.iter('testcase'):
            if x.find('failure') is not None or x.find('error') is not None: errors.append(f'{f.relative_to(BASE)}: {x.attrib.get("name")} falló')
    except ET.ParseError as e:errors.append(f'{f.relative_to(BASE)}: XML inválido {e}')
# Comprobar cantidad y cobertura de los IDs obligatorios, no solo exit status.
sel=set();pw=set();functional=set();k6=set();k6tienda=set()
for f in files:
    try:
        for node in ET.parse(f).getroot().iter('testcase'):
            name=node.attrib.get('name','')
            p=str(f).replace('\\','/')
            if '/selenium/' in p:
                m=re.search(r'test_(\d\d)_',name)
                if m:sel.add(int(m.group(1)))
            elif '/playwright/' in p:
                m=re.search(r'TC(\d\d)',name)
                if m:pw.add(int(m.group(1)))
            elif f.name=='aula-functional.xml':
                m=re.search(r'F(\d\d)',name)
                if m:functional.add(int(m.group(1)))
            elif '/k6/aula-nova/' in p:
                m=re.search(r'([RES]\d\d)',name)
                if m:k6.add(m.group(1))
            elif '/k6/tienda-demo/' in p:
                m=re.search(r'([RES]\d\d)',name)
                if m:k6tienda.add(m.group(1))
    except ET.ParseError:pass
for group,observed,expected in [
    ('Selenium TC01-TC41',sel,set(range(1,42))),
    ('Playwright TC01-TC41',pw,set(range(1,42))),
    ('Aula Nova F01-F25',functional,set(range(1,26))),
    ('Aula Nova k6 R/E/S01-10',k6,{f'{letter}{i:02d}' for letter in 'RES' for i in range(1,11)}),
    ('TiendaDemo k6 R/E/S01-10',k6tienda,{f'{letter}{i:02d}' for letter in 'RES' for i in range(1,11)})
]:
    if observed!=expected:
        errors.append(f'{group}: faltan {sorted(expected-observed)}; inesperados {sorted(observed-expected)}')
if os.getenv('REQUIRE_TESTLINK','0')=='1':
    p=BASE/'status'/'testlink.json'
    if not p.exists() or not json.loads(p.read_text()).get('success'): errors.append('TestLink no sincronizado')
print('QUALITY GATE:', 'FAILED' if errors else 'PASSED')
for err in errors:print(' -',err)
raise SystemExit(1 if errors else 0)
