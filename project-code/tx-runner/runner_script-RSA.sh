
export FPC_PATH=/project/src/github.com/hyperledger/fabric-private-chaincode
export CFG="$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/connection-org1.yaml"


sed -i 's#grpcs://localhost:7051#grpcs://peer0.org1.example.com:7051#g' "$CFG" || true
sed -i 's#grpcs://localhost:9051#grpcs://peer0.org2.example.com:9051#g' "$CFG" || true

awk '
  /client:/ && !added { print; print "  discovery:\n    enabled: true\n    asLocalhost: false"; added=1; next }
  /^entityMatchers:/ { print "entityMatchers:\n  peer: []\n  orderer: []"; skip=1; next }
  skip && NF==0 { skip=0; next }
  skip { next }
  { print }
' "$CFG" > /tmp/conn.yaml && mv /tmp/conn.yaml "$CFG"

export FABRIC_SDK_GO_CONFIG_FILE="$CFG"
export GATEWAY_CONFIG="$CFG"

export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_MSPCONFIGPATH="$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
export CORE_PEER_ADDRESS=peer0.org1.example.com:7051
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_TLS_ROOTCERT_FILE="$FPC_PATH/samples/deployment/test-network/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
export SGX_MODE="SIM"
export CORE_PEER_ADDRESS_="peer0.org1.example.com:7051 "

fpcclient init $CORE_PEER_ADDRESS_ || true
fpcclient query getAccount thieu

apt-get update
apt-get install -y --no-install-recommends python3-flask

python3 runner-server-RSA.py