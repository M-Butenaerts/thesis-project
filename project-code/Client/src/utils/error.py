import tkinter as tk
from utils.config import *


def error(window, text):
    print(text)
    error_label = tk.Label(window, text=text, bg=PRIMARY_ERROR_COLOR, fg=SECONDARY_ERROR_COLOR, font=(FONT, LABEL_SIZE-5), padx=10, pady=10)
    error_label.place(relx=1, rely=1, y=-50, x=-50, anchor="se")

    error_label.bind("<Button-1>", lambda e: error_label.destroy())