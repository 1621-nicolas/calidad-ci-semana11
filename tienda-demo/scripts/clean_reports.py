"""Limpieza conservadora de reportes de ejecuciones anteriores."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1] / 'reports'
for subdir in ('unittest', 'behave', 'semana8', 'semana9', 'rendimiento', 'estres', 'seguridad', 'exportador'):
    folder = root / subdir
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)
print('Informes preparados en:', root)
