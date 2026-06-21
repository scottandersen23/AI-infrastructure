FROM python:3.12-slim

WORKDIR /app
COPY rag-service/requirements.txt /app/rag-service/requirements.txt
RUN pip install --no-cache-dir -r /app/rag-service/requirements.txt
COPY rag-service /app/rag-service
COPY sample-docs /app/sample-docs
WORKDIR /app/rag-service
EXPOSE 8012
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8012"]
