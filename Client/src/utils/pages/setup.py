
import tkinter as tk
from utils.config import *


def set_up(window):
    for widget in window.winfo_children():
        widget.destroy()
    tk.Label(window, bg=QUATERNARY_COLOR).place(x=0, y=0, relheight=1, relwidth=1)

def set_up_title(window):
    set_up(window)

    title_section = tk.Label(window, text="TITLE", bg=PRIMARY_COLOR, fg=SECONDARY_COLOR, font=(FONT, TITLE_SIZE))
    title_section.place(x=0, y=0, height=100, relwidth=1)

    sub_title_section = tk.Label(window, text="", bg=SECONDARY_COLOR)
    sub_title_section.place(x=0, y=100, height=10, relwidth=1)

