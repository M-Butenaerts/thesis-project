this read me is here to guide you into setting up the blockchain network. 

first create the certificates by running the following command:

export CHANNEL_NAME=bank-channel
export ORG_NAME=OrgBankMSP
export FABRIC_CFG_PATH=./channel/


./bin/cryptogen generate --config=./channel/crypto-config.yaml --output=.channel/crypto-config/

next create the genesis block, the channel and the anchor peer

./bin/configtxgen -profile OrdererGenesis -configPath ./channel -channelID sys-channel -outputBlock ./artifacts/genesis.block
./bin/configtxgen -profile BankChannel -configPath ./channel -channelID bank-channel -outputCreateChannelTx ./artifacts/bank-channel.tx
./bin/configtxgen -profile BankChannel -outputAnchorPeersUpdate ./artifacts/${ORG_NAME}-anchors.tx -channelID $CHANNEL_NAME -asOrg $ORG_NAME

./bin/peer lifecycle chaincode package chaincode/tar/bank-chaincode.tar.gz --path ./chaincode/bank-chaincode --lang golang --label bank-chaincode_1.0

