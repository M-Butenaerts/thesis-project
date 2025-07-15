
import os
import random
from time import sleep
import tkinter as tk

from utils.kyber.kyber_scripts import decaps, key_gen
from utils.send import Corresponder
from utils.pages.setup import set_up_title
from utils.config import *
from utils.items import *
from utils.error import *

def to_intro_page_f(window): 
    from utils.pages.intro_page import intro_page
    intro_page(window) 

def submit_f(window, account_name, pin_code, repeated_pin_code): 
    # CHECK ACCOUNT IS AT LEAST 8 CHARS LONG
    if len(account_name) < 8: 
        error(window, "Account name is too short.")
        return 

    # CHECK PINCODE IS LONG ENOUGH AND OF CORRECT FORMAT
    if len(pin_code) < 4 or not pin_code.isdigit():
        error(window, "Pin must be at least 4 digits and numeric.")
        return

    # CHECK REPEATED PIN MATCHES  
    if pin_code != repeated_pin_code: 
        error(window, "Pin codes do not match.")
        return 
    # CONNECT TO SERVER
    
    c = None
    for _ in range(20):
        print("connnecting to server...")
        c = Corresponder(url=random.choice(PEER_URLS))
        
        if c.ping(): 
            break
        sleep(1)
    if not c: 
        error(window, "Server not responding.")


    # create account
    pk, sk = key_gen()
    with open("log.txt", "w") as f: f.write(pk + "\n\n" + sk)
    # print(pk, sk)
    data = c.create_account(account_name, pk)
    # print(data["status"])
    if data["status"] == "account created.":
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
        # print(path)
        with open(f"{path}/{account_name}.txt", "w") as f:
            ss = decaps(sk, data["cypher_text"])[0]
            # print(ss)
            f.write(f"{pin_code}\n{ss}") 
        
        from utils.pages.intro_page import intro_page
        sleep(15)
        intro_page(window)
    
    elif data["status"] == "account already exists.":
        error(window, "Account already exists.") 
    else:
        error(window, "Unknown server error.") 

def create_account_page(window):
    set_up_title(window)

    account_number_label = tk.Label(window, text="account number:", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    account_number_label.place(relx=0.5, y=220, x=-50, anchor="e")

    pin_code_label = tk.Label(window, text="pincode:", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    pin_code_label.place(relx=0.5, y=270, x=-50, anchor="e")
    
    repeate_pin_code_label = tk.Label(window, text="confirm pincode:", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    repeate_pin_code_label.place(relx=0.5, y=320, x=-50, anchor="e")

    account_number_input = text_input(window, relx=0.5, x=50, y=205)
    pin_code_input = text_input(window, relx=0.5, x=50, y=255, is_password=True)
    repeat_pin_code_input = text_input(window, relx=0.5, x=50, y=305, is_password=True)

    submit_button = button(window, text="Submit", relx=0.5, y=405, anchor="c", f=lambda:submit_f(window, account_number_input.get(), pin_code_input.get(), repeat_pin_code_input.get()))
    create_account_button = button(window, text="login", rely=1, x=25, y=-25, anchor="sw", width=25, size=LABEL_SIZE-7, f=lambda: to_intro_page_f(window))
        