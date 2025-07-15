import tkinter as tk

from utils.pages.main_page import main_page
from utils.pages.kyber_page import kyber_page
from utils.pages.setup import set_up
from utils.config import *
from utils.items import *

def run():
    window = tk.Tk()
    window.title("Banking app")

    window.geometry('750x600')
    window.resizable(False, False)
    
    kyber_page(window)
    # main_page(window, "butti123", "")
    window.mainloop()

run()
