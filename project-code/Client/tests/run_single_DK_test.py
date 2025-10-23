import base64
from datetime import date, datetime
import json
from time import sleep
import requests
import rsa

from dilithium.dilithium_scripts import sign
from dilithium.dilithium_scripts import key_gen as d_key_gen
from kyber.kyber_scripts import decaps
from kyber.kyber_scripts import key_gen as k_key_gen


#  ======== ACC 1 =========

acc1 = "dk-acc0"
acc2 = "dk-acc1"

pk, sk = k_key_gen()

response = requests.post("http://127.0.0.1:8080/create-account", json={
    "id": acc1,
    "pk": pk,
})
print(f"create acc1 >: {response.status_code}")

data = json.loads(response.content.decode('utf-8'))
ss1 = decaps(sk, data["ct"])[0]

message = {
    "type": "BALANCE",
    "account_name": acc1,
    "shared_secret": ss1,
    "date": str(datetime.now())
}

pk, sk = d_key_gen()
signature = sign(str(message), sk)


response = requests.post("http://127.0.0.1:8080/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc1 >: {data}")

# #  ======== ACC 2 =========

pk, sk = k_key_gen()
response = requests.post("http://127.0.0.1:8080/create-account", json={
    "id": acc2,
    "pk": pk,
})
print(f"create acc2 >: {response.status_code}")

data = json.loads(response.content.decode('utf-8'))
ss2 = decaps(sk, data["ct"])[0]

message = {
    "type": "BALANCE",
    "account_name": acc2,
    "shared_secret": ss2,
    "date": str(datetime.now())
}

pk, sk = d_key_gen()
signature = sign(str(message), sk)


response = requests.post("http://127.0.0.1:8080/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc2 >: {data}")

#  ======== deposit =========

message = {
    "type": "DEPOSIT",
    "account_name": acc1,
    "amount": "100",
    "shared_secret": ss1,
    "date": str(datetime.now())
}

pk, sk = d_key_gen()
signature = sign(str(message), sk)

response = requests.post("http://127.0.0.1:8080/deposit", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "amount": "100",
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))
print(f"deposit acc1 >: {response.status_code}")


message = {
    "type": "BALANCE",
    "account_name": acc1,
    "shared_secret": ss1,
    "date": str(datetime.now())
}

pk, sk = d_key_gen()
signature = sign(str(message), sk)


response = requests.post("http://127.0.0.1:8080/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc1 >: {data}")

#  ======== transfer =========

message = {
    "type": "TRANSFER",
    "account_name": acc1,
    "receiver": acc2,
    "amount": "50",
    "shared_secret": ss1,
    "date": str(datetime.now())
}


pk, sk = d_key_gen()
signature = sign(str(message), sk)

response = requests.post("http://127.0.0.1:8080/transfer", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "amount": "50",
    "receiver": acc2,
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))

print(f"transfer acc1 to acc2 >: {response.status_code}")


message = {
    "type": "BALANCE",
    "account_name": acc1,
    "shared_secret": ss1,
    "date": str(datetime.now())
}

pk, sk = d_key_gen()
signature = sign(str(message), sk)


response = requests.post("http://127.0.0.1:8080/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc1 >: {data}")

message = {
    "type": "BALANCE",
    "account_name": acc2,
    "shared_secret": ss2,
    "date": str(datetime.now())
}

pk, sk = d_key_gen()
signature = sign(str(message), sk)


response = requests.post("http://127.0.0.1:8080/get-balance", json={
    "id": acc2,
    "pk": pk,
    'date': message["date"],
    "signature": signature
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc2 >: {data}")
