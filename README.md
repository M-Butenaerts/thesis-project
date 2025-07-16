# Thesis Project

This project provides a guide for setting up and running a **Hyperledger Fabric network** and a **Python application** that interacts with it.

It is intended to be run on **Windows Subsystem for Linux (WSL)**. Below are the system specifications used during development:

- **WSL version**: 2.5.7.0  
- **Kernel version**: 6.6.87.1-1  
- **WSLg version**: 1.0.66  
- **MSRDC version**: 1.2.6074  
- **Direct3D version**: 1.611.1-81528511  
- **DXCore version**: 10.0.26100.1-240331-1435.ge-release  
- **Windows version**: 10.0.26100.4652  

---

## Hyperledger Fabric Network

This project defines a Fabric network consisting of **four peer nodes** under a single **banking organization**.

The network is defined in the [`docker-compose.yaml`](bank-network/docker-compose.yaml) file.
Clone the GitHub repositories for Dilithium and Kyber into the following directories:

bank-network/peer-scripts/dilithium/

bank-network/peer-scripts/kyber/

Client/src/utils/dilithium/

Client/src/utils/kyber/

You can do this using the following commands:

```bash
git clone https://github.com/pq-crystals/dilithium.git bank-network/peer-scripts/dilithium
git clone https://github.com/pq-crystals/kyber.git bank-network/peer-scripts/kyber

git clone https://github.com/pq-crystals/dilithium.git Client/src/utils/dilithium
git clone https://github.com/pq-crystals/kyber.git Client/src/utils/kyber
```

Be sure to set the environment variables:

```bash
export CHANNEL_NAME=bank-channel
export ORG_NAME=OrgBankMSP
export FABRIC_CFG_PATH=./channel/
```

### Certificate Generation

Certificates for the peers and the orderer are included in the repository. However, you can regenerate them using the following commands:

```bash

./bin/cryptogen generate --config=./channel/crypto-config.yaml --output=./channel/crypto-config/
```

### Artifact Generation
To regenerate the artifacts you can run:

```bash
./bin/configtxgen -profile OrdererGenesis \
  -configPath ./channel \
  -channelID sys-channel \
  -outputBlock ./artifacts/genesis.block

./bin/configtxgen -profile BankChannel \
  -configPath ./channel \
  -channelID bank-channel \
  -outputCreateChannelTx ./artifacts/bank-channel.tx

./bin/configtxgen -profile BankChannel \
  -outputAnchorPeersUpdate ./artifacts/${ORG_NAME}-anchors.tx \
  -channelID $CHANNEL_NAME \
  -asOrg $ORG_NAME
```

### Chaincode Packaging
The chaincode can be repackaged, with:

```bash
./bin/peer lifecycle chaincode package chaincode/tar/bank-chaincode.tar.gz \
  --path ./chaincode/bank-chaincode \
  --lang golang \
  --label bank-chaincode_1.0
  ```

  ### Running the Network

  The network can be managed with docker:

  ```bash
docker-compose build
docker-compose down
docker-compose up -d
  ```
## Client Application

The application runs in Python. install the requirements with 
```bash
pip install -r requirements.txt
```
Then run the application with:
```bash
python3 main.py
```