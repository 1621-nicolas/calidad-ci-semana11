FROM python:3.12.8-slim
WORKDIR /workspace
COPY tienda-demo/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt
COPY tienda-demo/ /workspace/tienda-demo/
COPY ci/ /workspace/ci/
WORKDIR /workspace/tienda-demo
ENV PYTHONIOENCODING=utf-8 SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub TIENDA_BASE_URL=http://tienda-demo:8008/
CMD ["python", "/workspace/ci/run_selenium.py"]
