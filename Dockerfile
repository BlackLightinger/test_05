FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-jaeger \
    prometheus_client \
    behave

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

RUN apt-get update && apt-get install -y coreutils

EXPOSE 8000

CMD ["python", "main.py"]
