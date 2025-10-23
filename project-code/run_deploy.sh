clear
export FPC_PATH=$PWD
# make -C $FPC_PATH/utils/docker pull
cd $FPC_PATH/samples/chaincode/bank_cc/
make 
cd $FPC_PATH 
make -C $FPC_PATH/utils/docker build

export PATH=$PATH:$FPC_PATH/fabric/bin
export FABRIC_CFG_PATH="${FPC_PATH}/integration/config"
export FABRIC_SCRIPTDIR="${FPC_PATH}/fabric/bin/"
export CC_ID=bank_cc
export CC_NAME=bank_cc
export SGX_MODE=SIM

export CCAAS_DOCKER_RUN=true

export CC_ID=bank_cc
export CHANNEL_NAME=mychannel
export CORE_PEER_ADDRESS=peer0.org1.example.com:7051
export CORE_PEER_ID=peer0.org1.example.com
export CORE_PEER_ORG_NAME=org1
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_MSPCONFIGPATH=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_TLS_CERT_FILE=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.crt
export CORE_PEER_TLS_ENABLED="true"
export CORE_PEER_TLS_KEY_FILE=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.key
export CORE_PEER_TLS_ROOTCERT_FILE=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export ORDERER_CA=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
export GATEWAY_CONFIG=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/connection-org1.yaml

make -C $FPC_PATH/samples/chaincode/bank_cc build docker
export CC_VER=$(cat $FPC_PATH/samples/chaincode/bank_cc/_build/lib/mrenclave)
echo "CC_VER=$CC_VER"
# make -C ${FPC_PATH}/ercc all docker
make -C "$FPC_PATH/ecc" \
  CC_NAME="bank_cc" \
  DOCKER_IMAGE="fpc/bank_cc" \
  DOCKER_ENCLAVE_SO_PATH="$FPC_PATH/samples/chaincode/bank_cc/_build/lib" \
  all docker

echo === NETWORK ===
cd $FPC_PATH/samples/deployment/test-network
./setup.sh

cd $FPC_PATH/samples/deployment/test-network/fabric-samples/test-network
./network.sh up createChannel -c mychannel -ccaasdocker true

cd $FPC_PATH/samples/deployment/test-network
./installFPC.sh  

make -C $FPC_PATH/samples/deployment/test-network ercc-ecc-start

cd $FPC_PATH/samples/deployment/test-network
./update-connection.sh
# Org1
# export CORE_PEER_ADDRESS=localhost:7051
# export CORE_PEER_LOCALMSPID=Org1MSP
# export CORE_PEER_MSPCONFIGPATH=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
# export CORE_PEER_TLS_ENABLED=true
# export CORE_PEER_TLS_ROOTCERT_FILE=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

# ORG1_ERCC_PKG_ID=$($FPC_PATH/fabric/bin/peer.sh lifecycle chaincode queryinstalled --output json \
#   | jq -r '.installed_chaincodes[] | select(.label=="ercc_1.0") | .package_id' | head -n1)
# ORG1_ECC_PKG_ID=$($FPC_PATH/fabric/bin/peer.sh lifecycle chaincode queryinstalled --output json \
#   | jq -r '.installed_chaincodes[] | select(.label|startswith("bank_cc_")) | .package_id' | head -n1)

# echo "ORG1_ERCC_PKG_ID=$ORG1_ERCC_PKG_ID"
# echo "ORG1_ECC_PKG_ID=$ORG1_ECC_PKG_ID"

# # Org2
# export CORE_PEER_ADDRESS=localhost:9051
# export CORE_PEER_LOCALMSPID=Org2MSP
# export CORE_PEER_MSPCONFIGPATH=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
# export CORE_PEER_TLS_ROOTCERT_FILE=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt

# ORG2_ERCC_PKG_ID=$($FPC_PATH/fabric/bin/peer.sh lifecycle chaincode queryinstalled --output json \
#   | jq -r '.installed_chaincodes[] | select(.label=="ercc_1.0") | .package_id' | head -n1)
# ORG2_ECC_PKG_ID=$($FPC_PATH/fabric/bin/peer.sh lifecycle chaincode queryinstalled --output json \
#   | jq -r '.installed_chaincodes[] | select(.label|startswith("bank_cc_")) | .package_id' | head -n1)

# echo "ORG2_ERCC_PKG_ID=$ORG2_ERCC_PKG_ID"
# echo "ORG2_ECC_PKG_ID=$ORG2_ECC_PKG_ID"

# export CORE_PEER_ADDRESS=localhost:9051
# export CORE_PEER_LOCALMSPID=Org1MSP
# export CORE_PEER_MSPCONFIGPATH=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
# export CORE_PEER_TLS_ENABLED=true
# export CORE_PEER_TLS_ROOTCERT_FILE=$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

# # What *this* peer approved for bank_cc & ercc on mychannel (this is the source of truth!)
# $FPC_PATH/fabric/bin/peer.sh lifecycle chaincode queryapproved -C mychannel --name bank_cc > /tmp/qappr_org1_bank.txt
# $FPC_PATH/fabric/bin/peer.sh lifecycle chaincode queryapproved -C mychannel --name ercc     > /tmp/qappr_org1_ercc.txt


echo === EXECUTE ===
cd $FPC_PATH/samples/application/simple-cli-go
make

./fpcclient init $CORE_PEER_ID
./fpcclient invoke createAccount thieu pk1234 xx-xx-xxxx
./fpcclient invoke deposit thieu 100 
./fpcclient query getAccount thieu
./fpcclient invoke withdrawal thieu 100 
./fpcclient query getAccount thieu

