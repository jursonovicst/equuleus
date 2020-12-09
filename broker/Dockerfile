FROM ubuntu:focal

RUN apt-get update && apt-get -y dist-upgrade && apt-get clean

RUN apt-get install -y python3 python3-zmq && apt-get clean

COPY app /app

ARG FRONTEND_PORT=5560
ARG BACKEND_PORT=5559
ENV FRONTEND_ENDPOINT="tcp://*:${FRONTEND_PORT}"
ENV BACKEND_ENDPOINT="tcp://*:${BACKEND_PORT}"
ENV BROKER_LOGLEVEL="DEBUG"

EXPOSE $FRONTEND_PORT:$FRONTEND_PORT
EXPOSE $BACKEND_PORT:$BACKEND_PORT

ENTRYPOINT python3 /app/broker.py --log-level $BROKER_LOGLEVEL $FRONTEND_ENDPOINT $BACKEND_ENDPOINT
#ENTRYPOINT ["python3", "/app/broker.py", "--log-level", "$BROKER_LOGLEVEL", "$FRONTEND_ENDPOINT", "$BACKEND_ENDPOINT"]
