FROM ubuntu:focal

RUN apt update && apt -y install python3 python3-zmq && apt clean

ADD app /app

WORKDIR /app
