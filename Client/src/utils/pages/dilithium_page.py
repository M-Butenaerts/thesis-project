from utils.pages.intro_page import intro_page
from utils.dilithium.dilithium_scripts import set_up_dilithium
from utils.config import *
from utils.pages.setup import set_up
import tkinter as tk


def dilithium_page(window):
    set_up(window)
    
    kyber_label = tk.Label(window, text="waiting for dilithium generations...", bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, font=(FONT, LABEL_SIZE))
    kyber_label.place(relx=0.5, rely=0.5, anchor="center")
    
    if not set_up_dilithium(): 
        window.destroy() 
        return 
    
    intro_page(window)

