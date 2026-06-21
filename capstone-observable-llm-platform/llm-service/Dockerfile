FROM python:3.12-slim

WORKDIR /app
COPY llm-service/requirements.txt /app/llm-service/requirements.txt
RUN pip install --no-cache-dir -r /app/llm-service/requirements.txt
COPY llm-service /app/llm-service
WORKDIR /app/llm-service
EXPOSE 8011
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
