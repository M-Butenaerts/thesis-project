
import base64
from datetime import datetime
import json
import random
import threading
from time import sleep
import psutil
import requests
import rsa

from dilithium.dilithium_scripts import sign
from dilithium.dilithium_scripts import key_gen as d_key_gen
from kyber.kyber_scripts import decaps
from kyber.kyber_scripts import key_gen as k_key_gen

store = []

def monitor_cpu():
    global store
    try:
        while True:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            store.append(cpu_percent)
            # print(store)
    except Exception: pass

def create_account_DK(acc):
    print(f"[CREATE_ACCOUNT]: {acc}")
    global store
    store = []
    
    t0 = datetime.now()
    pk, sk = k_key_gen()

    response = requests.post("http://127.0.0.1:8080/create-account", json={
        "id": acc,
        "pk": pk,
    })
    
    data = json.loads(response.content.decode('utf-8'))
    ss = decaps(sk, data["ct"])[0]    
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    

    print(f"create {acc}>: [{response.status_code}]")
    print(store)
    if len(store) > 0:
        return ss, t, sum(store) / len(store) 
    else:
        return ss, t, None

def get_balance_DK(acc, ss):
    global store
    store = []
    
    
    t0 = datetime.now()
    message = {
        "type": "BALANCE",
        "account_name": acc,
        "shared_secret": ss,
        "date": str(datetime.now())
    }

    pk, sk = d_key_gen()
    signature = sign(str(message), sk)

    response = requests.post("http://127.0.0.1:8080/get-balance", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "signature": signature
    })
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    
    

    print(f"get balance {acc}>: [{response.status_code}]")
    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None 


def deposit_DK(acc, ss, amount, seq):
    print(f"[DEPOSIT]: {acc} | {amount}")
    global store
    store = []
    
    
    t0 = datetime.now()
    message = {
        "type": "DEPOSIT",
        "account_name": acc,
        "amount": amount,
        "shared_secret": ss,
        "seq": seq,
        "date": str(datetime.now())
    }

    pk, sk = d_key_gen()
    signature = sign(str(message), sk)

    response = requests.post("http://127.0.0.1:8080/deposit", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "seq": seq,
        "amount": amount,
        "signature": signature
    })  
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    

    print(f"deposit {acc}>: [{response.status_code}]")
    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None
    
def withdrawal_DK(acc, ss, amount, seq):
    
    print(f"[WITHDRAWAL]: {acc} | {amount}")
    global store
    store = []
    
    t0 = datetime.now()
    
    message = {
        "type": "WITHDRAWAL",
        "account_name": acc,
        "amount": amount,
        "shared_secret": ss,
        "seq": seq,
        "date": str(datetime.now())
    }

    pk, sk = d_key_gen()
    signature = sign(str(message), sk)

    response = requests.post("http://127.0.0.1:8080/withdrawal", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "seq": seq,
        "amount": amount,
        "signature": signature
    })
    
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    

    print(f"withdrawal {acc}>: [{response.status_code}]")
    
    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None



def transfer_DK(acc, ss, amount, receiver, seq):
    print(f"[TRANSFER]: {acc} | {receiver} | {amount}")
    
    global store
    store = []
    
    
    t0 = datetime.now()
    message = {
        "type": "TRANSFER",
        "account_name": acc,
        "receiver": receiver,
        "amount": amount,
        "shared_secret": ss,
        "seq": seq,
        "date": str(datetime.now())
    }
    
    pk, sk = d_key_gen()
    signature = sign(str(message), sk)

    response = requests.post("http://127.0.0.1:8080/transfer", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "amount": amount,
        "seq": seq,
        "receiver": receiver,
        "signature": signature
    })
    print(signature)
    data = json.loads(response.content.decode('utf-8'))

    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    

    print(f"transfer acc1 to acc2 >: {response.status_code}")
            
    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None

def create_account_RSA(acc):
    print(f"[CREATE_ACCOUNT]: {acc}")
    
    global store
    store = []
    
    
    t0 = datetime.now()
    
    pubkey, privkey = rsa.newkeys(2560)
    pk = pubkey.save_pkcs1().decode("ascii")

    response = requests.post("http://127.0.0.1:8081/create-account", json={
        "id": acc,
        "pk": pk,
    })
    data = json.loads(response.content.decode('utf-8'))
    ss = rsa.decrypt(base64.b64decode(data["ct"]), privkey).decode("ascii")
    
    t1 = datetime.now()

    # print(f"create {acc}>: [{response.status_code}]")
    t = (t1 - t0).total_seconds()
    

    print(f"create {acc}>: [{response.status_code}]")
    
    if len(store) > 0:
        return ss, t, sum(store) / len(store) 
    else:
        return ss, t, None


def get_balance_RSA(acc, ss):
    message = {
        "type": "BALANCE",
        "account_name": acc,
        "shared_secret": ss,
        "date": str(datetime.now())
    }
    pubkey, privkey = rsa.newkeys(2560)
    pk = pubkey.save_pkcs1().decode("ascii")

    signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
    response = requests.post("http://127.0.0.1:8081/get-balance", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "signature": base64.b64encode(signature).decode("ascii")
    })
    print(f"get balance {acc}>: [{response.status_code}]")
    

def deposit_RSA(acc, ss, amount, seq):
    print(f"[DEPOSIT]: {acc} | {amount}")
    
    global store
    store = []
    
    
    t0 = datetime.now()

    message = {
        "type": "DEPOSIT",
        "account_name": acc,
        "amount": str(amount),
        "shared_secret": ss,
        "seq": seq,
        "date": str(datetime.now())
    }

    pubkey, privkey = rsa.newkeys(2560)
    pk = pubkey.save_pkcs1().decode("ascii")

    signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
    # print(acc)
    # print(message)
    # print(signature)

    response = requests.post("http://127.0.0.1:8081/deposit", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "amount": str(amount),
        "seq": seq,
        "signature": base64.b64encode(signature).decode("ascii")
    })
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    

    print(f"deposit {acc} >: [{response.status_code}]")
    print(store)

    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None

def withdrawal_RSA(acc, ss, amount, seq):

    print(f"[WITHDRAWAL]: {acc} | {amount}")

    global store
    store = []
    
    
    t0 = datetime.now()
    
    message = {
        "type": "WITHDRAWAL",
        "account_name": acc,
        "amount": str(amount),
        "shared_secret": ss,
        "seq": seq,
        "date": str(datetime.now())
    }

    pubkey, privkey = rsa.newkeys(2560)
    pk = pubkey.save_pkcs1().decode("ascii")

    signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
    response = requests.post("http://127.0.0.1:8081/withdrawal", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "amount": str(amount),
        "seq": seq,
        "signature": base64.b64encode(signature).decode("ascii")
    })
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    
    
    print(f"withdrawal {acc} >: [{response.status_code}]")
    
    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None
    
def transfer_RSA(acc, ss, receiver, amount, seq):
    
    print(f"[TRANSFER]: {acc} | {receiver} | {amount}")
    
    global store
    store = []
    
    
    t0 = datetime.now()
    
    message = {
        "type": "TRANSFER",
        "account_name": acc,
        "receiver": receiver,
        "amount": str(amount),
        "shared_secret": ss,
        "seq": seq,
        "date": str(datetime.now())
    }

    pubkey, privkey = rsa.newkeys(2560)
    pk = pubkey.save_pkcs1().decode("ascii")

    signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")

    response = requests.post("http://127.0.0.1:8081/transfer", json={
        "id": acc,
        "pk": pk,
        'date': message["date"],
        "amount": str(amount),
        "receiver": receiver,
        "seq": seq,
        "signature": base64.b64encode(signature).decode("ascii")
    })
    
    t1 = datetime.now()
    t = (t1 - t0).total_seconds()
    

    print(f"transfer {acc} to {receiver} >: [{response.status_code}]")
    
    if len(store) > 0:
        return t, sum(store) / len(store) 
    else:
        return t, None
results = {
    "RSA": {
        "create_account": [],
        "deposit": [],
        "withdrawal": [],
        "transfer": [],
    },
    "DK": {
        "create_account": [],
        "deposit": [],
        "withdrawal": [],
        "transfer": [],
    }
}
run_id = "".join([random.choice("1234567890abcdefghijklmnopqrstuvwxyz") for _ in range(6)])
visited = {"RSA": {}, "DK": {}}

def run_transaction(transaction, mode): 
    
    acc = run_id + "_" + mode + "_" + str(transaction["Sender Account ID"])
    receiver = run_id + "_" + mode + "_" + str(transaction["Receiver Account ID"])
    amount = str(transaction["Transaction Amount"]).replace(".", "")
    tx_type = transaction["Transaction Type"]
    
    if mode == "RSA":
        if acc not in visited[mode].keys(): 
            ss, t, cpu = create_account_RSA(acc)
            
            visited[mode][acc] = (ss, "3")
            results[mode]["create_account"].append([t, cpu])
        
        if receiver not in visited[mode].keys(): 
            ss, t, cpu = create_account_RSA(receiver)
            visited[mode][receiver] = (ss, "3")
            results[mode]["create_account"].append([t, cpu])

        if tx_type == "Deposit": 
            t, cpu = deposit_RSA(acc, visited[mode][acc][0], amount, visited[mode][acc][1])
            visited[mode][acc] = (visited[mode][acc][0], str(int(visited[mode][acc][1]) + 1))
            
            results[mode]["deposit"].append([t, cpu])
        
        if tx_type == "Withdrawal":
            t, cpu = withdrawal_RSA(acc, visited[mode][acc][0], amount, visited[mode][acc][1])
            visited[mode][acc] = (visited[mode][acc][0], str(int(visited[mode][acc][1]) + 1))

            results[mode]["withdrawal"].append([t, cpu])
        
        if tx_type == "Transfer":
            t, cpu = transfer_RSA(acc, visited[mode][acc][0], receiver, amount, visited[mode][acc][1])
            visited[mode][acc] = (visited[mode][acc][0], str(int(visited[mode][acc][1]) + 1))

            results[mode]["transfer"].append([t, cpu])
    
    if mode == "DK":
        if acc not in visited[mode].keys(): 
            ss, t, cpu = create_account_DK(acc)
            
            visited[mode][acc] = (ss, 3)
            results[mode]["create_account"].append([t, cpu])
        
        if receiver not in visited[mode].keys(): 
            ss, t, cpu = create_account_DK(receiver)
            visited[mode][receiver] = (ss, 3)
            results[mode]["create_account"].append([t, cpu])

        if tx_type == "Deposit": 
            t, cpu = deposit_DK(acc, visited[mode][acc][0], amount, visited[mode][acc][1])
            visited[mode][acc] = (visited[mode][acc][0], str(int(visited[mode][acc][1]) + 1))
            results[mode]["deposit"].append([t, cpu])
        
        if tx_type == "Withdrawal":
            t, cpu = withdrawal_DK(acc, visited[mode][acc][0], amount, visited[mode][acc][1])
            visited[mode][acc] = (visited[mode][acc][0], str(int(visited[mode][acc][1]) + 1))
            results[mode]["withdrawal"].append([t, cpu])
        
        if tx_type == "Transfer":
            t, cpu = transfer_DK(acc, visited[mode][acc][0], receiver, amount, visited[mode][acc][1])
            visited[mode][acc] = (visited[mode][acc][0], str(int(visited[mode][acc][1]) + 1))
            results[mode]["transfer"].append([t, cpu])
        

def run_dataset(df, mode, file_name):
    print(f"=== RUN TRANSACTIONS ({mode}) ===") 
    for i, tx in df.iterrows():
        run_transaction(tx, mode)
        if ((i+1) % 10 == 0) and i > 0:
            print(f"{float(i+1)/10}% DONE")
            
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            # exit()
print(f"DATASET TEST with ID  [{run_id}]")
print()
print("=== LOAD DATASET ===")
monitor_thread = threading.Thread(target=monitor_cpu, args=(), daemon=True)
monitor_thread.start()

import pandas as pd

df = pd.read_csv("../transaction_data.csv")
print("dataset loaded!")

file_name = run_id + "-results.json"

run_dataset(df, "RSA", file_name)
run_dataset(df, "DK", file_name)

monitor_thread.join()

with open(file_name, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
