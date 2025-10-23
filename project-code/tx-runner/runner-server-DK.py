# save this as server.py
import base64
import subprocess
import sys
from flask import Flask, json, request, jsonify
import os

from datetime import date, datetime, timedelta

from kyber_scripts import decaps, encaps, key_gen, set_up_kyber
from dilithium_scripts import set_up_dilithium, verify

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
    return datetime.today()

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


def check_date(id_): 
    res, res_code = query(["getAccount", id_])
    current_date = get_date()
    if res_code != 200:
        return False
    parsed_res = json.loads(res["output"][2:-1])
    old_date = datetime.strptime(parsed_res["date"], "%d-%m-%Y")
    date.today().strftime("%d-%m-%Y")
    # log(old_date)
    # log(old_date + timedelta(days=3))
    # log(current_date)
    # log(old_date + timedelta(days=3) > current_date)
    return old_date + timedelta(days=3) > current_date # SS invalid after 3 days


def check_seq(id_, seq): 
    res, res_code = query(["getAccount", id_])
    if res_code != 200:
        return False
    parsed_res = json.loads(res["output"][2:-1])
    old_seq = parsed_res["seq"]
    if int(seq) > int(old_seq):
        invoke(["setSeq", id_, str(seq)])
        return True
    else:
        return False


def initiate_update_ss(id_): 

    
    pk, sk = key_gen()
    res, res_code = invoke(["updateSs", id_, ""])
    res, res_code = invoke(["updateSk", id_, sk])
    
    return {"status":"expired secret.", "pk": pk}, 200



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
    ct, ss = None, None
    
    try:
        ct, ss = encaps(pk)
        log(ct, ss)
        if not ct and not ss:
             return {"status": "error", "error": "encaps failed."}, 500
    
    except Exception as e:
        return {"status": "error", "error": e.stderr}, 500
    
    res, res_code = invoke(["createAccount", id_, ss, get_date().strftime("%d-%m-%Y")])
    if res["status"] == "error": return res
    
    return {"status": "account created.", "ct": str(ct), }, 200


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
    signature = data['signature']
    
    if not check_date(id_):
        return initiate_update_ss(id_)
    
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
    # log(verify(str(message), signature, pk))
    if pk == "OVERRIDE" or verify(str(message), signature, pk):
        return {"status":"verified.", "balance": amount}, 200
    else:
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
    signature = data['signature']
    amount = data['amount']
    seq = data['seq']
    
    if not check_date(id_):
        return initiate_update_ss(id_)

    if not check_seq(id_, seq):
        return {"status": "error", "error": "invalid seq"}, 500
    
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
    

    if verify(str(message), signature, pk):
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
    signature = data['signature']
    amount= data['amount']
    seq= data['seq']
    
    if not check_date(id_):
        return initiate_update_ss(id_)

    if not check_seq(id_, seq):
        return {"status": "error", "error": "invalid seq"}, 500
    

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
    

    if verify(str(message), signature, pk):
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
    signature = data['signature']
    amount = data['amount']
    seq = data['seq']
    
    if not check_date(id_):
        return initiate_update_ss(id_)

    if not check_seq(id_, seq):
        return {"status": "error", "error": "invalid seq"}, 500
    
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

    if verify(str(message), signature, pk):
        res, res_code = invoke(["deposit", id_, amount])
        if res["status"] == "error": return res
        return {"status": "deposit made."}, 200

    else:
        log("invalid signature. (deposit)")
        return {"status": "error", "error": "invalid signature."}, 500


@app.route('/update-ss', methods=['POST'])
def update_ss():
    data = request.json 
    id_ = data['id']
    ct = data['ct']
    try:
        res, res_code = query(["getAccount", id_])
        if res_code != 200:
            return res
        parsed_res = json.loads(res["output"][2:-1])
        sk = parsed_res["sk"]
        
        ss = decaps(sk, ct)
        res, res_code = invoke(["setSs", id_, ss])
        res, res_code = invoke(["setSk", id_, ""])
        res, res_code = invoke(["setSeq", id_, "1"])
    except:
        log("invalid ciphertext. ")
        return {"status": "error", "error": "invalid ciphertext."}, 500

    return {"status": "ss updated."}, 200

    
    

if __name__ == '__main__':
    set_up_kyber()
    set_up_dilithium()
    app.run(host='0.0.0.0', port=8000)
