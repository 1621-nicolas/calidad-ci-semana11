FROM python:3.12.8-slim
WORKDIR /app
COPY tienda-demo/app/ ./app/
COPY tienda-demo/scripts/qa_server.py ./scripts/qa_server.py
EXPOSE 8008
CMD ["python", "-m", "scripts.qa_server", "--host", "0.0.0.0", "--port", "8008"]
