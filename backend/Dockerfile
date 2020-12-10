FROM ubuntu:focal

RUN apt-get update && apt-get -y dist-upgrade && apt-get clean

RUN apt-get install -y python3 python3-pip && apt-get clean

COPY app /app

RUN pip3 install -r /app/requirements.txt

WORKDIR /app

ENV BACKEND_LOGLEVEL="INFO"
ENV BACKEND_PORT=80

EXPOSE 80:$BACKEND_PORT

HEALTHCHECK CMD curl -s -d '{"method": "lookup", "parameters": {"local": "0.0.0.0", "qname": "keepalive.main.xpx.t-online.de.", "qtype": "A","real-remote": "172.24.0.1/32"}}' http://127.0.0.1/dns |grep 192.0.2.1

ENTRYPOINT python3 backend.py --log-level $BACKEND_LOGLEVEL --port $BACKEND_PORT

