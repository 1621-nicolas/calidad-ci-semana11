"""Regresión del lector de umbrales k6 y su integración con JUnit."""
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET
from types import SimpleNamespace
from ci import execute
from ci.execute import k6_threshold_failures

class ThresholdSummaryTests(unittest.TestCase):
    def test_k6_054_false_significa_umbral_aprobado(self):
        # Mismo tipo de resumen usado por grafana/k6:0.54.0.
        summary={'metrics':{
            'http_req_failed':{'value':0.0,'thresholds':{'rate<0.01':False}},
            'checks':{'value':1.0,'thresholds':{'rate>0.99':False}},
            'http_req_duration':{'p(95)':8.46,'thresholds':{'p(95)<500':False}},
        }}
        self.assertEqual(k6_threshold_failures(summary),[])

    def test_k6_054_true_significa_umbral_incumplido(self):
        summary={'metrics':{'http_req_failed':{
            'value':.25,'thresholds':{'rate<0.01':True}}}}
        self.assertEqual(k6_threshold_failures(summary),
                         ['http_req_failed: rate<0.01 no cumple'])

    def test_compatibilidad_objeto_ok(self):
        self.assertEqual(k6_threshold_failures({'metrics':{'checks':{
            'thresholds':{'rate>0.99':{'ok':True}}}}}),[])
        self.assertEqual(k6_threshold_failures({'metrics':{'checks':{
            'thresholds':{'rate>0.99':{'ok':False}}}}}),
            ['checks: rate>0.99 no cumple'])

    def test_sin_umbral_no_se_aprueba(self):
        self.assertIn('no se encontraron umbrales',
                      '; '.join(k6_threshold_failures({'metrics':{'checks':{'value':1}}})))

    def test_json_invalido_no_se_aprueba(self):
        self.assertTrue(k6_threshold_failures({}))
        self.assertTrue(k6_threshold_failures({'metrics':None}))

    def test_valor_desconocido_no_se_aprueba(self):
        bad={'metrics':{'checks':{'thresholds':{'rate>0.99':'aprobado'}}}}
        self.assertTrue(k6_threshold_failures(bad))


class IntegrationReportTests(unittest.TestCase):
    def _simulate(self, fail_case=None, create_summary=True):
        with tempfile.TemporaryDirectory() as work:
            root=Path(work)
            def fake_run(args, capture=True):
                outarg=next(a for a in args if str(a).startswith('--summary-export='))
                relpath=outarg.split('/reports/',1)[1]
                target=root/relpath
                target.parent.mkdir(parents=True,exist_ok=True)
                n=target.stem
                if create_summary:
                    breached=n==fail_case
                    target.write_text(json.dumps({'metrics':{
                        'checks':{'value':0.0 if breached else 1.0,
                                  'thresholds':{'rate>0.99':breached}},
                        'http_req_failed':{'value':0.1 if breached else 0.0,
                                           'thresholds':{'rate<0.01':breached}}
                    }}),encoding='utf-8')
                return SimpleNamespace(returncode=0,stdout='simulación de proceso k6\n')
            with patch.object(execute,'REPORTS',root),patch.object(execute,'run',fake_run):
                if not create_summary:
                    stale=root/'k6'/'aula-nova'/'rendimiento'/'R01.json'
                    stale.parent.mkdir(parents=True,exist_ok=True)
                    stale.write_text(json.dumps({'metrics':{'checks':{
                        'thresholds':{'rate>0.99':False}}}}),encoding='utf-8')
                exit_code=execute.k6('rendimiento','aula-nova',smoke=True)
                xmls=list((root/'k6'/'aula-nova'/'rendimiento').glob('*.xml'))
                failures=sum(len(list(ET.parse(f).getroot().iter('failure'))) for f in xmls)
                status=json.loads((root/'status'/'k6-aula-nova-rendimiento.json').read_text())
                return exit_code,len(xmls),failures,status

    def test_legacy_sin_fallos_genera_diez_xml_aprobados(self):
        code,count,failures,status=self._simulate()
        self.assertEqual((code,count,failures),(0,10,0))
        self.assertFalse(status['success'])  # smoke no equivale a validación completa

    def test_legacy_umbral_verdadero_es_error_junit(self):
        code,count,failures,_=self._simulate(fail_case='R02')
        self.assertEqual((code,count,failures),(1,10,1))

    def test_json_viejo_no_se_reutiliza(self):
        code,count,failures,_=self._simulate(create_summary=False)
        self.assertEqual((code,count,failures),(1,10,10))

if __name__=='__main__': unittest.main()
