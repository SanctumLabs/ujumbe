FROM python:3.8.6-alpine3.11

WORKDIR /usr/src/app

COPY . .

RUN mkdir -p /logs/celery

RUN pip install pipenv
RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt

EXPOSE 4000

RUN mkdir -p logs/celery

CMD ["gunicorn", "--config", "config/gunicorn_config.py", "wsgi:app"]
