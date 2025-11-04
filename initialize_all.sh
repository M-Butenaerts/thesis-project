clear
docker ps -aq | xargs -r docker rm -f
docker volume prune -f

# Create environment
echo === CREATE ENVIRONMENT ===
rm -rf environment
mkdir environment
cd environment
mkdir src
cd src
mkdir github.com
cd github.com
mkdir hyperledger
cd hyperledger
mkdir fabric-private-chaincode
cd ../../../..

# clone FPC 
# clear
echo === CREATE ENVIRONMENT ===
echo "> DONE"
# echo
echo === CLONE FPC ===
export FPC_PATH=$PWD/environment/src/github.com/hyperledger/fabric-private-chaincode
git clone --recursive https://github.com/hyperledger/fabric-private-chaincode.git $FPC_PATH
# cd $FPC_PATH
# curl -sSL https://bit.ly/2ysbOFE | bash -s

# cd ../../../../..
# clear
echo === CREATE ENVIRONMENT ===
echo "> DONE"
echo
echo === CLONE FPC ===
echo "> DONE"
echo
echo === COPY FILES ===

cp project-code/run_deploy.sh $FPC_PATH
cp -r project-code/bank_cc $FPC_PATH/samples/chaincode

# clear
echo === CREATE ENVIRONMENT ===
echo "> DONE"
echo
echo === CLONE FPC ===
echo "> DONE"
echo
echo === COPY FILES ===
echo "> DONE"
echo
echo === START DEVELOPMENT ENVIRONMENT ===

cd $FPC_PATH
export FPC_VERSION=main

make -C "$PWD/utils/docker" pull pull-dev
make -C "$PWD/utils/docker" build build-dev
make docker 
make -C "$PWD/utils/docker" run-dev

