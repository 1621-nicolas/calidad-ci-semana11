"""Sincroniza casos y resultados JUnit XML con TestLink XML-RPC.

Requiere TESTLINK_URL, TESTLINK_DEVKEY, TESTLINK_AUTHOR_LOGIN.
Crea proyecto, plan, suites y casos si faltan. No se ejecuta de forma simulada.
"""
import csv, json, os, re, sys, time, xml.etree.ElementTree as ET, xmlrpc.client
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports'
MATRIX=ROOT/'docs'/'matriz_trazabilidad.csv'

def fail(msg):
    print('TESTLINK ERROR:',msg,file=sys.stderr)
    (REPORTS/'status').mkdir(parents=True,exist_ok=True)
    (REPORTS/'status'/'testlink.json').write_text(json.dumps({'success':False,'details':msg},ensure_ascii=False),encoding='utf-8')
    raise SystemExit(2)

def result_status(node):
    if node.find('error') is not None or node.find('failure') is not None:return 'f'
    if node.find('skipped') is not None:return 'b'
    return 'p'

def case_key(path,node):
    name=node.attrib.get('name','')
    p=str(path).replace('\\','/')
    if '/week8/' in p:
        m=re.search(r's08_(\d\d)',name)
        return f'TIENDA-S08-{m.group(1)}' if m else None
    if '/week9/' in p:
        m=re.search(r's09_f(\d\d)',name)
        return f'TIENDA-S09-F{m.group(1)}' if m else None
    if '/security/' in p:
        m=re.search(r's09_s(\d\d)',name)
        return f'TIENDA-S09-S{m.group(1)}' if m else None
    if '/uat/' in p:
        m=re.search(r'TC[- ]?(\d\d)',name)
        return f'UAT-TC{m.group(1)}' if m else None
    if '/selenium/' in p:
        m=re.search(r'test_(\d\d)_',name)
        return f'SEL-TC{m.group(1)}' if m else None
    if '/playwright/' in p:
        m=re.search(r'TC(\d\d)',name)
        return f'PW-TC{m.group(1)}' if m else None
    if path.name=='aula-functional.xml':
        m=re.search(r'\bF(\d\d)\b',name)
        return f'AULA-F{m.group(1)}' if m else None
    if '/k6/tienda-demo/' in p:
        m=re.search(r'([RES]\d\d)',name)
        return f'TIENDA-{m.group(1)}' if m else None
    if '/k6/aula-nova/' in p:
        m=re.search(r'([RES]\d\d)',name)
        return f'AULA-{m.group(1)}' if m else None
    return None

def parse_junit():
    records={}
    for path in REPORTS.rglob('*.xml'):
        try:tree=ET.parse(path)
        except ET.ParseError as e:fail(f'XML inválido {path}: {e}')
        for node in tree.iter('testcase'):
            key=case_key(path,node)
            if not key:continue
            status=result_status(node)
            err=node.find('failure')
            if err is None:err=node.find('error')
            notes=(err.attrib.get('message','') if err is not None else '')
            records[key]={'status':status,'name':node.attrib.get('name',''),'notes':notes,'file':str(path.relative_to(ROOT))}
    return records

class TestLink:
    def __init__(self):
        url=os.getenv('TESTLINK_URL','').strip();key=os.getenv('TESTLINK_DEVKEY','').strip()
        if not url or not key:fail('Faltan TESTLINK_URL o TESTLINK_DEVKEY; no se puede demostrar sincronización')
        self.api=xmlrpc.client.ServerProxy(url,allow_none=True)
        self.key=key
    def call(self,method,**kwargs):
        try:
            result=getattr(self.api.tl,method)({'devKey':self.key,**kwargs})
        except Exception as exc:raise RuntimeError(f'{method}: {exc}') from exc
        if isinstance(result,list) and result and isinstance(result[0],dict) and result[0].get('code'):
            raise RuntimeError(f'{method}: {result[0]}')
        return result


def main():
    if not MATRIX.is_file():fail('No existe matriz de trazabilidad')
    records=parse_junit()
    if not records:fail('No hay casos correlacionables en reportes JUnit; no se publica éxito ficticio')
    client=TestLink()
    project_name=(os.getenv('TESTLINK_PROJECT') or 'Calidad Semana11')
    plan_name=(os.getenv('TESTLINK_PLAN') or 'Plan Integración CI')
    author=(os.getenv('TESTLINK_AUTHOR_LOGIN') or 'admin')
    try:
        try:project=client.call('getTestProjectByName',testprojectname=project_name)
        except RuntimeError:
            project=client.call('createTestProject',testprojectname=project_name,testprojectprefix='QA11',notes='Calidad y Pruebas Semana 11',active=True,public=False)
        project_id=int(project['id'] if isinstance(project,dict) else project[0]['id'])
        try:plan=client.call('getTestPlanByName',testprojectname=project_name,testplanname=plan_name)
        except RuntimeError:plan=client.call('createTestPlan',testplanname=plan_name,testprojectname=project_name,notes='Plan Selenium, Playwright y k6')
        plan_id=int(plan['id'] if isinstance(plan,dict) else plan[0]['id'])
        raw_suites=client.call('getFirstLevelTestSuitesForTestProject',testprojectid=project_id)
        suites={v['name']:int(v['id']) for v in (raw_suites.values() if isinstance(raw_suites,dict) else raw_suites or [])}
        rows=list(csv.DictReader(MATRIX.open(encoding='utf-8')))
        mapping={};created=0
        for row in rows:
            group=row['suite'];name=row['case_id']+' | '+row['description']
            if group not in suites:
                res=client.call('createTestSuite',testprojectid=project_id,testsuitename=group,details='Casos '+group,checkduplicatedname=True,actiononduplicatedname='block')
                suites[group]=int(res['id'] if isinstance(res,dict) else res[0]['id'])
            try:
                case=client.call('getTestCaseIDByName',testcasename=name,testsuitename=group,testprojectname=project_name)
                case_id=int(case[0]['id'] if isinstance(case,list) else case['id'])
                external=(case[0].get('full_external_id') if isinstance(case,list) else case.get('full_external_id'))
            except (RuntimeError,IndexError,KeyError,TypeError):
                res=client.call('createTestCase',testcasename=name,testsuiteid=suites[group],testprojectid=project_id,authorlogin=author,summary=row['expected'],preconditions=row['requirement'],importance=2,executiontype=2)
                case_id=int(res['id'] if isinstance(res,dict) else res[0]['id']);external=None;created+=1
            if not external:
                raw=client.call('getTestCase',testcaseid=case_id)
                data=raw[0] if isinstance(raw,list) else raw
                external=data.get('full_external_id') or data.get('external_id')
            if not external:raise RuntimeError('TestLink no devolvió external id para '+name)
            try:client.call('addTestCaseToTestPlan',testprojectid=project_id,testplanid=plan_id,testcaseexternalid=str(external),version=1)
            except RuntimeError as exc:
                # Si el caso ya estaba en el plan, continuar; registrar otros errores.
                if 'already' not in str(exc).lower() and 'existe' not in str(exc).lower():raise
            mapping[row['case_id']]={'testcaseid':case_id,'external_id':external}
        buildname=(os.getenv('CI_PIPELINE','manual')+'-'+os.getenv('BUILD_NUMBER',os.getenv('GITHUB_RUN_ID',str(int(time.time())))))[:90]
        try:client.call('createBuild',testplanid=plan_id,buildname=buildname,buildnotes='CI automatizada')
        except RuntimeError as exc:
            if 'already' not in str(exc).lower() and 'existe' not in str(exc).lower():raise
        # Registrar también como Blocked los casos no ejecutados, nunca como Passed.
        for missing in set(mapping)-set(records):
            records[missing]={'status':'b','name':missing,'notes':'No ejecutado: sin JUnit verificable','file':''}
        published=0;errors=[]
        for key,item in records.items():
            if key not in mapping:errors.append('Sin registro: '+key);continue
            url=os.getenv('CI_REPORT_URL','')
            notes=f"Herramienta={key.split('-')[0]}; Estado={item['status']}; FechaUTC={time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}; CI={buildname}; Archivo={item['file']}; Reporte={url}; Error={item['notes'][:700]}"
            try:client.call('reportTCResult',testcaseid=mapping[key]['testcaseid'],testplanid=plan_id,status=item['status'],buildname=buildname,notes=notes,guess=True)
            except RuntimeError as exc:errors.append(f'{key}: {exc}');continue
            published+=1
        out=REPORTS/'testlink';out.mkdir(exist_ok=True)
        (out/'resultado.json').write_text(json.dumps({'project':project_name,'plan':plan_name,'build':buildname,'registered':len(mapping),'created':created,'published':published,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
        ok=not errors and published>=len(records)
        (REPORTS/'status'/'testlink.json').write_text(json.dumps({'success':ok,'details':f'{published} resultados enviados; {len(errors)} errores'},ensure_ascii=False),encoding='utf-8')
        print(f'TestLink: registrados={len(mapping)}, publicados={published}, errores={errors[:3]}')
        return 0 if ok else 1
    except Exception as exc:fail(str(exc))
if __name__=='__main__':raise SystemExit(main())
