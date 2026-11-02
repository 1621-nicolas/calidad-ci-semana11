"""Ejecutor ÚNICO usado por Jenkins y GitHub Actions.
Llama a Docker Compose y registra informes JUnit; no inventa ejecuciones.
"""
import argparse, os, json, subprocess, sys, time, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports'

def run(args,capture=True):
    print('+ '+' '.join(map(str,args)),flush=True)
    if capture:
        return subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace')
    return subprocess.run(args,cwd=ROOT).returncode

def compose(*args):return ['docker','compose',*args]

def report(phase,ok,details=''):
    path=REPORTS/'status';path.mkdir(parents=True,exist_ok=True)
    (path/f'{phase}.json').write_text(json.dumps({'phase':phase,'success':ok,'details':details,'timestamp':int(time.time()),'pipeline':os.getenv('CI_PIPELINE','local')},ensure_ascii=False,indent=2),encoding='utf-8')

def test_command(phase,service,cmd):
    for folder in ('selenium','playwright','week8','week9','uat','regression','security','exportador'):
        (REPORTS/folder).mkdir(parents=True,exist_ok=True)
    result=run(compose('run','--rm','-T',service,*cmd))
    print(result.stdout[-12000:],flush=True)
    (REPORTS/'console').mkdir(parents=True,exist_ok=True)
    (REPORTS/'console'/f'{phase}.txt').write_text(result.stdout,encoding='utf-8')
    report(phase,result.returncode==0,'exit code '+str(result.returncode))
    return result.returncode

def run_k6_parser_unit_tests():
    """Valida en la máquina del pipeline el parser de resultados k6."""
    result=run([sys.executable,'-m','unittest','discover','-s','ci/tests',
                '-p','test_k6_thresholds.py','-v'])
    (REPORTS/'console').mkdir(parents=True,exist_ok=True)
    (REPORTS/'console'/'unit-k6-parser.txt').write_text(result.stdout,encoding='utf-8')
    print(result.stdout[-12000:],flush=True)
    report('unit-k6-parser',result.returncode==0,'exit code '+str(result.returncode))
    return result.returncode

def k6_threshold_failures(summary):
    """Interpreta los umbrales de k6 sin invertir los resultados.

    k6 0.54 (``--summary-export``) guarda cada umbral como booleano:
      false = NO se excedió el umbral (PASS)
      true  = se excedió el umbral (FAIL)
    Un objeto {"ok": bool} indica explícitamente aprobación o rechazo.
    Por seguridad, un esquema desconocido o sin umbrales no se aprueba.
    """
    if not isinstance(summary, dict) or not isinstance(summary.get('metrics'), dict):
        return ['Resumen k6: falta metrics o el formato JSON no es válido']
    reasons = []
    checked = 0
    for metric_name, metric in summary['metrics'].items():
        if not isinstance(metric, dict):
            continue
        thresholds = metric.get('thresholds', {})
        if not isinstance(thresholds, dict):
            reasons.append(f'{metric_name}: thresholds inválido')
            continue
        for condition, record in thresholds.items():
            checked += 1
            if isinstance(record, bool):
                # Formato legacy (--summary-export, k6 0.54): true == BREACHED
                violated = record
            elif isinstance(record, dict) and type(record.get('ok')) is bool:
                # Formato de objeto: ok == passed
                violated = not record['ok']
            else:
                reasons.append(f'{metric_name}: {condition} tiene un resultado de umbral desconocido')
                continue
            if violated:
                reasons.append(f'{metric_name}: {condition} no cumple')
    if checked == 0:
        reasons.append('Resumen k6: no se encontraron umbrales de aceptación')
    return reasons

def k6(group,app,smoke=False):
    output=REPORTS/'k6'/app/group;output.mkdir(parents=True,exist_ok=True)
    failures=[];suffix={'rendimiento':'R','estres':'E','seguridad':'S'}[group]
    for i in range(1,11):
        ident=f'{suffix}{i:02d}'
        base='http://aula-nova:3000' if app=='aula-nova' else 'http://tienda-demo:8008'
        name=f'{app}-{ident}'
        script=f'/scripts/{app}/{group}.js'
        cmd=['run',f'--summary-export=/reports/k6/{app}/{group}/{ident}.json', '-e',f'BASE_URL={base}', '-e',f'CASO={i}']
        if smoke:cmd.extend(['-e','CI_SMOKE=1'])
        cmd.append(script)
        # No permitir que un JSON de una ejecución anterior apruebe la actual.
        previous_summary=output/f'{ident}.json'
        if previous_summary.exists():previous_summary.unlink()
        result=run(compose('run','--rm','-T','k6',*cmd))
        (output/f'{ident}.txt').write_text(result.stdout,encoding='utf-8')
        summary=output/f'{ident}.json';reason=[]
        if result.returncode!=0:reason.append('k6 exit='+str(result.returncode))
        if not summary.exists():reason.append('No se generó JSON k6')
        else:
            try:
                data=json.loads(summary.read_text(encoding='utf-8'))
                reason.extend(k6_threshold_failures(data))
            except Exception as exc:reason.append(f'JSON ilegible: {exc}')
        suite=ET.Element('testsuite',name=f'{app}.{group}.{ident}',tests='1',failures=str(bool(reason)),errors='0')
        case=ET.SubElement(suite,'testcase',classname=f'{app}.{group}',name=ident)
        if reason:ET.SubElement(case,'failure',message='; '.join(reason)).text=result.stdout[-4000:]
        ET.SubElement(case,'system-out').text=result.stdout[-4000:]
        ET.ElementTree(suite).write(output/f'{ident}.xml',encoding='utf-8',xml_declaration=True)
        print(name, 'FALLÓ' if reason else 'OK', ('; '.join(reason))[:200],flush=True)
        if reason:failures.append(ident)
    report(f'k6-{app}-{group}',not failures and not smoke,('SOLO SMOKE, no cuenta como validación completa; ' if smoke else '')+'fallidos: '+', '.join(failures))
    return 1 if failures else 0

def main():
    p=argparse.ArgumentParser()
    p.add_argument('phase',choices=['build','environment','unit','selenium','playwright','functional','uat','performance','stress','security','testlink','reports','quality','cleanup'])
    p.add_argument('--smoke',action='store_true',help='Solo diagnóstico local; nunca sustituye pruebas completas')
    a=p.parse_args();phase=a.phase
    REPORTS.mkdir(exist_ok=True)
    try:
        if phase=='build':
            code=run(compose('build','aula-nova','tienda-demo','selenium-tests','playwright-tests'),False)
        elif phase=='environment':
            code=run(compose('up','-d','--wait','aula-nova','tienda-demo','selenium'),False)
        elif phase=='unit':
            code=test_command('unit-aula','aula-nova',['node','--test','--test-reporter=junit','--test-reporter-destination=/reports/aula-unit.xml','backend/server.test.js'])
            code|=test_command('unit-exporter','selenium-tests',['python','-m','xmlrunner','discover','-s','quality/week9','-p','test_exportador_k6.py','-o','/reports/exportador'])
            code|=run_k6_parser_unit_tests()
        elif phase=='selenium':code=test_command('selenium','selenium-tests',['python','/workspace/ci/run_selenium.py'])
        elif phase=='playwright':code=test_command('playwright','playwright-tests',['python','-m','pytest','-q','/workspace/tests/playwright','--junitxml=/reports/playwright/TEST-playwright.xml'])
        elif phase=='functional':
            code=test_command('functional-aula','aula-nova',['node','--test','--test-reporter=junit','--test-reporter-destination=/reports/aula-functional.xml','backend/functional.week9.test.js'])
            code|=test_command('functional-tienda-week8','selenium-tests',['python','-m','xmlrunner','discover','-s','quality/week8','-p','test_semana8.py','-o','/reports/week8'])
            code|=test_command('functional-tienda-week9','selenium-tests',['python','-m','xmlrunner','discover','-s','quality/week9','-p','test_funcionales.py','-o','/reports/week9'])
        elif phase=='uat':
            code=test_command('uat','selenium-tests',['python','-m','behave','features','--junit','--junit-directory','/reports/uat'])
            code|=test_command('regression','selenium-tests',['python','-m','xmlrunner','discover','-s','tests','-p','test_fails.py','-o','/reports/regression'])
        elif phase=='performance':
            code=k6('rendimiento','aula-nova',a.smoke)
            code|=k6('rendimiento','tienda-demo',a.smoke)
        elif phase=='stress':
            code=k6('estres','aula-nova',a.smoke)
            code|=k6('estres','tienda-demo',a.smoke)
        elif phase=='security':
            code=test_command('security-tienda-http','selenium-tests',['python','-m','xmlrunner','discover','-s','quality/week9','-p','test_http_seguridad.py','-o','/reports/security'])
            code|=test_command('security-tienda-dom','selenium-tests',['python','-m','xmlrunner','discover','-s','quality/week9','-p','test_seguridad_ui.py','-o','/reports/security'])
            code|=k6('seguridad','aula-nova',a.smoke)
            code|=k6('seguridad','tienda-demo',a.smoke)
        elif phase=='testlink':
            result=run([sys.executable,str(ROOT/'ci'/'testlink_sync.py')]);print(result.stdout[-5000:]);code=result.returncode
        elif phase=='reports':
            files=list(REPORTS.rglob('*.xml'));print(f'Archivos JUnit XML: {len(files)}');code=0 if files else 1
        elif phase=='quality':
            result=run([sys.executable,str(ROOT/'ci'/'quality_gate.py')]);print(result.stdout);code=result.returncode
        else:code=run(compose('down','--remove-orphans'),False)
        if phase in ('build','environment','reports','quality'):report(phase,code==0)
        return code
    except Exception as exc:
        print(f'ERROR en {phase}: {exc}',file=sys.stderr);report(phase,False,str(exc));return 1
if __name__=='__main__':raise SystemExit(main())
