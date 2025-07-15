#!/bin/sh
set -e
# set -x

echo $CORE_PEER_ID
# sleep 5
# if [ -f "/etc/hyperledger/bank-channel.block" ]; then
#     rm "/etc/hyperledger/bank-channel.block"
#     echo "File removed."
# else
#     echo "File does not exist."
# fi

# sleep 2
# export CORE_PEER_TLS_ENABLED=true  
# export ORDERER_CA="/etc/hyperledger/orderer/tls/ca.crt"
# # export PEER_TLS_CA="/etc/hyperledger/crypto/peer/tls/ca.crt"
# export FABRIC_CFG_PATH="/etc/hyperledger/channel"

# export CHANNEL_NAME="bank-channel"
# export CHAINCODE_NAME="bank-chaincode"

# export CORE_PEER_LOCALMSPID=OrgBankMSP
# export CORE_PEER_TLS_ROOTCERT_FILE="/etc/hyperledger/crypto/peer/tls/ca.crt"

# export CORE_PEER_MSPCONFIGPATH="/etc/hyperledger/crypto/admin/msp"

# CHAINCODE_VERSION="1.0"
# CHAINCODE_SEQUENCE="1"
# CHAINCODE_PACKAGE="/etc/hyperledger/chaincode/tar/bank-chaincode.tar.gz"

# check_commit_readiness() {
    
#   echo "Checking commit readiness for $CORE_PEER_ID..."

#   while true; do
#     STATUS=$(peer lifecycle chaincode checkcommitreadiness \
#       --channelID $CHANNEL_NAME \
#       --name $CHAINCODE_NAME \
#       --version $CHAINCODE_VERSION \
#       --sequence $CHAINCODE_SEQUENCE \
#       --init-required \
#       --output json)

#       # Flatten JSON into a single line
#     STATUS_CLEAN=$(echo "$STATUS" | tr -d '\n' | tr -d '[:space:]')

#     # Look for exact pattern
#     if echo "$STATUS_CLEAN" | grep -q '"OrgBankMSP":true'; then
#       echo "Is commit ready!"
#       break
#     else
#       echo "Not ready yet. Retrying in 5 seconds..."
#       sleep 5
#      fi
#   done
# }

# if [ "$CORE_PEER_ID" = "enclavecc-echo-peer0" ]; then
#   export CORE_PEER_ADDRESS=enclavecc-echo-peer0:7051

# fi
