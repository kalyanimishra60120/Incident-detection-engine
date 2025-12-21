FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY order_service ./order_service
COPY incident_engine.py .
COPY incident_config.json .



RUN mkdir -p /app/logs
RUN chmod -R 777 /app/logs

EXPOSE 8000

# Run app + log monitor together
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & uvicorn order_service.main:app --host 0.0.0.0 --port 8001 & python3 incident_engine.py"]
