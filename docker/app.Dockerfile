FROM python:3-alpine

WORKDIR /app
COPY ./ ./

RUN pip install -r redis_proxy/requirements.txt