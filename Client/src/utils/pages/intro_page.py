import os
import tkinter as tk

from utils.pages.main_page import main_page
from utils.pages.setup import set_up_title
from utils.config import *
from utils.items import *
from utils.error import *

# === COMMANDS ===
def to_create_account_page_f(window): 
    from utils.pages.create_account_page import create_account_page
    create_account_page(window)


def submit_f(window, account_number, pin_code):
    # print(account_number)
    # print(pin_code)
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
    try:
        if f"{account_number}.txt" in os.listdir(path):
            with open(f"{path}/{account_number}.txt", "r") as f:
                data = f.read()
                pin = data.split("\n")[0]
                ss = data.split("\n")[1]
                if pin == pin_code:
                    main_page(window, account_number, ss)
                else:
                    error(window,"credentials do not match.")
                    return 
        else:
            error(window, "credentials do not match.")
            
    except Exception as e:
        print(e)
        error(window, "credentials do not match.")
        return 

# === PAGE ===
def intro_page(window):
    
    set_up_title(window)

    account_number_label = tk.Label(window, text="account number:", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    account_number_label.place(relx=0.5, y=220, x=-50, anchor="e")

    pin_code_label = tk.Label(window, text="pincode:", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    pin_code_label.place(relx=0.5, y=270, x=-50, anchor="e")

    account_number_input = text_input(window, relx=0.5, x=50, y=205)
    pin_code_input = text_input(window, relx=0.5, x=50, y=255, is_password=True)

    submit_button = button(window, text="Submit", relx=0.5, y=355, anchor="c", f=lambda:submit_f(window, account_number_input.get(), pin_code_input.get()))
    create_account_button = button(window, text="Create a new account", rely=1, x=25, y=-25, anchor="sw", width=25, size=LABEL_SIZE-7, f=lambda: to_create_account_page_f(window))
        
