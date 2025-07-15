from datetime import datetime
import json
import os
import random
import threading
from time import sleep
import tkinter as tk
from utils.dilithium.dilithium_scripts import key_gen, sign
from utils.items import button
from utils.pages.setup import set_up_title
from utils.config import * 
from utils.send import Corresponder
from utils.error import *

BALANCE = "LOADING..."

def communication(window, acc, ss):
    global BALANCE
    c = None
    for _ in range(20):
        print("connnecting to server...")
        c = Corresponder(url=random.choice(PEER_URLS))
        
        if c.ping(): 
            break
        sleep(1)
    if not c: 
        error(window, "Server not responding.")
    while True:
        pk, sk = key_gen()
        date = str(datetime.now())
        
        
        message = {
            "type": "BALANCE",
            "account_name": acc,
            "shared_secret": ss,
            "date": date
        } 

        signature = sign(str(message), sk)
        
        res = json.loads(str(c.get_balance(acc, signature, pk, date)))
        print(res)
        if "status" in res.keys() and res["status"] == 200:
            BALANCE = float(res)

        else: 
            BALANCE = "LOADING..."
        sleep(60)


def main_page(window, acc, ss):
    
    set_up_title(window)
    
    t = threading.Thread(target=communication, args=(window, acc, ss))
    t.start()

    tk.Label(window, bg=TERTIARY_COLOR).place(relx=0.6, y=110, relheight=1, height=-110, relwidth=0.4)
    tk.Label(window, text=acc, bg=QUATERNARY_COLOR, fg=PRIMARY_COLOR, font=(FONT, LABEL_SIZE+5)).place(x=30, y=150)
    tk.Label(window, text=f"BALANCE: {BALANCE}", bg=QUATERNARY_COLOR, fg=PRIMARY_COLOR, font=(FONT, LABEL_SIZE+4)).place(x=30, y=230)

    transfer_button = button(window, text="transfer", bg=TERTIARY_COLOR, fg=QUATERNARY_COLOR, relx=0.8, y=200, anchor="center")
    transfer_button = button(window, text="widthdrawal", bg=TERTIARY_COLOR, fg=QUATERNARY_COLOR, relx=0.8, y=270, anchor="center")
    transfer_button = button(window, text="deposit", bg=TERTIARY_COLOR, fg=QUATERNARY_COLOR, relx=0.8, y=340, anchor="center")