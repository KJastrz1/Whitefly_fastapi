FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN pip install uvicorn celery

COPY nginx.conf /etc/nginx/nginx.conf

RUN echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf

CMD redis-server & \
    uvicorn app.app:app --host 0.0.0.0 --port 8000 & \
    celery -A app.celery_config.celery worker --loglevel=info & \
    nginx -g "daemon off;"