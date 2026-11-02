FROM mcr.microsoft.com/playwright/python:v1.57.0-noble
WORKDIR /workspace
COPY tests/playwright/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt
COPY tests/playwright/ /workspace/tests/playwright/
COPY tienda-demo/app/ /workspace/tienda-demo/app/
ENV PYTHONIOENCODING=utf-8 TIENDA_BASE_URL=http://tienda-demo:8008/ AULA_BASE_URL=http://aula-nova:3000
CMD ["python", "-m", "pytest", "-q", "/workspace/tests/playwright", "--junitxml=/reports/playwright/TEST-playwright.xml"]
