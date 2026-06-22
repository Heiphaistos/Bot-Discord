FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_new.txt .
RUN pip install --no-cache-dir -r requirements_new.txt

COPY . .

RUN mkdir -p data logs

COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://127.0.0.1:5000/health || exit 1

CMD ["/start.sh"]
