"""
Simple text input window - prints to console on OK.
"""

import tkinter as tk


def on_ok():
    text = entry.get()
    print(f"Input: {text}")


window = tk.Tk()
window.title("Frank's Diner")
window.geometry("400x120")
window.resizable(False, False)

entry = tk.Entry(window, width=50)
entry.pack(padx=20, pady=20)
entry.focus()

btn = tk.Button(window, text="OK", width=10, command=on_ok)
btn.pack()

# Enter key also triggers OK
window.bind("<Return>", lambda e: on_ok())

window.mainloop()
