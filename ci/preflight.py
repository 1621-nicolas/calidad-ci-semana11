"""Revisa requisitos locales sin cambiar el sistema."""
import os, shutil, subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
print('PREFLIGHT - Calidad CI Semana 11')
checks=[('Python',shutil.which('python') or shutil.which('python3')),('Git',shutil.which('git')),('Docker',shutil.which('docker'))]
for name,value in checks:print(f'{name}: {value or "NO INSTALADO/NO DISPONIBLE"}')
if shutil.which('docker'):
    r=subprocess.run(['docker','compose','version'],capture_output=True,text=True)
    print('Docker Compose:',r.stdout.strip() or r.stderr.strip())
else:print('Docker Compose: no verificable')
for p in ['docker-compose.yml','Jenkinsfile','.github/workflows/ci.yml','docs/matriz_trazabilidad.csv']:
 print(p,'OK' if (root/p).exists() else 'FALTA')
print('TestLink:','credencial y URL definidas' if os.getenv('TESTLINK_DEVKEY') and os.getenv('TESTLINK_URL') else 'PENDIENTE DE CONFIGURACIÓN')
