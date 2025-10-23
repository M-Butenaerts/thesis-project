FROM debian:bookworm-slim
RUN set -eux; apt-get update; apt-get install -y --no-install-recommends ca-certificates bash curl python3 python3-pip build-essential file python3-rsa && rm -rf /var/lib/apt/lists/*
WORKDIR /run

COPY fpcclient /usr/local/bin/fpcclient

COPY dilithium /run/dilithium/
COPY kyber /run/kyber/
COPY dilithium_scripts.py /run/
COPY kyber_scripts.py /run/

COPY runner_script-DK.sh /run/
COPY runner_script-RSA.sh /run/
COPY runner-server-DK.py /run/
COPY runner-server-RSA.py /run/

COPY organizations /project/src/github.com/hyperledger/fabric-private-chaincode/samples/deployment/test-network/fabric-samples/test-network/organizations

RUN gcc --version

RUN python3 --version && pip3 --version
ENTRYPOINT ["/bin/bash","-lc"]
CMD ["fpcclient --help"]
