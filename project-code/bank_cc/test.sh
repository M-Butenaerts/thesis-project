#!/usr/bin/env bash

if [[ -z "${FPC_PATH}" ]]; then
  echo "Error: FPC_PATH not set"; exit 1
fi

FABRIC_CFG_PATH="${FPC_PATH}/integration/config"
FABRIC_SCRIPTDIR="${FPC_PATH}/fabric/bin/"

. ${FABRIC_SCRIPTDIR}/lib/common_utils.sh
. ${FABRIC_SCRIPTDIR}/lib/common_ledger.sh

# this is the path points to FPC chaincode binary
CC_PATH=${FPC_PATH}/samples/chaincode/bank_cc/_build/lib/

CC_ID=bank_cc
CC_VER="$(cat ${CC_PATH}/mrenclave)"
CC_EP="OR('SampleOrg.member')"
CC_SEQ="1"

run_test() {
    say "- install bank_cc chaincode"
    PKG=/tmp/${CC_ID}.tar.gz
    ${PEER_CMD} lifecycle chaincode package --lang fpc-c --label ${CC_ID} --path ${CC_PATH} ${PKG}
    ${PEER_CMD} lifecycle chaincode install ${PKG}

    PKG_ID=$(${PEER_CMD} lifecycle chaincode queryinstalled | awk "/Package ID: ${CC_ID}/{print}" | sed -n 's/^Package ID: //; s/, Label:.*$//;p')

    ${PEER_CMD} lifecycle chaincode approveformyorg -o ${ORDERER_ADDR} -C ${CHAN_ID} --package-id ${PKG_ID} --name ${CC_ID} --version ${CC_VER} --sequence ${CC_SEQ} --signature-policy ${CC_EP}
    ${PEER_CMD} lifecycle chaincode checkcommitreadiness -C ${CHAN_ID} --name ${CC_ID} --version ${CC_VER} --sequence ${CC_SEQ} --signature-policy ${CC_EP}
    ${PEER_CMD} lifecycle chaincode commit -o ${ORDERER_ADDR} -C ${CHAN_ID} --name ${CC_ID} --version ${CC_VER} --sequence ${CC_SEQ} --signature-policy ${CC_EP}

    # create an FPC chaincode enclave
    ${PEER_CMD} lifecycle chaincode initEnclave -o ${ORDERER_ADDR} --peerAddresses "localhost:7051" --name ${CC_ID}

    say "- create accounts"
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["createAccount","thieu","PK12345","dd-mm-yyyy"]}' --waitForEvent
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["createAccount","quinten","PK12345","dd-mm-yyyy"]}' --waitForEvent
    
    say "- query accounts"
    ${PEER_CMD} chaincode query  -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["getAccount","thieu"]}'
    ${PEER_CMD} chaincode query  -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["getAccount","quinten"]}'

    # retrieve current value for "asset1";  should be 100;
    say "- deposit"
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["deposit", "thieu", "100"]}' --waitForEvent

    say "- transfer"
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["transfer", "thieu", "quinten", "50"]}' --waitForEvent
    
    say "- query accounts"
    ${PEER_CMD} chaincode query  -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["getAccount","thieu"]}'
    ${PEER_CMD} chaincode query  -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["getAccount","quinten"]}'

    say "- update date"
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["updateDate", "thieu", "xx-xx-xxxx"]}' --waitForEvent
    ${PEER_CMD} chaincode query  -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["getAccount","thieu"]}'
    say "- update pk"
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["updateSs", "thieu", "pk67890"]}' --waitForEvent
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["updateSk", "thieu", "ss12345"]}' --waitForEvent
    ${PEER_CMD} chaincode invoke -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["updateDate", "thieu", "yy-yy-yyyy"]}' --waitForEvent
    ${PEER_CMD} chaincode query  -o ${ORDERER_ADDR} -C ${CHAN_ID} -n ${CC_ID} -c '{"Args":["getAccount","thieu"]}'
    
}

trap ledger_shutdown EXIT

say "Setup ledger ..."
ledger_init

para
say "Run bank_cc test ..."
run_test

para
say "Shutdown ledger ..."
ledger_shutdown

yell "bank_cc test PASSED"

exit 0