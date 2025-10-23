from utils.pages.dilithium_page import dilithium_page
from utils.kyber.kyber_scripts import set_up_kyber
from utils.config import *
from utils.pages.setup import set_up
import tkinter as tk


def kyber_page(window):
    set_up(window)
    
    kyber_label = tk.Label(window, text="waiting for Kyber generations...", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    kyber_label.place(relx=0.5, rely=0.5, anchor="center")
    
    if not set_up_kyber(): 
        window.destroy() 
        return 

    dilithium_page(window)

