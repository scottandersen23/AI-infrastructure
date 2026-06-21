FROM python:3.12-slim

WORKDIR /app
COPY observability/requirements.txt /app/observability/requirements.txt
RUN pip install --no-cache-dir -r /app/observability/requirements.txt
COPY observability /app/observability
WORKDIR /app/observability
EXPOSE 8013
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8013"]
