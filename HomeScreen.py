import ttkbootstrap as ttkb
from ttkbootstrap.style import Colors
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import customtkinter as ctk
import subprocess


def getstarted():
    try:
        import login
        subprocess.Popen(["python", "login.py"])
        app.destroy() # type: ignore
    except ImportError:
        tk.messagebox.showerror("Error", "The 'login' module was not found.")
    except AttributeError:
        tk.messagebox.showerror("Error", "The 'login' module does not have a 'run' function.")

import customtkinter as ctk
from PIL import Image, ImageTk

# Set appearance and theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Main window
app = ctk.CTk()
app.title("Home_Screen")
app.geometry("914x673")
app.configure(fg_color="white")

# -------- Header --------
header = ctk.CTkFrame(app, width= 888, height=52, fg_color="#85c3e8", corner_radius=0)
header.pack(fill="x", padx=13, pady=12)

title = ctk.CTkLabel(header, text="Accounting and Bookkeeping App", font=ctk.CTkFont(size=20, weight="bold"), text_color="black")
title.pack(padx=13, pady=12)

# -------- Sidebar --------
sidebar = ctk.CTkFrame(app, width=140, height= 550, fg_color="#85c3e8", corner_radius=0)
sidebar.place(x=11, y=80)

# Load and add images to sidebar
image_paths = [r"images/Bookkeeping_homescreen.jpg", r"images/coin_homescreen.jpg", r"images/Bookkeeping_homescreen.jpg", r"images/pig_homescreen.jpg"]

for path in image_paths:
    try:
        img = Image.open(path).resize((123,110))
        img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(sidebar, image=img, text="")
        img_label.image = img
        img_label.pack(padx= 8, pady=25)
    except Exception as e:
        placeholder = ctk.CTkLabel(sidebar, text="Image", width=123, height=110)
        placeholder.pack(padx=8, pady=25)

try:
    image = Image.open(r"images/bigimage_home_screen.jpg")  # Replace with your image file
    image = image.resize((700, 500))
    photo = ImageTk.PhotoImage(image)
    image_label = ctk.CTkLabel(app, image=photo, text="")
    image_label.image = photo
    image_label.place(x=176, y=81)
except Exception as e:
    print(f"Image could not be loaded: {e}")


# -------- Start Button --------
start_button = ctk.CTkButton(app, text="Start", width=282, height=93, fg_color="#85c3e8", text_color="black", font=ctk.CTkFont(size=20),command=getstarted)
start_button.place(x=356, y=510)

app.mainloop()