
from datetime import datetime
import random
from time import sleep
import tkinter as tk
from utils.dilithium.dilithium_scripts import key_gen, sign
from utils.send import Corresponder, get_seq
from utils.config import FONT, LABEL_SIZE, PEER_URLS, QUATERNARY_COLOR, TERTIARY_COLOR
from utils.items import button, number_input
from utils.pages.setup import set_up_title
from utils.error import *


    
def back_f(window, acc, ss): 
    from utils.pages.main_page import main_page
    main_page(window, acc, ss)

def submit_f(window, acc, ss, amount): 
    
    c = None
    for _ in range(20):
        print("connnecting to server...")
        c = Corresponder(url=random.choice(PEER_URLS))
        
        if c.ping(): 
            break
        sleep(1)
    if not c: 
        error(window, "Server not responding.")

    pk, sk = key_gen()
    date = str(datetime.now())
    
    message = {
        "type": "DEPOSIT",
        "account_name": acc,
        "amount": amount,
        "shared_secret": ss,
        "seq": get_seq(acc),
        "date": date
    } 
    signature = sign(str(message), sk)
    
    res = c.deposit(acc, signature, pk, date, amount, message["seq"])

    try:
        status = res.get("status")
        if status == "deposit made.":
            from utils.pages.main_page import main_page
            main_page(window, acc, ss)
            
    except Exception as e:
        print("parse error:", e)
        error(window, "transaction failed.")
    return 

def deposit_page(window, acc, ss):
    set_up_title(window)

    amount_label = tk.Label(window, text="amount:", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    amount_label.place(relx=0.5, y=220, x=-50, anchor="e")

    amount_input = number_input(window, relx=0.5, x=50, y=205)
    submit_button = button(window, text="Submit", relx=0.5, y=405, anchor="c", f=lambda:submit_f(window, acc, ss, amount_input.get()))
    back_button = button(window, text="Back", relx=0.1, rely=0.9, anchor="sw", f=lambda:back_f(window, acc, ss))
    
