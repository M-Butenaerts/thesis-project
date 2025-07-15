import tkinter as tk
from utils.config import *
# ALL APPLICATION ITEMS

def text_input(window, x=None, y=None, relx=None, rely=None, is_password=False):
    frame = tk.Frame(window, bg=TERTIARY_COLOR, padx=2, pady=2)
    frame.place(relx=relx, rely=rely, x=x, y=y)

    if is_password:
        text_input = tk.Entry(frame, bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, bd=0, width=15, font=(FONT, LABEL_SIZE-5), show="-")
    else:
        text_input = tk.Entry(frame, bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, bd=0, width=15, font=(FONT, LABEL_SIZE-5))
    
    
    text_input.pack()
    
    return text_input

def button(window, text="", f=lambda: print("no function."), x=None, y=None, relx=None, rely=None, anchor="nw", width=15, bg=QUATERNARY_COLOR, fg=TERTIARY_COLOR, size=LABEL_SIZE-5):

    frame = tk.Frame(window, bg=fg, padx=2, pady=2)
    frame.place(relx=relx, rely=rely, x=x, y=y, anchor=anchor)

    button = tk.Button(frame, text=text, bg=bg, fg=fg, bd=0, width=width, font=(FONT, size), activebackground=fg, activeforeground=bg, command=f)
    button.pack()
    
    def color_enter(e): 
        e.widget["bg"] = fg
        e.widget["fg"] = bg
    def color_leave(e): 
        e.widget["bg"] = bg
        e.widget["fg"] = fg
    
    button.bind("<Enter>", color_enter)
    button.bind("<Leave>", color_leave)

    return button

