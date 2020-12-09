# our chosen base image
FROM ubuntu:focal AS builder

# TODO: make sure /source looks roughly the same from git or tar

# Reusable layer for base update
RUN apt-get update && apt-get -y dist-upgrade && apt-get clean

# Needed to avoid prompt on Ubuntu
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Berlin"

# devscripts gives us mk-build-deps (and a lot of other stuff)
RUN apt-get update && apt-get -y dist-upgrade && apt-get install -y  --no-install-recommends devscripts equivs git python3-venv && apt-get clean

# import everything - this could be pdns.git OR an auth tarball!
COPY pdns/builder-support /source/builder-support

# TODO: control file is not in tarballs at all right now
RUN mk-build-deps -i -t 'apt-get -y -o Debug::pkgProblemResolver=yes --no-install-recommends' /source/builder-support/debian/authoritative/debian-buster/control && \
    apt-get clean

# for 0MQ backend
RUN apt-get install -y libzmq3-dev

# build and install (TODO: before we hit this line, rearrange /source structure if we are coming from a tarball)
WORKDIR /source/

COPY pdns/pdns /source/pdns
COPY pdns/modules /source/modules
COPY pdns/codedocs /source/codedocs
COPY pdns/docs /source/docs
COPY pdns/build-aux /source/build-aux
COPY pdns/m4 /source/m4
COPY pdns/ext /source/ext
COPY pdns/.git /source/.git
ADD pdns/configure.ac pdns/Makefile.am /source/
COPY pdns/builder/helpers/set-configure-ac-version.sh /usr/local/bin

ARG MAKEFLAGS=
ENV MAKEFLAGS ${MAKEFLAGS:--j2}

ARG DOCKER_FAKE_RELEASE=NO
ENV DOCKER_FAKE_RELEASE ${DOCKER_FAKE_RELEASE}

RUN if [ "${DOCKER_FAKE_RELEASE}" = "YES" ]; then \
      BUILDER_VERSION="$(BUILDER_MODULES=authoritative ./builder-support/gen-version | sed 's/\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')" set-configure-ac-version.sh;\
    fi && \
    BUILDER_MODULES=authoritative autoreconf -vfi

# simplify repeated -C calls with SUBDIRS?
RUN mkdir /build && \
    ./configure \
      --with-lua=luajit \
      --sysconfdir=/etc/powerdns \
      --enable-option-checking=fatal \
      --with-dynmodules='pipe remote' \
      --enable-tools \
      --enable-remotebackend-zeromq && \
    make clean && \
    make $MAKEFLAGS -C ext && make $MAKEFLAGS -C modules && make $MAKEFLAGS -C pdns && \
    make -C pdns install DESTDIR=/build && make -C modules install DESTDIR=/build && make clean && \
    strip /build/usr/local/bin/* /build/usr/local/sbin/* /build/usr/local/lib/pdns/*.so
RUN cd /tmp && mkdir /build/tmp/ && mkdir debian && \
    echo 'Source: docker-deps-for-pdns' > debian/control && \
    dpkg-shlibdeps /build/usr/local/bin/* /build/usr/local/sbin/* /build/usr/local/lib/pdns/*.so && \
    sed 's/^shlibs:Depends=/Depends: /' debian/substvars >> debian/control && \
    equivs-build debian/control && \
    dpkg-deb -I equivs-dummy_1.0_all.deb && cp equivs-dummy_1.0_all.deb /build/tmp/





# Runtime
FROM ubuntu:focal

# Reusable layer for base update - Should be cached from builder
RUN apt-get update && apt-get -y dist-upgrade && apt-get clean

# Ensure python3 and jinja2 is present (for startup script), and tini (for signal management)
RUN apt-get install -y python3 python3-jinja2 tini libcap2-bin vim libzmq5 iputils-ping dnsutils && apt-get clean

# Output from builder
COPY --from=builder /build /
RUN chmod 1777 /tmp # FIXME: better not use /build/tmp for equivs at all
RUN setcap 'cap_net_bind_service=+eip' /usr/local/sbin/pdns_server

# Ensure dependencies are present
RUN apt install -y /tmp/equivs-dummy_1.0_all.deb && apt clean

# Start script
COPY pdns/dockerdata/startup.py /usr/local/sbin/pdns_server-startup

COPY pdns/dockerdata/pdns.conf /etc/powerdns/
RUN mkdir -p /etc/powerdns/pdns.d /var/run/pdns /var/lib/powerdns /etc/powerdns/templates.d

# Work with pdns user - not root
RUN adduser --system --disabled-password --disabled-login --no-create-home --group pdns --uid 953
RUN chown pdns:pdns /var/run/pdns /var/lib/powerdns /etc/powerdns/pdns.d /etc/powerdns/templates.d
#USER pdns

COPY remote_backend.j2 edns.j2 /etc/powerdns/templates.d/
ENV TEMPLATE_FILES="remote_backend,edns"

COPY app /app
RUN apt-get install -y python3-zmq

ENV PDNS_LOGLEVEL="INFO"
ENV BROKER_ENDPOINT="tcp://127.0.0.1:5560"

# DNS ports
EXPOSE 53/udp
EXPOSE 53/tcp
# webserver port
EXPOSE 8081/tcp

HEALTHCHECK CMD dig +short @127.0.0.1 keepalive.main.xpx.t-online.de |grep 192.0.2.1 >/dev/null
#HEALTHCHECK CMD pdns_control rping

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/sbin/pdns_server-startup"]
