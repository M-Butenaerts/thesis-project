# save this as server.py
import base64
import subprocess
import sys
from flask import Flask, json, request, jsonify
import os

from kyber_scripts import encaps, set_up_kyber
from dilithium_scripts import set_up_dilithium

port = sys.argv[1]
peer_ports = {
    "8080": 7051,
    "8081": 8051,
    "8082": 9051,
    "8083": 10051,
}
app = Flask(__name__)

# CORE_PEER_MSPCONFIGPATH = "/etc/hyperledger/crypto-config/peerOrganizations/bank.example.com/users/Admin@bank.example.com/msp"
# ORDERER_CA = "/etc/hyperledger/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"
# CORE_PEER_TLS_ROOTCERT_FILE = "/etc/hyperledger/crypto/peer/tls/ca.crt"

# env = os.environ.copy()
# env["CORE_PEER_MSPCONFIGPATH"] = CORE_PEER_MSPCONFIGPATH
# env["CORE_PEER_LOCALMSPID"] = "OrgBankMSP"
# env["CORE_PEER_TLS_ENABLED"] = "true"
def log(text, file="/tmp/log.txt"):
    with open(file, "a") as f:
        f.write(f"{text}\n")


def invoke(function_call):
    # global CORE_PEER_MSPCONFIGPATH
    # global ORDERER_CA
    # global CORE_PEER_TLS_ROOTCERT_FILE
    
    command = [
        "peer", "chaincode", "invoke",
        "-o", "orderer.example.com:7050",
        "--ordererTLSHostnameOverride", "orderer.example.com",
        "--tls",
        "--cafile", os.environ["ORDERER_CA"],
        "-C", "bank-channel",
        "-n", "bank-chaincode",
        "--peerAddresses", f"peer{port[-1]}.bank.example.com:{peer_ports[port]}",
        "--tlsRootCertFiles", os.environ["CORE_PEER_TLS_ROOTCERT_FILE"],
        "-c", function_call
    ]
    try: 
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}, 500

def query(function_call):
    # global CORE_PEER_MSPCONFIGPATH
    # global ORDERER_CA
    # global CORE_PEER_TLS_ROOTCERT_FILE
    
    command = [
        "peer", "chaincode", "query",
        "-o", "orderer.example.com:7050",
        "--ordererTLSHostnameOverride", "orderer.example.com",
        "--tls",
        "--cafile", os.environ["ORDERER_CA"],
        "-C", "bank-channel",
        "-n", "bank-chaincode",
        "--peerAddresses", f"peer{port[-1]}.bank.example.com:{peer_ports[port]}",
        "--tlsRootCertFiles", os.environ["CORE_PEER_TLS_ROOTCERT_FILE"],
        "-c", function_call
    ]
    try: 
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}, 500


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'peer is running'})

@app.route('/create-account', methods=['POST'])
def create_account():
    data = request.json 
    id = data['id']
    public_key = data['public_key']
    # log(id)
    # log(public_key)
    cipher_text, shared_key = encaps(public_key)
    # log(cipher_text)
    # log(shared_key)
    function_call = json.dumps({
        "function": "CreateAccount",
        "Args": [id , public_key, shared_key]
    })
    ok = invoke(function_call)
    log(ok)
    response = str(ok)
    if "already exists" in response:
        return jsonify({"status": "account already exists."})
    else:
        return jsonify({"cypher_text": cipher_text, "status": "account created."})

@app.route('/get-balance', methods=['POST'])
def get_balance():
    log("BALANCE")
    data = request.json 
    id = data['id']
    public_key = data['public_key']
    date = data['date']
    signature = data['signature']

    function_call = json.dumps({
        "function": "GetAccount",
        "Args": [id]
    })
    result = query(function_call)
    log(str(result))
    if result["status"] != "success":
        return jsonify({"status": "error", "message": "Account not found"}), 404

    try:
        account_data = json.loads(result["output"])
    except Exception:
        return jsonify({"status": "error", "message": "Invalid data returned from ledger"}), 500
    
    log(str(account_data))
    ss = ""
    new_message = str({
        "type": "BALANCE",
        "account_name": id,
        "shared_secret": ss,
        "date": date
    })
    
    return jsonify({
        "status": "suck my dick"
    })

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json 
    idFrom = data['id_from']
    idTo = data['id_to']
    amount = data['amount']
    
    function_call = json.dumps({
        "function": "Transfer",
        "Args": [idFrom, idTo, amount]
    })

    return invoke(function_call)

@app.route('/withdrawal', methods=['POST'])
def withdrawal():
    data = request.json 
    id = data['id']
    amount = data['amount']

    function_call = json.dumps({
        "function": "withdrawal",
        "Args": [id, amount]
    })

    return invoke(function_call)

@app.route('/deposit', methods=['POST'])
def deposit():
    
    data = request.json 
    id = data['id']
    amount = data['amount']

    function_call = json.dumps({
        "function": "Deposit",
        "Args": [id, amount]
    })

    return invoke(function_call)

@app.route('/ledger', methods=['GET'])
def ledger():
    
    function_call = json.dumps({
        "function": "GetAllAccounts",
        "Args": []
    })

    return query(function_call)

if __name__ == '__main__':
    set_up_kyber()
    set_up_dilithium()
    app.run(host='0.0.0.0', port=port)
