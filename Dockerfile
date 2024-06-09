FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y redis-server nginx pkg-config libmariadb-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY redis.conf /usr/local/etc/redis/redis.conf
COPY nginx.conf /etc/nginx/nginx.conf

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

EXPOSE 80

CMD ["sh", "-c", "redis-server /usr/local/etc/redis/redis.conf & uvicorn app:app --host 0.0.0.0 --port 8000 & celery -A app.celery worker --loglevel=info & nginx -g 'daemon off;'"]
