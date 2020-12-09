FROM ubuntu:focal

RUN apt-get update && apt-get -y dist-upgrade && apt-get clean

RUN apt-get install -y python3 python3-zmq python3-petname python3-yaml && apt-get clean

COPY app /app

COPY config.yml /app/

WORKDIR /app

ENV BACKEND_LOGLEVEL="INFO"
ENV BACKEND_WORKERS=2
ENV BROKER_ENDPOINT="tcp://127.0.0.1:5559"

ENTRYPOINT python3 backend.py --log-level $BACKEND_LOGLEVEL --workers $BACKEND_WORKERS $BROKER_ENDPOINT

