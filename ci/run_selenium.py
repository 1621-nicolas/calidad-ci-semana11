"""Ejecuta únicamente TC01-TC41 en Selenium y publica JUnit; los casos extra se separan."""
import re
import sys
import unittest
from pathlib import Path
import xmlrunner
ROOT=Path(__file__).resolve().parents[1]/'tienda-demo'
sys.path.insert(0,str(ROOT))
loader=unittest.TestLoader()
suite=loader.discover(str(ROOT/'tests'),pattern='test_tc*.py',top_level_dir=str(ROOT))

def cases(s):
    for item in s:
        if isinstance(item,unittest.TestSuite):
            yield from cases(item)
        else:
            yield item
chosen=[t for t in cases(suite) if re.match(r'^test_(0[1-9]|[1-3][0-9]|4[01])_',t._testMethodName)]
identifiers=[int(re.match(r'^test_(\d\d)_',t._testMethodName).group(1)) for t in chosen]
assert sorted(identifiers)==list(range(1,42)),f'No hay 41 casos únicos: {identifiers}'
print('Selenium: 41 casos TC01–TC41',flush=True)
result=xmlrunner.XMLTestRunner(output='/reports/selenium',verbosity=2).run(unittest.TestSuite(chosen))
raise SystemExit(0 if result.wasSuccessful() else 1)
