FROM python:3-alpine

WORKDIR /app
COPY ./redis_proxy ./redis_proxy

RUN pip install -r redis_proxy/requirements.txt