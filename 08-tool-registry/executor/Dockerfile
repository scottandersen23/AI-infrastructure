FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY executor/requirements.txt /app/executor/requirements.txt
RUN pip install --no-cache-dir -r /app/executor/requirements.txt

COPY executor /app/executor

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8009

CMD ["uvicorn", "executor.app.main:app", "--host", "0.0.0.0", "--port", "8009"]
