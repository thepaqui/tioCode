import tkinter as tk
from datetime import datetime

def update_clock():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=now)
    label.after(1000, update_clock)  # update every second

root = tk.Tk()
root.title("Live Clock")

label = tk.Label(root, font=("Helvetica", 48), bg="black", fg="lime")
label.pack(fill="both", expand=True)

update_clock()
root.mainloop()
