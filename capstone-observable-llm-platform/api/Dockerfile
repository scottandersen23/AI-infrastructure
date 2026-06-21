FROM python:3.12-slim

WORKDIR /app
COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt
COPY api /app/api
COPY sample-docs /app/sample-docs
EXPOSE 8010
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8010"]
