#!/bin/bash

set -e  # Exit on error
set -o pipefail

cd "$(dirname "$0")"

FPC_DIR=./chaincode/fpc/fabric-private-chaincode

make -C "$FPC_DIR" docker SGX_MODE=SIM

docker tag hyperledger/fabric-private-chaincode-ccenv:main hyperledger/fpc-ccenv:latest

docker-compose down -v
docker-compose build
docker-compose up -d

