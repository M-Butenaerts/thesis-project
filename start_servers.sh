clear
cd project-code/tx-runner

ls

rm -r organizations
rm fpcclient
mkdir -p organizations

cd ../..
ls environment/src/github.com/hyperledger/fabric-private-chaincode/samples/deployment/test-network/fabric-samples/test-network/organizations/

cp -r environment/src/github.com/hyperledger/fabric-private-chaincode/samples/deployment/test-network/fabric-samples/test-network/organizations/* project-code/tx-runner/organizations
cp environment/src/github.com/hyperledger/fabric-private-chaincode/samples/application/simple-cli-go/fpcclient project-code/tx-runner

cd project-code/tx-runner
./run_runners.sh