# save this as server.py
import base64
import random
import subprocess
import sys
from flask import Flask, json, request, jsonify
import os
import rsa #type:ignore

from datetime import date

# port = sys.argv[1]
peer_ports = {
    "8080": 7051,
    "8081": 8051,
    "8082": 9051,
    "8083": 10051,
}
app = Flask(__name__)

def log(text, file="/tmp/log.txt"):
    with open(file, "a") as f:
        f.write(f"{text}\n")

def get_date():
    return date.today().strftime("%d-%m-%Y")

def invoke(function_call): 
    command = ["fpcclient", "invoke"] + function_call
    try: 
        log(f"[LOG]: invoke {command}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}, 200
    except subprocess.CalledProcessError as e:
        log(f"[ERROR]: {e.stderr}")
        return {"status": "error", "error": e.stderr}, 500

def query(function_call): 
    command = ["fpcclient", "query"] + function_call
    try: 
        log(f"[LOG]: query {function_call}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}, 200
    except subprocess.CalledProcessError as e:
        log(f"[ERROR]: {e.stderr}")
        return {"status": "error", "error": e.stderr}, 500


@app.route('/ping', methods=['GET'])
def ping():
    log(f"[LOG]: ping")
    return jsonify({'status': 'peer is running'})


@app.route('/create-account', methods=['POST'])
def create_account(): 
    # {
    #     id: string,
    #     pk: string,
    #     timestamp: datetime,
    # }
    data = request.json 
    id_ = data['id']
    pk = data['pk']
    pub = rsa.PublicKey.load_pkcs1(pk.encode("ascii"))
    
    ss = "".join([random.choice("0123456789abcdefghijklmniopklmnop") for _ in range(64)])
    log(ss)
    ct = base64.b64encode(rsa.encrypt(ss.encode("ascii"), pub)).decode("ascii")
    
    try:
        if not ct and not ss:
             return {"status": "error", "error": "encaps failed."}, 500
    except Exception as e:
        return {"status": "error", "error": e.stderr}, 500
    
    res, res_code = invoke(["createAccount", id_, ss, get_date()])
    if res["status"] == "error": return res
    
    return {"status": "account created.", "ct": ct}, 200


@app.route('/get-balance', methods=['POST'])
def get_balance(): 

    # {
    #     id: string,
    #     signature: string,
    #     timestamp: datetime,
    # }
    
    data = request.json 
    id_ = data['id']
    pk = data['pk']
    date = data['date']
    signature = base64.b64decode(data['signature'])
    res, res_code = query(["getAccount", id_])
    if res_code != 200:
        return res
    parsed_res = json.loads(res["output"][2:-1])
    ss = parsed_res["ss"]
    amount = parsed_res["amount"]
    message = {
        "type": "BALANCE",
        "account_name": id_,
        "shared_secret": ss,
        "date": date
    }
    pub = rsa.PublicKey.load_pkcs1(pk.encode("ascii"))
    parsed_res = json.loads(res["output"][2:-1])
    
    message = {
        "type": "BALANCE",
        "account_name": id_,
        "shared_secret": ss,
        "date": date
    }
    log(str(message).encode("ascii"))
    log(signature)
    log(rsa.verify(str(message).encode("ascii"), signature, pub))

    
    # log(verify(str(message), signature, pk))
    # if pk == "OVERRIDE" or verify(str(message), signature, pk):
    try:
        if rsa.verify(str(message).encode("ascii"), signature, pub) == "SHA-256":
            return {"status":"verified.", "balance": amount}, 200
        else:
            return {"status":"error", "error": "invalid signature."}, 500
    except:
        return {"status":"error", "error": "invalid signature."}, 500

@app.route('/transfer', methods=['POST'])
def transfer():     
    # {
    #     id: string,
    #     receiver_id: string,
    #     amount: string
    #     signature: string,
    #     timestamp: datetime,
    # }
    data = request.json 
    id_ = data['id']
    receiver = data['receiver']
    pk = data['pk']
    date = data['date']
    signature = base64.b64decode(data['signature'])
    amount= data['amount']
    seq= data['seq']
    
    res, res_code = query(["getAccount", id_])
    if res_code != 200:
        return res
    parsed_res = json.loads(res["output"][2:-1])
    ss = parsed_res["ss"]
    
    res, res_code = query(["getAccount", receiver])
    if res_code != 200:
        return res
    
    message = {
        "type": "TRANSFER",
        "account_name": id_,
        "receiver": receiver,
        "amount": amount,
        "shared_secret": ss,
        "seq": seq,
        "date": date
    }  
    pub = rsa.PublicKey.load_pkcs1(pk.encode("ascii"))
    
    log(str(message).encode("ascii"))
    log(signature)
    log(pub)
    
    log(rsa.verify(str(message).encode("ascii"), signature, pub))


    if rsa.verify(str(message).encode("ascii"), signature, pub) == "SHA-256":
        res, res_code = invoke(["transfer", id_, receiver, amount])
        if res["status"] == "error": return res
        return {"status": "transfer made."}, 200

    else:
        log("invalid signature. (transfer)")
        return {"status": "error", "error": "invalid signature."}, 500


@app.route('/withdrawal', methods=['POST'])
def withdrawal(): 
    # {
    #     id: string,
    #     amount: string
    #     signature: string,
    #     timestamp: datetime,
    # }
    data = request.json 
    id_ = data['id']
    pk = data['pk']
    date = data['date']
    signature = base64.b64decode(data['signature'])
    seq= data['seq']
    amount= data['amount']
    
    res, res_code = query(["getAccount", id_])
    if res_code != 200:
        return res
    parsed_res = json.loads(res["output"][2:-1])
    ss = parsed_res["ss"]
    
    message = {
        "type": "WITHDRAWAL",
        "account_name": id_,
        "amount": amount,
        "shared_secret": ss,
        "seq": seq,
        "date": date
    }  
    
    pub = rsa.PublicKey.load_pkcs1(pk.encode("ascii"))

    log(id_)
    log(str(message).encode("ascii"))
    log(signature)
    log(rsa.verify(str(message).encode("ascii"), signature, pub))

    if rsa.verify(str(message).encode("ascii"), signature, pub) == "SHA-256":
        res, res_code = invoke(["withdrawal", id_, amount])
        if res["status"] == "error": return res
        return {"status": "withdrawal made."}, 200

    else:
        log("invalid signature. (withdrawal)")
        return {"status": "error", "error": "invalid signature."}, 500


@app.route('/deposit', methods=['POST'])
def deposit(): 
    # {
    #     id: string,
    #     amount: string
    #     signature: string,
    #     timestamp: datetime,
    # }
    data = request.json 
    id_ = data['id']
    pk = data['pk']
    date = data['date']
    signature = base64.b64decode(data['signature'])
    amount= data['amount']
    seq= data['seq']
    
    res, res_code = query(["getAccount", id_])
    if res_code != 200:
        return res
    parsed_res = json.loads(res["output"][2:-1])
    ss = parsed_res["ss"]
    
    message = {
        "type": "DEPOSIT",
        "account_name": id_,
        "amount": amount,
        "shared_secret": ss,
        "seq": seq,
        "date": date
    }  
    
    log(str(message))
    pub = rsa.PublicKey.load_pkcs1(pk.encode("ascii"))

    if rsa.verify(str(message).encode("ascii"), signature, pub) == "SHA-256":
        res, res_code = invoke(["deposit", id_, amount])
        if res["status"] == "error": return res
        return {"status": "deposit made."}, 200

    else:
        log("invalid signature. (deposit)")
        return {"status": "error", "error": "invalid signature."}, 500


# @app.route('/ledger', methods=['GET'])
# def ledger(): pass

if __name__ == '__main__':
    # import rsa # type: ignore
    app.run(host='0.0.0.0', port=8001)
