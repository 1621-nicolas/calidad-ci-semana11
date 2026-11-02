# Demostración de un quality gate rechazando un defecto

**No modificar la rama principal ni los reportes para fabricar un fallo.** Crea una rama temporal a partir de un commit que ya pase CI.

1. `git checkout -b demo/quality-gate-fail`
2. En `aula-nova/backend/functional.week9.test.js`, cambia solo el valor esperado del caso F05 de 4 cursos a 5. Conservar el requisito oficial (cuatro cursos) en la matriz; esta modificación es deliberadamente incorrecta para demostrar que CI la detecta.
3. `git add aula-nova/backend/functional.week9.test.js; git commit -m "Demo: introducir fallo controlado F05"; git push -u origin demo/quality-gate-fail`
4. Abre un Pull Request hacia `main` y comprueba en GitHub Actions y Jenkins el fallo identificado como `F05`. Guarda las capturas y enlaces del run.
5. Restaura el código correcto desde el editor (F05 espera 4 cursos), haz otro commit y push en la misma rama. Comprueba que ambos pipelines pasan y que la historia conserva ambas evidencias.
6. Cierra la PR de demostración sin fusionar la modificación incorrecta.

El fallo debe aparecer en el JUnit XML generado por el runner y provocar que `ci/quality_gate.py` devuelva `FAILED`. No eliminar ni falsear los XML.
