FROM python:3.6-alpine
ADD requirements.txt /app/requirements.txt
ADD ./test_celery/ /app/
WORKDIR /app/
RUN pip install -r requirements.txt
ENTRYPOINT celery -A test_celery worker --concurrency=20 --loglevel=info
