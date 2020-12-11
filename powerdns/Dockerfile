# Runtime
FROM ubuntu:focal

# Reusable layer for base update - Should be cached from builder
RUN apt-get update && apt-get -y dist-upgrade && apt-get clean

# PowerDNS repo
RUN echo "deb [arch=amd64] http://repo.powerdns.com/ubuntu focal-auth-43 main" >/etc/apt/sources.list.d/pdns.list
RUN echo "Package: pdns-*\nPin: origin repo.powerdns.com\nPin-Priority: 600" >/etc/apt/preferences.d/pdns
RUN apt-get install -y gnupg2
ADD https://repo.powerdns.com/FD380FBB-pub.asc FD380FBB-pub.asc
RUN apt-key add FD380FBB-pub.asc && apt-get update

# Ensure pdns-server, python3 and jinja2 is present (for startup script), and tini (for signal management)
RUN apt-get install -y pdns-server pdns-backend-remote pdns-backend-pipe python3 python3-jinja2 tini libcap2-bin && apt-get clean

# Start script
COPY pdns/dockerdata/startup.py /usr/sbin/pdns_server-startup

RUN mkdir -p /etc/powerdns/templates.d

# Work with pdns user - not root
#RUN adduser --system --disabled-password --disabled-login --no-create-home --group pdns --uid 953
#RUN chown pdns:pdns /var/run/pdns /var/lib/powerdns /etc/powerdns/pdns.d /etc/powerdns/templates.d
#USER pdns

COPY pdns.conf /etc/powerdns/
COPY remote_backend.j2 edns.j2 pipe_backend.j2 /etc/powerdns/templates.d/

ENV TEMPLATE_FILES="remote_backend,edns"
#ENV TEMPLATE_FILES="pipe_backend,edns"

#COPY app /app

# for debug
#RUN apt-get install -y vim iputils-ping dnsutils tcpdump tshark iproute2 && apt-get clean

ENV PDNS_LOGLEVEL="INFO"

# for zmqconnector
#ENV BACKEND_ENDPOINT="tcp://127.0.0.1:5560"
# for PipeBackend
#ENV BACKEND_ENDPOINT="/tmp/backend.sock"
# for HTTPBackend
ENV BACKEND_ENDPOINT="http://backend:8080"

# DNS ports
EXPOSE 53/udp
EXPOSE 53/tcp
# webserver port
EXPOSE 8081/tcp

#HEALTHCHECK CMD dig +short @127.0.0.1 keepalive.main.xpx.t-online.de |grep 192.0.2.1 >/dev/null
HEALTHCHECK CMD pdns_control rping

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/sbin/pdns_server-startup"]
