#!/bin/sh
set -e
# set -x

sleep 5
if [ -f "/etc/hyperledger/bank-channel.block" ]; then
    rm "/etc/hyperledger/bank-channel.block"
    echo "File removed."
else
    echo "File does not exist."
fi

sleep 2
export CORE_PEER_TLS_ENABLED=true  
export ORDERER_CA="/etc/hyperledger/orderer/tls/ca.crt"
# export PEER_TLS_CA="/etc/hyperledger/crypto/peer/tls/ca.crt"
export FABRIC_CFG_PATH="/etc/hyperledger/channel"

export CHANNEL_NAME="bank-channel"
export CHAINCODE_NAME="bank-chaincode"

export CORE_PEER_LOCALMSPID=OrgBankMSP
export CORE_PEER_TLS_ROOTCERT_FILE="/etc/hyperledger/crypto/peer/tls/ca.crt"

export CORE_PEER_MSPCONFIGPATH="/etc/hyperledger/crypto/admin/msp"


CHAINCODE_VERSION="1.0"
CHAINCODE_SEQUENCE="1"
CHAINCODE_PACKAGE="/etc/hyperledger/chaincode/tar/bank-chaincode.tar.gz"

check_commit_readiness() {
    
  echo "Checking commit readiness for $CORE_PEER_ID..."

  while true; do
    STATUS=$(peer lifecycle chaincode checkcommitreadiness \
      --channelID $CHANNEL_NAME \
      --name $CHAINCODE_NAME \
      --version $CHAINCODE_VERSION \
      --sequence $CHAINCODE_SEQUENCE \
      --init-required \
      --output json)

      # Flatten JSON into a single line
    STATUS_CLEAN=$(echo "$STATUS" | tr -d '\n' | tr -d '[:space:]')

    # Look for exact pattern
    if echo "$STATUS_CLEAN" | grep -q '"OrgBankMSP":true'; then
      echo "Is commit ready!"
      break
    else
      echo "Not ready yet. Retrying in 5 seconds..."
      sleep 5
     fi
  done
}

if [ "$CORE_PEER_ID" = "peer0.bank.example.com" ]; then
  export CORE_PEER_ADDRESS=peer0.bank.example.com:7051

fi
if [ "$CORE_PEER_ID" = "peer1.bank.example.com" ]; then
  export CORE_PEER_ADDRESS=peer1.bank.example.com:8051

fi
if [ "$CORE_PEER_ID" = "peer2.bank.example.com" ]; then
  export CORE_PEER_ADDRESS=peer2.bank.example.com:9051

fi
if [ "$CORE_PEER_ID" = "peer3.bank.example.com" ]; then
  export CORE_PEER_ADDRESS=peer3.bank.example.com:10051
fi

echo "===================== Starting peer node... ====================="
peer node start &

echo "Waiting for peer $CORE_PEER_ID to start..."
until nc -z $(echo $CORE_PEER_ADDRESS | cut -d':' -f1) $(echo $CORE_PEER_ADDRESS | cut -d':' -f2); do
  sleep 2
done


# === SIDE PEERS ===
if [ "$CORE_PEER_ID" != "peer0.bank.example.com" ]; then
  sleep 2
  # WAIT FOR CHANNEL BLOCK TO EXIST
  while [ ! -f /etc/hyperledger/artifacts/bank-channel.block ]; do
    echo "Waiting for channel block to exist..."
    sleep 2
  done

  # JOIN CHANNEL
  echo "=====================  Joining channel on $CORE_PEER_ID... ===================== "
  peer channel join -b /etc/hyperledger/artifacts/bank-channel.block
  peer channel list

  # INSTALL CHAINCODE

  echo "=====================  Installing chaincode on $CORE_PEER_ID... ====================="
  peer lifecycle chaincode install $CHAINCODE_PACKAGE

  # SAVE PACKAGE ID
  PACKAGE_ID=$(peer lifecycle chaincode queryinstalled | grep ${CHAINCODE_NAME}_${CHAINCODE_VERSION} | awk -F "[, ]+" '{print $3}')
  echo "Detected package ID: $PACKAGE_ID"
  sleep 10

  echo "=====================  Check readiness on $CORE_PEER_ID...  ===================== "
  check_commit_readiness

fi

# === MAIN PEER === 
if [ "$CORE_PEER_ID" = "peer0.bank.example.com" ]; then
  echo "===================== Creating channel on peer0... ===================== "
  peer channel create -o orderer.example.com:7050 -c $CHANNEL_NAME \
    --ordererTLSHostnameOverride orderer.example.com \
    -f /etc/hyperledger/artifacts/bank-channel.tx \
    --outputBlock /etc/hyperledger/artifacts/bank-channel.block \
    --tls --cafile $ORDERER_CA

  echo
  echo "===================== Joining channel... ===================== "
  peer channel join -b /etc/hyperledger/artifacts/bank-channel.block
  peer channel list
  
  peer channel update -o orderer.example.com:7050 --ordererTLSHostnameOverride orderer.example.com -c $CHANNEL_NAME -f /etc/hyperledger/artifacts/${CORE_PEER_LOCALMSPID}-anchors.tx --tls $CORE_PEER_TLS_ENABLED --cafile $ORDERER_CA
  echo
  echo "===================== Installing chaincode again on peer0... ====================="
  peer lifecycle chaincode install $CHAINCODE_PACKAGE

  PACKAGE_ID=$(peer lifecycle chaincode queryinstalled | grep ${CHAINCODE_NAME}_${CHAINCODE_VERSION} | awk -F "[, ]+" '{print $3}')
  echo "Package ID: $PACKAGE_ID"
  
  peer lifecycle chaincode queryinstalled
  
  echo
  echo "===================== Approving chaincode... ===================== "

  peer lifecycle chaincode approveformyorg \
    -o orderer.example.com:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls $CORE_PEER_TLS_ENABLED \
    --cafile $ORDERER_CA \
    --channelID $CHANNEL_NAME \
    --name $CHAINCODE_NAME \
    --version $CHAINCODE_VERSION \
    --package-id $PACKAGE_ID \
    --sequence $CHAINCODE_SEQUENCE \
    --init-required \
    --waitForEvent
 
  echo
  echo "===================== Committing chaincode... ===================== "
  
  # peer lifecycle chaincode checkcommitreadiness --channelID $CHANNEL_NAME \
  #       --peerAddresses localhost:7051 --tlsRootCertFiles $PEER0_BANK_CA \
  #       --name ${CHAINCODE_NAME} --version ${CHAINCODE_VERSION} --sequence ${CHAINCODE_SEQUENCE} --output json --init-required
  
  echo "Waiting for all peers to be commit ready..."

  check_commit_readiness() {
    
    echo "Checking commit readiness for $CORE_PEER_ID..."

    while true; do
      STATUS=$(peer lifecycle chaincode checkcommitreadiness \
        --channelID $CHANNEL_NAME \
        --name $CHAINCODE_NAME \
        --version $CHAINCODE_VERSION \
        --sequence $CHAINCODE_SEQUENCE \
        --init-required \
        --output json)

        # Flatten JSON into a single line
      STATUS_CLEAN=$(echo "$STATUS" | tr -d '\n' | tr -d '[:space:]')

      # Look for exact pattern
      if echo "$STATUS_CLEAN" | grep -q '"OrgBankMSP":true'; then
        echo "Is commit ready!"
        break
      else
        echo "Not ready yet. Retrying in 5 seconds..."
        sleep 5
      fi
    done
  }

  export CORE_PEER_ID=peer3.bank.example.com
  export CORE_PEER_ADDRESS=peer3.bank.example.com:10051
  export CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/crypto/peers/peer3/tls/ca.crt

  check_commit_readiness
  
  export CORE_PEER_ID=peer2.bank.example.com
  export CORE_PEER_ADDRESS=peer2.bank.example.com:9051
  export CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/crypto/peers/peer2/tls/ca.crt

  check_commit_readiness
  
  export CORE_PEER_ID=peer1.bank.example.com
  export CORE_PEER_ADDRESS=peer1.bank.example.com:8051
  export CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/crypto/peers/peer1/tls/ca.crt

  check_commit_readiness
  
  export CORE_PEER_ID=peer0.bank.example.com
  export CORE_PEER_ADDRESS=peer0.bank.example.com:7051
  export CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/crypto/peer/tls/ca.crt

  check_commit_readiness
  
  
  echo "All peers are commit ready."

  peer lifecycle chaincode commit \
    -o orderer.example.com:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls $CORE_PEER_TLS_ENABLED \
    --cafile $ORDERER_CA \
    --channelID $CHANNEL_NAME \
    --name $CHAINCODE_NAME \
    --version $CHAINCODE_VERSION \
    --sequence $CHAINCODE_SEQUENCE \
    --init-required \
    --peerAddresses peer0.bank.example.com:7051 --tlsRootCertFiles /etc/hyperledger/crypto/peer/tls/ca.crt \
    --peerAddresses peer1.bank.example.com:8051 --tlsRootCertFiles /etc/hyperledger/crypto/peers/peer1/tls/ca.crt \
    --peerAddresses peer2.bank.example.com:9051 --tlsRootCertFiles /etc/hyperledger/crypto/peers/peer2/tls/ca.crt \
    --peerAddresses peer3.bank.example.com:10051 --tlsRootCertFiles /etc/hyperledger/crypto/peers/peer3/tls/ca.crt \
    --waitForEvent
# --collections-config $PRIVATE_DATA_CONFIG \
        
  # peer lifecycle chaincode commit -o orderer.example.com:7050 \
  #   --ordererTLSHostnameOverride orderer.example.com \
  #   --channelID $CHANNEL_NAME --name $CHAINCODE_NAME \
  #   --version $CHAINCODE_VERSION --sequence $CHAINCODE_SEQUENCE \
  #   --peerAddresses peer0.bank.example.com:7051 \
  #   --peerAddresses peer1.bank.example.com:8051 \
  #   --peerAddresses peer2.bank.example.com:9051 \
  #   --peerAddresses peer3.bank.example.com:10051 \
  #   --tlsRootCertFiles /etc/hyperledger/crypto-config/peerOrganizations/bank.example.com/peers/peer0.bank.example.com/tls/ca.crt \
  #   --tlsRootCertFiles /etc/hyperledger/crypto-config/peerOrganizations/bank.example.com/peers/peer1.bank.example.com/tls/ca.crt \
  #   --tlsRootCertFiles /etc/hyperledger/crypto-config/peerOrganizations/bank.example.com/peers/peer2.bank.example.com/tls/ca.crt \
  #   --tlsRootCertFiles /etc/hyperledger/crypto-config/peerOrganizations/bank.example.com/peers/peer3.bank.example.com/tls/ca.crt \
  # --tls --cafile $ORDERER_CA
fi
if [ "$CORE_PEER_ID" = "peer0.bank.example.com" ]; then
  echo "Invoking chaincode init..."
  peer chaincode invoke \
    -o orderer.example.com:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls \
    --cafile $ORDERER_CA \
    -C $CHANNEL_NAME \
    -n $CHAINCODE_NAME \
    --isInit \
    --peerAddresses $CORE_PEER_ADDRESS \
    --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE \
    -c '{"Args":[]}'
fi

sleep 5

echo "Launching Flask API server..."
if [ "$CORE_PEER_ID" = "peer0.bank.example.com" ]; then
  python3 /etc/hyperledger/peer-scripts/peer-server.py 8080

fi
if [ "$CORE_PEER_ID" = "peer1.bank.example.com" ]; then
  python3 /etc/hyperledger/peer-scripts/peer-server.py 8081

fi
if [ "$CORE_PEER_ID" = "peer2.bank.example.com" ]; then
  python3 /etc/hyperledger/peer-scripts/peer-server.py 8082

fi
if [ "$CORE_PEER_ID" = "peer3.bank.example.com" ]; then
  python3 /etc/hyperledger/peer-scripts/peer-server.py 8083
fi
