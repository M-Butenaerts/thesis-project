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
from utils.send import Corresponder, get_seq
from utils.error import *

def to_deposit_page_f(window, acc, ss):
    from utils.pages.deposit_page import deposit_page
    deposit_page(window, acc, ss) 

def to_withdrawal_page_f(window, acc, ss):
    from utils.pages.withdrawal_page import withdrawal_page
    withdrawal_page(window, acc, ss) 

def to_transfer_page_f(window, acc, ss):
    from utils.pages.transfer_page import transfer_page
    transfer_page(window, acc, ss) 

def communication(window, acc, ss, set_balance):
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
        
        res = c.get_balance(acc, signature, pk, date)
        print(res)
        try:
            # if c.get_balance returns requests.Response, do: res = res.json()
            status = res.get("status")
            if status == "verified" or status == "verified.":  # be lenient about the dot
                balance = float(res["balance"])
                # schedule UI update on main loop
                window.after(0, set_balance, f"{balance:.2f}")
            else:
                window.after(0, set_balance, "LOADING...")
        except Exception as e:
            print("parse error:", e)
            window.after(0, set_balance, "LOADING...")
        sleep(15)



def main_page(window, acc, ss):
    set_up_title(window)

    balance_var = tk.StringVar(value="BALANCE: LOADING...")

    def set_balance(text):
        balance_var.set(f"BALANCE: {text}")

    t = threading.Thread(target=communication, args=(window, acc, ss, set_balance), daemon=True)
    t.start()

    tk.Label(window, bg=TERTIARY_COLOR).place(relx=0.6, y=110, relheight=1, height=-110, relwidth=0.4)
    tk.Label(window, text=acc, bg=QUATERNARY_COLOR, fg=PRIMARY_COLOR, font=(FONT, LABEL_SIZE+5)).place(x=30, y=150)
    tk.Label(window, textvariable=balance_var, bg=QUATERNARY_COLOR, fg=PRIMARY_COLOR,
             font=(FONT, LABEL_SIZE+4)).place(x=30, y=230)

    button(window, text="transfer",    bg=TERTIARY_COLOR, fg=QUATERNARY_COLOR, relx=0.8, y=200, anchor="center", f=lambda: to_transfer_page_f(window, acc, ss))
    button(window, text="withdrawal",  bg=TERTIARY_COLOR, fg=QUATERNARY_COLOR, relx=0.8, y=270, anchor="center", f=lambda: to_withdrawal_page_f(window, acc, ss))
    button(window, text="deposit",     bg=TERTIARY_COLOR, fg=QUATERNARY_COLOR, relx=0.8, y=340, anchor="center", f=lambda: to_deposit_page_f(window, acc, ss))
