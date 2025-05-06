import customtkinter as ctk
import ttkbootstrap as ttkb
import subprocess
import sys 

# Global variables to store email and OTP
generated_otp = None
user_email = None
username= None

WINDOW_WIDTH = 920
WINDOW_HEIGHT = 655

def next():
    subprocess.Popen(["python", "resetpassword.py"])
    root.destroy()

root = ttkb.Window(title="Password Help", themename="cerculean")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)

# Access the style object
style = ttkb.Style()

# Configure the background color for the Toplevel widget
#style.configure('Toplevel', background='#5c9ec0')
root.config(background='#5c9ec0') # You might need this as well for some themes

font_style = ctk.CTkFont('Italianno', 38, 'bold')

heretohelp = ctk.CTkLabel(root, text="Don't Worry,", font=font_style, text_color="#000000")
heretohelp.place(anchor="center", relx=0.5, rely=0.4)

help = ctk.CTkLabel(root, text="We're Here To Help!", font=font_style, text_color="#000000")
help.place(anchor="center", relx=0.5, rely=0.6)

nextbtn = ctk.CTkButton(root, text="Next", font=font_style, command=next)
nextbtn.place(anchor="center", relx=0.5, rely=0.8)

root.mainloop()