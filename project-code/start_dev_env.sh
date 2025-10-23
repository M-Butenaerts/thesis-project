cd src/github.com/hyperledger/fabric-private-chaincode

export FPC_PATH_=$PWD 
export FPC_PATH="/project/src/github.com/hyperledger/fabric-private-chaincode"

make -C "$FPC_PATH_/utils/docker" pull pull-dev
make -C "$FPC_PATH_/utils/docker" build build-dev
make -C "$FPC_PATH_/utils/docker" run-dev

