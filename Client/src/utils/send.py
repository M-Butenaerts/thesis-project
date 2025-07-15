
import json
import requests
from datetime import datetime

class Corresponder:
    
    def __init__(self, url="http://127.0.0.1:8080"):
        self.url = url

    def ping(self):
        print(self.url)
        try: 
            res = requests.get(self.url+ "/ping", timeout=5)
            print(res)
        except:
            print("peer down")
            return False
        print("peer up")
        return True
        

    def create_account(self, account, public_key):
        response = requests.post(self.url + "/create-account", json={
            "id": account,
            "public_key": public_key,
            "date": str(datetime.now())
        })
        data = json.loads(response.content.decode('utf-8'))
        return data

    def get_balance(self, acc, signature, pk, date):
        
        response = requests.post(self.url + "/get-balance", json={
            "id": acc,
            "signature":signature,
            "date": date,
            "public_key": pk
        })
        print(response.content)
        data = json.loads(response.content.decode('utf-8'))
        return data

    