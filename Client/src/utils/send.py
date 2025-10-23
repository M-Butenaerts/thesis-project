
import json
import os
import requests
from datetime import datetime


def get_seq(acc):
    content = None
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    with open(f"{path}/{acc}.txt", "r") as f:
        content = f.read()
    
    seq = int(content.split("\n")[2]) + 1
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

    with open(f"{path}/{acc}.txt", "w") as f:
        f.write(f"{content.split("\n")[0]}\n{content.split("\n")[1]}\n{seq}")
    
    return str(seq)

class Corresponder:
    
    def __init__(self, url="http://127.0.0.1:8080"):
        self.url = url

    def ping(self):
        print(self.url)
        try: 
            res = requests.get(self.url+ "/ping", timeout=5)
            # print(res)
        except:
            print("peer down")
            return False
        print("peer up")
        return True
        

    def create_account(self, account, pk):
        response = requests.post(self.url + "/create-account", json={
            "id": account,
            "pk": pk,
        })
        data = json.loads(response.content.decode('utf-8'))
        return data

    def get_balance(self, acc, signature, pk, date):
        
        response = requests.post(self.url + "/get-balance", json={
            "id": acc,
            "signature":signature,
            "date": date,
            "pk": pk
        })
        # print(response.content)
        data = json.loads(response.content.decode('utf-8'))
        return data

    def deposit(self, acc, signature, pk, date, amount, seq):
        response = requests.post(self.url + "/deposit", json={
            "id": acc,
            "amount": amount,
            "signature":signature,
            "date": date,
            "seq": seq,
            "pk": pk
        })

        data = json.loads(response.content.decode('utf-8'))
        return data
    
    def withdrawal(self, acc, signature, pk, date, amount, seq):
        response = requests.post(self.url + "/withdrawal", json={
            "id": acc,
            "amount": amount,
            "signature":signature,
            "date": date,
            "seq": seq,
            "pk": pk
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def transfer(self, acc, signature, pk, date, receiver, amount, seq):

        response = requests.post(self.url + "/transfer", json={
            "id": acc,
            "amount": amount,
            "receiver": receiver,
            "signature":signature,
            "date": date,
            "seq": seq,
            "pk": pk
        })

        data = json.loads(response.content.decode('utf-8'))
        return data
