FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9


RUN apt-get update && apt-get install -y nginx && apt-get clean


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


COPY nginx.conf /etc/nginx/nginx.conf


EXPOSE 80 8000


CMD service nginx start && uvicorn main:app --host 0.0.0.0 --port 8000
