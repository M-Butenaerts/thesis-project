import base64
from datetime import date, datetime
import json
from time import sleep
import requests
import rsa

#  ======== ACC 1 =========
pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

acc1 = "rsa-acc14"
acc2 = "rsa-acc15"

response = requests.post("http://127.0.0.1:8081/create-account", json={
    "id": acc1,
    "pk": pk,
})
print(f"create acc1 >: {response.status_code}")
data = json.loads(response.content.decode('utf-8'))
ss1 = rsa.decrypt(base64.b64decode(data["ct"]), privkey).decode("ascii")

message = {
    "type": "BALANCE",
    "account_name": acc1,
    "shared_secret": ss1,
    "date": str(datetime.now())
}
pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": base64.b64encode(signature).decode("ascii")
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc1 >: {data}")

#  ======== ACC 2 =========

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

response = requests.post("http://127.0.0.1:8081/create-account", json={
    "id": acc2,
    "pk": pk,
})
print(f"create acc2 >: {response.status_code}")
data = json.loads(response.content.decode('utf-8'))
ss2 = rsa.decrypt(base64.b64decode(data["ct"]), privkey).decode("ascii")

message = {
    "type": "BALANCE",
    "account_name": acc2,
    "shared_secret": ss2,
    "date": str(datetime.now())
}

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/get-balance", json={
    "id": acc2,
    "pk": pk,
    'date': message["date"],
    "signature": base64.b64encode(signature).decode("ascii")
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

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/deposit", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "amount": "100",
    "signature": base64.b64encode(signature).decode("ascii")
})
data = json.loads(response.content.decode('utf-8'))
print(f"deposit acc1 >: {response.status_code}")

message = {
    "type": "BALANCE",
    "account_name": acc1,
    "shared_secret": ss1,
    "date": str(datetime.now())
}

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": base64.b64encode(signature).decode("ascii")
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

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/transfer", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "amount": "50",
    "receiver": acc2,
    "signature": base64.b64encode(signature).decode("ascii")
})
data = json.loads(response.content.decode('utf-8'))
print(f"transfer acc1 to acc2 >: {response.status_code}")

message = {
    "type": "BALANCE",
    "account_name": acc1,
    "shared_secret": ss1,
    "date": str(datetime.now())
}

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/get-balance", json={
    "id": acc1,
    "pk": pk,
    'date': message["date"],
    "signature": base64.b64encode(signature).decode("ascii")
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc1 >: {data}")


message = {
    "type": "BALANCE",
    "account_name": acc2,
    "shared_secret": ss2,
    "date": str(datetime.now())
}

pubkey, privkey = rsa.newkeys(2560)
pk = pubkey.save_pkcs1().decode("ascii")

signature = rsa.sign(str(message).encode('ascii'), privkey, "SHA-256")
response = requests.post("http://127.0.0.1:8081/get-balance", json={
    "id": acc2,
    "pk": pk,
    'date': message["date"],
    "signature": base64.b64encode(signature).decode("ascii")
})
data = json.loads(response.content.decode('utf-8'))
print(f"acc2 >: {data}")
