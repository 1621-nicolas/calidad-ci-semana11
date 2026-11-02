"""Ejecuta casos k6 contra un servidor local y exporta JUnit para Jenkins.

Ejemplos:
  python -m scripts.run_k6_suite --group rendimiento --cases 1,2,3 --smoke
  python -m scripts.run_k6_suite --group seguridad --cases all
  python -m scripts.run_k6_suite --group estres --cases all
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import threading
from xml.etree import ElementTree as ET

from scripts.qa_server import create_server

ROOT = Path(__file__).resolve().parents[1]
PATHS = {'rendimiento': ROOT / 'k6' / 'rendimiento.js',
         'estres': ROOT / 'k6' / 'estres.js',
         'seguridad': ROOT / 'k6' / 'seguridad.js'}


def junit_file(group, case, path, code, summary, output):
    case_id = ('R' if group == 'rendimiento' else 'E' if group == 'estres' else 'S') + f'{case:02d}'
    # Versiones de k6 representan cada umbral como booleano o como {"ok": bool}.
    # No ocultar los umbrales fallidos ni interrumpir la publicacion JUnit.
    metrics = summary.get('metrics', {}) if isinstance(summary, dict) else {}
    if not isinstance(metrics, dict):
        metrics = {}
    failures = []
    for name, values in metrics.items():
        if not isinstance(values, dict):
            failures.append('%s: metrica con formato desconocido' % name)
            continue
        thresholds = values.get('thresholds') or {}
        if not isinstance(thresholds, dict):
            failures.append('%s: umbrales con formato desconocido' % name)
            continue
        for rule, result in thresholds.items():
            if isinstance(result, bool):
                passed = result
            elif isinstance(result, dict) and isinstance(result.get('ok'), bool):
                passed = result['ok']
            else:
                failures.append('%s %s: resultado de umbral desconocido' % (name, rule))
                continue
            if not passed:
                failures.append('%s %s: umbral no cumplido' % (name, rule))
    if code != 0:
        failures.append('k6 termino con codigo %s; revisar el registro TXT' % code)
    if not summary:
        failures.append('No se genero resumen JSON verificable de k6')
    tests = ET.Element('testsuite', name='TiendaDemo.%s' % group, tests='1',
                       failures='1' if failures else '0', errors='0')
    test = ET.SubElement(tests, 'testcase', classname='semana9.%s' % group,
                         name=case_id, time='0')
    if failures:
        ET.SubElement(test, 'failure', message='; '.join(failures)).text = output[-10000:]
    ET.SubElement(test, 'system-out').text = json.dumps({
        'caso': case_id, 'codigo_salida': code,
        'metricas': {k: v.get('values', {}) for k, v in metrics.items()
                     if k in ('http_req_duration', 'http_req_failed', 'checks') and isinstance(v, dict)},
        'nota': 'SMOKE reducido no equivale a prueba completa de 30 minutos' if '--smoke' in output else '',
    }, ensure_ascii=False)
    ET.ElementTree(tests).write(path, encoding='utf-8', xml_declaration=True)
    return not failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True, choices=sorted(PATHS))
    parser.add_argument('--cases', default='1,2,3', help='lista 1,2,3 o all (1..10)')
    parser.add_argument('--k6', default='k6', help='ruta completa de k6.exe o k6')
    parser.add_argument('--smoke', action='store_true', help='cargas reducidas, no resultados completos')
    args = parser.parse_args()
    cases = list(range(1, 11)) if args.cases.lower() == 'all' else [int(x) for x in args.cases.split(',')]
    if not cases or len(set(cases)) != len(cases) or any(x not in range(1, 11) for x in cases):
        parser.error('Los casos deben ser unicos, numerados 1..10')
    out = ROOT / 'reports' / args.group
    out.mkdir(parents=True, exist_ok=True)
    binary = shutil.which(args.k6)
    if not binary:
        print('ERROR: k6 no esta disponible. Instalalo: winget install k6 --source winget')
        # El pipeline no confunde "sin ejecutar" con una aprobacion.
        for case in cases:
            junit_file(args.group, case, out / f'caso-{case:02d}.xml', 127, None, 'k6 no instalado')
        return 2
    server = create_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print('Servidor QA local:', 'http://127.0.0.1:%d' % server.server_port, flush=True)
    ok_count = 0
    try:
        for case in cases:
            name = ('R' if args.group == 'rendimiento' else 'E' if args.group == 'estres' else 'S') + f'{case:02d}'
            summary_path = out / f'{name}.json'
            log_path = out / f'{name}.txt'
            command = [binary, 'run', '--summary-export', str(summary_path),
                       '-e', 'BASE_URL=http://127.0.0.1:%s' % server.server_port,
                       '-e', 'CASO=%s' % case,
                       '-e', 'CI_SMOKE=%s' % ('1' if args.smoke else '0'),
                       str(PATHS[args.group])]
            print('Ejecutando', name, '[SMOKE]' if args.smoke else '[COMPLETO]', flush=True)
            try:
                result = subprocess.run(command, cwd=str(ROOT), stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=2400, text=True,
                                        encoding='utf-8', errors='replace')
                output, code = result.stdout, result.returncode
            except (subprocess.TimeoutExpired, OSError) as e:
                output, code = str(e), 124
            log_path.write_text(output, encoding='utf-8')
            try:
                summary = json.loads(summary_path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                summary = None
            if junit_file(args.group, case, out / (name + '.xml'), code, summary,
                          output + (' --smoke' if args.smoke else '')):
                ok_count += 1
            else:
                print('FALLO', name, 'consultar', log_path, flush=True)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    print('%s: %s/%s casos aprobados' % (args.group, ok_count, len(cases)), flush=True)
    return 0 if ok_count == len(cases) else 1


if __name__ == '__main__':
    raise SystemExit(main())
