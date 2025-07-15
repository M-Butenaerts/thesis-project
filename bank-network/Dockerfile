    FROM hyperledger/fabric-peer:2.1

    USER root
    WORKDIR /

    RUN apk add --no-cache \
        build-base \
        musl-dev \
        gcc \
        libc-dev \
        make
    RUN touch /tmp/log.txt
    RUN apk add --no-cache python3 py3-pip && \
        ln -sf python3 /usr/bin/python && \
        ln -sf pip3 /usr/bin/pip

    RUN python3 --version && pip3 --version

    COPY peer-scripts/peer-server.py /opt/peer-server.py
    COPY peer-scripts/requirements-peer-server.txt /tmp/requirements.txt
    COPY peer-scripts/run_peer_server.sh /etc/hyperledger/run_peer_server.sh

    RUN pip install --no-cache-dir -r /tmp/requirements.txt
    RUN chmod +x /etc/hyperledger/run_peer_server.sh

    RUN mkdir -p /var/hyperledger/production && \
        chown -R 1000:1000 /var/hyperledger

    ENTRYPOINT ["/etc/hyperledger/run_peer_server.sh"]
